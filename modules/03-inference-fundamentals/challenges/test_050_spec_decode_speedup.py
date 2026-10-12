import pytest


def _load():
    import importlib.util

    path = __file__.replace("test_050_spec_decode_speedup.py", "050_spec_decode_speedup.py")
    spec = importlib.util.spec_from_file_location("chal_m3_050", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def chal():
    return _load()


class TestExpectedTokens:
    def test_alpha_point_eight_k_four(self, chal):
        # (1 - 0.8^5) / 0.2 = 3.3616
        assert chal.expected_tokens_per_pass(0.8, 4) == pytest.approx(3.3616)

    def test_perfect_acceptance_gives_k_plus_one(self, chal):
        assert chal.expected_tokens_per_pass(1.0, 4) == 5

    def test_zero_acceptance_gives_one(self, chal):
        # every draft rejected, but the verify pass still emits its own token
        assert chal.expected_tokens_per_pass(0.0, 4) == 1.0

    def test_invalid_alpha_raises(self, chal):
        with pytest.raises(ValueError):
            chal.expected_tokens_per_pass(1.5, 4)
        with pytest.raises(ValueError):
            chal.expected_tokens_per_pass(-0.1, 4)

    def test_invalid_k_raises(self, chal):
        with pytest.raises(ValueError):
            chal.expected_tokens_per_pass(0.8, 0)


class TestCostAndSpeedup:
    def test_cost(self, chal):
        assert chal.verify_cost(4, 0.1) == pytest.approx(1.4)

    def test_lesson_headline_number(self, chal):
        s = chal.speedup(0.8, 4, 0.1)
        assert s == pytest.approx(2.4, abs=0.01)

    def test_marginal_at_low_acceptance(self, chal):
        s = chal.speedup(0.5, 4, 0.1)
        assert 1.3 < s < 1.5

    def test_great_at_high_acceptance(self, chal):
        s = chal.speedup(0.95, 4, 0.1)
        assert 3.0 < s < 3.4

    def test_expensive_draft_can_lose_money(self, chal):
        # same-size draft model: c = 0.9, alpha 0.5 → net slower than 1x
        assert chal.speedup(0.5, 4, 0.9) < 1.0


class TestBestDraft:
    def test_optimum_for_lesson_numbers(self, chal):
        # alpha=0.8, c=0.1: speedup peaks at k=6 (~2.47), not at the
        # "obvious" k=4 — longer drafts eventually pay more than they earn
        k, s = chal.best_draft_length(0.8, 0.1, k_min=1, k_max=10)
        assert k == 6
        assert s == pytest.approx(2.4696, abs=0.01)
        assert s > chal.speedup(0.8, 4, 0.1)

    def test_no_gain_when_alpha_is_zero(self, chal):
        k, s = chal.best_draft_length(0.0, 0.1)
        assert k == 1  # every draft is dead weight; shortest wins
        assert s < 1.0
