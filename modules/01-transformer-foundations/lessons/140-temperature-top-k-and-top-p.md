# Temperature, top-k, and top-p

**Reading time:** ~8 min · Module 1

The model hands you a probability distribution over 50k–200k tokens. Sampling
parameters decide *which* token you actually get. These three knobs are the
difference between a JSON API and a slot machine — and they're the only part of
the pipeline you control from the request body. Let's nail each one
mechanically.

## Start: the raw distribution

The model outputs logits (unnormalized scores). Softmax turns them into
probabilities:

```python
probs = softmax(logits)          # sums to 1 over the whole vocabulary
next_token = np.random.choice(len(probs), p=probs)
```

Raw sampling like this occasionally picks a 0.0001-probability token — fluent
prose, then suddenly "asparagus." The three knobs below all attack that tail.

## Temperature: how peaked the distribution is

Divide logits by T *before* softmax:

```python
probs = softmax(logits / T)
```

- **T → 0:** differences between logits get amplified; the max token's
  probability → 1. Greedy, deterministic-ish. (Implementation detail: T=0 is
  usually implemented as argmax, not literal division — same effect.)
- **T = 1:** the model's native distribution, unmodified.
- **T > 1:** flattens the distribution; unlikely tokens get real probability
  mass. Creative at best, incoherent at worst.

Intuition: temperature sets how much the model is allowed to deviate from its
top preference. Practical defaults: **0–0.3** for extraction, code, and anything
structured; **0.7–1.0** for prose and brainstorming.

Important precision: temperature reshapes probabilities; it doesn't know
*which* tokens are bad. A confident wrong answer at T=0 is still wrong —
temperature controls variance, not correctness. (People keep expecting T=0 to
fix hallucination. It doesn't; it just makes the same hallucination
reproducible.)

## Top-k: keep only the k best

Zero out everything outside the k highest-probability tokens, renormalize:

```python
top_k = 40
indices = np.argsort(logits)[-top_k:]
mask = np.full_like(logits, -np.inf)
mask[indices] = logits[indices]
probs = softmax(mask)
```

Guarantee: you'll never draw from outside the top 40. Good: kills the
asparagus tail. Bad: **k is context-blind.** When 5 tokens are plausible
(multiple-choice answer), k=40 does nothing. When 200 are plausible (open
prose), k=40 amputates real options. Fixed cutoffs don't adapt.

## Top-p (nucleus): keep the smallest set covering p mass

Sort descending; keep the smallest prefix whose probabilities sum to ≥ p;
renormalize; sample:

```python
sorted_probs = np.sort(probs)[::-1]
cutoff = np.searchsorted(np.cumsum(sorted_probs), p) + 1
# keep top `cutoff` tokens, zero the rest, renormalize, sample
```

- Tight distribution (model is confident): p=0.9 might keep just 3 tokens.
- Flat distribution (genuinely open choice): same p=0.9 keeps hundreds.

**Top-p adapts to confidence; that's why it largely displaced top-k** for open
text. Typical: p=0.9–0.95. You'll implement both in the challenge — the
cumsum/searchsorted version is the production-quality one, and its edge cases
(numerical drift so cumsum lands at 0.9998; p=1.0) are exactly the kind of
thing tests catch.

## Combined pipeline, in order

Real stacks apply these sequentially:

```
logits → (repeat/frequency penalties) → temperature → top-k → top-p → softmax → sample
```

Penalties (subtract a value from logits of already-used tokens) are the fourth,
optional knob — powerful against repetition loops (lesson 130), dangerous for
code, where repeating identifiers is *correct*.

## Choosing settings, as an engineer

| Task | Setting | Why |
|---|---|---|
| Extraction, classification, SQL/JSON | T=0 (or 0.1) | variance is the enemy |
| Doc summarization | T=0.3–0.5 | slight variation, no invention |
| Marketing copy, fiction | T=0.8–1.0 + top-p 0.95 | diversity is the point |
| Agent tool-call arguments | T=0 | args must be exact |

And the meta-rule that saves the most pain: **treat sampling params as
configuration under version control and A/B them like code** (Module 7). Teams
lose days to a silent default change ("the provider updated the client lib and
T went 0→1") that disciplined config would have caught in one diff.

## Check yourself

1. Your extraction endpoint occasionally emits a wildly off-topic token at
   T=0.2. Which knob addresses the tail, and why is lowering T further not the
   fix?
2. Why does top-p dominate top-k for open-ended generation? Express it in
   terms of what each method keeps when the distribution is flat vs peaked.
3. A teammate proposes sampling at T=1.4 "for creativity" on a support bot.
   Give the two failure modes you'd expect and what you'd propose instead.

Next: [150 — Why models hallucinate](150-why-models-hallucinate.md)
