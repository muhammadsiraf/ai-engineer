# LoRA rank and alpha

**Reading time:** ~6 min · Module 5

Two hyperparameters control every LoRA run, and they control *different*
things: r is capacity, α is scale. Confusing them produces runs that are
either silently underpowered or silently mis-scaled.

## Rank r: the capacity knob

r is the dimension of the update subspace — how many independent
directions the adapter can move the output in. Empirical folklore, all
confirmable on your own eval:

- **r=4–8:** style/tone/format shifts, small closed tasks.
- **r=16–32:** the default for instruction-following and domain
  adaptation. The shock of the LoRA literature is how little quality
  improves beyond ~32 for most task work.
- **r=64+:** larger datasets, harder tasks, diminishing returns — and
  past some point you're paying VRAM/step-time for nothing (lesson 030's
  plateau signal).

Cost scales linearly in r: trainable params 2·r·d per target matrix,
optimizer state and step time with it.

## Alpha α: the scale knob

The delta enters as `(α/r)·BA` — α sets how *loud* the update is
relative to the frozen weights, independent of how many directions it
uses. The effective learning-rate multiplier on the delta path is α/r:

- Double α (r fixed): every value of BA counts twice as much.
- The community convention: **set α = 2r** (or α = r) and *tune r*, so
  that one knob moves capacity and the other stays pinned. What's
  dangerous is moving both at once: r=8→32 with α fixed just quietly
  quartered your effective scale; the run then "underperformed" for a
  reason that had nothing to do with capacity.

## The two failure signatures

- **Underfit (r too low):** eval plateaus below baseline-possible; training
  loss itself struggles to fall; increasing r (with α/r held) moves it.
- **Mis-scaled (α/r wrong):** training loss falls but the model drifts
  from its prior skills (lesson 100) or the delta overwhelms the base —
  outputs get weird in ways unrelated to the task. Signature: great on
  task, worse at everything else, at *any* r.

The lesson: when a run disappoints, ask *which knob's* failure mode you're
looking at before touching anything. This is the same discipline as
Module 3's latency debugging: signature → component → knob.

## Practical recipe (the one you'll actually run)

1. r=16, α=32, targets q,v + MLP projections, LR ~1–2e-4.
2. Eval. Underfit → r=32 (α=64). Overfit/drifty → r=8, more data.
3. Only after data quality is ruled out (lesson 060) touch anything else.

## Check yourself

1. A teammate doubles r from 16 to 32 and leaves α=16, then reports "more
   rank made it worse." What actually happened, and what's the control
   experiment?
2. Why does the community set α proportional to r instead of leaving α
   fixed at, say, 16 forever?
3. Cost check: r=8 vs r=64 on a 7B model with q,v+MLP targeted — order
   the two configs by trainable parameters by roughly what factor?

Next: [050 — QLoRA](050-qlora.md)
