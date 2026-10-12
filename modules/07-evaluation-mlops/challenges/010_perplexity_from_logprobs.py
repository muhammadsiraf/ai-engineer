"""Challenge 010 — Compute perplexity from log-probs.

Lesson: 030 — perplexity and reference metrics.

Given per-token log-probs (natural log, what `logprobs` fields emit):

    mean loss (nats):  L = −(1/n) Σ ln p_i
    perplexity:        PPL = e^L

    if your log-probs are in bits (log base 2):
    perplexity         PPL = 2^( −(1/n) Σ log2 p_i )

PPL reads as "effective branching factor": PPL 40 ≈ the model was as
uncertain as a uniform choice among 40 tokens. Lower = less surprised.

Implement (pure Python, math module):

  - perplexity(logprobs: list[float]) -> float
        ValueError on empty input
  - perplexity_from_bits(bit_logprobs: list[float]) -> float
        same, for log2 inputs
  - interpret(ppl: float) -> str
        ppl < 10    → "confident"
        ppl < 100   → "typical"
        else        → "uncertain"

Reference (tests encode them):
    uniform over V tokens: each ln p = −ln V → PPL == V
    [ln 0.5, ln 0.5] → PPL == 2 ; one certain token (ln 1.0) → PPL == 1

Run:  pytest modules/07-evaluation-mlops/challenges/test_010_perplexity_from_logprobs.py -v
"""

import math


def perplexity(logprobs: list[float]) -> float:
    raise NotImplementedError


def perplexity_from_bits(bit_logprobs: list[float]) -> float:
    raise NotImplementedError


def interpret(ppl: float) -> str:
    raise NotImplementedError
