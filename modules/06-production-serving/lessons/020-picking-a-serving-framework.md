# Picking a serving framework

**Reading time:** ~7 min · Module 6

vLLM, TGI, SGLang, TensorRT-LLM, llama.cpp, LMDeploy, plus the
managed endpoints (Sagemaker, Bedrock, Azure AI, Together, Fireworks).
The zoo is loud because every engine is optimizing a different point on
the same curve. The pick is an architecture decision you'll live with
for quarters, so the lesson is the decision procedure, not the verdict.

## What actually differentiates engines

All serious engines implement Module 3's toolbox (paged KV, continuous
batching, prefix caching). The differences that matter:

1. **Raw throughput/latency at YOUR shape** — batch sizes, sequence
   lengths, model family. Differences of 10–30% are common and 10% of
   GPU spend is real money; benchmark, don't quote blog posts.
2. **Feature coverage for your tricks:** speculative decoding? quantized
   checkpoints (which formats — Module 3 lesson 090's zoo)? dynamic
   adapter serving (Module 5 lesson 130)? structured output? Multi-LoRA?
3. **Model family coverage and update cadence:** new architecture drops;
   how fast does the engine support it?
4. **Operational surface:** metrics you can scrape, config you can
   understand, memory of the community when it breaks at 3am.

## The benchmark that decides

Take your *real* traffic shape: p50/p95 input+output lengths, target
concurrency, model. Run 2–3 candidate engines with the same model artifact
(same quantization!), same load profile, measure: aggregate tok/s, p95
TTFT, p95 end-to-end, VRAM headroom. Module 3 lesson 120's procedure
gives the harness; the winner is the one that hits your SLO at the
lowest cost, and second place is often within noise.

## Managed vs self-hosted, honestly

- **Managed endpoints:** you trade 30–60% price premium and less config
  control for zero ops. Right answer for early stage, spiky traffic, or
  small teams. Same SLO/observability discipline applies — their
  dashboard is not your observability.
- **Self-hosted:** the premium is your margin; the price is everything
  in this module. Makes sense at sustained utilization, with
  customization needs (adapters, custom runtime), or data-residency
  requirements.

The decision flips with utilization (lesson 090's math): a 24/7 70%
utilized fleet amortizes ops costs easily; 10% sporadic usage never will.

## The migration insurance

Whichever you pick, wrap it: your app talks to an OpenAI-compatible
interface through *your* gateway, never to the engine's private API.
Engines are swappable at that boundary; the cost of the abstraction is
near zero and it converts "pick a framework" from marriage to dating.

## Check yourself

1. Two engines differ 15% in benchmarked throughput at your shape. Walk
   the annual-cost math that makes the slower one potentially still
   right.
2. Why does "same model artifact, same quantization" matter when
   benchmarking engines? What cross-comparison would violate it?
3. Name the three questions about *your workload* (not the engine) that
   decide managed vs self-hosted.

Next: [030 — Load-testing](030-load-testing.md)
