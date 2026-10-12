import pytest


def _load():
    import importlib.util

    path = __file__.replace("test_040_route_to_worker.py", "040_route_to_worker.py")
    spec = importlib.util.spec_from_file_location("chal_m8_040", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def chal():
    return _load()


RULES = {
    "billing": ["refund", "invoice", "charge"],
    "shipping": ["package", "delivery", "track"],
}


class TestScore:
    def test_counts(self, chal):
        s = chal.score_workers(RULES, "Where is my refund for the lost package?")
        assert s == {"billing": 1, "shipping": 1}

    def test_clear_winner(self, chal):
        s = chal.score_workers(RULES, "I need a refund and my invoice corrected")
        assert s["billing"] == 2
        assert s["shipping"] == 0

    def test_case_insensitive(self, chal):
        assert chal.score_workers(RULES, "REFUND please")["billing"] == 1

    def test_whole_words_only(self, chal):
        rules = {"orders": ["order"], "greet": ["arrived"]}
        assert chal.score_workers(rules, "my preorder arrived") == {
            "orders": 0,
            "greet": 1,
        }

    def test_repeated_keyword_counts_twice(self, chal):
        assert chal.score_workers(RULES, "refund and another refund")["billing"] == 2

    def test_empty_query(self, chal):
        assert chal.score_workers(RULES, "") == {"billing": 0, "shipping": 0}


class TestRoute:
    def test_tie_goes_alphabetical(self, chal):
        assert chal.route(RULES, "refund for the package") == "billing"

    def test_winner(self, chal):
        assert (
            chal.route(RULES, "I need a refund and my invoice corrected") == "billing"
        )
        assert chal.route(RULES, "track my delivery") == "shipping"

    def test_default_on_no_hits(self, chal):
        assert chal.route(RULES, "hello there") == "general"

    def test_default_override(self, chal):
        assert chal.route(RULES, "hello there", default="triage") == "triage"


class TestMargin:
    def test_margin_counts(self, chal):
        assert chal.margin({"billing": 2, "shipping": 1}) == 1

    def test_tie_margin_zero(self, chal):
        assert chal.margin({"billing": 1, "shipping": 1}) == 0

    def test_single_worker(self, chal):
        assert chal.margin({"billing": 3}) == 3
