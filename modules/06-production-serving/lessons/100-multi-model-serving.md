# Multi-model serving

**Reading time:** ~6 min · Module 6

Real platforms serve more than one model: draft + target (Module 3
lesson 100), distilled + frontier tiers (lesson 050's degradation),
per-customer adapters (Module 5 lesson 130), an embedding model, a
reranker (Module 4 lesson 090). The architecture question: one replica
per model, or several models sharing a GPU? This lesson is the decision
framework and the failure catalog.

## The three deployment shapes

1. **Isolated replicas** (model per fleet): full Module 3 isolation,
   independent scaling and SLOs. Costs: each fleet pays its own floor
   (lesson 090), KV cache memory is siloed, N fleets to operate.
2. **Packed co-location** (several models, one replica): the GPU's 80GB
   hosts a 7B server + embedding model + reranker with memory budgets
   per model. Wins on floor consolidation and lets the RAG pipeline's
   stages share a node (retrieval → rerank → generate without network
   hops). Costs: memory contention (one model's VRAM spike OOMs its
   neighbors), coupled scaling, noisy-neighbor latency.
3. **Engine-native multi-model:** one process serving several LoRA
   adapters over a shared base (vLLM multi-LoRA), or engine-managed
   model swap. The extreme of packing; the base weights are paid once —
   the adapter-fleet economics of Module 5 lesson 130.

## The decision arithmetic

Pack models together when: combined weights + KV comfortably fit (say
< 70% of VRAM), their traffic is correlated (they serve the *same
request pipeline* — the RAG case), and utilization of each is too low
to justify a floor. Keep them isolated when: SLOs differ sharply
(voice-tier vs batch), traffic is independent (one's peak is another's
trough — packing *increases* total capacity needed), or one model's
load is spiky enough to starve the rest.

The middle path most platforms converge to: **tier by criticality** —
interactive models isolated (protect the SLO), utility models
(embeddings, rerankers, batch summarization) packed.

## Failure catalog (packed fleets)

- **OOM roulette:** no per-model memory isolation → first spike wins.
  Mitigate with hard memory budgets per model and triage in lesson 030's
  load tests (test models *together*, not separately).
- **Latency interference:** compute-bound prefill of one model stalls
  another's decode (two schedulers, one SM array). The Module 3
  arithmetic applies per-model only when the GPU is quiet; co-location
  invalidates last quarter's load test — re-run it packed.
- **Upgrade coupling:** engine version serves all packed models at once;
  one model needing a newer engine forces a fleet-wide rollout (lesson
  110's canary, for all tenants at once).

## The tenant dimension

The same triad applies per *tenant* instead of per model: dedicated
fleets (enterprise isolation), shared fleet + quotas (standard), packed
adapters (Module 5). Routing (lesson 070) and rate limiting live at the
gateway; the serving shape below is chosen per tier by the same
arithmetic.

## Check yourself

1. Embedding model (2GB, 5% util), reranker (3GB, 10% util), 8B serving
   model (16GB weights + KV, 60% util). Propose the deployment triad and
   justify each choice in one line.
2. Why does "test models together, not separately" change load-test
   numbers? Which two interference effects are you measuring?
3. An enterprise customer demands dedicated capacity for their 3GB
   adapter. What does the Module 5 lesson 130 economics say about the
   price they should pay vs shared-adapter serving?

Next: [110 — Zero-downtime rollouts](110-zero-downtime-rollouts.md)
