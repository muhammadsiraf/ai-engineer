import pytest


def _load():
    import importlib.util

    path = __file__.replace("test_050_cost_per_million_tokens.py", "050_cost_per_million_tokens.py")
    spec = importlib.util.spec_from_file_location("chal_m6_050", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def chal():
    return _load()


class TestPerSecond:
    def test_two_dollars(self, chal):
        assert chal.cost_per_replica_second(2.0) == pytest.approx(2.0 / 3600)


class TestCostPerMillion:
    def test_lesson_body_number(self, chal):
        # $2/hr at 1400 tok/s fully utilized → ~$0.40 per 1M
        assert chal.cost_per_million_tokens(2.0, 1400, 1.0) == pytest.approx(0.3968, abs=1e-3)

    def test_check_yourself_80pct(self, chal):
        assert chal.cost_per_million_tokens(1.6, 800, 0.8) == pytest.approx(0.6944, abs=1e-3)

    def test_check_yourself_50pct(self, chal):
        assert chal.cost_per_million_tokens(1.6, 800, 0.5) == pytest.approx(1.1111, abs=1e-3)

    def test_utilization_is_inverse(self, chal):
        full = chal.cost_per_million_tokens(2.0, 1000, 1.0)
        half = chal.cost_per_million_tokens(2.0, 1000, 0.5)
        assert half == pytest.approx(2 * full)

    def test_validation(self, chal):
        with pytest.raises(ValueError):
            chal.cost_per_million_tokens(0, 1000, 0.8)
        with pytest.raises(ValueError):
            chal.cost_per_million_tokens(2.0, 0, 0.8)
        with pytest.raises(ValueError):
            chal.cost_per_million_tokens(2.0, 1000, 0.0)
        with pytest.raises(ValueError):
            chal.cost_per_million_tokens(2.0, 1000, 1.2)


class TestMonthly:
    def test_two_replicas_two_dollars(self, chal):
        assert chal.monthly_cost(2.0, 2) == pytest.approx(2.0 * 2 * 730)

    def test_custom_hours(self, chal):
        assert chal.monthly_cost(3.0, 1, hours=100) == pytest.approx(300.0)


class TestMargin:
    def test_healthy_margin(self, chal):
        # self-host $0.40 vs managed $1.00 → 60% margin
        assert chal.margin_vs_managed(0.40, 1.00) == pytest.approx(0.60)

    def test_losing_money_is_negative(self, chal):
        assert chal.margin_vs_managed(1.20, 1.00) == pytest.approx(-0.20)

    def test_break_even_is_zero(self, chal):
        assert chal.margin_vs_managed(0.80, 0.80) == pytest.approx(0.0)

    def test_pipeline(self, chal):
        cost = chal.cost_per_million_tokens(2.0, 1400, 0.7)
        margin = chal.margin_vs_managed(cost, 1.25)
        assert 0 < margin < 1
