# Size the KV cache

**Reading time:** ~8 min · Module 3

Last lesson gave you the formula; this lesson makes you fast and safe with
it — because "will this fit" and "how many users fit" are daily questions,
and getting them wrong means OOM crashes or idle GPUs. This is the VRAM
budget lesson.

## The full VRAM budget, top to bottom

```
VRAM_total
  ├─ weights          = params × bytes_per_param        (fixed)
  ├─ activations      = transient workspace             (small, but not zero)
  ├─ CUDA/framework   ~1–2 GB overhead                  (fixed-ish)
  └─ KV cache pool    = whatever remains                (the flexible part)
                          └─ Σ over live sequences of
                             2 × L × H_kv × d_head × n_tokens × bytes
```

Serving engines reserve a KV pool at startup (vLLM: 90% of free VRAM by
default minus weights) and everything else is allocation from that pool.

## Worked example, end to end

Serve Llama-3-8B on one 24 GB card (RTX 4090 / L4):

```
weights (FP16):      8B × 2 = 16.0 GB
overhead:            ~1.5 GB
KV pool:             24 − 16 − 1.5 ≈ 6.5 GB
per-token KV (GQA, 8 kv-heads, d_head 128, L=32, FP16):
  2 × 32 × 8 × 128 × 2 = 131,072 B/token ≈ 128 KB/token
capacity:            6.5 GB ÷ 128 KB ≈ 52,400 tokens of total cache
```

Now the scheduler questions answer themselves:

- 4k-context chat (4,096 tokens each): **~12 concurrent sequences**
- 8k contexts: ~6 concurrent
- With INT8 KV cache: doubles both numbers

Twelve users per $1,600 card, or you quantize. Every serving decision is
this multiplication chain.

## The questions this arithmetic answers

**1. "Can I serve model X on GPU Y at precision P?"**
weights(P) + overhead + min_cache < VRAM_total. If min_cache is negative,
the answer is no before any user arrives.

**2. "How many concurrent users at context C?"**
`floor(KV_pool ÷ bytes_per_token(C_max))` — then derate 20–30% for
fragmentation and burst alignment (next lesson fixes part of that).

**3. "What's my throughput ceiling?"**
Concurrency × (1/mean_interarrival) roughly; decode throughput per batch
size comes from lesson 120's measurements. Multiply into $/M-token
(lesson 100 of Module 2's ratio math).

**4. "Should I shorten max context?"**
Halving allowed context doubles capacity. If 95% of conversations die by
2k tokens, capping at 4k buys you 2x concurrency for a rare truncation —
an unusually honest product/cost trade.

## The traps

- **Forgetting GQA:** naive formula overestimates 4x on Llama-3-class
  models; you'd buy 4x too much GPU.
- **Forgetting generation length:** cache grows during decode; budget
  `prompt_max + output_max`, not prompt averages.
- **FP16 everywhere:** KV quantization to FP8 is nearly free quality-wise
  for most workloads and doubles capacity. The precision challenge (next
  challenge set) covers choosing.
- **Forgetting overhead:** that 1.5 GB of CUDA context is real; "the math
  says it fits" then the first request OOMs.

## The interactive calculator

The challenge for this lesson builds a `VRAMBudget` class: given model spec
(layers, kv-heads, d_head), precision, GPU size, overhead — answer
`max_concurrent(context)`, `fits(model, precision, gpu)`, and
`tokens_capacity()`. Tests encode every worked example above. Fifteen
minutes to build; you'll reopen it for every deployment decision in
Modules 5–6.

## Capacity planning in one paragraph

For your Module 6 deployment: measure mean and p95 tokens-per-request from
real traffic (Module 2 lesson 090's counting), apply this lesson's formula
for concurrency, apply lesson 120's batch/throughput numbers for requests
per second, and buy 30% headroom. That's the entire capacity plan — the
rest is monitoring (Module 6's observability lesson) to catch where reality
drifts from the model.

## Check yourself

1. Re-do the 24 GB worked example with FP8 weights AND FP8 KV cache.
   What's the concurrency at 4k contexts?
2. Traffic: mean prompt 900 tokens, mean output 250, p99 output 1,800.
   What context budget do you size per sequence, and why p99-driven?
3. Why does "barely fits with zero KV room" make a model unservable even
   though it loads?

Next: [050 — PagedAttention](050-pagedattention.md)
