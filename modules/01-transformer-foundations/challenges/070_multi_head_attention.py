"""Challenge 070 — Implement multi-head attention.

Lesson: 120-multi-head-attention-the-one-sentence-version

Split d_model into h heads of d_head = d_model / h dims each; run independent
causal attention per head on its slice; concatenate head outputs; apply the
final output projection Wo.

    Q,K,V = X @ Wq, X @ Wk, X @ Wv        # (n, d_model) each
    per head i (slice [i*dh : (i+1)*dh]):
        A_i = softmax(Q_i @ K_i^T / sqrt(dh), causal)
        out_i = A_i @ V_i
    output = concat(out_0..out_h-1) @ Wo   # (n, d_model)

You may reuse `self_attention` from challenge 050 by importing it, or
re-implement inline. Tests verify both the slicing mechanics and the
properties (shape, causality, heads-differ, Wo-mixing).

Run:  pytest modules/01-transformer-foundations/challenges/test_070_multi_head_attention.py -v
"""

import numpy as np


def multi_head_attention(
    X: np.ndarray,
    Wq: np.ndarray,
    Wk: np.ndarray,
    Wv: np.ndarray,
    Wo: np.ndarray,
    n_heads: int,
    causal: bool = True,
) -> np.ndarray:
    """Multi-head causal self-attention.

    Args:
        X: (n, d_model).
        Wq, Wk, Wv: (d_model, d_model) projections.
        Wo: (d_model, d_model) final output projection.
        n_heads: h; must divide d_model evenly.
        causal: passed through to each head's attention.

    Returns:
        (n, d_model).

    Raises:
        ValueError: if d_model not divisible by n_heads.
    """
    raise NotImplementedError
