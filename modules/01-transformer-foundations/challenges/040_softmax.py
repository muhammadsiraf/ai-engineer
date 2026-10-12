"""Challenge 040 — Implement softmax.

Lesson: 090 / 100 / 140 — softmax appears in attention, model output, and sampling.

    softmax(x)_i = exp(x_i) / sum_j exp(x_j)

Requirements:
  1. Numerically stable: subtract the row max before exp (same trick as the
     cross-entropy challenge). softmax(x) == softmax(x + c) for any scalar c,
     so the shift is free mathematically and prevents overflow.
  2. Rows independently for 2-D input (this is what attention needs).
  3. Support an optional `mask`: boolean array, same shape, where True means
     "forbid this position" — masked positions must get EXACTLY 0.0 probability
     and the remaining probabilities must still sum to 1. A fully-masked row
     (all True) should raise ValueError.

This function is the last building block before attention — after this you can
write `softmax(QK^T / sqrt(dk), mask=causal)` yourself.

Run:  pytest modules/01-transformer-foundations/challenges/test_040_softmax.py -v
"""

import numpy as np


def softmax(x: np.ndarray, mask: np.ndarray | None = None) -> np.ndarray:
    """Numerically-stable softmax over the last axis.

    Args:
        x: (..., n) array of raw scores.
        mask: optional boolean array broadcastable to x.shape; True = forbidden.

    Returns:
        Same-shape array; each "row" (last axis) sums to 1 (masked entries 0.0).

    Raises:
        ValueError: if any row is fully masked.
    """
    raise NotImplementedError
