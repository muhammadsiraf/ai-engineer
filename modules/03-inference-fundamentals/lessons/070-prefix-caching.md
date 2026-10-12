# Prefix caching

**Reading time:** ~6 min · Module 3

You already know prefix caching from the client side (Module 2 lesson 120:
stable-prefix structure, discount economics). This lesson is the server-side
mechanism — how a serving engine actually skips redundant prefill work, and
why your prompt structure decisions determine whether the mechanism fires.

## The observation

Requests repeat long prefixes constantly:
- same system prompt + tools on **every** request (your biggest fixed cost)
- multi-turn conversations: each turn resends the whole history + adds one
  message
- RAG re-queries with the same retrieved set
- A/B evals: identical prompts, different sampling

Prefill is the compute-bound phase (lesson 020) — it's the most *valuable*
work to skip. And thanks to causality (Module 1 lesson 110), a shared
prefix's KV state is *identical* across requests. You computed it once; the
second, tenth, ten-thousandth request can reuse it verbatim.

## The mechanism (with the pieces you now know)

1. **Block-aligned matching.** KV cache lives in fixed blocks (lesson 050).
   The engine hashes each block's token content into a chain: `hash(block_i)
   includes hash(block_{i-1})`, so a prefix match is walking a hash tree.
2. **Hit → reuse blocks.** A new request whose first k blocks hash-match
   existing blocks attaches to them (refcount++, copy-on-write if it
   diverges later). Prefill starts at the mismatch point.
3. **Miss → compute, and leave the blocks behind** for future requests.

What this means for cost and latency, with numbers from a typical setup:

```
system+tools prefix: 1,800 tokens   (every request)
per-request novel:     400 tokens

without prefix cache: prefill 2,200 tokens/request
with:                 prefill   400 tokens/request  → 82% of prefill work gone
```

TTFT drops correspondingly (prefill is the dominant TTFT term), and because
prefill is compute-bound, the GPU capacity freed is substantial at scale.

## Why YOUR structure decides hit rate

The engine can only reuse *exact, contiguous, block-aligned* prefixes. Your
prompt template is the hit-rate dial:

- ✅ `system + tools` byte-identical across requests, volatile content
  appended after — maximal hits (the `[stable][volatile]` discipline from
  Module 2 lesson 100/120)
- ❌ timestamp/user-id/session-id anywhere in the prefix — every request is
  a new prefix, zero hits
- ❌ retrieved documents *before* the system prompt in the rendered string —
  the stable part is buried behind volatile bytes
- ⚠️ multi-turn: works beautifully (history is a growing shared prefix)
  *if* your history serialization is deterministic — same truncation rules,
  same whitespace, same message ordering

Module 6's lab measures hit rate before and after fixing a deliberately
broken template — the delta is usually the most satisfying metric of the
week.

## Eviction and the cache's memory cost

Cached prefixes consume KV blocks (the shared ones cost nothing extra —
that's the refcounting beauty). Under block pressure the engine evicts
least-recently-used *leaf* blocks first (never a block someone's live
sequence is using). Practical consequences:

- Cache is best-effort: a burst of novel long prompts can flush it. Don't
  build correctness on hits; build *economics* on them.
- Tiny TTL/reuse windows get little benefit; your fleet should generally
  share one engine instance per model so the cache is warm fleet-wide.

## The client-side/server-side split (recap and tie)

| Layer | What it caches | Wins | Lesson |
|---|---|---|---|
| Your app (response cache) | complete request→answer | skips the whole call | M2 L120 |
| Engine (prefix cache) | prefill state for shared prefixes | skips prefill only | this |
| Both need | stable structure | — | M2 L100 |

They compose: response-cache misses fall through to the engine, which
hopefully prefix-hits. Note prefix caching also helps *different* prompts
sharing only a system prefix — response caching can't.

## Check yourself

1. A teammate inserts `"Session: {uuid}\n"` as the first line of every
   prompt. Estimate the hit rate and name the fix.
2. Multi-turn chat, turns 1–10: what fraction of turn 10's prefill can be
   cache hits if nothing else changed?
3. Why does eviction prefer leaf blocks? (Hint: what does the hash chain
   imply about block dependencies?)

Next: [080 — Quantization](080-quantization.md)
