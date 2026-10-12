# Inference is a scheduler problem

**Reading time:** ~6 min · Module 3

Module 3 is the first inside-the-serving-stack module: what actually happens
between your HTTP request and the tokens coming back, and why the difference
between a naive and a good inference server is 10x throughput. The framing
that unlocks everything: **LLM serving is an OS scheduling problem.**

## The three resources

Serving one generation consumes, simultaneously:

1. **Compute** — GPU matmuls for every layer, every token
2. **VRAM** — weights (fixed) + KV cache (grows per sequence, per token — lesson 040)
3. **Time** — the serial decode loop (Module 1 lesson 130)

The scheduler's job: pack as many concurrent sequences as possible onto the
same weights and the same GPU without violating anyone's latency SLO. Weights
are *shared, read-only* — 10 users asking the same model don't need 10 copies
of 16 GB. That sharing is the entire economic opportunity.

## Why batching is the superpower

Run one request at a time and your GPU is mostly idle: a single decode step's
matmuls are too small to saturate the hardware (memory-bandwidth-bound — each
weight byte is read to produce a few tokens' worth of math). Batch 32
sequences together and the *same* weight read serves all 32 — GPU utilization
and tokens-per-second-per-dollar jump. Throughput per request drops slightly
(interference), aggregate throughput soars.

All of Module 3's machinery exists to answer scheduler questions:

| Question | Lesson |
|---|---|
| What state does a sequence hold between steps? | KV cache (030–040) |
| How to avoid VRAM fragmentation killing batch size? | PagedAttention (050) |
| When do new requests join the batch? | continuous batching (060) |
| How to skip recomputing shared prompts? | prefix caching (070) |
| How to shrink per-sequence state? | quantization (080–090) |
| How to start output sooner? | speculative decoding (100) |
| What if the model doesn't fit one GPU? | parallelism (110) |
| What trade-off governs it all? | throughput vs latency (120) |

## The two clock regimes (recap, with serving eyes)

From Module 2 lesson 110: TTFT = queue + prefill; TPS = decode. The scheduler
affects both differently:

- **Queue time** is pure scheduling — batch full? request waits. This is why
  p95 TTFT explodes exactly when load exceeds capacity (and why lesson 120's
  SLO math matters).
- **Prefill** is compute-bound (big parallel matmuls over your prompt).
- **Decode** is memory-bandwidth-bound (read weights + KV cache per token).

That last asymmetry — *prefill compute-bound, decode bandwidth-bound* — is
the single most useful sentence in this module. It explains batching gains,
prefix caching's value, and why chunked prefill exists.

## The utilization wall

Cost per million tokens ≈ GPU-hour price ÷ tokens the GPU-hour produces.
Every optimization in this module attacks the denominator: more concurrency
(batching), less redundant work (prefix caching), smaller state (quantization),
faster decode (speculation). A naive stack produces 500 tok/s/GPU; a tuned
vLLM deployment produces 10,000+. Same GPU, same model — 20x on the
denominator. That's why inference engineering is a discipline.

## What you'll build in this module

Six challenges, all arithmetic and simulation, no GPU needed: timing a
request, KV-cache sizing (the VRAM formula), prefix-cache savings, precision
selection, speculative-decode speedup, and batch-size-from-SLO. The numbers
you compute here are the numbers you'll configure in Module 6's real vLLM
deployment.

## Check yourself

1. Why don't concurrent requests need separate copies of the weights?
2. Why is decode memory-bandwidth-bound but prefill compute-bound? (Hint:
   how much work per weight byte in each phase?)
3. Your p95 TTFT triples every weekday at 10:00. Scheduler intuition: what's
   happening, and which two lessons address it?

Next: [020 — Prefill and decode](020-prefill-and-decode.md)
