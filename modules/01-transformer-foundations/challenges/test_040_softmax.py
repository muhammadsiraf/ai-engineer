import math

import numpy as np
import pytest


def _load():
    import importlib.util

    path = __file__.replace("test_040_softmax.py", "040_softmax.py")
    spec = importlib.util.spec_from_file_location("chal040", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def chal():
    return _load()


class TestBasic:
    def test_sums_to_one(self, chal):
        out = chal.softmax(np.array([1.0, 2.0, 3.0]))
        assert out.sum() == pytest.approx(1.0)

    def test_known_values(self, chal):
        out = chal.softmax(np.array([0.0, math.log(3.0)]))
        assert out[0] == pytest.approx(0.25)
        assert out[1] == pytest.approx(0.75)

    def test_order_preserved(self, chal):
        x = np.array([-1.0, 3.0, 0.5, 2.0])
        out = chal.softmax(x)
        assert np.argsort(out) == np.argsort(x)
        assert np.all(out > 0)

    def test_shift_invariance(self, chal):
        x = np.array([1.0, 2.0, 3.0])
        assert np.allclose(chal.softmax(x), chal.softmax(x + 1000.0))
        assert np.allclose(chal.softmax(x), chal.softmax(x - 1000.0))

    def test_stable_for_extreme_values(self, chal):
        out = chal.softmax(np.array([1e4, 0.0, -1e4]))
        assert np.all(np.isfinite(out))
        assert out[0] == pytest.approx(1.0)
        assert out[1] < 1e-30

    def test_2d_rows_independent(self, chal):
        x = np.array([[1.0, 2.0], [100.0, 200.0]])
        out = chal.softmax(x)
        assert out.shape == (2, 2)
        assert np.allclose(out.sum(axis=1), 1.0)
        assert np.allclose(out[0], chal.softmax(x[0]))
        assert np.allclose(out[1], chal.softmax(x[1]))


class TestMasking:
    def test_masked_positions_are_exactly_zero(self, chal):
        x = np.array([1.0, 2.0, 3.0, 4.0])
        mask = np.array([False, True, False, True])  # forbid positions 1, 3
        out = chal.softmax(x, mask=mask)
        assert out[1] == 0.0
        assert out[3] == 0.0
        assert out.sum() == pytest.approx(1.0)

    def test_mask_renormalizes(self, chal):
        x = np.array([1.0, 2.0, 3.0])
        mask = np.array([True, False, False])
        out = chal.softmax(x, mask=mask)
        # only positions 1,2 survive: ratio 2:1
        assert out[1] == pytest.approx(2 / 3)
        assert out[2] == pytest.approx(1 / 3)

    def test_causal_pattern(self, chal):
        # the actual attention use case: row i may attend to keys <= i
        x = np.random.default_rng(3).normal(size=(4, 4))
        causal = np.triu(np.ones((4, 4), dtype=bool), k=1)  # True above diagonal
        out = chal.softmax(x, mask=causal)
        assert np.allclose(np.triu(out, k=1), 0.0)
        assert np.allclose(out.sum(axis=1), 1.0)
        # row 0 can only attend to itself
        assert out[0, 0] == pytest.approx(1.0)

    def test_fully_masked_row_raises(self, chal):
        x = np.array([1.0, 2.0])
        with pytest.raises(ValueError):
            chal.softmax(x, mask=np.array([True, True]))

    def test_2d_with_partial_masks(self, chal):
        x = np.ones((3, 5))
        mask = np.zeros((3, 5), dtype=bool)
        mask[0, 2:] = True   # row 0: 2 allowed
        mask[1, 1:] = True   # row 1: 1 allowed
        out = chal.softmax(x, mask=mask)
        assert np.allclose(out[0, :2], 0.5)
        assert out[1, 0] == pytest.approx(1.0)
        assert np.allclose(out[2], 0.2)  # unmasked row is uniform
