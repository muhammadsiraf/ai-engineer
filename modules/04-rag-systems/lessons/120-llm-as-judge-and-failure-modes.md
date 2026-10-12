# LLM-as-judge and failure modes

**Reading time:** ~7 min · Module 4

Retrieval metrics (lesson 110) measure the pipeline's front half. The back
half — did the *answer* correctly use the evidence — has no exact metric,
and labeling thousands of answers by hand doesn't scale. The standard tool
is the LLM-as-judge, and its honest companion is a catalog of biases and a
bisection procedure for production failures.

## The three judge rubrics for RAG

Score each answer against its retrieved context and query:

1. **Groundedness / faithfulness:** every claim in the answer is supported
   by the retrieved chunks. (Catches hallucination and stitching errors —
   lesson 100's failure modes.)
2. **Relevance:** the answer actually addresses the question asked.
3. **Completeness:** the evidence in context that *should* have been used
   was used.

Rubric discipline from Module 7, stated here because you'll build one
this module: binary or 1–3 scales beat 1–10 (judges can't keep 10 levels
calibrated); define each level with examples; require the judge to quote
the supporting chunk text before ruling — forcing evidence-first
reasoning measurably improves judge consistency.

## Judge biases you must design around

- **Position bias:** judges prefer the first option presented. Mitigate by
  swapping order and averaging, or never asking comparisons when a
  pointwise rubric works.
- **Verbosity bias:** longer answers score higher, quality-equal. Counter:
  rubric explicitly scores hallucinated/unsupported content negatively.
- **Self-preference:** a model rates its own outputs higher. Use a
  different family as judge, and validate the judge against a small
  human-labeled set — **a judge is a model, and it needs its own eval**
  (the pass@agreement rate vs human labels is the judge's golden set).

## The failure taxonomy

| # | Failure | Stage | Signature |
|---|---|---|---|
| 1 | Evidence never retrieved | index/retrieve | recall@k low |
| 2 | Retrieved but not in top-k after rerank | rerank | recall@50 ok, recall@5 low |
| 3 | In context, ignored or misquoted | generate/assemble | grounded answer present |
| 4 | Partial evidence, model overfills | generate | half-right answer |
| 5 | Wrong chunk retrieved (high similarity, wrong relevance) | retrieve | precision@k low |
| 6 | Stale/wrong-permission content | index ops | correct shape, outdated fact |

## The bisection procedure (the part to memorize)

For any failing query:

1. **Look at the context actually sent** (you logged it — lesson 020).
2. Ask: *is the information needed for a correct answer present in that
   context?*
   - **No** → retrieval-side. Walk up: was it in the reranker's input
     (stage 2)? In the retriever's candidate pool at all (stage 1)? In the
     index (stage 6/chunking)? The first stage where it goes missing is
     the stage that owns the bug.
   - **Yes** → generation-side. Assembly order? Grounding instruction?
     Model capability? Swap in a stronger model *just for this query* to
     separate prompt bugs from model limits.
3. Convert the query into a golden-set case (lesson 110) so the fix is
   verified, not vibes.

Ninety percent of "RAG is flaky" reduces to: stage 1 didn't fetch it, or
stage 3 ignored it. The bisection tells you which in five minutes.

## Check yourself

1. Your judge scores groundedness 0.95 — before trusting it, what number
   do you need and how do you get it?
2. Query fails. Context contains the right chunk at position 4 of 8.
   Which taxonomy row(s) are candidates, and what do you test next?
3. Why is "ask a stronger LLM to judge" not automatically valid —
   name the two checks that make it valid.

Next: [130 — Production RAG architecture](130-production-rag-architecture.md)
