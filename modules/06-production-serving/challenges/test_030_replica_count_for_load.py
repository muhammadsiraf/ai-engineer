import pytest


def _load():
    import importlib.util

    path = __file__.replace("test_030_replica_count_for_load.py", "030_replica_count_for_load.py")
    spec = importlib.util.spec_from_file_location("chal_m6_030", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def chal():
    return _load()


class TestReplicasNeeded:
    def test_lesson_check_yourself(self, chal):
        assert chal.replicas_needed(40, 12, 0.75) == 5  # not ceil(40/12)=4

    def test_full_utilization_is_naive_math(self, chal):
        assert chal.replicas_needed(40, 12, 1.0) == 4

    def test_exactly_divisible(self, chal):
        assert chal.replicas_needed(30, 10, 0.5) == 6

    def test_more_headroom_more_replicas(self, chal):
        assert chal.replicas_needed(100, 10, 0.5) > chal.replicas_needed(100, 10, 0.9)

    def test_validation(self, chal):
        with pytest.raises(ValueError):
            chal.replicas_needed(40, 0)
        with pytest.raises(ValueError):
            chal.replicas_needed(40, 12, 0.0)
        with pytest.raises(ValueError):
            chal.replicas_needed(40, 12, 1.5)


class TestUtilization:
    def test_normal(self, chal):
        assert chal.provisioned_utilization(5, 12, 36) == pytest.approx(0.6)

    def test_overloaded_exceeds_one(self, chal):
        assert chal.provisioned_utilization(2, 12, 40) == pytest.approx(40 / 24)

    def test_zero_traffic(self, chal):
        assert chal.provisioned_utilization(3, 12, 0) == 0.0


class TestBurst:
    def test_floor_absorbs(self, chal):
        assert chal.can_absorb_burst(3, 12, 36) is True

    def test_floor_too_small(self, chal):
        assert chal.can_absorb_burst(2, 12, 36) is False

    def test_exact_boundary_counts_as_absorbed(self, chal):
        assert chal.can_absorb_burst(3, 12, 36.0) is True


class TestScaleDecision:
    def test_scale_out_on_deep_queue(self, chal):
        assert chal.scale_decision(50, 20, 4, 2, 10, False) == "scale_out"

    def test_ceiling_guardrail(self, chal):
        assert chal.scale_decision(50, 20, 10, 2, 10, False) == "at_max"

    def test_scale_in_needs_sustained_idle(self, chal):
        assert chal.scale_decision(0, 20, 8, 2, 10, True) == "scale_in"
        assert chal.scale_decision(0, 20, 8, 2, 10, False) == "hold"

    def test_floor_blocks_scale_in(self, chal):
        assert chal.scale_decision(0, 20, 2, 2, 10, True) == "hold"

    def test_moderate_queue_holds(self, chal):
        assert chal.scale_decision(10, 20, 4, 2, 10, True) == "hold"
