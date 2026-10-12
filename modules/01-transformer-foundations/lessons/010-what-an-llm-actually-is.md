# What an LLM actually is

**Reading time:** ~7 min · Module 1

If you've spent your career calling REST APIs and managing state, an LLM is going
to feel simultaneously familiar and alien. Familiar because it really is just a
function you call over an API. Alien because nobody can hand you its source-level
spec — the "logic" lives in billions of learned floating-point numbers.

This lesson gives you a working mental model precise enough to reason about
production behavior. Everything else in this module sharpens it.

## The one-sentence definition

An LLM is a function with this signature:

```python
def llm(tokens: list[int], weights: Tensor) -> list[float]:
    """Returns a probability distribution over the next token."""
```

Given a sequence of tokens (integers), it returns a probability for every token
in its vocabulary of being **the next one**. That's it. That is the entire
contract. Chat, code completion, translation, summarization — every capability
you've seen is this one function, called repeatedly.

Three consequences follow immediately from the signature:

1. **It has no memory.** The function is stateless. What looks like "the model
   remembering the conversation" is the caller passing the whole conversation
   back in `tokens` on every call.
2. **It predicts, it doesn't look up.** There is no database inside. "Knowing"
   something means: certain weight configurations make the next-token
   distribution put high mass on the right token.
3. **It's deterministic at its core.** Same input tokens + same weights = same
   output distribution. Randomness enters later, at sampling time (lesson 140).

## The stack, from your seat

As an engineer you'll touch four layers. Knowing which layer a bug lives in is
half the job.

```
┌─────────────────────────────────────────────┐
│ Your application code                        │  prompts, retries, parsing
├─────────────────────────────────────────────┤
│ Inference engine (vLLM, Triton, API provider)│  batching, KV cache, scheduling
├─────────────────────────────────────────────┤
│ Model (transformer + weights)                │  the actual math
├─────────────────────────────────────────────┤
│ Tokenizer                                    │  text ⇄ integers
└─────────────────────────────────────────────┘
```

Most "the model is broken" reports are actually layer 1 (bad prompt structure)
or layer 2 (timeouts, rate limits, quantization differences). Actual layer-3
failures — genuine capability limits — are rarer than they feel.

## What the numbers look like

A production model is a stack of transformer blocks, each holding matrices of
weights. Concrete scale, so the vocabulary of the field sticks:

| Model | Parameters | FP16 size | Rough VRAM to serve |
|---|---|---|---|
| GPT-2 small (the one we build later) | 124M | ~250 MB | laptop CPU |
| Llama 3 8B | 8B | ~16 GB | one 24 GB GPU |
| Llama 3 70B | 70B | ~140 GB | 2-4 datacenter GPUs |

"Parameters" = the entries in those weight matrices. One parameter = one float.
The model file you download **is** those numbers in a container format (safetensors,
GGUF); the architecture code just says how to multiply them together.

## Why next-token prediction is enough

The skeptical question worth sitting with: how does a next-token predictor write
working code or do arithmetic? The training signal is deceptively simple —
predict the next token over trillions of tokens of text — but to lower its loss
on that objective, the model is *forced* to internalize whatever structure makes
text predictable: syntax, facts, cause and effect, the shape of a Python function
signature. Prediction pressure is the teacher; the capabilities are side effects
that turn out to be general.

This framing also tells you the failure mode. Anything that doesn't reduce
next-token uncertainty wasn't learned well. The model knows the phrase
`"the capital of France is"` continues with `Paris` because that completion is
massively predictable in training text. It flubs a novel 12-digit multiplication
because nothing in pretraining made those specific digits predictable — there's
no algorithm inside doing long multiplication, just pattern completion.

## The mental model to carry forward

Think of the model as a **probability engine over text**:

- Input: context (tokens)
- Output: a probability distribution over every possible next token
- Everything you'll engineer — sampling parameters, prompts, fine-tuning,
  RAG — is an attempt to **move probability mass toward the tokens you want**
  and away from the ones you don't.

Keep that framing. Prompt engineering = reshaping the input so the desired
continuation is high-probability. Fine-tuning = permanently reshaping the
weights. RAG = putting the right text in the context so the right answer is the
predictable one. The rest of this course is variations on that theme.

## Check yourself

1. A teammate says "the model remembered what I said earlier in the session."
   What's actually happening, mechanically?
2. Why does lowering `temperature` to 0 make outputs reproducible, given the
   model itself is deterministic?
3. Your app needs to guarantee an output matches a JSON schema. Which of the
   four layers from the diagram would you trust to enforce that, and why can't
   you rely on prompting alone?

Next: [020 — The input/output contract](020-the-input-output-contract.md)
