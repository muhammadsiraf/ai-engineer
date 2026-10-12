# LLM-as-judge

**Reading time:** ~7 min · Module 7

The judge is a model scoring another model's work against your rubric.
It's the only evaluation that scales to open-ended generation, and it's
also a model — with biases, drift, and failure modes you must engineer
around. This lesson is the judge's operating manual; the challenge
implements its two canonical defenses (position-bias debiasing and
confidence bounds on the resulting win rates).

## The judge prompt, dissected

```
[role]      You are evaluating support-bot answers for groundedness.
[rubric]    Score 1–3. 1 = contradicted by context; 2 = partially
            supported; 3 = every claim traceable to the context.
            (Define each level with an example — scales need anchors.)
[evidence]  <context> ... </context>
[question]  ...
[answer]    ...
[procedure] Quote the supporting context for each claim, THEN score.
[output]    JSON: {"score": int, "evidence": [...]}
```

The two highest-leverage prompt choices: **few, anchored levels**
(binary or 1–3 — judges can't hold 10 levels calibrated) and
**evidence-first procedure** (forcing quotes before the verdict
measurably improves consistency — and gives you an auditable trail).

## The bias catalog (and the defenses)

- **Position bias:** in pairwise comparison, judges favor the first
  (sometimes last) option. *Defense: run both orders, count a win only
  when it wins both (or aggregate with order-swapped pairs — the
  challenge implements exactly this).*
- **Verbosity bias:** longer answers score higher at equal quality.
  *Defense: rubric explicitly penalizes unsupported padding; pairwise
  where possible.*
- **Self-preference:** models rate their own outputs higher (style
  overlap reads as quality). *Defense: judge family ≠ evaluated family;
  rotate judges.*
- **Rubric drift/misreading:** the judge interprets "grounded"
  differently than you do. *Defense: calibration set (below).*

## Validation: the judge must pass an eval too

Take 50–100 cases, human-label them, run the judge: report **agreement
with humans** (and Cohen's kappa, not raw % — chance agreement
inflates). Below ~80% agreement / kappa < 0.6: fix the rubric, shrink
the scale, or add few-shot anchors — do not ship the judge. Re-validate
when the judge model changes (it's a dependency with a version).

## Protocols: pointwise, pairwise, listwise

- **Pointwise** (score one answer): cheapest, composes with dashboards;
  absolute-scale noise is the weakness.
- **Pairwise** (which is better, A or B?): more reliable per call —
  comparative judgments are what LLMs do best; feeds win-rate
  statistics (the challenge's confidence bound: with n comparisons and
  win rate p, the 95% interval is roughly p ± 1.96·√(p(1−p)/n) — small
  n means wide bands, which is the honest way to say "we can't tell
  yet").
- **Listwise** (rank k answers): most context per call, most
  position-bias-prone; use for reranking (Module 4 lesson 090), not
  scoring.

## Cost engineering

A judge call is a full model call over your answer *plus* context —
at scale it can rival the product's own inference bill. Controls:
sample (1–5% of traffic), cascade (cheap judge first, expensive judge
only on disagreement/borderline), cache (same answer+context+rubric
version → same result), and batch small checks into one call.

## Check yourself

1. Your pairwise judge picks option A 65% of the time when A is first,
   45% when A is second. What's A's debiased win rate, and what would
   the naive protocol have reported?
2. Why is percent-agreement with humans a weak validation metric, and
   what does kappa add?
3. Design the cascade: which checks go to the cheap judge, which to the
   expensive one, and what triggers escalation?

Next: [060 — A/B-testing](060-ab-testing.md)
