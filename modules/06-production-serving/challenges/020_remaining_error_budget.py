"""Challenge 020 — Compute the remaining error budget.

Lesson: 040 — SLOs and error budgets.

    allowed    = (1 − slo) × total_requests          (the whole budget)
    remaining  = 1 − violations / allowed            (can go negative!)
    burn_rate  = (violations / allowed) ÷ (elapsed / window)
                 (1.0 = consuming budget exactly on schedule)

Policy thresholds (lesson 040):
    remaining >  0.50          → "ship"
    0.25 < remaining <= 0.50   → "tighten"
    remaining <= 0.25          → "freeze"

Implement:

  - allowed_violations(total_requests, slo) -> float
  - remaining_budget_fraction(total_requests, violations, slo) -> float
  - burn_rate(violations, allowed, elapsed_hours, window_hours) -> float
  - action(remaining) -> str          one of "ship" / "tighten" / "freeze"

Validate: 0 < slo < 1; violations >= 0; elapsed, window > 0 (ValueError).

Lesson check-yourself numbers (tests encode them):
    SLO 99.5%, 2M requests, 14,000 violations
      → allowed 10,000, remaining −0.40 → "freeze"
    burn: 3,500 violations, allowed 10,000, 168h into a 672h window
      → 1.4x budget speed

Run:  pytest modules/06-production-serving/challenges/test_020_remaining_error_budget.py -v
"""


def allowed_violations(total_requests: float, slo: float) -> float:
    raise NotImplementedError


def remaining_budget_fraction(
    total_requests: float, violations: float, slo: float
) -> float:
    raise NotImplementedError


def burn_rate(
    violations: float, allowed: float, elapsed_hours: float, window_hours: float
) -> float:
    raise NotImplementedError


def action(remaining: float) -> str:
    raise NotImplementedError
