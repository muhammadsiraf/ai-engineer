# The ReAct loop

**Reading time:** ~7 min · Module 8

ReAct (Reason + Act) is the canonical agent loop: the model
interleaves *thought* (what do I need?), *action* (call a tool), and
*observation* (the result), until a thought concludes "done" and it
answers. It's worth studying precisely because it's minimal — every
fancier pattern in this module is this loop with extras.

## The loop, in fifteen lines

```python
messages = [system(TOOLS_RULES), user(goal)]
for step in range(max_steps):                  # lesson 060's budget
    out = llm(messages, tools=TOOL_SCHEMAS)
    if out.tool_calls is None:                 # model chose to answer
        return out.text                        # success or premature?
    for call in out.tool_calls:
        result = execute(validated(call))      # lesson 020's harness
        messages.append(tool_result(call.id, result))
return raise_or_degrade()                      # budget exhausted
```

Three exits exist: the model answers, the budget cuts it off, or a
guard trips (lesson 030's challenge implements the guard). Every
production incident story about agents is a story about one of those
three exits being wrong.

## What the loop needs from you

- **Stop conditions that aren't just step counts:** final answer,
  budget, repeated identical calls (thrash — lesson 040), error
  streaks. The naive `for` loop with only `max_steps` is how you get
  a $40 run.
- **Observation hygiene:** tool results go into context and stay
  there. Truncate, summarize, or spill-to-file long results
  (lesson 070) — a 50k-token page dump on step 3 poisons every later
  turn.
- **Turn discipline:** append *every* result before the next model
  call, even failures. A transcript where errors vanish teaches the
  model to retry blindly.

## Why interleaving matters

A plan-then-execute model commits to steps before seeing evidence;
ReAct lets each observation reshape the next action — that's what
makes it competent at tasks where the path depends on what it finds
(lesson 010's "when the agent is worth it"). The price is drift:
nothing forces coherence across turns, which is why budgets and the
failure taxonomy exist before the fancy patterns do.

The patterns of lesson 090 (plan-and-execute, reflexion) are
modifications of exactly this loop: what gets appended, and when the
model is allowed to reconsider.

## Check yourself

1. Trace the fifteen-line loop on a two-tool task ("find the cheapest
   flight, then hold it"): what does the transcript look like after
   step 2?
2. A tool returns a 200KB page. What are your two options before it
   enters the transcript, and when do you pick each?
3. The loop's `for` exit fires. Name the two things the run record
   must capture for Module 7's evaluation to grade this run fairly.

Next: [040 — Why agents fail](040-why-agents-fail.md)
