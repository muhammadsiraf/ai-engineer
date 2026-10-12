# Evaluating agents

**Reading time:** ~7 min · Module 8

Everything from Module 7 applies here with one upgrade: an agent run
isn't an output, it's a *trajectory* — a sequence of decisions you
can grade separately from the result. The naive number ("it got 70%
of tasks done") is necessary and insufficient; the craft is scoring
the path as well as the destination.

## The three scores

- **Completion** — did the agent *declare* done? (cheap, self-
  reported, systematically inflated: lesson 040's premature stop
  makes this a vanity metric on its own)
- **Success** — did the work actually meet the goal? Checked by a
  verifier: a test on the final state (refund exists in the ledger),
  a checker function, or a judge over the answer + trajectory. This
  is the headline number.
- **Cost** — steps, tokens, dollars, wall-clock per run — and per
  *successful* run, which is the number that decides viability
  (Module 7 lesson 090's unit economics; the challenge computes
  all of these).

The completion–success gap is itself a metric: an agent that claims
done on tasks it failed has a grounding problem (lesson 040, shape
4) no amount of prompt polish fixes.

## Grading trajectories

Success tells you *what* failed; trajectory grading tells you *why*.
Unit-level checks: given a context where exactly one tool is right,
did it call that tool with valid args? (pure capability tests, cheap
and CI-friendly). Judge-level review: an LLM judge scores the
trajectory for process quality — efficient path, no thrash, no
permission violations — using Module 7's judge discipline: versioned
rubric, position-bias debiasing, agreement against a labeled
residue.

And lesson 040's four failure shapes become the *categories* of
your regression report: per-shape rates tracked like Module 7's
per-category scores, gated with the same max-drop slack. "Misuse
rate tripled" is a reviewable, blockable finding; "success dipped"
is a shrug.

## The environment problem

You can't eval against production tools — evals must not email real
customers. So you simulate: mock tools with scripted, deterministic
responses (the challenge's registries are the seed of one), sandboxes
for code execution, staged data for side-effectful APIs. The mock is
an artifact with its own version in the manifest — a stale mock
silently invalidates every number, exactly like a stale judge prompt
(Module 7 lesson 120's invisible killer, now wearing a tool costume).

Keep a small residue suite against *real* backends behind flags for
the drift the mocks can't see (lesson 110's golden-replay logic,
applied to agents).

## Check yourself

1. Your completion rate is 95%, success 78%. Name the failure shape
   this gap points to and the two artifacts you'd inspect first.
2. Why must mock tools be versioned in the run manifest? What breaks
   when they aren't?
3. Design the trajectory-judge rubric in four lines, then say how
   you'd validate the judge before trusting it (Module 7 lesson 050's
   checklist).

Next: [130 — Production agent architecture](130-production-agent-architecture.md)
