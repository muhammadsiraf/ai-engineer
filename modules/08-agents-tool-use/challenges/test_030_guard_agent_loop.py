import pytest


def _load():
    import importlib.util

    path = __file__.replace("test_030_guard_agent_loop.py", "030_guard_agent_loop.py")
    spec = importlib.util.spec_from_file_location("chal_m8_030", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def chal():
    return _load()


class TestRepeat:
    def test_second_identical_call_trips(self, chal):
        g = chal.LoopGuard()
        assert g.record("a", True) == "continue"
        assert g.record("a", True) == "repeat_loop"

    def test_sticky(self, chal):
        g = chal.LoopGuard()
        g.record("a", True)
        g.record("a", True)
        assert g.record("a", True) == "repeat_loop"
        assert g.record("b", True) == "repeat_loop"

    def test_alternating_never_trips(self, chal):
        g = chal.LoopGuard(max_steps=100)
        for i in range(12):
            assert g.record("ab"[i % 2], True) == "continue"

    def test_repeat_before_error(self, chal):
        g = chal.LoopGuard(max_error_streak=5)
        assert g.record("a", False) == "continue"
        assert g.record("a", False) == "repeat_loop"


class TestErrorStreak:
    def test_trips_on_third_error(self, chal):
        g = chal.LoopGuard()
        assert g.record("a", False) == "continue"
        assert g.record("b", False) == "continue"
        assert g.record("c", False) == "error_streak"

    def test_success_resets(self, chal):
        g = chal.LoopGuard()
        g.record("a", False)
        g.record("b", False)
        assert g.record("s", True) == "continue"
        g.record("c", False)
        assert g.record("d", False) == "continue"  # streak was reset

    def test_error_before_budget(self, chal):
        g = chal.LoopGuard(max_steps=2, max_error_streak=2)
        assert g.record("a", False) == "continue"
        assert g.record("b", False) == "error_streak"


class TestBudget:
    def test_budget_allows_exactly_max_steps(self, chal):
        g = chal.LoopGuard(max_steps=3)
        assert g.record("a", True) == "continue"
        assert g.record("b", True) == "continue"
        assert g.record("c", True) == "step_budget_exceeded"

    def test_budget_counts_errors_too(self, chal):
        g = chal.LoopGuard(max_steps=3, max_error_streak=10)
        assert g.record("a", False) == "continue"
        assert g.record("b", False) == "continue"
        assert g.record("c", False) == "step_budget_exceeded"

    def test_sticky_after_budget(self, chal):
        g = chal.LoopGuard(max_steps=1)
        g.record("a", True)
        assert g.record("b", True) == "step_budget_exceeded"


class TestAnswer:
    def test_record_answer(self, chal):
        g = chal.LoopGuard()
        g.record("a", True)
        assert g.record_answer() == "done"
        assert g.stop_reason == "answered"

    def test_steps_counter(self, chal):
        g = chal.LoopGuard()
        g.record("a", True)
        g.record("b", True)
        assert g.steps == 2
