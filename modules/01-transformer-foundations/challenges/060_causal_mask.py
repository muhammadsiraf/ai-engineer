"""Challenge 060 — Apply a causal mask.

Lesson: 110-why-attention-is-causal-at-inference-time

The causal mask is a correctness guarantee: position i may attend to positions
<= i only. In production code it appears as either (a) a boolean mask fed to a
masked softmax, or (b) adding -inf to future scores before softmax. You'll
implement both, plus a KV-cache-aware variant that real serving engines need.

Key subtlety: the KV-cache variant. When generating token n+1 with a cache of
n previous tokens, the NEW query's scores have shape (1, n+1) — it may attend
to ALL n cached positions plus itself. There is nothing to mask. Masks are
needed only when processing multiple positions at once. `causal_mask_for`
builds the right mask for that situation.

Run:  pytest modules/01-transformer-foundations/challenges/test_060_causal_mask.py -v
"""

import numpy as np


def causal_mask(n: int) -> np.ndarray:
    """Boolean (n, n) mask; True = FORBIDDEN.

    mask[i, j] is True iff j > i. Diagonal is always allowed.
    """
    raise NotImplementedError


def apply_causal_mask(scores: np.ndarray) -> np.ndarray:
    """Return a copy of (n, n) scores with future positions set to -inf.

    Must not mutate the input. Assume scores is square; assume nothing about
    their values (they can be huge, tiny, NaN-free floats).
    """
    raise NotImplementedError


def causal_mask_for(n_cached: int, n_new: int) -> np.ndarray:
    """Mask for processing n_new fresh queries when n_cached tokens came before.

    Query rows are the n_new tokens at absolute positions
    n_cached .. n_cached+n_new-1. Key columns are ALL n_cached+n_new tokens.

    Shape: (n_new, n_cached + n_new). True = forbidden.
    Example: n_cached=2, n_new=3 ->
        [[F F T T T]     absolute position 2 sees keys 0,1,2
         [F F F T T]     position 3 sees keys 0..3
         [F F F F T]]    position 4 sees keys 0..4
    """
    raise NotImplementedError
