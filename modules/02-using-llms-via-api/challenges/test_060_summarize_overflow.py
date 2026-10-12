import pytest


def _load():
    import importlib.util

    path = __file__.replace("test_060_summarize_overflow.py", "060_summarize_overflow.py")
    spec = importlib.util.spec_from_file_location("chal_m2_060", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def chal():
    return _load()


class FakeTok:
    """1 token per char."""

    def encode(self, text: str) -> list[int]:
        return [0] * len(text)


@pytest.fixture()
def tok():
    return FakeTok()


def msgs(*pairs, system="You are helpful."):
    out = [{"role": "system", "content": system}]
    for i, (u, a) in enumerate(pairs):
        out += [{"role": "user", "content": u}, {"role": "assistant", "content": a}]
    return out


def all_summaries_notice(m):
    return m["role"] == "assistant" and m["content"].startswith("[summary] ")


class TestFitHistory:
    def test_under_budget_untouched(self, chal, tok):
        m = msgs(("hi", "hello there"))
        out = chal.fit_history(m, 10_000, tok, lambda t: "s")
        assert out == m

    def test_system_prompt_always_first_and_verbatim(self, chal, tok):
        m = msgs(("a" * 200, "b" * 200), ("c" * 200, "d" * 200))
        out = chal.fit_history(m, 100, tok, lambda t: "s")
        assert out[0] == m[0]

    def test_oldest_pair_summarized_first(self, chal, tok):
        m = msgs(("one " * 50, "uno " * 50), ("two " * 5, "dos " * 5))
        order = []

        def summarize(text):
            order.append(text[:6])
            return "compact"

        out = chal.fit_history(m, 120, tok, summarize)
        assert order[0].startswith("one")
        assert any(all_summaries_notice(x) for x in out[1:])
        assert out[-1]["content"].startswith("dos")  # newest pair survives verbatim

    def test_iterates_until_under_budget(self, chal, tok):
        m = msgs(("p1", "q1"), ("p2", "q2"), ("p3", "q3"))
        calls = {"n": 0}

        def summarize(text):
            calls["n"] += 1
            return "tiny"

        out = chal.fit_history(m, 40, tok, summarize)
        # 40 = 3 base + msgs... with 1 pair + summary: sys(15+4) + s(5+4) + p3(2+4)+q3(2+4)=40
        assert calls["n"] == 2
        assert len(out) == 4  # system + summary + 2 latest
        assert sum(len(tok.encode(x["content"])) for x in out) + (4 * len(out)) + 3 <= 40

    def test_no_pairs_left_returns_system_only(self, chal, tok):
        m = msgs(("a" * 500, "b" * 500))
        out = chal.fit_history(m, 30, tok, lambda t: "s")
        assert out == [m[0]]

    def test_single_oversized_pair_kept(self, chal, tok):
        m = msgs(("a" * 500, "b" * 500))
        out = chal.fit_history(m, 40, tok, lambda t: "s")
        # can't summarize the only pair away to nothing AND keep latest pair;
        # per spec: last pair stays intact
        assert out[0] == m[0]
        assert out[1]["content"] == "a" * 500 or out[-1]["content"] == "b" * 500

    def test_input_not_mutated(self, chal, tok):
        m = msgs(("x" * 100, "y" * 100))
        snapshot = [dict(x) for x in m]
        chal.fit_history(m, 30, tok, lambda t: "s")
        assert m == snapshot
