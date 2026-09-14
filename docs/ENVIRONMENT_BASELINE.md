# Development environment baseline

Collected during **Session 0, 2026-09-13 America/Los_Angeles** (UTC timestamps on 2026-09-14). Canonical artifact: [dev-machine-baseline.json](../reports/dev-machine-baseline.json).

This is a bounded manual development inventory, **not output from an implemented HHS scanner**. Historical hints were UNVERIFIED inputs. Evidence IDs, methods, scopes, timestamps and heuristic confidence are retained in the JSON. Exact personal user-home names are replaced with portable placeholders.

## Scope and classifications

Command resolution plus fixed conventional/historically known provider paths; nine existing Python interpreters; allowlisted Linux/Windows queries. No recursive disk scan, personal-file search, package changes, model downloads or environment activation. Python probes used isolated `-I -B`, excluding current-directory/user-site imports and disabling bytecode writes.

OBSERVED means directly obtained. VERIFIED is limited to explicit cross-checks (CPU, OS build identity, Fedora WSL2 context, GPU identity/capability, Linux cuDNN runtime/header agreement, and matching framework metadata/runtime versions). Package presence and CUDA availability calls are not model-run verification.

## Fedora and WSL

| Item | Result / scope |
|---|---|
| Fedora | 44 (WSL), x86_64; UID 1000, username redacted |
| Kernel | 6.18.33.2-microsoft-standard-WSL2 |
| Init | systemd reported running |
| RAM | 33,322,299,392 bytes total (~31.03 GiB); 31,257,235,456 available at initial query; 8 GiB swap |
| CPU | AMD Ryzen 5 5600G, 6 cores/12 logical processors; Linux and Windows agree |
| WSL | 2.7.14.0; current Fedora registration is WSL2 |
| Current-user registrations | FedoraLinux-44 and docker-desktop, both listed Running/WSL2 |
| WSLg | 1.0.73.2 reported; graphical functionality not exercised this session |
| Windows mount | C: at /mnt/c through 9p/DrvFS; root ext4 on /dev/sdd |
| Workspace | /mnt/c/Codex-Projects/huggingface-helper-scanner; scoped write/read/remove test passed |
| Interop setting | enabled; appendWindowsPath=false; unchanged |

## Windows

CIM and WSL host-version output agree on **Windows 10 Pro / build 19045**; WSL reports full build **10.0.19045.7725**. Windows PowerShell **5.1.19041.7725** executed allowlisted queries. Installed RAM totals **68,719,476,736 bytes (64 GiB)**; OS-visible physical memory is **68,047,577,088 bytes**, a distinct measurement.

Historical **Windows 11 Pro/build around 28000** is contradicted by current observations. **Ubuntu-26.04** was not listed for the current Windows user; global absence across other users/locations is UNKNOWN. No repair was attempted. A Windows script-file invocation was blocked by execution policy; inline read-only queries succeeded without changing that policy.

## Storage constraint

C: total **479,295,156,224 bytes**, available approximately **41.325 billion bytes (~38.5 GiB)** at collection. Linux root reports **987,403,431,936 bytes** available inside its virtual filesystem. These figures are not interchangeable or additive. The actual HHS workspace is on C:, and future model/cache/build budgets must use the selected filesystem's capacity. No model-size requirement was selected, so workload fit is UNKNOWN. Small free-space differences between sequential OS queries are preserved as changing snapshots.

## NVIDIA, CUDA and cuDNN

- RTX 3050, **6144 MiB/6 GiB**, compute capability **8.6**; checked through NVIDIA tools, Windows CIM identity and a framework device query. AMD Radeon Graphics was also reported; its compute support was not tested.
- NVIDIA driver **616.92**; Windows CIM encoding **32.0.16.1692**. CUDA driver API reports **13040**, represented as **13.4** capability.
- Fedora nvcc **13.4.59**, `/usr/local/cuda-13.4`; Windows nvcc **13.4.46**, `C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4`.
- Native cuDNN version queries return **92501 / 9.25.1** on both sides. Fedora's header independently agrees. No convolution or native compilation ran this session.
- Historical Windows Toolkit 13.3 work is not evidence of the selected toolkit now; the known queried provider is 13.4. Other toolkits were not exhaustively searched.

