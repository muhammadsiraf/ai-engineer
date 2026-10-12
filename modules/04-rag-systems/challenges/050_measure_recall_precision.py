"""Challenge 050 — Measure recall@k and precision@k.

Lesson: 110 — evaluating retrieval.

    retrieved: ranked list of doc/chunk ids (best first)
    relevant:  set of golden ids

    recall@k    = |retrieved[:k] ∩ relevant| / |relevant|
                  (relevant == empty → 0.0; nothing retrieved can be right)
    precision@k = |retrieved[:k] ∩ relevant| / min(k, len(retrieved))
                  (denominator is what you actually returned)
    mrr         = 1 / rank_of_first_relevant (1-based), 0.0 if none

Validate: k >= 1 else ValueError.

The k that matters: the number of chunks your generator actually receives
(lesson 100's context budget). Reference scenario (tests encode it):
    relevant = {d1, d2, d3, d4}; retrieved top-10 contains d2, d1, d3
    → recall@10 = 3/4, precision@10 = 3/10.

Run:  pytest modules/04-rag-systems/challenges/test_050_measure_recall_precision.py -v
"""


def recall_at_k(retrieved: list, relevant: set, k: int) -> float:
    raise NotImplementedError


def precision_at_k(retrieved: list, relevant: set, k: int) -> float:
    raise NotImplementedError


def mrr(retrieved: list, relevant: set) -> float:
    raise NotImplementedError
