"""Challenge 040 — Catch regressions (the CI gate).

Lesson: 070 — a prompt is code; give it a regression suite with a gate.

    per category c present in BOTH baseline and candidate:
        regression  ⇔  candidate[c] < baseline[c] − max_drop
    gate passes  ⇔  no category regressed

    (a drop of exactly max_drop passes — the slack absorbs judge
     noise; anything beyond it is a finding)

Implement (pure Python):

  - category_scores(results) -> dict[str, float]
        mean score per category from records shaped
        {"category": str, "score": float, ...}   (extra keys ignored)
  - find_regressions(baseline, candidate, max_drop=0.02) -> list[str]
        categories present in BOTH dicts that regressed,
        sorted worst-first (largest drop first)
  - gate(baseline, candidate, max_drop=0.02) -> bool
        True iff find_regressions is empty
  - diff_report(baseline, candidate) -> dict
        {cat: {"baseline": b, "candidate": c, "delta": c − b}}
        common categories only, sorted worst-first

Reference (tests encode them):
    billing 0.90 → 0.85  → regression (drop 0.05 > 0.02 slack)
    billing 0.90 → 0.88  → passes (drop == slack)
    a brand-new candidate category is not a regression;
    a category the candidate dropped is not a regression either.

ValueError on max_drop < 0 (a gate you can't fail is not a gate).

Run:  pytest modules/07-evaluation-mlops/challenges/test_040_catch_regressions.py -v
"""


def category_scores(results: list[dict]) -> dict[str, float]:
    raise NotImplementedError


def find_regressions(
    baseline: dict[str, float],
    candidate: dict[str, float],
    max_drop: float = 0.02,
) -> list[str]:
    raise NotImplementedError


def gate(
    baseline: dict[str, float],
    candidate: dict[str, float],
    max_drop: float = 0.02,
) -> bool:
    raise NotImplementedError


def diff_report(
    baseline: dict[str, float], candidate: dict[str, float]
) -> dict[str, dict]:
    raise NotImplementedError
