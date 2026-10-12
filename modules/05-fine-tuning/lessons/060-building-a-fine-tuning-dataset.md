# Building a fine-tuning dataset

**Reading time:** ~7 min · Module 5

Every experienced practitioner says it, and every team learns it the
expensive way: **the dataset is the model.** A LoRA run is hours; the data
behind it is weeks — and data quality dominates every hyperparameter in
this module combined. Model capacity is not your bottleneck; distribution
quality is.

## Shape and scale

Instruction data is `(instruction, input?, response)` triples — thousands
of examples showing the *behavior* you want. Scale guidance by task:

- Style/format adaptation: 500–2,000 examples
- Task adaptation (extraction, classification, transformation): 1k–10k
- Broad instruction-following: 50k+ (you are not doing this; the frontier
  labs did it for you)

More data beats more rank (lesson 040) at every margin worth caring
about.

## The five quality rules

1. **Distribution match:** the eval set (Module 7's golden set) and the
   training set must come from the same task distribution you'll serve.
   The #1 silent failure: training on cleaned examples, serving messy
   real inputs.
2. **Diversity within the distribution:** 5,000 near-duplicates of one
   pattern teaches one pattern — and overfits it (lesson 100). Cover the
   input space: lengths, edge cases, negatives (inputs where the right
   answer is "none found" or "cannot determine").
3. **Correct labels, judged at the response level:** "mostly right"
   responses teach the model *mostly*-right behavior, including the
   errors. Human review on a sample is not optional; inter-annotator
   agreement tells you if your task is even well-defined.
4. **Response style consistency:** one voice, one format, everywhere. The
   model will learn the *average* of your styles; mixed formats in =
   mixed formats out.
5. **No leakage:** dev/test examples (or near-duplicates of them) in
   training make your eval a fiction. Dedup against eval with the same
   n-gram machinery you'd use for any leakage check.

## Where examples come from

- **Logs of real usage** (the best source): inputs are real by
  construction; responses need expert curation or rewriting.
- **Strong-model distillation:** generate responses with a frontier
  model, humans *review and correct*, train the small model (lesson 010's
  economics story). The correction step is what keeps quality; raw
  model output inherits the teacher's failures.
- **Synthetic augmentation:** paraphrases, template variations, programmatic
  negatives — with a dedup pass and a held-out real-only eval slice to
  prove synthetics didn't skew the distribution.

## The 80/20 of effort

Budget rule of thumb: 80% of fine-tuning project time is data work. Spend
it on: response quality review, distribution coverage, and the negative
examples everyone forgets. Then r and α are half-day sweeps (lesson 040's
recipe), not research.

## Check yourself

1. Your fine-tuned extraction model scores 0.95 on eval, 0.6 in
   production. Name the two most likely dataset-level causes and the
   checks that would have caught each.
2. Why do "negative" examples (empty result, ambiguous input) matter
   disproportionately for RAG-adjacent fine-tunes?
3. You have 300 hand-written examples. Fine-tune now, or grow data first?
   What's the minimum eval that decides?

Next: [070 — Instruction format and chat templates](070-instruction-format-and-chat-templates.md)
