# Multi-head attention, the one-sentence version

**Reading time:** ~5 min · Module 1

One-sentence version first, then the unpacking: **multi-head attention runs
several small attentions in parallel — each with its own Q, K, V projections —
so different heads can specialize in different relationship types, and their
outputs are concatenated and mixed back together.**

## Why one attention isn't enough

A single attention pattern per layer must average every kind of relationship a
token needs: syntax (adjective → noun), coreference (pronoun → antecedent),
long-range topic tracking, code symbol → definition... One softmax row is one
probability distribution; it can't be 80% on the antecedent *and* 80% on the
grammatical head at once. The fix is not a bigger distribution — it's **several
distributions**, each free to look somewhere different.

## Mechanics: split, attend, concat, project

For hidden size `d` and `h` heads, each head works in dimension `dk = d/h`
(e.g., d=768, h=12, dk=64 — GPT-2's numbers):

```python
# split the d-dim space into h subspaces
Qh = Q.view(n, h, dk).transpose(0, 1)   # (h, n, dk)
Kh = K.view(n, h, dk).transpose(0, 1)
Vh = V.view(n, h, dk).transpose(0, 1)

# independent attention per head  (h, n, n) scores, then (h, n, dk) out
out = attention(Qh, Kh, Vh, mask)

# stitch subspaces back together, then a final linear mix
out = out.transpose(0, 1).reshape(n, d)
out = out @ Wo        # (d, d) — lets heads interact
```

Note the total width is unchanged: 12 heads × 64 dims = 768. Multi-head is not
"more compute" so much as **the same compute, split into parallel channels with
separate routing tables.** The final `Wo` projection is what lets head outputs
interact — without it, heads would remain isolated subspaces forever.

## What heads actually learn

In small models, head roles are famously legible; interpretability work has
found heads that do induction (find earlier occurrences of the current token,
copy what followed — a big part of in-context learning), duplicate-token
detection, syntax attachment, and positional copying. In big models, roles blur
and compose into circuits spanning layers. For you the operational point is:
head diversity is real and load-bearing — ablate the wrong head and a specific
capability (often in-context copying) collapses while everything else survives.

## The cost arithmetic you'll reuse

Attention compute per layer ≈ `h · n² · dk` = `n² · d` (the h·dk product is d).
So multi-head changes *quality per flop*, not the flop count. But the KV cache
*does* scale with heads: you store K and V for every head, every layer —
`2 · layers · heads · dk · n` values. Module 3's VRAM sizing and techniques
like grouped-query attention (share K/V across heads to shrink the cache) fall
straight out of this expression. Write it on a sticky note:
**cache = 2 × L × H × dk × n × bytes.**

## Check yourself

1. Why is one softmax distribution insufficient, mechanically, for attending to
   two different previous tokens for two different reasons?
2. Where in the code could two heads see *identical* inputs yet produce
   different outputs? (Which parameters differ?)
3. Doubling heads while halving dk keeps parameters equal. What changes in
   (a) attention compute, (b) KV cache size?

Next: [130 — Generation is autoregressive](130-generation-is-autoregressive.md)
