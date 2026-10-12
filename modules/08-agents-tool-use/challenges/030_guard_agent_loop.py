"""Challenge 030 — Guard the agent loop.

Lesson: 060 — budgets are enforced in code, never requested in a
prompt. One verdict per turn: continue, or stop-with-reason.

The guard watches three quantities and trips the FIRST threshold hit,
in precedence order (most diagnostic first):

    repeat_loop    the same call signature appears max_repeats times
                   in a row (default 2) — calling again is a loop,
                   not a plan
    error_streak   max_error_streak consecutive failing calls
                   (default 3); a success resets the streak
    step_budget    max_steps total tool calls (default 25);
                   the max_steps-th call trips it

Once tripped the verdict is sticky — the run is over; every later
record() returns the same reason.

Implement (pure Python):

  - class LoopGuard(max_steps=25, max_error_streak=3, max_repeats=2)
        .record(signature, ok) -> str
              call AFTER each executed tool call; signature is any
              hashable canonical id (see challenge 020)
              → "continue" | "repeat_loop" | "error_streak"
                | "step_budget_exceeded"
        .record_answer() -> str
              the model answered; run over → "done"
        exposes .steps (calls recorded) and
                .stop_reason ("answered" after record_answer)

Reference (tests encode them):
    defaults: ("a", True) → continue; ("a", True) again → repeat_loop
    max_steps=3 → the third distinct call trips step_budget_exceeded
    E, E, S, E, E with max_error_streak=3 → never trips

Run:  pytest modules/08-agents-tool-use/challenges/test_030_guard_agent_loop.py -v
"""


class LoopGuard:
    def __init__(
        self, max_steps: int = 25, max_error_streak: int = 3, max_repeats: int = 2
    ):
        raise NotImplementedError

    def record(self, signature: str, ok: bool) -> str:
        raise NotImplementedError

    def record_answer(self) -> str:
        raise NotImplementedError
