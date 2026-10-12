# Augmenting and citations

**Reading time:** ~6 min · Module 4

You have 5–10 chunks. Everything from here is Module 2 craft applied to a
new input: assembling a prompt where the evidence is *findable, readable,
and attributable*. Small mechanical choices here move end-to-end quality
more than most retrieval tuning.

## Assembly rules that matter

1. **Order: best evidence first and last.** The "lost in the middle"
   result: models attend most to the start and end of long contexts. Put
   the top-reranked chunk(s) first; if you have 8+ chunks, consider
   mirror-ordering (best, ..., 2nd, best-again is wrong; use best-first,
   tail-last placement for the strongest two).
2. **Delimit each chunk with its source marker.** Numbered, labeled blocks:
   `[1] (source: runbook.md, section "Rotation")`. The marker doubles as
   the citation key and the model's reference anchor.
3. **Dedup and trim.** Overlapped chunks (lesson 050) mean repeated
   sentences — dedup before assembly. Trim each chunk to the relevant
   window when you can localize it; every wasted token is context budget
   and attention noise.
4. **Budget arithmetic, again:** system + chunks + question + room to
   answer ≤ context limit, with the answer reserve generous (Module 2
   lesson 060's overflow procedure applies verbatim — drop *lowest-ranked*
   chunks first; the reranker already ordered them for sacrifice).

## The instruction that earns its tokens

Tell the model the contract explicitly:

```
Answer ONLY from the provided sources. Cite each claim as [n].
If the sources don't contain the answer, say so — do not guess.
```

Two behaviors this buys: **grounding** (claims composed from evidence) and
**the graceful out** ("the docs don't cover this") — which is the single
most important RAG behavior, because the alternative is confident
hallucination over partial context (lesson 010's failure #4).

## Citations: generated ≠ verified

Asking for `[n]` markers is presentation. **Verification is post-hoc**:
check that each cited chunk actually supports the claim. Options in
increasing rigor: (1) heuristic — citation exists and points to a real
chunk; (2) lexical — the claim's key terms appear in the cited chunk;
(3) entailment/judge — an NLI model or LLM judge (lesson 120) scores
chunk → claim support. Regulated deployments need at least (2); audited
ones need (3). Log (query, chunks, answer, citations) for every request —
the verification pass is also your drift detector.

## Answer composition failures to watch

- **Stitching errors:** true facts from different chunks fused into a
  false sentence ("rotated quarterly" + "expires in 90 days" → nonsense).
  More chunks = more stitching surface.
- **Majority-vote hallucination:** three chunks say X, one says not-X, the
  model picks by fluency, not recency or authority. Metadata (timestamps,
  doc status) in the prompt helps; so does "prefer the most recent source."
- **Citation offset:** the model cites [2] where [3] supports the claim —
  off-by-one reality of generated citations, and why verification is
  post-hoc.

## Check yourself

1. Why does "if not in sources, say so" *need* an explicit instruction?
   What does the model default to otherwise, and why is that its rational
   behavior given training?
2. Design the cheapest citation verification you'd ship for an internal
   tool vs one for a regulated financial product.
3. Your answers regularly mix two policy versions. Which assembly-level
   and metadata-level fixes apply?

Next: [110 — Evaluating retrieval](110-evaluating-retrieval.md)
