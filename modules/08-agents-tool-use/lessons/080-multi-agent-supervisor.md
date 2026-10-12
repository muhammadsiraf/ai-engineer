# Multi-agent: the supervisor pattern

**Reading time:** ~7 min · Module 8

One agent with thirty tools degrades — choices blur, descriptions
drown each other, context fills with mixed concerns. The supervisor
pattern splits the problem: a coordinator agent owns the *goal* and
routes subtasks to narrow workers, each with a clean context, a small
tool set, and one job. It's the microservice move, with the same
trade: isolation bought with coordination cost.

## The shape

```
                 ┌────────────┐
   goal ────────▶│ supervisor │──── final answer
                 └─────┬──────┘
        ┌──────────┬───┴───────┬──────────┐
        ▼          ▼           ▼          ▼
    billing     shipping    research    ...workers
    agent       agent       agent
   (3 tools)   (2 tools)   (web tools)
```

The supervisor loop is lesson 030's ReAct loop where the "tools" are
*workers*: it decides which worker gets which subtask, reads the
worker's structured result, and either routes again or answers.
Workers are ordinary agents (or plain workflows — lesson 010's dial
applies per worker: not everything needs autonomy).

## Why it works

- **Context isolation:** each worker starts fresh; the billing
  worker never sees the 30KB of research output. Attention stays on
  one concern (lesson 070's pressure problem, solved structurally).
- **Least privilege:** workers get only their own tools and
  permissions — the research worker *cannot* issue refunds
  (lesson 110's blast-radius rule).
- **Independent evolution and eval:** a worker is a unit — versioned,
  tested, gated on its own suite (Module 7's discipline, now
  composable).

## What it costs

- **Tokens:** every handoff re-states context; realistic overhead is
  2–4× a single well-run agent. Budget per *task*, not per agent
  (lesson 060).
- **The telephone game:** free-text handoffs degrade. Worker
  results come back as *structured records* — status, findings,
  artifacts, errors (Module 2's structured output as the inter-agent
  contract).
- **Coordination bugs are new bugs:** duplicated work, workers
  blocking on each other, the supervisor re-delegating a task it
  already had answered. The run record (lesson 130) must log
  supervisor decisions per step or this is undebuggable.

Go multi-agent when tool sets or permissions genuinely conflict, or
when contexts genuinely pollute each other — not for the architecture
diagram.

## Check yourself

1. Your single agent confuses refund policy with shipping policy.
   Which property of the supervisor pattern addresses this, and what
   makes the split real rather than cosmetic?
2. Design the structured result record for the billing worker: name
   four fields and say what the supervisor does with each.
3. A supervisor delegates the same research task twice because the
   first worker's reply was buried in its context. Which lesson's
   mechanism prevents the *second* delegation?

Next: [090 — Planning patterns](090-planning-patterns.md)
