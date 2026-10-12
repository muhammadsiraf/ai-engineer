import pytest

from importlib import import_module, util
import pathlib

HERE = pathlib.Path(__file__).parent

def _load():
    spec = util.spec_from_file_location("chal010", HERE / "010_bpe_merge_step.py")
    mod = util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def chal():
    return _load()


class TestMerge:
    def test_basic_merge(self, chal):
        assert chal.merge([1, 2, 3, 2, 3], (2, 3), 9) == [1, 9, 9]

    def test_no_occurrence(self, chal):
        assert chal.merge([1, 2, 3], (5, 6), 9) == [1, 2, 3]

    def test_overlapping_triple(self, chal):
        # [a,a,a] with target (a,a) -> merge positions 0-1, continue after
        assert chal.merge(["a", "a", "a"], ("a", "a"), "AA") == ["AA", "a"]

    def test_overlapping_quad(self, chal):
        assert chal.merge(["a", "a", "a", "a"], ("a", "a"), "AA") == ["AA", "AA"]

    def test_chained_merge_not_recursive(self, chal):
        # after merging (1,2)->9, the new 9 must NOT merge with a following 9-target
        assert chal.merge([1, 2, 3], (1, 2), 3) == [3, 3]
        assert chal.merge([1, 2, 1, 2], (1, 2), (1, 2)) == [(1, 2), (1, 2)]

    def test_input_not_mutated(self, chal):
        ids = [1, 2, 3]
        chal.merge(ids, (1, 2), 9)
        assert ids == [1, 2, 3]

    def test_empty(self, chal):
        assert chal.merge([], (1, 2), 9) == []


class TestMostFrequentPair:
    def test_simple(self, chal):
        assert chal.most_frequent_pair([1, 2, 3, 1, 2]) == (1, 2)

    def test_tie_goes_to_earliest_first_occurrence(self, chal):
        # (1,2) occurs once at pos 0; (2,3) occurs once at pos 1 -> (1,2) wins
        assert chal.most_frequent_pair([1, 2, 3]) == (1, 2)

    def test_overlapping_counts(self, chal):
        assert chal.most_frequent_pair(["a", "a", "a"]) == ("a", "a")

    def test_short_sequences(self, chal):
        assert chal.most_frequent_pair([]) is None
        assert chal.most_frequent_pair([1]) is None

    def test_full_bpe_roundtrip(self, chal):
        # simulate two training merge steps
        ids = [5, 6, 5, 6, 5, 6, 7]
        pair = chal.most_frequent_pair(ids)          # (5, 6)
        ids = chal.merge(ids, pair, 99)              # [99, 99, 99, 7]
        assert ids == [99, 99, 99, 7]
        pair2 = chal.most_frequent_pair(ids)         # (99, 99) occurs twice
        ids = chal.merge(ids, pair2, 100)            # [100, 99, 7]
        assert ids == [100, 99, 7]
