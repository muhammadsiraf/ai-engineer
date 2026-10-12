import numpy as np
import pytest


def _load():
    import importlib.util

    path = __file__.replace("test_080_autoregressive_generation.py", "080_autoregressive_generation.py")
    spec = importlib.util.spec_from_file_location("chal080", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def chal():
    return _load()


def always_eos(logits):
    return chal_eos


chal_eos = 0


class TestGreedy:
    def test_argmax(self, chal):
        logits = np.array([0.1, 3.0, 1.0])
        assert chal.greedy(logits) == 1

    def test_tie_lowest_id(self, chal):
        logits = np.array([2.0, 2.0, 1.0])
        assert chal.greedy(logits) == 0


class TestGenerate:
    def test_appends_exactly_max_new_tokens(self, chal):
        model = chal.BigramStyleLM(vocab_size=10, seed=1)
        prompt = [5]
        out = chal.generate(model, prompt, max_new_tokens=7, sample_fn=chal.greedy)
        assert out[:1] == [5]
        assert len(out) == 8  # prompt preserved + 7 new

    def test_prompt_not_mutated(self, chal):
        model = chal.BigramStyleLM(seed=2)
        prompt = [3, 4]
        chal.generate(model, prompt, max_new_tokens=5, sample_fn=chal.greedy)
        assert prompt == [3, 4]

    def test_stops_on_eos(self, chal):
        model = chal.BigramStyleLM(vocab_size=10, seed=3)
        # force the model to always prefer EOS from any state
        model.table[:, :] = -100.0
        model.table[:, chal.EOS] = 100.0
        out = chal.generate(model, [1], max_new_tokens=50, sample_fn=chal.greedy)
        assert out == [1]  # EOS sampled immediately -> nothing appended

    def test_stops_on_eos_midway(self, chal):
        model = chal.BigramStyleLM(vocab_size=10, seed=4)
        model.table[5, :] = 0.0
        model.table[5, 8] = 50.0   # 5 -> 8
        model.table[8, :] = 0.0
        model.table[8, chal.EOS] = 50.0  # 8 -> EOS
        out = chal.generate(model, [5], max_new_tokens=50, sample_fn=chal.greedy)
        assert out == [5, 8]

    def test_conditions_on_growing_context(self, chal):
        model = chal.BigramStyleLM(vocab_size=10, seed=5)
        # chain: 1 -> 2 -> 3 -> EOS using the mock's per-token preferences
        model.table[1, :] = 0.0
        model.table[1, 2] = 50.0
        model.table[2, :] = 0.0
        model.table[2, 3] = 50.0
        model.table[3, :] = 0.0
        model.table[3, chal.EOS] = 50.0
        out = chal.generate(model, [1], max_new_tokens=10, sample_fn=chal.greedy)
        assert out == [1, 2, 3]

    def test_passes_full_sequence_each_call(self, chal):
        model = chal.BigramStyleLM(vocab_size=10, seed=6)
        # lengths of the sequences passed to logits() must grow 1,2,3,...
        model.table[:, :] = 0.0
        model.table[:, chal.EOS] = 100.0  # EOS everywhere -> ends after prompt
        chal.generate(model, [4], max_new_tokens=1, sample_fn=chal.greedy)
        assert model.calls == [1]

    def test_max_new_zero(self, chal):
        model = chal.BigramStyleLM(seed=7)
        out = chal.generate(model, [9], max_new_tokens=0, sample_fn=chal.greedy)
        assert out == [9]
        assert model.calls == []
