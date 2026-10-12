# The input/output contract

**Reading time:** ~7 min · Module 1

Every integration bug I've seen in LLM apps traces back to a fuzzy mental model
of what goes in and what comes out. So let's make the contract exact — types,
shapes, and the places where implementations differ.

## Input: a list of token IDs (that you'll usually specify as text)

The API you call accepts text, but that's a convenience wrapper. The contract
underneath is:

```python
text  = "def hello():"
token_ids = [1181, 25, 19122, 424]   # model-specific integers
```

The mapping text → IDs is done by the **tokenizer** (lesson 030), and it is
model-specific: token ID `1181` means something different to Llama than to GPT-2.
You can never mix token IDs across model families.

The full input payload to a chat model is a list of messages, each with a role
and content:

```python
messages = [
    {"role": "system",    "content": "You are a helpful assistant."},
    {"role": "user",      "content": "Summarize this log..."},
    {"role": "assistant", "content": "Sure — here's what happened..."},
    {"role": "user",      "content": "Now make it shorter."},
]
```

Before the model sees any of this, the provider flattens the messages into a
single token stream, inserting special separator tokens between roles. You
don't control that template directly through most chat APIs — but you pay for
its tokens, and its exact shape affects model behavior. (Module 5 shows the
template when we fine-tune; getting it wrong there silently degrades the model.)

## Output: two distinct things people constantly conflate

**1. The raw output — a distribution.** For the last position in the input, the
model emits one score (logit) per vocabulary token. Vocab sizes are typically
32k–256k. These logits get converted to probabilities via softmax. This is the
true output of the `llm()` function from lesson 010.

**2. The API output — sampled text.** The inference stack then *picks* token(s)
from that distribution using your sampling parameters, and repeats until a stop
condition. What comes back over the wire:

```python
response = client.chat.completions.create(
    model="...", messages=messages,
    temperature=0.7,
    max_tokens=512,
    stop=["\n\n"],
)
response.choices[0].message.content   # str — the sampled text
response.usage                        # prompt_tokens, completion_tokens
```

Key fields to care about in production:

| Field | Why it matters |
|---|---|
| `content` | May be `None` when the run ended in a tool call or length limit — null-check it |
| `finish_reason` | `stop` (clean), `length` (truncated!), `tool_calls`, `content_filter` |
| `usage` | Your cost model. Log it always. |
| `logprobs` | Optional per-token probabilities — gold for eval and routing (Module 7) |

## The finish_reason you will get bitten by

`finish_reason: "length"` means the model wanted to keep going and got cut off.
JSON truncated mid-string is the classic result:

```json
{"summary": "The incident began when the deploy
```

Production rule: if you're emitting structured output, check `finish_reason`
*before* parsing. Retrying with higher `max_tokens` (or fixing the prompt) beats
a 3 a.m. `json.decoder.JSONDecodeError` page.

## Streaming changes the shape, not the contract

With `stream=True` you receive the same tokens, incrementally, as SSE events.
Two engineering notes:

- You're still billed for the full completion; streaming is UX, not savings.
- Each chunk is a few tokens. Reassembling and parsing the final text is your
  job; naive per-chunk JSON parsing is a rite-of-passage bug.

## Idempotency and the stateless contract

The API is stateless: send the same request twice and you get two (possibly
different — see lesson 160) completions, billed twice. Corollaries:

- "Editing" a conversation = resending the whole history, longer prompt, more
  cost. This is why context management is an engineering discipline (lesson 050).
- Retries on timeouts must be safe: a retry after a timeout you can't observe
  may double-bill you. Module 2 builds a retry strategy around exactly this.

## Check yourself

1. You need machine-parseable output. List, in order, the three defenses:
   finish_reason check, structured output/JSON mode, validation on your side.
2. Why does the 10th turn of a conversation cost more than the 1st, even if
   each user message is the same length?
3. Your integration tests pass with `temperature=0`. Why might production still
   see different outputs for identical prompts?

Next: [030 — Tokens: what one token actually is](030-tokens-what-one-token-actually-is.md)
