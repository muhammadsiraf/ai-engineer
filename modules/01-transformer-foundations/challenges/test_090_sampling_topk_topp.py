import numpy as np
import pytest


def _load():
    import importlib.util

    path = __file__.replace("test_090_sampling_topk_topp.py", "090_sampling_topk_topp.py")
    spec = importlib.util.spec_from_file_location("chal090", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def chal():
    return _load()


class TestTemperature:
    def test_divides(self, chal):
        out = chal.apply_temperature(np.array([1.0, 2.0]), 2.0)
        assert np.allclose(out, [0.5, 1.0])

    def test_zero_gives_greedy_onehot_scores(self, chal):
        out = chal.apply_temperature(np.array([0.1, 3.0, 2.0]), 0.0)
        probs = np.exp(out - out.max())
        probs /= probs.sum()
        assert probs[1] == pytest.approx(1.0)

    def test_high_t_flattens(self, chal):
        logits = np.array([4.0, 0.0])
        p_low = np.exp(chal.apply_temperature(logits, 0.5))
        p_high = np.exp(chal.apply_temperature(logits, 5.0))
        p_low = p_low / p_low.sum()
        p_high = p_high / p_high.sum()
        assert p_low[0] > p_high[0]  # less peaked at higher T


class TestTopK:
    def test_basic(self, chal):
        out = chal.top_k_filter(np.array([1.0, 5.0, 3.0, 2.0]), 2)
        assert np.isneginf(out[0]) and np.isneginf(out[3])
        assert out[1] == 5.0 and out[2] == 3.0

    def test_k_equals_vocab_noop(self, chal):
        x = np.array([1.0, 2.0, 3.0])
        assert np.allclose(chal.top_k_filter(x, 3), x)

    def test_ties_at_cutoff_kept(self, chal):
        x = np.array([1.0, 2.0, 2.0, 2.0])
        out = chal.top_k_filter(x, 2)  # 2nd largest is 2.0, tied 3x
        assert np.isneginf(out[0])
        assert np.all(out[1:] == 2.0)

    def test_no_mutation(self, chal):
        x = np.array([1.0, 2.0, 3.0])
        chal.top_k_filter(x, 1)
        assert np.allclose(x, [1.0, 2.0, 3.0])


class TestTopP:
    def test_peaked_distribution_small_set(self, chal):
        # one token has ~all mass -> p=0.9 keeps exactly it
        probs = np.array([0.98, 0.01, 0.005, 0.005])
        out = chal.top_p_filter(probs, 0.9)
        assert out[0] == pytest.approx(1.0)
        assert np.all(out[1:] == 0.0)

    def test_flat_distribution_wide_set(self, chal):
        probs = np.full(10, 0.1)
        out = chal.top_p_filter(probs, 0.9)
        kept = int((out > 0).sum())
        assert kept == 9  # smallest set with sum >= 0.9

    def test_inclusive_threshold(self, chal):
        # 0.6 + 0.3 = 0.9 exactly -> both kept at p=0.9
        probs = np.array([0.6, 0.3, 0.1])
        out = chal.top_p_filter(probs, 0.9)
        assert (out > 0).sum() == 2
        assert out[0] == pytest.approx(2 / 3)
        assert out[1] == pytest.approx(1 / 3)
        assert out[2] == 0.0

    def test_float_tolerance(self, chal):
        # cumsum that lands at 0.89999999 must still count
        probs = np.array([0.5, 0.4, 0.1]) * (1 / 1.0000001)
        probs = probs / probs.sum()
        out = chal.top_p_filter(probs, 0.9)
        assert (out > 0).sum() >= 2

    def test_p_one_keeps_all(self, chal):
        probs = np.full(5, 0.2)
        out = chal.top_p_filter(probs, 1.0)
        assert np.allclose(out, probs)

    def test_renormalizes_to_one(self, chal):
        probs = np.array([0.5, 0.25, 0.25])
        out = chal.top_p_filter(probs, 0.5)
        assert out.sum() == pytest.approx(1.0)


class TestPipeline:
    def test_greedy_pipeline_deterministic(self, chal):
        rng = np.random.default_rng(0)
        logits = np.array([0.1, 5.0, 0.2])
        draws = chal.sample(logits, temperature=0.0, rng=rng, n=20)
        assert np.all(draws == 1)

    def test_top_k_constrains_draws(self, chal):
        rng = np.random.default_rng(1)
        logits = np.array([10.0, 9.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        draws = chal.sample(logits, temperature=1.0, top_k=2, rng=rng, n=500)
        assert set(np.unique(draws)) <= {0, 1}

    def test_top_p_constrains_draws(self, chal):
        rng = np.random.default_rng(2)
        logits = np.array([8.0, 7.5, 0.1, 0.05, 0.0, 0.0])
        draws = chal.sample(logits, temperature=1.0, top_p=0.6, rng=rng, n=500)
        assert set(np.unique(draws)) <= {0, 1}

    def test_seed_reproducibility(self, chal):
        logits = np.random.default_rng(10).normal(size=100)
        a = chal.sample(logits, temperature=0.9, top_k=40, top_p=0.95, rng=np.random.default_rng(42), n=10)
        b = chal.sample(logits, temperature=0.9, top_k=40, top_p=0.95, rng=np.random.default_rng(42), n=10)
        assert np.array_equal(a, b)

    def test_n_shape(self, chal):
        draws = chal.sample(np.zeros(5), rng=np.random.default_rng(0), n=7)
        assert draws.shape == (7,)
