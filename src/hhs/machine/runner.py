"""Finite command execution with bounded pipes and no inherited credential environment."""
from dataclasses import dataclass
import math
import os
import signal
import subprocess
import threading
import time

OUTPUT_LIMIT = 65536  # Each pipe, retained only in memory; never publish raw streams.

@dataclass(frozen=True)
class Spec:
    probe_id: str
    provider_id: str
    kind: str
    candidates: tuple
    scope: str

@dataclass
class Result:
    stdout: str = ''
    stderr: str = ''
    returncode: int = 0
    failure: str | None = None


def child_environment():
    # Construct, do not copy os.environ. No HOME, tokens, proxy, PYTHONPATH or tool hooks.
    return {'PATH': 'C:\\Windows\\System32' if os.name == 'nt' else '/usr/bin:/bin',
            'SystemRoot': 'C:\\Windows', 'WINDIR': 'C:\\Windows',
            'LANG': 'C.UTF-8', 'LC_ALL': 'C.UTF-8',
            'PYTHONDONTWRITEBYTECODE': '1', 'CUDA_CACHE_DISABLE': '1',
            'CONDA_NO_PLUGINS': 'true', 'PIP_DISABLE_PIP_VERSION_CHECK': '1'}


def run_command(spec, timeout):
    if not math.isfinite(timeout) or not 0 < timeout <= 30:
        raise ValueError('invalid timeout')
    deadline = time.monotonic() + timeout
    for argv in spec.candidates:
        if not argv or not os.path.isabs(argv[0]):
            return Result(failure='INVALID_EXECUTABLE')
        if time.monotonic() >= deadline:
            return Result(failure='TIMEOUT')
        try:
            process = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE, shell=False,
                                       cwd='C:\\Windows' if os.name == 'nt' else '/',
                                       env=child_environment(), start_new_session=os.name != 'nt')
        except FileNotFoundError:
            continue  # Only executable lookup failure permits the next fixed candidate.
        except PermissionError:
            return Result(failure='PERMISSION_DENIED')
        except OSError:
            return Result(failure='START_ERROR')
        streams = [bytearray(), bytearray()]
        overflow = threading.Event()
        read_error = threading.Event()
        def collect(pipe, target):
            try:
                while True:
                    chunk = pipe.read1(4096)
                    if not chunk: break
                    remaining = OUTPUT_LIMIT + 1 - len(target)
                    target.extend(chunk[:max(0, remaining)])
                    if len(target) > OUTPUT_LIMIT:
                        overflow.set()
                        break
            except (OSError, ValueError):
                read_error.set()
            finally:
                pipe.close()
        threads = [threading.Thread(target=collect, args=(pipe, buf), daemon=True)
                   for pipe, buf in zip((process.stdout, process.stderr), streams)]
        for thread in threads: thread.start()
        failure = None
        while process.poll() is None or any(t.is_alive() for t in threads):
            if overflow.is_set(): failure = 'OUTPUT_LIMIT'; break
            if time.monotonic() >= deadline: failure = 'TIMEOUT'; break
            time.sleep(0.01)
        if overflow.is_set(): failure = 'OUTPUT_LIMIT'
        if failure:
            try:
                if os.name != 'nt': os.killpg(process.pid, signal.SIGKILL)
                else: process.kill()
            except (ProcessLookupError, OSError): pass
        try: process.wait(timeout=0.5)
        except subprocess.TimeoutExpired: failure = failure or 'TERMINATION_ERROR'
        for thread in threads: thread.join(timeout=0.1)
        if read_error.is_set(): failure = failure or 'READ_ERROR'
        if failure: return Result(failure=failure)  # Drop partial raw output, including secrets.
        try:
            return Result(streams[0].decode('utf-8-sig'), streams[1].decode('utf-8-sig'), process.returncode)
        except UnicodeError:
            return Result(failure='OUTPUT_ENCODING')
    return Result(failure='NOT_FOUND')
