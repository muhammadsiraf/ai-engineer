# PagedAttention

**Reading time:** ~7 min · Module 3

PagedAttention is the single most important idea in modern LLM serving —
vLLM's founding insight, now standard in every serious engine. It's virtual
memory for the KV cache. One idea, lifted wholesale from OS design, worth
2–4x throughput.

## The problem: fragmentation kills concurrency

The KV cache grows one token at a time, and sequences end at unpredictable
lengths. Classic allocator behavior under that pattern:

- **Preallocation waste:** to avoid reallocating per token, naive serving
  reserves `max_context` per sequence up front. You budget for 4,096 tokens;
  the conversation uses 400. **90% of your cache pool is reserved for
  nothing** while other requests wait.
- **External fragmentation:** sequences die at random times, leaving
  scattered holes; a new 3 GB sequence can't fit three 1.2 GB holes.

Result: the arithmetic capacity from lesson 040 is theoretical; real
utilization lands at 20–40%. Concurrency — the whole economic engine —
bleeds out through allocation overhead.

## The idea: pages, like virtual memory

The OS solved this exact problem for process memory in the 1960s: don't
allocate contiguous; allocate fixed-size **pages** and keep a page table
mapping logical → physical.

PagedAttention: chop the KV cache into fixed-size **blocks** (vLLM default:
16 tokens' worth). Each sequence holds an ordered list of block pointers
(its "page table"). Attention kernels gather K/V through the table instead
of assuming contiguity.

```
seq A: [blk 7][blk 12][blk 3][blk 41]   ← 4 pages, allocated as needed
seq B: [blk 8][blk 15]
pool:  block #s 0..N-1, allocated on demand, freed whole
```

Consequences, each worth real money:

- **No preallocation:** a sequence pays for what it has used, +1 block
  granularity (≤ 15 tokens of slack, vs thousands).
- **No external fragmentation:** blocks are uniform; any free block fits
  any sequence. Pool utilization → 90%+.
- **Cheap growth:** append = grab a block when the current one fills.
- **Instant sharing:** two sequences can point at the SAME block
  (copy-on-write) — the door to prefix caching (lesson 070) and beam-search
  sharing.

## Copy-on-write, the elegant part

When a sequence forks (beam search: top-2 continuations share the parent
prefix) or a new request matches a cached prefix, the new sequence's page
table simply references the existing blocks, refcount++ . Only when someone
*diverges* — writes a different token into a shared block — is the block
copied, page-table updated, refcount--. Exactly fork() semantics; exactly
why speculative decoding's rejected drafts (lesson 100) cost only the
divergent suffix.

## The numbers

Utilization: naive reserve-max runs at 20–40% effective cache utilization;
paged allocators report 85–96%. That's a 2–4x concurrency gain *before any
model or hardware change* — the cheapest throughput you will ever "buy."

Block-size trade-off: smaller blocks = less internal slack but more
page-table overhead and kernel-gather cost; 16 tokens is the empirical
sweet spot (it's a config you'll tune in Module 6).

## The pattern to steal

This lesson's transferable engineering lesson: **when a resource has
unpredictable lifetime and growth, fixed-size pages + indirection beat
contiguous allocation.** You'll see the same shape again in agent-state
stores (Module 8's memory) and in pricing multi-tenant GPU sharing
(Module 6's k3s work).

## Check yourself

1. Compute the waste: pool of 6.5 GB, reserve-max 4,096 tokens/sequence at
   128 KB/token, average conversation 500 tokens, 12 sequences live.
2. Why does block sharing make prefix caching *cheap to implement* rather
   than just useful?
3. What OS concept corresponds to: (a) the page table, (b) refcounted
   shared pages, (c) the OOM killer? (Fun, and it lands.)

Next: [060 — Continuous batching](060-continuous-batching.md)
