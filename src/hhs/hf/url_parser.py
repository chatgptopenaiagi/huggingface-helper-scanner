"""Conservative URL grammar. Never echo rejected input into diagnostics."""
import re
from urllib.parse import unquote, urlsplit


class InputError(ValueError):
    def __init__(self, code='INVALID', reason='URL does not match the supported safe grammar.'):
        self.code, self.reason = code, reason
        super().__init__(reason)


def safe_path(value):
    return (isinstance(value, str) and 0 < len(value) <= 1024
            and all(re.fullmatch(r'[A-Za-z0-9_.@+ -]+', p) and p not in ('.', '..')
                    for p in value.split('/')))


def revision_ok(value):
    return (isinstance(value, str) and 0 < len(value) <= 200
            and all(re.fullmatch(r'[A-Za-z0-9_][A-Za-z0-9_.-]*', p)
                    and '..' not in p and not p.endswith('.') for p in value.split('/')))


def parse_url(url, revision=None):
    if not isinstance(url, str) or len(url) > 2048 or any(ord(c) <= 32 or ord(c) == 127 for c in url):
        raise InputError()
    try:
        parts = urlsplit(url)
    except ValueError:
        raise InputError() from None
    if (parts.scheme != 'https' or parts.netloc.lower() != 'huggingface.co'
            or parts.query or parts.fragment or '?' in url or '#' in url):
        raise InputError()
    raw = parts.path.removesuffix('/').split('/')[1:]
    kind = 'model'
    if raw and raw[0] in ('datasets', 'spaces'):
        kind = {'datasets':'dataset', 'spaces':'space'}[raw.pop(0)]
    if len(raw) < 2 or not all(re.fullmatch(r'[A-Za-z0-9_][A-Za-z0-9_.-]{0,95}', s)
                                    and '..' not in s and not s.endswith(('.', '.git')) for s in raw[:2]):
        raise InputError()
    owner, name = raw[:2]
    requested, path = None, None
    if len(raw) > 2:
        if raw[2] not in ('tree', 'blob', 'resolve'):
            raise InputError('UNSUPPORTED', 'Unsupported repository URL route.')
        if len(raw) < 4: raise InputError()
        requested = unquote(raw[3], errors='replace')
        if not revision_ok(requested): raise InputError()
        if len(raw) > 4:
            segments = [unquote(s, errors='replace') for s in raw[4:]]
            if any('/' in s for s in segments): raise InputError()
            path = '/'.join(segments)
            if not safe_path(path): raise InputError()
        if raw[2] in ('blob', 'resolve') and path is None: raise InputError()
    if revision is not None:
        if not revision_ok(revision): raise InputError()
        if requested is not None and requested != revision:
            raise InputError('INVALID', 'URL revision and explicit revision conflict.')
        requested = revision
    return {'provider':'huggingface', 'host':'huggingface.co', 'repo_type':kind,
            'repo_id':owner+'/'+name, 'owner':owner, 'name':name,
            'requested_revision':requested, 'effective_revision':requested or 'main',
            'requested_path':path, 'resolved_revision':None}
