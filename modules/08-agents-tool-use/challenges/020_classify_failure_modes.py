"""Challenge 020 — Classify the four failure shapes.

Lesson: 040 — agent failures look infinite and are actually four.
Every run gets one label; per-shape rates gate regressions (lesson 120).

Trajectory format (a list of steps):
    {"type": "tool_call", "name": str, "args": dict}
    {"type": "tool_result", "ok": True, "result": ...}
    {"type": "tool_result", "ok": False, "error_kind": str, "error": str}
        error_kind ∈ {"unknown_tool", "invalid_args", "runtime"}
    {"type": "answer", "text": str}

Labels (checked in this order):
    thrash      any call signature repeats ≥ 3 times — precedence
                over misuse (even if an invalid_args error occurred)
    misuse      any unknown_tool / invalid_args error occurred
                (recovered or not — the event still counts)
    unfinished  the trajectory does not end with an answer
    no_tools    answered without a single tool call
    premature   answered with tool calls but zero successful
                results — whatever it answered, it fabricated
    success     none of the above

Implement (pure Python, json module):

  - call_signature(name, args) -> str
        canonical: name + json.dumps(args, sort_keys=True) — argument
        order must not matter
  - error_kinds(trajectory) -> dict[str, int]
        histogram of error_kind over failed tool_results
  - classify(trajectory) -> str          (ValueError on empty)
  - shape_rates(trajectories) -> dict[str, float]
        fraction of runs per observed label

Run:  pytest modules/08-agents-tool-use/challenges/test_020_classify_failure_modes.py -v
"""

import json


def call_signature(name: str, args: dict) -> str:
    raise NotImplementedError


def error_kinds(trajectory: list[dict]) -> dict[str, int]:
    raise NotImplementedError


def classify(trajectory: list[dict]) -> str:
    raise NotImplementedError


def shape_rates(trajectories: list[list[dict]]) -> dict[str, float]:
    raise NotImplementedError
