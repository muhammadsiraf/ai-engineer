import pytest


def _load():
    import importlib.util

    path = __file__.replace("test_010_p99_from_load_test.py", "010_p99_from_load_test.py")
    spec = importlib.util.spec_from_file_location("chal_m6_010", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def chal():
    return _load()


SAMPLES = [13.0, 10.0, 17.0, 11.0, 19.0, 14.0, 16.0, 12.0, 18.0, 15.0]  # 10..19 shuffled


class TestPercentile:
    def test_docstring_reference_values(self, chal):
        assert chal.percentile(SAMPLES, 50) == pytest.approx(14.5)
        assert chal.percentile(SAMPLES, 95) == pytest.approx(18.55)
        assert chal.percentile(SAMPLES, 99) == pytest.approx(18.91)

    def test_unsorted_input_ok(self, chal):
        assert chal.percentile(SAMPLES, 50) == chal.percentile(sorted(SAMPLES), 50)

    def test_exact_ranks(self, chal):
        assert chal.percentile([5.0, 6.0, 7.0, 8.0], 0.0001) == pytest.approx(5.0)
        assert chal.percentile([5.0, 6.0, 7.0, 8.0], 100) == pytest.approx(8.0)

    def test_single_sample(self, chal):
        assert chal.percentile([42.0], 99) == pytest.approx(42.0)

    def test_two_samples_interpolate(self, chal):
        assert chal.percentile([0.0, 10.0], 50) == pytest.approx(5.0)

    def test_does_not_mutate_input(self, chal):
        original = list(SAMPLES)
        chal.percentile(SAMPLES, 95)
        assert SAMPLES == original

    def test_validation(self, chal):
        with pytest.raises(ValueError):
            chal.percentile([], 50)
        with pytest.raises(ValueError):
            chal.percentile(SAMPLES, 0)
        with pytest.raises(ValueError):
            chal.percentile(SAMPLES, 101)


class TestSummarize:
    def test_keys_and_values(self, chal):
        s = chal.summarize(SAMPLES)
        assert set(s) == {"p50", "p95", "p99", "mean"}
        assert s["p50"] == pytest.approx(14.5)
        assert s["mean"] == pytest.approx(14.5)  # 10..19 average is 14.5
        assert s["p50"] <= s["p95"] <= s["p99"]


class TestSLO:
    def test_meets(self, chal):
        # p95 = 18.55 → threshold 19 passes, 18 fails
        assert chal.meets_slo(SAMPLES, 19.0) is True
        assert chal.meets_slo(SAMPLES, 18.0) is False

    def test_custom_pct(self, chal):
        # p99 = 18.91
        assert chal.meets_slo(SAMPLES, 18.5, pct=99) is False
        assert chal.meets_slo(SAMPLES, 19.0, pct=99) is True


class TestCapacity:
    TABLE = {10: 400.0, 20: 700.0, 40: 1500.0, 80: 4000.0}

    def test_knee_finding(self, chal):
        assert chal.max_rps_meeting_slo(self.TABLE, 2000) == 40

    def test_tight_slo(self, chal):
        assert chal.max_rps_meeting_slo(self.TABLE, 700) == 20

    def test_impossible(self, chal):
        assert chal.max_rps_meeting_slo(self.TABLE, 100) is None

    def test_order_does_not_matter(self, chal):
        shuffled = {80: 4000.0, 10: 400.0, 40: 1500.0, 20: 700.0}
        assert chal.max_rps_meeting_slo(shuffled, 2000) == 40
