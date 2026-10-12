import pytest


def _load():
    import importlib.util

    path = __file__.replace("test_050_score_agent_run.py", "050_score_agent_run.py")
    spec = importlib.util.spec_from_file_location("chal_m8_050", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def chal():
    return _load()


RUNS = [
    {"done": True, "verified": True, "steps": 4, "tokens": 1200, "dollars": 0.03},
    {"done": True, "verified": False, "steps": 9, "tokens": 3100, "dollars": 0.09},
    {"done": False, "verified": False, "steps": 25, "tokens": 6000, "dollars": 0.18},
    {"done": True, "verified": True, "steps": 6, "tokens": 1800, "dollars": 0.05},
]


class TestRates:
    def test_completion(self, chal):
        assert chal.completion_rate(RUNS) == pytest.approx(0.75)

    def test_success(self, chal):
        assert chal.success_rate(RUNS) == pytest.approx(0.5)

    def test_success_never_exceeds_completion(self, chal):
        assert chal.success_rate(RUNS) <= chal.completion_rate(RUNS)

    def test_perfect_run(self, chal):
        runs = [
            {"done": True, "verified": True, "steps": 2, "tokens": 100, "dollars": 0.01}
        ]
        assert chal.completion_rate(runs) == 1.0
        assert chal.success_rate(runs) == 1.0

    def test_empty_rejected(self, chal):
        with pytest.raises(ValueError):
            chal.completion_rate([])
        with pytest.raises(ValueError):
            chal.success_rate([])


class TestCost:
    def test_dollars_per_success_counts_verified_only(self, chal):
        assert chal.cost_per_success(RUNS) == pytest.approx(0.04)

    def test_no_success_is_an_error(self, chal):
        runs = [
            {"done": False, "verified": False, "steps": 5, "tokens": 900, "dollars": 0.02}
        ]
        with pytest.raises(ValueError):
            chal.cost_per_success(runs)

    def test_steps_per_success(self, chal):
        assert chal.steps_per_success(RUNS) == pytest.approx(5.0)

    def test_avg_tokens_all_runs(self, chal):
        assert chal.avg_tokens(RUNS) == pytest.approx(3025.0)


class TestSummary:
    def test_card(self, chal):
        s = chal.summary(RUNS)
        assert s["completion"] == pytest.approx(0.75)
        assert s["success"] == pytest.approx(0.5)
        assert s["dollars_per_success"] == pytest.approx(0.04)
        assert s["steps_per_success"] == pytest.approx(5.0)
        assert s["avg_tokens"] == pytest.approx(3025.0)

    def test_single_run(self, chal):
        runs = [
            {"done": True, "verified": True, "steps": 3, "tokens": 500, "dollars": 0.02}
        ]
        s = chal.summary(runs)
        assert s["dollars_per_success"] == pytest.approx(0.02)
        assert s["steps_per_success"] == pytest.approx(3.0)
