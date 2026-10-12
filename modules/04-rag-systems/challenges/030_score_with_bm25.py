"""Challenge 030 — Score a document with BM25.

Lesson: 070 — BM25 and sparse retrieval.

    tokenize:  re.findall(r"[a-z0-9]+", text.lower())
    idf(t)     = ln( (N − df + 0.5) / (df + 0.5) + 1 )     (df = 0 → 0.0)
    score(q,d) = Σ_t  idf(t) · tf(t,d)·(k1+1) / (tf(t,d) + k1·(1 − b + b·|d|/avgdl))

    defaults k1=1.5, b=0.75; natural log (math.log)

Implement class `BM25`:

  - __init__(corpus: list[str], k1: float = 1.5, b: float = 0.75)
  - tokenize(text) -> list[str]                    (staticmethod)
  - idf(term) -> float
  - score(query: str, doc_index: int) -> float
  - search(query: str, k: int = 10) -> list[tuple[int, float]]
        only documents with score > 0, best first;
        ties broken by lower index; at most k results

Reference corpus (tests encode it):
    ["term a b c", "term term a b", "term term term a"]
    all docs length 4 → length normalization is neutral here, so scores
    isolate the TF-saturation curve: each extra "term" buys less.

Run:  pytest modules/04-rag-systems/challenges/test_030_score_with_bm25.py -v
"""

import math
import re


class BM25:
    def __init__(self, corpus: list[str], k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.corpus = [self.tokenize(doc) for doc in corpus]
        raise NotImplementedError

    @staticmethod
    def tokenize(text: str) -> list[str]:
        raise NotImplementedError

    def idf(self, term: str) -> float:
        raise NotImplementedError

    def score(self, query: str, doc_index: int) -> float:
        raise NotImplementedError

    def search(self, query: str, k: int = 10) -> list[tuple[int, float]]:
        raise NotImplementedError
