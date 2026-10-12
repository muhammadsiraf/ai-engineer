# The minimum-viable LLM app architecture

**Reading time:** ~6 min · Module 2

Everything in this module assembles into one diagram. This is the reference
architecture for an LLM feature that survives production — not a platform,
just the minimum that doesn't page you at night. Module 8 (the lab in
particular) has you build every box.

## The diagram

```
                        ┌────────────────────────────────────────────┐
 user ──► your API      │            your service                    │
        ──► ┌────────────▼─────────────┐                              │
            │ 1. request validation    │  schema, size caps, authz    │
            ├──────────────────────────┤                              │
            │ 2. context assembler     │  template + retrieved data   │
            │    (stable→volatile!)    │  [stable prefix][volatile]   │
            ├──────────────────────────┤                              │
            │ 3. guard checks          │  token budget, PII policy,   │
            │                          │  injection fence             │
            ├──────────────────────────┤                              │
            │ 4. LLM gateway           │  the ONLY place that calls   │
            │   ┌────────────────┐     │  out to a model:             │
            │   │ cache lookup   │     │   - response cache (120)     │
            │   │ limiter (130)  │     │   - rate limiter + retry     │
            │   │ client (010)   │     │   - logging: req/resp/usage  │
            │   └────────────────┘     │   - provider fallback ladder │
            ├──────────────────────────┤                              │
            │ 5. output validation     │  finish_reason, parse,       │
            │                          │  schema (060), redaction     │
            ├──────────────────────────┤                              │
            │ 6. response + telemetry  │  latency split (110), cost   │
            └──────────────────────────┘                              │
                        │                                             │
                golden-set logging ──► eval store ──► dashboards (Module 7)
```

## Why each box exists (traceability to lessons)

1. **Request validation** — you never send unvalidated user bytes to a
   model (lesson 020, 160). Size caps prevent the 200k-token paste.
2. **Context assembler** — the single function that renders the prompt from
   versioned templates: `[stable prefix][volatile suffix]` (lesson 100/120).
   If it's not one function, caching and evals are impossible.
3. **Guard checks** — pre-flight token budget (090), PII policy, injection
   fencing for any untrusted content (160).
4. **The gateway** — one module that owns: caching, limiting, retry/backoff
   (130), usage logging (090), provider selection/fallback (140). The
   challenge `llm-gateway` builds this exactly.
5. **Output validation** — `finish_reason` check, structured parse + one
   repair retry (060), output sanitization (160).
6. **Telemetry** — TTFT/TPS split (110), cost per request (090), sampled
   request/response capture for the eval store.

## The three properties to defend

**One door to the models.** Every LLM call goes through the gateway. The
day someone imports the SDK directly in a controller, you lose cost
accounting, rate limiting, and the fallback ladder in one commit. Review
for this like you review for SQL-injection.

**Templates are code.** Prompts live in versioned template files with
owners and tests — not in string literals scattered through business
logic, and definitely not in the database where product managers edit
them live. (If PMs must tweak, the template has a *parameter* they can set,
validated.)

**Everything is replayable.** Log enough to reconstruct any request
(messages, params, model version, template version, retrieved-doc ids).
This converts every future incident from "can't reproduce" to "replay the
last 50 failures" — and it's the raw material of Modules 4–7's evals.

## What NOT to build yet

The minimum-viable version skips: vector DBs (until Module 4 says
otherwise), multi-agent orchestration (Module 8), fine-tuning pipelines
(Module 5), and Kubernetes (Module 6). One model, one task, one gateway,
one golden set. Boring is the feature. Teams that build the platform
before the first eval of a single prompt learn the platform instead of the
problem.

## The growth path

```
MVP (this lesson) → + retrieval (Module 4) → + eval gates in CI (Module 7)
                  → + self-hosted tier behind the router (Modules 3, 6)
                  → + tools/agents (Module 8)
```

Each stage adds one box to the diagram without changing the invariants:
one door, templates as code, replayable. Those three invariants are the
actual architecture; the boxes are details.

## Check yourself

1. A teammate needs "a quick LLM call" in a new endpoint and imports the
   SDK directly. What are the three concrete things that break?
2. Why does the context assembler render `[stable][volatile]` — name the
   two subsystems that depend on that split.
3. Your incident: outputs went subtly wrong at 14:02. Walk the replay path:
   what must have been logged at 14:01 to reconstruct a failing request?

**Module 2 complete.** Next: [Module 3 — LLM Inference & Optimization](../../03-inference-fundamentals/lessons/010-inference-is-a-scheduler-problem.md)
