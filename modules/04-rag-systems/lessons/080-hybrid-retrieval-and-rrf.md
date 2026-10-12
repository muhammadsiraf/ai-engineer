# Hybrid retrieval and RRF

**Reading time:** ~6 min · Module 4

Lesson 070/030 gave you two retrievers with *disjoint* failure modes:
dense handles paraphrase and misses exact tokens; BM25 handles exact
tokens and misses paraphrase. Hybrid retrieval runs both and merges. The
merge has one genuinely tricky part — the two systems' scores are not
comparable — and one standard fix you'll implement: Reciprocal Rank Fusion.

## The scales problem

Dense cosine says 0.82; BM25 says 14.7. Neither number means anything in
the other's units, and the scales aren't even stable across *queries*
(lesson 030: raw similarity is only meaningful within one query's pool).
Normalizing scores (min-max per query) is possible but fragile: score
distributions shift, one outlier rescales everything, and the "right"
relative weighting is another hyperparameter you must tune.

## RRF: fuse ranks, not scores

Reciprocal Rank Fusion sidesteps scales entirely by using only *ranks*.
For each document d and each ranking list R:

```
RRF(d) = Σ_R  1 / (k + rank_R(d))          rank is 1-based; absent → 0
```

with k ≈ 60 (the community default from the original paper).

Reading the formula:

- Rank 1 contributes ~1/61, rank 100 contributes ~1/160 — the harmonic-ish
  decay rewards top placements without letting any single list dominate.
- **Consensus wins.** A doc 4th in both lists (~2/64 ≈ 0.031) beats a doc
  1st in one and absent in the other (1/61 ≈ 0.016). That's exactly the
  hybrid thesis: agreement between independent signals is the strongest
  relevance evidence you have.
- **k is the flattening knob.** Small k → top ranks dominate (closer to
  "pick the best single list"); large k → ranks compress toward equality
  (closer to "any hit counts"). k=60 sits where rank differences between
  1 and 3 matter but 40 vs 60 barely do.

## What hybrid buys, concretely

Typical golden-set result when dense-only recall@10 is ~0.75: +5–15 points
from adding BM25 via RRF, concentrated in the identifier/jargon queries
dense retrieval blurs. It's the cheapest recall you will ever buy — two
indexes and ~20 lines of fusion code (this module's challenge).

## Beyond plain RRF

- **Weighted RRF:** multiply each list's contribution by a weight (lean
  lexical for support portals full of error codes; lean dense for
  natural-language FAQs). One extra hyperparameter — now you need the
  golden set to tune it, you have one (lesson 110).
- **Score normalization fusion:** still useful when you must preserve
  calibrated scores downstream (e.g., thresholding); normalize per query,
  not globally.

Reranking (lesson 090) sits *after* fusion: fuse cheaply to a top-50,
then let the expensive model sort the shortlist.

## Check yourself

1. Doc A: 1st in dense, absent in BM25. Doc B: 5th in both. Compute both
   RRF scores (k=60) — who wins, and why is that the right call?
2. Your team ships hybrid and recall *drops*. What did they most likely
   get wrong?
3. Why does RRF need no per-query calibration when raw-score weighted
   averaging does?

Next: [090 — Reranking with cross-encoders](090-reranking-with-cross-encoders.md)
