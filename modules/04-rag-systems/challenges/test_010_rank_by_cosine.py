import math

import pytest


def _load():
    import importlib.util

    path = __file__.replace("test_010_rank_by_cosine.py", "010_rank_by_cosine.py")
    spec = importlib.util.spec_from_file_location("chal_m4_010", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def chal():
    return _load()


class TestCosine:
    def test_identical_is_one(self, chal):
        v = [1.0, 2.0, 3.0]
        assert chal.cosine(v, v) == pytest.approx(1.0)

    def test_orthogonal_is_zero(self, chal):
        assert chal.cosine([1.0, 0.0], [0.0, 1.0]) == pytest.approx(0.0)

    def test_opposite_is_minus_one(self, chal):
        assert chal.cosine([1.0, 2.0], [-1.0, -2.0]) == pytest.approx(-1.0)

    def test_scale_invariant(self, chal):
        a = [1.0, 2.0, -0.5]
        assert chal.cosine(a, [5.0 * x for x in a]) == pytest.approx(1.0)

    def test_dimension_mismatch_raises(self, chal):
        with pytest.raises(ValueError):
            chal.cosine([1.0, 2.0], [1.0, 2.0, 3.0])

    def test_zero_vector_raises(self, chal):
        with pytest.raises(ValueError):
            chal.cosine([0.0, 0.0], [1.0, 1.0])
        with pytest.raises(ValueError):
            chal.cosine([1.0, 1.0], [0.0, 0.0])


class TestRanking:
    QUERY = [1.0, 0.0, 1.0]

    DOCS = [
        [0.9, 0.1, 0.9],   # near-duplicate direction
        [0.5, 0.5, 0.5],   # related
        [0.0, 1.0, 0.0],   # orthogonal-ish
        [0.9, 0.1, 0.9],   # exact tie with doc 0
    ]

    def test_order_and_scores(self, chal):
        ranked = chal.rank_by_cosine(self.QUERY, self.DOCS)
        assert [idx for idx, _ in ranked] == [0, 3, 1, 2]
        scores = dict(ranked)
        assert scores[0] == pytest.approx(scores[3])
        assert scores[0] > scores[1] > scores[2]

    def test_scaling_docs_does_not_change_ranks(self, chal):
        scaled = [[7.0 * x for x in doc] for doc in self.DOCS]
        assert [i for i, _ in chal.rank_by_cosine(self.QUERY, scaled)] == [
            i for i, _ in chal.rank_by_cosine(self.QUERY, self.DOCS)
        ]

    def test_all_docs_returned_best_first(self, chal):
        ranked = chal.rank_by_cosine(self.QUERY, self.DOCS)
        assert len(ranked) == len(self.DOCS)
        scores = [s for _, s in ranked]
        assert scores == sorted(scores, reverse=True)

    def test_duplicate_query_doc_scores_one(self, chal):
        ranked = chal.rank_by_cosine([3.0, -1.0], [[3.0, -1.0], [1.0, 0.0]])
        assert ranked[0][0] == 0
        assert ranked[0][1] == pytest.approx(1.0)
