"""Synthetic bounded-probe results; no installed packages or host probes required."""
import copy
import json
from pathlib import Path
import unittest

from hhs.machine.engine import inspect_machine, provider, validate_snapshot, compare_history
from hhs.machine.runner import Result

F = json.loads((Path(__file__).parent / 'fixtures/machine.json').read_text())

class FakeRunner:
    def __init__(self, overrides=None):
        self.overrides = overrides or {}
        self.calls = []

    def __call__(self, spec, timeout):
        self.calls.append((spec, timeout))
        if spec.probe_id in self.overrides:
            value = self.overrides[spec.probe_id]
            return value if isinstance(value, Result) else Result(stdout=json.dumps(value))
        if spec.kind == 'host': return Result(stdout=json.dumps(F['host']))
        if spec.kind == 'windows': return Result(stdout=json.dumps(F['windows']))
        if spec.kind == 'python': return Result(stdout=json.dumps(F['python']))
        if spec.kind == 'conda': return Result(stdout=json.dumps(F['conda']))
        if spec.kind == 'nvidia': return Result(stdout=F['nvidia'])
        if spec.kind == 'driver': return Result(stdout='CUDA Version: 13.1')
        if spec.kind == 'docker': return Result(stdout=json.dumps(F['docker']))
        return Result(stdout='tool version 1.2.3')

