# Caching prompts and responses

**Reading time:** ~7 min · Module 2

Two completely different things are called "caching" in LLM engineering:

1. **Response caching** — *you* store request→completion pairs and skip the
   call entirely (money → ~zero, TTFT → ~zero).
2. **Prompt/prefix caching** — the *provider* discounts repeated input
   prefixes it has already prefilled (input cost −50–90%, TTFT down).

They compose. Both are mostly about *discipline in what you send*, and both
have sharp edges. This lesson covers both, plus the consistency rules that
make either safe.

## Response caching: your side

The pattern is a memoization layer in front of the provider:

```python
key = hash(canonical_request)   # model + messages + params + toolset VERSION
if (hit := store.get(key)) is not None:
    return hit["completion"]    # + mark: cached=True, saved=$X
result = call_provider(...)
store.set(key, result, ttl=...)
```

Design decisions, in order of pain:

**The key must canonicalize.** Whitespace, message ordering, and param
defaults that vary by call site will shard your cache into uselessness.
Build the key from a *normalized* request: sort what's unordered, strip
what's cosmetic, resolve defaults explicitly.

**Never cache on user-content-only keys for personal data.** If messages
contain per-user PII, the cache maps content → completion globally — treat
it as sensitive storage with the same access rules as logs (and encrypt at
rest like logs).

**TTL is a correctness dial, not a perf dial.** Cached answers freeze the
world ("what's my balance?"). Partition keys by content-version: include a
version string for the knowledge the answer depends on, so a knowledge-base
update invalidates by key, not by hoping the TTL expires.

**Deterministic params or bust.** Caching T=0.7 outputs and replaying them
converts your app to deterministic-by-cache — sometimes exactly what you
want (tests, demos), sometimes a silent behavior change. Decide explicitly.

## Prefix caching: the provider's side

Mechanism (Module 3 will build the serving-side version): prefill of your
prompt is computed once and its intermediate state (KV cache) is kept on
their fleet briefly; identical prefixes reuse it. Rules that make it work:

- **Stable content first.** `system + tool definitions` as one unchanged
  prefix; per-request content strictly after. One early volatile byte
  invalidates everything downstream.
- **Don't timestamp the prefix.** A date in the system prompt changes
  daily (and cache keys are content-sensitive). Move volatile data to the
  suffix.
- **Same model, same region, roughly-same-time** for hits; check the
  provider's minimum prefix length and TTL.
- **Watch the hit-rate metric** (response field or dashboard). If it's ~0
  while your prefix is supposedly stable, something in your template is
  mutating — find it by diffing rendered prompts in staging.

## The consistency rules (both kinds)

1. **Logged ≠ cached ≠ live.** Decide which is the source of truth for
   evals. Golden-set replays (Module 7) should bypass response cache or use
   a separate store, or you'll measure your cache, not your model.
2. **Invalidate on model/param change.** Include model version and the
   sampling params in the key. A silent provider bump + an old cache is a
   support-ticket generator.
3. **Budget the cache.** Unbounded stores become liabilities. Set TTLs and
   size caps per namespace; evict least-recently-used.

## What not to cache

- Tool-call *sequences* mid-agent (Module 8) — the loop's next step depends
  on live tool state; caching whole runs is usually wrong except for
  identical replays.
- High-entropy creative outputs where variety IS the product.
- Anything where "slightly stale" is a compliance problem (balances,
  moderation verdicts on new content).

## The compounding math

A realistic support-bot call: 900-token stable prefix (system + tools) +
300 volatile tokens + 150 output. At 10k calls/day, prompt caching alone
saves ~90% of the input bill; response caching (FAQ-shaped questions hit
20–40% in practice) removes 20–40% of *everything*. Together these two
boring layers routinely halve an LLM line item. Do them before any clever
optimization.

## Check yourself

1. Your prefix-cache hit rate is 0% despite a fixed system prompt. Give the
   four most likely template sins.
2. A PM asks "can we cache answers so the demo is snappy?" — what three
   questions do you ask before yes?
3. Design the cache key for a RAG endpoint (query + top-k docs + model +
   k) so that k changes and doc updates invalidate correctly.

Next: [130 — Rate limits, retries, and idempotency](130-rate-limits-retries-and-idempotency.md)
