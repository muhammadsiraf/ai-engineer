import pytest


def _load():
    import importlib.util

    path = __file__.replace("test_010_time_a_request.py", "010_time_a_request.py")
    spec = importlib.util.spec_from_file_location("chal_m3_010", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def chal():
    return _load()


@pytest.fixture()
def model(chal):
    return chal.LatencyModel(queue_s=0.1)


DATA = [
    {"input_tokens": 1000, "output_tokens": 100, "total_s": 0.1 + 0.040 * 1 + 0.020 * 100},
    {"input_tokens": 2000, "output_tokens": 100, "total_s": 0.1 + 0.040 * 2 + 0.020 * 100},
    {"input_tokens": 500, "output_tokens": 500, "total_s": 0.1 + 0.040 * 0.5 + 0.020 * 500},
    {"input_tokens": 8000, "output_tokens": 50, "total_s": 0.1 + 0.040 * 8 + 0.020 * 50},
    {"input_tokens": 300, "output_tokens": 800, "total_s": 0.1 + 0.040 * 0.3 + 0.020 * 800},
]


class TestCalibrate:
    def test_recovers_true_coefficients(self, model, chal):
        model.calibrate(DATA)
        assert model.k1 == pytest.approx(0.040, abs=1e-6)
        assert model.k2 == pytest.approx(0.020, abs=1e-6)

    def test_handles_queue(self, model):
        model.calibrate(DATA)
        assert model.queue_s == pytest.approx(0.1)


class TestPredict:
    def test_decomposition(self, model, chal):
        model.calibrate(DATA)
        p = model.predict(1000, 100)
        assert set(p) == {"ttft_s", "decode_s", "total_s"}
        assert p["ttft_s"] == pytest.approx(0.1 + 0.040)
        assert p["decode_s"] == pytest.approx(0.020 * 100)
        assert p["total_s"] == pytest.approx(p["ttft_s"] + p["decode_s"])

    def test_zero_tokens(self, model):
        model.calibrate(DATA)
        p = model.predict(0, 0)
        assert p["total_s"] == pytest.approx(0.1)


class TestReport:
    def test_tiny_error_on_clean_data(self, model, chal):
        model.calibrate(DATA)
        rep = model.report(DATA)
        assert rep["ttft_max_err_s"] < 1e-6
        assert rep["total_max_err_s"] < 1e-6

    def test_flags_outliers(self, model, chal):
        model.calibrate(DATA)
        dirty = DATA + [{"input_tokens": 1000, "output_tokens": 100, "total_s": 5.0}]
        rep = model.report(dirty)
        assert rep["total_max_err_s"] > 4.0
