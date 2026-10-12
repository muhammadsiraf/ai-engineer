# Production checklist

**Reading time:** ~6 min · Module 6

Twelve lessons of machinery, compressed to the list you actually run
before saying "yes, it can take traffic." Each line names its lesson;
each unchecked line is a known incident shape from production LLM
platforms.

## Capacity and performance

- [ ] Load-tested at 2x forecast peak with real request shapes; SLO
      pass/fail recorded per stage (030)
- [ ] Operating point chosen left of the knee; per-replica capacity C
      documented (120, 030)
- [ ] Replica math: floor covers night peak + cold-start gap; ceiling
      = budget guardrail with an alarm (050, 060)
- [ ] Cold start measured; readiness probe checks a real generation;
      warmup request in the boot path (060)

## Cost

- [ ] Cost per 1M tokens computed per tier, split input/output;
      utilization per fleet on a dashboard (090)
- [ ] Floor cost priced and owned by a name, not discovered by finance
      (090, 050)
- [ ] Output token caps set (the free money) (090)

## Reliability and rollouts

- [ ] SLOs defined (TTFT + end-to-end, plus a quality budget); burn-rate
      alerts wired to paging (040)
- [ ] Autoscaling on queue depth, not GPU meters; scale-in slowed (050)
- [ ] Draining + canary + pre-registered guardrails for every deployable
      artifact: engine, config, model, prompt template (110)
- [ ] Rollback path tested *this week* (110)

## Traffic and efficiency

- [ ] Prefix-aware routing keyed on the stable prefix; hit rate
      dashboarded; hot-shard plan exists (070)
- [ ] Prompt templates honor the stable/volatile discipline — the
      server-side dollar value (070, M2 L100)

## Artifact integrity

- [ ] Container pinned (driver/CUDA/engine/model-hash), CVE-scanned,
      CI smoke test does a real generation (080)
- [ ] Model provenance recorded: exact weights, quantization, eval
      results of the deployed artifact (080, M5 L110)

## Observability

- [ ] Four layers live: metrics, structured logs, traces, quality
      samples (120)
- [ ] Request id end-to-end; deploy annotations on the metric timeline
      (120)
- [ ] Alert list reviewed for pages that shouldn't page (120)

## The pre-launch ritual

Run one hour of shadow traffic (or the load test) the day before
launch, with the *whole* checklist above visible on one screen. The
goal is not perfection — it's knowing exactly which risks you're
carrying into launch, with each one named, priced, and owned. That
document is the difference between operating a platform and being
operated by one.

**Module 6 complete.** Next: [Module 7 — Evaluation & MLOps](../../07-evaluation-mlops/lessons/010-why-llm-eval-is-different.md)
