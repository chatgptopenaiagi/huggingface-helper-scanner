# Future source structure — documentation only

No HHS implementation exists in this directory. No language, package manager or CLI framework is selected.

Potential modules are intent/URL parsing, repository inspection, machine probes, evidence/domain types, requirement normalization, reconciliation, planning and manifest export. An optional future executor must have a separate explicit authorization boundary; it must not be imported as a hidden side effect of discovery.

The proposed next slice is Repository Inspector V0 only; it requires a new explicitly authorized task. Define its public input/output, budgets, failure model and fixtures before writing code. Do not create empty implementation packages or scaffold the entire pipeline just to mirror this conceptual list.
