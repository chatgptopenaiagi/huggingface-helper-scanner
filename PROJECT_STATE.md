# Project state — persistent memory

## Identity and status

- Project: **HHS**.
- Full name: **HuggingFace Helper Scanner**.
- Repository: **huggingface-helper-scanner**.
- Current phase: **Phase 1 - Hugging Face Repository Inspector**.
- Session: **Session 1 - Repository Inspector V0**, 2026-09-14, America/Los_Angeles.
- Status: **Session 1 COMPLETE / Phase 1 V0 COMPLETE**, with the failed live check documented and the EOF fix validated offline. Session 0 / Phase 0 remains COMPLETE. The user explicitly authorized Phase 1 only on 2026-09-14.
- Session 1 starting commit: `b3068e6a68fd69193c226507c2d51a318edb12a5`; clean local main and remote main matched before implementation.
- Actual local workspace: `/mnt/c/Codex-Projects/huggingface-helper-scanner`.
- Windows equivalent: `C:\Codex-Projects\huggingface-helper-scanner`.
- Workspace selection: existing shared parent passed a scoped write/read/remove test; fallback was unnecessary.
- GitHub: https://github.com/chatgptopenaiagi/huggingface-helper-scanner
- Visibility: **PUBLIC**. License: **not selected**.
- Branch: `main`.
- Initial foundation commit: `98d89c8760e1f61925cc5feb2d05dfb674add5e9` — the original paused checkpoint, preserved unchanged.
- Latest commit: **current `HEAD`**, resolved with `git log -1 --format=%H`; a file cannot contain the hash of the commit containing itself. Session 0 completion is `b3068e6a68fd69193c226507c2d51a318edb12a5`; Session 1 uses normal forward history.

## Completed work

Repository initialization; concept/theory/architecture; read-only and planning invariants; evidence taxonomy; agent-neutral manifest concept; draft JSON Schema and deliberately illustrative example; bounded Fedora/Windows development baseline; read-only review of known ARX architecture documents; security and contribution rules; roadmap issues for Phases 1–10; Session 0 documentation-only placeholders. Session 1 adds a standard-library Python repository metadata inspector, CLI, synthetic fixture, 29 tests and V0 snapshot validation. GitHub workflow remains documentation-only.

The baseline is an independently collected session artifact, not output from an implemented HHS scanner. Review [ENVIRONMENT_BASELINE](docs/ENVIRONMENT_BASELINE.md) and [reports/dev-machine-baseline.json](reports/dev-machine-baseline.json) before reusing any machine fact.

## Unimplemented work

Machine probe engine, requirement extraction, compatibility reconciliation, planner, intent interpreter, agent adapters, stable manifest exporters, execution engine, packaged executable, GUI, installation and automatic system changes. Model-only repository metadata parsing/inspection and a Python module CLI now exist. No model weights or other repository file contents were downloaded.

## Fixed architectural decisions

DISCOVER != MODIFY. PLAN != EXECUTE. Read-only default; a future executor is separate and requires specific authorization. Evidence retains provenance, scope, timestamps and confidence. Providers remain distinct. HHS is AI-provider neutral and separate from ARX. Remote project text is untrusted data. Secrets must not enter reports/Git. Schema versioning and HHS versioning are distinct; the draft is not frozen. No software license is selected today.

## Current environment baseline

Session 0 observed Fedora 44 WSL2, Windows 10 Pro build 19045.7725, Ryzen 5 5600G/12 logical processors, 64 GiB installed host RAM, RTX 3050/6 GiB and four Windows PyTorch providers reporting CUDA available. Native CUDA toolkits report 13.4; native cuDNN reports 9.25.1. Fedora system Python lacks torch in the isolated probe. About 38.5 GiB was free on C: at collection time. Values are snapshots, not permanent support promises.

Historical Windows 11/build-28000 and Ubuntu-26.04 hints were not confirmed. The current-user WSL list instead showed FedoraLinux-44 and docker-desktop. Do not repair the machine to match historical hints. No selected Hugging Face workload has been assessed.

## Open questions

Initial URL/repository-type support; bounded API pagination and revision identity; which files to inspect later; conflicting requirement sources; memory estimates for workload/quantization variants; selected execution-context identity; confidence calibration; schema evolution; cache reuse semantics; licensing; future execution approval/rollback design. See the architecture, theory and roadmap.

## Session 0 completion review

Final documentation, draft-schema/security profile and baseline consistency review completed. The baseline retains all 89 evidence records, nine Python providers and four CUDA-available Windows torch providers. All three JSON artifacts are byte-identical to the initial checkpoint. Existing successful Draft 2020-12/example and negative-case validation is reused; no validator or machine probe was rerun. JSON parsing, reference integrity and provider counts were checked from stored artifacts. See the final session-log entry for publication checks and changed files.

No unresolved Session 0 content blocker remains. Historical probe failures below remain evidence, not repair tasks. Licensing and future product questions remain deliberately deferred.

No packages or system components were intentionally modified. Existing failures/conflicts are preserved: Windows 10/build 19045 rather than historical Windows 11/build 28000; Ubuntu not in the current-user WSL list; Fedora Docker socket denial; Miniforge HF CLI output-encoding error; initial PowerShell script-policy rejection followed by successful inline read-only queries; initial Windows npm path error followed by a successful native-path retry.

## Session 1 implementation and acceptance evidence

Python standard-library V0 supports owner/repo, tree, blob and resolve URL forms; recognizes dataset/Space families but returns UNSUPPORTED without network requests. One fixed model-info API response, no redirects/retries, 1 MiB response budget plus overflow sentinel, configurable bounded file count and socket/body-read timeout. No optional text retrieval was implemented. Snapshot IDs/provenance, requested/resolved revision, API-reported file/LFS metadata, inferred roles/framework hints, failure states, coverage and download accounting remain explicit.

29 deterministic tests pass, including the real HTTP transport exercised through a fake connection, CLI offline output and structural/reference negative cases. No packages were installed. The one authorized live check of grichard99/statpredict-lite failed on a local EOF socket access bug before producing a snapshot. The bug was fixed and covered offline; no second live request was made. Live file names/sizes, repository fields and resolved revision remain UNKNOWN, and exact metadata bytes were not recovered. Model/file payload bytes are zero. See docs/HF_REPOSITORY_INSPECTOR_V0.md and reports/session-1-live-validation.json.

Remaining limitations: public model metadata only; conservative URL/path grammar; one metadata document; no text/config contents; no authentication, alias/redirect handling or retry; socket/body timeouts are not hard DNS/header wall-clock bounds; only the existing Fedora Python 3.14.7 was tested. The corrected transport has not yet passed a live acceptance check. These limitations are retained for human review; no machine compatibility verdict exists.

## Exact next scope

Stop at Phase 1. Final safety checks passed; the completion commit must be pushed normally and local/remote equality verified for the human handoff. A new explicitly authorized Phase 1 follow-up should repeat one bounded live metadata check after the EOF fix and review the snapshot. Phase 2 is not started or authorized. No environment scan, repair or installer follows automatically.

On return read RESUME.md, PROJECT_STATE.md, docs/SESSION_LOG.md, docs/ROADMAP.md, docs/SECURITY_MODEL.md and docs/EVIDENCE_MODEL.md first, then check Git. The initial checkpoint and completed Session 0 commit remain ancestors; never rewrite them. No HHS license has been selected.
