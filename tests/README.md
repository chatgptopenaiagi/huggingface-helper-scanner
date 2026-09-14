# Inspector V0 tests

Run from the repository root:

```bash
PYTHONPATH=src python3 -B -m unittest discover -s tests -v
```

29 standard-library unittest methods cover URL forms and unsafe input, metadata/files/LFS, access/error states, size/file/page/request limits, weight/text content-route refusal, command-text minimization, redaction, structural/reference failures, real transport with a fake HTTPS connection, EOF closure, partial-byte timeout accounting, CLI output and exclusive-create protection. Parameterized subtests cover additional cases. No network, credentials or package installation is needed.

`fixtures/model.json` is hand-authored synthetic data for example-owner/example-model, not a claim that this repository exists. Commands in its card metadata are deliberately inert adversarial strings. No remote source was copied or imported. Source weights are never stored in fixtures.

Session 0 schema/example negative-check history remains in the [session log](../docs/SESSION_LOG.md); its artifacts are unchanged. Session 1 uses its own snapshot validator. The one authorized live test failed before snapshot generation, then the EOF defect was fixed and tested offline; see the [manual record](../reports/session-1-live-validation.json).

Future machine, compatibility and executor tests belong to separately authorized phases. Phase 2 has not started.
