# Context window economics

**Reading time:** ~6 min · Module 2

Module 1 lesson 170 dissected what's *in* the context. This lesson is the
money view: context is the resource you spend, and its growth curve — not
model quality — is what usually breaks LLM unit economics. Here's the
arithmetic and the levers.

## The curve that gets teams

Input tokens are re-billed on **every call**. A conversation that accumulates
history therefore has superlinear cost across a session:

```
turn:        1     2     3     4    ...  10
prompt:    1.0k  2.2k  3.4k  4.6k ...  13k     (0.2k/new turn + tools 0.8k)
session input total (sum):          ~70k tokens for a 10-turn chat
```

Ten turns × 300 tokens of *new* content = 3k tokens of novelty, but you paid
for ~70k. The ratio gets worse with tools and long system prompts (fixed
costs × every turn). This is why "just keep the whole conversation" quietly
doubles hosting costs at scale — and why every lever below exists.

## Lever 1: prompt caching (the big one)

Providers discount **repeated prefixes** heavily (typically 50–90% off the
cached portion) — the mechanics are lesson 120; the economics matter here:

- Structure requests so the *stable* part (system + tools) is a strict
  prefix, and volatile content comes last. Any interleaving (e.g., today's
  date injected early) breaks the cache for the whole suffix.
- Cache hits have latency benefits too: cached prefixes skip most prefill.
- Minimum cacheable lengths and TTLs vary by provider; within a busy hour,
  the same system+tools prefix hits constantly.

If you take one operational rule from this lesson: **design prompts as
`[stable prefix][volatile suffix]`, religiously.**

## Lever 2: history management

For long sessions, don't resend everything:

- **Sliding window:** keep last k turns. Cheap, lossy — early constraints
  vanish (Module 1 lesson 170's failure mode). Pair with re-injecting a
  pinned "key facts" block.
- **Summarize-then-truncate:** periodically compress old turns into a
  summary paragraph (one cheap LLM call), keep recent turns verbatim.
  Bounded loss, bounded cost. Watch summary quality — it's a new failure
  surface (Module 7: evaluate summarization against task success).
- **Drop tool outputs:** old tool results (huge JSON blobs) can shrink to
  their one-line conclusion after the turn that used them.

## Lever 3: right-size retrieval

RAG's cost dial is k (number of retrieved chunks). Going k=3 → k=10 triples
the retrieval block *per request*, forever. Module 4's reranking exists so
you can keep k small and dense. The economics: reranker cost is per-request
and small; context bloat is per-request and large. Denser beats bigger.

## Lever 4: route by size and difficulty

Not every request deserves the premium model:

```
if est_tokens < 500 and task_tier == "simple":  → small cheap model
elif needs_long_context:                        → big-context model
else:                                           → default premium model
```

Classification of "simple" is itself an LLM call (or a rule). A two-tier
route typically cuts blended cost 30–60% in real workloads, at the price of
a router to maintain and evaluate (Module 7: per-route evals). Cascade
variations (try cheap, escalate on low confidence using logprobs — Module 1
lesson 020) add quality insurance.

## The dashboard that keeps you honest

Four lines, per feature (not just per model):

1. **Input tokens/request** (p50, p95) — bloat detector
2. **Output tokens/request** — runaway-generation detector
3. **Cache hit rate** on input — prefix-hygiene detector
4. **$ / successful task** — the only number the business cares about

The p95s matter more than the means: one user pasting a 200k-token log, one
tool returning unbounded JSON — tail events dominate bills (lesson 030's
tokenization density warnings live here too).

## Check yourself

1. Compute session input cost at $3/M: 12-turn chat, 900-token fixed prefix,
   250 tokens new content per turn. Now with a 90%-discounted cached
   prefix. What's the saving?
2. Your RAG answer quality is identical at k=5 and k=12 on your golden set.
   What do you ship, and why is that the right call even if k=12 "feels
   safer"?
3. Design the two-tier router for a support product: what signals, what
   models, and how do you evaluate that routing didn't hurt quality?

Next: [110 — Latency: time-to-first-token vs total](110-latency-time-to-first-token-vs-total.md)
