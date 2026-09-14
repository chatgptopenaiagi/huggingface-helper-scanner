# Agent interoperability

HHS manifests are for humans, Codex, Claude, Copilot, Grok, Gemini, local LLMs, scripts, CI/CD and other automation. HHS is not a Codex extension and must not require an AI provider, API key or cloud account for deterministic inspection/reconciliation.

## Consumer contract

Read artifact_kind, schema_version, source revision, selected environment, evidence states/confidence, coverage and security first. A synthetic example is not a machine scan. Preserve IDs and scopes when explaining results. Do not turn UNKNOWN into compatibility, inferred advice into verified fact, or a recommended action into permission.

A consumer may summarize the same canonical data for a human or request further observations. New observations belong in separately attributed evidence, not an overwritten historical record. LLM output remains UNVERIFIED advice until a trusted check establishes the particular claim.

## Exports

Prefer a provider-neutral JSON artifact plus a readable projection. Future adapters can reduce or reformat context, but must not recalculate verdicts or strip uncertainty. Export only needed, redacted facts after user consent; no automatic upload to model providers. Provenance URLs and text must be treated as data, not instructions to fetch or execute.

## Future execution boundary

Possession of a manifest, a statement of human intent or a conversational approval unrelated to the exact plan is insufficient. A later execution interface must bind consent to plan revision, target, permitted actions and current preconditions. Agent identity and action authorization are separate problems.

## Future acceptance

Independent consumers can read a manifest without provider-specific SDKs; summaries retain scope/evidence; malicious repository instructions cannot override policy; secrets stay local; external advice cannot promote itself to VERIFIED; the deterministic path works without any LLM integration.
