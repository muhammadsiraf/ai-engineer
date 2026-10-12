# Building an eval set

**Reading time:** ~7 min · Module 7

The eval set is the asset that appreciates. Models churn, prompts churn,
frameworks churn — the set of tasks with known-good judgments is what
makes every churn decision cheap and safe. This lesson is the
construction manual; the course has referenced it five times already.

## Anatomy: the case record

Each case is more than a prompt:

```
{
  "id": "support-0417",
  "category": "billing-refund",        # per-category reporting lives here
  "input": {...},                      # the full request (messages, tools, context)
  "expected": {...} | null,            # exact answer if one exists
  "rubric": "...",                     # what "good" means, when no exact answer
  "must_include": ["30 days"],         # hard content requirements
  "must_not": ["apologize", "invent policy"],
  "source": "prod-incident-8841",      # provenance — cases have biographies
  "version": 3
}
```

Categories are load-bearing: aggregate scores hide tail failures
(every prior module's warning), and per-category breakdowns are what
turn "quality dropped" into "Chinese-language extraction dropped."

## Sourcing: where cases come from, ranked

1. **Production failures** — every incident, escalation, and user
   correction becomes a case (the highest-value data that exists;
   Module 5 lesson 140's harvest, viewed from the eval side).
2. **Real traffic sampling** — stratified by category; keeps the
   distribution honest.
3. **Stakeholder interviews** — the cases support/sales/legal worries
   about, before they happen ("what if the user asks about refunds for
   gift cards?").
4. **Synthetic generation** — fine for volume and edge-case coverage,
   but always paired with a real-traffic slice so the distribution
   isn't the generator's imagination of your users.

## The statistical honesty rules

- **Size:** ~50 cases per category for coarse signal, 200+ for
  regression gates you'll actually trust (the challenge puts confidence
  bounds under a win rate; the same math says why 10 cases is
  decoration). Coverage beats size: 30 weird cases > 300 easy ones.
- **Split discipline:** cases the model could have memorized (public
  docs, its own outputs) are *leaky*. Keep a private rotating slice —
  public benchmarks leak into training data; your golden set must not
  leak into your prompts.
- **Version the set:** cases get corrected, added, retired. Every eval
  result records the set version it ran against; a score without its
  set version is uninterpretable (lesson 120).
- **Label the labels:** for judged sets, measure inter-judge agreement
  (human-human first) — disagreement above ~20% means the rubric, not
  the model, is the problem.

## The maintenance loop

Eval sets rot: they encode yesterday's product (retired policies,
renamed features) and yesterday's failure modes (once fixed, the case
trains your attention elsewhere). Quarterly: prune obsolete, add the
quarter's failures, re-validate a random sample against current
ground truth. The set is a garden, not a monument.

## Check yourself

1. Your boss wants "a 1000-case eval set by Friday." What do you push
   back with, and what do you propose instead?
2. Why is `must_not: ["invent policy"]` often more valuable than
   `expected: {...}` for support bots?
3. Your per-category scores moved after you *added* cases to one
   category. What actually happened, and which field in the case record
   makes it debuggable?

Next: [030 — Perplexity and reference metrics](030-perplexity-and-reference-metrics.md)
