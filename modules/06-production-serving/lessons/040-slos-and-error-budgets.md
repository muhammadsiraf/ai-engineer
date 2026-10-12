# SLOs and error budgets

**Reading time:** ~7 min · Module 6

An SLO is a promise about a *distribution*, not a vibe. "Fast and
reliable" becomes "p95 end-to-end ≤ 8s for 99% of requests over 28
days." Error budgets turn that promise into a decision machine: the
remaining budget tells you whether to ship features or freeze and fix.
This lesson makes the numbers precise — the challenge computes them.

## The SLI → SLO chain

- **SLI (indicator):** a measured quantity per request — latency, success
  (non-5xx), quality-for-LLMs (groundedness sample, Module 4 lesson 120).
- **SLO (objective):** a threshold over a window — "99% of requests < 8s
  over 28 days."
- **SLA (agreement):** the SLO with consequences (credits, contracts).
  Internal SLOs need no lawyers, which is what makes them useful.

For LLM serving, split the SLO by phase — Module 3 taught you why: TTFT
(interactivity, prefill+queue) and throughput-per-request (total time,
decode) fail for different reasons. A single "8s" hides which.

## Error budgets: the actual machinery

Budget = (1 − SLO) × total requests. At 99% over a million requests:
10,000 "bad" requests allowed per window — where *bad* means violating
the threshold (slow OR failed). Track **budget burn**:

```
remaining_budget = 1 − (violations_so_far / allowed_violations)
```

Reading the gauge:

- **Remaining > 50%:** healthy; ship features, take calculated risks.
- **25–50%:** tighten — freeze risky rollouts, investigate top burn
  causes.
- **< 25%:** the budget is the boss: reliability work outranks features,
  canary everything, consider degradation modes (smaller model tier,
  shorter outputs) rather than breach.

Burn *rate* (budget consumed per hour vs the steady-state allowance)
turns this into alerting: "burning 14x budget speed" pages someone;
"60% remaining" doesn't until it's burning fast.

## Why budgets beat uptime dashboards

Uptime % is backwards-looking and averages away bursts. The budget
frames every deploy, config change, and marketing campaign (traffic!) as
a spend from a fixed account — which is exactly what they are. It also
resolves the classic product/eng argument with arithmetic instead of
seniority: "can we ship Friday?" → "we have 34% budget left and the
change is canaried — yes."

## LLM-specific budget items

- **Timeout policy is part of the SLO:** a request your gateway kills at
  30s counts against budget — the budget prices your tail, so shrinking
  the tail (Module 3) is budget work.
- **Quality SLOs burn differently:** sample 1% of answers through the
  groundedness judge; a model regression burns the *quality* budget even
  while latencies look perfect. Keep the budgets separate; a fast wrong
  answer shouldn't spend the latency budget.

## Check yourself

1. SLO 99.5% over 28 days; 2M requests served; 14,000 violations.
   Compute remaining budget — and name the action per the thresholds.
2. Why two SLOs (TTFT, end-to-end) instead of one, in Module 3 terms?
3. Your burn-rate alert fires at 3am for the quality budget, not latency.
   What class of incident is this, and why would a latency-only
   dashboard have missed it entirely?

Next: [050 — Autoscaling](050-autoscaling.md)
