import math

import pytest


def _load():
    import importlib.util

    path = __file__.replace("test_040_compute_sft_loss.py", "040_compute_sft_loss.py")
    spec = importlib.util.spec_from_file_location("chal_m5_040", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def chal():
    return _load()


class TestBuildLabels:
    def test_docstring_example(self, chal):
        # ids [10, 11, 12, 13], response starts at index 2
        # position 1 predicts 12, position 2 predicts 13
        assert chal.build_labels([10, 11, 12, 13], 2) == [-100, 12, 13, -100]

    def test_full_response_masks_nothing_interior(self, chal):
        labels = chal.build_labels([1, 2, 3, 4], 0)
        assert labels == [2, 3, 4, -100]

    def test_single_response_token(self, chal):
        # only token index 2 is response; it is *predicted* by position 1
        assert chal.build_labels([5, 6, 7], 2) == [-100, 7, -100]

    def test_whole_sequence_response(self, chal):
        labels = chal.build_labels([9, 8, 7], 0)
        assert labels == [8, 7, -100]

    def test_no_response_raises(self, chal):
        with pytest.raises(ValueError):
            chal.build_labels([1, 2, 3], 3)
        with pytest.raises(ValueError):
            chal.build_labels([1, 2, 3], 10)

    def test_last_position_always_ignored(self, chal):
        assert chal.build_labels([1, 2, 3], 1)[-1] == -100


class TestMaskedCE:
    def test_uniform_logits_give_ln_vocab(self, chal):
        logits = [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]
        labels = [1, 2]
        assert chal.masked_cross_entropy(logits, labels) == pytest.approx(math.log(3))

    def test_two_vocab_coin_flip(self, chal):
        assert chal.masked_cross_entropy([[0.0, 0.0]], [1]) == pytest.approx(math.log(2))

    def test_confident_prediction_near_zero_loss(self, chal):
        assert chal.masked_cross_entropy([[100.0, 0.0]], [0]) == pytest.approx(0.0, abs=1e-6)

    def test_wrong_confident_prediction_costs_dearly(self, chal):
        assert chal.masked_cross_entropy([[100.0, 0.0]], [1]) == pytest.approx(100.0, abs=1e-6)

    def test_ignored_positions_skipped(self, chal):
        # position 0 would be a terrible prediction — must not affect loss
        logits = [[0.0, 100.0], [0.0, 0.0]]
        labels = [-100, 1]
        assert chal.masked_cross_entropy(logits, labels) == pytest.approx(math.log(2))

    def test_mean_not_sum(self, chal):
        logits = [[0.0, 0.0], [0.0, 0.0]]
        single = chal.masked_cross_entropy(logits[:1], [1])
        double = chal.masked_cross_entropy(logits, [1, 1])
        assert double == pytest.approx(single)  # both are ln 2 (mean preserved)

    def test_all_masked_raises(self, chal):
        with pytest.raises(ValueError):
            chal.masked_cross_entropy([[0.0, 0.0]], [-100])


class TestPipeline:
    def test_prompt_logits_do_not_matter(self, chal):
        ids = [0, 1, 2, 3]
        labels = chal.build_labels(ids, 2)  # [-100, 2, 3, -100]
        noisy = [[500.0, -500.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0]]
        clean = [[0.0, 0.0, 0.0, 0.0]] * 4
        # only positions 1 and 2 count; position 0 (the noisy one) is masked
        assert chal.masked_cross_entropy(noisy, labels) == pytest.approx(
            chal.masked_cross_entropy(clean, labels)
        )

    def test_uniform_pipeline_loss(self, chal):
        ids = [0, 1, 2, 3]
        labels = chal.build_labels(ids, 2)
        logits = [[0.0] * 4] * 4
        assert chal.masked_cross_entropy(logits, labels) == pytest.approx(math.log(4))
