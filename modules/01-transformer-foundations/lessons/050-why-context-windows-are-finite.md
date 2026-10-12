# Why context windows are finite

**Reading time:** ~6 min · Module 1

"128k context" isn't a marketing choice someone could have made bigger with more
money. Finiteness is baked into the architecture and into physics. Understanding
*why* shapes every context-management decision you'll make.

## The mechanical reason: attention is pairwise

The transformer's attention mechanism (lesson 100) computes, for every token,
how much it should look at **every other token**. That's `n × n` relationships
for a sequence of `n` tokens:

- Compute scales roughly with n² (quadratic in prefill)
- The KV cache (Module 3) grows linearly with n *per layer, per head* — and it
  must live in GPU VRAM

At n = 8k these costs are trivial. At n = 1M they're the whole GPU. Context
length is where the quadratic curve hits your hardware budget.

## The learned reason: models are trained at a context length

Attention itself is length-agnostic — the same math works for 10 tokens or 10
million. But the *quality* of attention at long ranges is learned from training
data. A model trained with 8k sequences has never practiced using information
from 50k tokens back; extend its window naively and long-range recall degrades
into mush long before anything crashes. Techniques exist to extend windows
(context-length scaling, RoPE frequency adjustments, sliding-window attention),
but they're engineering, not free.

## The empirical reason: effective context < advertised context

Even within the window, models don't use context uniformly. The well-documented
pattern:

- **Primacy/recency:** information at the very beginning and very end of the
  prompt gets used much more reliably than the middle
- **Lost in the middle:** retrieval accuracy from the middle of a long context
  can drop dramatically
- **Distraction:** irrelevant-but-plausible text in context *actively hurts* —
  the model can't fully ignore what it can attend to

So "supports 128k" and "reliably uses 128k well" are different claims. Your
production context budget should be set by measured task performance, not by
the spec sheet.

## The engineering consequences

**1. Context is a budget you allocate.** Treat it like memory in an embedded
system:

```
system prompt        ~500–2,000 tok   (fixed cost, every call)
tool definitions     200–5,000 tok    (fixed, every call)
retrieved documents  ??? tok          (the flexible part)
conversation history ??? tok          (grows every turn)
response headroom    1,000–4,000 tok  (reserve for output)
```

**2. History must be managed, not accumulated.** Sliding window, summarization
of old turns, or dropping tool outputs — Module 2 builds this. The stateless
contract (lesson 020) means *you* own this problem; the model cannot forget
for you.

**3. RAG exists because of this lesson.** You cannot put the whole wiki in
context. Retrieval is the discipline of putting the *right* 5% of the corpus in
the window. Module 4 is this sentence expanded to 13 lessons.

**4. Long context ≠ free RAG replacement.** "Just dump everything in" fails on
cost (paying for 500k tokens per query), latency (prefill time), and the
accuracy effects above. Retrieval stays cheaper, faster, and more accurate —
which is why the biggest-context models on the market still get RAG'd in
production.

## Check yourself

1. Why does attention make cost grow quadratically with sequence length while
   the KV cache grows linearly? (Module 3 makes this precise — take a first
   swing at it now.)
2. Your task needs one fact from page 40 of a 100-page PDF. Give two reasons
   "put the whole PDF in context" is the wrong default.
3. Where would you place the single most important retrieved document in a long
   prompt, given the attention pattern above, and why?

Next: [060 — Embeddings: vectors as meaning](060-embeddings-vectors-as-meaning.md)
