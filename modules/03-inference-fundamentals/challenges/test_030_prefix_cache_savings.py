import pytest


def _load():
    import importlib.util

    path = __file__.replace("test_030_prefix_cache_savings.py", "030_prefix_cache_savings.py")
    spec = importlib.util.spec_from_file_location("chal_m3_030", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def chal():
    return _load()


def lesson_scenario(chal, **kw):
    defaults = dict(prefix_tokens=1800, novel_tokens=400, num_requests=10_000)
    defaults.update(kw)
    return chal.PrefixCacheSavings(**defaults)


class TestCacheable:
    def test_block_size_one_aligns_everything(self, chal):
        assert lesson_scenario(chal).cacheable_prefix_tokens() == 1800

    def test_block_alignment_floors(self, chal):
        # 1800 / 16 = 112.5 -> only 112 full blocks are reusable
        b = lesson_scenario(chal, block_size=16)
        assert b.cacheable_prefix_tokens() == 1792

    def test_warm_prefill_skips_only_aligned_part(self, chal):
        b = lesson_scenario(chal, block_size=16)
        # mismatch point is at token 1792; 1800+400-1792 = 408 tokens remain
        assert b.prefill_tokens_cached() == 408

    def test_cold_prefill_is_everything(self, chal):
        assert lesson_scenario(chal).prefill_tokens_uncached() == 2200


class TestTotals:
    def test_uncached_total(self, chal):
        assert lesson_scenario(chal).total_prefill_uncached() == 10_000 * 2200

    def test_cached_total_first_request_is_cold(self, chal):
        b = lesson_scenario(chal, num_requests=3)
        # 2200 (cold) + 400 + 400
        assert b.total_prefill_cached() == 2200 + 2 * 400

    def test_cached_with_alignment(self, chal):
        b = lesson_scenario(chal, num_requests=3, block_size=16)
        assert b.total_prefill_cached() == 2200 + 2 * 408


class TestSavings:
    def test_lesson_number_about_82pct(self, chal):
        f = lesson_scenario(chal).savings_fraction()
        assert 0.80 < f < 0.83
        assert f == pytest.approx(1 - 4_001_800 / 22_000_000)

    def test_single_request_saves_nothing(self, chal):
        assert lesson_scenario(chal, num_requests=1).savings_fraction() == 0.0

    def test_zero_requests_saves_nothing(self, chal):
        assert lesson_scenario(chal, num_requests=0).savings_fraction() == 0.0

    def test_longer_prefix_saves_more(self, chal):
        short = lesson_scenario(chal, prefix_tokens=200).savings_fraction()
        long = lesson_scenario(chal, prefix_tokens=1800).savings_fraction()
        assert long > short


class TestTTFT:
    def test_cold_ttft(self, chal):
        b = lesson_scenario(chal)
        assert b.ttft_seconds(50_000, warm=False) == pytest.approx(2200 / 50_000)

    def test_warm_ttft(self, chal):
        b = lesson_scenario(chal)
        assert b.ttft_seconds(50_000, warm=True) == pytest.approx(400 / 50_000)

    def test_warm_respects_block_alignment(self, chal):
        b = lesson_scenario(chal, block_size=16)
        assert b.ttft_seconds(50_000, warm=True) == pytest.approx(408 / 50_000)

    def test_bad_rate_raises(self, chal):
        b = lesson_scenario(chal)
        with pytest.raises(ValueError):
            b.ttft_seconds(0, warm=True)
        with pytest.raises(ValueError):
            b.ttft_seconds(-1, warm=False)
