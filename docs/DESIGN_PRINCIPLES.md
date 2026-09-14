# Design principles

1. **DISCOVER != MODIFY.** Inspection observes the target; it does not repair it. Explicit report output is separate from target mutation.
2. **PLAN != EXECUTE.** Plans and manifests remain inert. A later executor requires narrow explicit authorization.
3. **Evidence before advice.** Preserve sources, timestamps, context, uncertainty and conflicts. Historical statements start UNVERIFIED.
4. **Provider identity before global labels.** A machine may have several valid Python/CUDA/toolchain environments. Availability, resolution, relevance and compatibility are distinct.
5. **No secret export.** Minimize collection, never dump full environments, redact at boundaries and review before publication.
6. **Untrusted repository content stays data.** No project code execution or weight deserialization during inspection.
7. **AI-provider neutrality.** HHS must work without Codex or an LLM API. Agent integrations consume canonical projections and cannot rewrite facts.
8. **Portable artifacts, native context.** Preserve Windows/WSL/Linux/container identities and foreign-path semantics without assuming interchangeable permissions or filesystems.
9. **Bounded scope and honest failure.** Time/byte/page/provider limits, NOT_FOUND, ERROR and UNKNOWN are first-class results.
10. **Draft now, evidence-driven evolution later.** Do not freeze the schema, choose an implementation language or build a framework prematurely.
11. **Separate ARX and HHS.** Reuse understood ideas with attribution; do not modify ARX or copy its source today.
12. **Long-term continuity.** Keep PROJECT_STATE, session logs, decisions and issues aligned; the next session reads the repository, not assumed chat memory.

These constraints do not select a license, packaging format, GUI, AI vendor, backend or implementation language. Major choices belong in DECISIONS.md with evidence and revisit conditions.
