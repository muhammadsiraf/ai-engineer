# The transformer block in one diagram

**Reading time:** ~6 min · Module 1

Every LLM you'll ever deploy is a stack of identical blocks. Each block does one
thing: **let tokens exchange information, then let each token think privately
about what it collected.** This lesson is the map; the next three lessons zoom
into attention, causality, and multi-head variants.

## The block

```
        x  (n tokens × d dims)
        │
        ├────────────────────────────┐
        │                            │
        ▼                            │
   ┌─────────┐                       │  residual (skip) connection:
   │ATTENTION│  tokens look at       │  the input is added back at the end,
   │         │  each other           │  so the block only has to learn
   └────┬────┘  (mix across tokens)  │  a *correction*, not a full transform
        │                            │
        ▼                            │
   ┌─────────┐                       │
   │   ADD   │◄──────────────────────┘
   └────┬────┘
        │
        ├────────────────────────────┐
        ▼                            │
   ┌─────────┐                       │
   │   MLP   │  each token thinks    │
   │  (4d)   │  alone (mix across    │
   └────┬────┘  features)            │
        ▼                            │
   ┌─────────┐                       │
   │   ADD   │◄──────────────────────┘
   └────┬────┘
        │
        ▼
   x'  (same shape as x)
```

(LayerNorm sits before each sub-block in modern models — "pre-norm." Omitted
from the diagram so the data flow is visible.)

Read it as two sentences:

1. **Attention: communication.** Each token's vector is updated using a
   weighted mix of *other tokens'* vectors. This is the only place information
   moves between positions.
2. **MLP: computation.** Each position's vector is transformed independently —
   expand to 4d, nonlinearity, project back. The "thinking" happens here, per
   token, on what attention gathered.

The insight worth keeping: **transformers alternate between mixing across
tokens (attention) and mixing across features (MLP).** That alternation, stacked
32–100 times, is the whole architecture.

## Residuals: why the ADDs matter

The skip connections aren't decoration. Without them, deep stacks are nearly
untrainable — the signal (and, during training, the gradient) degrades through
every layer. With them, each block only learns an incremental correction:
`x' = x + correction`. Conceptually, information flows up the residual "highway"
and each layer contributes edits. This is also why residual-stream metaphors
("the model reads and writes to a shared bus") dominate interpretability
research — and why LayerNorm's job (keeping the bus voltage stable) matters.

## Shapes stay constant

Input to a block: `n × d`. Output: `n × d`. Same for every block in the stack.
Two practical payoffs:

- Stacking is trivial: just loop `for block in blocks`.
- The final output at each position is a same-shaped vector; only the last
  position's vector goes through the LM head to produce next-token logits.
  (During training, *all* positions produce logits at once — that's what makes
  training parallel; lesson 110.)

## Scale in numbers

A Llama-3-8B-class model: 32 blocks, hidden size 4096, MLP expansion 4x, 32
attention heads of dim 128 each. GPT-2 small (which you'll build): 12 blocks,
d=768, 12 heads of dim 64. The architecture barely changed from 2017 to now —
what scaled was the block count, the widths, and the data. This is worth
internalizing: **the reason LLMs took over the world is not architectural
cleverness; it's that this simple, regular, parallelizable design happened to
scale like nothing else.**

## Where bugs will live later

- Attention scaling factors and masking → correctness bugs in your from-scratch
  build (challenges 050–070)
- MLP activation choice (GELU/SwiGLU) → subtle loss differences in Module 5
- Norm placement → training instability in fine-tunes

## Check yourself

1. In the block diagram, where exactly can information move *between* token
   positions? Why does the MLP's "each position alone" property matter for
   parallelism?
2. A block's attention is deleted (identity). What does the model become
   capable of? What does it lose?
3. Why do residual connections make gradient flow *through 100 layers*
   survivable, in one intuitive sentence?

Next: [100 — Self-attention in five minutes](100-self-attention-in-five-minutes.md)
