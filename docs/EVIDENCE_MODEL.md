# Evidence model

Evidence describes how a claim is known. Compatibility classifications describe what a claim means for a selected requirement/context. Neither should replace the other.

| State | Initial meaning |
|---|---|
| **OBSERVED** | Directly obtained from a command, API, filesystem metadata, configuration/repository metadata, hardware query or deterministic probe. |
| **INFERRED** | Derived from observed evidence but not independently confirmed; retain rule/reasoning and references. |
| **VERIFIED** | An important observation independently confirmed by another trusted probe or consistency check. Record which check and its limited claim. |
| **UNVERIFIED** | Supplied by a human, prior report, documentation or historical context and not confirmed in the current scan. |
| **NOT_FOUND** | Expected component not located within an explicit bounded discovery scope. Not proof of machine-wide absence. |
| **ERROR** | Probe failed. Retain safe failure type, context and limitations; do not convert to MISSING. |
| **UNKNOWN** | Insufficient evidence to classify the state. |

## Minimal record

Stable ID; subject; state; confidence; source/method; scope/provider/repository revision where relevant; observation time; value or structured failure; supporting references; limitations. Preserve the initial observation when deriving a new finding rather than overwriting its provenance.

Confidence ranges from 0 to 1 in the draft and is **heuristic, not calibrated probability**. A high-confidence ERROR means the error was reliably observed, not that the software is absent. Confidence in a documentation claim's origin is distinct from confidence that the claimed dependency is correct. Illustrative example claims are explicitly unverified, with confidence zero for fictional input facts.

## Verification discipline

A single successful command is usually OBSERVED. Two reports copied from the same source are not independent corroboration. A consistency check must name what it actually validates: package metadata/runtime-version agreement, for example, does not establish GPU workload execution. JSON/schema validation verifies structure, not model compatibility or factual hardware state.

In this baseline, CPU identity is cross-checked between Linux and Windows; GPU identity/capability uses driver/CIM/framework observations; selected native Linux cuDNN version is compared with its header. Individual torch.cuda.is_available results remain runtime API observations. Prior successful GPU calculations were not repeated and remain historical context.

## From evidence to findings

PRESENT/MISSING describe availability at a stated scope. COMPATIBLE/INCOMPATIBLE compare known requirements with a named provider/context. OPTIONAL/RECOMMENDED express policy or requirement importance. BLOCKING describes consequence. UNKNOWN/UNVERIFIED retain uncertainty. A missing optional component need not block anything; a present incompatible provider can still block the chosen context.

Conflicts are retained as linked competing evidence. Prefer a suitable current observation over an old hint only for the fact actually queried. Do not globally discard useful historical context or repair the machine to match it. Unknown requirements, incomplete API pages and failed probes must remain visible to consumers.


## Session 1 repository evidence

V0 keeps API metadata OBSERVED, URL inputs UNVERIFIED and filename/framework/family hints INFERRED. Each snapshot observation identifies its API URL, requested/resolved revision, timestamp and scope. Metadata/file observations refer to the response-body SHA-256; file rows and derived hints reference their evidence IDs. API-reported sizes and LFS hashes are not independently verified payloads. Offline fixtures are explicitly synthetic, even when testing the OBSERVED code path.

See [Inspector V0](HF_REPOSITORY_INSPECTOR_V0.md). The manual live-validation report preserves the failed Session 1 invocation with its unknown values and separately records the successful Session 1.1 snapshot: four evidence records and 2,372 metadata body bytes. Failed-run unknown bytes are not replaced with the later successful-run count.