Driver capability, installed toolkit, native cuDNN and framework-bundled runtimes are independent layers. Differences are not automatically incompatibilities.

## Python and framework providers

All versions below were freshly observed; named provider IDs are preserved in JSON.

| Provider | Python | PyTorch | CUDA reported available / runtime | Framework cuDNN |
|---|---|---|---|---|
| Fedora system | 3.14.7 | NOT_FOUND in isolated interpreter | Not tested | Not tested |
| Windows C:\Python314 | 3.14.7 | NOT_FOUND | Not tested | Not tested |
| Windows preview | 3.15.0b4 | NOT_FOUND | Not tested | Not tested |
| Windows C:\AI\pytorch-cu132 | 3.14.7 | 2.14.0+cu132 | true / 13.2 | 92400 / 9.24.0 |
| Windows Anaconda | 3.14.7 | NOT_FOUND | Not tested | Not tested |
| Pinokio Miniforge | 3.10.20 | NOT_FOUND | Not tested | Not tested |
| LocalAI CUDA 13.3 provider | 3.12.14 | 2.15.0a0+gita6066c4 | true / 13.3 | null / not reported by this build |
| theDAW application venv | 3.12.13 | 2.14.0+cu130 | true / 13.0 | 92400 / 9.24.0 |
| theDAW underfit venv | 3.10.20 | 2.7.1+cu128 | true / 12.8 | 90701 / 9.7.1 |

The four torch imports reported RTX 3050 and capability (8,6). No tensor computation, model loading, inference or training was performed in this session. A historical container PyTorch environment was not run; its current status remains UNVERIFIED. Native cuDNN presence does not change the LocalAI build's null backend report.

Other freshly observed package metadata includes NumPy **2.5.3/2.4.6/2.5.2/2.2.6** in separate providers; Transformers **5.17.0** in theDAW; huggingface_hub **1.31.0** in Windows system/theDAW, **1.20.1** in Miniforge and **1.15.0** in underfit; safetensors **0.8.0/0.7.0** in those app environments. No TensorRT module was found in the nine tested interpreter metadata sets; machine-wide availability is UNKNOWN.

## Development tools

| Tool | Fedora observation | Windows observation |
|---|---|---|
| Git | 2.55.0 | 2.55.0.windows.5 |
| Git LFS | `git lfs version` failed: subcommand unavailable in current context | 3.7.1 |
| GitHub CLI | 2.97.0 | 2.100.0 |
| Codex CLI | 0.154.0 | Not checked; not an HHS dependency |
| pip | 26.0.1 | 26.2.1 in several providers; preview 26.1.2 |
| Conda | NOT_FOUND on PATH/fixed conventional Linux roots | Anaconda 26.7.2; Miniforge package metadata 26.5.3 |
| GCC / G++ | 16.2.1 | Not checked |
| Clang | 22.1.8 | 22.1.8 |
| CMake | 4.3.0 | 4.4.3 |
| Ninja | 1.13.2 | 1.13.2 |
| Rust / Cargo | NOT_FOUND on PATH and named user paths | rustc 1.98.1; cargo 1.98.1; rustup 1.29.1 |
| Node / npm | 22.23.1 / 10.9.8 | 26.8.1 / 11.19.0 |
| Docker client | 29.8.0 | 29.7.2 |
| MSVC | Windows provider accessed through interop | 19.51.36257; toolset path 14.51.36231 |
| Hugging Face CLI | NOT_FOUND on current PATH/fixed user path | C:\Python314\Scripts\hf.exe reports 1.31.0 |

Version/banner queries do not prove complete builds. Fedora Docker daemon access failed on socket permissions as the current user; no escalation or service changes were attempted. Docker Desktop being listed as a running distro does not itself prove its API is healthy.

## Errors and limits retained

Miniforge `hf version` returned an output-encoding error; metadata still establishes its huggingface_hub package version. The first Windows npm invocation used a Linux-style argument incorrectly; a native-Windows-path retry returned 11.19.0. This is a probe construction error, not an npm installation diagnosis.

No comprehensive tool search, credentials/cache inventory, Flutter/Android recheck, software compilation, container workload, performance benchmark or real Hugging Face compatibility assessment was done. Failure and non-detection are legitimate scoped evidence, not instructions to install or repair.
