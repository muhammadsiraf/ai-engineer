"""Challenge 030 — Compute the replica count for a load.

Lesson: 050 — autoscaling (capacity from lesson 030's load tests).

    replicas_needed = ceil( peak_demand ÷ (capacity_per_replica × target_util) )

    target_utilization ≤ 1.0 is the headroom that absorbs bursts and the
    minutes-long scale-out reaction gap; lesson 050's rule: 0.7–0.8.

Implement:

  - replicas_needed(peak_rps, per_replica_rps, target_utilization=0.75)
        -> int   (ValueError if per_replica_rps <= 0 or utilization
                  not in (0, 1])
  - provisioned_utilization(current_replicas, per_replica_rps, actual_rps)
        -> float   (actual / (replicas × per_replica); >1.0 = overloaded)
  - can_absorb_burst(min_replicas, per_replica_rps, burst_rps) -> bool
  - scale_decision(queue_depth, queue_threshold, current_replicas,
                   min_replicas, max_replicas, sustained_idle) -> str
        queue_depth > threshold:
            current < max → "scale_out"   else → "at_max"
        else if sustained_idle and current > min → "scale_in"
        else → "hold"

Lesson check-yourself numbers (tests encode them):
    40 RPS peak, 12 RPS/replica, 0.75 util → 5 replicas (not ceil(40/12)=4)

Run:  pytest modules/06-production-serving/challenges/test_030_replica_count_for_load.py -v
"""

import math


def replicas_needed(
    peak_rps: float, per_replica_rps: float, target_utilization: float = 0.75
) -> int:
    raise NotImplementedError


def provisioned_utilization(
    current_replicas: int, per_replica_rps: float, actual_rps: float
) -> float:
    raise NotImplementedError


def can_absorb_burst(
    min_replicas: int, per_replica_rps: float, burst_rps: float
) -> bool:
    raise NotImplementedError


def scale_decision(
    queue_depth: int,
    queue_threshold: int,
    current_replicas: int,
    min_replicas: int,
    max_replicas: int,
    sustained_idle: bool,
) -> str:
    raise NotImplementedError
