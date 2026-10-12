"""Challenge 080 — Generate tokens autoregressively.

Lesson: 130-generation-is-autoregressive

The generation loop of lesson 130, implemented against a mock language model:

    tokens = list(prompt)
    loop:
        logits = model.logits(tokens)        # (vocab,) for the NEXT token
        next_id = sample_fn(logits)          # your choice: greedy or random
        append; stop on EOS or max_new_tokens

The mock model is provided (`BigramStyleLM`): its "learned" transition table
makes tests deterministic. Your job is the LOOP mechanics — condition on
everything so far, append exactly one token per step, honor stop conditions,
and never exceed the budget.

Critical detail: `model.logits(tokens)` must receive the FULL sequence each
iteration (that's the stateless contract from lesson 020 — the model has no
memory; the loop IS the memory).

Run:  pytest modules/01-transformer-foundations/challenges/test_080_autoregressive_generation.py -v
"""

from typing import Callable

import numpy as np

EOS = 0  # the mock model's end-of-sequence token id


class BigramStyleLM:
    """A fake 'language model' with a fixed next-token table.

    logits(tokens) returns scores for the next token given the FULL token
    history (only the last token matters for this mock — like a bigram model).
    Provided for you; do not modify.
    """

    def __init__(self, vocab_size: int = 10, seed: int = 0):
        rng = np.random.default_rng(seed)
        self.vocab_size = vocab_size
        self.table = rng.normal(size=(vocab_size, vocab_size))
        self.table[:, EOS] -= 2.0  # make EOS rarer
        self.calls: list[int] = []

    def logits(self, tokens: list[int]) -> np.ndarray:
        if not tokens:
            raise ValueError("need at least one token")
        self.calls.append(len(tokens))
        return self.table[tokens[-1]]


def generate(
    model: BigramStyleLM,
    prompt: list[int],
    max_new_tokens: int,
    sample_fn: Callable[[np.ndarray], int],
) -> list[int]:
    """Autoregressive generation.

    Args:
        model: object exposing .logits(list[int]) -> (vocab,) scores.
        prompt: initial token ids (non-empty).
        max_new_tokens: hard cap on generated (not prompt) tokens.
        sample_fn: function (logits) -> chosen token id. Greedy, sampled —
                   your implementation is injected here.

    Returns:
        prompt + generated tokens. Stops early (without appending) if the
        sampled token is EOS.
    """
    raise NotImplementedError


def greedy(logits: np.ndarray) -> int:
    """Argmax sampling. Ties: lowest id wins (np.argmax behavior)."""
    raise NotImplementedError
