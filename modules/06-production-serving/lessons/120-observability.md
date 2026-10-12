# Observability

**Reading time:** ~7 min · Module 6

Every debugging story in this course ended the same way: *look at the
logged intermediates.* Observability is the discipline of producing
those intermediates on purpose — metrics for the health of the system,
structured logs for the life of each request, traces for the journey
across stages, and eval samples for the quality dimension none of the
other three can see.

## The four layers, and what each answers

1. **Metrics (aggregated, cheap, alertable):** RPS, p50/p95/p99 TTFT and
   end-to-end, tokens in/out, queue depth, KV-cache utilization, GPU
   memory, prefix-cache hit rate, per-replica throughput. Answers: *is
   the system healthy?* (lesson 040's SLO burn lives here).
2. **Structured request logs:** per request — ids, model version, prompt
   template version, token counts, sampled timings, cost, and (with
   retention care) the prompt/response themselves. Answers: *what
   exactly happened to THIS request?* Module 4 lesson 120's bisection
   runs on these.
3. **Traces:** the request's path across stages — gateway → retrieve →
   rerank → generate, or client → your API → provider. Answers: *where
   did the 4 seconds go?* Span timings per stage make Module 3's
   latency decomposition (queue vs prefill vs decode) visible per
   request, not just in aggregate.
4. **Quality samples:** a percentage of answers through the judge
   (groundedness, M4 L120), citation verification results, user
   feedback joins. Answers: *is the system right?* — the dimension
   metrics/logs/traces are structurally blind to.

## Instrumenting the GPU path specifically

- **Engine metrics first:** vLLM-class engines export the numbers Module
  3 taught you to care about — batch occupancy, cache hit rate, preemption
  counts, per-phase latency. Scrape them; they're the difference between
  "slow" and "preempting 40% of sequences."
- **Correlate:** one request id from client to response, stamped on
  every log line, span, and metric label where possible. The debugging
  superpower is joining layers: this slow request (trace) had cache
  miss (metric) because of the routing change (deploy annotation).
- **Annotate deploys:** version markers on the metric timeline. Half of
  all "what changed?" mysteries resolve to a deploy that nobody put on
  the graph.

## Alerts that respect sleep

- **Page on user impact:** SLO burn rate (lesson 040), error rate,
  queue-depth saturation. Symptom-based, thresholded on burn speed.
- **Ticket on leading indicators:** KV-cache pressure trend, disk on
  the weight store, hit-rate decay — investigate by day.
- **Never page on** raw GPU utilization (lies, lesson 050) or single
  slow requests (tails happen).

## The retention economics

Full prompt/response logs are big and sensitive. Tiered retention:
metrics for a year, traces for weeks, full payloads for days (sampled
beyond), quality samples and eval artifacts *forever* (they're the
golden set's breeding ground — Module 7 lesson 020). Redaction at
ingestion for anything regulated; access to payloads is a permission
model, not a norm.

## Check yourself

1. p95 TTFT degraded 30% with no error-rate change. Walk the four
   layers: what does each tell you, in what order do you look?
2. Why is "GPU utilization 95%" on a dashboard an anti-pattern, and
   which two metrics replace it?
3. Design the quality-sampling scheme: what fraction, what rubric,
   where do results go, and what does a regression trigger?

Next: [130 — Production checklist](130-production-checklist.md)
