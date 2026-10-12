"""Challenge 060 — Summarize the overflow.

Lesson: 100-context-window-economics / Module 1 lesson 170

History management: keep the conversation inside a token budget using the
summarize-then-truncate strategy, without ever touching the system prompt.

Rules (the tests are the spec):
  - messages[0] is ALWAYS the system prompt and is always kept verbatim.
  - Turn pairs are (user, assistant) message pairs after the system message.
  - While total tokens > budget: summarize the OLDEST pair into one
    assistant-style message '[summary] ...' via the injected summarizer,
    and replace that pair with it. Repeat until under budget (or no pairs
    remain).
  - The summarizer signature: summarize(text: str) -> str. Concatenate the
    pair's contents with '\n' when calling it. Prefix the result with
    '[summary] '.
  - Count tokens with the injected tokenizer (encode -> len), PLUS the same
    msg_overhead=4 per message, PLUS base overhead 3.
  - If even one pair exceeds the budget with an empty history, leave the
    last pair intact (never return an empty conversation) — under-budget
    is best-effort, not guaranteed.

Implement `fit_history(messages, budget, tokenizer, summarize)` -> new list.
Do not mutate the input.

Run:  pytest modules/02-using-llms-via-api/challenges/test_060_summarize_overflow.py -v
"""

from typing import Callable

Summarize = Callable[[str], str]


def _count(messages: list[dict], tokenizer) -> int:
    return 3 + sum(4 + len(tokenizer.encode(m["content"])) for m in messages)  # noqa: PLR2004


def fit_history(
    messages: list[dict],
    budget: int,
    tokenizer,
    summarize: Summarize,
) -> list[dict]:
    raise NotImplementedError
