# A/B-testing

**Reading time:** ~6 min · Module 7

The A/B test is the arbiter between two candidate systems on *real*
users. Online, it captures what no offline eval can: behavior. But LLM
A/B tests have unusual variance (long-tail outputs, quality judgments),
and the statistics have teeth — the challenge computes the win-rate
confidence bounds that decide when a result is real.

## The design, LLM-flavored

- **Unit = conversation/request,** randomly assigned; variants: control
  (incumbent) vs treatment (new prompt/model/retrieval config). Module
  6 lesson 110's canary IS the deployment mechanism; the A/B test is
  the measurement plan riding on it.
- **Metric hierarchy, pre-registered:** one primary metric (resolution
  rate, task completion, engagement) + a few guardrails (latency SLO,
  cost/request, safety flags). Deciding post-hoc which of 30 metrics
  "won" is how teams lie to themselves with real data.
- **Sample size before you start:** for a proportion metric going from
  50% → 55%, you need roughly ~1,600 per arm for 80% power at α=0.05 —
  most teams' "we ran it for a day" tests are underpowered noise
  generators. The challenge's confidence-bound math is the intuition
  pump: small n → wide bands → no decision.

## The LLM-specific wrinkles

1. **Quality is judged, not just measured:** pair the behavioral metric
   with judge-scored samples (lesson 050) — engagement can rise because
   the model got more sycophantic; only the judge sees it.
2. **Interference:** conversations share context across requests (a
   user experiences both variants in one thread if assignment is
   per-request). Assign per *user/session*, consistently.
3. **Cost asymmetry:** the treatment may cost 2x per request; report
   cost-per-outcome, not outcome alone (lesson 090's arithmetic, now
   with error bars).
4. **Novelty and primacy effects:** early interactions with a new
   variant aren't representative; run long enough for the curve to
   flatten, or exclude a warm-up window.

## Sequential testing and peeking

Checking "did we win yet?" every hour and stopping at the first p<0.05
inflates false positives ~3–5x. Either fix the horizon in advance, or
use a sequential test (mSPRT-style, always-valid intervals) designed
for peeking. The engineering version: the challenge's confidence bound
is what your dashboard should show *while* the test runs — wide and
honest, narrowing in real time.

## When NOT to A/B

- Too little traffic for power (do an offline judge-off on the golden
  set instead, and ship behind a flag).
- The change is a fix for something broken — you don't A/B a crash fix.
- One variant is strictly dominated (worse on every guardrail): ship
  the other, don't burn weeks proving it.

## Check yourself

1. Your primary metric is 14-day retention; the PM wants results in 3
   days. What do you tell them, concretely, using sample-size logic?
2. Why must assignment be per-session for a chat product? Describe the
   corrupted measurement if it isn't.
3. Treatment wins engagement +3% but the judge's groundedness score
   drops 0.4. What happened, and which pre-registered artifact resolves
   the dispute?

Next: [070 — Regression tests for prompts](070-regression-tests-for-prompts.md)
