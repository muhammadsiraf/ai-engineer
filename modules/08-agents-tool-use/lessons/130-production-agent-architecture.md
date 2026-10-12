# Production agent architecture

**Reading time:** ~7 min · Module 8

The demo agent is a loop in a notebook. The production agent is a
service with a stack around the loop: gateway, harness, tool layer,
observability, and eval — each holding one of the guarantees you've
built across this course. This capstone assembles the pieces and
names the run record that ties them together.

## The stack

```
 request ──▶ gateway        auth, rate limits, request ids (M6 050)
                │
                ▼
            harness         the loop: budgets, guards, retries,
                │           state serialization (030/060/070)
                ▼
            tool layer      schemas, validation, permissions,
                │           idempotency keys, timeouts (020/050/110)
                ▼
            model calls     routing, fallbacks, cost telemetry
                │           (M2/M3/M6/M7)
                ▼
            observability   the run record + trace per step (M7 100)
```

Each layer has one job and one reason the layer below can't be
trusted with it. The gateway doesn't parse tool calls; the harness
doesn't hold credentials; tools don't decide policy.

## The run record (the atom of the system)

Every run writes one record: `{run_id, goal, agent version, tool
manifest version, model versions, budget config, steps[] (each:
thought, call, result, latency, tokens), guards_fired, outcome,
done, verified, dollars}`. It's simultaneously the debug artifact
(replay from any step — lesson 070's tier 2), the eval input (lesson
120 scores records, not vibes), and the audit log (lesson 110's
post-hoc review). If you build one thing from this module properly,
build the record; the loop in the middle is commodity code by
comparison.

## Operations the demos skip

- **Idempotency keys** on every write tool; timeouts and bounded
  retries per tool call; duplicate execution is the default failure
  of distributed systems, and agents are distributed systems.
- **Kill switches:** tool-level and agent-level, toggled without a
  deploy. The first production incident converts this from nice-to-
  have to law.
- **Sandboxing** for code-execution and file tools: containers with
  no network, no secrets, caps on CPU/time (M6's engine discipline,
  now load-bearing for security).
- **Human-in-the-loop tiers:** none for read-only; sampling review
  for low-risk writes; approval gates for irreversible actions
  (lesson 110), with the gate queue staffed and measured.
- **Capacity:** agent turns multiply model calls 5–20×; load-test the
  loop against Module 3/6 numbers or the agent becomes your p99.

## The course, closed

Eight modules, one arc: *what the model is* (M1), *how to steer it*
(M2), *what it costs to run* (M3), *how to ground it* (M4), *how to
specialize it* (M5), *how to serve it* (M6), *how to know it works*
(M7), *how to let it act* (M8). The through-line is the one this
module needed most: agents are engineering — loops, budgets, records,
gates — wrapped around a probabilistic core. The teams that ship them
reliably are the teams that treat the wrapper as the product. Build
the record, gate the changes, bound the blast radius — and the
remaining risk is the good kind: the kind you can measure.

**Module 8 complete — and with it, the course.**
