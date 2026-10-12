# The RAG pipeline

**Reading time:** ~6 min · Module 4

Every RAG system is the same six boxes in two phases. Knowing the map lets
you localize failures — "wrong answers" is not a debuggable symptom; "the
reranker is dropping the right chunk at stage 4" is.

## Indexing (offline, runs on your corpus)

```
load → chunk → embed → store
```

1. **Load:** pull documents from their systems of record (confluence,
   S3, DBs). Capture metadata now — source, timestamps, permissions —
   because it's unrecoverable later.
2. **Chunk:** split documents into retrieval-sized pieces (lesson 050).
   The single most underestimated design decision in the pipeline.
3. **Embed:** map each chunk to a vector (lesson 030/040). Deterministic
   per model version — change models, re-embed everything.
4. **Store:** vectors + text + metadata in a vector store (lesson 060).

## Serving (online, runs per query)

```
retrieve → (rerank) → augment → generate
```

1. **Retrieve:** embed the query, fetch top-k similar chunks. Hybrid with
   lexical search when exact terms matter (lessons 070–080).
2. **Rerank:** rescore the top candidates with a more expensive, more
   accurate model (lesson 090). Optional but common.
3. **Augment:** assemble the prompt — system + retrieved chunks (with
   source markers) + question (lesson 100). Your Module 2 skills run
   this step.
4. **Generate:** the LLM answers, ideally citing [1], [2]...

## Where the latency and cost go

Retrieval is milliseconds; embedding the query is single-digit
milliseconds; a cross-encoder rerank over 50 candidates is the first
nontrivial line item; generation dominates. A typical budget for a chat
product: retrieve 20ms + rerank 100ms + prefill/decode 1–3s. Module 3's
arithmetic applies to the generation term verbatim.

## The two failure families

- **Index-side:** stale content, chunking that destroys answer units,
  embedding/model skew between index and query time, permission drift.
  These fail *silently* — no error, just wrong retrieval.
- **Serving-side:** retrieval misses, rerank drops, prompt assembly
  buries the evidence, generation ignores or misquotes it. These are
  debuggable per-request with tracing (lesson 120's bisection).

The lesson that anchors debugging: **log every intermediate artifact** —
query, retrieved ids + scores, final prompt, citations. You cannot bisect
a pipeline you didn't instrument.

## Check yourself

1. A chunk is retrieved that *contains* the answer but the model ignores
   it. Which stage is broken — and which of the two failure families?
2. Why must chunking happen before embedding rather than after?
3. Your docs update hourly. Which boxes change, and which don't?

Next: [030 — Embeddings and cosine similarity](030-embeddings-and-cosine.md)
