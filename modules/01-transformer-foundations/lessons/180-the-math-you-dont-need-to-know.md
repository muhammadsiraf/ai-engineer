# The math you don't need to know (and the bits you do)

**Reading time:** ~6 min · Module 1

You can ship excellent LLM systems without deriving backpropagation. But five
small pieces of math show up so constantly — in loss curves, eval metrics,
logprob APIs, cost models — that not owning them will slow you down weekly.
This lesson is the honest list: what to skip, what to keep, and the exact
operations to internalize.

## Safe to skip (for this job)

- **Derivations of the transformer.** Knowing *why* attention works from
  first principles is research knowledge; you need *what it does and what it
  costs*, which lessons 100–120 covered in shapes and code.
- **Measure theory, fancy probability.** Nothing in applied LLM engineering
  requires it.
- **Matrix calculus by hand.** Autodiff does it; you do arithmetic with the
  results.
- **Novel architecture papers.** Your job is deploying and improving systems,
  not inventing backbones. Read model cards, not proofs.

Skip confidently. Revisit if you change careers.

## Keep #1: logarithms as the native language of probability

LLMs speak in log-probs everywhere: loss values, `logprobs` API fields,
perplexity, scoring in rerankers, beam search. Two facts are 90% of what you
need:

```python
# products of probabilities become sums of logs
P(a) · P(b) · P(c)  =  exp( logP(a) + logP(b) + logP(c) )

# log(p) is negative; closer to 0 = more confident
log(0.5) = -0.69      log(0.01) = -4.6      log(1e-6) = -13.8
```

Fluency check: the model returns logprobs `[-0.1, -2.3, -5.0]` for three
candidate completions. Multiply out which is most likely — or just see that
`-0.1` is nearly certain and `-5.0` is a 0.7% shot. Every eval metric in
Module 7 is this, aggregated.

## Keep #2: the softmax, one more time

```python
softmax(x)_i = exp(x_i) / Σ exp(x_j)
```

Converts arbitrary scores to a probability distribution. It's in the model
output, in your sampling code, in attention itself (lesson 100), and in every
"convert scores to probabilities" moment in RAG fusion (RRF's rivals) and agent
routing. One formula, everywhere, worth having under your fingers.

## Keep #3: expected value and averaging for evals

An LLM's output is a random variable; a single test run is one draw. The
workhorse of all evaluation: run k times, average, report variance.

```
mean = (1/k) Σ x_i        var = (1/k) Σ (x_i - mean)²
```

Module 7 builds confidence bounds on win rates from exactly this. If you can
average and eyeball a variance, you can do production eval.

## Keep #4: ratios for cost and throughput math

Everything commercial is ratio arithmetic — no calculus, just unit analysis:

```
cost per request  =  input_tokens × input_price  +  output_tokens × output_price
tokens/sec        =  1 / seconds_per_token          (decode)
GPU utilization   =  busy_ms / wall_ms
$ per 1M tokens   =  monthly_cost / (monthly_tokens / 1e6)
```

The Module 6 and Module 3 challenges are these formulas wearing different hats.
Engineers who can't flip between "per-token" and "per-million" pricing burn
budget on spreadsheet errors.

## Keep #5: the vector ops from this module

You've already met them; this is the consolidated kit:

- **dot product** — relevance scores (attention), similarity
- **cosine similarity** — embedding comparison (lesson 060, challenge 020)
- **L2 norm** — vector length, needed for cosine
- **softmax** — see above
- **cross-entropy** = `-log p(correct)` (lesson 070, challenge 030)

Five operations, each ≤ 5 lines of NumPy, and you can implement the conceptual
core of an LLM — which is exactly what the Module 1 challenge set does.

## The one graph worth knowing cold

A **loss curve** (loss vs training step), because Module 5 is reading these:

```
loss
 │＼
 │  ＼＿＿            ← train loss keeps falling
 │      ＼＿
 │      ___＼──        ← eval loss bottoms out, then RISES
 └────────────── steps
        ↑ this divergence = overfitting: stop here
```

The divergence point is where the model started memorizing instead of
generalizing. Fine-tuning run bookkeeping is 80% "did we stop at the bottom of
the eval curve."

## Check yourself

1. Convert logprobs `[-0.69, -2.30, -4.61]` to probabilities (in your head,
   using e⁻⁰·⁷ ≈ 0.5, e⁻²·³ ≈ 0.1).
2. A provider charges $3/M input, $15/M output. Your request averages 2k in /
   500 out, 10k requests/day. Daily cost? (Keep #4.)
3. You sampled an eval 30 times: 21 wins. Mean and a rough standard error?
   Is 70% meaningfully better than a 60% baseline? (Keep #3 — and note we'll
   do this properly in Module 7.)

**Module 1 complete.** Next: [Module 2 — Using LLMs via API](../../02-using-llms-via-api/lessons/010-api-call-shape.md)
