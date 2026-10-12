import numpy as np
import pytest


def _load():
    import importlib.util

    path = __file__.replace("test_070_multi_head_attention.py", "070_multi_head_attention.py")
    spec = importlib.util.spec_from_file_location("chal070", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def chal():
    return _load()


@pytest.fixture()
def setup():
    rng = np.random.default_rng(11)
    d, n, h = 8, 4, 2
    scale = 0.5
    return dict(
        X=rng.normal(size=(n, d)),
        Wq=rng.normal(size=(d, d)) * scale,
        Wk=rng.normal(size=(d, d)) * scale,
        Wv=rng.normal(size=(d, d)) * scale,
        Wo=rng.normal(size=(d, d)) * scale,
        n_heads=h,
    )


class TestBasics:
    def test_shape(self, chal, setup):
        assert chal.multi_head_attention(**setup).shape == (4, 8)

    def test_indivisible_heads_raises(self, chal, setup):
        setup["n_heads"] = 3
        with pytest.raises(ValueError):
            chal.multi_head_attention(**setup)

    def test_finite(self, chal, setup):
        assert np.all(np.isfinite(chal.multi_head_attention(**setup)))


class TestCausality:
    def test_token0_independent_of_future(self, chal, setup):
        X = setup["X"].copy()
        out_a = chal.multi_head_attention(**{**setup, "X": X})
        X[1:] = 12345.0
        out_b = chal.multi_head_attention(**{**setup, "X": X})
        assert np.allclose(out_a[0], out_b[0])

    def test_prefix_property(self, chal, setup):
        X = setup["X"].copy()
        out_a = chal.multi_head_attention(**{**setup, "X": X})
        X[2:] = -777.0
        out_b = chal.multi_head_attention(**{**setup, "X": X})
        assert np.allclose(out_a[:2], out_b[:2])


class TestMechanics:
    def test_single_head_matches_manual(self, chal, setup):
        setup["n_heads"] = 1
        X, Wq, Wk, Wv, Wo = (setup[k] for k in ("X", "Wq", "Wk", "Wv", "Wo"))
        d = X.shape[1]
        Q, K, V = X @ Wq, X @ Wk, X @ Wv
        n = X.shape[0]
        scores = Q @ K.T / np.sqrt(d)
        mask = np.triu(np.ones((n, n), dtype=bool), k=1)
        scores = np.where(mask, -np.inf, scores)
        e = np.exp(scores - scores.max(axis=-1, keepdims=True))
        A = e / e.sum(axis=-1, keepdims=True)
        expected = (A @ V) @ Wo
        assert np.allclose(chal.multi_head_attention(**setup), expected)

    def test_heads_differ_from_moved_axis(self, chal, setup):
        # permutation of the d_model axes is NOT a no-op: heads slice fixed
        # ranges, so shuffling columns must change the result (almost surely)
        out_a = chal.multi_head_attention(**setup)
        perm = np.random.default_rng(3).permutation(8)
        s = {**setup}
        for k in ("Wq", "Wk", "Wv", "Wo"):
            s[k] = s[k][perm][:, perm]
        out_b = chal.multi_head_attention(**s)
        assert not np.allclose(out_a, out_b)

    def test_two_heads_equal_manual_blockwise(self, chal, setup):
        X, Wq, Wk, Wv, Wo = (setup[k] for k in ("X", "Wq", "Wk", "Wv", "Wo"))
        n, d = X.shape
        h, dh = setup["n_heads"], d // setup["n_heads"]

        def head(i):
            Q, K, V = X @ Wq[:, i * dh : (i + 1) * dh], X @ Wk[:, i * dh : (i + 1) * dh], X @ Wv[:, i * dh : (i + 1) * dh]
            scores = Q @ K.T / np.sqrt(dh)
            mask = np.triu(np.ones((n, n), dtype=bool), k=1)
            scores = np.where(mask, -np.inf, scores)
            e = np.exp(scores - scores.max(axis=-1, keepdims=True))
            A = e / e.sum(axis=-1, keepdims=True)
            return A @ V

        concat = np.concatenate([head(i) for i in range(h)], axis=-1)
        expected = concat @ Wo
        assert np.allclose(chal.multi_head_attention(**setup), expected)

    def test_identity_weights_pass_value_through(self, chal):
        # Wq=0, Wk=0 -> uniform attention per head; Wv=Wo=I -> mean of past tokens
        n, d, h = 3, 4, 2
        X = np.arange(n * d, dtype=float).reshape(n, d)
        out = chal.multi_head_attention(X, np.zeros((d, d)), np.zeros((d, d)), np.eye(d), np.eye(d), n_heads=h)
        assert np.allclose(out[0], X[0])
        assert np.allclose(out[2], X[:3].mean(axis=0))
