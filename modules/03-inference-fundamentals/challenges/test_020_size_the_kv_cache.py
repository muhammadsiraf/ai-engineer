import pytest


def _load():
    import importlib.util

    path = __file__.replace("test_020_size_the_kv_cache.py", "020_size_the_kv_cache.py")
    spec = importlib.util.spec_from_file_location("chal_m3_020", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def chal():
    return _load()


GB = 1_000_000_000


def llama8b_24gb(chal, **kw):
    defaults = dict(
        layers=32, kv_heads=8, d_head=128, params=8e9, gpu_bytes=24 * GB,
        overhead_bytes=1.5 * GB,
    )
    defaults.update(kw)
    return chal.VRAMBudget(**defaults)


class TestFormula:
    def test_kv_bytes_per_token_gqa(self, chal):
        b = llama8b_24gb(chal)
        # 2 × 32 × 8 × 128 × 2 = 131072
        assert b.kv_bytes_per_token() == 131_072

    def test_mha_comparison(self, chal):
        naive = llama8b_24gb(chal, kv_heads=32, d_head=128)
        assert naive.kv_bytes_per_token() == 4 * 131_072  # no GQA -> 4x

    def test_weights(self, chal):
        assert llama8b_24gb(chal).weights_bytes() == pytest.approx(16 * GB)

    def test_int4_weights(self, chal):
        b = llama8b_24gb(chal, weight_bytes_per_param=0.5)
        assert b.weights_bytes() == pytest.approx(4 * GB)


class TestBudget:
    def test_pool(self, chal):
        b = llama8b_24gb(chal)
        assert b.kv_pool_bytes() == pytest.approx(24 * GB - 16 * GB - 1.5 * GB)

    def test_pool_clamps_at_zero(self, chal):
        b = llama8b_24gb(chal, gpu_bytes=15 * GB)  # weights 16GB don't fit
        assert b.kv_pool_bytes() == 0
        assert b.capacity_tokens() == 0
        assert b.max_concurrent(1000) == 0

    def test_capacity_tokens(self, chal):
        b = llama8b_24gb(chal)
        pool = 24 * GB - 16 * GB - 1.5 * GB
        assert b.capacity_tokens() == int(pool // 131_072)
        # lesson's ~52.4k number
        assert 52_000 < b.capacity_tokens() < 53_000


class TestConcurrency:
    def test_4k_context(self, chal):
        b = llama8b_24gb(chal)
        assert b.max_concurrent(4096) == int((24 * GB - 16 * GB - 1.5 * GB) // (131_072 * 4096))
        assert 11 <= b.max_concurrent(4096) <= 13

    def test_8k_halves(self, chal):
        b = llama8b_24gb(chal)
        assert b.max_concurrent(8192) * 2 == pytest.approx(b.max_concurrent(4096), abs=1)

    def test_int8_kv_doubles(self, chal):
        fp16 = llama8b_24gb(chal)
        int8 = llama8b_24gb(chal, kv_bytes_per_elem=1)
        assert int8.max_concurrent(4096) == pytest.approx(fp16.max_concurrent(4096) * 2, abs=1)

    def test_context_zero_raises(self, chal):
        with pytest.raises((ValueError, ZeroDivisionError)):
            llama8b_24gb(chal).max_concurrent(0)


class TestFits:
    def test_fp16_fits_24gb(self, chal):
        assert llama8b_24gb(chal).fits() is True

    def test_fp16_not_on_16gb(self, chal):
        assert llama8b_24gb(chal, gpu_bytes=16 * GB).fits() is False

    def test_int4_on_16gb(self, chal):
        b = llama8b_24gb(chal, gpu_bytes=16 * GB, weight_bytes_per_param=0.5)
        assert b.fits() is True
        assert b.max_concurrent(4096) > 20  # huge cache room now
