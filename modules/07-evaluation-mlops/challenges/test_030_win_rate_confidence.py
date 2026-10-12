import math

import pytest


def _load():
    import importlib.util

    path = __file__.replace("test_030_win_rate_confidence.py", "030_win_rate_confidence.py")
    spec = importlib.util.spec_from_file_location("chal_m7_030", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def chal():
    return _load()


class TestSE:
    def test_known_value(self, chal):
        # p=0.6, n=1000 → sqrt(0.24/1000) ≈ 0.01549
        assert chal.standard_error(600, 1000) == pytest.approx(0.015492, abs=1e-5)

    def test_extremes_have_zero_se(self, chal):
        assert chal.standard_error(1000, 1000) == 0.0
        assert chal.standard_error(0, 1000) == 0.0

    def test_validation(self, chal):
        with pytest.raises(ValueError):
            chal.standard_error(5, 0)
        with pytest.raises(ValueError):
            chal.standard_error(-1, 10)
        with pytest.raises(ValueError):
            chal.standard_error(11, 10)


class TestCI:
    def test_docstring_reference(self, chal):
        lo, hi = chal.ci95(600, 1000)
        assert lo == pytest.approx(0.5696, abs=1e-3)
        assert hi == pytest.approx(0.6304, abs=1e-3)

    def test_not_significant_case(self, chal):
        lo, hi = chal.ci95(520, 1000)
        assert lo == pytest.approx(0.4890, abs=1e-3)
        assert hi == pytest.approx(0.5510, abs=1e-3)
        assert lo < 0.5 < hi

    def test_clamped_to_unit_interval(self, chal):
        lo, hi = chal.ci95(1000, 1000)
        assert lo == pytest.approx(1.0)
        assert hi == pytest.approx(1.0)
        lo, hi = chal.ci95(0, 1000)
        assert lo == pytest.approx(0.0)

    def test_wider_with_small_n(self, chal):
        width_100 = chal.ci95(60, 100)[1] - chal.ci95(60, 100)[0]
        width_1000 = chal.ci95(600, 1000)[1] - chal.ci95(600, 1000)[0]
        assert width_100 > width_1000


class TestSignificant:
    def test_600_of_1000(self, chal):
        assert chal.significant(600, 1000) is True

    def test_520_of_1000(self, chal):
        assert chal.significant(520, 1000) is False

    def test_exactly_coin_flip(self, chal):
        assert chal.significant(500, 1000) is False

    def test_small_n_needs_big_effect(self, chal):
        # 9/10 wins: CI ≈ [0.716, 1.0] → significant even at n=10
        assert chal.significant(9, 10) is True
        # 7/10: CI ≈ [0.34, 0.93] → not
        assert chal.significant(7, 10) is False


class TestSampleSize:
    def test_lesson_060_number(self, chal):
        n = chal.sample_size_needed(0.55)
        assert n == pytest.approx(1562, abs=100)
        assert 1400 <= n <= 1700

    def test_smaller_effect_needs_more(self, chal):
        assert chal.sample_size_needed(0.52) > chal.sample_size_needed(0.55)

    def test_more_power_more_samples(self, chal):
        assert chal.sample_size_needed(0.55, power=0.9) > chal.sample_size_needed(0.55)

    def test_result_is_an_integer_ceiling(self, chal):
        assert isinstance(chal.sample_size_needed(0.6), int)
        assert chal.sample_size_needed(0.6) >= math.ceil(
            (1.96 + 0.8416) ** 2 * (0.6 * 0.4 + 0.25) / 0.01
        ) - 1
