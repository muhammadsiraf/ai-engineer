import math

import pytest


def _load():
    import importlib.util

    path = __file__.replace("test_010_perplexity_from_logprobs.py", "010_perplexity_from_logprobs.py")
    spec = importlib.util.spec_from_file_location("chal_m7_010", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def chal():
    return _load()


class TestPerplexity:
    @pytest.mark.parametrize("v", [2, 4, 8, 100, 50257])
    def test_uniform_is_vocab_size(self, chal, v):
        lp = [-math.log(v)] * 7
        assert chal.perplexity(lp) == pytest.approx(v)

    def test_two_coin_flips(self, chal):
        assert chal.perplexity([math.log(0.5), math.log(0.5)]) == pytest.approx(2.0)

    def test_certain_token_is_one(self, chal):
        assert chal.perplexity([0.0]) == pytest.approx(1.0)

    def test_mix_averages_in_log_space(self, chal):
        # one certain + one uniform-over-4: mean loss = (0 + ln4)/2
        ppl = chal.perplexity([0.0, -math.log(4)])
        assert ppl == pytest.approx(math.exp(math.log(4) / 2))  # = 2

    def test_order_does_not_matter(self, chal):
        a = chal.perplexity([-1.0, -2.0, -3.0])
        b = chal.perplexity([-3.0, -1.0, -2.0])
        assert a == pytest.approx(b)

    def test_empty_raises(self, chal):
        with pytest.raises(ValueError):
            chal.perplexity([])


class TestBits:
    def test_uniform_over_four(self, chal):
        # each token: -log2(0.25) = 2 bits → PPL = 2^2 = 4
        assert chal.perplexity_from_bits([-2.0, -2.0]) == pytest.approx(4.0)

    def test_matches_nats_version(self, chal):
        nats = [-1.5, -0.5, -2.0]
        bits = [v / math.log(2) for v in nats]
        assert chal.perplexity_from_bits(bits) == pytest.approx(chal.perplexity(nats))


class TestInterpret:
    def test_bands(self, chal):
        assert chal.interpret(5.0) == "confident"
        assert chal.interpret(50.0) == "typical"
        assert chal.interpret(500.0) == "uncertain"

    def test_boundaries(self, chal):
        assert chal.interpret(10.0) == "typical"
        assert chal.interpret(100.0) == "uncertain"
