# Quantization formats

**Reading time:** ~6 min · Module 3

"GPTQ," "AWQ," "GGUF," "FP8," "bitsandbytes" — the format zoo is genuinely
confusing because each name bundles three separate decisions: *what math*,
*what storage*, and *what runtime*. This lesson separates the axes so the
names become legible, then maps which format fits which deployment
(Module 6 uses one of them for real).

## The three axes

**Axis 1 — bit width & arithmetic:** FP16/BF16, FP8 (E4M3/E5M2), INT8,
INT4. Determines speed and hardware support.

**Axis 2 — quantization algorithm:** RTN, GPTQ, AWQ, plus dynamic methods
that quantize at load time. Determines quality at a given width.

**Axis 3 — container/runtime:** safetensors (raw tensors), GGUF
(llama.cpp's format, CPU/edge-friendly, bundles metadata + mmap-able
quantized weights), bitsandbytes (on-the-fly, training-adjacent), engine
formats (vLLM/TensorRT-LLM take GPTQ/AWQ/FP8 checkpoints directly).

A model card line like *"Llama-3-8B AWQ 4-bit (INT4, W4A16, safetensors)"*
now reads as: algorithm AWQ, width 4-bit weights / 16-bit activations,
container safetensors.

## W-x-A-y notation

`W4A16` = 4-bit **W**eights, 16-bit **A**ctivations: dequantize weights to
FP16 for the matmul (memory savings; compute still FP16). `W8A8` /
`W4A16` vs `FP8` (both weights and activations in FP8, hardware matmul):

| Regime | Memory | Speed | Hardware story |
|---|---|---|---|
| W4A16 (GPTQ/AWQ) | best | good — bandwidth win on decode | any modern GPU |
| W8A8-INT8 | good | good | mature kernels everywhere |
| FP8 (E4M3) | good | best on H100+/Ada | recent tensor cores only |
| W4A4 experimental | smallest | mixed | kernel-limited |

Decode is bandwidth-bound (lesson 020), so **W4A16's smaller weight
reads already speed up decode** even without special hardware — the most
common production sweet spot for 7–13B-class models on commodity GPUs.

## Group size and scales, the quality knob

Within an algorithm, granularity matters: per-tensor scales (coarse) < per-
channel < per-group-of-64/128 (fine). Finer groups = more scale metadata =
better quality at the same bit width. The format zoo's "g128" tags are this
knob. When comparing two 4-bit variants that score differently, group size
is often the whole story.

## Choosing per deployment shape

- **Cloud GPU serving, recent hardware (H100/L40S):** FP8 weights+KV where
  supported; AWQ-INT4 otherwise. (Module 6's vLLM lab: W4A16 AWQ on a
  commodity card.)
- **Single-user / local / edge:** GGUF via llama.cpp (Q4_K_M etc.) —
  mmap-able, CPU/GPU hybrid, quantization quality tuned by community
  wizardry. Different ecosystem, same axes.
- **Big models across many GPUs:** per-GPU FP16 with parallelism (lesson
  110) often beats INT4-of-a-huge-model on quality; quantify before
  assuming quantization is right at the frontier scale.
- **Fine-tuning interplay (Module 5 preview):** QLoRA trains adapters *on
  top of* a 4-bit frozen base (W4A16 + adapters in BF16). The formats here
  are the same formats; Module 5 exploits them for training-time VRAM.

## Conversion and verification workflow

1. Get or make the checkpoint (e.g., `auto-awq` / `gptq-models` tooling) —
   or download a community-quantized release *only with a known provenance*
   (random-repo quantizations are a real supply-chain risk; prefer
   official/first-party uploads).
2. **Verify the quantization itself:** perplexity delta vs FP16 on a fixed
   corpus, spot-check a few generation tasks, confirm logits sanity. (A
   broken conversion — wrong scale groups, mismatched config — usually
   shows up as gibberish or subtly deranged output. Catch it in staging.)
3. Benchmark: VRAM (nvidia-smi), TTFT/TPS at your batch (lesson 120),
   quality on the golden set. Record all three against the FP16 baseline
   in your decision doc.

## Check yourself

1. Decode "Qwen2-7B-Instruct GPTQ-Int4 g128 W4A16" into the three axes.
2. Why does W4A16 speed up decode more than prefill? (Hint: which phase is
   bandwidth-bound?)
3. Two community INT4 checkpoints of the same model differ 3 points on your
   set. Give the two most likely technical causes.

Next: [100 — Speculative decoding](100-speculative-decoding.md)
