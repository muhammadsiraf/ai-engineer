# Serving is a platform

**Reading time:** ~6 min · Module 6

Modules 3's arithmetic told you what one GPU can do. This module is what
stands between that GPU and your users: the platform. The frame shift:
"a model endpoint" is not a deployment — a deployment is a *system* with
load balancing, autoscaling, rollouts, observability, and an economics
model, and the model is one (stateful, expensive) component inside it.

## The stack, top to bottom

```
clients → gateway (auth, rate limit, routing) → serving fleet (replicas)
                                                      ↓
                              model server (vLLM etc.) → GPU
                                                      ↓
                              observability: metrics, logs, traces
```

- **Gateway:** authentication, quotas, request routing (lesson 070),
  canary traffic splits (lesson 110). Stateless, horizontally scalable,
  cheap — put everything here that doesn't need a GPU.
- **Fleet:** N identical replicas, each a model server with its own KV
  cache and scheduler (Module 3). Load balancer spreads requests;
  autoscaler (lesson 050) adjusts N.
- **Model server:** the engine — continuous batching, paged KV, prefix
  cache (all of Module 3). Your config choices here are the biggest
  single lever on cost/latency.
- **Observability:** the nervous system (lesson 120). Not optional
  plumbing: without per-stage metrics you are operating blind.

## What makes GPU serving its own discipline

- **Expensive, scarce, stateful capacity.** A GPU replica costs 10–100x a
  CPU one and holds session state (KV cache) — naive load balancing
  destroys prefix-cache hit rates.
- **Cold starts are brutal** (lesson 060): 30s–5min model load vs
  milliseconds for a CPU service. The autoscaler must think in minutes.
- **Unit economics are the product** (lesson 090): every percentage point
  of GPU utilization or batch efficiency is real money; conversely every
  queueing second is user trust.

## The platform team's actual job

Not "run the model" — that's one config file. The job: make the *seven
reliability verbs* work for any model — deploy, scale, roll out, roll
back, observe, load-test, cost-allocate. Every lesson in this module is
one of those verbs. If each new model requires reinventing them, you
have a demo, not a platform.

## Check yourself

1. Your team's serving "platform" is a single script that starts vLLM.
   Name the first three verbs it's missing and the incident each will
   cause.
2. Why is round-robin load balancing actively harmful for LLM workloads
   with shared system prompts? (One word from Module 3 lesson 070.)
3. Where does auth/quota enforcement belong, and why not in the model
   server?

Next: [020 — Picking a serving framework](020-picking-a-serving-framework.md)
