# Cost monitoring

**Reading time:** ~6 min · Module 7

Module 6 lesson 090 computed cost per token; this lesson makes it a
*monitored, allocated, alerted* quantity — because LLM costs fail
differently from compute costs: they scale with usage you don't fully
control (user creativity, loops, retries) and drift with pricing and
model swaps you didn't schedule.

## The instrumented cost model

Per request, accumulate: input tokens × price, output tokens × price,
cache-discount deltas (Module 2 lesson 120), reranker/judge calls,
tool-call round trips (each is a full prompt!), retries (Module 2
lesson 130). Emit as a metric per request alongside latency — cost is
a first-class observability dimension, not a monthly invoice
postmortem.

```
cost = Σ_stages  tokens_in×p_in + tokens_out×p_out   −   cache_credits
```

Tag every cost metric with: feature, tenant, model version, prompt
template version. Allocation questions ("what does the copilot feature
cost?") are tag queries, not archaeology.

## The monitoring surfaces

- **Unit economics:** cost per request, per resolved ticket, per
  1M tokens — trended. Module 6's formula, now with deploy annotations
  (a "cost regression" can be a template change, not infra).
- **Distribution, not average:** p95 tokens-per-request is the number
  that writes the invoice; one user pasting a 50k-token PDF moves means
  invisibly but percentiles visibly.
- **Anomaly alerts:** cost-rate burn (like lesson 040's budgets: daily
  spend vs expectation), per-tenant spikes (the runaway retry loop),
  output-length drift (a prompt edit making the model chatty is a cost
  bug).

## The classic cost incidents

1. **The retry storm:** provider errors + Module 2's backoff = 5x bill
   during an outage (each retry re-pays input tokens — idempotency and
   caps are the fix).
2. **The agent loop:** a tool result that never satisfies the model →
   50-step conversations (Module 8's step budgets are cost controls).
3. **The context bloat:** conversation history grows unbounded (Module
   2 lesson 060's summarization is a cost feature).
4. **The silent repricing:** provider price change or silent model swap
   — unit-economics trend catches it; the invoice confirms it, late.

## Budgets as guardrails

Hard ceilings per tenant/feature (reject or degrade when exceeded —
Module 6 lesson 050's multi-tier degradation is also a cost tool), and
a monthly review with one slide: unit economics by feature, top 3
cost movers, and the optimization backlog ranked by $saved/effort
(output caps, cache-hit improvement, distillation — Module 5's
economics argument, quantified).

## Check yourself

1. Daily spend tripled with flat traffic. Name the four suspects and
   the tag query that discriminates them.
2. Why is p95 tokens-per-request the alerting metric rather than mean
   cost per request?
3. Your judge pipeline costs 30% of serving. Walk the three controls
   from lesson 050's cost engineering and what each buys back.

Next: [100 — Tracing](100-tracing.md)
