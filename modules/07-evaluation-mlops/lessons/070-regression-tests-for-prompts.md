# Regression tests for prompts

**Reading time:** ~6 min · Module 7

A prompt is code: it has behavior, it has regressions, and it changes
for the same reasons code does — except your team edits it without
tests, review gates, or rollback discipline. The fix is to treat the
prompt (and everything it pulls in: retrieval configs, templates,
tool schemas) as a versioned artifact with a CI suite. The challenge
implements the gate.

## What a prompt regression suite looks like

The golden set (lesson 020) compiled into executable assertions:

```
for case in golden_set:
    out = run_pipeline(case.input)
    assert schema_valid(out)                       # shape 1: exact
    assert all(m in out.text for m in case.must_include)
    assert not any(m in out.text for m in case.must_not)
    scores = judge(case, out)                      # shape 3: rubric
    assert scores.groundedness >= case.min_groundedness
```

Run on every PR that touches: the prompt string, the template version,
the model version, retrieval parameters (k, reranker on/off), tool
schemas — *any* input to the behavior. Per-category thresholds, not
just aggregate (lesson 020's per-category reporting, now as a gate —
the challenge's job).

## The nondeterminism accommodation

You can't assert on exact strings from a sampling model. Three
practical patterns, in strictness order:

1. **Constrain then assert:** structured output + temperature 0 for
   testable surfaces (routing, extraction) — exact-match CI works.
2. **Property assertions:** must_include/must_not, schema, length
   bounds, citation presence — robust across samples.
3. **Judge gates with margins:** require score ≥ threshold with slack;
   for pairwise, require the new prompt wins-or-ties (with the
   challenge's confidence math deciding "tie").

Flaky tests destroy trust in the suite — when a case fails
intermittently, either make its assertion sample-robust (property, not
string) or mark it flaky and fix the *behavior*; never delete silently.

## Baselines and deltas

Every PR compares against `main`'s stored results (same set version,
same judge version): the report is a diff table — per category, per
case, with the offending outputs attached. "Score moved 0.3 on
billing-refund, 12 cases regressed, here are three" is a reviewable
artifact; "+0.1 average" is not. Store results with their full
provenance (set version, judge version, model version, temperature) —
lesson 120's versioning discipline, applied.

## The maintenance economy

The suite runs on every PR; cases are cheap to add, so the set grows —
and slow suites get skipped, and skipped suites rot. Controls: tier the
suite (fast ~50-case smoke on every PR; full set nightly + on
release), cache judge verdicts by (case, output, rubric version), and
prune quarterly (lesson 020's garden). A suite that takes 40 minutes
on every PR will be bypassed by Friday.

## Check yourself

1. A teammate edits the system prompt in the WYSIWYG tool, ships
   directly. Name the two missing gates and the incident shape each
   invites.
2. Your CI gate is flaky on 5% of runs. Walk the three response
   patterns and why "re-run until green" is the worst one.
3. Design the tiering: what's in the 2-minute PR suite vs the nightly
   full run, and what decides the boundary?

Next: [080 — Monitoring](080-monitoring.md)
