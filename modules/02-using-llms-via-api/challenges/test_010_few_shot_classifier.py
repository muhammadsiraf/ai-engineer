import pytest


def _load():
    import importlib.util

    path = __file__.replace("test_010_few_shot_classifier.py", "010_few_shot_classifier.py")
    spec = importlib.util.spec_from_file_location("chal_m2_010", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def chal():
    return _load()


@pytest.fixture()
def client():
    return chal.MockLLM()


EXAMPLES = [
    ("my card was charged twice this month", "billing"),
    ("where is my package, it says shipped", "shipping"),
    ("the app crashes when i open settings", "product"),
    ("refund the duplicate charge on my visa", "billing"),
]


class TestBuildMessages:
    def test_structure(self, chal):
        msgs = chal.build_few_shot_messages(
            "You classify support tickets.", EXAMPLES, "my package never arrived"
        )
        assert msgs[0] == {"role": "system", "content": "You classify support tickets."}
        roles = [m["role"] for m in msgs[1:]]
        assert roles == ["user", "assistant"] * 4 + ["user"]
        assert msgs[-1]["role"] == "user"
        assert msgs[-1]["content"].startswith("<ticket>")
        assert msgs[-1]["content"].endswith("</ticket>")
        assert "my package never arrived" in msgs[-1]["content"]

    def test_empty_examples(self, chal):
        msgs = chal.build_few_shot_messages("sys", [], "hello")
        assert [m["role"] for m in msgs] == ["system", "user"]

    def test_no_pool_mutation(self, chal):
        before = list(EXAMPLES)
        chal.build_few_shot_messages("s", EXAMPLES, "x")
        assert EXAMPLES == before


class TestClassify:
    def test_billing(self, chal, client):
        assert chal.classify(client, EXAMPLES, "i was charged twice on my card") == "billing"

    def test_shipping(self, chal, client):
        assert chal.classify(client, EXAMPLES, "where is my package") == "shipping"

    def test_unknown_label_raises(self, chal, client):
        with pytest.raises(ValueError):
            chal.classify(client, [], "anything at all")

    def test_messages_passed_through(self, chal, client):
        chal.classify(client, EXAMPLES, "app crashes on settings screen")
        assert client.last_messages is not None
        assert client.last_messages[0]["role"] == "system"


class TestSelectExamples:
    def test_k_limit(self, chal):
        out = chal.select_examples(EXAMPLES, "refund my card charge", 2)
        assert len(out) == 2
        assert out[0] == EXAMPLES[3]  # most overlap: refund/charge/card

    def test_k_over_pool_size(self, chal):
        out = chal.select_examples(EXAMPLES, "zzz", 99)
        assert len(out) == 4

    def test_best_first_order(self, chal):
        out = chal.select_examples(EXAMPLES, "package shipment tracking info", 3)
        assert out[0] == EXAMPLES[1]

    def test_k_zero(self, chal):
        assert chal.select_examples(EXAMPLES, "x", 0) == []
