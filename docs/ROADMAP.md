# Roadmap

These are directional stages, not delivery dates or permission to implement future phases. Security, evidence and provider neutrality apply throughout. Findings may reorder or split stages.

| Phase | Direction | Exit evidence / boundary |
|---|---|---|
| 0 — complete | Foundation, theory, GitHub, security/evidence model and baseline | Reviewed docs/schema/example/baseline, planning issues, clean pushed repository; no software |
| 1 | Hugging Face Repository Inspector V0 | URL to bounded metadata evidence; revisions/failures/coverage; no installs or weights |
| 2 | Local Machine Probe Engine | Named scope, trusted provider probes, timeouts, redaction and precise non-detection |
| 3 | Requirement Extraction and Normalization | Sourced constraints, alternatives, conflicts and explicit unknowns |
| 4 | Compatibility and Reconciliation Engine | Selected-context verdicts with explainable evidence/rules and resource uncertainty |
| 5 | HHS Manifest schema and exporters | V1 candidate driven by real evidence, semantic references, compatibility/migration tests |
| 6 | Human Intent Interpreter | Goal/variant clarification without converting intent into approval |
| 7 | AI Agent Interfaces | Provider-neutral contracts; optional external export; advice stays unverified |
| 8 | Dry-Run Planning Engine | Reviewable inert actions, prerequisites, risks and verification/rollback intentions |
| 9 | Explicitly Authorized Execution Engine | Separate authority boundary, stale-plan checks and narrowly scoped mutation/verification |
| 10 | Windows CLI and hhs.exe packaging | Packaging an already tested CLI, with artifact integrity and scoped Windows acceptance |
| 11 | Optional desktop GUI | A thin presentation of canonical evidence/plans, not a second reasoning engine |
| 12 | Large compatibility test corpus | Hugging Face repository variants and different machines/environments with known expected outcomes |
| 13 | Advanced optimization recommendations | Evidence-backed alternatives, cost/resource tradeoffs and explicit confidence |
| 14 | Multi-environment support | Windows, WSL, native Linux, containers and remote machines with explicit trust/identity boundaries |

Windows/WSL separation is modeled now, even though broad multi-environment support is a later stage. Execution design does not imply execution is mandatory. A machine-baseline success is not a compatibility-engine success.

## GitHub planning issues

- [Phase 1 - Hugging Face Repository Inspector V0](https://github.com/chatgptopenaiagi/huggingface-helper-scanner/issues/1)
- [Phase 2 - Local Machine Probe Engine](https://github.com/chatgptopenaiagi/huggingface-helper-scanner/issues/2)
- [Phase 3 - Requirement Normalization Engine](https://github.com/chatgptopenaiagi/huggingface-helper-scanner/issues/3)
- [Phase 4 - Compatibility Reconciliation Engine](https://github.com/chatgptopenaiagi/huggingface-helper-scanner/issues/4)
- [Phase 5 - HHS Manifest V1](https://github.com/chatgptopenaiagi/huggingface-helper-scanner/issues/5)
- [Phase 6 - Human Intent Interpreter](https://github.com/chatgptopenaiagi/huggingface-helper-scanner/issues/6)
- [Phase 7 - Agent Interoperability](https://github.com/chatgptopenaiagi/huggingface-helper-scanner/issues/7)
- [Phase 8 - Dry-Run Planner](https://github.com/chatgptopenaiagi/huggingface-helper-scanner/issues/8)
- [Phase 9 - Authorized Execution Engine](https://github.com/chatgptopenaiagi/huggingface-helper-scanner/issues/9)
- [Phase 10 - Windows Executable Packaging](https://github.com/chatgptopenaiagi/huggingface-helper-scanner/issues/10)

Each issue describes a future goal, boundaries and acceptance evidence. None was implemented in Session 0.

## Future scope — requires new authorization

**PHASE 1 / SESSION 1 — Hugging Face Repository Inspector V0**

**HHS SESSION 1: HUGGING FACE REPOSITORY INSPECTOR V0**

Inspect a Hugging Face URL and produce structured repository metadata evidence without installing or downloading model weights. Begin with public model metadata, preserve revision/type/provenance, use bounded pagination/timeouts, and distinguish inaccessible, absent, unsupported and failed. No full requirements engine, machine engine or executor is part of this first slice.
