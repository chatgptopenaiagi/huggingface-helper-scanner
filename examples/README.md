# Illustrative examples

[example-hhs-manifest.json](example-hhs-manifest.json) is **illustrative and NOT a real scan**. Its Hugging Face URL is fictional; existence is not asserted, no request was made to it, and no machine is represented by its placeholders.

The example shows unknown values, unverified synthetic inputs, an inert next-observation suggestion, empty execution candidates and explicit read-only security. Empty arrays do not mean the project has no requirements, blockers or files. No installation/run command is provided.

Validate against the [draft schema](../schemas/hhs-manifest-draft.schema.json). This proves structural agreement only. The [real manual baseline](../reports/dev-machine-baseline.json) is a separate artifact with a different purpose/format.


[repository-snapshot-v0.json](repository-snapshot-v0.json) is a Session 1 CLI-generated **offline synthetic** repository snapshot from tests/fixtures/model.json. It is not a real Hugging Face observation and is separate from the Session 0 illustrative manifest/schema. It records zero network requests and zero file payload bytes. Validate with `hhs.hf.inspector.validate_snapshot`; see [Inspector V0](../docs/HF_REPOSITORY_INSPECTOR_V0.md).
