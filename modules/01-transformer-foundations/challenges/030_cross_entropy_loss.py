"""Challenge 030 — Implement cross-entropy loss.

Lesson: 070-what-training-actually-does

Cross-entropy is THE loss of language modeling:

    loss = -log( p(target) )

where p(target) is the probability the model assigned to the correct next
token. This challenge has you implement it from logits, the numerically-stable
way (the same trick PyTorch's F.cross_entropy uses internally).

The stable recipe (log-sum-exp):
    log_softmax(x)_i = x_i - max(x) - log(sum(exp(x - max(x))))
    loss             = -log_softmax(x)[target]

Subtracting max(x) before exp prevents overflow when logits are large.
If you skip it, your tests WILL fail on the large-logit case — that's the point.

Also implement `perplexity`: exp(mean cross-entropy over a sequence).
Perplexity answers "how many tokens is the model effectively choosing between?"

Run:  pytest modules/01-transformer-foundations/challenges/test_030_cross_entropy_loss.py -v
"""

import numpy as np


def cross_entropy(logits: np.ndarray, target: int) -> float:
    """Cross-entropy between raw logits (shape: [vocab]) and a target index.

    Must be numerically stable for large logits (e.g., 1e4).
    """
    raise NotImplementedError


def batch_cross_entropy(logits: np.ndarray, targets: np.ndarray) -> float:
    """Mean cross-entropy over a batch.

    Args:
        logits: (batch, vocab) raw scores. Row t is the prediction for
                position t.
        targets: (batch,) int array of correct next-token ids.

    Language-modeling subtlety this must handle: position t's PREDICTION is
    compared against target at position t, and callers pass logits already
    aligned with targets (i.e., logits[t] should predict targets[t]).
    """
    raise NotImplementedError


def perplexity(logits: np.ndarray, targets: np.ndarray) -> float:
    """exp(mean cross-entropy) over the batch — the 'effective vocabulary size'."""
    raise NotImplementedError
