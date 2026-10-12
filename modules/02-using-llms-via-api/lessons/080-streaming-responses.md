# Streaming responses

**Reading time:** ~6 min · Module 2

Perceived latency is dominated by time-to-first-content. A 12-second answer
that starts printing at 800 ms feels better than a 6-second answer that
appears all at once. Streaming is the feature that delivers this — and it
comes with real engineering costs. Here's the honest version.

## What's actually flowing

With `stream=True`, the API sends Server-Sent Events: small chunks, each a
few tokens, in order:

```python
stream = client.chat.completions.create(model=MODEL, messages=msgs, stream=True)
for event in stream:
    delta = event.choices[0].delta          # incremental text fragment
    if delta.content:
        print(delta.content, end="", flush=True)
# final event(s) carry finish_reason and (often) usage
```

The chunks are literally the autoregressive loop (Module 1 lesson 130)
forwarded over the wire as it runs. Three properties follow:

- **Order is guaranteed; grouping is not.** Chunk boundaries are
  implementation detail — never assume a chunk = a word or a line.
- **You can't know it's over until it's over.** Only the terminal chunk has
  `finish_reason`.
- **Usage may arrive at the end** (some providers need `stream_options` to
  include it). If you build cost accounting, handle both conventions.

## The two costs nobody budgets for

**1. It's UX, not savings.** Identical tokens are billed whether streamed or
not (lesson 020). In fact streaming usually *adds* overhead: one HTTP
connection held open per response, more requests through your proxy, more
infrastructure to keep alive.

**2. It breaks your pipeline's assumptions.** Everything downstream of "a
string came back" must now handle "a string is *becoming*": logging (write
on close, not per chunk), caching (cache the *assembled* result, lesson
120), retries (you cannot retry mid-stream — see below), and moderation/
validation (you can't validate JSON until it's complete).

## The retry problem, precisely

Non-streaming: timeout → retry, clean. Streaming: tokens have already gone
to the user when the stream dies at 80%. You can't "unsend" them. Options,
in increasing sophistication:

1. **Retry only if nothing was emitted yet** — safe, covers the common
   connection-refused case. Track `emitted_any`.
2. **Retry-with-note:** if the stream dies midway, emit a fresh stream
   prefixed with a visible "(reconnecting...)" — honest but clunky.
3. **Buffer-then-flush with cutoff:** buffer behind a spinner and only
   stream after N tokens arrive; trade some perceived latency for resilience.
4. **Background completion:** stream into storage while showing a progress
   UI; user reads the stored result. Loses the whole point for chat.

Production chat UIs mostly live on option 1 plus a graceful error card.

## When NOT to stream

- **Structured output.** Parse-at-end anyway; streaming buys nothing but
  complication (except fancy partial-JSON UIs — skip until you need them).
- **Machine-to-machine calls.** Your service calling another service wants
  one response object, timeouts, and retries. Stream only at the *user*
  boundary.
- **Short outputs.** A 40-token classification arrives faster than the
  stream handshake in most networks. Measure before defaulting to stream.

## Architecture note: stream at the edge, not through everything

The clean pattern: your backend makes a **non-streaming** call to the LLM
(or streams internally into storage), and your *edge/frontend* uses SSE or
WebSockets against your own service for the user experience. This keeps
retries, caching, and cost accounting in simple non-streaming code, and
contains streaming complexity to the one place it pays: the browser.

Many teams invert this (LLM stream → proxy → user) and end up writing
teeing/buffering middleware to recover the properties they gave up. Start
with the clean pattern; earn the inversion when scale demands it.

## Check yourself

1. Where in a streaming response does `finish_reason` appear, and what does
   your code do with `"length"` mid-UI?
2. Your chat service streams directly from the provider. A deploy restarts
   mid-response. What does the user see, and which mitigation do you pick?
3. Why does caching interplay badly with streaming, and what's the fix?

Next: [090 — Token counting before you call](090-token-counting-before-you-call.md)
