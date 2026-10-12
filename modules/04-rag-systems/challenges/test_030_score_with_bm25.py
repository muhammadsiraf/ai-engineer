import math

import pytest


def _load():
    import importlib.util

    path = __file__.replace("test_030_score_with_bm25.py", "030_score_with_bm25.py")
    spec = importlib.util.spec_from_file_location("chal_m4_030", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def chal():
    return _load()


@pytest.fixture(scope="module")
def bm25(chal):
    return chal.BM25(["term a b c", "term term a b", "term term term a"])


def expected_idf(n_docs: int, df: int) -> float:
    return math.log((n_docs - df + 0.5) / (df + 0.5) + 1)


class TestTokenize:
    def test_lowercases_and_strips_punctuation(self, chal):
        assert chal.BM25.tokenize("ERR-0x4512 was FIXED!") == [
            "err", "0x4512", "was", "fixed",
        ]

    def test_apostrophe_splits(self, chal):
        assert chal.BM25.tokenize("don't panic") == ["don", "t"]


class TestIDF:
    def test_rare_beats_common(self, chal):
        corpus = chal.BM25(["apple banana cherry", "banana cherry dog", "cherry dog cat"])
        assert corpus.idf("apple") > corpus.idf("banana") > corpus.idf("cherry")

    def test_all_positive_even_when_df_equals_n(self, bm25):
        # df(term) == N here; the +1 inside the log keeps idf positive
        assert bm25.idf("term") > 0

    def test_exact_value(self, bm25):
        assert bm25.idf("term") == pytest.approx(expected_idf(3, 3))

    def test_unseen_term_is_zero(self, bm25):
        assert bm25.idf("zebra") == 0.0


class TestScore:
    def test_more_occurrences_score_higher(self, bm25):
        s = [bm25.score("term", i) for i in range(3)]
        assert s[0] < s[1] < s[2]

    def test_saturation_is_concave(self, bm25):
        s = [bm25.score("term", i) for i in range(3)]
        assert (s[1] - s[0]) > (s[2] - s[1])  # 2nd occurrence buys more than 3rd

    def test_scores_bounded_by_k1_plus_one_times_idf(self, bm25):
        ceiling = (1.5 + 1) * bm25.idf("term")
        for i in range(3):
            assert bm25.score("term", i) < ceiling

    def test_hand_computed_value(self, bm25):
        # doc0: tf=1, |d|=4, avgdl=4 → norm term = 1
        # score = idf * 1*(k1+1)/(1 + k1) = idf
        assert bm25.score("term", 0) == pytest.approx(expected_idf(3, 3))

    def test_no_match_is_zero(self, bm25):
        assert bm25.score("zebra", 0) == 0.0
        assert bm25.score("zebra term", 0) == bm25.score("term", 0)  # zebra adds nothing

    def test_multi_term_sums(self, bm25):
        # query with two known terms must beat either term alone on doc 1
        s_a = bm25.score("a", 1)
        s_b = bm25.score("b", 1)
        s_ab = bm25.score("a b", 1)
        assert s_ab == pytest.approx(s_a + s_b)

    def test_length_normalization_favors_short_docs(self, chal):
        corpus = chal.BM25(["term", "term b c d e f g h i j"], k1=1.5, b=0.75)
        assert corpus.score("term", 0) > corpus.score("term", 1)

    def test_b_zero_disables_length_normalization(self, chal):
        corpus = chal.BM25(["term", "term b c d e f g h i j"], k1=1.5, b=0.0)
        assert corpus.score("term", 0) == pytest.approx(corpus.score("term", 1))


class TestSearch:
    def test_ranked_best_first(self, bm25):
        got = bm25.search("term")
        assert [i for i, _ in got] == [2, 1, 0]
        assert [s for _, s in got] == sorted([s for _, s in got], reverse=True)

    def test_k_limits_results(self, bm25):
        assert len(bm25.search("term", k=2)) == 2
        assert [i for i, _ in bm25.search("term", k=1)] == [2]

    def test_no_match_returns_empty(self, bm25):
        assert bm25.search("zebra") == []

    def test_ties_break_by_index(self, chal):
        corpus = chal.BM25(["cat", "cat", "cat"])
        got = corpus.search("cat")
        assert [i for i, _ in got] == [0, 1, 2]
        assert all(s == got[0][1] for _, s in got)
