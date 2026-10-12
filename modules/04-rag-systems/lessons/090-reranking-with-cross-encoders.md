# Reranking with cross-encoders

**Reading time:** ~6 min · Module 4

Retrieval optimizes for searching a million chunks; reranking optimizes for
sorting fifty. Different problems, different architectures — and the
bi-encoder/cross-encoder split is one of those ideas that cleanly explains
why the pipeline looks the way it does.

## Bi-encoder vs cross-encoder

- **Bi-encoder (retrieval):** embed query and document *independently*,
  compare vectors. The interaction between query and document words never
  happens — each is compressed to one vector *before* comparison. Cheap at
  query time (document vectors precomputed), which is exactly what search
  over 10⁶ chunks requires.
- **Cross-encoder (reranking):** feed `query [SEP] document` through the
  model *together*, let attention match words against words, output one
  relevance score. Every token interacts with every other token — vastly
  more accurate. And vastly more expensive: **one forward pass per
  (query, document) pair**, so it cannot be precomputed and cannot index.
  It can only judge a shortlist.

## The two-stage pattern

```
retrieve (bi-encoder + BM25, fused)  →  top 50–100
rerank (cross-encoder)               →  top 5–10 to the generator
```

The math: 100 cross-encoder pairs at ~5–15ms each is 0.5–1.5s — must-have
if your SLO tolerates it, skippable if it doesn't (Module 3's latency
arithmetic decides). The payoff: the generator's context window is small
(lesson 100), so *precision of the top-5 matters more than recall of the
top-100*. Rerankers reliably buy 5–15 points of precision@5 over raw
retriever order — the last step before generation, where errors are
cheapest to fix.

## Reranker options, in cost order

1. **A dedicated cross-encoder** (e.g., bge-reranker-class models): fast,
   cheap, local, good. The default.
2. **A hosted rerank API** (Cohere Rerank and peers): zero ops, quality
   comparable, per-call cost, latency via network.
3. **The LLM itself as reranker:** pointwise ("rate relevance 0–10 for
   this chunk...") or listwise ("order these chunks for this query...").
   Most capable, most expensive — a Module 2 cost-arithmetic problem
   (50 chunks × full context = real money per query). Reserve for
   small shortlists or quality-critical paths.

## Caveats

- Reranking changes *which* chunks enter context, not what the generator
  does with them — evaluate end-to-end too (lesson 120's bisection), not
  just precision@5.
- Cross-encoders have their own context limits; a 900-token chunk plus
  query can overflow a 512-token reranker and truncate the evidence.
- Reranker and embedder are *independent* — you can swap either without
  re-embedding the index. Enjoy this; it's the only swap in the pipeline
  that's free.

## Check yourself

1. Why can't a cross-encoder be used for first-stage retrieval over 10M
   chunks — state it as a precompute argument.
2. Your p95 latency budget has 200ms spare. Retrieve-at-100 + local
   cross-encoder at 12ms/pair: does it fit, and what's the alternative
   if not?
3. Precision@5 improved 12 points but end-to-end answers didn't. Name the
   two most likely causes.

Next: [100 — Augmenting and citations](100-augmenting-and-citations.md)
