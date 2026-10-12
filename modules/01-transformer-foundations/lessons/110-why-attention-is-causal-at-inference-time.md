# Why attention is causal at inference time

**Reading time:** ~6 min · Module 1

There's a line of code in every decoder-only LLM that looks like an
implementation detail and is actually a correctness guarantee: the **causal
mask**. Get it wrong and your model trains beautifully and generates garbage —
or trains on the test set without you noticing. This lesson makes it exact.

## The problem attention would have without a mask

Attention, as taught in lesson 100, lets every token look at every other token —
including tokens *after* it. During generation that's incoherent: when the model
is predicting token 50, tokens 51+ don't exist yet. A model trained with full
visibility would learn to base its prediction of the next token on... the next
token. That's not prediction; that's copying.

## The fix: forbid looking right

Before softmax, add `-inf` to every score position `j > i` (query i looking at
key j in the future):

```
scores (before mask)          after causal mask            after softmax
q1: [s11 s12 s13 s14]         [-inf  s12→? ...]  wait — row 1: only key 1 allowed
```

Concretely, for a 4-token sequence, the allowed attention pattern is
**lower-triangular**:

```
        keys →
q1  [  ■    ✗    ✗    ✗  ]
q2  [  ■    ■    ✗    ✗  ]      ■ = may attend
q3  [  ■    ■    ■    ✗  ]      ✗ = masked (-inf → 0 after softmax)
q4  [  ■    ■    ■    ■  ]
```

After softmax, masked entries become exactly 0 — the future contributes nothing.
You'll implement exactly this in the challenge; the classic bug is masking the
wrong triangle or forgetting that softmax turns -inf into 0 (and NaN if a whole
row is masked — can't happen with causality, since the diagonal is always allowed).

## The same mask serves two masters

**At training time:** the mask lets one forward pass compute *all n next-token
predictions in parallel* without leakage. Position 7's prediction path can only
see positions ≤ 7. This parallelism is why training is efficient at all — the
alternative (feeding prefixes one at a time) would be n passes per sequence.

**At inference time:** the mask matches reality — the future genuinely doesn't
exist. The training-time mask isn't a hack that inference has to imitate; it's
what makes the training distribution *equal* to the inference distribution. A
model trained causally plays by exactly the rules it will face when generating.

## The connection to KV caching (preview of Module 3)

Because position `i` only depends on positions `≤ i`, when you generate token
n+1 you do **not** need to recompute attention over all of the history's keys
and values — you can cache the K and V vectors of tokens 1..n and only compute
the new token's Q against them. That cache is the KV cache, it's the reason
generation cost per token is roughly linear rather than quadratic, and it's why
"KV cache size" is a central number in Module 3's VRAM math. Causality is what
makes the cache *valid*: frozen history stays frozen.

## The failure mode that proves the rule

Classic from-scratch bug: train with the mask, then at inference accidentally
feed the model a prompt that *includes* the target text (e.g., when scoring
candidate completions) without masking it. Losses look amazing; generation is
fine; but your eval numbers are fiction — the model peeked. Whenever you see a
language model with implausibly good next-token accuracy, the causal mask
boundary is one of the first places to audit: **who was allowed to see what,
exactly?**

## Check yourself

1. Why would a transformer trained *without* a causal mask still produce
   fluent text at inference time — and what would be quietly broken about it?
2. In the 4×4 diagram, why is the diagonal always allowed?
3. Generation with a KV cache reuses K,V from earlier positions. Why does the
   causal mask guarantee those vectors never need updating?

Next: [120 — Multi-head attention, the one-sentence version](120-multi-head-attention-the-one-sentence-version.md)
