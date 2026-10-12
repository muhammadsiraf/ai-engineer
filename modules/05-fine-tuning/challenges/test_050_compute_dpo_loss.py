import math

import pytest


def _load():
    import importlib.util

    path = __file__.replace("test_050_compute_dpo_loss.py", "050_compute_dpo_loss.py")
    spec = importlib.util.spec_from_file_location("chal_m5_050", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def chal():
    return _load()


ZEROS = (-1.0, -2.0, -1.0, -2.0)  # pc, pr, rc, rr — zero margin


class TestSigmoid:
    def test_midpoint(self, chal):
        assert chal.sigmoid(0.0) == pytest.approx(0.5)

    def test_positive(self, chal):
        assert chal.sigmoid(2.0) == pytest.approx(1 / (1 + math.exp(-2.0)))

    def test_extremes_do_not_overflow(self, chal):
        assert chal.sigmoid(50.0) == pytest.approx(1.0, abs=1e-12)
        assert chal.sigmoid(-50.0) == pytest.approx(0.0, abs=1e-12)
        assert chal.sigmoid(1000.0) == pytest.approx(1.0)


class TestDPOLoss:
    def test_no_signal_is_ln2(self, chal):
        assert chal.dpo_loss(*ZEROS) == pytest.approx(math.log(2))

    def test_positive_margin_below_ln2(self, chal):
        # chosen improved relative to ref; rejected didn't
        loss = chal.dpo_loss(-1.0, -2.0, -1.0, -3.0)  # margin = 1
        assert loss < math.log(2)

    def test_negative_margin_above_ln2(self, chal):
        loss = chal.dpo_loss(-1.0, -2.0, -2.0, -2.0)  # margin = -1
        assert loss > math.log(2)

    def test_monotone_in_margin(self, chal):
        losses = [
            chal.dpo_loss(-1.0, -1.0, -1.0 - m, -1.0)  # margin = m
            for m in (-2.0, -1.0, 0.0, 1.0, 2.0)
        ]
        assert losses == sorted(losses, reverse=True)

    def test_big_margin_near_zero(self, chal):
        # margin 10, beta 0.1 → z = 1.0 → L = -log σ(1) ≈ 0.313
        assert chal.dpo_loss(-1.0, -1.0, -11.0, -1.0) == pytest.approx(0.3133, abs=1e-3)
        # huge margin → ~0
        assert chal.dpo_loss(-1.0, -1.0, -501.0, -1.0) == pytest.approx(0.0, abs=1e-9)

    def test_beta_sharpens(self, chal):
        pc, pr, rc, rr = -1.0, -1.0, -3.0, -1.0  # margin 2
        assert chal.dpo_loss(pc, pr, rc, rr, beta=0.2) < chal.dpo_loss(pc, pr, rc, rr, beta=0.1)

    def test_reference_deltas_cancel(self, chal):
        # add 5 to policy AND ref logp of chosen → margin unchanged
        base = chal.dpo_loss(-1.0, -2.0, -1.5, -2.5)
        shifted = chal.dpo_loss(4.0, -2.0, 3.5, -2.5)
        assert shifted == pytest.approx(base)

    def test_raising_policy_chosen_lowers_loss(self, chal):
        assert chal.dpo_loss(0.5, -2.0, -1.0, -2.0) < chal.dpo_loss(-0.5, -2.0, -1.0, -2.0)

    def test_raising_policy_rejected_raises_loss(self, chal):
        assert chal.dpo_loss(-1.0, 0.5, -1.0, -2.0) > chal.dpo_loss(-1.0, -0.5, -1.0, -2.0)
