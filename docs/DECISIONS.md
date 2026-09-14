# Foundation decisions

| ID | Status / date | Decision | Rationale and remaining uncertainty |
|---|---|---|---|
| D-01 | FIXED / 2026-09-13 | HHS = HuggingFace Helper Scanner; repository huggingface-helper-scanner | Owner-established identity; separate from ARX and OLW |
| D-02 | FIXED / 2026-09-13 | DISCOVER != MODIFY; PLAN != EXECUTE | Read-only default, separate future authorization/execution |
| D-03 | FIXED / 2026-09-13 | Provider-neutral portable manifests | No dependency on Codex or another AI provider |
| D-04 | FIXED / 2026-09-13 | Evidence taxonomy and scoped confidence | Errors/non-detection/history must not become false certainty |
| D-05 | FIXED / 2026-09-13 | Session 0 only foundation/evidence/docs/schema | No pipeline implementation, installs, repairs or weights |
| D-06 | SELECTED / 2026-09-13 | Shared workspace and public GitHub repository | Requested parent exists and is writable; sanitized publication explicitly authorized |
| D-07 | DEFERRED / 2026-09-13 | Software license | Owner explicitly instructed no license selection today |
| D-08 | DRAFT / 2026-09-13 | JSON Schema 2020-12, schema version 0.1.0-draft | Minimal contract exploration; domain sections remain open and example synthetic |
| D-09 | SELECTED / 2026-09-13 | No active GitHub Actions workflow in Session 0 | Validate locally with an existing validator; keep workflow README for later |
| D-10 | PROPOSED / 2026-09-13 | Session 1 initial public-model metadata slice | Narrow starting point; unsupported types explicit; owner may refine scope |
| D-11 | DEFERRED / 2026-09-13 | Implementation language, dependencies, CLI/UI, executor design | Existing developer tools are evidence, not a stack decision |

For a future major decision, record ID/date, proposed/accepted/superseded status, owner, context, alternatives, evidence, consequences and revisit trigger. Preserve superseded history. No source-reuse or license choice is implied by ARX's local presence.
