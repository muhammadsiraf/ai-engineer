# Zero-downtime rollouts

**Reading time:** ~7 min · Module 6

Every deploy in this module's stack — engine upgrade, config change,
fine-tuned model (Module 5), new prompt template — is an experiment
running against your error budget (lesson 040). The rollout discipline
makes experiments cheap to run and cheap to undo: drain, canary,
compare, promote or roll back. The distinctive GPU problem: replicas
hold *state* (KV caches, in-flight generations), so "just restart" is a
user-visible event.

## Draining: the zero-downtime baseline

Swap a replica without dropping requests:

1. Mark the replica **not-ready** (load balancer stops *new* requests;
   the prefix-cache shards re-home per lesson 070's hashing).
2. **Drain in-flight** work: streams finish (with a cap — a 10-minute
   generation gets a kill signal and the client retries; that's a
   timeout policy, lesson 040).
3. Terminate, replace with the new version, gate on *engine-level*
   readiness (lesson 060's probe), and pre-warm (cold start is not a
   rollout excuse).

Rolling through 20 replicas at 1 minute of drain each is 20+ minutes —
which is why rollouts and warm pools and max-surge settings are one
design, not three.

## Canary: the experiment frame

Route a small slice of live traffic to the new version (5% → 25% → 100%),
with the comparison pre-registered:

- **What to compare:** SLO metrics (p95 TTFT, p95 end-to-end), error
  rate, and for model changes the *quality* signal — sampled judge
  scores (Module 4 lesson 120) or a fixed prompt-battery run against
  both versions. Latency-only canaries ship quality regressions.
- **Guardrails, written before the deploy:** rollback triggers ("p95
  TTFT +15% for 10 min", "error rate > 1%", "judge score −0.2"). If
  you're deciding mid-incident whether 12% is bad, the guardrail
  already failed.
- **Statistical honesty:** at 5% traffic for 30 minutes you may have a
  few thousand samples — enough for latency percentiles, not for 1%
  quality deltas. Widen traffic or time before believing small numbers
  (Module 7's significance machinery, previewed).

## What makes model rollouts different from code rollouts

- **No semantic versioning of behavior:** "v2 of the fine-tune" can be
  subtly worse on the tail (Module 5 lessons 100/110) — quality canaries
  are not optional.
- **Stateful caches invalidate:** prefix caches start cold on new
  replicas (hit rate dips for minutes — lesson 070's expected dip;
  announce it, don't alert on it).
- **A/B on prompts is also a rollout:** template changes ride the same
  canary machinery with response-cache considerations (Module 2 lesson
  120) — the cache must key on the template version or you serve
  stale-mixed results.

## Rollback: the feature you build first

Rollback = flip traffic weights back to the previous version — *kept
deployed* for the rollout window. Rolling forward from a bad model
deploy takes a retrain; rolling back takes 30 seconds. The retrospective
question after every rollback: why didn't the pre-deploy tests catch
this? → the answer becomes a new gate (lesson 030 CI load test, lesson
080 smoke test, Module 7's regression suite).

## Check yourself

1. During a rolling deploy your p95 TTFT spikes for 4 minutes then
   recovers. Give the two mechanisms (cold starts and cache), and the
   pre-warming change that flattens the spike.
2. Your canary shows +0.5% latency, −0.1% judge score at 5% traffic.
   Which guardrail decides, and why might the judge number be noise?
3. Why must the response cache key include the prompt-template version
   during a template rollout?

Next: [120 — Observability](120-observability.md)
