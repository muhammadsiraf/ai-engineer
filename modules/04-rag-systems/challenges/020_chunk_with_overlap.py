"""Challenge 020 — Chunk with overlap.

Lesson: 050 — chunking strategies.

Word-level sliding window: chunk into windows of `chunk_size` words,
stepping by `chunk_size - overlap`, so consecutive chunks share exactly
`overlap` words (the sentence-straddling-a-boundary insurance).

Rules (tests encode them):
  - split on whitespace: text.split()
  - a trailing window FULLY CONTAINED in the previous chunk is skipped
    (it would be duplicate context, not overlap)
  - empty/whitespace-only text -> []
  - ValueError if chunk_size < 1, overlap < 0, or overlap >= chunk_size
    (the last would step backward forever)

Implement:

  chunk_text(text, chunk_size, overlap) -> list[str]
      each chunk is its words joined by single spaces

Worked example (tests encode it):
    12 words, chunk_size=5, overlap=3  →  step=2
    windows start at words 0,2,4,6,8 — the start-10 window is a subset
    of the start-8 window and is dropped → 5 chunks total.

Run:  pytest modules/04-rag-systems/challenges/test_020_chunk_with_overlap.py -v
"""


def chunk_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    raise NotImplementedError
