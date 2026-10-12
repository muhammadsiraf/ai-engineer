# Token counting before you call

**Reading time:** ~6 min · Module 2

The `usage` field tells you what a call *cost* — after you've paid. Counting
*before* the call is how you enforce budgets, prevent overflow, price
features, and decide routing. This lesson makes pre-flight counting exact.

## Why the response's `usage` isn't enough

| Need | Why post-hoc fails |
|---|---|
| Reject requests that won't fit | they'll error (or truncate) before usage exists |
| Enforce per-user budgets | you want to refuse, not bill-and-warn |
| Price a feature / show a quote | the estimate must precede the action |
| Route small→cheap / large→premium | routing happens before the call |

All of these need the count *first*.

## Counting exactly, offline

For OpenAI-compatible models, `tiktoken` gives exact counts with no network:

```python
import tiktoken
enc = tiktoken.get_encoding("o200k_base")   # match your model's encoding!
n = len(enc.encode(text))
```

For open-weight models, the HF tokenizer is the source of truth:

```python
from transformers import AutoTokenizer
tok = AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-3-8B")
n = len(tok.encode(text))
```

(First call downloads the tokenizer; cache it at deploy time — don't let the
first production request pay a cold download.)

**Pin the encoding to the model.** The classic silent bug: cost dashboard
counts with `cl100k_base` while the model switched to a newer encoding.
Numbers drift 5–15% and nobody can prove anything. Make tokenizer choice a
property of the model config object, not a global constant.

## Counting the conversation, not the string

A chat request's input tokens = sum over messages, **plus per-message
overhead and role-separator tokens** the provider inserts (Module 1 lesson
020). Two practical approaches:

1. **Approximate (fine for budgets/routing):** sum per-message content
   counts + a constant overhead fudge (~4–8 tokens/message). Calibrate the
   fudge against real `usage` once and revisit on model changes.
2. **Exact (for quotes/tests):** construct the provider's rendered prompt
   (for chat models this is internal; approximate) — or measure the delta
   between `usage.prompt_tokens` and your content sum in CI, and alert when
   drift exceeds a threshold.

Approach 2 done as a *drift alarm* is the production winner: you don't need
perfect offline counting, you need to know when your counting stops being
trustworthy.

## The overhead people forget to count

A request's true input = messages + **tool definitions** (easily 500–3,000
tokens; Module 8) + system prompt + the conversation's separator overhead.
Teams that count only user text routinely underestimate by 2–3x. Your
`count_request()` helper should take the full `messages` + `tools` +
`system`, not a string.

## Enforcing the budget, pre-flight

The guard clause your LLM gateway (challenge `llm-gateway`) needs:

```python
total = count_request(messages, tools) + max_output_tokens
if total > model.context_limit:
    raise ContextOverflowError(total, model.context_limit)
```

Decide policy *before* the raise: truncate history (drop oldest turns — but
see Module 1 lesson 170 for what that silently loses), summarize (Module 4
techniques), or 4xx to the caller with a helpful message. A pre-flight
refusal you designed beats a provider error you didn't.

## Cost estimation, the same shape

```python
def estimate_cost(req_tokens, out_tokens, model_cfg):
    return (req_tokens * model_cfg.input_price
            + out_tokens * model_cfg.output_price) / 1_000_000
```

The challenge for this lesson builds the full estimator: real tokenizer,
message overhead, tool overhead, per-model price table, and a quote function.
It's 60 lines and it's the most-reused code in every LLM codebase I've
worked on.

## Check yourself

1. Why is "count user text ÷ 4 chars" unacceptable for budget enforcement,
   and what's the minimal correct replacement?
2. Your dashboard says $1,100/month; the bill says $1,430. Give the three
   most likely counting gaps, in order of probability.
3. Design the pre-flight policy for a 128k model with 100k-context
   requests arriving: truncate, summarize, or refuse — and what does each
   cost the user experience?

Next: [100 — Context window economics](100-context-window-economics.md)
