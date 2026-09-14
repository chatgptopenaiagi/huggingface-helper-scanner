# Hugging Face Repository Inspector V0

HHS 0.1.0 observes public model repository metadata. It does not assess machine compatibility. This is a provisional repository snapshot, separate from the unchanged Session 0 manifest draft and manual machine baseline. No license has been selected for HHS.

## Run without installation

From the repository root, using the existing Python interpreter:

```bash
PYTHONPATH=src python3 -B -m hhs inspect-hf https://huggingface.co/owner/repo
PYTHONPATH=src python3 -B -m hhs inspect-hf https://huggingface.co/owner/repo --revision main --max-files 200 --timeout 10 --output snapshot.json
PYTHONPATH=src python3 -B -m hhs inspect-hf https://huggingface.co/example-owner/example-model --offline-fixture tests/fixtures/model.json
PYTHONPATH=src python3 -B -m unittest discover -s tests -v
```

`PYTHONPATH` applies only to that process; `-B` suppresses bytecode files. No package installation, activation or persistent environment change is needed. Python 3.14.7 on the existing Fedora context was tested; Windows and other Python versions have not been acceptance-tested. This is not an installer or packaged executable.

Default output is JSON on stdout. Exit 0 means a structurally valid, complete metadata snapshot; exit 2 means partial coverage, structured inspection failure or a safe CLI/file error. `--output` exclusively creates a new file and refuses overwriting an existing file. Output parent directories must exist. CLI/file-operation diagnostics omit sensitive argument/path details. Offline fixtures contain the API model-info JSON object, not a snapshot, and are explicitly labeled synthetic in output. Offline mode makes no network calls.

## URL grammar and identity

Only HTTPS and the exact `huggingface.co` host are accepted (case-insensitive hostname). No credentials, explicit ports, query strings, fragments, whitespace/control characters, path traversal, empty segments, backslashes or double-encoded escape sequences. Owner/repository names use a conservative ASCII subset. Invalid input is not echoed into JSON.

Supported model forms:

- `/owner/repo` or `/owner/repo/`
- `/owner/repo/tree/<revision>` and optional repository-relative path
- `/owner/repo/blob/<revision>/<path>`
- `/owner/repo/resolve/<revision>/<path>`

Dataset `/datasets/owner/repo` and Space `/spaces/owner/repo` families, including the same suffix grammar, are recognized but inspection returns `UNSUPPORTED` without network access. Other routes and one-component legacy model IDs are unsupported/invalid. No guessing of organizational pages, discussions, commits, collections or arbitrary Hub pages.

The revision occupies one URL segment. A slash-containing revision must be percent-encoded within that segment, e.g. `tree/refs%2Fpr%2F1`, or supplied using `--revision refs/pr/1`. Segments following the revision are a path, not guessed branch-name components. Conflicting URL and option revisions are invalid. A blob/resolve input identifies a repository and requested path; it never causes that file to be retrieved or limits observation to that path.

The source retains `requested_revision` (null when absent), `effective_revision` (`main` by default), `requested_path` and API `resolved_revision` (a validated 40-hex commit). An explicitly requested commit must equal the returned commit. Response repository identity must match the requested ID; aliases/moves are not guessed. Repository existence and revision resolution remain unverified until the metadata response passes validation.

## Architecture and metadata contract

`url_parser.py` parses identity → `client.py` constructs one fixed API endpoint → `inspector.py` projects allowlisted fields and builds evidence → `cli.py` serializes JSON. There is no remote-file downloader, plugin loader, interpreter of repository instructions, machine probe, compatibility engine or executor.

The sole request is:

```text
GET https://huggingface.co/api/models/<owner>/<repo>/revision/<revision>?blobs=true
```

The model-info response supplies repository flags, library/pipeline tags, license metadata, immutable commit and sibling file metadata including sizes and LFS metadata when reported. No tree, raw, blob, resolve, CDN, LFS or Xet content request is made. The model-info endpoint is used as one bounded document; arbitrary pagination URLs are never followed. A Link header or retained-file limit produces `PARTIAL` coverage.

