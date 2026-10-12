import pytest


def _load():
    import importlib.util

    path = __file__.replace("test_020_chunk_with_overlap.py", "020_chunk_with_overlap.py")
    spec = importlib.util.spec_from_file_location("chal_m4_020", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def chal():
    return _load()


def words_of(chunk: str) -> list[str]:
    return chunk.split()


TWELVE = "w0 w1 w2 w3 w4 w5 w6 w7 w8 w9 w10 w11"


class TestBasic:
    def test_short_text_single_chunk(self, chal):
        assert chal.chunk_text("hello world", 5, 2) == ["hello world"]

    def test_empty_is_empty(self, chal):
        assert chal.chunk_text("", 5, 2) == []
        assert chal.chunk_text("   \n\t ", 4, 1) == []

    def test_no_overlap_tiles_exactly(self, chal):
        chunks = chal.chunk_text(TWELVE, 4, 0)
        assert [words_of(c)[0] for c in chunks] == ["w0", "w4", "w8"]
        assert all(len(words_of(c)) == 4 for c in chunks)

    def test_last_chunk_may_be_short(self, chal):
        chunks = chal.chunk_text(TWELVE, 5, 0)
        assert len(chunks) == 3
        assert len(words_of(chunks[-1])) == 2  # w10 w11


class TestOverlap:
    def test_consecutive_chunks_share_overlap_words(self, chal):
        chunks = chal.chunk_text(TWELVE, 5, 2)
        for a, b in zip(chunks, chunks[1:]):
            assert words_of(a)[-2:] == words_of(b)[:2]

    def test_step_is_size_minus_overlap(self, chal):
        chunks = chal.chunk_text(TWELVE, 5, 2)
        starts = [words_of(c)[0] for c in chunks]
        assert starts == ["w0", "w3", "w6", "w9"]


class TestTrailingSubsetRule:
    def test_lesson_example(self, chal):
        # starts 0,2,4,6,8; start-10 window ⊂ start-8 window → dropped
        chunks = chal.chunk_text(TWELVE, 5, 3)
        assert [words_of(c)[0] for c in chunks] == ["w0", "w2", "w4", "w6", "w8"]
        assert len(words_of(chunks[-1])) == 4  # w8..w11

    def test_no_subset_when_last_chunk_extends(self, chal):
        # 12 words, size 8, overlap 3 → step 5: starts 0, 5 → w5..w11 covers end
        chunks = chal.chunk_text(TWELVE, 8, 3)
        assert [words_of(c)[0] for c in chunks] == ["w0", "w5"]


class TestValidation:
    def test_bad_chunk_size(self, chal):
        with pytest.raises(ValueError):
            chal.chunk_text(TWELVE, 0, 0)
        with pytest.raises(ValueError):
            chal.chunk_text(TWELVE, -3, 0)

    def test_negative_overlap(self, chal):
        with pytest.raises(ValueError):
            chal.chunk_text(TWELVE, 5, -1)

    def test_overlap_ge_size(self, chal):
        with pytest.raises(ValueError):
            chal.chunk_text(TWELVE, 5, 5)
        with pytest.raises(ValueError):
            chal.chunk_text(TWELVE, 5, 6)


class TestReconstruction:
    def test_chunks_reassemble_original_order(self, chal):
        text = " ".join(f"word{i}" for i in range(40))
        chunks = [words_of(c) for c in chal.chunk_text(text, 7, 2)]
        rebuilt = list(chunks[0])
        for nxt in chunks[1:]:
            rebuilt.extend(nxt[2:])  # skip the 2 overlap words
        assert rebuilt == [f"word{i}" for i in range(40)]
