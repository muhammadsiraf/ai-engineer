import pytest


def _load():
    import importlib.util

    path = __file__.replace("test_020_remaining_error_budget.py", "020_remaining_error_budget.py")
    spec = importlib.util.spec_from_file_location("chal_m6_020", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def chal():
    return _load()


class TestAllowed:
    def test_lesson_number(self, chal):
        assert chal.allowed_violations(2_000_000, 0.995) == pytest.approx(10_000)

    def test_two_nines(self, chal):
        assert chal.allowed_violations(1_000_000, 0.99) == pytest.approx(10_000)

    def test_slo_validation(self, chal):
        for bad in (0.0, 1.0, 1.5, -0.1):
            with pytest.raises(ValueError):
                chal.allowed_violations(1000, bad)


class TestRemaining:
    def test_lesson_check_yourself(self, chal):
        r = chal.remaining_budget_fraction(2_000_000, 14_000, 0.995)
        assert r == pytest.approx(-0.40)  # over budget — negative is the point

    def test_healthy(self, chal):
        assert chal.remaining_budget_fraction(1_000_000, 2_000, 0.99) == pytest.approx(0.8)

    def test_exact_budget_spent(self, chal):
        assert chal.remaining_budget_fraction(1_000_000, 10_000, 0.99) == pytest.approx(0.0)

    def test_negative_violations_raises(self, chal):
        with pytest.raises(ValueError):
            chal.remaining_budget_fraction(1000, -1, 0.99)


class TestBurnRate:
    def test_lesson_number(self, chal):
        # 3500/10000 consumed at 168/672 of the window → 1.4x
        assert chal.burn_rate(3500, 10_000, 168, 672) == pytest.approx(1.4)

    def test_on_schedule_is_one(self, chal):
        assert chal.burn_rate(2500, 10_000, 168, 672) == pytest.approx(1.0)

    def test_fast_burn(self, chal):
        assert chal.burn_rate(5000, 10_000, 24, 672) == pytest.approx(14.0)

    def test_zero_violations(self, chal):
        assert chal.burn_rate(0, 10_000, 100, 672) == 0.0

    def test_validation(self, chal):
        with pytest.raises(ValueError):
            chal.burn_rate(1, 10_000, 0, 672)
        with pytest.raises(ValueError):
            chal.burn_rate(1, 10_000, 168, 0)


class TestAction:
    def test_ship_zone(self, chal):
        assert chal.action(0.8) == "ship"
        assert chal.action(0.51) == "ship"

    def test_tighten_zone(self, chal):
        assert chal.action(0.5) == "tighten"   # boundary: not > 0.5
        assert chal.action(0.3) == "tighten"

    def test_freeze_zone(self, chal):
        assert chal.action(0.25) == "freeze"
        assert chal.action(0.2) == "freeze"
        assert chal.action(-0.4) == "freeze"   # lesson 040's verdict

    def test_full_pipeline(self, chal):
        remaining = chal.remaining_budget_fraction(2_000_000, 14_000, 0.995)
        assert chal.action(remaining) == "freeze"
