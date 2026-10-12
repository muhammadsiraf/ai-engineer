# Packaging the GPU container

**Reading time:** ~6 min · Module 6

The serving container is where reproducibility, cold-start latency
(lesson 060), and supply-chain risk all meet. It looks like a Dockerfile
and is actually a release artifact with four properties to engineer:
small, pinned, cached, and verifiable.

## The anatomy of a GPU serving image

```
base:      CUDA + driver-compat runtime (NGC/PyTorch official, pinned)
layer:     engine + deps (vLLM/TensorRT-LLM, exact versions)
layer:     model weights (baked in, or mounted from fast storage)
config:    engine flags, health/readiness probes, resource limits
```

**The version matrix is the real constraint:** driver × CUDA × PyTorch ×
engine. Pin all four; "latest" tags on any layer are how you get a
mysterious 3am failure that reproduces nowhere. The base image tag
includes the CUDA version; the engine version is exact (no `^`/`~`
ranges); the model is pinned by *content hash*, not by repo name
(a repointed `main` on a HF repo is a supply-chain incident).

## Size and speed (feeding lesson 060)

- **Multi-stage builds:** compilers and build caches don't ship.
- **Weights:** bake into the image for immutable versioning (big images,
  but registry pull ≫ model download, and layer caching makes the pull
  incremental) *or* mount from node-local NVMe for shared weights across
  replicas. Pick per cluster topology; measure both (lesson 030's
  discipline).
- **Pull speed:** a 20GB image on a fresh node is a minute of cold start
  — pre-pull daemonsets or registry mirroring in-cluster for scale-out
  bursts.

## Verification (the part teams skip)

- **Scan** for CVEs (the base image is 90% of the surface); rebuild
  monthly for base patches — a scheduled, tested rebuild, not an
  accidental one.
- **Verify the model artifact:** checksum the weights at build time;
  community-quantized checkpoints from unknown repos are Module 3 lesson
  090's named risk — provenance or nothing.
- **Smoke-test in CI:** build → run → one real generation → assert
  output sanity (not gibberish — Module 3 lesson 090's verification
  step). A broken CUDA install or mismatched engine/weights shows up
  here, in CI, not in prod.

## Runtime configuration as code

Engine flags (max batch, KV blocks, quantization, prefix caching on) live
in the image's config or an adjacent versioned manifest — never as
hand-edited runtime state. The config diff is part of the release;
Module 3 lesson 120's "re-run the load test after every config change"
assumes you know what config is running, which this guarantees.

## Check yourself

1. A teammate "fixes" flaky builds by moving from pinned versions to
   `:latest` everywhere. Name the three incidents this buys, with the
   layer each lives in.
2. Bake-weights-in-image vs node-local NVMe mount: one advantage each,
   and the workload shape that decides.
3. Your smoke test passed for weeks then started producing gibberish
   with no code change. What changed underneath you, and which pin would
   have caught it?

Next: [090 — GPU economics](090-gpu-economics.md)
