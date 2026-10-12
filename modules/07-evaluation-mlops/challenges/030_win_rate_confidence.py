"""Challenge 030 — Win-rate confidence bounds.

Lessons: 050/060 — how many comparisons before a win rate is real?

    p  = wins / n
    se = sqrt( p(1−p) / n )
    95% CI = [p − 1.96·se, p + 1.96·se]   (clamped to [0, 1])

    "significant" = the 95% CI excludes 0.5 (better-than-coin-flip)

Sample size for detecting a true rate p1 vs the 0.5 baseline at power:

    n = ceil( (z_α/2 + z_β)² · (p1(1−p1) + p2(1−p2)) / (p1 − p2)² )
    defaults: α=0.05 → z=1.960, power=0.8 → z=0.8416
    (p2 is the baseline rate, default 0.5)

Implement (pure Python, math module):

  - standard_error(wins, n) -> float       (ValueError unless 0<=wins<=n, n>=1)
  - ci95(wins, n) -> tuple[float, float]   (clamped)
  - significant(wins, n, alpha=0.05) -> bool
        z from alpha: two-sided normal quantile (1.960 for 0.05;
        implement with an approximation or hardcode a small lookup)
  - sample_size_needed(p1, p2=0.5, alpha=0.05, power=0.8) -> int

Reference (tests encode them):
    600/1000 → CI ≈ [0.570, 0.630], significant
    520/1000 → CI ≈ [0.489, 0.551], NOT significant
    p1=0.55 vs 0.5 → n ≈ 1,562   (lesson 060's "roughly 1,600 per arm")

Run:  pytest modules/07-evaluation-mlops/challenges/test_030_win_rate_confidence.py -v
"""

import math


def standard_error(wins: int, n: int) -> float:
    raise NotImplementedError


def ci95(wins: int, n: int) -> tuple[float, float]:
    raise NotImplementedError


def significant(wins: int, n: int, alpha: float = 0.05) -> bool:
    raise NotImplementedError


def sample_size_needed(
    p1: float, p2: float = 0.5, alpha: float = 0.05, power: float = 0.8
) -> int:
    raise NotImplementedError
