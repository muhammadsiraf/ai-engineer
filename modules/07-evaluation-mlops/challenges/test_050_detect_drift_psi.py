import math

import pytest


def _load():
    import importlib.util

    path = __file__.replace("test_050_detect_drift_psi.py", "050_detect_drift_psi.py")
    spec = importlib.util.spec_from_file_location("chal_m7_050", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def chal():
    return _load()


class TestBucketEdges:
    def test_median_of_four(self, chal):
        assert chal.bucket_edges([0, 1, 2, 3], n_buckets=2) == [1.5]

    def test_quartiles_linear_interpolation(self, chal):
        edges = chal.bucket_edges(list(range(100)), n_buckets=4)
        assert edges[0] == pytest.approx(24.75)
        assert edges[1] == pytest.approx(49.5)
        assert edges[2] == pytest.approx(74.25)

    def test_count_and_ascending(self, chal):
        edges = chal.bucket_edges([3, 1, 2], n_buckets=3)
        assert len(edges) == 2
        assert edges == sorted(edges)

    def test_validation(self, chal):
        with pytest.raises(ValueError):
            chal.bucket_edges([], n_buckets=4)
        with pytest.raises(ValueError):
            chal.bucket_edges([1, 2, 3], n_buckets=1)


class TestShares:
    def test_split_at_edge(self, chal):
        edges = chal.bucket_edges([0, 1, 2, 3], n_buckets=2)
        assert chal.shares([0, 0, 0, 3], edges) == pytest.approx([0.75, 0.25])

    def test_sums_to_one(self, chal):
        edges = chal.bucket_edges(list(range(50)), n_buckets=5)
        assert sum(chal.shares(list(range(30)), edges)) == pytest.approx(1.0)

    def test_empty_values_rejected(self, chal):
        with pytest.raises(ValueError):
            chal.shares([], [1.0])


class TestPSI:
    def test_identical_is_zero(self, chal):
        ref = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        assert chal.psi(ref, list(ref)) == pytest.approx(0.0, abs=1e-12)

    def test_hand_computed_alarm(self, chal):
        v = chal.psi([0, 1, 2, 3], [0, 0, 0, 3], n_buckets=2)
        # (0.75−0.5)·ln(0.75/0.5) + (0.25−0.5)·ln(0.25/0.5)
        expected = 0.25 * math.log(1.5) + 0.25 * math.log(2.0)
        assert v == pytest.approx(expected, abs=1e-12)
        assert v == pytest.approx(0.2747, abs=1e-3)

    def test_empty_bucket_clamped_finite(self, chal):
        v = chal.psi([0, 1, 2, 3], [0, 0, 0, 0], n_buckets=2)
        assert math.isfinite(v)
        assert v == pytest.approx(6.908, abs=1e-2)

    def test_bigger_shift_bigger_psi(self, chal):
        ref = list(range(100))
        small = [x + 2 for x in ref]
        big = [x + 20 for x in ref]
        assert chal.psi(ref, small) < chal.psi(ref, big)

    def test_validation(self, chal):
        with pytest.raises(ValueError):
            chal.psi([], [1, 2, 3])
        with pytest.raises(ValueError):
            chal.psi([1, 2, 3], [])
        with pytest.raises(ValueError):
            chal.psi([1, 2], [1, 2], n_buckets=1)


class TestLevel:
    def test_thresholds(self, chal):
        assert chal.psi_level(0.05) == "quiet"
        assert chal.psi_level(0.1) == "investigate"
        assert chal.psi_level(0.2) == "investigate"
        assert chal.psi_level(0.25) == "investigate"
        assert chal.psi_level(0.3) == "alarm"

    def test_hand_case_alarms(self, chal):
        v = chal.psi([0, 1, 2, 3], [0, 0, 0, 3], n_buckets=2)
        assert chal.psi_level(v) == "alarm"
