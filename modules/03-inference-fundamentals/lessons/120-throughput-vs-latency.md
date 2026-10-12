# Throughput vs latency

**Reading time:** ~7 min · Module 3

Every scheduling decision in this module trades throughput against latency.
This lesson gives that trade a mathematical spine — the queueing model, the
batch-size curve, and the procedure for picking operating points from SLOs.
It's the capstone of Module 3 and the input to Module 6's capacity planning.

## The fundamental curve

Per-batch decode throughput rises sublinearly with batch size (amortized
weight reads — lesson 020), while per-request speed falls:

```
throughput (tok/s, aggregate)
   │            ________
   │        ___/
   │      _/
   │    _/
   │  _/
   │_/
   └──────────────────────────── batch size
       ↑ knee

per-request TPS: roughly 1/(amortization gain) × batch interference →
monotonically decreasing with batch size
```

Below the knee, adding requests is nearly free (they ride along on
unclaimed bandwidth); past the knee, each addition steals from everyone
(curve saturates at VRAM/compute limits). **The operating point you want is
usually just left of the knee** — maximum throughput where the latency
SLO still holds.

## The queueing reality

Requests arrive randomly; the serving system is a queue in front of the
batcher. The two facts from queueing theory that run your life:

1. **Utilization creeps toward 1 → latency explodes.** At 90% utilization,
   queues are manageable; at 99%, p95 latency is ~100x the service time.
   Capacity planning at 95%+ utilization is planning for an outage.
2. **Variance is poison.** Mean arrival rate is a lie; bursts + long-tail
   service times (p99 output lengths!) dominate p95s. Headroom isn't waste;
   it's the price of a flat p95.

Rule of thumb for sizing: keep *offered load* ≤ 70–80% of measured knee
capacity, and re-measure the knee whenever model/traffic changes.

## From SLO to operating point (the procedure)

Your product says: "95% of responses start within 1.5 s and finish within
8 s." Walk it down:

1. **Token budget:** p95 output ≈ 700 tokens → need decode TPS ≥ 700/6.5s
   ≈ 108 tok/s per request at p95 → at batch B, per-request TPS ≈
   aggregate(B)/B → solve for the largest B satisfying it.
2. **TTFT budget:** TTFT = queue + prefill(tokens_in). Pre-measured prefill
   rate (lesson 020's calibration) + the engine's queue at utilization U →
   cap U so queue tail fits.
3. **Convert B and U into engine knobs:** max_num_seqs ≈ B,
   max_num_batched_tokens from the prefill chunking (lesson 060), and the
   replica count = offered load ÷ (B × per-request rate) ÷ 0.75.
4. **Verify by load test** (Module 6), not by faith: run the measured
   arrival process, watch p95 TTFT and p95 total. Iterate knobs.

The challenge `pick_batch_for_slo` makes you do exactly this arithmetic on
provided measurement tables — it's the interview question for this module.

## The three-way tension, honestly stated

```
throughput  ↑   (batch big, context long, quantize aggressive)
latency SLO ↑   (batch small, TTFT tight, speculative decoding on)
cost        ↑   (replicas + headroom, premium hardware, less quantization)
```

You pick two. The craft is knowing which axis your product actually needs:
a batch analytics pipeline wants throughput and cost (latency don't-care);
a voice assistant wants latency at almost any cost; a chat product lives on
the curve's knee with p95 SLOs. Write the priority ordering down per
service — most "inference is slow/expensive" meetings are two people with
different implicit orderings.

## The measurement discipline

Everything above runs on measured tables, and tables rot:

- Re-run the batch sweep after every model or engine upgrade
- Track p95 TTFT / p95 TPS / utilization per replica in prod (Module 6's
  observability), alert at the 80% utilization line
- Keep a synthetic load-test job (constant + burst profiles) in CI for the
  serving config — config drift shows up as knee shifts

## Module 3 recap — the chain you can now derive

Scheduler framing (010) → two phases (020) → KV state (030–040) → paged
allocation (050) → iteration-level batching (060) → skip shared prefill
(070) → shrink bytes (080–090) → start early (100) → scale out (110) →
and this lesson: choose operating points on purpose.

Next up, Module 4: with the serving stack understood, we build the most-
shipped LLM application pattern — RAG — on top of it.

## Check yourself

1. At 65% utilization your p95s are flat; at 85% they triple. What do you
   set as the autoscaling trigger and why not 90%?
2. Derive the max batch size for: aggregate throughput table
   B=1→90 tok/s, B=8→600, B=16→950, B=32→1,400, B=64→1,600; SLO needs
   ≥40 tok/s per request.
3. A PM proposes a 2x-longer system prompt "for quality." Latency/cost
   consequences through the whole stack — list four.

**Module 3 complete.** Next: [Module 4 — Retrieval-Augmented Generation](../../04-rag-systems/lessons/010-why-rag-exists.md)
