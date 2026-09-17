# HHS manifest concept

A portable HHS manifest should carry enough context for another human/tool/agent to understand a compatibility finding without re-running the entire diagnostic conversation. It is an interoperability artifact, not a shell script or permission token.

## Draft structure

The initial envelope includes schema_version, hhs_version, generated_at, intent, source, repository, requirements, machine, detected_components, compatibility, blockers, warnings, missing, recommended_actions, files_required, storage_estimates, execution_candidates, evidence and security. The additional artifact_kind explicitly distinguishes illustrative examples from scan manifests.

Schema version is **0.1.0-draft**. HHS version is null because the example was hand-authored during Session 0, before HHS software existed; it remains an illustrative foundation artifact. The schema is deliberately provisional: broad domain objects stay extensible while evidence, findings, inert actions and security fields get minimal typed structure.

## Meaning rules

- Important conclusions carry evidence state, confidence, scope and evidence references.
- Provider/repository revision and target-context identities must survive export.
- Unknown sizes are null, not zero. Empty requirement/file/blocker arrays may mean not inspected, not absent.
- Keep requirement alternatives, conflicting sources and unverified documentation separate from observed machine facts.
- Actions are inert descriptions with prerequisites, risks, target context and verification intent. They require authorization and are not executable in the foundation profile.
- Confidence is a heuristic claim weight, not a probability or substitute for verification.
- Security declarations are assertions to validate/review, not proof that the artifact is safe.

## Validation layers

JSON syntax → JSON Schema shape → unique IDs/reference integrity → semantic consistency → provenance/trust review → publication redaction. Passing the earlier layers does not prove factual truth, compatibility or authorization. Schema validation must not fetch arbitrary external references supplied by an untrusted manifest.

The draft uses [JSON Schema 2020-12](https://json-schema.org/draft/2020-12/json-schema-core), reviewed 2026-09-13. Its top-level property names are explicit, but internal domain sections are not frozen. The foundation security profile enforces read-only and execution_authorized=false; a future executor requires a separate reviewed authority contract.

See [schema](../schemas/hhs-manifest-draft.schema.json), [schema notes](../schemas/README.md) and [illustrative example](../examples/example-hhs-manifest.json). The real development baseline has a separate draft report format; it is not claimed to conform to the full HHS manifest schema.
