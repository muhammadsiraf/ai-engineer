import math

import numpy as np
import pytest


def _load():
    import importlib.util

    path = __file__.replace("test_030_cross_entropy_loss.py", "030_cross_entropy_loss.py")
    spec = importlib.util.spec_from_file_location("chal030", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def chal():
    return _load()


class TestCrossEntropy:
    def test_uniform_logits_equal_log_vocab(self, chal):
        logits = np.zeros(1000)
        for target in (0, 499, 999):
            assert chal.cross_entropy(logits, target) == pytest.approx(math.log(1000), rel=1e-9)

    def test_confident_correct_prediction(self, chal):
        logits = np.array([0.1, 5.0, 0.1, -3.0])
        assert chal.cross_entropy(logits, 1) == pytest.approx(0.078889, abs=1e-4)

    def test_confident_wrong_prediction(self, chal):
        logits = np.array([5.0, 0.1])
        # p(target=1) = e^0.1 / (e^5 + e^0.1)
        expected = -math.log(math.exp(0.1) / (math.exp(5.0) + math.exp(0.1)))
        assert chal.cross_entropy(logits, 1) == pytest.approx(expected)

    def test_matches_naive_definition(self, chal):
        rng = np.random.default_rng(7)
        logits = rng.normal(size=50)
        target = 17
        probs = np.exp(logits) / np.exp(logits).sum()
        naive = -math.log(probs[target])
        assert chal.cross_entropy(logits, target) == pytest.approx(naive, rel=1e-9)

    def test_stable_for_huge_logits(self, chal):
        logits = np.array([1e4, 1e4 - 5, 0.0])
        value = chal.cross_entropy(logits, 1)
        assert math.isfinite(value)
        # gap of 5 between top-2 -> loss ~ 5 + log(1 + e^-5)
        assert value == pytest.approx(5.0 + math.log(1 + math.exp(-5.0)), abs=1e-4)

    def test_stable_for_very_negative(self, chal):
        logits = np.array([-1e4, -1e4, 0.0])
        value = chal.cross_entropy(logits, 2)
        assert math.isfinite(value)
        assert value == pytest.approx(0.0, abs=1e-6)


class TestBatch:
    def test_mean_over_batch(self, chal):
        logits = np.array([[0.0, 0.0], [math.log(4), 0.0]])
        targets = np.array([0, 0])
        # row 0: log(2); row 1: p(0) = 4/5 -> -log(4/5)
        expected = (math.log(2) - math.log(0.8)) / 2
        assert chal.batch_cross_entropy(logits, targets) == pytest.approx(expected)

    def test_single_row(self, chal):
        logits = np.array([[0.1, 5.0, 0.1]])
        targets = np.array([1])
        assert chal.batch_cross_entropy(logits, targets) == pytest.approx(
            chal.cross_entropy(logits[0], 1)
        )


class TestPerplexity:
    def test_uniform_1000_vocab(self, chal):
        logits = np.zeros((3, 1000))
        targets = np.array([1, 500, 999])
        assert chal.perplexity(logits, targets) == pytest.approx(1000.0, rel=1e-9)

    def test_perfect_model(self, chal):
        # massive logit on the target -> ppl ~ 1
        logits = np.full((2, 10), -100.0)
        logits[0, 3] = 100.0
        logits[1, 7] = 100.0
        assert chal.perplexity(logits, np.array([3, 7])) < 1.001

    def test_monotonic_in_loss(self, chal):
        rng = np.random.default_rng(1)
        logits = rng.normal(size=(20, 30))
        targets = rng.integers(0, 30, size=20)
        ppl = chal.perplexity(logits, targets)
        ce = chal.batch_cross_entropy(logits, targets)
        assert ppl == pytest.approx(math.exp(ce), rel=1e-9)
        assert 1.0 < ppl < 30.0
