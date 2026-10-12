# Merging vs serving adapters

**Reading time:** ~6 min · Module 5

Training is done; the artifact is a base model plus adapters. The
deployment question: fold them together (merge) or keep them separate
(dynamic adapter serving)? This is an operations decision with quality
and latency consequences — and it's reversible, which shapes everything.

## Merging: fold the delta in

`W_merged = W_0 + (α/r)·BA` — precompute once (lesson 030's property 2):

- **Zero runtime overhead:** the model is a plain model. Any engine, any
  quantization, no adapter-aware stack required (Module 3's serving
  arithmetic applies unchanged).
- **Quantize after merging** (the standard pipeline), then *re-evaluate*
  (lesson 110's rule 3).
- **One artifact per adapter:** ten adapters = ten model copies. Storage
  is cheap; the real cost is rigidity — changing the base model means
  re-merging and re-validating everything.
- **Merging coefficients:** `W_0 + λ·(α/r)·BA` with λ<1 dials the adapter's
  strength back — the cheapest fix when lesson 100's forgetting table
  says "task great, general worse, but not catastrophically."

## Dynamic adapter serving: swap per request

Keep the base resident; load adapters as small overlays. vLLM and peers
serve many adapters against one base, switching per request (or batching
across them):

- **One base, many behaviors:** per-customer or per-task adapters on a
  single serving fleet — the VRAM for the base is paid once (Module 3
  lesson 040's arithmetic, multiplied).
- **Sub-millisecond switching** in the better engines; hot-swap new
  adapters without a redeploy — the fastest rollout story in this module.
- **Costs:** adapter-aware engine required (a real constraint on where
  you can deploy), slight per-token overhead in some implementations,
  quantization interacts (a 4-bit base + BF16 adapters is exactly QLoRA's
  serving shape — fine, but measure, don't assume).

## The decision table

| Situation | Choice |
|---|---|
| One adapter, all traffic, any engine | **Merge** |
| Many adapters, shared fleet | **Dynamic serving** |
| Target engine can't do adapters | **Merge** |
| Per-customer isolation requirements | **Dynamic** (or separate deployments) |
| Fast experiment cadence | Dynamic in staging; merge winners |

The hybrid default: develop and A/B dynamically, *merge the winners* for
the production path. The adapter file is small — keep it in the repo as
the source-of-truth artifact even after merging; it's your diff against
the base and your undo button.

## Check yourself

1. Why does merging "before quantizing" order matter, and what goes wrong
   with the reverse?
2. Ten enterprise customers, each with a private adapter, one GPU fleet.
   Compute the naive merged approach's VRAM (7B BF16 ≈ 14 GB) vs dynamic.
3. Your forgetting table says λ≈0.7 looks right. Why is that knob an
   argument *for* keeping adapters unmerged in staging?

Next: [140 — Continuous fine-tuning](140-continuous-fine-tuning.md)
