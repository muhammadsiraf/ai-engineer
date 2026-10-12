import pytest


def _load():
    import importlib.util

    path = __file__.replace("test_060_pick_batch_for_slo.py", "060_pick_batch_for_slo.py")
    spec = importlib.util.spec_from_file_location("chal_m3_060", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def chal():
    return _load()


TABLE = {1: 90, 8: 600, 16: 950, 32: 1400, 64: 1600}


class TestPerRequest:
    def test_batch_16(self, chal):
        assert chal.per_request_tps(TABLE, 16) == pytest.approx(950 / 16)

    def test_batch_32_is_lesson_number(self, chal):
        assert chal.per_request_tps(TABLE, 32) == pytest.approx(43.75)

    def test_monotonically_decreasing(self, chal):
        tps = [chal.per_request_tps(TABLE, b) for b in sorted(TABLE)]
        assert all(a > b for a, b in zip(tps, tps[1:]))


class TestSlo:
    def test_lesson_answer_is_32(self, chal):
        assert chal.max_batch_for_slo(TABLE, 40) == 32

    def test_tighter_slo_backs_off_to_16(self, chal):
        # B=32 gives 43.75 >= 40 but < 50 → 16 (59.375)
        assert chal.max_batch_for_slo(TABLE, 50) == 16

    def test_impossible_slo_returns_none(self, chal):
        assert chal.max_batch_for_slo(TABLE, 100) is None

    def test_dict_order_does_not_matter(self, chal):
        shuffled = {64: 1600, 1: 90, 32: 1400, 8: 600, 16: 950}
        assert chal.max_batch_for_slo(shuffled, 40) == 32


class TestReplicas:
    def test_three_replicas_for_2500tps(self, chal):
        # 2500 / (1400 × 0.75) = 2.38 → 3
        assert chal.replicas_for_load(TABLE, 32, 2500) == 3

    def test_full_utilization_needs_fewer_on_paper(self, chal):
        # 2500 / 1400 = 1.79 → 2 (and lesson 120 explains why you won't run it)
        assert chal.replicas_for_load(TABLE, 32, 2500, utilization=1.0) == 2

    def test_zero_demand_needs_zero_replicas(self, chal):
        assert chal.replicas_for_load(TABLE, 32, 0) == 0

    def test_negative_demand_raises(self, chal):
        with pytest.raises(ValueError):
            chal.replicas_for_load(TABLE, 32, -5)

    def test_bad_utilization_raises(self, chal):
        with pytest.raises(ValueError):
            chal.replicas_for_load(TABLE, 32, 100, utilization=0)
        with pytest.raises(ValueError):
            chal.replicas_for_load(TABLE, 32, 100, utilization=1.5)
