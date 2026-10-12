# Rate limits, retries, and idempotency

**Reading time:** ~6 min · Module 2

Every LLM app at scale meets the 429. The difference between a blip and an
incident is the retry design — and the difference between a retry design and
a money incinerator is idempotency. This lesson is the production checklist.

## Reading the limits

Providers limit three axes, usually per-model and per-tier:

- **RPM** — requests per minute
- **TPM** — tokens per minute (often the binding constraint: your big
  prompts burn budget fast — lesson 090)
- **Burst capacity** — short-term headroom above the sustained rate

The 429 response usually tells you what to do: a `Retry-After` header, or
error metadata with the constraint hit. **Honor `Retry-After` before your
own backoff math.** Ignoring it is the fastest way to get escalating
penalties.

## The retry policy, concretely

Retryable: 429, 500/502/503/504, timeouts, connection resets.
Not retryable: 400/401/403/404/422 — your bug won't heal (Module 2 lesson
010's taxonomy).

```python
for attempt in range(max_retries + 1):
    try:
        return call()
    except RetryableError as e:
        if attempt == max_retries:
            raise
        delay = min(base * 2**attempt + jitter(), cap)
        if (ra := e.retry_after) is not None:
            delay = max(delay, ra)          # server is right, you are guessing
        sleep(delay)
```

The two non-negotiable ingredients:

- **Exponential backoff** (base × 2^attempt): a slammed service needs your
  pressure to *decay*, not persist. Typical: base 0.5–1s, cap ~30s,
  max_retries 3–5.
- **Jitter** (random ± on every delay): without it, a thousand clients that
  synchronized on one outage retry in a thundering herd on the same
  millisecond. Jitter breaks the synchrony; full random jitter between 0 and
  the backoff value is fine.

## The idempotency problem, precisely

Timeouts on an LLM call are ambiguous: **the generation may have completed
and billed on their side** while your socket died. A blind retry can pay
twice. Worse for side-effecting chains: an agent that retries a
"send refund email" tool (Module 8) can send it twice.

Layers of defense:

1. **Provider idempotency keys** where offered: send the same key on retry;
   provider dedups and returns the original result.
2. **Your own dedup for tool calls:** the executor keeps a short-TTL
   (`tool_call_id, args_hash) → result` store; retries hit the store, not
   the world. This is the challenge for this lesson.
3. **Semantics at the design level:** make side-effecting tools naturally
   idempotent when you can (upsert by external key, dedupe by request ID in
   the downstream system). The best retry policy is one where retries are
   safe by construction.

## Client-side rate limiting: don't get 429'd into it

Retries react to rejection; a token-bucket limiter in your client *avoids*
the rejection:

```python
class TokenBucket:
    def __init__(self, rate_per_min, burst): ...
    def acquire(self, tokens=1): ...   # blocks until budget available
```

Two buckets work best: one for **requests** (RPM) and one for **estimated
tokens** (TPM — `acquire(count_request(...))` from lesson 090). Per-model
buckets, shared across threads/processes via Redis if you're beyond one
box. The limiter turns your 429 graph from a sawtooth into a flat line —
and makes the remaining 429s a signal about *other* tenants, not you.

## Circuit breaking: when to stop trying

If the last N calls all failed, open the circuit: fail fast (or fall back to
a cheaper model — lesson 140's fallback ladder) for a cooldown, then probe
with a single request before restoring. Protects your latency SLO from a
provider brown-out and protects *them* during incidents. Standard library
implementations exist; wire it into the wrapper from lesson 010.

## The queue-shaped insight

Under sustained overload, **shed load visibly rather than degrading
silently**: accept fewer requests and answer them well, return 503+Retry-
After to the rest, autoscale the *self-hosted* tier (Module 6). An LLM
gateway that hides saturation behind 60-second p99s is worse than one that
says "busy" — plan the shed-reason headers into your API from day one.

## Check yourself

1. Why is naive `time.sleep(30)`-then-retry worse than exponential backoff
   with jitter? Give the failure mode for each missing ingredient.
2. Your agent's `book_flight` tool timed out; retry succeeded. The customer
   has two bookings. Which of the three defenses would have prevented it,
   and where does each live?
3. Design the two-bucket limiter for: 500 RPM / 300k TPM, with requests
   averaging 3k input tokens. What's your sustainable request mix?

Next: [140 — Provider comparison: OpenAI / Anthropic / open](140-provider-comparison-openai-anthropic-open.md)
