"""Synthetic fixtures; no network or inspected repository code execution."""
import copy
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from hhs.hf.url_parser import parse_url, InputError
from hhs.hf.client import Client, Limits, Failure, Response
from hhs.hf.inspector import inspect_repository, validate_snapshot

URL = 'https://huggingface.co/example-owner/example-model'
FIXTURE = Path(__file__).parent / 'fixtures/model.json'


class ParserTests(unittest.TestCase):
    def test_supported_forms(self):
        for tail, revision, path in [('', None, None), ('/', None, None),
                ('/tree/main', 'main', None), ('/tree/v1', 'v1', None),
                ('/blob/main/config.json', 'main', 'config.json'),
                ('/resolve/main/config.json', 'main', 'config.json'),
                ('/tree/refs%2Fpr%2F1/subdir', 'refs/pr/1', 'subdir')]:
            with self.subTest(tail=tail):
                result = parse_url(URL + tail)
                self.assertEqual(result['repo_id'], 'example-owner/example-model')
                self.assertEqual(result['requested_revision'], revision)
                self.assertEqual(result['requested_path'], path)

    def test_other_repo_types(self):
        for prefix, kind in [('datasets/', 'dataset'), ('spaces/', 'space')]:
            self.assertEqual(parse_url('https://huggingface.co/' + prefix + 'owner/repo')['repo_type'], kind)

    def test_invalid_and_unsupported(self):
        for url in ['', 'not a URL', 'http://huggingface.co/a/b',
                'https://evil.test/a/b', 'https://huggingface.co.evil.test/a/b',
                'https://huggingface.co/owner', 'https://huggingface.co/',
                'https://user:password@huggingface.co/a/b',
                'https://huggingface.co:443/a/b', URL+'?token=hidden',
                URL+'#fragment', URL+'/blob/main', URL+'/tree',
                URL+'/commit/main', URL+'/tree/main/../secret',
                URL+'/tree/%252e%252e', URL+'/tree/%0a',
                URL+'/tree/main/%2fetc', URL+'/tree/main/x\\y',
                URL+'/tree/main//x', URL+'\n']:
            with self.subTest(url=url):
                with self.assertRaises(InputError): parse_url(url)

    def test_revision_override(self):
        self.assertEqual(parse_url(URL, 'refs/pr/1')['requested_revision'], 'refs/pr/1')
        with self.assertRaises(InputError): parse_url(URL+'/tree/main', 'other')


