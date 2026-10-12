# Vector stores and ANN

**Reading time:** ~7 min · Module 4

The vector store is the least intellectually mysterious component — it's a
database with one special power, approximate nearest-neighbor search — but
it has failure modes that are invisible until you measure. This lesson is
about knowing what you're configuring.

## Brute force first

Exact search = cosine of the query against every vector. At 10k chunks
× 768 dims that's single-digit milliseconds — **do not reach for
sophistication below ~100k vectors.** The lesson's challenge ranking is
brute force; so is the right first version of most systems. The point of
ANN is a speed/recall trade you only need at scale.

## The ANN tradeoff

Exact search returns the true top-k. ANN returns *probably*-top-k, faster.
Everything about vector indexes is this dial:

- **Graph methods (HNSW, the default everywhere):** build a multi-layer
  proximity graph; search greedily from a sparse top layer downward.
  Knobs: `M` (links per node), `ef_construction` (build-time effort),
  `ef_search` (query-time effort — your runtime recall/speed dial).
- **Quantization/compression (IVF-PQ etc.):** cluster vectors, store
  compressed codes, search centroids then refine. Cheaper memory, lower
  recall per compute; common for 100M+ vectors where HNSW graphs stop
  fitting RAM.

Measure the trade as **recall@k vs latency vs RAM** against your exact
brute-force baseline on *your* data — the numbers vary wildly by
dimensionality and cluster structure.

## The filter trap (the one that bites everyone)

"Retrieve top-10 among docs this user can see." Two implementations:

- **Post-filter:** fetch ANN top-10, then drop the ones without permission.
  Broken: you might keep 2 of 10, silently. Recall loss is invisible —
  the system never knows what it discarded.
- **Pre-filter:** constrain the search to permitted vectors, *then* take
  top-10. Correct, but requires the index to support filtered ANN (all
  serious stores do, with varying quality at highly selective filters).

Rule: **filters that can eliminate most of the corpus must be pre-filters.**
The same logic covers tenant separation, language, and date ranges.

## Operations you must plan for

- **Upsert/delete by id** — docs change; tombstones and idempotent
  ingestion (lesson 130).
- **Namespaces/collections** — per-tenant or per-version isolation; a
  re-embedding migration runs in a new namespace and flips traffic.
- **Persistence and backup** — the index is rebuildable from source + the
  embedding config; treat "rebuild procedure" as part of the system, since
  it's your only recovery from a bad migration.

## Check yourself

1. Why is ef_search a *runtime* knob while M and ef_construction are
   build-time decisions?
2. A compliance requirement says "users must never see other tenants'
   content even in an error path." Post-filter or pre-filter, and why is
   the answer about correctness rather than recall?
3. Your 1M-vector index answers in 8ms at 0.99 recall@10 with brute force
   45ms. The new PM wants 50M vectors. What breaks first — memory or
   latency — and which index family addresses it?

Next: [070 — BM25 and sparse retrieval](070-bm25-and-sparse-retrieval.md)
