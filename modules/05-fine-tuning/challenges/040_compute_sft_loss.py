"""Challenge 040 — Compute the SFT loss (prompt masking).

Lesson: 080 — training loop and loss mask.

Two functions, the shift-and-mask pipeline in pure Python:

  build_labels(token_ids, response_start, ignore_index=-100) -> list[int]
      Position i of the logits predicts token i+1. The trainable positions
      are exactly those whose PREDICTED token lies in the response span:
          labels[i] = token_ids[i+1]   if response_start <= i+1 < n
          labels[i] = ignore_index     otherwise (incl. the last position)
      ValueError if response_start >= len(token_ids) (no response tokens).

  masked_cross_entropy(logits, labels, ignore_index=-100) -> float
      Mean over positions with labels != ignore_index of
          -log softmax(logits[i])[labels[i]]
      ValueError if every position is masked.

Reference (tests encode them):
    ids = [a, b, c, d], response_start = 2
      → labels = [-100, c, d, -100]     (positions 1 and 2 train)
    uniform logits over V tokens → loss = ln(V)

Run:  pytest modules/05-fine-tuning/challenges/test_040_compute_sft_loss.py -v
"""

import math


def build_labels(
    token_ids: list[int], response_start: int, ignore_index: int = -100
) -> list[int]:
    raise NotImplementedError


def masked_cross_entropy(
    logits: list[list[float]], labels: list[int], ignore_index: int = -100
) -> float:
    raise NotImplementedError