class MachineTests(unittest.TestCase):
    def scan(self, overrides=None, **kwargs):
        self.runner = FakeRunner(overrides)
        return inspect_machine(runner=self.runner, executable='/usr/bin/python3', **kwargs)

    def evidence(self, result, probe):
        return next(e for e in result['evidence'] if e['probe_id'] == probe)

    def test_provider_identity_isolation(self):
        a=provider('/usr/bin/python3'); b=provider(r'C:\Python314\python.exe')
        self.assertNotEqual(a['provider_id'],b['provider_id'])
        self.assertEqual(b,provider('/mnt/c/Python314/python.exe'))
        self.assertNotEqual(b,provider(r'C:\Other\python.exe'))

    def test_windows_python_provider(self):
        p=provider(r'C:\Python314\python.exe'); r=self.scan(providers=[r'C:\Python314\python.exe'])
        self.assertIn(p,r['providers']); self.assertEqual(p['host'],'windows-host')

    def test_fedora_python_provider(self):
        r=self.scan(); self.assertEqual(r['hosts'][0]['observation']['name'],'Fedora Linux')
        self.assertEqual(r['providers'][0]['host'],'local-host')

    def test_torch_present_and_cuda_available(self):
        r=self.scan({'python-0':F['torch']}); e=self.evidence(r,'python-0')
        self.assertEqual(e['observation']['torch']['state'],'OBSERVED')
        self.assertTrue(e['observation']['torch']['cuda_available'])

    def test_torch_not_found_scoped(self):
        e=self.evidence(self.scan(),'python-0')
        self.assertEqual(e['observation']['torch']['state'],'NOT_FOUND')
        self.assertTrue(e['provider_id']); self.assertEqual(e['state'],'OBSERVED')

    def test_cuda_unavailable(self):
        data=copy.deepcopy(F['torch']); data['torch'].update(cuda_available=False,gpus=[])
        e=self.evidence(self.scan({'python-0':data}),'python-0')
        self.assertFalse(e['observation']['torch']['cuda_available'])

    def test_nvidia_missing(self):
        e=self.evidence(self.scan({'nvidia':Result(failure='NOT_FOUND')}),'nvidia')
        self.assertEqual(e['state'],'NOT_FOUND')

    def test_nvidia_error(self):
        e=self.evidence(self.scan({'nvidia':Result(returncode=1,stderr='driver failure')}),'nvidia')
        self.assertEqual(e['state'],'ERROR'); self.assertNotIn('driver failure',json.dumps(e))

    def test_docker_permission_denied(self):
        e=self.evidence(self.scan({'docker':Result(returncode=1,stderr='permission denied')}),'docker')
        self.assertEqual(e['state'],'ERROR'); self.assertEqual(e['stderr_classification'],'PERMISSION_DENIED')

    def test_docker_absent(self):
        self.assertEqual(self.evidence(self.scan({'docker':Result(failure='NOT_FOUND')}),'docker')['state'],'NOT_FOUND')

    def test_command_timeout(self):
        e=self.evidence(self.scan({'docker':Result(failure='TIMEOUT')}),'docker')
        self.assertEqual(e['state'],'ERROR'); self.assertEqual(e['error_code'],'TIMEOUT')
        self.assertTrue(all(0<t<=10 for _,t in self.runner.calls))

    def test_malformed_output(self):
        for output in ['bad', '{"version":NaN}', '[]', '{}']:
            e=self.evidence(self.scan({'python-0':Result(stdout=output)}),'python-0')
            self.assertEqual(e['error_code'],'MALFORMED_OUTPUT')

    def test_conflicting_os_evidence(self):
        r=self.scan(); compare_history(r,[{'provider_id':'local-host','subject':'host','field':'name','value':'Ubuntu','source':'synthetic:old','timestamp':'2020-01-01T00:00:00Z'}])
        self.assertEqual(r['conflicts'][0]['state'],'CONFLICT'); validate_snapshot(r)
        self.assertEqual(len(r['conflicts'][0]['evidence_refs']),2)

    def test_multiple_cuda_sources(self):
        r=self.scan({'python-0':F['torch']})
        self.assertEqual(self.evidence(r,'python-0')['observation']['torch']['cuda_runtime'],'13.0')
        self.assertEqual(self.evidence(r,'nvidia-driver')['observation']['driver_cuda_capability'],'13.1')
        self.assertTrue(any(e['probe_id']=='nvcc' for e in r['evidence']))

    def test_conda_enumeration(self):
        r=self.scan(conda_roots=[r'C:\Tools\miniforge'])
        e=self.evidence(r,'conda-0'); self.assertEqual(len(e['observation']['environments']),1)
        self.assertEqual(e['observation']['environments'][0]['python_path'],r'C:\Tools\miniforge\python.exe')
        self.assertEqual(len([s for s,_ in self.runner.calls if s.kind=='python']),1)

    def test_secret_redaction(self):
        data=copy.deepcopy(F['torch']); secret='hf_'+'x'*32; data['torch']['version']=secret
        data['private_notes']='never export'; r=self.scan({'python-0':data})
        self.assertNotIn(secret,json.dumps(r)); self.assertNotIn('never export',json.dumps(r))

    def test_provider_scoped_failure(self):
        r=self.scan({'python-1':Result(failure='TIMEOUT')},providers=[r'C:\Python314\python.exe'])
        self.assertEqual(self.evidence(r,'python-0')['state'],'OBSERVED')
        self.assertEqual(self.evidence(r,'python-1')['state'],'ERROR')
        self.assertNotEqual(self.evidence(r,'python-0')['provider_id'],self.evidence(r,'python-1')['provider_id'])

    def test_reference_integrity(self):
        r=self.scan(); validate_snapshot(r); r['toolchains'][0]['evidence_refs']=['absent']
        with self.assertRaises(ValueError):validate_snapshot(r)

    def test_structural_validation(self):
        r=self.scan(); r['evidence'][0]['timeout']=0
        with self.assertRaises(ValueError):validate_snapshot(r)

    def test_invalid_limits_no_commands(self):
        for t in [0,-1,31,float('inf'),float('nan')]:
            runner=FakeRunner()
            with self.assertRaises(ValueError):inspect_machine(timeout=t,runner=runner)
            self.assertFalse(runner.calls)

    def test_paths_require_selected_absolute_interpreter(self):
        for path in ['python','../python','/tmp/tool.sh','https://evil/python.exe','/tmp/a\n/python']:
            with self.assertRaises(ValueError):provider(path)

    def test_windows_scope_separate_host(self):
        r=self.scan(scope='windows'); self.assertEqual(r['hosts'][0]['provider_id'],'windows-host')
        self.assertTrue(all(p['host']=='windows-host' for p in r['providers']))

    def test_output_budget_failure(self):
        e=self.evidence(self.scan({'docker':Result(failure='OUTPUT_LIMIT')}),'docker')
        self.assertEqual(e['state'],'ERROR'); self.assertEqual(e['error_code'],'OUTPUT_LIMIT')

    def test_import_failure_is_not_missing(self):
        data=copy.deepcopy(F['python']); data['torch']={'state':'ERROR','error_code':'IMPORT_ERROR'}
        r=self.scan({'python-0':data})
        self.assertEqual(self.evidence(r,'python-0')['observation']['torch']['state'],'ERROR')
        self.assertTrue(r['errors'])

if __name__=='__main__': unittest.main()
