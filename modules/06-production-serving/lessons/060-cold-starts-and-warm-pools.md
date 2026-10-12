# Cold starts and warm pools

**Reading time:** ~6 min · Module 6

The cold start is the GPU platform's defining tax: a new replica must
schedule, pull a multi-GB image, allocate, and load model weights before
it can serve — 30 seconds to many minutes, versus milliseconds for a
CPU service. Everything about capacity planning in this module bends
around this one number.

## The anatomy of the minute(s)

```
schedule pod → pull container image → allocate GPU
           → load weights (disk/network → VRAM) → warm up engine → ready
```

Typical budgets for a 7B–70B model: image pull 10–60s (layer caching!),
weight load 10s–3min (dominated by storage bandwidth — a 14GB read at
200MB/s is 70 seconds), engine warmup 2–10s (CUDA graphs, kernel
autotuning, a real dummy forward pass).

## The toolbox, cheapest first

1. **Keep replicas warm** (min replicas > 0): the baseline. Size the
   floor to night-time peak (lesson 050) — this *is* the warm pool.
2. **Shrink the artifacts:** slim images (no build toolchains, multi-
   stage builds), quantized weights (Module 3 lessons 080/090 — a 4-bit
   70B loads 4x faster than BF16), model files baked into the image or
   on a fast local NVMe cache rather than fetched from object storage
   at boot.
3. **Pre-warm on signal:** scale before the traffic — schedule-based
   ramps (lesson 050), or pre-deploy in new zones *ahead* of need.
4. **Warmup requests at boot:** engines autotune kernels and allocate
   KV blocks lazily; a synthetic request at readiness avoids the first
   real user paying the autotuning cost.
5. **Shared weights across replicas** (engine/infra dependent): copy-on-
   write or shared memory pools for the base model — many adapters
   (Module 5 lesson 130) over one loaded base is the extreme version.

## The readiness gate

A replica that accepts traffic before weights are loaded serves errors;
one marked ready too late wastes pool capacity. The readiness probe must
reflect *engine readiness* (a real generation completed), not just
"process is up." First-request latency after scale-out is a first-class
dashboard metric — it's the fingerprint of a cold-start leak.

## Spot/preemptible GPUs: the cold start, scheduled

Cheap preemptible capacity (60–90% discounts) is the standard for
throughput tiers — the price is that preemption *is* a cold start with
30 seconds' notice. The playbook: checkpoint nothing (inference is
stateless per request), drain gracefully, replace from the warm pool,
and never let spot + cold-start-naive autoscaling meet a traffic spike.
Warm pools + spot is the cost/sleep trade of this module, made explicit.

## Check yourself

1. Your 70B BF16 replica takes 6 minutes to become ready. Compute the
   weight-load component (weights ≈ 140 GB) at 300MB/s and 1GB/s, and
   name which toolbox item buys back most of it.
2. Why does a readiness probe that passes when "the HTTP server is
   listening" cause errors rather than just slow starts?
3. Design the warm pool for: night peak 2 RPS, day peak 20 RPS, cold
   start 4 minutes, scale-out signal reaction 10s. State the floor and
   what the 10s reaction time can and cannot save.

Next: [070 — Prefix-aware routing](070-prefix-aware-routing.md)
