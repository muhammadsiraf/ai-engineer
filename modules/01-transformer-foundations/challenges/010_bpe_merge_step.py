"""Challenge 010 — One BPE merge step.

Lesson: 030-tokens-what-one-token-actually-is

Byte-Pair Encoding builds its vocabulary by repeatedly merging the most
frequent adjacent token pair. Your job: implement ONE merge step, faithfully.

The algorithm for a single merge (target, ids) -> new ids:
  1. Scan the sequence left to right.
  2. Everywhere `ids[i] == target[0]` and `ids[i+1] == target[1]`, replace the
     pair with `new_id`.
  3. Merges are greedy and left-to-right, and overlapping occurrences must not
     double-count. Example: merging ('a','a') in [a, a, a] yields
     [AA, a] — the third `a` is NOT merged (it was consumed as part of the
     first pair's right element... careful: scan left to right, after merging
     positions 0-1 you continue scanning from position after the merged token).
  4. Return a NEW list; do not mutate the input.

Work with symbols as hashable tokens (strings or ints both fine).

Run:  pytest modules/01-transformer-foundations/challenges/test_010_bpe_merge_step.py -v
"""

from typing import Hashable, Sequence


def merge(ids: Sequence[Hashable], target: tuple[Hashable, Hashable], new_id: Hashable) -> list[Hashable]:
    """Replace every (non-overlapping, left-to-right) occurrence of `target`
    in `ids` with `new_id`.

    Args:
        ids: sequence of tokens.
        target: the (left, right) pair to merge.
        new_id: token to substitute for each merged pair.

    Returns:
        A new list with merges applied.
    """
    raise NotImplementedError


def most_frequent_pair(ids: Sequence[Hashable]) -> tuple[Hashable, Hashable] | None:
    """Return the adjacent pair that occurs most often in `ids`.

    Ties: return the pair whose FIRST occurrence appears earliest in `ids`.
    Overlaps count: in [a, a, a], pair ('a','a') occurs twice (positions 0-1
    and 1-2).
    Returns None for sequences shorter than 2.
    """
    raise NotImplementedError
