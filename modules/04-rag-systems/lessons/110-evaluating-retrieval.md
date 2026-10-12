# Evaluating retrieval

**Reading time:** ~7 min · Module 4

You cannot tune chunking, embedding models, fusion weights, or rerankers
without retrieval metrics — "the answers look better" has no gradient.
This lesson builds the measurement layer: a golden set plus four metrics
you'll compute in the challenge.

## The golden set first (always)

The unit of evaluation is **(query, set of relevant chunk/document ids)**.

1. Collect 50–200 *real* queries (support logs, search logs, stakeholder
   interviews — never invented in a conference room).
2. For each, mark which chunks/docs would make the answer correct. A
   first pass takes an afternoon with an LLM-assisted labeling loop and a
   human spot-check; keep judgments per-*chunk* when you evaluate
   chunking, per-*doc* when you don't.
3. Freeze it, version it, extend it when queries fail in production —
   every production failure becomes a test case. This is Module 7's
   discipline arriving early.

Without this set, every design debate in this module is aesthetics. With
it, most debates are 20-minute measurements.

## The four metrics

Let `retrieved` be the ranked list you returned, `relevant` the golden
labels, `k` the cutoff:

- **Recall@k** = |retrieved∩relevant| / |relevant| — *did we get the
  evidence?* The generator can't use what wasn't fetched. The headline
  retrieval metric.
- **Precision@k** = |retrieved∩relevant| / k — *how much of our k was
  worth it?* The context-window hygiene metric (junk chunks cost money,
  attention, and stitching errors per lesson 100).
- **MRR** = 1/rank of the first relevant hit — *how high does the first
  good thing land?* The metric for one-right-answer query shapes.
- **nDCG@k** — like precision but position-weighted with graded
  relevance; the subtle one, reach for it when ranking quality *within*
  the window matters.

**k is a design parameter, not a constant:** it's the number of chunks
you'd actually feed the generator (lesson 100's budget). Report the whole
curve recall@{5,10,20,50}; a system with recall@5=0.6/recall@50=0.9 needs
a reranker (lesson 090), while recall@50=0.5 needs retrieval surgery.

## The bisecting insight

End-to-end quality answers nothing by itself. Measure the stages apart:

- **Retrieval bad (low recall@k):** the failure is indexing — chunking,
  embedding, fusion. No prompt fixes it.
- **Retrieval good, answer bad:** the failure is generation — assembly,
  grounding instructions, the model itself.

The diagnostic question "would the golden chunk(s) have been in the
context?" splits every production bug into one of these two worlds, and
lesson 120 turns it into a procedure.

Two honest caveats: (1) retrieval metrics don't capture *distractor harm*
— more retrieved chunks can technically raise recall while hurting answers
(lesson 100's stitching); (2) golden labels have their own noise — when
two configs sit within a couple points, re-label before celebrating.

## Check yourself

1. Your support bot feeds the generator 5 chunks. Which cutoff k do you
   report, and why is recall@50 still on the dashboard?
2. Precision@5 fell 10 points while recall@5 held steady after adding a
   second retrieval source. Walk the tradeoff — is this good or bad,
   and what decides it?
3. Build the failure taxonomy: for (a) query uses a synonym the docs
   never contain, (b) chunk split the answer, (c) reranker truncation —
   which metric moves, and which stage owns the fix?

Next: [120 — LLM-as-judge and failure modes](120-llm-as-judge-and-failure-modes.md)
