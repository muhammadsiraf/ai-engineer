import numpy as np
import pytest


def _load():
    import importlib.util

    path = __file__.replace("test_050_self_attention.py", "050_self_attention.py")
    spec = importlib.util.spec_from_file_location("chal050", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def chal():
    return _load()


@pytest.fixture()
def small():
    rng = np.random.default_rng(0)
    return dict(
        X=rng.normal(size=(5, 8)),
        Wq=rng.normal(size=(8, 4)) * 0.3,
        Wk=rng.normal(size=(8, 4)) * 0.3,
        Wv=rng.normal(size=(8, 6)) * 0.3,
    )


class TestShapesAndBasics:
    def test_output_shape(self, chal, small):
        out = chal.self_attention(**small)
        assert out.shape == (5, 6)

    def test_different_dv(self, chal, small):
        s = dict(small)
        s["Wv"] = np.random.default_rng(1).normal(size=(8, 3)) * 0.3
        assert chal.self_attention(**s).shape == (5, 3)

    def test_finite_output(self, chal, small):
        assert np.all(np.isfinite(chal.self_attention(**small)))


class TestCausality:
    def test_token0_independent_of_future(self, chal, small):
        X = small["X"].copy()
        out_a = chal.self_attention(X, small["Wq"], small["Wk"], small["Wv"], causal=True)
        X[1:] = 999.0  # clobber the future
        out_b = chal.self_attention(X, small["Wq"], small["Wk"], small["Wv"], causal=True)
        assert np.allclose(out_a[0], out_b[0])

    def test_token_i_independent_of_strictly_later_tokens(self, chal, small):
        X = small["X"].copy()
        out_a = chal.self_attention(X, small["Wq"], small["Wk"], small["Wv"], causal=True)
        X[3:] = -500.0
        out_b = chal.self_attention(X, small["Wq"], small["Wk"], small["Wv"], causal=True)
        assert np.allclose(out_a[:2], out_b[:2])

    def test_last_token_depends_on_all(self, chal, small):
        X = small["X"].copy()
        out_a = chal.self_attention(X, small["Wq"], small["Wk"], small["Wv"], causal=True)
        X[2, :] += 5.0  # perturb a middle token
        out_b = chal.self_attention(X, small["Wq"], small["Wk"], small["Wv"], causal=True)
        assert not np.allclose(out_a[-1], out_b[-1])

    def test_non_causal_allows_lookahead(self, chal, small):
        X = small["X"].copy()
        out_a = chal.self_attention(X, small["Wq"], small["Wk"], small["Wv"], causal=False)
        X[1:] = 999.0
        out_b = chal.self_attention(X, small["Wq"], small["Wk"], small["Wv"], causal=False)
        assert not np.allclose(out_a[0], out_b[0])


class TestMechanics:
    def test_matches_manual_computation(self, chal, small):
        X, Wq, Wk, Wv = small["X"], small["Wq"], small["Wk"], small["Wv"]
        n, dk = X.shape[0], Wq.shape[1]
        Q, K, V = X @ Wq, X @ Wk, X @ Wv
        scores = Q @ K.T / np.sqrt(dk)
        mask = np.triu(np.ones((n, n), dtype=bool), k=1)
        A = chal._reference_softmax(scores, mask)
        expected = A @ V
        assert np.allclose(chal.self_attention(X, Wq, Wk, Wv, causal=True), expected)

    def test_identity_projection_uniform_attention_blend(self, chal):
        # With tiny weights, attention ~ uniform over allowed positions.
        # For token 0 (causal), output ~= V[0] exactly.
        rng = np.random.default_rng(5)
        X = rng.normal(size=(4, 6))
        Wq = np.zeros((6, 6))
        Wk = np.zeros((6, 6))
        Wv = np.eye(6)
        out = chal.self_attention(X, Wq, Wk, Wv, causal=True)
        # token 0: only itself -> V[0] = X[0]
        assert np.allclose(out[0], X[0])

    def test_zero_qk_gives_uniform_over_past(self, chal):
        rng = np.random.default_rng(9)
        X = rng.normal(size=(3, 4))
        Wq = np.zeros((4, 4))
        Wk = np.zeros((4, 4))
        Wv = np.eye(4)
        out = chal.self_attention(X, Wq, Wk, Wv, causal=True)
        # token 2 attends uniformly over tokens 0,1,2
        assert np.allclose(out[2], X[:3].mean(axis=0))
