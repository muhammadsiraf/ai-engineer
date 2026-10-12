# Latency: time-to-first-token vs total

**Reading time:** ~6 min · Module 2

LLM latency has two components with different causes and different fixes.
Conflating them is why teams optimize the wrong thing. This lesson splits
the number, explains each half mechanically, and gives you the diagnostic
that points at the right lever.

## The decomposition

```
total = TTFT + TPS × output_tokens
        ↑        ↑
        │        └─ decode speed (tokens/sec) after generation starts
        └─ time to first token = network + queue + prefill(your prompt)
```

- **TTFT** scales with **input size** (prefill — every input token must be
  processed once before the first output token exists) and with provider
  **queueing/load**.
- **TPS** (decode speed) is mostly a property of the *model and hardware* —
  the autoregressive loop (Module 1 lesson 130) — plus your network
  streaming.

Concrete intuition for magnitudes: a hosted flagship might run ~1–3s TTFT on
a 10k-token prompt and 40–80 tok/s decode. A 500-token answer: 1–2 s prefill
+ 7–12 s decode. **Decode dominates for long outputs; prefill dominates for
huge inputs.** Your optimization target depends on which regime you're in —
measure first.

## Measuring it properly

```python
t0 = time.perf_counter()
stream = client.chat.completions.create(..., stream=True)
first = next(iter(stream)); ttft = time.perf_counter() - t0
for event in stream: ...                     # count tokens as they arrive
total = time.perf_counter() - t0
tps = (n_tokens) / (total - ttft)
```

Log `ttft`, `tps`, `output_tokens`, and `input_tokens` separately, per
model and per feature. A single "latency" number will lie to you: p95 TTFT
spikes are provider load; p95 TPS drops are your network or their region.
(Non-streaming callers can't see the split — another reason to stream, or
at least to measure with a streaming probe in your synthetic monitors.)

## Fixing TTFT (input-side levers)

1. **Shrink the prompt.** Every input token costs prefill. Context hygiene
   (lesson 100) is a latency feature, not just a cost feature.
2. **Prompt caching.** Cached prefixes skip most prefill work — the single
   biggest TTFT lever for long stable prefixes. Structure prompts as
   `[stable][volatile]` (lesson 120).
3. **Skip the queue:** provisioned throughput / priority tiers when the
   budget exists; region selection to cut network RTT.
4. **First-token tricks:** a short fixed prelude (model emits e.g. "On it —
   finding your order...") makes perceived TTFT tiny. Genuinely useful for
   agent loops (Module 8); don't let it replace real optimization.

## Fixing TPS/output-side levers

1. **Generate fewer tokens.** The most reliable speedup: tighter max_tokens,
   summarization instead of full quotes, structured fields instead of
   prose. Output tokens are linear cost on both money and wall clock.
2. **Smaller/faster model for the job** — the routing lever from lesson
   100. TPS is roughly a model-size property; a small model can decode 3–5x
   faster than a flagship.
3. **Speculative decoding and serving tricks** are real (Module 3) but
   they're the *provider's* or *your serving stack's* lever, not the API
   caller's.

## Budgeting like an SRE

Work backward from product targets:

```
"Answer within 3s for 95% of users"
  → budget TTFT ≤ 1.2s (incl. network), output ≤ 90 tokens @ 60 tok/s
  → derive: max prompt size, max output budget, which models qualify
```

That arithmetic decides design choices *before* benchmarking: it's why the
extractive summary beats the eloquent paragraph, and why the tool result
should be a line, not a JSON dump. Write the latency budget into the
service's config and alert on it (p95 by feature, excluding the 1% jobs
that are legitimately heavy).

## The percentiles that matter

- **p50 TTFT:** what most users feel
- **p95 TTFT:** queueing/discovery of capacity problems
- **p95 total:** the "this feature feels slow" number for long generations
- **max output_tokens × slowest TPS:** your worst-case wall clock — is it
  within a browser/webhook timeout?

Track them per feature. An aggregate average across a 40-token classifier
and a 1,500-token writer is a meaningless number.

## Check yourself

1. A feature regressed from 4s → 9s. Input size didn't change; outputs
   tripled. Which term blew up, and what are your two cheapest fixes?
2. Why does prompt caching improve TTFT but not TPS?
3. Your webhook consumer times out at 10s. p95 output is 700 tokens at 50
   tok/s; TTFT p95 is 2.5s. Design the fix in priority order.

Next: [120 — Caching prompts and responses](120-caching-prompts-and-responses.md)
