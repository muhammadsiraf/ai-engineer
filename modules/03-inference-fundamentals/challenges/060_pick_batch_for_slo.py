"""Challenge 060 — Pick the batch for your SLO.

Lesson: 120 — throughput vs latency (the module capstone).

You measured an aggregate decode-throughput table for a serving config:

    throughput_table: {batch_size: aggregate_tokens_per_second}

Per-request speed falls with batch size:

    per_request_tps(B) = throughput_table[B] / B

The operating point is the LARGEST batch whose per-request TPS still meets
the SLO. From that operating point, capacity planning:

    replicas = ceil( demand_tps / (aggregate_tps(B) × utilization) )

with utilization ≤ 1.0 (rule of thumb: ≤ 0.75 — queueing at 95%+ is an
outage; lesson 120's fact #1).

Implement:

  - per_request_tps(throughput_table, batch) -> float
  - max_batch_for_slo(throughput_table, min_per_request_tps)
        -> int | None   (None when even batch 1 can't meet the SLO;
                         must work regardless of dict insertion order)
  - replicas_for_load(throughput_table, batch, demand_tps, utilization=0.75)
        -> int          (ValueError if demand_tps < 0 or utilization
                         not in (0, 1])

Reference table (tests encode it):
    B=1→90, B=8→600, B=16→950, B=32→1400, B=64→1600 aggregate tok/s
    SLO ≥ 40 tok/s per request → batch 32 (43.75); batch 64 gives 25 — out.

Run:  pytest modules/03-inference-fundamentals/challenges/test_060_pick_batch_for_slo.py -v
"""


def per_request_tps(throughput_table: dict, batch: int) -> float:
    raise NotImplementedError


def max_batch_for_slo(throughput_table: dict, min_per_request_tps: float) -> int | None:
    raise NotImplementedError


def replicas_for_load(
    throughput_table: dict,
    batch: int,
    demand_tps: float,
    utilization: float = 0.75,
) -> int:
    raise NotImplementedError
