"""Challenge 050 — Compute the spec-decode speedup.

Lesson: 100 — speculative decoding.

Per verify pass, with per-token acceptance rate α, draft length k, and
draft cost c (in units of one target-model pass):

    expected tokens per verify pass:
        E = (1 − α^(k+1)) / (1 − α)         (α = 1 → k + 1)
    cost of the round (draft + verify):
        C = 1 + k·c
    speedup:
        S = E / C

Reference numbers (tests encode them):
    α=0.8, k=4, c=0.1 → E ≈ 3.36, C = 1.4 → S ≈ 2.4x
    α=0.5             → S ≈ 1.3–1.4x      (marginal)
    α=0.95            → S ≈ 3.2–3.3x      (acceptance is everything)

Implement:

  - expected_tokens_per_pass(alpha, k) -> float
        ValueError unless 0 <= alpha <= 1 and k >= 1
  - verify_cost(k, c) -> float
  - speedup(alpha, k, c) -> float
  - best_draft_length(alpha, c, k_min=1, k_max=16) -> tuple[int, float]
        the k in [k_min, k_max] maximizing speedup, with its speedup

Run:  pytest modules/03-inference-fundamentals/challenges/test_050_spec_decode_speedup.py -v
"""


def expected_tokens_per_pass(alpha: float, k: int) -> float:
    raise NotImplementedError


def verify_cost(k: int, c: float) -> float:
    raise NotImplementedError


def speedup(alpha: float, k: int, c: float) -> float:
    raise NotImplementedError


def best_draft_length(
    alpha: float, c: float, k_min: int = 1, k_max: int = 16
) -> tuple[int, float]:
    raise NotImplementedError
