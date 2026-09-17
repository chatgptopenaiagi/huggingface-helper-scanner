"""Owned fixed read-only scripts. Never built from repository or report instructions."""

HOST = r'''
import json, os, sys
from pathlib import Path

def read(path, limit):
    with open(path, encoding='utf-8') as f: return f.read(limit)
u = os.uname()
release = {}
for line in read('/etc/os-release', 16384).splitlines():
    key, sep, value = line.partition('=')
    if key in ('PRETTY_NAME','VERSION_ID'): release[key] = value.strip('"')
cpu = next((s.split(':',1)[1].strip() for s in read('/proc/cpuinfo',65536).splitlines() if s.startswith('model name')), 'UNKNOWN')
mem = next((int(s.split()[1])*1024 for s in read('/proc/meminfo',16384).splitlines() if s.startswith('MemTotal:')), None)
print(json.dumps(dict(os=sys.platform, name=release.get('PRETTY_NAME','UNKNOWN'), version=release.get('VERSION_ID','UNKNOWN'), build=u.release, architecture=u.machine, wsl='microsoft' in u.release.lower(), cpu_model=cpu, logical_processors=os.cpu_count(), memory_bytes=mem)))
'''

PYTHON = r'''
import sys, os, json, sysconfig
from pathlib import Path
# -I -B -S excludes project/user modules, sitecustomize and executable .pth hooks.
exe = Path(sys.executable)
root = exe.parent
if root.name.lower() in ('scripts','bin'): root = root.parent
venv = (root / 'pyvenv.cfg').is_file()
conda = (root / 'conda-meta').is_dir()
if venv:
    sys.prefix = sys.exec_prefix = str(root)
else:
    root = Path(sys.prefix)
paths = [root / 'Lib' / 'site-packages'] if os.name == 'nt' else [root / 'lib' / ('python%d.%d' % sys.version_info[:2]) / 'site-packages', root / 'lib64' / ('python%d.%d' % sys.version_info[:2]) / 'site-packages']
for p in paths:
    if p.is_dir() and str(p) not in sys.path: sys.path.append(str(p))
import importlib.metadata as md
out = dict(version=sys.version.split()[0], environment_type='conda' if conda else 'venv' if venv else 'system')
try: out['pip'] = dict(state='OBSERVED', version=md.version('pip'))
except md.PackageNotFoundError: out['pip'] = dict(state='NOT_FOUND')
except Exception: out['pip'] = dict(state='ERROR', error_code='METADATA_ERROR')
try:
    import torch
except ModuleNotFoundError as e:
    out['torch'] = dict(state='NOT_FOUND') if e.name == 'torch' else dict(state='ERROR', error_code='IMPORT_ERROR')
except Exception:
    out['torch'] = dict(state='ERROR', error_code='IMPORT_ERROR')
else:
    t = dict(state='OBSERVED', version=str(torch.__version__))
    try:
        t.update(cuda_available=bool(torch.cuda.is_available()), cuda_runtime=torch.version.cuda,
                 cudnn_runtime=torch.backends.cudnn.version(), gpus=[])
        if t['cuda_available']:
            count = torch.cuda.device_count()
            t['gpus'] = [dict(name=torch.cuda.get_device_name(i), compute_capability=list(torch.cuda.get_device_capability(i))) for i in range(min(count,8))]
            t['gpus_truncated'] = count > 8
    except Exception: t.update(runtime_state='ERROR', error_code='RUNTIME_QUERY_ERROR')
    out['torch'] = t
print(json.dumps(out))
'''

WINDOWS = r'''
$ErrorActionPreference='Stop'; [Console]::OutputEncoding=[System.Text.UTF8Encoding]::new($false)
$o=Get-CimInstance Win32_OperatingSystem
$c=@(Get-CimInstance Win32_Processor)
$m=Get-CimInstance Win32_ComputerSystem
[ordered]@{os='windows';name=$o.Caption;version=$o.Version;build=$o.BuildNumber;architecture=$o.OSArchitecture;wsl=$false;cpu_model=($c.Name -join '; ');logical_processors=[int]$m.NumberOfLogicalProcessors;memory_bytes=[long]$m.TotalPhysicalMemory}|ConvertTo-Json -Compress
'''

# Metadata-only enumeration under one explicitly selected root; no activation or conda plugins.
CONDA = r'''
import json, os, sys
from pathlib import Path
root=Path(sys.argv[1])
if not root.is_dir() or not (root/'conda-meta').is_dir():
    print(json.dumps(dict(state='NOT_FOUND'))); sys.exit(0)
def row(p):
    py=p/('python.exe' if os.name=='nt' else 'bin/python')
    return dict(path=str(p), python_path=str(py) if py.is_file() else None)
rows=[row(root)]; truncated=False
folder=root/'envs'
if folder.is_dir():
    with os.scandir(folder) as entries:
        for i, entry in enumerate(entries):
            if i>=16: truncated=True; break
            if entry.is_dir(follow_symlinks=False) and (Path(entry.path)/'conda-meta').is_dir(): rows.append(row(Path(entry.path)))
exe=root/('Scripts/conda.exe' if os.name=='nt' else 'bin/conda')
print(json.dumps(dict(base_path=str(root),executable=str(exe) if exe.is_file() else None,environments=rows,truncated=truncated)))
'''
