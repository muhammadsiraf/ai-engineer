# Budgets and step limits

**Reading time:** ~6 min · Module 8

An unsupervised agent is unbounded by default: it will happily take
forty steps, repeat one failing call ten times, and spend more than
the task is worth. Budgets are the harness's promise that a run
terminates with bounded cost — and they are enforced in *code*, never
requested in *prompt* ("please stay under 10 steps" is a suggestion;
a loop counter is a fact).

## The five budgets

1. **Steps** — max model turns (or tool calls). The coarse spine;
   every other budget hangs off the same loop.
2. **Tokens** — cumulative input+output across all turns. Catches the
   slow bleed of a bloating transcript even when step counts look
   fine.
3. **Wall-clock** — user-facing agents need latency bounds; a correct
   answer at four minutes is a wrong answer.
4. **Cost** — dollars per run, computed from the token ledger
   (Module 7 lesson 090's telemetry, now as a guard).
5. **Errors** — consecutive tool failures; three in a row means the
   model is lost, and attempt five won't be different (lesson 040's
   thrash shape, caught early).

Budget exhaustion is *not* an error to hide — it's a normal exit with
a normal record.

## Graceful degradation

The budget tripping should produce the most useful thing still
possible: partial results, the best-so-far answer, and an honest
"couldn't finish: step budget exhausted after the search succeeded
but before pricing was fetched." That message is a contract with
downstream code (do they retry? escalate to a human?) and with eval
(lesson 120 scores it as the incomplete run it is). Silence or a
raw exception is the failure mode that makes on-call hate agents.

## The circuit breaker

Repeat detection is the cheap, decisive guard: canonicalize each call
to a signature — `(tool_name, stable_json(args))` — and stop when the
*same* signature recurs. Identical call, identical inputs, calling
again is not planning; it's a loop. The challenge implements the full
guard: step budget, error streak, and repeat detection with
precedence between them, so your harness has one verdict function
per turn: continue, or stop-with-reason.

Log which guard fired on which step (Module 7's tracing) —
"stopped: repeat_loop at step 14" in your dashboard is the whole
incident report half the time.

## Check yourself

1. Why is a prompt-level instruction not a budget? What does the
   code-level check add?
2. A run trips the token budget but not the step budget. What does
   that tell you about the transcript, and which lesson's fix
   applies?
3. Design the degraded output for a travel agent that held a flight
   but hit its budget before booking. What does the user see, what
   does the record show?

Next: [070 — State and memory](070-state-and-memory.md)
