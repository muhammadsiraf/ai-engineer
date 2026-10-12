# Embeddings and cosine similarity

**Reading time:** ~7 min · Module 4

Module 1 lesson 020 introduced embeddings as the model's semantic coordinate
system. This lesson makes the geometry operational, because retrieval *is*
geometry: your entire system runs on one operation, repeated billions of
times.

## The operation

An embedding maps text to a fixed-length vector where semantic closeness
becomes geometric closeness. The standard closeness measure is **cosine
similarity** — the cosine of the angle between vectors, independent of
their lengths:

```
cos(a, b) = (a · b) / (||a|| × ||b||)        range: [−1, 1]
```

- 1 → same direction (semantically identical)
- 0 → orthogonal (unrelated — in practice, unrelated texts score ~0.1–0.3,
  not 0: embeddings live in a narrow cone, the "anisotropy" quirk)
- −1 → opposite (rarely meaningful for text)

Length-invariance is the point: a 3-word query and a 300-word document can
still point the same direction. (Modern embedding models output
unit-normalized vectors, which reduces cosine to a plain dot product — same
ranking, cheaper. Similarity functions differ only when norms vary.)

## The challenge you'll implement

`rank_by_cosine`: given a query vector and document vectors, produce the
documents sorted by similarity. It's ~10 lines, and implementing it once
means you'll never again treat the retriever as a magic box — every
"why did this rank below that" question is now answerable by printing two
vectors.

## Similarity is not relevance — the key caveat

Cosine measures *semantic relatedness*, and relatedness is not the same as
answering-the-question:

- Query "how do I rotate API keys" vs doc "API keys are rotated quarterly"
  → high similarity, wrong document (procedure ≠ policy).
- Query "ERR_0x4512" vs any doc → *low* similarity with everything, but the
  one doc containing that exact token is the right answer. Dense retrieval
  blurs exact identifiers — this is precisely the hole lexical search fills
  (lesson 070), and why hybrid systems exist (lesson 080).

This is the conceptual justification for every precision mechanism later in
the module: rerankers, hybrid fusion, and evaluation all exist because
nearest-neighbor-in-embedding-space is a good first guess, not the answer.

## The properties worth internalizing

1. **Symmetric but not inherently aligned.** cos(q, d) = cos(d, q); whether
   a query and a document "match" is a property the model was *trained*
   for (lesson 040's query/passage prefixes).
2. **Relative, not absolute.** A 0.42 score means nothing alone; scores are
   only meaningful within one query's candidate pool (never ship "score >
   0.8" as a semantic threshold across queries).
3. **Monotonic in rank, meaningless in magnitude.** Downstream systems
   should consume *ranks* (or recalibrated scores), not raw similarities.

## Check yourself

1. Why does unit-normalizing vectors make cosine and dot product
   interchangeable, and which one do you pick for a 100M-vector index?
2. Your threshold "drop chunks below cosine 0.75" works for English
   queries and fails for German ones. What property of similarity scores
   does this violate?
3. Give a concrete query/document pair where high cosine similarity means
   the document is the *wrong* answer.

Next: [040 — Picking an embedding model](040-picking-an-embedding-model.md)
