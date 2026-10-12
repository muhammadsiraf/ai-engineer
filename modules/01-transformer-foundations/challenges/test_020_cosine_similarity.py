import numpy as np
import pytest


def _load():
    import importlib.util

    here = importlib.util.spec_from_file_location(
        "chal020", __file__.replace("test_020_cosine_similarity.py", "020_cosine_similarity.py")
    )
    mod = importlib.util.module_from_spec(here)
    here.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def chal():
    return _load()


class TestCosineSim:
    def test_identical_vectors(self, chal):
        a = np.array([1.0, 2.0, 3.0])
        assert chal.cosine_sim(a, a) == pytest.approx(1.0)

    def test_opposite_vectors(self, chal):
        a = np.array([1.0, 2.0])
        assert chal.cosine_sim(a, -a) == pytest.approx(-1.0)

    def test_orthogonal_vectors(self, chal):
        a = np.array([1.0, 0.0])
        b = np.array([0.0, 5.0])
        assert chal.cosine_sim(a, b) == pytest.approx(0.0)

    def test_scale_invariance(self, chal):
        a = np.array([1.0, 2.0, 3.0])
        assert chal.cosine_sim(a, 100 * a) == pytest.approx(1.0)
        assert chal.cosine_sim(a, 0.001 * a) == pytest.approx(1.0)

    def test_known_value(self, chal):
        # 60 degrees -> 0.5
        a = np.array([1.0, 0.0])
        b = np.array([0.5, np.sqrt(3) / 2])
        assert chal.cosine_sim(a, b) == pytest.approx(0.5)

    def test_zero_vector_returns_zero(self, chal):
        a = np.array([0.0, 0.0])
        b = np.array([1.0, 2.0])
        assert chal.cosine_sim(a, b) == 0.0
        assert chal.cosine_sim(b, a) == 0.0
        assert chal.cosine_sim(a, a) == 0.0

    def test_float64_stability(self, chal):
        # huge values would overflow float32 dot products
        a = np.array([1e150, 1e150])
        b = np.array([1e150, 0.0])
        result = chal.cosine_sim(a, b)
        assert np.isfinite(result)
        assert result == pytest.approx(np.sqrt(2) / 2, rel=1e-6)


class TestTopKSimilar:
    @pytest.fixture()
    def docs(self):
        rng = np.random.default_rng(42)
        base = rng.normal(size=(10, 8))
        base[3] = base[0] * 2.5  # doc 3 is a scaled copy of doc 0
        return base

    def test_ranking_and_order(self, chal, docs):
        q = docs[0] + 0.01
        results = chal.top_k_similar(q, docs, 3)
        assert len(results) == 3
        idxs = [i for i, _ in results]
        assert idxs[0] == 0
        assert set(idxs[1:]) <= {3, *range(1, 10)}
        scores = [s for _, s in results]
        assert scores == sorted(scores, reverse=True)

    def test_k_exceeds_n(self, chal, docs):
        results = chal.top_k_similar(docs[0], docs, 99)
        assert len(results) == 10

    def test_scores_match_direct_computation(self, chal, docs):
        results = chal.top_k_similar(docs[1], docs, 1)
        idx, score = results[0]
        assert idx == 1
        assert score == pytest.approx(1.0)


class TestMatrix:
    def test_shape_and_diagonal(self, chal):
        rng = np.random.default_rng(0)
        v = rng.normal(size=(7, 4))
        m = chal.cosine_sim_matrix(v)
        assert m.shape == (7, 7)
        assert np.allclose(np.diag(m), 1.0)
        assert np.allclose(m, m.T)

    def test_symmetric_values(self, chal):
        v = np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]])
        m = chal.cosine_sim_matrix(v)
        assert m[0, 2] == pytest.approx(np.sqrt(2) / 2)
        assert m[2, 0] == pytest.approx(np.sqrt(2) / 2)

    def test_zero_row(self, chal):
        v = np.array([[0.0, 0.0], [1.0, 2.0]])
        m = chal.cosine_sim_matrix(v)
        assert np.all(m[0] == 0.0)
        assert np.all(m[:, 0] == 0.0)
        assert m[1, 1] == pytest.approx(1.0)
