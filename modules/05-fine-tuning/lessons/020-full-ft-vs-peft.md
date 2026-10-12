# Full fine-tuning vs PEFT

**Reading time:** ~7 min · Module 5

You have a base model and a task. One fork immediately: update *all* the
weights (full fine-tuning) or a tiny injected subset (parameter-efficient
fine-tuning, PEFT). The fork is mostly about VRAM, artifacts, and what
you're willing to put at risk.

## Full fine-tuning

Every weight updates. Maximum expressiveness — the model can reorganize
itself — and maximum cost:

- **VRAM:** weights + gradients + optimizer states. With Adam (the
  default), that's roughly **16 bytes per parameter** in mixed precision:
  4 (FP32 master weights) + 4 (gradient) + 8 (Adam's m and v states),
  plus activations. An 8B model: ~128 GB before activations — multi-GPU
  territory (Module 3 lesson 110's parallelism applies to training too).
- **Artifacts:** every run produces a *whole model*. Storage, versioning,
  and deployment all scale with full size; rolling back means rolling back
  everything.
- **Risk:** full updates can move *any* behavior, including ones you liked
  (lesson 100's forgetting), and catastrophic divergence mid-run eats the
  whole budget.

You choose full FT when the behavior change is deep and broad (a new
language, major domain shift, continued pretraining) and you have the
infrastructure. It is rarely the right first choice for task adaptation.

## PEFT: the LoRA-shaped family

Freeze the base; learn a small delta. LoRA (next two lessons) is the
workhorse; its cousins — prompt tuning, prefix tuning, IA³, VEra — trade
slightly different capacity/shape curves. The shared wins:

- **VRAM:** no optimizer state or gradients for frozen weights. The 8B
  model above: LoRA trains a few tens of millions of parameters →
  optimizer memory collapses; with QLoRA (lesson 050) the whole run fits
  a 24 GB card.
- **Artifacts:** a 10–200 MB adapter per run instead of 16 GB. A/B them,
  stack experiment histories, keep per-customer variants.
- **Composability:** one base model serves many adapters (lesson 130).
- **Bounded blast radius:** the base is untouched; the delta is small
  enough to inspect, and worst case you delete the adapter.

The quality gap vs full FT, at matched data, is small for task adaptation
— close enough that PEFT's operational wins win the default.

## The default decision

Task adaptation → **LoRA (or QLoRA if VRAM-tight)**. Deep/broad change →
full FT. Truly no training infra → API-provider fine-tuning endpoints
(some offer LoRA under the hood; you trade control for convenience).

Everything from lesson 060 on — datasets, templates, loss masks, curves,
forgetting, evaluation — applies to *both* paths; the module's challenges
use LoRA arithmetic because that's what you'll actually run.

## Check yourself

1. Where does the 16x VRAM difference between full FT and LoRA come from?
   Name the three components that disappear.
2. Your team insists on full FT "for maximum quality." What data settles
   the argument, and what's the expected result for a task-adaptation
   job?
3. Why is "one base + many adapters" an operational advantage beyond
   storage? Name two production consequences.

Next: [030 — LoRA in one decomposition](030-lora-in-one-decomposition.md)
