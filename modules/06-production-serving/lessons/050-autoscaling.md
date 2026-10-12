# Autoscaling

**Reading time:** ~7 min · Module 6

CPU autoscaling doctrine (scale on load, react in seconds, scale to
zero) is wrong for GPU serving in every particular. GPU autoscaling is a
slower, buffer-based discipline — because capacity takes minutes to
arrive, costs real money while idle, and queueing collapses latency long
before utilization looks alarming (Module 3 lesson 120's fact #1).

## Why the CPU playbook fails

- **Scale-out latency:** a GPU replica takes 1–5 minutes to schedule,
  pull the image, and *load the model* (lesson 060). By the time a
  reactive scaling event completes, the traffic spike that caused it is
  20 minutes gone — and the queue during the gap burned your error
  budget.
- **Utilization is a lagging, lying signal:** GPU "utilization" metrics
  report kernel-active time, not capacity; a saturated scheduler can
  show 80%. Scale on demand-vs-capacity (queue depth, tokens-in-flight),
  not on GPU meters.
- **Scale-to-zero is a fiction** with 3-minute cold starts. Min replicas
  = your burst survival plan.

## The buffer-based design

1. **Sizing unit from load tests** (lesson 030): capacity per replica =
   the measured SLO-safe RPS (or tok/s) at your traffic shape. Call it C.
2. **Replicas needed** = peak_demand / C ÷ target_utilization, with
   target utilization 0.7–0.8 — the headroom absorbs bursts and the
   minutes-long reaction gap. (The challenge computes this from a table.)
3. **Signal:** queue depth per replica (requests waiting > X ms) or
   tokens-in-flight vs the engine's configured max — leading indicators,
   measurable in seconds.
4. **Reaction:** scale *out* immediately on signal breach (pods request
   now, arrive in minutes — hence min replicas must cover the gap);
   scale *in* slowly and conservatively (5–10 min stability window) —
   thrashing costs more than idle.
5. **Floor and ceiling:** min = burst survival (≥ 1, sized to peak of
   the *night*); max = budget guardrail (lesson 090's cost ceiling),
   alarm at the ceiling rather than silently failing SLOs.

## Scheduled + predictive scaling

LLM traffic is diurnal and event-driven (product launches, batch jobs).
Pre-scale for the known: cron the workday ramp 30 minutes before
breakfast traffic; hold capacity for announced events. Prediction
(Holt-Winters on last weeks' curve) is nice; a calendar is 80% of the
value.

## Multi-tier escape hatch

When the queue is deep and scale-out won't arrive in time: degrade to a
smaller model tier (quantized variant, distilled model — Module 5's
distillation pays off here) with a response header saying so. A slightly
worse answer beats a timeout; the SLO applies to the *experience*, and
the budget judges you accordingly (lesson 040).

## Check yourself

1. Load test says 12 RPS per replica at SLO. Demand: 40 RPS peak. At
   0.75 target utilization, how many replicas steady-state — and why is
   the answer not ceil(40/12)?
2. Why is scale-in more dangerous than scale-out? Describe the incident
   pattern of an aggressive scale-in policy.
3. Your autoscaler triggers at GPU utilization 85%. What does Module 3
   lesson 120 predict about p95s before the trigger ever fires, and what
   signal replaces it?

Next: [060 — Cold starts and warm pools](060-cold-starts-and-warm-pools.md)
