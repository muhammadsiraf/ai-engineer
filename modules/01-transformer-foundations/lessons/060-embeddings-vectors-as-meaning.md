# Embeddings: vectors as meaning

**Reading time:** ~7 min · Module 1

Embeddings are the bridge between "text as characters" and "text as something a
computer can compute over." They power semantic search, RAG (Module 4),
clustering, dedup, classification, and memory for agents (Module 8). This lesson
builds the geometric intuition you'll use for the rest of the course.

## The core idea

An embedding function maps a piece of text to a fixed-length vector of floats:

```python
"the cat sat on the mat"  ->  [0.021, -0.113, 0.441, ..., 0.007]   # e.g. 768 dims
"a feline rested on a rug"->  [0.019, -0.108, 0.437, ..., 0.011]   # similar!
"quarterly revenue fell"  ->  [-0.442, 0.223, -0.108, ..., 0.390]  # far away
```

The claim embedding models are trained to satisfy: **texts with similar meaning
land close together in vector space.** Meaning becomes geometry. Once meaning is
geometry, "find similar documents" becomes "find nearby vectors" — a solved
problem with decades of library support (FAISS, Module 4).

## Closeness: cosine similarity

The standard distance is cosine similarity — the cosine of the angle between
vectors, ignoring length:

```python
import numpy as np
def cosine_sim(a, b):
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
```

Range is [-1, 1]: 1 = same direction, 0 = unrelated, negative = opposed. Why
cosine rather than straight Euclidean distance? Embedding vector *lengths* tend
to encode artifacts (text frequency, verbosity) rather than meaning; the angle
is the meaning-carrying part. Most providers normalize embeddings to unit
length, after which cosine and dot product are identical.

You'll implement cosine similarity in the challenge — five lines, but getting
the normalization edge cases right is the point.

## What "close" actually encodes

Training objective matters. Embedding models are trained on pairs — either
predicting co-occurring text (classic word2vec-style) or contrastively: pull
matched pairs together, push mismatched pairs apart. So distance means
"would plausibly appear in similar contexts," not "means the same thing."

Calibrate with the typical behavior of a modern text embedder:

| Pair | Typical cosine |
|---|---|
| Paraphrases of the same sentence | 0.85–0.95 |
| Question and its answer | 0.6–0.8 |
| Same topic, different points | 0.4–0.6 |
| Unrelated texts | 0.0–0.2 |

Note: **similar ≠ relevant.** "How do I reset my password" is *similar* to
"how do I change my password" (great) but also fairly close to "password
policy best practices" (not what the user needs). Similarity gets you
candidates; it doesn't guarantee answers. That gap is why Module 4 adds
reranking and why hybrid retrieval (lesson: BM25 + dense) exists.

## Embeddings you'll meet

- **Token embeddings:** inside an LLM, each token ID looks up a learned vector —
  the model's first layer. This is *input representation*, not for search.
- **Sentence/text embeddings:** what embedding APIs return — one vector for a
  whole passage, trained for retrieval. Models: BGE, E5, GTE, OpenAI
  `text-embedding-3`, Cohere embed. This is the RAG workhorse.
- **Universal vs. domain-tuned:** off-the-shelf models are strong generalists;
  domain-specific fine-tuning of embedders is a real (advanced) technique.

Two operational rules: (1) you cannot mix vector spaces — documents and queries
must use the *same model version*; (2) dimensionality (384–3072) trades storage
and speed against nuance, and it's fixed per model.

## A first application, to see it work

```python
# pip install sentence-transformers
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("BAAI/bge-small-en-v1.5")
docs = ["Reset your password from the login page.",
        "API keys are rotated every 90 days.",
        "Our refund policy allows 30 days."]
q = model.encode("how do I change my password")
for doc in docs:
    d = model.encode(doc)
    print(cosine_sim(q, d), doc[:40])
```

The password document wins by a wide margin despite sharing zero important
words with the query ("change" vs "reset"). That's the entire value proposition.

## Check yourself

1. Why do two short documents ("yes", "no") land closer to each other in some
   models than two long documents on the same topic? What does that imply about
   chunk sizes for RAG?
2. Search returns a semantically similar document that is *not* the right
   answer. Which two module-4 mechanisms address this?
3. You upgrade your embedding model. What must happen to your stored vectors,
   and why can't you mix old and new?

Next: [070 — What 'training' actually does](070-what-training-actually-does.md)
