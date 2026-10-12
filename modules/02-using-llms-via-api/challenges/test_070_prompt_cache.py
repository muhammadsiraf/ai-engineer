import pytest


def _load():
    import importlib.util

    path = __file__.replace("test_070_prompt_cache.py", "070_prompt_cache.py")
    spec = importlib.util.spec_from_file_location("chal_m2_070", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def chal():
    return _load()


class FakeClock:
    def __init__(self):
        self.t = 1000.0

    def __call__(self):
        return self.t


@pytest.fixture()
def clock():
    return FakeClock()


def complete_counter():
    calls = {"n": 0}

    def complete(model, messages, **params):
        calls["n"] += 1
        return f"answer-{calls['n']}"

    complete.calls = calls
    return complete


MSGS = [{"role": "user", "content": "Where is my order?"}]


class TestKey:
    def test_deterministic(self, chal):
        c = chal.ResponseCache()
        assert c.key("m1", MSGS) == c.key("m1", MSGS)

    def test_different_model_differs(self, chal):
        c = chal.ResponseCache()
        assert c.key("m1", MSGS) != c.key("m2", MSGS)

    def test_whitespace_normalized(self, chal):
        c = chal.ResponseCache()
        a = c.key("m", [{"role": "user", "content": "hello   there"}])
        b = c.key("m", [{"role": "user", "content": "hello there"}])
        assert a == b

    def test_default_params_resolved(self, chal):
        c = chal.ResponseCache()
        assert c.key("m", MSGS, {}) == c.key("m", MSGS, {"temperature": 1.0, "max_tokens": None})

    def test_real_param_differs(self, chal):
        c = chal.ResponseCache()
        assert c.key("m", MSGS, {"temperature": 0.2}) != c.key("m", MSGS)

    def test_param_order_irrelevant(self, chal):
        c = chal.ResponseCache()
        assert c.key("m", MSGS, {"a": 1, "b": 2}) == c.key("m", MSGS, {"b": 2, "a": 1})


class TestGetPut:
    def test_roundtrip(self, chal):
        c = chal.ResponseCache()
        k = c.key("m", MSGS)
        assert c.get(k) is None
        c.put(k, "v")
        assert c.get(k) == "v"

    def test_expiry(self, chal, clock):
        c = chal.ResponseCache(ttl_seconds=10, clock=clock)
        k = c.key("m", MSGS)
        c.put(k, "v")
        clock.t += 9
        assert c.get(k) == "v"
        clock.t += 2
        assert c.get(k) is None


class TestWrap:
    def test_hit_second_call(self, chal, clock):
        c = chal.ResponseCache(clock=clock)
        inner = complete_counter()
        wrapped = c.wrap(inner)
        assert wrapped("m", MSGS) == "answer-1"
        assert wrapped("m", MSGS) == "answer-1"  # cached, not a second call
        assert inner.calls["n"] == 1
        assert c.stats == {"hits": 1, "misses": 1}

    def test_params_partition(self, chal, clock):
        c = chal.ResponseCache(clock=clock)
        inner = complete_counter()
        wrapped = c.wrap(inner)
        wrapped("m", MSGS, temperature=0.2)
        wrapped("m", MSGS, temperature=0.9)
        assert inner.calls["n"] == 2

    def test_expired_going_back_to_model(self, chal, clock):
        c = chal.ResponseCache(ttl_seconds=5, clock=clock)
        inner = complete_counter()
        wrapped = c.wrap(inner)
        wrapped("m", MSGS)
        clock.t += 6
        assert wrapped("m", MSGS) == "answer-2"
        assert inner.calls["n"] == 2

    def test_stats(self, chal, clock):
        c = chal.ResponseCache(clock=clock)
        wrapped = c.wrap(complete_counter())
        wrapped("m", MSGS)
        wrapped("m", MSGS)
        wrapped("m", MSGS)
        assert c.stats == {"hits": 2, "misses": 1}
