# LoRA in one decomposition

**Reading time:** ~7 min · Module 5

Fine-tuning changes weights by some delta: `W_new = W_0 + ΔW`. The LoRA
observation (Hu et al., 2021): the deltas that matter live in a *low
dimension* — you can write the update as a product of two skinny matrices
and train only those:

```
h = W_0 x  +  (α/r) · B A x

W_0 ∈ ℝ^{d×d}   frozen
A    ∈ ℝ^{r×d}  "down" projection   (initialized: small random)
B    ∈ ℝ^{d×r}  "up" projection     (initialized: zeros)
r ≪ d        the "rank" — 8, 16, 32, 64 are typical
α            the scale — see lesson 040
```

Three properties fall straight out of the algebra, and each is the answer
to a production question.

## 1. Trainable parameters collapse

Full square update: d² parameters. LoRA: 2·r·d. For d=4096, r=16:
4096² = 16.8M per matrix → 2·16·4096 = **131k** — a 128x reduction per
layer, and it compounds across the model (the challenge has you compute
the real totals). Optimizer states and gradients exist *only* for A and B,
which is where lesson 020's VRAM win comes from.

## 2. Inference cost is zero

At serving time, `B·A` is a d×d matrix; fold it in: `W_merged = W_0 +
(α/r)·BA`. One matrix multiply, no adapters at runtime. Alternatively keep
adapters separate and *swap* them per request (lesson 130's trade).

## 3. Zero-initialization of B means the run starts as the base model

B=0 at step 0 → the delta contributes nothing → training begins exactly at
the pretrained behavior and drifts from there. That's not a convenience;
it's why LoRA runs are stable. (A starting at random and B at zero is the
canonical choice; A=0/B=random would break symmetry and zero-gradient
properties differently — the details matter less than knowing the *start
is the base model*.)

## Where to attach adapters

Originally attention projections only (W_q, W_v); modern practice adds the
MLP projections (gate/up/down), sometimes all linear layers. More targets
= more capacity + more trainable params + slower steps. The sweep is
cheap with adapters; start with q,v + MLP and expand if eval says
underfit.

## What LoRA can't do

The low-rank assumption is a real constraint: massive knowledge injection
or deep behavioral rewiring can saturate it (eval will show a plateau no
rank bump fixes — and that's your signal to reconsider data or move to
full FT, not to keep turning the r knob).

## Check yourself

1. Derive the trainable-parameter count for r=32, d=4096, applied to both
   W_q and W_v of one layer. Then compute the full-FT count for the same
   two matrices.
2. Why does B=0 initialization make training *stable*, mechanically?
3. Your LoRA eval plateaus at r=16, 32, 64 identically. What does that
   tell you the bottleneck is — capacity or data — and why?

Next: [040 — LoRA rank and alpha](040-lora-rank-and-alpha.md)
