# Project state — persistent memory

## Identity and status

- Project: **HHS**.
- Full name: **HuggingFace Helper Scanner**.
- Repository: **huggingface-helper-scanner**.
- Current phase: **Phase 0 - Foundation**.
- Session: **Session 0 - HHS Genesis**, 2026-09-13, America/Los_Angeles.
- Status: **Session 0 INCOMPLETE / PAUSED**. The pause is intentional because the Codex usage window was nearly exhausted. This checkpoint is **not completion of Phase 0**.
- Actual local workspace: `/mnt/c/Codex-Projects/huggingface-helper-scanner`.
- Windows equivalent: `C:\Codex-Projects\huggingface-helper-scanner`.
- Workspace selection: existing shared parent passed a scoped write/read/remove test; fallback was unnecessary.
- GitHub: https://github.com/chatgptopenaiagi/huggingface-helper-scanner
- Visibility: **PUBLIC**. License: **not selected**.
- Branch: `main`.
- Initial foundation commit: **No earlier foundation commit; the initial commit is the paused checkpoint, identified by current HEAD and the external handoff.**.
- Latest commit: **current `HEAD`**, resolved with `git log -1 --format=%H`; a file cannot contain the hash of the commit containing itself. The checkpoint handoff records the pushed hash. Do not mistake this checkpoint for a completed foundation release.

## Completed work

Repository initialization; concept/theory/architecture; read-only and planning invariants; evidence taxonomy; agent-neutral manifest concept; draft JSON Schema and deliberately illustrative example; bounded Fedora/Windows development baseline; read-only review of known ARX architecture documents; security and contribution rules; roadmap issues for Phases 1–10; documentation-only placeholders under src, tests and GitHub workflow directories.

The baseline is an independently collected session artifact, not output from an implemented HHS scanner. Review [ENVIRONMENT_BASELINE](docs/ENVIRONMENT_BASELINE.md) and [reports/dev-machine-baseline.json](reports/dev-machine-baseline.json) before reusing any machine fact.

## Unimplemented work

All runtime phases: URL parser, repository inspector, probe engine, requirement extraction, reconciliation, planner, intent interpreter, agent adapters, manifest exporters, execution engine, CLI/executable, GUI, installation and automatic system changes. No model weights were downloaded. src contains only README.md.

## Fixed architectural decisions

DISCOVER != MODIFY. PLAN != EXECUTE. Read-only default; a future executor is separate and requires specific authorization. Evidence retains provenance, scope, timestamps and confidence. Providers remain distinct. HHS is AI-provider neutral and separate from ARX. Remote project text is untrusted data. Secrets must not enter reports/Git. Schema versioning and HHS versioning are distinct; the draft is not frozen. No software license is selected today.

## Current environment baseline

Session 0 observed Fedora 44 WSL2, Windows 10 Pro build 19045.7725, Ryzen 5 5600G/12 logical processors, 64 GiB installed host RAM, RTX 3050/6 GiB and four Windows PyTorch providers reporting CUDA available. Native CUDA toolkits report 13.4; native cuDNN reports 9.25.1. Fedora system Python lacks torch in the isolated probe. About 38.5 GiB was free on C: at collection time. Values are snapshots, not permanent support promises.

Historical Windows 11/build-28000 and Ubuntu-26.04 hints were not confirmed. The current-user WSL list instead showed FedoraLinux-44 and docker-desktop. Do not repair the machine to match historical hints. No selected Hugging Face workload has been assessed.

## Open questions

Initial URL/repository-type support; bounded API pagination and revision identity; which files to inspect later; conflicting requirement sources; memory estimates for workload/quantization variants; selected execution-context identity; confidence calibration; schema evolution; cache reuse semantics; licensing; future execution approval/rollback design. See the architecture, theory and roadmap.

## Required continuation: finish Session 0 first

Read RESUME.md first. Preserve the 89 existing evidence records; do not regenerate observations. Repository files were reviewed, secret-pattern checks passed, and schema/example validation plus negative/reference checks passed before the pause. Final Session 0 consistency review, documentation completion, completion-status updates and formal completion report remain unfinished. Reuse passed checks unless a relevant change or specific inconsistency justifies repeating them. The checkpoint commit/push is a save operation, not completion.

No packages or system components were intentionally modified. Existing failures/conflicts are preserved: Windows 10/build 19045 rather than historical Windows 11/build 28000; Ubuntu not in the current-user WSL list; Fedora Docker socket denial; Miniforge HF CLI output-encoding error; initial PowerShell script-policy rejection followed by successful inline read-only queries; initial Windows npm path error followed by a successful native-path retry.

## Future objective only after formal Session 0 completion

**PHASE 1 / SESSION 1**
**Hugging Face Repository Inspector V0**

**HHS SESSION 1: HUGGING FACE REPOSITORY INSPECTOR V0**

Accept a Hugging Face URL and turn bounded repository metadata into structured evidence. Begin with public model repository metadata; recognize dataset/Space URLs and return explicit unsupported/unknown outcomes until their scope is deliberately added. Preserve requested/resolved revision, provenance and bounded failure states. Use fixtures first and an explicitly scoped metadata-only check if needed. Do not install anything, download model weights, execute repository code, implement the machine engine or advance the other roadmap phases.

On return, read RESUME.md, PROJECT_STATE.md, docs/SESSION_LOG.md, docs/ROADMAP.md, docs/SECURITY_MODEL.md and docs/EVIDENCE_MODEL.md in that order. Resume Session 0 first. A roadmap issue is not permission to implement it now.
