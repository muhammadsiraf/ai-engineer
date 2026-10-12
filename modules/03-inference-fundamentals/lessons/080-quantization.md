# Quantization

**Reading time:** ~7 min · Module 3

Quantization — storing and computing with fewer bits per weight — is the
cheapest capacity multiplier in inference. FP16 → INT4 is 4x smaller models
and KV caches for typically <1% quality loss. But "typically" is doing work
in that sentence; this lesson covers what's actually happening to the
numbers, and how to choose a precision deliberately.

## The core idea

Weights are floats whose information content is far below their FP16
precision. Empirically, weight distributions cluster near zero with long
thin tails (lesson 080 of Module 1). Quantization maps them to a small grid
of representable values:

```
x_q = round(x / scale) + zero_point        (per-group, usually 64–128 weights)
x   ≈ (x_q − zero_point) × scale           (dequantize for compute)
```

The `scale`/`zero_point` per group absorb the distribution's shape. All the
engineering is in *how you choose scales*: that choice is the difference
between "free 4x" and "the model got stupid."

## Precision ladder and what it costs

| Format | Bits | 8B model | Typical quality |
|---|---|---|---|
| FP32 | 32 | 32 GB | reference (training) |
| BF16/FP16 | 16 | 16 GB | indistinguishable for serving |
| INT8 (W8A8) | 8 | 8 GB | ~lossless for most tasks |
| INT4 (W4A16: GPTQ/AWQ) | 4 | ~4.5 GB | 0.1–1% avg quality drop; watch edge tasks |
| FP8 (W8A8, H100+) | 8 | 8 GB | near-lossless, hardware-accelerated |

The pattern that matters: **weights tolerate 4 bits surprisingly well;
activations and attention states are more delicate** (KV-cache quantization
to FP8: fine; INT4 KV: usually not). When a quantized model fails, it fails
on the tail: rare languages, exact arithmetic, long-range retrieval, niche
code — precisely where you might have needed it.

## Post-training quantization (PTQ) algorithms, in one pass each

- **RTN (round-to-nearest):** exactly what it says. Baseline; degrades
  visibly at 4 bits.
- **GPTQ:** quantize weights column-by-column, using second-order (Hessian)
  info to compensate each round-off with adjustments elsewhere. Strong 4-bit
  quality; one calibration pass over ~128–512 samples.
- **AWQ:** activation-aware — protect the ~1% of weight channels that
  activations actually flow through (scale them before quantizing).
  Robust, fast, popular for serving.
- **FP8:** not grid quantization but a smaller float format — with H100+
  tensor-core support it's often the best *speed* option where hardware
  allows.

You don't implement these; you *choose* among them and **measure** (next
paragraph). The precision-sweep challenge has you model the decision
arithmetic: VRAM saved vs quality lost vs hardware support.

## The decision procedure (the part to internalize)

1. **Establish your golden set FIRST** (Module 7 discipline; ~100+ tasks
   with judged outputs). No eval, no quantization — that's the rule.
2. **Sweep:** run the set on FP16 / INT8 / INT4 variants. Record quality
   *per task category*, not just average — averages hide the exact
   failures quantization causes.
3. **Apply the threshold:** ship the smallest precision whose worst
   category drop is within your product tolerance (e.g., ≤2 points on
   every category). Not the best average — the smallest acceptable
   worst-case.
4. **Re-run the sweep on every model upgrade.** Quantization interacts with
   model versions in surprising ways; a sweet INT4 recipe for v1 says
   nothing about v2.

## What quantization buys, concretely (tie to lesson 040)

- Weights: 16 GB → 4.5 GB (8B INT4) — fits a 16 GB card with real KV room,
  or doubles concurrency on the same card.
- KV cache in FP8: halves per-token bytes → doubles sequences-per-GPU.
- Bandwidth: decode is bandwidth-bound (lesson 020) — fewer bytes per
  weight read = faster decode. INT4 serving is often *faster*, not just
  cheaper.

The full picture — precision × context × concurrency × speed — is exactly
the `pick_precision` challenge: given a GPU budget and an SLO, choose the
configuration, show the arithmetic, and say what you'd measure to confirm.

## Check yourself

1. Why do quantization failures concentrate in tail tasks rather than
   shifting everything uniformly worse?
2. Your 8B FP16 deployment serves 12 concurrent sequences (lesson 040's
   example). Roughly what does INT4-weights + FP8-KV buy?
3. Why is "the INT4 model scored 1 point lower on average" an unacceptable
   evaluation, and what would you demand instead?

Next: [090 — Quantization formats](090-quantization-formats.md)
