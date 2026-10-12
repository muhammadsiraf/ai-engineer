# Continuous batching

**Reading time:** ~7 min · Module 3

Batching is the throughput superpower (lesson 010); continuous batching is
what makes the superpower usable in production. The difference between
static and continuous batching is the difference between a demo and a
serving stack — and it's purely a scheduling idea.

## Static batching and its waste

Static (batch-at-a-time) serving: collect N requests, run all N to
completion, return all N, collect the next N. The problem: sequences in a
batch finish at wildly different times (different output lengths), but the
batch is a single unit of work:

```
batch of 8, outputs: [200, 180, 900, 210, 150, 190, 175, 205] tokens
                     → 7 sequences FINISH early, GPU keeps decoding
                       one long straggler with a batch-shaped-hole
```

All the finished slots still occupy memory and a slot in every step's
compute. Effective utilization craters for the whole duration of the
straggler — and with p99 output lengths 10x the median, *there is always a
straggler*.

## The fix: iteration-level scheduling

Continuous (dynamic) batching: **the batch is re-formed every decode step.**

```
every step:
  - finished sequences leave (their KV blocks free instantly — PagedAttention)
  - waiting requests join (their prefill is chunked in — lesson 020)
  - the step runs over whoever is present
```

No sequence ever blocks the batch. New work starts within one step of
arriving; finished work releases within one step of ending. GPU occupancy
stays high regardless of output-length variance — the waste above simply
stops existing.

## What it changes operationally

**Latency:** requests no longer wait for a "batch to fill" or a "batch to
finish" — TTFT collapses to queue + prefill-chunk. This is why modern
engines hold good p95 under load while naive stacks fall off a cliff.

**Throughput:** sustained high batch occupancy → the 5–10x aggregate gains
over static, on top of static's gains over batch-1.

**Implementation complexity (why it took until 2022–23 to standardize):**
the scheduler must juggle per-step admission, prefill/decode mixing
(chunked prefill), block accounting (PagedAttention), preemption under
memory pressure, and SLO-aware ordering. This is the "scheduler" of lesson
010 made real — and it's *the* core of vLLM's value.

## Tuning the knobs (you'll set these in Module 6)

- **max_num_seqs** — cap on concurrent sequences in the batch. Higher =
  more throughput, worse per-token latency; lower = the reverse. Set from
  lesson 120's SLO math.
- **max_num_batched_tokens** — cap on tokens per step across prefill+decode
  (chunked prefill size). Bounds the TTFT damage a giant prompt can do.
- **preemption mode** — what to evict under block pressure (recompute vs
  swap).

The challenge set for this lesson has you *simulate* a continuous batcher:
a discrete-event loop with arrivals, decode steps, and block accounting —
then answer SLO questions from the simulation (challenge: pick the batch
for your SLO). Writing 80 lines of simulator teaches more about serving
than a week of config docs.

## The mental model to keep

A serving engine is a pipelined assembly line where:
- **admission** = a queue with a bouncer (token budget, seq cap)
- **prefill chunks** = big parcels interleaved with small parcels
- **decode steps** = the heartbeat; every heartbeat the line reshuffles
- **KV blocks** = the pallets (paged, shared, freed instantly)

Latency SLOs are contracts between the bouncer and the heartbeat. Everything
in Module 6's deployment work is configuring this line and proving it holds
its contracts under load.

## Check yourself

1. In the static batch above, compute utilization: what fraction of
   sequence-steps were spent decoding already-finished sequences?
2. Why does continuous batching need PagedAttention to work well, but not
   vice versa?
3. Your p50 output is 120 tokens, p99 is 1,500. Which batching scheme
   suffers more, and what's the utilization intuition?

Next: [070 — Prefix caching](070-prefix-caching.md)
