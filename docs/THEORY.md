# Theory: reconciling two realities

## External reality

A Hugging Face repository may contain safetensors, GGUF, PyTorch or TensorFlow weights; tokenizers and configuration; Python/custom model code; requirements.txt, pyproject.toml, environment.yml and Dockerfile; Git LFS references; datasets, scripts, checkpoints and adapters; quantization details; README guidance; CUDA/PyTorch/Transformers constraints; GPU/CPU architecture assumptions and memory estimates.

File presence alone does not prove relevance. A repository can offer alternatives rather than require every weight or backend. A filename or model card can suggest a requirement without establishing that it applies to the chosen revision and workload.

## Internal reality

The selected environment includes OS/WSL/container boundaries, CPU/RAM, GPU/VRAM, driver capability, installed CUDA toolkits and native cuDNN, framework runtimes, Python/Conda/venv providers, build tools, dependency libraries, caches and storage. Preserve separate provider identities and the execution context where resolution was observed.

```text
EXTERNAL REQUIREMENTS
          ↓
      RECONCILIATION
          ↑
LOCAL MACHINE REALITY
```

## Independent questions

Availability is not resolution. Resolution is not compatibility. Compatibility is not relevance. Relevant capabilities must be evaluated for the selected workload; resource feasibility is separate from software version compatibility. A recommended action is not evidence that it happened.

Possible finding classifications include PRESENT, MISSING, COMPATIBLE, INCOMPATIBLE, OPTIONAL, RECOMMENDED, BLOCKING, UNKNOWN and UNVERIFIED. They answer different questions; do not force them into one mutually exclusive machine-wide status. Evidence states and confidence are separate dimensions described in EVIDENCE_MODEL.md.

## Reconciliation examples

- A compatible PyTorch environment elsewhere is an alternative provider, not proof the selected interpreter satisfies the requirement.
- A driver advertising CUDA 13.4, a Toolkit 13.4 install and PyTorch bundled with CUDA 13.2 are separate facts, not automatically a conflict or proof of compatibility.
- An unknown workload VRAM requirement cannot be declared to fit merely because a GPU has 6 GiB.
- NOT_FOUND from one interpreter must not become machine-wide MISSING.
- Conflicting README and dependency-file constraints must preserve both sources and the reason for any later preference.

## Open theory questions

How to model intended inference versus training, context length/batch/quantization variants, authoritative versus stale claims, platform markers, optional dependencies, minimum versus recommended resources and cache reuse? What should a plan do when disk/RAM/VRAM estimates are intervals rather than exact values? No arbitrary defaults should erase these uncertainties.
