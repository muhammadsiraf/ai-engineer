import pytest


def _load():
    import importlib.util

    path = __file__.replace("test_050_measure_recall_precision.py", "050_measure_recall_precision.py")
    spec = importlib.util.spec_from_file_location("chal_m4_050", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def chal():
    return _load()


RELEVANT = {"d1", "d2", "d3", "d4"}
RETRIEVED = ["d7", "d2", "d1", "d9", "d5", "d6", "d8", "d10", "d11", "d3"]


class TestRecall:
    def test_lesson_scenario(self, chal):
        # d2, d1, d3 found in top-10; d4 missing
        assert chal.recall_at_k(RETRIEVED, RELEVANT, 10) == pytest.approx(0.75)

    def test_perfect(self, chal):
        assert chal.recall_at_k(["a", "b"], {"a", "b"}, 2) == 1.0

    def test_k_truncates(self, chal):
        # top-3 only: d2, d1 → 2/4
        assert chal.recall_at_k(RETRIEVED, RELEVANT, 3) == pytest.approx(0.5)

    def test_relevant_beyond_k_counts_zero(self, chal):
        assert chal.recall_at_k(RETRIEVED, RELEVANT, 1) == 0.0

    def test_empty_relevant_is_zero(self, chal):
        assert chal.recall_at_k(RETRIEVED, set(), 5) == 0.0

    def test_bad_k_raises(self, chal):
        with pytest.raises(ValueError):
            chal.recall_at_k(RETRIEVED, RELEVANT, 0)


class TestPrecision:
    def test_lesson_scenario(self, chal):
        assert chal.precision_at_k(RETRIEVED, RELEVANT, 10) == pytest.approx(0.3)

    def test_perfect(self, chal):
        assert chal.precision_at_k(["a", "b", "c"], {"a", "b"}, 2) == 1.0

    def test_denominator_is_returned_not_k(self, chal):
        # only 2 docs retrieved, both relevant, k=5 → 2/2 not 2/5
        assert chal.precision_at_k(["a", "b"], {"a", "b"}, 5) == 1.0

    def test_precision_order_sensitive(self, chal):
        # same hits, better placement → higher precision@2
        good = chal.precision_at_k(["d1", "d2", "d7", "d9"], RELEVANT, 2)
        bad = chal.precision_at_k(["d7", "d9", "d1", "d2"], RELEVANT, 2)
        assert good == pytest.approx(1.0)
        assert bad == 0.0
        assert good > bad

    def test_empty_relevant_is_zero(self, chal):
        assert chal.precision_at_k(RETRIEVED, set(), 5) == 0.0


class TestMRR:
    def test_first_hit_at_rank_two(self, chal):
        assert chal.mrr(["d7", "d2", "d9"], RELEVANT) == pytest.approx(0.5)

    def test_first_position(self, chal):
        assert chal.mrr(["d3", "d8"], RELEVANT) == 1.0

    def test_no_hit(self, chal):
        assert chal.mrr(["d7", "d9"], RELEVANT) == 0.0

    def test_empty_retrieved(self, chal):
        assert chal.mrr([], RELEVANT) == 0.0


class TestCurve:
    def test_recall_monotone_in_k(self, chal):
        recalls = [chal.recall_at_k(RETRIEVED, RELEVANT, k) for k in range(1, 11)]
        assert recalls == sorted(recalls)

    def test_reranker_shape(self, chal):
        # recall@50 high but recall@5 low → reranker territory (lesson 090)
        pool = ["d1", "d2", "d3", "d4"] + [f"junk{i}" for i in range(46)]
        assert chal.recall_at_k(pool, {"d1", "d2", "d3", "d4"}, 50) == 1.0
        assert chal.recall_at_k(pool, {"d1", "d2", "d3", "d4"}, 5) == 1.0
        bad_order = [f"junk{i}" for i in range(46)] + ["d1", "d2", "d3", "d4"]
        assert chal.recall_at_k(bad_order, {"d1", "d2", "d3", "d4"}, 50) == 1.0
        assert chal.recall_at_k(bad_order, {"d1", "d2", "d3", "d4"}, 5) == 0.0
