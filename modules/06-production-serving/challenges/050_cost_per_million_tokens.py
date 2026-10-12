"""Challenge 050 — Compute cost per million tokens.

Lesson: 090 — GPU economics.

    cost_per_replica_second = hourly_price ÷ 3600
    effective_tps           = aggregate_tps × utilization   (you pay wall-clock,
                                                              throughput is earned)
    cost_per_1M_tokens      = cost_per_replica_second ÷ (effective_tps ÷ 1e6)
                            = hourly_price × 1e6 ÷ (3600 × aggregate_tps × util)

Implement:

  - cost_per_replica_second(hourly_price) -> float
  - cost_per_million_tokens(hourly_price, aggregate_tps, utilization)
        -> float    (ValueError for non-positive price/tps or
                     utilization not in (0, 1])
  - monthly_cost(hourly_price, replicas, hours=730.0) -> float
  - margin_vs_managed(self_cost_per_1m, managed_price_per_1m) -> float
        (1 − self/managed; negative = you'd lose money self-hosting)

Reference numbers (tests encode them):
    $2/hr, 1400 tok/s, 100% util  → ≈ $0.397 per 1M   (lesson's "$0.40")
    $1.60/hr, 800 tok/s, 80% util → ≈ $0.694 per 1M
    same at 50% util              → ≈ $1.111 per 1M   (utilization is the game)

Run:  pytest modules/06-production-serving/challenges/test_050_cost_per_million_tokens.py -v
"""


def cost_per_replica_second(hourly_price: float) -> float:
    raise NotImplementedError


def cost_per_million_tokens(
    hourly_price: float, aggregate_tps: float, utilization: float
) -> float:
    raise NotImplementedError


def monthly_cost(hourly_price: float, replicas: int, hours: float = 730.0) -> float:
    raise NotImplementedError


def margin_vs_managed(self_cost_per_1m: float, managed_price_per_1m: float) -> float:
    raise NotImplementedError
