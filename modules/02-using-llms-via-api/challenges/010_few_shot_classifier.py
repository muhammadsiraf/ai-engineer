"""Challenge 010 — Classify with few-shot examples.

Lesson: 030-few-shot-examples-when-they-matter

You have a mock LLM whose "skill" is imitation: it answers by matching the
format and label-set of the examples it is shown (see MockLLM below). Your
job is the PROMPT ARCHITECTURE, not the model:

  1. build_few_shot_messages(system, examples, user_input) — render a proper
     message list: system turn, then each example as a user/assistant pair,
     then the real user input, fenced.
  2. classify(client, examples, text) — call the mock with your messages and
     parse the label out of the response.
  3. select_examples(example_pool, text, k) — pick the k most relevant
     examples for the input (a simple lexical-overlap scorer is fine).

Contract details the tests enforce:
  - Examples must be alternated user -> assistant, IN ORDER, before the
    real input. The real input must be LAST.
  - Input fencing: the real text goes between <ticket> and </ticket>.
  - classify() must raise ValueError if the model's answer is not one of
    the labels seen in `examples`.
  - select_examples must never return more than k, must not mutate the pool,
    and must return examples (not indices).

Run:  pytest modules/02-using-llms-via-api/challenges/test_010_few_shot_classifier.py -v
"""

from typing import Callable, Iterable

MockComplete = Callable[[list[dict]], str]


class MockLLM:
    """A fake classifier LLM.

    Its 'intelligence': it scans the conversation for EXAMPLES (user/assistant
    pairs) and the fenced input; it returns the label of the example whose
    user-side text shares the most words with the fenced input. With zero
    examples it answers 'unknown'. This models the few-shot mechanism well
    enough to test prompt structure.
    """

    def __init__(self) -> None:
        self.last_messages: list[dict] | None = None

    def complete(self, messages: list[dict]) -> str:
        self.last_messages = messages
        examples: list[tuple[str, str]] = []
        i = 0
        while i + 1 < len(messages):
            if messages[i]["role"] == "user" and messages[i + 1]["role"] == "assistant":
                examples.append((messages[i]["content"], messages[i + 1]["content"]))
                i += 2
            else:
                i += 1
        fenced = _extract_fenced(messages)
        best_label, best_score = "unknown", 0
        q = set(_words(fenced or ""))
        for user_text, answer in examples:
            label = answer.strip()
            score = len(q & set(_words(user_text)))
            if score > best_score:
                best_label, best_score = label, score
        return best_label


def _words(s: str) -> list[str]:
    out, cur = [], []
    for ch in s.lower():
        if ch.isalnum():
            cur.append(ch)
        elif cur:
            out.append("".join(cur))
            cur = []
    if cur:
        out.append("".join(cur))
    return out


def _extract_fenced(messages: list[dict]) -> str | None:
    for m in reversed(messages):
        if m["role"] != "user":
            continue
        if "<ticket>" in m["content"] and "</ticket>" in m["content"]:
            return m["content"].split("<ticket>", 1)[1].split("</ticket>", 1)[0]
    return None


def build_few_shot_messages(
    system: str,
    examples: Iterable[tuple[str, str]],
    user_input: str,
) -> list[dict]:
    """Render [system, (user, assistant) per example..., fenced user input].

    Fenced input format:  '<ticket>\n' + user_input + '\n</ticket>'
    """
    raise NotImplementedError


def classify(client: MockLLM, examples: list[tuple[str, str]], text: str) -> str:
    """Build messages, call client.complete, validate the label against the
    example label set. Raise ValueError on unknown labels."""
    raise NotImplementedError


def select_examples(
    pool: list[tuple[str, str]],
    text: str,
    k: int,
) -> list[tuple[str, str]]:
    """Return the k pool examples whose user text shares the most words with
    `text`. Ties: earlier pool entries win. Stability: equal scores keep
    pool order; the returned list is ordered best-first."""
    raise NotImplementedError
