# Monitoring

**Reading time:** ~6 min · Module 7

Module 6 lesson 120 instrumented the serving system. This lesson adds
the dimension that layer cannot see: *quality in production*, over
time, as the traffic, corpus, prompts, and models drift. Monitoring is
the eval suite's cousin in prod — same rubrics and judges, sampled
continuously, wired to alerts.

## The quality telemetry loop

```
live traffic ──sample──▶ judge pipeline (rubric, lesson 050)
      │                       │
      │                       ▼
      └──▶ metrics store ◀── scores: groundedness, relevance, refusal rate
                     │
                     ▼
             dashboards + burn-style alerts (Module 6 lesson 040's shape)
```

- **Sample smartly:** uniform 1–5%, *plus* oversample interesting
  strata — errors, refusals, user thumbs-down, new-tenant traffic.
  Uniform sampling alone starves exactly the cases you need.
- **Judge in batch, alert on burn:** scores are noisy per-sample;
  aggregate to rolling windows and alert on *rate of change* (like
  lesson 040's burn rate), not absolute thresholds nobody calibrated.
- **Join with human signals:** thumbs-down, escalations, edits — the
  cheapest judge panel that exists. Every user correction is a labeled
  case arriving in real time (Module 5 lesson 140's harvest).

## What to watch, per layer

- **Model behavior:** refusal rate, answer length distribution,
  language mix, format-violation rate — cheap counters that move early
  when a model or prompt shifts under you (provider silently updates
  their endpoint? length distribution sees it in hours).
- **Retrieval health (RAG):** zero-hit rate, score distributions per
  stage, citation-verification failure rate (Module 4 lessons 110/120).
- **Agent health (preview of Module 8):** tool-call failure rate, step
  counts, loop/timeout rate.
- **Cost (lesson 090):** tokens/request percentiles, cost per outcome.

## Alerting discipline (sleep-preserving)

- Page on user-impact proxies only: quality-burn (rolling judge score
  −0.2 sustained), refusal spike (3x baseline), format-violation surge.
- Ticket on leading indicators: retrieval zero-hit creep, length-drift,
  cache-hit decay (Module 6 lesson 070).
- Every page links to a runbook that starts with lesson 100's traces —
  an alert you can't act on trains the on-call to ignore it.

## Dashboards that get used

One screen, four rows: SLO burn (Module 6), quality scores by category,
retrieval/agent health, cost. Annotated with deploy markers (lesson
120). Reviewed in a weekly ops review with one question: "what moved,
and do we know why?" The meeting is the feedback loop that turns
monitoring from wallpaper into practice.

## Check yourself

1. Your provider silently swaps the model behind the same API version.
   Which two of your metrics notice first, and why does avg latency
   miss it?
2. Design the oversampling: which strata get 10x sampling and why is
   uniform 1% insufficient for them?
3. A judge-score drop of 0.15 fires at 2am. Walk the runbook's first
   three steps (which artifact do you open first?).

Next: [090 — Cost monitoring](090-cost-monitoring.md)
