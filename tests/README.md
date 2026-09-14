# Future test strategy — documentation only

Session 0 tests document/JSON/schema consistency, not application behavior. No HHS test implementation is created here.

Future Inspector V0 tests should use bounded metadata fixtures: valid/invalid URLs, explicit unsupported repo types, revision identity, paginated/truncated results, inaccessible/gated/not-found/rate-limited responses, oversized data, malicious text/redirects and credential-bearing URLs. Verify no weight endpoint is fetched, no repository code is executed and no secret appears in output.

Later probe/reconciliation tests must distinguish multiple providers, selected context, NOT_FOUND vs ERROR, native Toolkit vs driver/runtime, unknown resource requirements, conflicts and semantic evidence references. Planner tests prove inertness. A future executor needs separate approval, stale-plan, interruption and recovery tests.

Live tests, when authorized, must be metadata-only initially and record their scope. Fixture provenance/licensing and personal-data minimization need review before a large corpus is committed.
