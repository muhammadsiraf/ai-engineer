"""Challenge 040 — Compute prefix-cache hits under routing.

Lesson: 070 — prefix-aware routing (mechanism: M3 L070).

Simulate a fleet of n replicas, each with a per-replica prefix cache
(capacity = number of distinct prefix keys; None = unlimited, eviction
= LRU). Routing policies:

    "round_robin":  request i → replica i % n        (cache-blind LB)
    "affinity":     request i → shard_for(prefix_key, n)
                    shard_for = crc32(key) % n        (prefix-aware LB)

Hit rate is TOKEN-WEIGHTED (the engine metric):
    hits = Σ tokens of requests whose replica held their prefix cached
    hit_rate = hits / total_tokens

Implement:

  - shard_for(key: str, n_replicas: int) -> int
  - simulate(requests, n_replicas, policy, cache_capacity=None) -> float
        requests: list[(prefix_key, prompt_tokens)]
        ValueError for n < 1, bad policy, capacity < 1

Reference results (tests encode them):
    1 replica, 3 keys × 10 interleaved requests, unlimited cache → 0.9
    same, capacity 2, strict k0,k1,k2 cycle           → 0.0  (LRU thrash)
    same, capacity 2, pattern k0,k0,k1,k1,k2,k2 ×5    → 0.5
    4 replicas, 5 keys × cycling, capacity 1:
        round_robin → 0.0 (each replica sees all 5 keys, period 20)
        affinity    → > round_robin, and deterministic

Run:  pytest modules/06-production-serving/challenges/test_040_prefix_cache_hits_under_routing.py -v
"""

import zlib


def shard_for(key: str, n_replicas: int) -> int:
    raise NotImplementedError


def simulate(
    requests: list,
    n_replicas: int,
    policy: str,
    cache_capacity: int | None = None,
) -> float:
    raise NotImplementedError
