"""One metadata endpoint, no redirects, credentials, cookies, proxies or payload APIs."""
from dataclasses import dataclass
import hashlib
import http.client
import json
import math
import re
import time
from urllib.parse import quote, unquote, urlsplit

from .url_parser import revision_ok


class Failure(Exception):
    def __init__(self, code, reason, bytes_read=0):
        self.code, self.reason, self.bytes_read = code, reason, bytes_read
        super().__init__(reason)


@dataclass(frozen=True)
class Limits:
    timeout: float = 10.0
    max_response_bytes: int = 1048576
    max_files: int = 1000

    def __post_init__(self):
        if not math.isfinite(self.timeout) or not 0 < self.timeout <= 30:
            raise ValueError('timeout must be finite and in (0, 30] seconds')
        if type(self.max_response_bytes) is not int or not 1 <= self.max_response_bytes <= 1048576:
            raise ValueError('response limit must be between 1 and 1048576 bytes')
        if type(self.max_files) is not int or not 1 <= self.max_files <= 10000:
            raise ValueError('max-files must be between 1 and 10000')


@dataclass
class Response:
    status: int
    headers: dict
    body: bytes


def http_transport(target, limits):
    """Read at most limit+1 body bytes; socket timeout plus body elapsed deadline.

    OS DNS resolution is not governed by Python's socket timeout. No retries.
    Headers use http.client's built-in count/line bounds. Error bodies are not read.
    """
    if not re.fullmatch(r'/api/models/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/revision/[A-Za-z0-9_.%\-]+\?blobs=true', target):
        raise Failure('UNSUPPORTED', 'Only model metadata transport is permitted.')
    if not revision_ok(unquote(target.split('?')[0].rsplit('/',1)[-1])):
        raise Failure('UNSUPPORTED', 'Unsafe metadata revision.')
    conn = http.client.HTTPSConnection('huggingface.co', timeout=limits.timeout)
    body = bytearray()
    try:
        conn.request('GET', target, headers={'User-Agent':'HHS/0.1.0 (repository-metadata-only)',
                                           'Accept':'application/json', 'Accept-Encoding':'identity'})
        response = conn.getresponse()
        headers = {k.lower():v for k,v in response.getheaders()
                   if k.lower() in ('content-length', 'content-type', 'content-encoding', 'link', 'x-error-code')}
        if response.status != 200: return Response(response.status, headers, b'')
        length = headers.get('content-length')
        if length is not None:
            if not length.isdecimal() or len(length)>20: raise Failure('MALFORMED_RESPONSE', 'Invalid Content-Length.')
            if int(length) > limits.max_response_bytes:
                raise Failure('RESPONSE_TOO_LARGE', 'Declared metadata response exceeds byte budget.')
        if headers.get('content-encoding', 'identity').lower() != 'identity':
            raise Failure('UNSUPPORTED', 'Compressed metadata responses are refused.')
        if headers.get('content-type', '').split(';')[0].strip().lower() != 'application/json':
            raise Failure('MALFORMED_RESPONSE', 'Metadata endpoint did not return application/json.')
        deadline = time.monotonic() + limits.timeout
        while len(body) <= limits.max_response_bytes:
            if response.fp is None:  # HTTPResponse closes itself after the final Content-Length byte.
                break
            remaining = deadline - time.monotonic()
            if remaining <= 0: raise TimeoutError()
            # The response owns the socket when the server closes the connection.
            response.fp.raw._sock.settimeout(min(limits.timeout, remaining))
            chunk = response.read1(min(65536, limits.max_response_bytes + 1 - len(body)))
            if not chunk: break
            body.extend(chunk)
        return Response(response.status, headers, bytes(body))
    except TimeoutError:
        raise Failure('TIMEOUT', 'Metadata request timed out.', len(body)) from None
    except (OSError, http.client.HTTPException):
        raise Failure('NETWORK_ERROR', 'Metadata transport failed; details omitted.', len(body)) from None
    finally:
        conn.close()


def metadata_url(source):
    repo = '/'.join(quote(s, safe='') for s in source['repo_id'].split('/'))
    revision = quote(source['effective_revision'], safe='')
    return f'https://huggingface.co/api/models/{repo}/revision/{revision}?blobs=true'


class Client:
    def __init__(self, limits=None, transport=None, mode='live'):
        self.limits = limits or Limits()
        self.transport = transport or http_transport
        self.mode = mode
        self.requests = 0
        self.bytes_read = 0
        self.response_hash = None

    def get_metadata(self, url):
        # Validate even internally generated URLs. No file content endpoint exists.
        parsed = urlsplit(url)
        if (parsed.scheme != 'https' or parsed.netloc != 'huggingface.co'
                or parsed.query != 'blobs=true' or parsed.fragment
                or not re.fullmatch(r'/api/models/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/revision/[A-Za-z0-9_.%\-]+', parsed.path)):
            raise Failure('UNSUPPORTED', 'Only the bounded model metadata endpoint is allowed.')
        if not revision_ok(unquote(parsed.path.rsplit('/', 1)[-1])):
            raise Failure('UNSUPPORTED', 'Unsafe revision in metadata route.')
        if self.requests >= 1: raise Failure('LIMIT_REACHED', 'One metadata response per client; no pagination or retries.')
        self.requests += 1
        try:
            response = self.transport(parsed.path+'?'+parsed.query, self.limits)
        except Failure as exc:
            self.bytes_read = exc.bytes_read
            raise
        except TimeoutError:
            raise Failure('TIMEOUT', 'Metadata request timed out.') from None
        except (OSError, http.client.HTTPException):
            raise Failure('NETWORK_ERROR', 'Metadata transport failed; diagnostic details omitted.') from None
        self.bytes_read = len(response.body)
        headers = {k.lower():v for k,v in response.headers.items()}
        status = response.status
        if status != 200:
            code = ('GATED' if status in (401,403) and headers.get('x-error-code') == 'GatedRepo'
                    else {401:'AUTH_REQUIRED',403:'AUTH_REQUIRED',404:'NOT_FOUND',429:'RATE_LIMITED'}.get(status,
                    'REDIRECT_BLOCKED' if 300 <= status < 400 else 'NETWORK_ERROR' if status >= 500 else 'UNKNOWN'))
            raise Failure(code, f'HTTP {status} from metadata endpoint; absence/private/revision ambiguity may remain.')
        if len(response.body) > self.limits.max_response_bytes:
            raise Failure('RESPONSE_TOO_LARGE', 'Metadata response exceeds byte budget; discarded.')
        try:
            data = json.loads(response.body, parse_constant=lambda _: (_ for _ in ()).throw(ValueError()))
        except (ValueError, UnicodeError, RecursionError):
            raise Failure('MALFORMED_RESPONSE', 'Invalid metadata JSON; raw response omitted.') from None
        self.response_hash = hashlib.sha256(response.body).hexdigest()
        return data, bool(headers.get('link'))
