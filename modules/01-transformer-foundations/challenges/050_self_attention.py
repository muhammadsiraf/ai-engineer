"""Challenge 050 — Implement self-attention.

Lesson: 100-self-attention-in-five-minutes

The heart of the transformer, in NumPy:

    A      = softmax( (Q @ K^T) / sqrt(dk), mask=causal )   # (n, n)
    output = A @ V                                          # (n, dv)

Your `self_attention` takes raw token embeddings X and weight matrices, builds
Q/K/V by linear projection, runs scaled dot-product attention with a causal
mask (reusing your softmax from challenge 040 — a copy is provided in
`_reference_softmax` if you skipped it), and returns the mixed values.

NOTE: no final output projection Wo here — that's part of challenge 070's
multi-head. Keep this one pure: projections in, attention mix out.

Shapes to be strict about:
    X           (n, d_model)
    Wq, Wk      (d_model, d_k)
    Wv          (d_model, d_v)
    output      (n, d_v)

Run:  pytest modules/01-transformer-foundations/challenges/test_050_self_attention.py -v
"""

import numpy as np


def _reference_softmax(x: np.ndarray, mask: np.ndarray | None = None) -> np.ndarray:
    """Stable softmax over the last axis. Available for you to reuse."""
    if mask is not None:
        x = np.where(mask, -np.inf, x)
    x = x - x.max(axis=-1, keepdims=True)
    e = np.exp(x)
    out = e / e.sum(axis=-1, keepdims=True)
    return np.where(mask, 0.0, out) if mask is not None else out


def self_attention(
    X: np.ndarray,
    Wq: np.ndarray,
    Wk: np.ndarray,
    Wv: np.ndarray,
    causal: bool = True,
) -> np.ndarray:
    """Single-head scaled dot-product self-attention.

    Args:
        X: (n, d_model) input embeddings, row i = token i.
        Wq: (d_model, d_k) query projection.
        Wk: (d_model, d_k) key projection.
        Wv: (d_model, d_v) value projection.
        causal: if True, token i may not attend to tokens > i.

    Returns:
        (n, d_v) array: each token's context-mixed value vector.
    """
    raise NotImplementedError
