# Perplexity and reference metrics

**Reading time:** ~7 min · Module 7

Before judging quality you should know the classical toolkit — both
because it's the right tool for specific jobs, and because knowing
*why it fails* on open-ended generation is the cleanest motivation for
everything else in this module.

## Perplexity: the model's own surprise

Perplexity answers "how surprised was the model to see this text?"
From Module 1 lesson 030's cross-entropy:

```
per token:      loss_i = −log p(token_i | prefix)
mean loss (nats): L = (1/n) Σ loss_i
perplexity:     PPL = e^L        (= 2^L with log2 loss)
```

PPL is "the effective branching factor": PPL 40 ≈ the model was as
uncertain as if choosing uniformly among 40 plausible continuations at
each step. Lower = the text is more predictable *to this model*.

What it's genuinely for: **compare checkpoints on the same corpus**
(did my fine-tune reduce loss on held-out domain text? — Module 5
lesson 090's honest panel), detect distribution shift (lesson 110:
PPL of prod traffic under the reference model is a drift meter), and
cheap triage of candidate data.

What it is NOT: answer quality. A factually wrong, fluently templated
answer has low perplexity; a brilliant, surprising insight has high
perplexity. PPL measures fit to *the model's* distribution — it cannot
grade truth. (The challenge computes PPL from log-probs you'd get from
an API's `logprobs` field.)

## Reference-based text metrics: diff against a gold answer

When you *have* a reference: exact match / containment (for extraction),
token-overlap scores:

- **BLEU/ROUGE:** n-gram overlap with the reference — a precision/recall
  flavored scoreboard for translation and summarization. Cheap, ancient,
  misleading: misses paraphrase entirely ("caused by" ≠ "stemmed from")
  and rewards fluently wrong answers that reuse the reference's words.
- **BERTScore / embedding similarity:** semantic overlap via embeddings
  (Module 1 lesson 020) — paraphrase-tolerant, still blind to
  correctness of specifics ("returns accepted within 60 days" scores
  ≈ "...within 30 days").

The honest verdict: reference metrics are *triage* — useful for bulk
regression checks and cheap ranking of candidates, never the final
arbiter for anything customer-facing. When a paper reports "ROUGE
+2.1," ask what the human-judged delta was.

## The exactness hierarchy for extractive tasks

For outputs with checkable structure, prefer in order: exact match →
normalized match (case/whitespace) → field-level match (the JSON has
the right values) → type+schema validity. Structured outputs (Module 2
lesson 030) exist precisely to move evaluation down this ladder into
cheap exactness — one more argument for making the model emit schemas.

## Check yourself

1. Your fine-tuned model's PPL on held-out domain text dropped 30%.
   Name the follow-up eval that checks this wasn't purchased with
   general capability (Module 5 tie-in).
2. Why does ROUGE reward a summarizer that copies reference sentences
   even when it misses the point? What failure class is invisible?
3. Rank for a refunds-policy QA bot: PPL, ROUGE, exact-match-on-policy-id,
   LLM judge. Justify the order in one line each.

Next: [040 — Four eval shapes](040-four-eval-shapes.md)
