"""Challenge 040 — Route a query to the right worker.

Lesson: 080 — the supervisor owns the goal and delegates subtasks;
routing is its first decision. Start deterministic: a keyword scorer
with a documented tie-break beats an untested prompt heuristic, and
the margin tells you when to ask a clarifying question instead.

    score(worker) = # of rule keywords appearing in the query
                    (whole words, case-insensitive)
    route         = argmax score; tie → lexicographically smallest
                    worker name; all-zero → default
    margin        = top score − runner-up score (0 when tied)

Implement (pure Python, re module):

  - score_workers(rules, query) -> dict[str, int]
        rules: {worker: [keywords]}; every worker appears in the
        result, 0 when it has no hits
  - route(rules, query, default="general") -> str
  - margin(scores) -> int
        the caller decides: margin 0 → clarify before delegating

Reference (tests encode them):
    rules: billing  ← [refund, invoice, charge]
           shipping ← [package, delivery, track]
    "Where is my refund for the lost package?" → 1 vs 1 → "billing"
    "I need a refund and my invoice corrected" → "billing" (2 vs 0)
    "hello" → "general"

Run:  pytest modules/08-agents-tool-use/challenges/test_040_route_to_worker.py -v
"""

import re


def score_workers(rules: dict[str, list[str]], query: str) -> dict[str, int]:
    raise NotImplementedError


def route(rules: dict[str, list[str]], query: str, default: str = "general") -> str:
    raise NotImplementedError


def margin(scores: dict[str, int]) -> int:
    raise NotImplementedError
