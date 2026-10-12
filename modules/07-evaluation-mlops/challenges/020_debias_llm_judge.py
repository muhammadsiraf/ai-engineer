"""Challenge 020 — De-bias an LLM judge (position bias).

Lesson: 050 — LLM-as-judge (defenses against position bias).

Pairwise comparisons run in BOTH orders. A result record:

    {"a": "model_a", "b": "model_b", "winner": "model_a"}
    # winner is whichever ITEM won; order within the pair is (a, b)

Position bias defense: a pair's verdict is only a win if the SAME item
wins in both orders; a split verdict is a tie (lesson 050's rule).

    debiased_verdict: "a" | "b" | "tie"   (ValueError if either order missing)
    debiased_win_rate(item): mean over that item's pairs of
                             win=1.0, tie=0.5, loss=0.0
    position_bias_index(item): P(item wins | listed first)
                               − P(item wins | listed second)
                               (0.0 = no position bias)

Implement (pure Python):

  - debiased_verdict(results, a, b) -> str
  - debiased_win_rate(results, item) -> float
        ValueError if the item appears in no pair
  - position_bias_index(results, item) -> float

Lesson 050's example (tests encode it):
    judge picks A 65% of the time when A is listed first, 45% when
    second → position_bias_index == 0.20, and the naive single-order
    protocol would have reported anything from .45 to .65.

Run:  pytest modules/07-evaluation-mlops/challenges/test_020_debias_llm_judge.py -v
"""


def debiased_verdict(results: list, a: str, b: str) -> str:
    raise NotImplementedError


def debiased_win_rate(results: list, item: str) -> float:
    raise NotImplementedError


def position_bias_index(results: list, item: str) -> float:
    raise NotImplementedError
