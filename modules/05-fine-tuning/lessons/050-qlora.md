# QLoRA

**Reading time:** ~6 min · Module 5

QLoRA (Dettmers et al., 2023) is one idea with a big consequence: *quantize
the frozen base to 4-bit, then run ordinary LoRA on top.* The adapters
train in full precision; the base just needs to be *stored and read*
cheaply. Result: 7B–70B fine-tunes on a single commodity GPU, with
published quality within noise of 16-bit LoRA on most benchmarks.

## The stack, layer by layer

1. **4-bit NormalFloat (NF4)** storage for the frozen base. Information-
   theoretically motivated for the bell-shaped weight distributions you
   met in Module 1: the 4-bit codebook spends its levels where weights
   actually live, beating uniform INT4 at the same width. (Module 3
   lessons 080/090 — this is the same quantization story, repurposed
   from serving to training.)
2. **Double quantization:** even the quantization scale constants get
   quantized (FP8→FP4-ish per group). Saves ~0.4 bits/param — meaningful
   at 65B, invisible at 7B, free to enable.
3. **Paged optimizer states:** NVIDIA unified-memory spills optimizer
   state to CPU RAM when a long-sequence gradient spike hits. Prevents
   the classic OOM-on-the-longest-example.
4. **LoRA adapters in BF16** on top, trained normally (lessons 030/040
   unchanged). Gradients flow through the *dequantized* weights —
   compute happens in BF16; only storage is 4-bit.

## The VRAM arithmetic (the challenge's job)

Ballpark for a 7B model, QLoRA, r=16 on q,v+MLP, batch via accumulation:

- base: 7e9 × 0.5 bytes ≈ 3.5 GB
- adapters + gradients + Adam states: tens–hundreds of MB
- activations: the real variable — batch size × sequence length ×
  model width; gradient checkpointing trades ~30% step speed for
  most of it

~4–6 GB + activations → fits a 12 GB card comfortably, a 24 GB card with
room for long sequences. Full FT of the same model: ~112 GB+ (lesson
020's 16 B/param). **That ratio — roughly 20x — is the whole value
proposition**, and the challenge makes you compute both sides.

## When QLoRA is the wrong choice

- You have H100s idle and need maximum quality on a hard task: full FT or
  16-bit LoRA removes the quantization question entirely.
- Training-time is dominated by reading the base either way; QLoRA's
  dequantize-on-the-fly makes steps *slower* than 16-bit LoRA (~10–30%
  typical). It buys memory, not speed.
- Extrema-sensitive tasks: NF4's outliers handling is good but not magic;
  eval decides (always).

## The one-paragraph default

`load_in_4bit(NF4, double_quant) + LoRA(r=16, α=32, q,v+MLP) +
checkpointing + grad accumulation` is the 2026 default for task adaptation
on modest hardware. Everything else in this module — data (060), masking
(080), curves (090), eval (110) — is unchanged by it.

## Check yourself

1. Why do the adapters stay in BF16 while the base is 4-bit — what would
   go wrong training the adapters at 4-bit too?
2. Compute rough VRAM for QLoRA on a 13B model (0.5 B/param base) with
   ~2 GB of activations, and compare full FT at 16 B/param.
3. Your QLoRA run OOMs only on the longest 1% of sequences. Which of the
   four stack pieces addresses exactly this, and what's the manual
   fallback?

Next: [060 — Building a fine-tuning dataset](060-building-a-fine-tuning-dataset.md)
