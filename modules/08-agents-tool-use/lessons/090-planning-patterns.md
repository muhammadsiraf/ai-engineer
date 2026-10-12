# Planning patterns

**Reading time:** ~7 min · Module 8

ReAct is the default because it's simple, but it meanders on long
tasks: each step is chosen myopically, and nothing holds a
multi-step agenda. Three patterns cover the space — ReAct,
plan-and-execute, and reflexion — and they're the same loop
(lesson 030) with different answers to one question: *when does the
model get to reconsider?*

## The three patterns

1. **ReAct (act → observe → act):** no explicit plan; the trajectory
   *is* the plan. Adapts instantly to surprises, cheap per step,
   and drifts — step 12 has forgotten step 3's purpose unless notes
   carry it (lesson 070). Right for short tasks and exploratory
   ones.
2. **Plan-and-execute (plan → execute → replan on deviation):** one
   upfront call produces an explicit task list; the executor runs it
   (often as plain ReAct per task); a deviation or failure triggers
   a *replan*, not improvisation. Front-loads cost, prevents
   thrash, and shines when the task decomposes cleanly ("gather
   prices → compare → draft → fact-check"). Fails interestingly
   when the plan was wrong about the world — hence replanning being
   part of the pattern, not an error path.
3. **Reflexion / self-critique (act → evaluate → retry with the
   critique in memory):** after an attempt, a critic pass asks "what
   went wrong, what would fix it" and the retry starts with that
   note attached. This is the only pattern that converts a *failed
   run* into progress within the run. It costs retries, and it
   rescues exactly the plausible-but-wrong answers that ReAct
   commits to (lesson 040's premature-stop shape).

## Choosing, and the hybrid that usually wins

Choose by task structure: unknown path, short horizon → ReAct;
decomposable, long horizon → plan-and-execute; high cost of silent
wrongness → reflexion on top. Production agents mostly run the
hybrid: a cheap plan sketch to set direction, ReAct execution inside
each planned step, replan or critique when a budget guard trips or a
tool contradicts the plan. The sketch costs one call; it repays by
preventing the dozen-step meander.

One discipline regardless of pattern: the plan is a *written
artifact* in the transcript — checklist, status per item — not a
vibe. Written plans can be inspected, resumed (lesson 070's tier 2),
and graded by eval (lesson 120 can check "did the executed sequence
match the declared plan?").

## Check yourself

1. A data-migration task has 9 known steps and one "inspect the
   source schema" step whose output reorders the rest. Where does
   plan-and-execute's replan trigger fire, and why is pure ReAct
   risky here?
2. Reflexion's critic accepts a wrong answer half the time. What
   does that do to its value, and which Module 7 tool measures
   exactly this?
3. Write the plan sketch (three items) the hybrid would produce for
   "book the cheapest refundable flight Tuesday, hold the hotel
   until the flight confirms."

Next: [100 — Model Context Protocol](100-model-context-protocol.md)