Primary API references reviewed on 2026-09-14: [Hub API entrypoint](https://huggingface.co/docs/hub/api) and [HfApi model_info/RepoSibling reference](https://huggingface.co/docs/huggingface_hub/package_reference/hf_api#huggingface_hub.HfApi.model_info). The OpenAPI Markdown URL returned an error through the documentation reader; the official HfApi reference was used instead. HHS does not depend on the Hugging Face Python library.

## Bounds and transport

| Control | V0 value |
|---|---|
| API requests / pages | At most 1 per inspection/client |
| Retry policy | 0 retries; no rate-limit wait or bypass |
| Redirects | Never followed |
| Timeout | Default 10 seconds, configurable above 0 and at most 30 |
| Metadata body | At most 1,048,576 bytes, plus at most one sentinel byte to detect overflow |
| Retained files | Default 1,000; `--max-files` 1–10,000 |
| Tags / tag text | At most 1,000 tags; 200 characters each |
| File path | At most 1,024 characters, conservative repository-relative grammar |
| Text and model contents | 0 bytes permitted |
| User-Agent | `HHS/0.1.0 (repository-metadata-only)` |

Timeout covers blocking socket operations and an additional elapsed deadline while reading the body. It is **not a hard whole-process deadline**: operating-system DNS resolution can exceed the socket timeout, and response-header reads use the standard library's per-operation timeout and count/line limits. This limitation is explicit; external process supervision would be needed for a strict wall-clock SLA. No such service is installed.

The direct standard-library HTTPS connection validates TLS using the default trust configuration. It does not read tokens, credential stores, cookies, `.netrc`, proxy variables or environment dumps. Requests contain only a fixed User-Agent, Accept and identity-encoding header, plus standard HTTP host/connection details. Response headers retained in memory are limited; raw headers and error bodies are never serialized. Oversized Content-Length, compressed responses and non-JSON media types are rejected before body consumption. Byte accounting measures body bytes returned to the application, not HTTP/TLS/DNS overhead or unread transport buffers.

A [generated offline snapshot](../examples/repository-snapshot-v0.json) demonstrates the output without any live repository claim.

## Snapshot and evidence

`hhs-repository-snapshot-0.1` contains version/timestamp/mode/status, normalized source, repository metadata, files, derived hints, evidence, warnings/errors, coverage, accounting and security. `validate_snapshot` performs dependency-free structural and semantic checks before serialization, including IDs/reference resolution and the no-content invariant. This validator is for V0 output; it is not a general JSON Schema engine or HHS Manifest V1.

Each metadata observation has a timestamp, API URL, repository/revision context, scope, method and evidence ID. Successful response bytes are SHA-256 hashed, and that digest is retained as provenance without exporting the raw response. Repository fields and file records reference their observations; classifications reference a separate `INFERRED` rule record. File-size values are API-reported bytes, not independently verified downloads. Missing size/LFS values remain null/not reported. A lack of LFS metadata does not prove Git-only storage.

States follow the [evidence model](EVIDENCE_MODEL.md). API metadata is `OBSERVED`, filename roles/framework/family hints are `INFERRED`, user identity input is `UNVERIFIED`, and scoped failures retain `ERROR`, `UNKNOWN` or `NOT_FOUND`. No claim is promoted to `VERIFIED` just because JSON is valid. Confidence is heuristic. Offline observations have source `synthetic_fixture`; no live repository fact is asserted by the fixture.

A complete response is complete only for the bounded metadata list returned by this endpoint, not for dependency requirements, repository content or machine compatibility. Empty derived arrays do not establish absence. Metadata flags and model-card license fields are repository claims, not independent legal or functional verification.

## Failure taxonomy

| Code | Meaning |
|---|---|
| INVALID | Unsafe/malformed input or conflicting revisions |
| UNSUPPORTED | Recognized unsupported repo family/route, compressed response or forbidden content endpoint |
| PRIVATE | API explicitly reports private=true; warning, not guessed from HTTP status |
| GATED | API gated flag or explicit GatedRepo error |
| AUTH_REQUIRED | 401/403 without a more specific supported error; no credential attempt |
| NOT_FOUND | HTTP 404 in this requested endpoint scope; may conceal private repos or missing revisions |
| RATE_LIMITED | HTTP 429, no automatic retry |
| NETWORK_ERROR | Transport/TLS/protocol failure or HTTP 5xx |
| TIMEOUT | Socket/body-read timeout |
| MALFORMED_RESPONSE | Invalid JSON, identity/revision/type/path/size/hash inconsistency |
| RESPONSE_TOO_LARGE | Metadata byte budget exceeded; body discarded |
| REDIRECT_BLOCKED | HTTP redirect refused |
| LIMIT_REACHED | File/page/request coverage limit |
| UNKNOWN | Other HTTP outcomes without sufficient classification evidence |

## Content security and download accounting

Every listed file has `downloaded=false` and `content_policy=METADATA_ONLY`. Weight extensions, adapters and LFS objects are classified from names/metadata only. README/configuration files are also never downloaded, even when tiny. A huge README is refused by the same zero-content policy; no text-size exception exists in V0.

Allowlisted metadata projection drops arbitrary model-card instructions, descriptions, command text, response error bodies and unrelated fields. Recognizable credential-like strings/assignments and private-home paths are redacted in projected metadata. Filters are defense in depth and cannot detect every secret or make repository text trusted. Never execute strings from snapshots. Review exports before publication.

Accounting separates live metadata body bytes, fixture bytes, network request attempts and model/file content bytes (always zero). A checksum is an observation of the response bytes, not proof of the truth or safety of their contents. Known files' reported sizes are not summed into a claimed exact amount of avoided traffic because coverage and sizes may be incomplete.

## Validation and known limitations

The synthetic [fixture](../tests/fixtures/model.json) includes LFS metadata, model/adapter files and malicious-looking model-card commands. Tests cover URL grammar, failures, content-route refusal, headers, body limits, file/page limits, EOF closure, partial-body timeout accounting, CLI output, no-overwrite behavior, redaction, evidence references and structural negative cases. No test imports inspected repository code or requires network/credentials.

Session 1's single live check failed on a local EOF socket-handling defect; the fix passed offline regression tests. Session 1.1 separately authorized exactly one acceptance attempt using the unchanged CLI/transport. It succeeded at 2026-09-14T18:13:13Z against grichard99/statpredict-lite: HTTP 200 JSON, revision `dc008d3102cde6d8be879ce89d22a13536aacfec`, eight file metadata entries, four evidence records, 2,372 metadata body bytes, no warnings/errors and zero file/model payload bytes. The EOF exception did not recur. All 29 deterministic tests passed afterward. No source change or second request was needed.

See the unchanged [CLI snapshot](../reports/session-1.1-statpredict-lite.json) and [validation report](../reports/session-1-live-validation.json), which preserves the earlier failed attempt. Reported model.safetensors size is 132,075,640 bytes, with LFS metadata; it was not downloaded. Public/ungated, transformers, text-generation and apache-2.0 are API metadata claims; gpt2 family and safetensors role/format are inferred hints. This validates this bounded live path, not all repositories or payload truth.

Remaining limits: model-only API support, conservative ASCII names/paths, one metadata page, zero content inspection, no authentication, no redirects/aliases, no retry, no hard DNS/header wall-clock bound, no packaged executable, no Windows acceptance run, heuristic roles/family tags, no stable Manifest V1, and no machine compatibility claims.

Stop at Phase 1. Session 1.1 live acceptance is finished; no further live request is authorized. Phase 2 remains unstarted and requires its own authorization.
