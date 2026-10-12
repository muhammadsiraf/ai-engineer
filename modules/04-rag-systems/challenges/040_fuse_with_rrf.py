"""Challenge 040 — Fuse rankings with RRF.

Lesson: 080 — hybrid retrieval and Reciprocal Rank Fusion.

    RRF(d) = Σ_over_rankings  1 / (k + rank)      rank is 1-based,
                                                   absent → contributes 0
    default k = 60

Implement:

  - rrf_score(doc_id, rankings, k=60) -> float
  - fuse(rankings, k=60) -> list[tuple[doc_id, float]]
        every doc that appears in ANY ranking, best RRF first;
        ties broken by doc_id ascending (deterministic output)

Worked example (tests encode it):
    dense = [A, B, C]     bm25 = [B, A, C]
    RRF(A) = 1/61 + 1/62
    RRF(B) = 1/62 + 1/61   →  identical! (A and B swap places 1↔2)
    RRF(C) = 1/63 + 1/63   →  C trails both

Consensus example (tests encode it):
    dense = [X, P, Q]     bm25 = [Y, P, Q]
    P (2nd in both) beats X (1st in dense, absent in bm25):
    RRF(P) = 2/62   >   RRF(X) = 1/61

Validate: rankings is a list of lists of doc_ids; k must be >= 0
(ValueError otherwise).

Run:  pytest modules/04-rag-systems/challenges/test_040_fuse_with_rrf.py -v
"""


def rrf_score(doc_id, rankings: list, k: int = 60) -> float:
    raise NotImplementedError


def fuse(rankings: list, k: int = 60) -> list:
    raise NotImplementedError
