import pytest


def _load():
    import importlib.util

    path = __file__.replace("test_050_cost_estimator_tiktoken.py", "050_cost_estimator_tiktoken.py")
    spec = importlib.util.spec_from_file_location("chal_m2_050", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def chal():
    return _load()


@pytest.fixture()
def est(chal):
    return chal.CostEstimator(chal.FakeTokenizer(), dict(chal.MODELS))


MSGS = [
    {"role": "system", "content": "You are terse."},          # 12 chars -> 3 tok
    {"role": "user", "content": "Where is my order?"},        # 17 chars -> 5 tok
]


class TestCounting:
    def test_message_includes_overhead(self, est):
        # "You are terse." = 14 chars -> ceil(17/4)=4 tokens + 4 overhead = 8
        assert est.count_message(MSGS[0]) == 4 + 4

    def test_request_base_and_tools(self, est):
        base = est.count_request(MSGS)
        # (3+4) + (5+4) + base 3 = 19
        assert base == 19
        with_tools = est.count_request(MSGS, tools=[{"fake": 1}, {"fake": 2}])
        assert with_tools == base + 2 * 8

    def test_empty_messages(self, est):
        assert est.count_request([]) == 3


class TestFits:
    def test_plenty_of_room(self, est):
        assert est.fits(MSGS, "flagship", 4_000) is True

    def test_output_pushes_over(self, est):
        assert est.fits(MSGS, "mini", 16_000) is False
        assert est.fits(MSGS, "mini", 15_981) is True   # 19 + 15981 == 16000

    def test_boundary_exact_fit(self, est):
        assert est.fits(MSGS, "mini", 16_000 - 19) is True
        assert est.fits(MSGS, "mini", 16_000 - 18) is False


class TestCost:
    def test_simple(self, est):
        # 2k in, 500 out on flagship: 2000*3/1e6 + 500*15/1e6
        expected = 2000 * 3.0 / 1e6 + 500 * 15.0 / 1e6
        assert est.estimate_cost("flagship", 2000, 500) == pytest.approx(expected)

    def test_unknown_model_raises(self, est):
        with pytest.raises(KeyError):
            est.estimate_cost("gpt-who", 10, 10)

    def test_rounding_at_end(self, est):
        v = est.estimate_cost("mini", 3333, 777)
        assert round(v, 6) == v


class TestQuote:
    def test_full_shape(self, est):
        q = est.quote(MSGS, "flagship", expected_output_tokens=150)
        assert q["input_tokens"] == 19
        assert q["output_tokens"] == 150
        assert q["fits"] is True
        assert q["cost_usd"] == pytest.approx(19 * 3.0 / 1e6 + 150 * 15.0 / 1e6)

    def test_over_limit_marks_not_fits(self, est):
        q = est.quote(MSGS, "mini", expected_output_tokens=15_990)
        assert q["fits"] is False

    def test_zero_output(self, est):
        q = est.quote(MSGS, "mini", 0)
        assert q["cost_usd"] == pytest.approx(19 * 0.15 / 1e6)
