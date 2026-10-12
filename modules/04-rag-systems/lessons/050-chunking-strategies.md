# Chunking strategies

**Reading time:** ~7 min · Module 4

Chunking answers one question — *what is the unit of retrieval?* — and it's
wrong more often than any other pipeline stage. Embed and retrieve the
wrong unit and no downstream component can save you: the retriever fetches
the fragments it was given.

## Why chunk at all

- **Embedding dilution:** a 20-page document compresses to one vector that
  means nothing in particular (averaging many topics blurs all of them).
  Short, coherent units produce sharp vectors.
- **Context economics:** you can fit 8 relevant 300-token chunks, not 8
  relevant 20-page documents (Module 2 lesson 050's budget arithmetic).
- **Ranking precision:** smaller units → cleaner relevance signal per hit.

The tension: chunks must be **small enough to be sharp** and **big enough
to be self-contained**. A chunk that says "See step 3 above" retrieves
badly and cites worse.

## The strategy ladder

1. **Fixed-size with overlap** (the baseline, and this module's challenge):
   windows of ~N tokens stepping by N−overlap. Overlap (10–20%) exists so
   a sentence straddling a boundary lives fully in at least one chunk.
   Crude, robust, everywhere.
2. **Structure-aware:** split on paragraphs/headings/markdown sections
   first, then pack to size. Respects the document's own semantic
   boundaries — usually the best effort/quality ratio.
3. **Semantic chunking:** embed sentences; cut where the embedding drifts
   (topic change). Costs an embedding pass over everything; rarely beats
   good structure-aware splitting enough to matter. Try it second.
4. **Small-to-big / parent-document:** retrieve on small sharp chunks but
   *return* the enclosing parent (section or page) to the generator. Gets
   precision of small + context of big. The trick worth stealing when
   answers need surrounding context.

Typical territory: 200–800 tokens per chunk, 10–20% overlap. But the real
answer is "your eval decided" — chunk size is a sweep, not a belief.

## Metadata is half the feature

Every chunk carries: source document id, title, section path, position,
timestamps, permissions. Metadata powers citations (lesson 100), recency
boosts, metadata filters (lesson 060), and access control (lesson 130).
Chunk text alone is an orphan; chunk text + metadata is an addressable
knowledge unit.

## Failure shapes to recognize in the wild

- **Answer split across chunks** ("the password is" / "hunter2") → overlap
  too small, or chunk boundaries in tables/code. Symptom: retrieval found
  *a* chunk but not the *completing* one.
- **Tables/lists shredded** → fixed-size cutting mid-structure; structure-
  aware splitting with table-atomicity fixes it.
- **Giant FAQ entries** → one chunk per Q/A pair, not fixed-size.
- **The retrieve-but-missed pattern:** recall@k shows the right *document*
  in the index but the wrong *chunks* retrieved — chunking, not embedding,
  is usually the culprit. (Lesson 120's bisection relies on this
  distinction.)

## Check yourself

1. Retrieval returns chunks containing "step 3" but the answer needs steps
   1–5. Name two fixes and their costs.
2. Why does 10–20% overlap help at *both* index time (embedding) and
   retrieval time (ranking)?
3. You switch from 300-token to 800-token chunks. Predict the effect on
   recall@5, on generator context budget, and on answer groundedness —
   and how you'd verify each.

Next: [060 — Vector stores and ANN](060-vector-stores-and-ann.md)
