"""Exercise the real transport with a fake HTTPS connection, and the CLI offline."""
import contextlib
import copy
import io
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from hhs.cli import main
from hhs.hf.client import Client, Failure, Limits, http_transport, metadata_url
from hhs.hf.inspector import inspect_repository, validate_snapshot
from hhs.hf.url_parser import parse_url

FIXTURE=Path(__file__).parent/'fixtures/model.json'
URL='https://huggingface.co/example-owner/example-model'


class TransportTests(unittest.TestCase):
    def setup_response(self, body=b'{}', status=200, headers=None, failure=None, close_at_eof=False):
        self.headers=headers or {'content-type':'application/json'}
        self.calls=[];self.reads=0;self.closed=False
        outer=self
        class FakeResponse:
            fp=SimpleNamespace(raw=SimpleNamespace(_sock=SimpleNamespace(settimeout=lambda _:None)))
            def getheaders(self):return list(outer.headers.items())
            def read1(self, n):
                outer.reads+=1
                if failure and outer.reads>1:raise failure
                data=outer.body[:n];outer.body=outer.body[n:]
                if close_at_eof and not outer.body:self.fp=None
                return data
        response=FakeResponse();response.status=status
        self.body=body
        class Connection:
            def __init__(self, host, timeout):outer.host=host;outer.timeout=timeout
            def request(self,*args,**kwargs):outer.calls.append((args,kwargs))
            def getresponse(self):return response
            def close(self):outer.closed=True
        return Connection

    def test_headers_no_credentials_and_byte_sentinel(self):
        connection=self.setup_response(b'123456789')
        with patch('hhs.hf.client.http.client.HTTPSConnection',connection):
            response=http_transport('/api/models/a/b/revision/main?blobs=true',Limits(max_response_bytes=4))
        self.assertEqual(response.body,b'12345')
        self.assertTrue(self.closed)
        headers=self.calls[0][1]['headers']
        self.assertEqual(set(headers),{'User-Agent','Accept','Accept-Encoding'})
        self.assertEqual(self.host,'huggingface.co')

    def test_redirect_and_declared_size_not_read(self):
        for status,headers,expected in [(302,{'location':'https://evil.test'},None),
                (200,{'content-length':'999'},'RESPONSE_TOO_LARGE'),
                (200,{'content-length':'invalid'},'MALFORMED_RESPONSE'),
                (200,{'content-encoding':'gzip'},'UNSUPPORTED'),
                (200,{'content-type':'application/octet-stream'},'MALFORMED_RESPONSE')]:
            connection=self.setup_response(status=status,headers=headers)
            with patch('hhs.hf.client.http.client.HTTPSConnection',connection):
                if expected:
                    with self.assertRaises(Failure) as raised: http_transport('/api/models/a/b/revision/main?blobs=true',Limits(max_response_bytes=4))
                    self.assertEqual(raised.exception.code,expected)
                else:http_transport('/api/models/a/b/revision/main?blobs=true',Limits(max_response_bytes=4))
            self.assertEqual(self.reads,0);self.assertTrue(self.closed)

    def test_response_closes_socket_at_content_length_eof(self):
        connection=self.setup_response(FIXTURE.read_bytes(), close_at_eof=True)
        with patch('hhs.hf.client.http.client.HTTPSConnection',connection):
            result=inspect_repository(URL)
        self.assertEqual(result['status'],'OK')
        self.assertEqual(self.reads,1)
        self.assertEqual(result['accounting']['metadata_body_bytes_retrieved'],len(FIXTURE.read_bytes()))

    def test_partial_body_timeout_accounted(self):
        connection=self.setup_response(b'abc',failure=TimeoutError())
        with patch('hhs.hf.client.http.client.HTTPSConnection',connection):
            result=inspect_repository(URL)
        self.assertEqual(result['errors'][0]['code'],'TIMEOUT')
        self.assertEqual(result['accounting']['metadata_body_bytes_retrieved'],3)

    def test_transport_itself_refuses_content_routes(self):
        with patch('hhs.hf.client.http.client.HTTPSConnection',side_effect=AssertionError('no connection')):
            for target in ['/owner/repo/resolve/main/model.safetensors',
                           '/owner/repo/resolve/main/README.md',
                           '/api/models/a/b/revision/%252f?blobs=true']:
                with self.assertRaises(Failure):http_transport(target,Limits())

    def test_invalid_json_and_second_request(self):
        from hhs.hf.client import Response
        for body in [b'{broken', b'\xff', b'{"bad":NaN}', b'['*2000]:
            client=Client(transport=lambda *args:Response(200,{},body))
            with self.assertRaises(Failure) as raised:client.get_metadata(metadata_url(parse_url(URL)))
            self.assertEqual(raised.exception.code,'MALFORMED_RESPONSE')
            with self.assertRaises(Failure) as raised:client.get_metadata(metadata_url(parse_url(URL)))
            self.assertEqual(raised.exception.code,'LIMIT_REACHED')

    def test_limits_reject_unbounded_values(self):
        for kwargs in [{'timeout':float('nan')},{'timeout':float('inf')},{'timeout':0},
                       {'timeout':31},{'max_files':0},{'max_files':10001},
                       {'max_response_bytes':1048577}]:
            with self.assertRaises(ValueError):Limits(**kwargs)


