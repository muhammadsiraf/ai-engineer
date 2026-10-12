import pytest


def _load():
    import importlib.util

    path = __file__.replace("test_020_debias_llm_judge.py", "020_debias_llm_judge.py")
    spec = importlib.util.spec_from_file_location("chal_m7_020", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def chal():
    return _load()


def R(a, b, winner):
    return {"a": a, "b": b, "winner": winner}


class TestVerdict:
    def test_agreement_both_orders(self, chal):
        results = [R("A", "B", "A"), R("B", "A", "A")]  # A wins either way
        assert chal.debiased_verdict(results, "A", "B") == "a"

    def test_agreement_for_b(self, chal):
        results = [R("A", "B", "B"), R("B", "A", "B")]
        assert chal.debiased_verdict(results, "A", "B") == "b"

    def test_position_bias_split_is_tie(self, chal):
        # whoever is listed first wins — the canonical bias signature
        results = [R("C", "D", "C"), R("D", "C", "D")]
        assert chal.debiased_verdict(results, "C", "D") == "tie"

    def test_missing_order_raises(self, chal):
        results = [R("A", "B", "A")]
        with pytest.raises(ValueError):
            chal.debiased_verdict(results, "A", "B")

    def test_duplicate_orders_use_latest_or_any_consistently(self, chal):
        # duplicates of the same order must not invent a verdict alone
        results = [R("A", "B", "A"), R("A", "B", "A")]
        with pytest.raises(ValueError):
            chal.debiased_verdict(results, "A", "B")


class TestWinRate:
    def test_sweeps(self, chal):
        results = [
            R("A", "B", "A"), R("B", "A", "A"),
            R("A", "C", "A"), R("C", "A", "A"),
        ]
        assert chal.debiased_win_rate(results, "A") == pytest.approx(1.0)
        assert chal.debiased_win_rate(results, "B") == pytest.approx(0.0)

    def test_ties_count_half(self, chal):
        results = [
            R("A", "B", "A"), R("B", "A", "A"),       # A win
            R("A", "C", "C"), R("C", "A", "C"),       # A loss
            R("A", "D", "A"), R("D", "A", "D"),       # tie
        ]
        assert chal.debiased_win_rate(results, "A") == pytest.approx((1.0 + 0.0 + 0.5) / 3)

    def test_unpaired_order_only_not_counted(self, chal):
        # a single-order result is not evidence — excluded from the rate
        results = [R("A", "B", "A"), R("B", "A", "A"), R("A", "E", "A")]
        assert chal.debiased_win_rate(results, "A") == pytest.approx(1.0)

    def test_unknown_item_raises(self, chal):
        with pytest.raises(ValueError):
            chal.debiased_win_rate([R("A", "B", "A")], "Z")


class TestPositionBiasIndex:
    def test_lesson_number_point_two(self, chal):
        # 20 comparisons: A first → 13 wins (65%); A second → 9 wins (45%)
        results = [R("A", "B", "A") for _ in range(13)] + [
            R("A", "B", "B") for _ in range(7)
        ]
        results += [R("B", "A", "A") for _ in range(9)] + [
            R("B", "A", "B") for _ in range(11)
        ]
        assert chal.position_bias_index(results, "A") == pytest.approx(0.65 - 0.45)

    def test_no_bias_is_zero(self, chal):
        results = [
            R("A", "B", "A"), R("A", "B", "A"),   # A first: 100% wins
            R("B", "A", "A"), R("B", "A", "A"),   # A second: 100% wins
        ]
        assert chal.position_bias_index(results, "A") == pytest.approx(0.0)

    def test_negative_bias(self, chal):
        results = [R("A", "B", "B"), R("B", "A", "A")]  # A never wins when first
        assert chal.position_bias_index(results, "A") == pytest.approx(-1.0)
