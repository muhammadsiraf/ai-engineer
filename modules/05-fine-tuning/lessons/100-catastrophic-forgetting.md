# Catastrophic forgetting

**Reading time:** ~6 min · Module 5

Fine-tuning optimizes the behavior you trained for. Nobody voted for what
happens to everything else: the same gradient steps that install the new
behavior can overwrite the general capabilities that made the base model
worth deploying. That's catastrophic forgetting, and it's the tax every
fine-tune pays — the question is how much, and whether anyone measured.

## The mechanism, briefly

The base model's capabilities are distributed across weights in ways that
overlap with your task's updates. Descent on your loss moves shared
parameters; representations supporting untrained skills (reasoning, other
domains, longer contexts, safety behaviors) degrade as collateral. The
degradation is *silent on your eval* — your golden set scores the task,
not the world.

## Why LoRA helps (and how much)

- **Small delta, frozen base:** only the low-rank adapters move; the base
  — the substrate of general capability — is untouched. Empirically LoRA
  forgets much less than full FT at matched task gains.
- **Fewer steps on narrow data:** 1–3 epochs (lesson 080) vs the many
  passes full FT tempts you with.
- **Residual forgetting still happens:** the adapters change outputs on
  *all* inputs, not just task inputs — the delta doesn't know where your
  task ends. Measure it anyway (below).

## The measurement that makes it real

Hold out a **general-capability slice**: a few hundred prompts across
reasoning, general knowledge, different languages, safety probes, your
long-context cases — *scored with the same judge/rubric discipline* (M4
lesson 120; Module 7). Run it on base and on every checkpoint. The
forgetting report is one table: task gain vs general-capability delta,
per checkpoint. Every fine-tuning decision doc includes it; "the task
score went up" alone is not a result.

## The mitigation toolbox, in order of cheapness

1. **Fewer epochs / lower LR / smaller r** — the overfitting knobs are the
   forgetting knobs; usually the only ones you need.
2. **Mix in general data** (5–20% replay): generic instruction examples in
   the training mix anchor the general distribution. Costs a bit of task
   peak; buys capability stability.
3. **Merge with care:** adapter merging coefficients (lesson 130) let you
   scale the delta back (e.g., 0.7x) when eval says the task survives.
4. **Full FT only with replay + model averaging (soups/EMA)** — the
   heavy-machinery end; you'll know if you're there.

## The tie back to deployment

A fine-tune is a *trade*, and the trade has two sides. Module 6's rollout
discipline treats the fine-tuned model exactly like any new artifact: canary,
compare against incumbent on BOTH eval slices, roll back on regression.
The forgetting table is the rollback criterion written down in advance.

## Check yourself

1. Your task score rose 8 points. What table do you produce before
   calling that a win, and what result in it would change the decision?
2. Why can LoRA still forget even though the base weights never move?
3. Rank the mitigations by cost and by effectiveness; where does the
   "5–20% replay mix" land on both axes, and why is it the workhorse?

Next: [110 — Evaluating a fine-tune](110-evaluating-a-fine-tune.md)
