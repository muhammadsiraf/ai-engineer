# Speculative decoding

**Reading time:** ~7 min · Module 3

Speculative decoding is the cleverest trick in the serving toolbox: use a
cheap model to *guess* several tokens ahead, then have the expensive model
**check all guesses in one parallel pass**. Same output distribution as the
big model alone — mathematically guaranteed — at a fraction of the wall
clock. This lesson covers why it's exact, when it wins, and the arithmetic
the challenge makes you do.

## The mechanism

The bottleneck (lesson 020): decode generates ONE token per pass, memory-
bound. The observation: verification is different from generation — scoring
k tokens through the model is ONE forward pass over k positions (parallel,
prefill-like) instead of k passes.

```
loop:
  1. DRAFT:   draft model (7B) greedily proposes tokens d1..dk  (k tiny passes, cheap)
  2. VERIFY:  target model (70B) runs ONE pass over prompt + d1..dk,
              producing its own distribution at every position
  3. ACCEPT:  walk the draft tokens left to right:
              - target agrees (draft token ∈ its high-prob set) → accept, continue
              - first disagreement → reject it AND everything after,
                emit target's own token for that position
```

Either the run accepts all k drafts (k tokens for one big pass — jackpot) or
rejects at some point (you still got the prefix + a *free* corrected token
from the verification pass — verification never wastes the pass).

## Why the output is EXACTLY the target model's

The acceptance rule is a probability-corrected resample, not a similarity
check. For each position, with draft distribution q and target distribution
p:

- accept the draft token with probability `min(1, p(x)/q(x))`
- on rejection, sample the next token from the *adjusted* residual
  distribution `norm(max(0, p − q))`

The result is provably distributed exactly as p — the target model's own
output. This is the crucial property (and the pop-quiz answer): speculative
decoding changes SPEED, never DISTRIBUTION. Quality is bit-for-bit the
model's; there is nothing to evaluate on that axis. (Serving stacks still
let you tune draft length k — that's a performance knob, not a quality one.)

## The speedup arithmetic

Per accepted token, target work drops; per draft token, you add tiny draft
passes. With acceptance rate α (per token) and draft cost c (in units of
target-pass time):

```
expected tokens per verify pass:  (1 − α^(k+1)) / (1 − α)
speedup ≈ that ÷ (1 + k·c)
```

The challenge walks concrete numbers: α=0.8, k=4, c=0.1 →
E[tokens] = (1−0.8⁵)/0.2 ≈ 3.36, cost = 1 + 0.4 = 1.4 target-pass
equivalents → **~2.4x faster**. Same math drives the sensitivity story: at
α=0.5 the same setup wins ~1.3x; at α=0.95 it's ~3.3x. **Acceptance rate is
everything** — which is why draft choice matters more than draft size.

## Choosing the draft

Requirements: same tokenizer as the target (non-negotiable — token IDs must
align for verification), much smaller (c small), and crucially *similar
enough in behavior* that α is high. Standard choices: the same family's
small sibling (70B ↔ 8B, or 8B ↔ 1B); fine-tuned n-gram/draft heads; or
self-speculation variants (early-exit layers). Measure α on YOUR traffic
(sample 1,000 requests, log accept lengths) — α is a workload property, not
a model constant: code completion drafts better than poetry.

## Where it fits (and doesn't)

- **Wins:** low-batch decode (batch 1–8), latency-sensitive paths, long
  outputs. This is why it's the TTFT/TPS lever for interactive products.
- **Doesn't:** heavily batched serving (lesson 060 already made decode
  compute-bound — the spare bandwidth speculative decoding exploits is gone;
  the draft passes become pure overhead at high batch). Engines like vLLM
  expose it as opt-in per deployment; Module 6 keeps it off for throughput
  serving, on for the interactive tier.
- **KV-cache note:** rejected draft suffixes must roll back cache state —
  PagedAttention block refcounts (lesson 050) make that cheap (copy-on-write
  the divergent block).

## Check yourself

1. In one sentence: why can't speculative decoding change output quality?
2. Your workload has α=0.6, k=3, c=0.15. Compute the speedup. Worth it?
3. Why does heavy batching kill the benefit? Reference lesson 020's two
   regimes.

Next: [110 — Tensor and pipeline parallelism](110-tensor-and-pipeline-parallelism.md)
