import pytest


def _load():
    import importlib.util

    path = __file__.replace("test_040_catch_regressions.py", "040_catch_regressions.py")
    spec = importlib.util.spec_from_file_location("chal_m7_040", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def chal():
    return _load()


BASELINE = {"billing": 0.90, "refund": 0.85, "shipping": 0.70}
CANDIDATE = {"billing": 0.85, "refund": 0.85, "shipping": 0.71, "returns": 0.50}


class TestCategoryScores:
    def test_mean_per_category(self, chal):
        results = [
            {"category": "billing", "score": 0.8},
            {"category": "billing", "score": 1.0},
            {"category": "shipping", "score": 0.6},
        ]
        scores = chal.category_scores(results)
        assert scores["billing"] == pytest.approx(0.9)
        assert scores["shipping"] == pytest.approx(0.6)

    def test_extra_keys_ignored(self, chal):
        results = [{"category": "billing", "score": 1.0, "id": "c1", "ms": 900}]
        assert chal.category_scores(results) == {"billing": 1.0}

    def test_empty_results(self, chal):
        assert chal.category_scores([]) == {}


class TestFindRegressions:
    def test_regression_flagged(self, chal):
        assert chal.find_regressions(BASELINE, CANDIDATE) == ["billing"]

    def test_small_drop_passes(self, chal):
        cand = dict(BASELINE, billing=0.89)  # drop 0.01, inside the slack
        assert chal.find_regressions(BASELINE, cand) == []

    def test_exact_slack_passes(self, chal):
        cand = dict(BASELINE, billing=0.88)  # drop == max_drop
        assert chal.find_regressions(BASELINE, cand) == []

    def test_new_and_removed_categories_ignored(self, chal):
        assert chal.find_regressions({"a": 0.9}, {"b": 0.0}) == []

    def test_sorted_worst_first(self, chal):
        base = {"a": 0.9, "b": 0.8, "c": 0.7}
        cand = {"a": 0.82, "b": 0.70, "c": 0.69}  # drops: a 0.08, b 0.10, c 0.01
        assert chal.find_regressions(base, cand) == ["b", "a"]

    def test_negative_slack_rejected(self, chal):
        with pytest.raises(ValueError):
            chal.find_regressions(BASELINE, CANDIDATE, max_drop=-0.01)


class TestGate:
    def test_fails_on_regression(self, chal):
        assert chal.gate(BASELINE, CANDIDATE) is False

    def test_passes_within_slack(self, chal):
        cand = dict(BASELINE, billing=0.885)  # drop 0.015
        assert chal.gate(BASELINE, cand) is True

    def test_disjoint_categories_pass(self, chal):
        assert chal.gate({"a": 1.0}, {"b": 0.0}) is True


class TestDiffReport:
    def test_common_only_and_sorted(self, chal):
        report = chal.diff_report(BASELINE, CANDIDATE)
        assert list(report) == ["billing", "refund", "shipping"]
        assert report["billing"]["baseline"] == pytest.approx(0.90)
        assert report["billing"]["candidate"] == pytest.approx(0.85)
        assert report["billing"]["delta"] == pytest.approx(-0.05)
        assert report["shipping"]["delta"] == pytest.approx(0.01)
        assert "returns" not in report

    def test_improvement_positive_delta(self, chal):
        report = chal.diff_report({"a": 0.5}, {"a": 0.75})
        assert report["a"]["delta"] == pytest.approx(0.25)
