# Reading loss curves honestly

**Reading time:** ~6 min · Module 5

The training loss curve is the most displayed, least informative artifact
in fine-tuning. It tells you the optimization *ran*; it cannot tell you
whether the model got *better* — and the ways it misleads are systematic
enough to catalog.

## What the curve can tell you

- **Divergence:** loss explodes → learning rate too high, data bug, or
  numerics. Unambiguous; fix and rerun.
- **Underfitting:** training loss still descending steeply at the end →
  more epochs or capacity (r), assuming data quality.
- **Plateau shape:** where it flattens and how noisy it is (batch-size
  hint). Fine-grained but real.
- **Spikes:** a spike at step N is usually one batch (long sequence,
  corrupted example). Log batch contents; make spikes debuggable.

## What it cannot tell you

- **Whether eval improved.** The correlation between training loss and
  task quality is real but loose, and *inverts* under overfitting:
  lesson 080's epoch-3 run has the best loss and worse answers.
- **Whether the model got weirder.** Loss is computed on *your*
  responses; the cost to other capabilities (lesson 100) is invisible on
  this axis by construction.
- **Whether data quality is binding.** Wrong labels lower loss
  perfectly well — the model learns your errors fluently.

The rule that fixes this: **no training run without an eval run.** Checkpoint
each epoch, run the golden set (lesson 110) on each, and pick checkpoints
by *eval*, never by loss. The loss curve is for debugging the optimizer;
the eval table is for choosing the artifact.

## The three panels worth plotting

1. Training loss (per-step, smoothed) — optimizer health.
2. **Eval loss on a held-out slice, same template/mask** — the honest
   generalization signal *for the next-token objective*; it rises when
   training loss falls = textbook overfitting, visible early.
3. Task metrics per checkpoint (your golden set) — the decision-maker.

When panel 2 rises while panel 3 is flat or falling, trust panel 3 for
the narrow task and investigate forgetting (lesson 100) for everything
else.

## Honesty about the eval too

Held-out eval loss is dominated by examples *like your training data*
(if you split randomly). Split by *source document / author / time* when
you can — the "random split" overstates generalization precisely where
production will test it. This is the same lesson as Module 7's eval-set
discipline: the split IS the experiment.

## Check yourself

1. Two runs, same data: run A loss 0.8, run B loss 0.95. B scores higher
   on your golden set. Give three explanations, ordered by likelihood.
2. Why does eval loss rise while training loss falls, mechanically —
   and which single hyperparameter most directly trades one against the
   other?
3. Your eval set was split randomly from training data. What specific
   production scenario will your numbers most overestimate?

Next: [100 — Catastrophic forgetting](100-catastrophic-forgetting.md)
