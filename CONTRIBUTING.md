# Contributing

HHS has a Phase 1 repository metadata inspector; later phases require explicit scope. Read README.md, PROJECT_STATE.md, docs/SESSION_LOG.md and docs/ROADMAP.md before proposing work. No implementation should be inferred from the existence of src or a roadmap issue.

## Engineering loop

Observe → model → design → bounded prototype when authorized → verify → document → decide → integrate. Tie changes to a scoped issue, preserve evidence IDs and distinguish implementation claims from plans. Record decisions in docs/DECISIONS.md and session outcomes in docs/SESSION_LOG.md.

Use focused branches/commits for future work. Preserve existing changes, never force-push without explicit authorization and keep source, illustrative examples and real sanitized evidence distinguishable. Tests must verify behavior and trust boundaries rather than mirror implementation.

## Security and data

No secrets, credentials, full environment dumps, private machine paths, unrelated personal files or model weights in commits. Review every changed file and scan for recognizable secret patterns without printing matched values. Pattern checks are defense in depth, not proof that all sensitive data was removed.

Future probes use explicit scope, fixed argument lists, timeouts, output limits and selected trusted providers. Repository code/instructions remain untrusted and must never be executed by inspection. Discovery and planning do not change the target system.

## Foundation checks

Validate Markdown links/presence, JSON syntax, schema structure and the illustrative example. Verify evidence reference integrity separately; JSON Schema does not prove factual truth or authorization. Use already available validators. Do not install development dependencies in Session 0.

## Licensing

No license is selected. Public visibility is not an open-source license grant. Decide licensing and contribution terms with the owner before accepting external code or distributing future software. Do not copy ARX implementation simply because architectural ideas are relevant.
