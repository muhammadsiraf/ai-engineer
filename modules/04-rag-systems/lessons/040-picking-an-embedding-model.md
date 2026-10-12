# Picking an embedding model

**Reading time:** ~6 min · Module 4

The embedding model is the highest-leverage, lowest-glamour choice in the
pipeline — it's chosen once, baked into an index, and expensive to change.
The decision procedure matters more than any specific recommendation,
because "best" is a property of *your corpus and queries*, not a leaderboard.

## What actually varies between models

- **Quality on your domain.** MTEB-style leaderboards measure generic
  benchmarks; a model fine-tuned for code or medical text can dominate on
  your corpus while scoring lower overall. Leaderboards shortlist; only
  your golden set (lesson 110) decides.
- **Context length.** 512 tokens truncates your 800-token chunks silently.
  Match to lesson 050's chunk size — truncation mid-chunk quietly deletes
  half the semantics.
- **Dimensions.** 384 vs 768 vs 1536 vs 3072: storage and distance-compute
  scale linearly; quality gains are sublinear. Matryoshka (MRL) models let
  you *truncate* the vector and keep most quality — a free dimension knob.
- **Query/document asymmetry.** Instruction-tuned embedders want prefixes
  (`query:`, `passage:`). Skipping the prefix is the classic silent
  quality bug: it can cost more recall than any model swap would gain.
- **Multilinguality** if your corpus isn't English-only.

## The two consistency rules

1. **Same model on both sides, always.** Query embedding and document
   embedding must come from the same model, same version, same
   preprocessing. Cross-model similarity is noise.
2. **Pin the version; plan re-embedding.** An embedding model upgrade is an
   index-wide migration: re-embed everything (or run dual indexes and
   migrate traffic — Module 6's rollout pattern). Budget for it; "just
   swap the model" is how you get the silent-quality-bug class of outage.

## The decision procedure

1. Assemble ~200 real queries with known relevant documents (yes, the
   golden set comes FIRST — lesson 110; this is the Module 7 discipline
   again).
2. Shortlist 2–4 candidate models from leaderboards + domain fit.
3. Embed your corpus with each; measure recall@k on the golden set.
4. Among those within noise of the best, pick the smallest dimension and
   cheapest serving cost. Record the winner's config *with the corpus
   snapshot* — an unrepeatable eval is worthless.

Cost reality check: embedding a 100k-document corpus once is dollars and
minutes; embedding per *query* is the serving-path cost, and it's tiny.
The expensive directions are re-embedding on model change and dimension
bloat at scale — both planning decisions, not runtime ones.

## Check yourself

1. You swap embedding models and only re-embed *new* documents. What
   exactly goes wrong, and when does it surface?
2. Chunks are 900 tokens; the model's limit is 512. Why is recall loss
   "silent," and what would you check first?
3. Two models tie on recall@10. Name two tie-breakers and which you'd
   weigh higher for a 50M-chunk deployment.

Next: [050 — Chunking strategies](050-chunking-strategies.md)
