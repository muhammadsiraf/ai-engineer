# Prefix-aware routing

**Reading time:** ~6 min · Module 6

Module 3 lesson 070 built prefix caching inside one engine. But your fleet
is N replicas with N independent caches — and a load balancer that
sprays requests randomly sends each request to a replica whose cache has
never seen its prefix. Prefix-aware routing fixes the mismatch: **route
requests sharing a prefix to the same replica**, so the cache actually
hits at fleet level.

## The mechanism

Extract a routing key from the request — hash of the stable prefix
(system prompt + tools, per Module 2's stable/volatile discipline), or
the session/conversation id — and route by `hash(key) mod N`
(consistent hashing so N changes don't reshuffle everything). Same key →
same replica → its prefix cache is warm for exactly those requests.

The win, in Module 3 lesson 070's numbers: a 1,800-token shared prefix
on every request, cache hit rate 0% under random routing (each replica
sees each prefix rarely), ~82% prefill work eliminated under affinity.
At fleet scale that's replicas you don't have to buy (lesson 090).

## The challenge's arithmetic

The gauge is the **hit rate**: requests that found a warm prefix ÷
requests. Measured from engine metrics (`cached_tokens / total_prompt_tokens`
in vLLM's prometheus exporter). Routing policy changes move this number
more than any engine config — the challenge scores candidate routing
policies against a request log, computing each policy's expected hit
rate.

## The failure modes (affinity has a price)

- **Hot spots:** one giant customer or one dominant system prompt pins a
  replica to 100% while others idle. Mitigations: cap the shard weight,
  split hot prefixes across a small set (2–3 replicas sharing a hot key
  still hits ~most of the cache), or fall back to least-loaded when a
  shard saturates.
- **Autoscaling resharding:** scaling N reshuffles keys (consistent
  hashing limits it); new replicas start cold (lesson 060) — another
  reason scale-out events need pre-warming.
- **Stateful routing + failures:** the replica holding a hot shard dies;
  the shard lands elsewhere cold. Health-aware consistent hashing, and
  accept the transient hit-rate dip.
- **Stale-routing bugs:** session affinity based on *client* IP or
  naive first-token hashing silently misses the actual shared prefix —
  measure hit rate per *policy change*, not per quarter.

## When NOT to bother

Uniform traffic with no shared prefixes (random short prompts) — no
prefix structure, nothing to exploit: plain least-loaded routing wins
because affinity adds skew without cache benefit. The hit-rate metric
tells you which world you're in before you build the machinery.

## Check yourself

1. Fleet of 8 replicas, 5 distinct system prompts with traffic shares
   60/20/10/5/5. Sketch the affinity layout and name the shard you'd
   split first.
2. Hit rate dropped from 80% to 20% after a deploy. Give the three most
   likely causes in order of probability.
3. Why does Module 2 lesson 100's stable-prefix discipline now have a
   *server-side* dollar value? Trace the mechanism from template to GPU
   cost.

Next: [080 — Packaging the GPU container](080-packaging-the-gpu-container.md)
