"""Challenge 010 — Rank by cosine similarity.

Lesson: 030 — embeddings and cosine.

    cos(a, b) = (a · b) / (||a|| × ||b||)

Implement (pure Python; no numpy):

  - cosine(a, b) -> float
        ValueError on length mismatch or a zero vector
        (similarity of a zero vector is undefined)
  - rank_by_cosine(query, docs) -> list[tuple[int, float]]
        [(doc_index, score), ...] sorted by score DESCENDING.
        Ties: lower index first. All docs included, best first.

Reference facts (tests encode them):
    cos(x, x) == 1 (up to float error)
    cos of orthogonal vectors == 0
    scaling a document's vector never changes its RANK
    a near-duplicate beats a merely-related doc

Run:  pytest modules/04-rag-systems/challenges/test_010_rank_by_cosine.py -v
"""

import math


def cosine(a: list[float], b: list[float]) -> float:
    raise NotImplementedError


def rank_by_cosine(query: list[float], docs: list[list[float]]) -> list[tuple[int, float]]:
    raise NotImplementedError
