import pytest


def _load():
    import importlib.util

    path = __file__.replace("test_010_count_lora_params.py", "010_count_lora_params.py")
    spec = importlib.util.spec_from_file_location("chal_m5_010", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def chal():
    return _load()


class TestPerMatrix:
    def test_lesson_headline(self, chal):
        assert chal.lora_param_count(4096, 16) == 131_072
        assert chal.full_param_count(4096) == 16_777_216

    def test_ratio_per_matrix(self, chal):
        assert chal.full_param_count(4096) / chal.lora_param_count(4096, 16) == 128

    def test_linear_in_r(self, chal):
        assert chal.lora_param_count(4096, 32) == 2 * chal.lora_param_count(4096, 16)

    def test_r_equals_d_is_full(self, chal):
        assert chal.lora_param_count(1024, 1024) == chal.full_param_count(1024)


class TestModelWide:
    def test_reference_config(self, chal):
        # 7B-ish: 32 layers, d=4096, r=16, 7 targets (q,k,v,o,gate,up,down)
        full, lora = chal.model_param_counts(4096, 32, 16, 7)
        assert full == 32 * 7 * 16_777_216
        assert lora == 32 * 7 * 131_072

    def test_single_target_single_layer_matches_per_matrix(self, chal):
        full, lora = chal.model_param_counts(4096, 1, 16, 1)
        assert full == chal.full_param_count(4096)
        assert lora == chal.lora_param_count(4096, 16)

    def test_compression_ratio(self, chal):
        ratio = chal.compression_ratio(4096, 32, 16, 7)
        assert ratio == pytest.approx(128.0)

    def test_rank_doubling_halves_ratio(self, chal):
        r16 = chal.compression_ratio(4096, 32, 16, 7)
        r32 = chal.compression_ratio(4096, 32, 32, 7)
        assert r16 == pytest.approx(2 * r32)


class TestSanity:
    def test_lora_never_exceeds_full_below_rank_d(self, chal):
        for r in (4, 8, 16, 32, 64):
            assert chal.lora_param_count(4096, r) < chal.full_param_count(4096)

    def test_trainable_share_is_tiny(self, chal):
        # adapter params vs a real 7B total: well under 1% of the model
        _, lora = chal.model_param_counts(4096, 32, 16, 7)
        assert lora / 7e9 < 0.01
