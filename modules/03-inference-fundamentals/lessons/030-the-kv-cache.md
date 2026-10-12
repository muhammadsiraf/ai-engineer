# The KV cache

**Reading time:** ~7 min · Module 3

The KV cache is the most consequential data structure in LLM serving. It's
why generation costs are survivable at all — and it's the resource your
capacity planning revolves around. Lesson 110 of Module 1 introduced it;
this lesson makes it mechanical.

## What it caches, precisely

Recall attention (Module 1 lesson 100): token i's output needs K and V
vectors of all tokens ≤ i. Naive generation would recompute those for the
whole prefix at every step — O(n²) work for n tokens. The cache observation
(KV values of past tokens never change — causality, lesson 110):

**After processing position t once, keep its K and V vectors; every later
step just appends position t+1's and reads the rest.**

Cost per decode step drops from "recompute everything" to "one new position
+ reads." That's the difference between generation being theoretically
quadratic and being linear per token in practice.

## The size formula (memorize this)

Per sequence, per layer, per head, each cached position stores a K vector
and a V vector of dimension `d_head`:

```
KV bytes = 2 × L × H × d_head × (n_prompt + n_generated) × bytes_per_elem
         = 2 × L × d_model × n_tokens × bytes      (since H × d_head = d_model)
```

Concrete: Llama-3-8B (L=32, d_model=4096), FP16 (2 bytes), 4,000 tokens:

```
2 × 32 × 4096 × 4000 × 2 = 2.1 GB per sequence
```

**Two gigabytes for one conversation.** Your 80 GB A100 fits ~35 concurrent
4k-token sequences minus weights (~16 GB) → ~30 effective. THIS arithmetic —
not vibes — is batch capacity. The challenge for this lesson automates it.

## What moves the number

| Lever | Effect |
|---|---|
| Longer context | linear growth — 32k tokens = 16.8 GB(!) |
| Quantized KV cache (FP8/INT8) | halves (or quarters) bytes — small quality cost |
| Grouped-Query Attention (GQA) | fewer K/V heads than Q heads: Llama-3-8B has 32 Q heads, **8 KV heads** → cache = 2 × L × **8** × d_head × ... — 4x smaller than the naive formula |
| Multi-head vs MHA | MHA = worst case; every modern serving model uses GQA or MQA |
| Sliding window / streaming | cap n: old positions' cache evicted |

Recompute the 8B example with GQA (8 KV heads, d_head 128): effective
`2 × 32 × 8 × 128 = 65,536` bytes/token → 4,000 tokens = 262 MB. The GQA
detail is why the naive formula overestimates modern models by 4–8x. Know
your model's *KV head count*, not just its parameter count.

## Cache management = sequence management

The scheduler's real job (lesson 010): VRAM is finite; the cache is the
growing part. Every admission/eviction decision is a cache decision:

- **Admit** a sequence only if `weights + Σ cached + new_seq_max_cache ≤ VRAM`
  (with safety margin)
- **Preempt** (evict) the newest or least-progressed sequence under pressure
  — recompute or swap its cache
- **Cap max context** per request to bound worst-case cache

Fragmentation makes this harder than the arithmetic suggests — allocation
sizes vary per sequence and grow token by token. That's exactly the problem
PagedAttention (next lesson) was built to fix.

## Reading a serving engine's numbers

vLLM's startup log tells you the budget directly:

```
# GPU blocks: 4096, block size 16 tokens → 65,536 tokens of cache
# ~16.4 GB available for KV cache after weights
```

From block count and block size you can compute max concurrent sequences =
blocks × block_size ÷ avg tokens per sequence. Decode the log line and you
own the capacity model — no dashboard required.

## Check yourself

1. Compute KV bytes for a 70B model (L=80, d_model=8192, 8 KV heads,
   d_head=128), FP16, at 8k tokens. Would it fit on one 80 GB GPU alongside
   ~140 GB of weights?
2. Why does causality make the cache *valid* rather than merely helpful?
3. Your provider doubles their price for 32k-token prompts. Using the
   formula, what's the serving-side explanation?

Next: [040 — Size the KV cache](040-size-the-kv-cache.md)
