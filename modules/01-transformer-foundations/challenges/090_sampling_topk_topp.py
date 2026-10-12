"""Challenge 090 — Temperature, top-k, and top-p sampling.

Lesson: 140-temperature-top-k-and-top-p

Build the sampling pipeline from lesson 140 as pure, testable functions:

    logits -> temperature -> top-k -> top-p -> softmax -> sample

Functions to implement:
  1. apply_temperature(logits, t)      — divide logits by t; t=0 means greedy
  2. top_k_filter(logits, k)           — -inf outside the k best (ties: keep
                                         ALL tokens tied at the k-th value)
  3. top_p_filter(probs, p)            — keep smallest set of LARGEST probs
                                         whose sum >= p; renormalize the rest to 0
  4. sample_from(probs, rng, n)        — draw n token ids with replacement
  5. sample(logits, temperature, top_k, top_p, rng, n) — full pipeline

Conventions that matter (and that tests check):
  - Filters return NEW arrays; never mutate inputs.
  - top_p operates on PROBABILITIES (post-softmax), not logits.
  - p=1.0 must keep everything; k >= vocab must change nothing.
  - Numerical: use cumsum with a small epsilon tolerance — a float cumsum may
    reach 0.9999999 and must still count as >= p.

Run:  pytest modules/01-transformer-foundations/challenges/test_090_sampling_topk_topp.py -v
"""

import numpy as np


def apply_temperature(logits: np.ndarray, t: float) -> np.ndarray:
    """logits / t. If t == 0, return a one-hot of the argmax as scores
    (e.g., argmax gets 1.0, rest -inf) so downstream softmax = greedy."""
    raise NotImplementedError


def top_k_filter(logits: np.ndarray, k: int) -> np.ndarray:
    """Keep the k highest logits, set the rest to -inf.

    Ties at the cutoff: if multiple tokens share the k-th largest value,
    keep them all (result may have > k survivors).
    """
    raise NotImplementedError


def top_p_filter(probs: np.ndarray, p: float) -> np.ndarray:
    """Nucleus filtering on a probability vector.

    Keep the smallest set of highest-probability tokens whose probabilities
    sum to >= p (inclusive of the token that crosses the threshold).
    Zero the others and renormalize survivors to sum to 1.
    """
    raise NotImplementedError


def sample_from(probs: np.ndarray, rng: np.random.Generator, n: int) -> np.ndarray:
    """Draw n ids (shape (n,)) from `probs` with replacement using `rng`."""
    raise NotImplementedError


def sample(
    logits: np.ndarray,
    temperature: float = 1.0,
    top_k: int | None = None,
    top_p: float = 1.0,
    rng: np.random.Generator | None = None,
    n: int = 1,
) -> np.ndarray:
    """The full pipeline in canonical order: temperature -> top-k -> top-p ->
    softmax -> draw n samples."""
    raise NotImplementedError
