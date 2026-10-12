"""Challenge 020 — Get the answer right with chain-of-thought.

Lesson: 050-chain-of-thought-when-to-use-it

The mock model here can only do ONE-STEP reasoning: each call, it either
peeks up a fact or combines two numbers ALREADY VISIBLE in the conversation.
Your job: write the prompt orchestration that makes multi-step problems
solvable anyway — the essence of CoT.

The mock (MockReasoner):
  - `complete(messages)` inspects the LAST user message for a request of the
    form:
        "ADD <a> <b>"        -> answers with the sum as a plain integer string
        "FACT <key>"         -> answers with facts[key] (or 'MISSING')
    A real CoT works the same way: each turn's context lets the model do one
    small deterministic step.

Implement:
  1. solve_two_hop(client, facts, a_key, b_key) — get price A, get price B,
     then request their ADD. Return the integer sum.
  2. solve_with_budget(client, facts, steps) — run a LIST of steps, where a
     step is ("FACT", key) or ("ADD", n1, n2) and ADD may reference results
     of earlier steps by their index as strings (e.g. ("ADD", "#0", "#1")).
     Return the final value.
  3. parse_final(text) — extract the trailing integer from a CoT-style
     response line 'Answer: <int>' (raise ValueError if absent).

The lesson this cements: the conversation IS the working memory; the
orchestrator decides what gets computed and when.

Run:  pytest modules/02-using-llms-via-api/challenges/test_020_chain_of_thought.py -v
"""

from typing import Callable

MockComplete = Callable[[list[dict]], str]


class MockReasoner:
    """One-step 'model'. Provided; do not modify."""

    def __init__(self, facts: dict[str, int]):
        self.facts = facts
        self.prompts_seen: list[str] = []

    def complete(self, messages: list[dict]) -> str:
        last = messages[-1]["content"]
        self.prompts_seen.append(last)
        tokens = last.split()
        if tokens and tokens[0] == "ADD" and len(tokens) == 3:
            return str(int(tokens[1]) + int(tokens[2]))
        if tokens and tokens[0] == "FACT" and len(tokens) == 2:
            return str(self.facts.get(tokens[1], "MISSING"))
        return "UNCLEAR"


def _last(messages: list[dict], content: str) -> list[dict]:
    return messages + [{"role": "user", "content": content}]


def solve_two_hop(client: MockReasoner, facts: dict[str, int], a_key: str, b_key: str) -> int:
    """Ask FACT for a_key, FACT for b_key, then ADD them. Return int sum.

    The FACT responses must come back through the conversation (append them
    as assistant messages) so the final ADD turn carries the full history.
    """
    raise NotImplementedError


def solve_with_budget(client: MockReasoner, facts: dict[str, int], steps: list[tuple]) -> int:
    """Execute steps in order; '#N' in an ADD operand refers to result N.

    Returns the final step's integer value. Raise ValueError on a MISSING
    fact or an unknown step shape.
    """
    raise NotImplementedError


def parse_final(text: str) -> int:
    """Extract the integer after 'Answer:' (case-insensitive). Raise
    ValueError if there is none."""
    raise NotImplementedError
