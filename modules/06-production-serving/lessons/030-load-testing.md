# Load-testing

**Reading time:** ~7 min · Module 6

You cannot reason about capacity; you can only measure it. Load-testing is
how Module 3's curves get their numbers, how autoscaling thresholds get
calibrated (lesson 050), and how rollouts get pre-flight validation
(lesson 110). Done wrong it produces confident lies; done right it's the
ground truth every other lesson stands on.

## What a load test must replicate

- **The arrival process, not just the rate.** Real traffic bursts;
  constant-rate tests flatter you (Module 3 lesson 120: variance is
  poison). Test constant rate AND burst profiles (2x mean for 30s).
- **The request shape distribution.** Real p50/p95 input and output
  lengths, not synthetic 100-in/100-out. Token counts drive prefill
  compute and decode time — wrong shapes = wrong numbers.
- **The open-world reality:** requests don't wait for the previous one
  (open model), and clients time out. A closed loop of 50 virtual users
  hiding queue growth behind backpressure is measuring your test client,
  not your service.

## The protocol

1. **Define pass/fail before running:** the SLO (lesson 040) at the
   target RPS. "See how it does" is not a test.
2. **Step up load:** ramp RPS in stages (e.g., 25%, 50%, 75%, 100%, 125%
   of target), hold each until steady state (minutes, not seconds —
   queues and caches need time), record per stage.
3. **Record the knee:** aggregate throughput, p50/p95/p99 TTFT, p95
   end-to-end, per-request TPS, GPU utilization, KV-cache pressure —
   per stage. The batch-size curve from Module 3 lesson 120, now at
   fleet level.
4. **Find the SLO-breaking point:** the RPS where p95 first violates.
   That's your measured capacity; the autoscaler targets a fraction of
   it (lesson 050's headroom rule).
5. **Soak test at 70–80% of that:** hours at sustained load catching
   slow leaks (VRAM fragmentation, connection pool rot) that step tests
   miss.

## The numbers this produces (and who eats them)

- The replica-count table (lesson 050's input; challenge 030's data)
- The knee for Module 3 lesson 120's operating-point choice
- The error-budget burn rate per load level (lesson 040)
- The before/after for every config change — engine upgrade, quantization
  swap, template change (Module 3 lesson 120's "tables rot" rule: re-run
  after each)

CI discipline: a small nightly load test at fixed profile with alerting
on drift catches config rot and noisy-neighbor effects before users do.
Full battery: per release and per infra change.

## Failure modes of the practice itself

- Testing in an environment that doesn't match prod (GPU SKU, network,
  co-tenancy) — results transfer at your own risk.
- Forgetting the client's own limits (connection pools, CPU) — the
  classic "our service is slow" that was the load generator dying.
- Trusting averages — always percentiles; the challenge this module
  computes p99 from raw samples for exactly this reason.
- No runbook for "load test says no" — decide in advance what a failed
  test triggers: capacity purchase? SLO renegotiation? traffic shaping?

## Check yourself

1. Your constant-rate test passes p95 at target RPS; production p95
   violations appear daily at that same mean rate. What property of real
   traffic did the test miss, and which test profile catches it?
2. Why does each ramp stage need a soak before measuring? Name the two
   stateful things still equilibrating.
3. Load test says capacity is 40 RPS at SLO. Traffic forecast: 30 RPS
   mean with 3x bursts. What's the verdict and the two mitigations?

Next: [040 — SLOs and error budgets](040-slos-and-error-budgets.md)
