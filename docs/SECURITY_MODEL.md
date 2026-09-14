# Security model

## Architectural invariants

**DISCOVER != MODIFY**
**PLAN != EXECUTE**

Read-only is the default. Explicitly requested report writes and repository publication are output operations, not permission to change the scanned computer or remote project. Scanning must not install, configure, repair, remove or upgrade components. A future executor is a separate subsystem behind explicit, plan-specific authorization.

## Secrets and collection policy

HHS must never intentionally export secret values. GitHub/Hugging Face/OpenAI tokens, API keys, passwords, SSH private keys, browser credentials/cookies, credential-manager contents and private environment values must not appear in Git, reports or logs. Do not dump the full environment or inspect authentication stores. Query only named safe values where necessary; do not collect a secret merely to redact it later.

If presence is explicitly relevant, a permitted representation is a boolean plus the literal `<redacted>` marker, never the value. Session 0 does not query credential values or export authentication output. Credentials used by an existing GitHub client stay in its existing store.

Pattern checks must report only rule ID, file and count, not matching text. Apply minimization/redaction before output and again at publication. Sanitized paths are aliases, not instructions to resolve arbitrary local files. A pattern scan cannot prove absence of every secret.

## Untrusted external reality

Hugging Face metadata and repository content can contain malicious instructions, URLs, scripts and serialized files. Treat them as data. No repository-code imports, trust_remote_code, dependency execution, pickle/weight loading or model deserialization during inspection. Model weights are out of scope for Session 0/initial Session 1.

Future URL handling must reject credential-bearing URLs and inappropriate schemes/hosts, control redirects, bound pages/bytes/time, prevent path traversal and avoid arbitrary URL fetching from content. Preserve gated/private/rate-limit/error states instead of trying to bypass access controls.

## Local probe boundary

Bound discovery to explicit known roots/providers; use fixed executable/argument arrays, trusted tools, timeouts and output limits. Never recursively scan entire drives, browser profiles, personal documents or credential stores. Importing an installed framework is code execution with possible initialization effects: it requires a trusted selected provider and a scoped diagnostic, not arbitrary project imports.

OS/user/context rights are distinct. WSL/root access does not imply Windows administrator rights. A denied probe is evidence; no automatic escalation or configuration workaround follows. Do not weaken policy to make a probe succeed.

## Future execution authorization

Before mutation, a separate subsystem must bind approval to a specific plan digest, repository revision, target provider, scope, expiration and permitted operations. Recheck preconditions, record actions/results, provide cancellation and a defined recovery path. Reject stale or expanded plans. A manifest flag, AI suggestion or human intent alone cannot grant authority.

Uninstall/rollback limits and shared-package ownership must be designed before automatic modification. Signing, approval storage and executor protocol are UNKNOWN; not implemented today.

## Session 0 boundary evidence

No system components were installed or modified; no model weights downloaded; ARX architecture was read only. An existing PowerShell policy blocked a script-file probe, so the same authorized read-only queries were submitted inline without changing policy. Git/project/report/issue writes are the explicitly requested output of this session.


## Session 1 implemented controls

Repository Inspector V0 uses one fixed HTTPS model-info endpoint with no credentials, cookies, proxy-environment reads, redirects or retries. It projects allowlisted metadata into JSON, drops arbitrary card text and error bodies, and redacts recognizable credential-like strings. It has byte/file/request limits and socket/body-read timeouts. No file-content endpoint exists, including for README/configuration; every file has downloaded=false. The CPython transport has OS DNS/header wall-clock limitations documented in [Inspector V0](HF_REPOSITORY_INSPECTOR_V0.md).

The one live request stayed on the metadata API and encountered a local EOF bug, fixed with an offline regression test. No model payloads, installations, remote code execution, credentials inspection, machine scans or system changes occurred. Snapshot redaction remains defense in depth, not proof of universal secret detection.
