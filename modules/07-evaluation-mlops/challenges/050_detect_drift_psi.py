"""Challenge 050 — Detect drift with PSI.

Lesson: 110 — drift is the slow failure; PSI is the early-warning
number that powers detection.

    PSI = Σ_buckets (current% − reference%) · ln(current% / reference%)

    buckets: n_buckets quantile bins of the REFERENCE window
             (linear interpolation between order statistics —
             the same rank rule as Module 6's p99)
    shares clamped to eps before the log (empty buckets are the edge case)
    reading:  < 0.1 quiet · 0.1–0.25 investigate · > 0.25 alarm

Implement (pure Python, math module):

  - bucket_edges(reference, n_buckets=10) -> list[float]
        the n_buckets − 1 interior quantile edges, ascending
  - shares(values, edges) -> list[float]
        fraction of values per bucket (bucket i = [edge[i−1], edge[i]),
        −inf/+inf at the ends; a value equal to an edge goes right —
        bisect_right over the edges)
  - psi(reference, current, n_buckets=10, eps=1e-6) -> float
  - psi_level(value) -> str    "quiet" / "investigate" / "alarm"

Reference (tests encode them):
    reference == current  → PSI = 0.0
    reference [0,1,2,3] in 2 buckets (edge 1.5),
    current [0,0,0,3]:
        ref shares [.5, .5] vs current [.75, .25]
        → PSI ≈ 0.2747       → "alarm"
    current [0,0,0,0] (second bucket empty): the eps clamp keeps
        PSI finite (≈ 6.908 at eps=1e-6)

ValueError on empty reference/current or n_buckets < 2.

Run:  pytest modules/07-evaluation-mlops/challenges/test_050_detect_drift_psi.py -v
"""

import math


def bucket_edges(reference: list[float], n_buckets: int = 10) -> list[float]:
    raise NotImplementedError


def shares(values: list[float], edges: list[float]) -> list[float]:
    raise NotImplementedError


def psi(
    reference: list[float],
    current: list[float],
    n_buckets: int = 10,
    eps: float = 1e-6,
) -> float:
    raise NotImplementedError


def psi_level(value: float) -> str:
    raise NotImplementedError
