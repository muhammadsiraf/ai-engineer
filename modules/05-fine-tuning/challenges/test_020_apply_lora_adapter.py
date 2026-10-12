import pytest


def _load():
    import importlib.util

    path = __file__.replace("test_020_apply_lora_adapter.py", "020_apply_lora_adapter.py")
    spec = importlib.util.spec_from_file_location("chal_m5_020", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def chal():
    return _load()


I2 = [[1.0, 0.0], [0.0, 1.0]]
A = [[5.0, 6.0], [7.0, 8.0]]      # r=2, d=2
B = [[1.0, 2.0], [3.0, 4.0]]      # d=2, r=2
X = [1.0, 2.0]


class TestMatvec:
    def test_identity(self, chal):
        assert chal.matvec(I2, X) == pytest.approx([1.0, 2.0])

    def test_simple(self, chal):
        W = [[2.0, 0.0], [0.0, 3.0]]
        assert chal.matvec(W, X) == pytest.approx([2.0, 6.0])

    def test_shape_mismatch_raises(self, chal):
        with pytest.raises(ValueError):
            chal.matvec(I2, [1.0, 2.0, 3.0])


class TestApply:
    def test_zero_B_starts_at_base(self, chal):
        z = [[0.0, 0.0], [0.0, 0.0]]
        assert chal.apply_lora(I2, A, z, alpha=4, r=2, x=X) == pytest.approx(X)

    def test_hand_computed(self, chal):
        # Ax = [17, 23]; B(Ax) = [63, 143]; scale α/r = 2 → delta [126, 286]
        # h = [1, 2] + [126, 286] = [127, 288]
        assert chal.apply_lora(I2, A, B, alpha=4, r=2, x=X) == pytest.approx([127.0, 288.0])

    def test_alpha_doubles_delta_not_base(self, chal):
        h1 = chal.apply_lora(I2, A, B, alpha=4, r=2, x=X)
        h2 = chal.apply_lora(I2, A, B, alpha=8, r=2, x=X)
        base = chal.matvec(I2, X)
        d1 = [a - b for a, b in zip(h1, base)]
        d2 = [a - b for a, b in zip(h2, base)]
        assert d2 == pytest.approx([2 * v for v in d1])
        assert d1[0] != 0  # delta is real for this fixture

    def test_alpha_equal_r_gives_unit_scale(self, chal):
        # α = r → delta = B(Ax) exactly
        delta = [63.0, 143.0]
        h = chal.apply_lora(I2, A, B, alpha=2, r=2, x=X)
        assert h == pytest.approx([1.0 + delta[0], 2.0 + delta[1]])


class TestMerge:
    def test_merge_matches_apply(self, chal):
        W = chal.merge(I2, A, B, alpha=4, r=2)
        assert chal.matvec(W, X) == pytest.approx(chal.apply_lora(I2, A, B, alpha=4, r=2, x=X))

    def test_merge_value(self, chal):
        # B@A = [[19,22],[43,50]]; ×2 + I = [[39,44],[86,101]]
        assert chal.merge(I2, A, B, alpha=4, r=2) == pytest.approx(
            [[39.0, 44.0], [86.0, 101.0]]
        )

    def test_zero_B_merge_is_identity(self, chal):
        z = [[0.0, 0.0], [0.0, 0.0]]
        assert chal.merge(I2, z, B, alpha=4, r=2) == pytest.approx(I2)
