# Continuous fine-tuning

**Reading time:** ~6 min · Module 5

The first fine-tune is a project. Fine-tuning as an *ongoing capability* —
new data flows in, the model keeps improving, deployments keep rolling —
is a system. This closing lesson is that system, and it's mostly the
disciplines of Modules 4/6/7 reassembled around a training loop.

## The flywheel

```
production logs → curation queue → labeled/corrected data
      → dataset version N+1 → train → eval gates → deploy → logs...
```

Every arrow is a component you already know: logging (M4 L020), golden
sets (M4 L110), judges (M4 L120), rollout discipline (Module 6), eval
machinery (Module 7). The new engineering is *data operations*: the
curation queue that turns raw usage into training examples.

## Data ops: the actual hard part

- **Harvest failures:** production cases the model got wrong (judge-flagged,
  user-corrected, edited outputs) are the highest-value training data that
  exists — the distribution's hard tail, labeled by reality.
- **Curate before you train:** the correction pass (lesson 060's quality
  bar) doesn't shrink just because data arrived automatically. Budget the
  review capacity *before* building the pipeline, or the queue becomes a
  graveyard.
- **Version datasets like code:** content-addressed, with a changelog per
  version ("+1.2k corrected extraction failures, −380 dupes"). Every model
  artifact records the dataset version that produced it.
- **Rehearsal against drift:** new data skews the distribution
  (seasonality, product changes). Keep the lesson 060 diversity rules
  running per *batch*, not just per dataset.

## Cadence and gates

A sensible loop for a product team: **monthly or on-trigger** (drift alarm,
new product area, quality regression), not continuous. Each cycle runs the
same gates as the first fine-tune, automated:

1. Task eval ≥ incumbent + threshold (lesson 010's memo, now a CI check)
2. Forgetting table within bounds (lesson 100)
3. Serving eval on the *deployment artifact* (lesson 110's rule 3)
4. Canary rollout (Module 6), rollback on the pre-registered criteria

The gates are the same every time, which is the point: automation is what
makes the tenth fine-tune as trustworthy as the first.

## Maintenance economics, stated plainly

- **Base model upgrades invalidate everything downstream** — adapters
  retrain, evals re-run, quantization re-checks. Budget the re-run; pin
  versions deliberately (upgrade when there's a *reason*, not when a
  version number increments).
- **The adapter artifact is small; the eval infrastructure is the
  asset.** Models churn; the golden set, judges, and gates are the
  compounding investment — the same closing note Module 4 made about
  retrieval, and the same one Module 7 will make about evaluation
  generally.

## Module 5 recap

When (010) → what form (020) → LoRA mechanics (030–050) → data (060–070)
→ training (080–090) → costs (100) → proof (110) → preferences (120) →
deployment (130) → the loop itself (140). The through-line: fine-tuning
is a data-quality intervention wearing a GPU costume.

## Check yourself

1. Design the harvest: which three production signals feed your curation
   queue, and what filter keeps garbage out?
2. Why does "continuous" fine-tuning actually mean monthly-or-triggered
   for most teams? Name the two costs that set the cadence.
3. A base-model upgrade lands with strong benchmarks. List the four gates
   your fine-tuned artifacts must re-pass before it ships.

**Module 5 complete.** Next: [Module 6 — Production serving](../../06-production-serving/lessons/010-serving-is-a-platform.md)
