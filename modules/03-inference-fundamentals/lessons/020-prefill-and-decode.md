# Prefill and decode

**Reading time:** ~7 min · Module 3

Every LLM request runs in two phases with opposite compute personalities.
You met them from the client side (Module 2 lesson 110: TTFT vs TPS); this
lesson is the server-side view, because every serving optimization is a bet
about which phase you're in.

## Phase 1: prefill (processing the prompt)

The prompt arrives — say 2,000 tokens. The model runs **one forward pass
over all 2,000 positions in parallel**, producing:

- the KV cache entries for every prompt position (lesson 030)
- the logits at the last position: your first output token

Because all positions process together, prefill is a small number of huge
matmuls: `(2000 × d) @ (d × d)`. Huge matmuls are exactly what GPUs are for —
**compute-bound**, high arithmetic intensity, excellent utilization.

Prefill cost ≈ `2 × params × prompt_tokens` FLOPs (rule of thumb: 2 FLOPs per
parameter per token). Doubling your prompt roughly doubles prefill work —
this is the mechanical reason long prompts cost TTFT (lesson 110) and why
prompt caching (lesson 070) pays so well.

## Phase 2: decode (generating the answer)

Then the loop, one token at a time: run the model over **one position** —
but the K and V of all previous positions must be read from VRAM (that's the
KV cache) along with all the weights. The matmuls are tiny (`1 × d @ d × d`),
so the GPU spends its time *reading* weights and cache, barely computing —
**memory-bandwidth-bound**.

Decode cost per token ≈ `2 × params` FLOPs of math but `params × bytes +
cache_bytes` of reads. Utilization is terrible: the GPU's compute units idle
while the memory bus streams. This is why batching works (lesson 010):
batch 64 decodes and each weight byte fetched serves 64 sequences — the bus
cost is amortized, arithmetic intensity rises 64-fold.

## The numbers that make it concrete

Arithmetic intensity = FLOPs per byte of memory traffic. Roughly:

```
prefill (batch 1, long prompt):  ~100+ FLOPs/byte   → compute-bound
decode  (batch 1):               ~1-2 FLOPs/byte    → bandwidth-bound
decode  (batch 64):              ~64-128 FLOPs/byte → compute-bound again!
```

That last line is the punchline of the whole module: **batching turns decode
into prefill's personality.** A well-batched decode is nearly free compute
compared to 64 separate decodes.

## Chunked prefill: mixing the regimes

Problem: a 30k-token prefill monopolizes the GPU for hundreds of
milliseconds; everyone else's decode stalls; their TTFT (well, TPOT — time
per output token) spikes. Chunked prefill splits big prompts into chunks
(1–2k tokens) interleaved with decode steps in the batch — smooths the
latency spikes at a small prefill-efficiency cost. vLLM and friends do this
by default; it's why their p95s hold under mixed workloads.

## The KV cache handoff

The bridge between phases: prefill *writes* the cache; decode *reads and
appends* to it, one position per step. This is why:

- the cache is sized by prompt + output (lesson 040's formula)
- prefix caching works — prefilled prefixes are reusable cache state (070)
- cache eviction = killing sequences (050's PagedAttention manages exactly
  this pressure)

## Timing it yourself

The challenge for this lesson: instrument a (mock) two-phase request and
report TTFT, TPOT, and total, then predict how each changes with prompt and
output length. The formula to internalize:

```
total ≈ queue + prefill(tokens_in) + steps × decode_step
      ≈ queue + k₁ × tokens_in + k₂ × tokens_out
```

Calibrate `k₁`, `k₂` from measurements; now you can *predict* latency for
any prompt/output combination — the basis of Module 6's capacity planning.

## Check yourself

1. Your prefill measured 40 ms for 1k tokens and 78 ms for 2k. Roughly
   linear — why, and what would make it worse than linear?
2. A teammate sees batch=1 GPU utilization at 5% and proposes "use more
   compute." Why is that the wrong lever? What's the right one?
3. Why does chunked prefill improve *other* requests' decode latency at a
   small cost to the big-prompt request's TTFT?

Next: [030 — The KV cache](030-the-kv-cache.md)
