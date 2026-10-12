import pytest


def _load():
    import importlib.util

    path = __file__.replace("test_030_qlora_vram_budget.py", "030_qlora_vram_budget.py")
    spec = importlib.util.spec_from_file_location("chal_m5_030", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def chal():
    return _load()


GB = 1_000_000_000
P7B = 7e9
ADAPTERS = 29_360_128  # 32 layers × 7 targets × 2·16·4096 (challenge 010)
ACT = 2 * GB


class TestComponents:
    def test_nf4_base_is_quarter_of_bf16(self, chal):
        assert chal.qlora_base_bytes(P7B) == pytest.approx(3.5 * GB)

    def test_adapter_bytes(self, chal):
        assert chal.adapter_train_bytes(ADAPTERS) == pytest.approx(ADAPTERS * 18)

    def test_full_ft_16_bytes(self, chal):
        assert chal.full_ft_bytes(P7B) == pytest.approx(112 * GB)


class TestTotals:
    def test_lesson_number_7b(self, chal):
        total = chal.qlora_total_bytes(P7B, ADAPTERS, ACT)
        assert total == pytest.approx(3.5 * GB + ADAPTERS * 18 + 2 * GB)
        assert 5.5 * GB < total < 6.5 * GB  # the "fits a 12GB card" claim

    def test_ratio_7b(self, chal):
        r = chal.vram_ratio(P7B, ADAPTERS, ACT)
        assert r == pytest.approx(112 * GB / (3.5 * GB + ADAPTERS * 18 + 2 * GB))
        assert 15 < r < 22  # lesson 050's "roughly 20x"

    def test_13b_lesson_check_yourself(self, chal):
        # base 6.5 GB + ~0 + 2 GB activations ≈ 8.5 GB
        total = chal.qlora_total_bytes(13e9, ADAPTERS, ACT)
        assert total == pytest.approx(6.5 * GB + ADAPTERS * 18 + 2 * GB)
        assert chal.full_ft_bytes(13e9) == pytest.approx(208 * GB)
        assert chal.vram_ratio(13e9, ADAPTERS, ACT) > 20

    def test_activations_dominate_when_small_model(self, chal):
        # tiny model, huge batch: activations, not weights, decide fit
        total = chal.qlora_total_bytes(0.5e9, 1e6, 20 * GB)
        assert total > 20 * GB  # base+adapters are ~0.26 GB
