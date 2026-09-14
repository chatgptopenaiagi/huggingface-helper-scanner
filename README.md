# HHS

**HuggingFace Helper Scanner**

**Status: SESSION 0 / PHASE 0 COMPLETE — foundation only.** No HHS application, CLI, scanner, installer or executable exists yet. This repository contains the Session 0 architecture, project memory, a manually collected development baseline and a draft manifest contract.

> **DISCOVER != MODIFY**
> **PLAN != EXECUTE**

## The human-time problem

Using a Hugging Face project can turn into hours of repeated copy/paste troubleshooting: inspect CUDA, find Python, discover a different environment, install a suggested dependency, encounter another error and start again. HHS aims to replace much of that repetition with systematic observation and reconciliation. It is not merely a downloader.

A project can combine weights, quantization formats, custom code, dependency manifests, undocumented resource assumptions and platform-specific instructions. A computer can have several valid but different Python, CUDA, toolchain and container providers. Installed somewhere does not mean selected, relevant or compatible for the intended workload.

```text
HUMAN INTENT × HUGGING FACE PROJECT × LOCAL COMPUTER REALITY
                           ↓
                          HHS
                           ↓
              COMPATIBILITY + REQUIREMENTS + PLAN
                           ↓
                  PORTABLE HHS MANIFEST
                           ↓
           Humans, AI agents, scripts and automation
```

## Two realities

**External reality:** repository metadata, revisions, model files, configurations, dependency declarations, custom code, datasets, adapters, quantization and stated resource requirements.

**Internal reality:** the actual selected operating environment, hardware, memory, drivers, toolkits, libraries, Python providers, frameworks, build tools, storage and caches.

The intended reconciliation engine will preserve evidence, uncertainty and context while explaining what is present, missing, compatible, incompatible, optional, recommended, blocking or unknown. These are proposed classifications, not verdicts produced by working HHS software today.

## Portable, provider-neutral output

An HHS manifest should be understandable by humans, Codex, Claude, Copilot, Grok, Gemini, local models, scripts and CI/CD. HHS must not depend on Codex or any AI vendor. AI advice must not overwrite observed machine evidence or grant execution permission.

Scanning is read-only by default. Future installation/configuration belongs to a separate, explicitly authorized execution architecture. A command described in a plan is not a command approved to run.

## Read first

1. [RESUME.md](RESUME.md): completed Session 0 handoff and stop boundary.
2. [PROJECT_STATE.md](PROJECT_STATE.md): current phase, workspace, completed/unimplemented work and next task.
3. [Session log](docs/SESSION_LOG.md): where development stopped.
4. [Roadmap](docs/ROADMAP.md): future phases and GitHub issues.
5. [Architecture](docs/ARCHITECTURE.md), [security model](docs/SECURITY_MODEL.md) and [evidence model](docs/EVIDENCE_MODEL.md).

## Repository map

- [Vision](docs/VISION.md), [theory](docs/THEORY.md), [design principles](docs/DESIGN_PRINCIPLES.md), [decisions](docs/DECISIONS.md).
- [ARX relationship](docs/ARX_RELATIONSHIP.md): read-only architectural comparison, no copied source.
- [Environment baseline](docs/ENVIRONMENT_BASELINE.md) and [sanitized JSON](reports/dev-machine-baseline.json): real, bounded Session 0 observations, not an HHS product scan.
- [Manifest concept](docs/HHS_MANIFEST_CONCEPT.md), [draft schema](schemas/hhs-manifest-draft.schema.json) and [illustrative example](examples/example-hhs-manifest.json). The example is **NOT a real scan**.
- [Agent interoperability](docs/AGENT_INTEROPERABILITY.md), [future source layout](src/README.md) and [future test strategy](tests/README.md).

Repository: https://github.com/chatgptopenaiagi/huggingface-helper-scanner

Public visibility does not select a software license. **No license is selected in Session 0.** Licensing will be decided in a future session; there is intentionally no LICENSE file. See [CONTRIBUTING](CONTRIBUTING.md).

## Future session — requires new authorization

**HHS SESSION 1: HUGGING FACE REPOSITORY INSPECTOR V0**

Initially learn to inspect a Hugging Face URL and turn repository metadata into structured evidence, **without installing anything or downloading model weights**. This future task was not implemented in Session 0.
