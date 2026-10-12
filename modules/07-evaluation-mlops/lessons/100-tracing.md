# Tracing

**Reading time:** ~6 min · Module 7

Metrics say the system is slow; logs say a request failed; neither says
*why*. Tracing records one request's journey through every stage —
retrieve, rerank, prompt-assembly, generation, tool calls, judge calls —
as a tree of spans with timings, inputs/outputs, and versions. It's the
artifact every debugging story in this course actually used.

## The anatomy of an LLM trace

```
trace: req_8841  (user=session_12, versions: template=v7, model=gpt-x, retriever=v3)
├── span: embed_query                     11ms
├── span: retrieve_dense                  18ms   → 50 ids, scores
├── span: retrieve_bm25                    6ms   → 50 ids, scores
├── span: rrf_fuse                        <1ms   → 50 fused
├── span: rerank                         140ms   → top 5
├── span: assemble_prompt                 2ms    → 3,812 tokens
├── span: generate                     2,140ms   → 412 tok out, TTFT 480ms
│     └── (engine-side: queue 90ms, prefill 390ms, decode 1,660ms)
└── span: verify_citations                95ms   → 4/4 verified
```

Reading it top-down answers "where did 2.4 seconds go" in ten seconds —
and it's the *only* artifact that answers it for one user's request,
which is the request support actually escalates.

## What must be on every span

- **Identity:** trace id, request id, session id (Module 6 lesson 120's
  correlation rule).
- **Versions:** model, prompt template, retriever config, engine — the
  span must be reproducible from its metadata.
- **The I/O (with retention care):** inputs and outputs per stage,
  sampled or truncated — this is what makes Module 4 lesson 120's
  bisection possible on real traffic.
- **Cost:** tokens in/out per span (lesson 090's per-stage attribution
  falls out for free).

## The debugging patterns traces enable

- **The bisection:** quality complaint → pull the trace → was the right
  chunk retrieved? → was it in the final prompt? → did the model use
  it? Three questions, three spans, one answer (Module 4 lesson 120).
- **The latency decomposition:** per Module 3 lesson 120 — queue vs
  prefill vs decode, per request, per stage; aggregate into the p95
  waterfall the whole team shares.
- **The cost waterfall:** which stage owns the bill (reranker? judge?
  the 8k-token system prompt?).
- **The replay:** traces are executable records — replay a failing
  trace against a candidate fix with the same inputs. This is what
  turns "I think the new prompt fixes it" into a measured claim
  (lesson 070's regression suite, seeded from real traces).

## The engineering basics

Standard protocols exist (OpenTelemetry + LLM-gen-ai conventions; the
provider SDKs and engines emit spans natively) — adopt one, don't
invent. Sample high-volume low-value traces (successes at 5–10%,
keep errors and slow requests at 100%). Retention: full payloads for
days, metadata for months (Module 6 lesson 120's tiering). Redact
secrets at span creation, not at export.

## Check yourself

1. Reconstruct the bisection: which three spans answer "retrieval or
   generation?" and what exactly do you compare in each?
2. A trace shows TTFT 480ms with 90ms queue. Compute the prefill rate
   in tokens/s if the prompt was 3,812 tokens — and name what you'd
   check if it's far below your calibration (Module 3 lesson 020).
3. Why are traces the raw material for the regression suite, and what
   does the replay need to be faithful?

Next: [110 — Detecting drift](110-detecting-drift.md)
