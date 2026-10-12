"""Challenge 020 — Cosine similarity.

Lesson: 060-embeddings-vectors-as-meaning

Cosine similarity measures the angle between two vectors, ignoring their
magnitudes. It is THE similarity metric for embeddings (RAG, dedup, memory).

    cos(a, b) = (a · b) / (||a|| * ||b||)

Rules for this challenge:
  - Implement it with NumPy (or pure Python) — no scipy/sklearn.
  - Handle the zero-vector edge case: if either vector has zero norm,
    similarity is undefined; return 0.0 (a common production convention).
  - Use float64 internally for numerical stability.
  - In `cosine_sim_matrix`, compute all pairwise similarities efficiently
    (vectorized — no Python loops over pairs) and return an (n, n) array with
    1.0 on the diagonal.

Run:  pytest modules/01-transformer-foundations/challenges/test_020_cosine_similarity.py -v
"""

import numpy as np


def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine similarity between two 1-D vectors.

    Returns 0.0 if either vector has zero norm.
    """
    raise NotImplementedError


def top_k_similar(query: np.ndarray, docs: np.ndarray, k: int) -> list[tuple[int, float]]:
    """Return indices and scores of the k documents most similar to `query`.

    Args:
        query: (d,) vector.
        docs: (n, d) matrix of document vectors.
        k: number of results (if k > n, return all n).

    Returns:
        List of (index, score) tuples, sorted by score descending.
        Ties: lower index first.
    """
    raise NotImplementedError


def cosine_sim_matrix(vectors: np.ndarray) -> np.ndarray:
    """All pairwise cosine similarities of an (n, d) matrix -> (n, n) array.

    Diagonal must be exactly 1.0 for non-zero rows (use np.fill_diagonal).
    Zero rows: their similarities are 0.0 (including the diagonal entry).
    """
    raise NotImplementedError