class CLITests(unittest.TestCase):
    def test_offline_json_and_output_no_overwrite(self):
        args=['inspect-hf',URL,'--offline-fixture',str(FIXTURE)]
        output=io.StringIO()
        with patch('hhs.hf.client.http_transport',side_effect=AssertionError('no network')):
            with contextlib.redirect_stdout(output):self.assertEqual(main(args),0)
            result=json.loads(output.getvalue());validate_snapshot(result)
            self.assertEqual(result['mode'],'offline_fixture')
            self.assertEqual(result['accounting']['metadata_body_bytes_retrieved'],0)
            self.assertTrue(all(e['source']=='synthetic_fixture' for e in result['evidence']))
            with tempfile.TemporaryDirectory() as folder:
                path=Path(folder)/'snapshot.json'
                self.assertEqual(main(args+['--output',str(path)]),0)
                before=path.read_bytes()
                with contextlib.redirect_stderr(io.StringIO()):self.assertEqual(main(args+['--output',str(path)]),2)
                self.assertEqual(before,path.read_bytes())

    def test_invalid_fixture_diagnostics_do_not_leak(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'fixture.json';path.write_text('invalid secret content')
            output=io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(main(['inspect-hf',URL,'--offline-fixture',str(path)]),2)
            self.assertNotIn('secret content',output.getvalue())
            self.assertEqual(json.loads(output.getvalue())['errors'][0]['code'],'MALFORMED_RESPONSE')

    def test_cli_error_does_not_echo_arguments(self):
        stderr=io.StringIO()
        with contextlib.redirect_stderr(stderr),self.assertRaises(SystemExit):
            main(['inspect-hf',URL,'--timeout','secret-value'])
        self.assertNotIn('secret-value',stderr.getvalue())

    def test_metadata_minimization_and_redaction(self):
        from hhs.hf.client import Response
        data=json.loads(FIXTURE.read_text())
        token='hf_'+'x'*30
        data['tags']=[token,'api_key=private-value']
        data['cardData']['private_notes']='do not export'
        result=inspect_repository(URL,client=Client(transport=lambda *args:Response(200,{},json.dumps(data).encode())))
        serialized=json.dumps(result)
        for secret in [token,'private-value','do not export']:self.assertNotIn(secret,serialized)
        self.assertEqual(result['repository']['tags'],['<redacted>','<redacted>'])

    def test_malformed_file_and_flags(self):
        from hhs.hf.client import Response
        base=json.loads(FIXTURE.read_text())
        for change in [lambda d:d.update(private='yes'),lambda d:d.update(sha='not-a-commit'),
                       lambda d:d['siblings'][0].update(rfilename='../outside'),
                       lambda d:d['siblings'][0].update(size=-1),
                       lambda d:d['siblings'][0].update(size=True),
                       lambda d:d['siblings'][3].update(lfs='bad')]:
            data=copy.deepcopy(base);change(data)
            result=inspect_repository(URL,client=Client(transport=lambda *args:Response(200,{},json.dumps(data).encode())))
            self.assertEqual(result['errors'][0]['code'],'MALFORMED_RESPONSE')


if __name__=='__main__':unittest.main()
