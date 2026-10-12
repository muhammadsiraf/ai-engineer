"""Challenge 050 — Score an agent run.

Lesson: 120 — completion is self-reported, success is verified, cost
decides viability. The completion–success gap is itself a metric: an
agent that claims done on tasks it failed has a grounding problem.

A run record:
    {"done": bool,        # the agent declared completion
     "verified": bool,    # an independent checker confirmed the goal
     "steps": int, "tokens": int, "dollars": float}

Implement (pure Python):

  - completion_rate(runs) -> float     mean(done)      — ValueError on empty
  - success_rate(runs) -> float        mean(verified)  — ValueError on empty
  - cost_per_success(runs) -> float
        sum(dollars of VERIFIED runs) / count(verified)
        — ValueError if runs empty or nothing verified
  - steps_per_success(runs) -> float   mean steps among verified runs
  - avg_tokens(runs) -> float          mean tokens across ALL runs
  - summary(runs) -> dict
        {"completion", "success", "dollars_per_success",
         "steps_per_success", "avg_tokens"}

Reference (tests encode them):
    4 runs: 3 done, 2 verified → completion .75, success .5
    dollars .03/.09/.18/.05 → dollars_per_success = (.03+.05)/2 = 0.04
      (the failed runs' dollars burn without counting)
    steps among verified: (4+6)/2 = 5.0; avg tokens 3025.0

Run:  pytest modules/08-agents-tool-use/challenges/test_050_score_agent_run.py -v
"""


def completion_rate(runs: list[dict]) -> float:
    raise NotImplementedError


def success_rate(runs: list[dict]) -> float:
    raise NotImplementedError


def cost_per_success(runs: list[dict]) -> float:
    raise NotImplementedError


def steps_per_success(runs: list[dict]) -> float:
    raise NotImplementedError


def avg_tokens(runs: list[dict]) -> float:
    raise NotImplementedError


def summary(runs: list[dict]) -> dict:
    raise NotImplementedError
