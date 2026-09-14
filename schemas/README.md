# Draft schema

[hhs-manifest-draft.schema.json](hhs-manifest-draft.schema.json) is a provisional JSON Schema 2020-12 discussion artifact, version 0.1.0-draft. It is not a stable API or an implemented exporter.

Top-level fields mirror the requested conceptual structure. Evidence/finding/action/security records have initial constraints; broad domain sections intentionally remain extensible. Internal $refs are local. The schema $id is a public identifier, not an instruction to fetch it.

Validate syntax and schema shape, then validate the [illustrative example](../examples/example-hhs-manifest.json). Separately check unique evidence IDs, reference resolution and semantic limits. Schema validation cannot prove the values are true, no secrets exist or an action is authorized. The current profile requires read-only and denies execution authorization; future executor authorization is separate.

The manual [development baseline](../reports/dev-machine-baseline.json) has its own report_format and is not claimed to implement this schema. A baseline schema can be considered after the probe engine produces real contracts. No validator package was installed in Session 0; an existing Windows Anaconda jsonschema provider was available.
