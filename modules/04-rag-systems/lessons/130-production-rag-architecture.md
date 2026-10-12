# Production RAG architecture

**Reading time:** ~7 min · Module 4

The notebook version of RAG is a weekend. The production version differs
in four dimensions — freshness, permissions, observability, and cost —
none of which change the six boxes (lesson 020) but all of which decide
whether the system survives contact with an organization. This closing
lesson is the checklist.

## Ingestion as a pipeline, not a script

- **Idempotent upserts:** every chunk keyed by a deterministic id
   `(doc_id, chunk_index, content_hash)` — re-running ingestion updates
   in place instead of duplicating. Content-hash ids make "unchanged doc,
   re-run everything" nearly free (skip on hash match).
- **Delete propagation:** when a source doc dies, its chunks must die —
  the #1 silent RAG hazard is the orphaned chunk of a deleted policy.
  Track source→chunk lineage; run a reconciliation job.
- **Versioned configs:** corpus snapshot + chunker params + embedding
  model = index version. Re-embedding migrations (lesson 040) build index
  N+1 in a new namespace and flip traffic — the same rollout discipline
  as Module 6's deployments.

## Serving path, instrumented end to end

```
query → embed → [dense ∥ BM25] → RRF → rerank → assemble → generate → verify citations
                    └────── log: ids, scores, stage timings, final prompt ──────┘
```

- **Cache layers:** exact-query response cache (Module 2 lesson 120) and —
  if prompts share a stable prefix — the engine's prefix cache (Module 3
  lesson 070). Retrieval + rerank is often 10–20% of latency; caching
  answers for repeated queries compounds.
- **Access control at retrieval:** metadata pre-filters (lesson 060's
  filter trap), never post-filtering, and the permission check belongs to
  the *ingestion side too* (stale permissions on indexed content are a
  data breach with extra steps).
- **Stage-level tracing:** query, retrieved ids + scores per stage, final
  context, answer, citations, per-stage latency. Lesson 120's bisection
  runs on this fuel; without it, debugging is archaeology.

## Observability that maps to the metrics

Dashboards, not vibes:

- **Retrieval health:** mean/rec-fraction of hits via logged click/relevant
  signals; score distributions per stage (a sudden rerank-score shift =
  drift or a config change).
- **Answer health:** groundedness judge sampled continuously (lesson 120's
  judge, on a percentage of live traffic), citation-verification failure
  rate, "not in sources" refusal rate (spikes = index problems).
- **Drift:** embedding-score distribution shift, corpus growth, query
  distribution shift (Module 7's PSI arrives here).
- **Cost per query:** embed + retrieve + rerank + generation tokens
  (Module 2 lesson 050 arithmetic), bucketed by query shape.

## The launch checklist

1. Golden set (queries + relevant chunk ids) versioned in the repo —
   retrieval metrics in CI on every pipeline change.
2. Deterministic ids + idempotent ingestion + reconciliation for deletes.
3. Index namespace per index version; documented re-embed migration runbook.
4. Pre-filter permissions, tested with an adversarial cross-tenant query.
5. Full trace logged per request; judge sampled; dashboards live.
6. Refusal path ("not in your sources") user-tested, not just implemented.
7. Cost per query measured, cached-path hit rate visible.

Module 5 will reuse this whole shape: the same eval discipline (golden
sets, judges, CI metrics) applies to fine-tuned models — and lesson 010's
knowledge/behavior line is exactly the boundary between this module and
the next.

## Check yourself

1. A deleted document still answers questions. Walk the failure: which
   mechanism was missing, and which two checklist lines catch it?
2. Where exactly does per-user permission checking live in the serving
   path, and what's wrong with checking permissions *after* generation?
3. Your cost per query doubled after adding a reranker. Name the three
   knobs that buy it back and what each costs in quality.

**Module 4 complete.** Next: [Module 5 — Fine-tuning](../../05-fine-tuning/lessons/010-when-to-fine-tune.md)
