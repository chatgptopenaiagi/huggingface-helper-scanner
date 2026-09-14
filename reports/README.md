# Reports

[dev-machine-baseline.json](dev-machine-baseline.json) is a real but bounded **manual Session 0 development inventory**, not an HHS-generated product scan or a universal machine certification.

It separates host_windows, wsl, fedora, gpu, cuda, cudnn, python, pytorch, development_tools, storage and evidence. Important facts retain state, confidence and references. Private user-home values use placeholders; no credential contents or full environment dump is retained. Command failures and conflicting historical hints remain visible.

The user explicitly authorized committing a sanitized public baseline. Future raw/private reports must not be committed automatically. Review each export and write only minimized allowlisted data. A historical baseline becomes UNVERIFIED input in a new scan until checked; do not keep reporting its dynamic free-space numbers as current.

This JSON is not required to conform to the full draft HHS manifest schema. See [environment summary](../docs/ENVIRONMENT_BASELINE.md) and [evidence model](../docs/EVIDENCE_MODEL.md).
