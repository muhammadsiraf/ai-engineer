import pytest


def _load():
    import importlib.util

    path = __file__.replace("test_040_pick_precision.py", "040_pick_precision.py")
    spec = importlib.util.spec_from_file_location("chal_m3_040", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def chal():
    return _load()


GB = 1_000_000_000
PARAMS = 8e9


def options(chal):
    return [
        chal.PrecisionOption("fp16", 2.0, 0.0, 1.0),
        chal.PrecisionOption("int8", 1.0, 0.2, 1.4),
        chal.PrecisionOption("fp8", 1.0, 0.1, 1.8),
        chal.PrecisionOption("int4", 0.5, 0.8, 2.1),
    ]


class TestWeights:
    def test_fp16_8b_is_16gb(self, chal):
        assert chal.weights_bytes(PARAMS, 2.0) == pytest.approx(16 * GB)

    def test_int4_8b_is_4gb(self, chal):
        assert chal.weights_bytes(PARAMS, 0.5) == pytest.approx(4 * GB)


class TestFits:
    def test_fp16_not_on_16gb(self, chal):
        got = chal.pick_precision(options(chal), PARAMS, 16 * GB, max_quality_drop_pct=0.0)
        # fp16 doesn't fit; nothing smaller is drop-free
        assert got is None

    def test_int4_fits_16gb(self, chal):
        got = chal.pick_precision(options(chal), PARAMS, 16 * GB)
        assert got is not None and got.name == "int4"

    def test_nothing_fits_tiny_gpu(self, chal):
        got = chal.pick_precision(options(chal), PARAMS, 4 * GB)  # int4 needs 4GB + 1.5 overhead
        assert got is None


class TestPick:
    def test_picks_most_aggressive_within_tolerance(self, chal):
        got = chal.pick_precision(options(chal), PARAMS, 24 * GB)
        assert got.name == "int4"

    def test_tight_tolerance_excludes_int4(self, chal):
        got = chal.pick_precision(options(chal), PARAMS, 24 * GB, max_quality_drop_pct=0.5)
        assert got.name == "fp8"  # tie on 1.0 B/param -> higher speedup wins

    def test_tie_breaks_on_speedup(self, chal):
        opts = [
            chal.PrecisionOption("slow_a", 1.0, 0.2, 1.4),
            chal.PrecisionOption("fast_b", 1.0, 0.2, 1.9),
        ]
        assert chal.pick_precision(opts, PARAMS, 24 * GB).name == "fast_b"

    def test_zero_tolerance_keeps_only_fp16(self, chal):
        got = chal.pick_precision(options(chal), PARAMS, 24 * GB, max_quality_drop_pct=0.0)
        assert got.name == "fp16"

    def test_overhead_can_disqualify(self, chal):
        # 6GB GPU: int4 weights 4GB fit alone but not with 2.5GB overhead
        got = chal.pick_precision(
            options(chal), PARAMS, 6 * GB, overhead_bytes=2.5 * GB
        )
        assert got.name == "fp8"
