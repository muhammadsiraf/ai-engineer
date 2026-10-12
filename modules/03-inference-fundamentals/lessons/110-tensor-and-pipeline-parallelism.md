# Tensor and pipeline parallelism

**Reading time:** ~6 min · Module 3

A 70B model in FP16 needs ~140 GB. Your biggest GPU has 80 GB. When the
model doesn't fit — or you need more than one GPU's bandwidth — you shard it.
There are two classic ways to slice a transformer across devices, with very
different personalities. This lesson gives you the working vocabulary and
the decision arithmetic.

## The two axes of sharding

**Tensor parallelism (TP):** slice *within* each layer. Split the big
matmuls (lesson 080 of Module 1: the attention QKV, the MLP up/down
projections) column-wise or row-wise across GPUs. Every layer requires the
GPUs to exchange partial results (all-reduce / all-gather) — twice per
layer, per token.

**Pipeline parallelism (PP):** slice *across* layers. GPU 1 holds layers
1–20, GPU 2 holds 21–40, and so on. A sequence flows through the pipeline
like an assembly line; no per-token cross-GPU math within a layer, just
activations handed down the line once per layer boundary.

## The personality difference

**TP: tight coupling, high bandwidth need.** Every token, every layer
synchronizes across all TP ranks. That's why TP ranks must sit on *fast
interconnect* (NVLink, ~900 GB/s) — over PCIe (~64 GB/s) the all-reduce
stalls dominate and everything crawls. Rule of thumb: TP within one node.

The upside: work is split finely and evenly; latency of a single request
improves nearly linearly (the per-layer matmuls are smaller, and each GPU
holds fewer weights). TP-4 makes one request *faster*, not just more
capacity.

**PP: loose coupling, bubble-shaped waste.** Layers hand off once per
boundary; interconnect demands are modest (works across nodes, InfiniBand
or even Ethernet-friendly). The cost is the **pipeline bubble**: while GPU
1 processes microbatch n+1, GPU 2 is still on microbatch n — any moment a
rank waits is a rank idle. With few in-flight requests, most of the
pipeline is bubble.

The classic fix — **microbatching** — feeds multiple requests through the
pipeline interleaved so every rank always has something; with continuous
batching upstream (lesson 060) keeping the pipeline full is the scheduler's
real job. PP increases *capacity*; TP increases *per-request speed*.

## The decision arithmetic

```
Does the model fit one GPU (with KV room, lesson 040)?
  yes → no sharding. (Single-GPU serving is the performance baseline.)
  no  → smallest TP degree that fits, within one node:
        TP = ceil(needed_GB / usable_GB_per_GPU)
Still capacity-hungry (throughput, or model huge even at TP-node-max)?
  add PP across nodes: total ranks = TP × PP
Data parallelism (DP): full model replicas behind a load balancer —
  for scale beyond one replica; combine with TP/PP (the "3D parallelism"
  of training shows up in serving topologies too, just simpler).
```

Concrete: 70B FP16 (140 GB) on 8× A100-80GB node → TP=2 (70 GB/GPU — too
tight with KV; lesson 040 says leave cache room) → TP=4 (35 GB/GPU weights,
plenty of KV) with DP=2 for throughput. vLLM command: `--tensor-parallel-size 4`
plus a second replica. Module 6 runs exactly this decision on a small
scale.

## What breaks in practice

- ** Uneven shards:** d_model not divisible by TP degree → padding, waste.
  Check divisibility before picking TP.
- **Interconnect lies:** "it worked on the test node" — then prod boxes
  have NVLink bridges in a different topology and TP-8 throughput halves.
  Benchmark on the actual fleet.
- **Failure domains:** one TP rank dies, the whole worker dies. Kubernetes
  placement rules (Module 6's k3s lab) exist to keep TP groups together.
- **VRAM miscounting:** TP shards *weights* by N but the *KV cache* is
  also sharded (each rank holds its heads' K/V) — lesson 040's formula
  applies per-rank with H_kv sharded too.

## The one-paragraph summary to keep

Fit first (quantize before sharding — lesson 080's 4x is cheaper than 4
GPUs). Speed per request → TP within a node. Throughput and very-large
models → PP across nodes, kept full by continuous batching. Capacity beyond
that → data-parallel replicas behind the router (Module 2 lesson 100's
pattern, one level down). Sharding is the LAST lever, not the first.

## Check yourself

1. Why does TP hate PCIe while PP tolerates it? (Count the
   synchronization events per token.)
2. 180B-parameter model, FP16, 80 GB GPUs. Propose TP/PP and defend in two
   lines of arithmetic.
3. Your TP-2 deployment shows GPU util at 55% with p95 TTFT fine. Which
   lever do you reach for first — and why not TP-4?

Next: [120 — Throughput vs latency](120-throughput-vs-latency.md)
