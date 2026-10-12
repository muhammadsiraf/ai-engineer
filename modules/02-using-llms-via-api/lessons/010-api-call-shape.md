# The API call shape

**Reading time:** ~6 min · Module 2

Module 1 gave you the machine; this module is the practice of using it well.
We start with the call itself — the one request shape you'll make millions of
times — and the discipline of structuring code around it.

## The canonical call

Every provider's SDK is a skin over this shape:

```python
from openai import OpenAI

client = OpenAI()  # reads OPENAI_API_KEY

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a precise assistant."},
        {"role": "user", "content": "Classify: 'my order is late' -> [billing|shipping|other]"},
    ],
    temperature=0,
    max_tokens=20,
)

text = response.choices[0].message.content
usage = response.usage  # .prompt_tokens, .completion_tokens
```

The same call against a self-hosted model (Module 3/6) is deliberately
identical — OpenAI-compatible endpoints are a de-facto standard (vLLM serves
this exact shape). Write your client layer against the standard once, and
you can move between hosted and self-hosted models with a config change.

## What varies, what doesn't

| Always present | Usually set | Rarely touched |
|---|---|---|
| `model` | `temperature`, `max_tokens` | `top_k` (OpenAI: absent) |
| `messages` | `stop`, `response_format` | `logit_bias` |
| | `tools` (Module 8 prep) | `presence/frequency_penalty` |

Two settings deserve defaults in every codebase: `temperature` (set it
explicitly per endpoint — see the sampling table in lesson 140 of Module 1)
and `max_tokens` (unset = provider default, which may be either stingy or
enormous; either can break you — truncation or cost).

## The wrapper your codebase actually needs

Raw SDK calls sprinkled through business logic age terribly. Wrap once:

```python
class LLMClient:
    def __init__(self, client, model: str):
        self._client = client
        self._model = model

    def complete(self, messages: list[dict], *, temperature: float = 0.0,
                 max_tokens: int = 1024) -> str:
        resp = self._client.chat.completions.create(
            model=self._model, messages=messages,
            temperature=temperature, max_tokens=max_tokens,
        )
        choice = resp.choices[0]
        if choice.finish_reason == "length":
            raise OutputTruncated(choice.finish_reason)
        return choice.message.content or ""
```

What this buys: one place to add retries (lesson 130), logging/cost tracking
(lesson 090), caching (lesson 120), and provider swaps (lesson 140). The
Module 2 challenge set builds this wrapper piece by piece — the tests define
the behavior contract.

## Errors are part of the shape

The call succeeds, or it fails in one of four ways — your wrapper must know
all four:

1. **4xx — you're wrong:** bad API key, malformed messages, context overflow.
   Do not retry; fix the request.
2. **429 — rate limited:** retryable *with backoff* (lesson 130).
3. **5xx / timeout — their bad day:** retryable, but idempotency matters.
4. **200 but truncated/degenerate:** `finish_reason` checks + validation
   (Module 1 lesson 020). The sneakiest class — no exception is raised.

## Anatomy of the messages list, recapped operationally

- Roles from Module 1: `system`, `user`, `assistant` (and `tool` in Module 8).
- Cost model: every message, every turn, resent and re-billed (lesson 100).
- Some providers accept named few-shot examples as alternating
  user/assistant turns — the technique of lesson 030 lives in the messages
  list, not in some special parameter.

## Check yourself

1. Why does `finish_reason == "length"` deserve its own exception type in the
   wrapper rather than a log line?
2. Your wrapper catches timeouts and retries. Which failure mode becomes
   dangerous as a result, and what property of your requests mitigates it?
3. You want to switch from a hosted model to self-hosted vLLM. Enumerate what
   should and should not change in your codebase.

Next: [020 — System prompts vs user prompts](020-system-vs-user-prompts.md)
