import numpy as np
import pytest


def _load():
    import importlib.util

    path = __file__.replace("test_060_causal_mask.py", "060_causal_mask.py")
    spec = importlib.util.spec_from_file_location("chal060", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def chal():
    return _load()


class TestCausalMask:
    def test_shape_and_dtype(self, chal):
        m = chal.causal_mask(4)
        assert m.shape == (4, 4)
        assert m.dtype == bool

    def test_lower_triangular_pattern(self, chal):
        m = chal.causal_mask(4)
        expected = np.array(
            [
                [False, True, True, True],
                [False, False, True, True],
                [False, False, False, True],
                [False, False, False, False],
            ]
        )
        assert np.array_equal(m, expected)

    def test_diagonal_always_allowed(self, chal):
        for n in (1, 2, 7, 33):
            assert not np.any(np.diag(chal.causal_mask(n)))

    def test_n1(self, chal):
        assert np.array_equal(chal.causal_mask(1), np.array([[False]]))


class TestApplyCausalMask:
    def test_future_positions_negative_inf(self, chal):
        scores = np.arange(16, dtype=float).reshape(4, 4)
        out = chal.apply_causal_mask(scores)
        expected_future = np.triu(np.ones((4, 4)), k=1).astype(bool)
        assert np.all(np.isneginf(out[expected_future]))

    def test_allowed_positions_untouched(self, chal):
        scores = np.arange(16, dtype=float).reshape(4, 4)
        out = chal.apply_causal_mask(scores)
        allowed = ~np.triu(np.ones((4, 4)), k=1).astype(bool)
        assert np.array_equal(out[allowed], scores[allowed])

    def test_input_not_mutated(self, chal):
        scores = np.ones((3, 3))
        original = scores.copy()
        chal.apply_causal_mask(scores)
        assert np.array_equal(scores, original)

    def test_softmax_after_mask_is_causal(self, chal):
        # end-to-end sanity: masked scores -> softmax rows put zero mass on future
        rng = np.random.default_rng(2)
        scores = rng.normal(size=(5, 5)) * 10
        masked = chal.apply_causal_mask(scores)
        e = np.exp(masked - masked.max(axis=-1, keepdims=True))
        probs = e / e.sum(axis=-1, keepdims=True)
        assert np.allclose(np.triu(probs, k=1), 0.0)
        assert np.allclose(probs.sum(axis=1), 1.0)

    def test_extreme_scores_stable(self, chal):
        scores = np.array([[1e8, 1e8], [1e8, 1e8]])
        out = chal.apply_causal_mask(scores)
        assert np.isfinite(out[0, 0]) and np.isneginf(out[0, 1])


class TestCausalMaskFor:
    def test_documented_example(self, chal):
        expected = np.array(
            [
                [False, False, True, True, True],
                [False, False, False, True, True],
                [False, False, False, False, True],
            ]
        )
        assert np.array_equal(chal.causal_mask_for(2, 3), expected)

    def test_no_cache_equals_plain_mask(self, chal):
        assert np.array_equal(chal.causal_mask_for(0, 4), chal.causal_mask(4))

    def test_pure_decode_single_token(self, chal):
        # generating ONE new token with a full cache: nothing is masked
        m = chal.causal_mask_for(10, 1)
        assert m.shape == (1, 11)
        assert not np.any(m)

    def test_all_shapes(self, chal):
        for cached, new in [(0, 1), (1, 1), (3, 2), (7, 4)]:
            m = chal.causal_mask_for(cached, new)
            assert m.shape == (new, cached + new)
            for i in range(new):
                abs_pos = cached + i
                # forbidden iff absolute key position > absolute query position
                expected_row = np.zeros(cached + new, dtype=bool)
                expected_row[abs_pos + 1 :] = True
                assert np.array_equal(m[i], expected_row), (cached, new, i)