class InspectorTests(unittest.TestCase):
    def run_fixture(self, data=None, status=200, headers=None, limits=None):
        calls = []
        body = json.dumps(data if data is not None else json.loads(FIXTURE.read_text())).encode()
        def transport(target, limits):
            calls.append(target)
            return Response(status, headers or {}, body)
        client = Client(limits=limits, transport=transport)
        result = inspect_repository(URL, client=client)
        validate_snapshot(result)
        return result, calls

    def test_metadata_files_lfs_and_evidence(self):
        result, calls = self.run_fixture()
        self.assertEqual(result['status'], 'OK')
        self.assertEqual(result['source']['resolved_revision'], 'a'*40)
        self.assertIsNone(result['source']['requested_revision'])
        self.assertEqual(result['source']['effective_revision'], 'main')
        self.assertEqual(len(result['files']), 6)
        weight = result['files'][3]
        self.assertEqual(weight['lfs']['sha256'], 'c'*64)
        self.assertEqual(weight['size_bytes'], 123456789)
        self.assertFalse(weight['downloaded'])
        self.assertEqual(weight['role_state'], 'INFERRED')
        self.assertEqual(len(calls), 1)
        self.assertIn('/revision/main?blobs=true', calls[0])
        self.assertEqual(result['accounting']['model_payload_bytes_retrieved'], 0)

    def test_oversized_readme_and_commands_never_fetched_or_executed(self):
        with patch('subprocess.run', side_effect=AssertionError('must not execute')):
            result, calls = self.run_fixture()
        self.assertFalse(result['files'][0]['downloaded'])
        self.assertEqual(result['files'][0]['content_policy'], 'METADATA_ONLY')
        self.assertEqual(len(calls), 1)
        self.assertNotIn('pip install', json.dumps(result))

    def test_weights_formats_metadata_only(self):
        data = json.loads(FIXTURE.read_text())
        data['siblings'] = [{'rfilename': 'model.'+ext, 'size': 100}
                            for ext in ['safetensors', 'gguf', 'bin', 'pt', 'pth', 'ckpt', 'onnx']]
        result, calls = self.run_fixture(data)
        self.assertTrue(all(f['role']=='model_weight' and not f['downloaded'] for f in result['files']))
        self.assertEqual(len(calls), 1)

    def test_gated_private_metadata(self):
        for field, value in [('private', True), ('gated', 'manual')]:
            data = json.loads(FIXTURE.read_text()); data[field] = value
            result, _ = self.run_fixture(data)
            self.assertEqual(result['repository'][field], value)
            self.assertIn(field.upper(), [w['code'] for w in result['warnings']])

    def test_http_failures(self):
        for status, headers, code in [(404, {}, 'NOT_FOUND'), (401, {}, 'AUTH_REQUIRED'),
                (403, {}, 'AUTH_REQUIRED'), (403, {'x-error-code':'GatedRepo'}, 'GATED'),
                (429, {}, 'RATE_LIMITED'), (500, {}, 'NETWORK_ERROR'),
                (302, {'location':'https://evil.test/weights.bin'}, 'REDIRECT_BLOCKED'),
                (418, {}, 'UNKNOWN')]:
            with self.subTest(status=status):
                result, calls = self.run_fixture({}, status, headers)
                self.assertEqual(result['errors'][0]['code'], code)
                self.assertEqual(len(calls), 1)

    def test_timeout_network(self):
        for exception, expected in [(TimeoutError(), 'TIMEOUT'), (OSError('secret detail'), 'NETWORK_ERROR')]:
            def transport(*args): raise exception
            result=inspect_repository(URL, client=Client(transport=transport))
            self.assertEqual(result['errors'][0]['code'], expected)
            self.assertNotIn('secret detail', json.dumps(result))

    def test_malformed_response(self):
        for data in [[], {}, {'id':'wrong/repo'}, {'id':'example-owner/example-model','sha':'a'*40,'siblings':'wrong'}]:
            result, _ = self.run_fixture(data)
            self.assertEqual(result['errors'][0]['code'], 'MALFORMED_RESPONSE')

    def test_response_limit(self):
        result, _ = self.run_fixture(limits=Limits(max_response_bytes=128))
        self.assertEqual(result['errors'][0]['code'], 'RESPONSE_TOO_LARGE')

    def test_file_limit_and_pagination(self):
        result, _ = self.run_fixture(limits=Limits(max_files=2))
        self.assertEqual(len(result['files']), 2)
        self.assertFalse(result['coverage']['complete'])
        result, calls = self.run_fixture(headers={'link':'<https://evil.test>; rel="next"'})
        self.assertFalse(result['coverage']['complete'])
        self.assertEqual(len(calls), 1)

    def test_unsupported_types_do_not_request(self):
        for prefix in ['datasets', 'spaces']:
            with patch('hhs.hf.client.http_transport', side_effect=AssertionError('no network')):
                result=inspect_repository('https://huggingface.co/'+prefix+'/owner/repo')
            self.assertEqual(result['errors'][0]['code'], 'UNSUPPORTED')

    def test_invalid_input_does_not_echo_secrets(self):
        result=inspect_repository(URL+'?token=secret-value')
        self.assertEqual(result['errors'][0]['code'], 'INVALID')
        self.assertNotIn('secret-value', json.dumps(result))

    def test_schema_and_reference_negative_cases(self):
        result, _ = self.run_fixture()
        for change in [lambda x:x.pop('security'),
                lambda x:x['files'][0].update(downloaded=True),
                lambda x:x['files'][0].update(evidence_refs=['NO-SUCH-ID']),
                lambda x:x['evidence'][0].update(confidence=2)]:
            broken=copy.deepcopy(result);change(broken)
            with self.assertRaises(ValueError): validate_snapshot(broken)

    def test_raw_payload_routes_refused(self):
        client=Client(transport=lambda *args: self.fail('transport must not run'))
        for url in [URL+'/resolve/main/model.safetensors', URL+'/resolve/main/README.md',
                    'https://evil.test/api/models/a/b']:
            with self.assertRaises(Failure): client.get_metadata(url)


if __name__ == '__main__': unittest.main()
