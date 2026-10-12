# Why RAG exists

**Reading time:** ~7 min · Module 4

An LLM knows two things: what's in its weights, and what's in its context.
Weights are frozen at training time, expensive to change, and lossy — a
model that "read" your company's wiki during training will paraphrase it
unreliably and cite nothing. Retrieval-Augmented Generation flips the
knowledge problem around: **keep knowledge outside the model and fetch the
relevant slice into context at query time.**

## The four failures of parametric knowledge

1. **Staleness.** Training cutoff means "latest pricing doc" is fiction.
2. **Privacy.** Your internal data was never in any training set.
3. **Attribution.** Weights can't show their work. Regulated domains need
   answers traceable to a source document.
4. **Access control.** A weight either knows something or doesn't — per-user
   permissions are unenforceable on parameters.

RAG solves all four with one move: the knowledge lives in a searchable
store you control, updates are re-indexing not re-training, and every
answer carries its sources.

## Knowledge vs behavior: the RAG/fine-tuning line

The single most useful classification when a stakeholder says "we should
train a model on our docs":

| Problem | Fix |
|---|---|
| Model doesn't KNOW facts/docs/policies | **RAG** |
| Model knows the facts but wrong format/tone/behavior | Prompting, then **fine-tuning** (Module 5) |
| Need citations or per-user access control | **RAG** (fine-tuning can't do either) |
| Fixed, small, closed knowledge (20 FAQs) | Neither — paste it into the context |

Fine-tuning teaches *skills and style*; it is a lossy, unversioned,
attribution-free way to store *knowledge*. RAG is the opposite trade.
Module 5 revisits this line with the fine-tuning decision tree.

## The contract you're signing

RAG's quality ceiling is retrieval quality: **the model can only use what
you fetched.** If the right document isn't in the context window, no amount
of generation skill produces a grounded answer — the model will either
refuse (good) or hallucinate from partial context (likely). This is why
this module spends most of its time on retrieval (lessons 030–090) and its
evaluation (110–120), not on the generation step, which you already own
from Module 2.

## When RAG is the wrong tool

- **Structured lookups** ("current balance for account X") → a tool call /
  API query, not similarity search (Module 8's tool-calling).
- **The corpus is tiny and stable** → put it in the prompt; skip the
  machinery (and note you get prefix-caching economics from Module 3
  lesson 070 for free).
- **You need the model to *reason differently*** → fine-tuning.

## Check yourself

1. A PM wants to "fine-tune on our support docs so the bot stops making
   things up." What do you propose instead, and what's the one-line reason?
2. Name the RAG failure that fine-tuning *also* cannot fix.
3. Why is a 20-page fixed handbook a poor RAG candidate?

Next: [020 — The RAG pipeline](020-the-rag-pipeline.md)
