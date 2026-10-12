import pytest


def _load():
    import importlib.util

    path = __file__.replace("test_040_fuse_with_rrf.py", "040_fuse_with_rrf.py")
    spec = importlib.util.spec_from_file_location("chal_m4_040", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def chal():
    return _load()


class TestScore:
    def test_docstring_example_symmetry(self, chal):
        rankings = [["A", "B", "C"], ["B", "A", "C"]]
        assert chal.rrf_score("A", rankings) == pytest.approx(
            chal.rrf_score("B", rankings)
        )
        assert chal.rrf_score("A", rankings) == pytest.approx(1 / 61 + 1 / 62)

    def test_absent_contributes_zero(self, chal):
        rankings = [["X", "P"], ["Y", "P"]]
        assert chal.rrf_score("X", rankings) == pytest.approx(1 / 61)
        assert chal.rrf_score("nowhere", rankings) == 0.0

    def test_consensus_beats_specialist(self, chal):
        rankings = [["X", "P", "Q"], ["Y", "P", "Q"]]
        assert chal.rrf_score("P", rankings) > chal.rrf_score("X", rankings)
        assert chal.rrf_score("P", rankings) == pytest.approx(2 / 62)

    def test_k_flattening(self, chal):
        # rank1 vs rank10 in a single list: gap shrinks as k grows
        rankings = [["a"] + [f"d{i}" for i in range(9)]]
        gap_small_k = chal.rrf_score("a", rankings, k=1) - chal.rrf_score("d8", rankings, k=1)
        gap_big_k = chal.rrf_score("a", rankings, k=1000) - chal.rrf_score("d8", rankings, k=1000)
        assert gap_small_k > gap_big_k > 0

    def test_negative_k_raises(self, chal):
        with pytest.raises(ValueError):
            chal.rrf_score("A", [["A"]], k=-1)


class TestFuse:
    def test_docstring_example_order(self, chal):
        rankings = [["A", "B", "C"], ["B", "A", "C"]]
        got = chal.fuse(rankings)
        # A and B tie; tie broken by doc_id ascending
        assert [d for d, _ in got] == ["A", "B", "C"]

    def test_consensus_ordering(self, chal):
        rankings = [["X", "P", "Q"], ["Y", "P", "Q"]]
        assert [d for d, _ in chal.fuse(rankings)] == ["P", "Q", "X", "Y"]

    def test_single_list_preserves_order(self, chal):
        rankings = [["m", "n", "o"]]
        assert [d for d, _ in chal.fuse(rankings)] == ["m", "n", "o"]

    def test_three_rankings(self, chal):
        rankings = [
            ["p", "q", "r"],
            ["q", "p", "r"],
            ["p", "r", "q"],
        ]
        scores = dict(chal.fuse(rankings))
        # p: 1/61 + 1/62 + 1/61 ; q: 1/62 + 1/61 + 1/63 ; r: 1/63 + 1/63 + 1/62
        assert scores["p"] > scores["q"] > scores["r"]
        assert scores["p"] == pytest.approx(1 / 61 + 1 / 62 + 1 / 61)

    def test_all_docs_present(self, chal):
        rankings = [["a", "b"], ["c"]]
        assert {d for d, _ in chal.fuse(rankings)} == {"a", "b", "c"}

    def test_empty_rankings(self, chal):
        assert chal.fuse([]) == []
