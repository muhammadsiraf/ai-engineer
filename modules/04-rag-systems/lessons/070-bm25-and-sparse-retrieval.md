# BM25 and sparse retrieval

**Reading time:** ~7 min · Module 4

Dense retrieval was 30 years old when BM25 arrived and is still the lexical
baseline to beat — and the component your RAG stack probably shouldn't
ship without. This lesson builds the formula once (it's this module's
challenge), because every parameter has a *reason* you can defend.

## The scoring function

BM25 scores a document for a query by summing, over each query term:

```
score(q, d) = Σ_t  idf(t) ×  tf(t,d) × (k1 + 1)
                        ─────────────────────────────────────
                        tf(t,d) + k1 × (1 − b + b × |d|/avgdl)

idf(t) = ln( (N − df + 0.5) / (df + 0.5) + 1 )
```

Three ideas, each doing one job:

1. **IDF** — terms in few documents are worth more. "Kubernetes" localizes;
   "the" doesn't. (The `+1` inside the log keeps IDF positive even when a
   term appears in every document.)
2. **TF saturation (k1, ~1.2–2.0):** the 2nd occurrence of a term adds
   evidence; the 20th adds almost none. Old TF-IDF grew linearly and let
   keyword-stuffed pages win; BM25's diminishing returns are the fix.
3. **Length normalization (b, ~0.75):** longer documents have more chances
   to contain any term. `b` discounts long docs; `b=0` disables, `b=1`
   fully normalizes.

## Why you still need it in 2026

Embeddings blur exact tokens — that's their strength (synonyms work) and
their failure mode:

- **Identifiers:** error codes (`ERR_0x4512`), part numbers, CVE ids,
  function names. The one doc with that token is the answer; cosine ranks
  it mid-pack among "similar-looking" docs.
- **Rare names and jargon** the embedder saw too little of.
- **Negations and precision:** "without telemetry" vs "with telemetry" can
  embed near-identically. Exact match doesn't confuse them.
- **Zero-training robustness:** BM25 has no model to be wrong about your
  domain. It's the baseline any dense system must beat *on your golden
  set* — sometimes it doesn't.

Weakness, symmetrically: **vocabulary mismatch.** Query "car", document
"automobile" — perfect BM25 score of zero. Dense retrieval is exactly the
medicine for this, which is why they combine (lesson 080), not compete.

## Mechanically

An inverted index maps term → list of (doc, tf), making scoring cost
proportional to query length, not corpus size. You'll never implement the
index in production (every search library ships BM25), but the challenge
builds the *scorer* over a tiny corpus so saturation, IDF, and length
normalization are things you've computed, not just quoted.

## Check yourself

1. A doc repeats the query term 40 times; another uses it twice and has
   equal length. Why doesn't the first win 20x — and which parameter
   encodes that?
2. You set b=0 by accident. What query/doc pair changes rank, and in which
   direction?
3. Give two query types where you'd trust BM25 over your dense retriever,
   and the one property of embeddings that causes both.

Next: [080 — Hybrid retrieval and RRF](080-hybrid-retrieval-and-rrf.md)
