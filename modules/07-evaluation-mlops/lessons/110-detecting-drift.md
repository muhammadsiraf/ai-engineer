# Detecting drift

**Reading time:** ~7 min · Module 7

Drift is the slow failure: nothing you shipped changed, and quality
moved anyway — traffic shifted, the corpus rotted, the provider swapped
a model, the world moved past your eval set. Drift detection is the
early-warning system; the challenge implements the standard numeric
tool (PSI) that powers it.

## The four drifts (name them to see them)

1. **Data/traffic drift:** users ask new questions (new product line,
   seasonality, a viral use case). The pipeline was built for
   yesterday's distribution.
2. **Concept drift:** the correct *answer* changes (policy updated,
   prices changed) while questions stay the same — the corpus/eval set
   is now wrong, not the pipeline.
3. **Model drift:** the artifact changed under you — provider silent
   updates, engine upgrades, your own fine-tune decay. Behavior shifts
   with no deploy.
4. **Index drift:** RAG-specific — corpus growth without re-chunking
   review, stale documents, orphaned deletions (Module 4 lesson 130's
   reconciliation failing quietly).

## The signal layer: distributions, not averages

Compare *distributions* of cheap observables between a reference window
(e.g., last month) and the current window:

- input length, output length, language mix, refusal rate
- retrieval scores, zero-hit rate, citation-verification failures
- judge scores by category, cost per request

**PSI (Population Stability Index)** — the challenge's function —
scores distribution shift per feature:

```
PSI = Σ_buckets (current% − reference%) × ln(current% / reference%)

buckets: 5–10 quantile bins of the reference window
reading: < 0.1 quiet · 0.1–0.25 investigate · > 0.25 alarm
```

It's one formula over two histograms — cheap enough to run on a dozen
features hourly, sensitive enough to catch the silent model swap the
latency average missed. (Handle empty buckets: clamp shares to a
small ε before the log — the challenge's edge case.)

## From signal to diagnosis

PSI says *which feature* shifted; the diagnosis walks the four drifts:
traffic mix (join with tenant/feature tags — a new customer, not a
model problem), concept (check the corpus changelog), model (replay
the golden set against the live endpoint — if golden-set scores held,
it's traffic; if they moved, it's the artifact), index (reconciliation
report). The replay is the discriminating experiment — keep it scripted.

## The response playbook

- **Traffic drift →** grow the golden set toward the new distribution
  (lesson 020's maintenance loop is a drift response), retrain/re-prompt
  if scores on the new slice sag.
- **Concept drift →** corpus update pipeline + eval set refresh; this
  is a content-ops bug with a quality symptom.
- **Model drift →** pin versions (lesson 120), canary revalidation,
  exercise the rollback.
- **Index drift →** fix reconciliation, alert on staleness age.

## Cadence

Daily automated PSI over the observable panel + weekly golden-set
replay (a few hundred cases through prod) + monthly set maintenance.
Drift work is gardening: cheap frequent checks, one honest weeding
session a month.

## Check yourself

1. PSI on input-length = 0.4, PSI on judge-groundedness = 0.05, golden
   replay unchanged. Diagnose in one sentence — which drift is it, and
   is quality at risk?
2. Why can "average latency" hide a provider model swap while PSI on
   output length catches it?
3. Your zero-hit retrieval rate crept 2%→8% over six weeks. Which
   drift is this, and which Module 4 checklist line failed?

Next: [120 — Versioning](120-versioning.md)
