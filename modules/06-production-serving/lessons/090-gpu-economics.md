# GPU economics

**Reading time:** ~7 min · Module 6

Serving is a business with one commodity input (GPU-hours) and one
revenue unit (tokens served). Every decision in this module — batch
sizes, quantization, routing, autoscaling floors — is this lesson's
arithmetic in disguise. The challenge computes the number that
management actually asks for: **cost per million tokens.**

## The unit equation

```
cost_per_1M_tokens = cost_per_replica_second ÷ (replica_tokens_per_s ÷ 1e6)

replica_tokens_per_s = aggregate throughput at your operating batch
                        (Module 3 lesson 120's knee, from lesson 030's tests)
cost_per_replica_second = hourly GPU price ÷ 3600  (+ overhead share)
```

Worked shape: A100-class at ~$2/hr, 1,400 tok/s aggregate at the knee →
$0.000556/s ÷ 1.4 tok/×10⁻⁶ → **~$0.40 per million output tokens.**
Compare managed-API pricing and the self-host margin appears — *if* the
utilization assumptions hold.

## Utilization is the whole game

The formula's brutal secret: throughput is measured at *your batch*,
but you pay for wall-clock. A replica at 30% utilization costs the same
as one at 70% — so cost per token scales inversely with utilization.
Concretely: the $0.40 above assumes you achieve 1,400 tok/s sustained;
at half that it's $0.80. This is why:

- lesson 070's routing (cache hits = fewer replica-seconds per token),
- lesson 050's floors (idle min replicas are pure cost),
- Module 3's quantization (2x throughput at same price → half cost),
- and batching discipline (Module 3 lessons 060/120)

are all *cost* lessons wearing engineering clothes. The lever ranking
for cost-per-token, usually: batch/utilization > quantization > engine
choice > hardware tier.

## Fixed vs variable: the floor problem

min replicas (lesson 050) are a fixed cost — you pay for night-time
capacity nobody uses. Two honest responses: (1) consolidate — fewer,
bigger replicas with higher per-replica utilization; (2) share the floor
across models/tenants (lesson 100's multi-model serving). The naive
response — no floor — reappears as cold-start SLO violations, which cost
more than the floor did. Price both before arguing.

## The finance view (what to put in the doc)

- **Cost per request** and **cost per million tokens**, by tier — split
  input/output (prefill vs decode cost differs, Module 3 lesson 020).
- **Utilization** per fleet, per hour — the health metric of the
  economics.
- **Unit economics trend** — is cost/token falling with each
  optimization cycle? (It should; if not, the optimizations are fake.)
- **Break-even vs managed APIs** at current utilization — revisit
  quarterly; the answer flips with traffic shape and price cuts.

## The traps

- Quoting throughput from a benchmark at batch 1 (best latency, worst
  economics) or from the engine's marketing (their workload, not yours).
- Forgetting overhead: gateway hosts, storage, the on-call human.
  Overhead is real but should be < 20% of GPU cost; if it's more, the
  fleet is too small to self-host.
- Optimizing tokens nobody asked for (max_tokens generosity — cap
  outputs; every wasted token is money).

## Check yourself

1. Compute cost per 1M output tokens: GPU $1.60/hr, 800 tok/s aggregate
   at operating batch, 80% sustained utilization. What does 50%
   utilization do to it?
2. Why does input/output cost split matter for the finance doc, in
   Module 3 lesson 020's terms?
3. Your cost/token doubled after adding a second model to the fleet.
   Name the two most likely lines this shows up in, and the lesson that
   fixes each.

Next: [100 — Multi-model serving](100-multi-model-serving.md)
