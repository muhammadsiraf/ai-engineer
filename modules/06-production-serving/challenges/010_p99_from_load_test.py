"""Challenge 010 — Compute p99 from a load test.

Lesson: 030 — load-testing (and 040 for the SLO check).

Percentile with LINEAR INTERPOLATION (numpy's default convention):

    given sorted samples x_0..x_{n-1}
    rank  = (p/100) × (n − 1)
    value = x[floor(rank)] + (rank − floor(rank)) × (x[ceil(rank)] − x[floor(rank)])

Implement:

  - percentile(samples, p) -> float
        samples may be unsorted (sort a COPY); ValueError if empty or
        p not in (0, 100]
  - summarize(samples) -> dict
        {"p50", "p95", "p99", "mean"} — float keys, mean = plain average
  - meets_slo(samples, threshold, pct=95) -> bool
        pct percent of requests at or under threshold
  - max_rps_meeting_slo(rps_to_p95: dict, slo_ms) -> float | None
        largest load level whose p95 <= slo_ms (None if even the
        lightest level fails); dict order must not matter

Reference (tests encode them):
    samples 10..19 (n=10): p50 = 14.5, p95 = 18.55, p99 = 18.91

Run:  pytest modules/06-production-serving/challenges/test_010_p99_from_load_test.py -v
"""


def percentile(samples: list, p: float) -> float:
    raise NotImplementedError


def summarize(samples: list) -> dict:
    raise NotImplementedError


def meets_slo(samples: list, threshold: float, pct: float = 95) -> bool:
    raise NotImplementedError


def max_rps_meeting_slo(rps_to_p95: dict, slo_ms: float) -> float | None:
    raise NotImplementedError
