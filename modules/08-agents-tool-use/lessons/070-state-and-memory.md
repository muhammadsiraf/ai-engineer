# State and memory

**Reading time:** ~7 min · Module 8

The transcript is the agent's working memory — and it is finite,
rented by the token, and rebuilt from scratch every run. Everything
else the agent "knows" lives in state you design: scratchpads,
checkpoints, and long-term stores. Getting the tiers right is the
difference between an agent that scales and one that quietly
drowns in its own context.

## The three tiers

1. **Within-run scratchpad:** the transcript itself — thoughts,
   actions, observations. Fast, always in view, expensive per token
   (Module 3's KV cache makes the *prefix* cheap; the growth still
   costs attention quality as well as money).
2. **Run persistence:** serialized state that lets a run pause,
   resume, or be replayed after a crash — goal, transcript so far,
   budget counters, tool-call ids. This is also your debugging
   substrate: Module 7's tracing captures the same record.
3. **Cross-run memory:** anything that should outlive a run —
   user preferences, entities learned, task results. Store it as
   *data* (a KV/relational store or Module 4's vector index), not as
   an ever-growing transcript, and pull it in deliberately per run.

## Context management: the three valves

When the scratchpad grows past its budget:

- **Truncate** — drop or clip old observations. Cheap, lossy;
   fine when recent steps dominate.
- **Summarize** — fold completed subtasks into a short note. Costs a
   call, keeps narrative coherence; the summary is itself a
   lossy artifact (test it — Module 7's judge shapes apply).
- **Spill to disk** — write large observations (page dumps, big
   JSON) to a file and leave a pointer + excerpt in the transcript;
   the agent re-reads on demand. The agent's version of swap space.

Pick per-observation, not per-run: a 40KB API response gets spilled;
a one-line error stays inline (it's the recovery signal from lesson
050).

## Write it down

Models are better at *using* notes than *remembering* across turns
under context pressure. The pattern that works: after each milestone,
the agent writes a short status note (goal, done, next) that rides at
the top of the scratchpad. It's a cache of intent — it survives
summarization and makes every restart cheap. Serialize it with the
run record (tier 2) and replay/debug becomes deterministic:
same notes, same tools, same order.

## Check yourself

1. A run fails at step 30 of 40. What exactly must tier-2 state
   contain for you to resume it *without re-paying* for steps 1–29?
2. Your agent's accuracy *drops* as tasks get longer. Which tier is
   misdesigned, and which of the three valves is the first fix?
3. What belongs in cross-run memory vs. the scratchpad? Give one
   example of each from a support agent.

Next: [080 — Multi-agent: the supervisor pattern](080-multi-agent-supervisor.md)
