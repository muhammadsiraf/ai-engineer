# Shipping end-to-end

**Reading time:** ~7 min · Module 7

This course built eight modules of machinery. The last mile is the
*operating loop* that holds them together: change → evaluate → gate →
canary → monitor → harvest → change. This capstone lesson assembles the
whole machine and hands you the checklist for making evaluation a
property of the organization, not a hero project.

## The loop, assembled from everything you've built

```
                    ┌─────────────────────────────────┐
                    │  harvest: incidents, corrections │◀── prod
                    │  (M5 L140, M7 L020, M7 L080)     │
                    ▼                                  │
  golden set vN ──▶ regression suite (M7 L070) ──▶ CI gate
                                                    │ pass
                                                    ▼
                    canary + guardrails (M6 L110) ──▶ prod
                                                    │
                     monitor: quality/cost/drift    │
                     (M7 L080/090/110, M6 L120)     │
                    └────────────────────────────────┘
```

The artifact handoffs are the system: prod failures become cases
(020); cases gate PRs (070); PRs deploy behind guardrails (M6 110);
prod scores and PSI feed the next iteration (080/110). Every arrow is
automatable; teams that automate all of them ship weekly with falling
incident rates.

## The launch gate (the whole course on one checklist)

Before a change ships, it has passed:

1. **Golden suite:** per-category thresholds met; diff vs baseline
   reviewed with outputs attached (070, 120's manifest)
2. **Quality guardrails pre-registered:** the numbers that trigger
   rollback, written *before* the canary starts (M6 110)
3. **Cost delta computed:** unit economics move approved (090, M6 090)
4. **Version manifest complete:** set/judge/model/template tuple
   recorded (120)
5. **Monitoring armed:** dashboards, alerts, runbook links (080, M6
   120)

If any line is N/A, the decision to skip it is *written down with a
name next to it* — the checklist's job is forcing explicit risk
acceptance, not perfection.

## Organizing the function

- **Who owns eval:** a platform-ish owner for the machinery (suite,
  judges, dashboards) + per-feature owners for their sets. Eval
  ownership scattered across every dev = no suite; centralized with no
  feature owners = a museum.
- **The weekly eval review:** deltas, drift, incidents-harvested,
  suite health (flaky rate, runtime). Thirty minutes; the meeting
  where quality gets managed.
- **Documentation that decays slowly:** the decision docs (Module 5
  lesson 010's memo pattern) linked from manifests — future-you can
  reconstruct *why* the baseline is what it is.

## The maturity ladder (where is your team?)

1. **Vibes:** demo-driven shipping, anecdotes as evidence.
2. **Ad-hoc evals:** sets exist per feature, run manually before
   launches.
3. **Gated:** CI regression suite, canary guardrails, manifests.
4. **Monitored:** prod quality sampling, drift PSI, cost telemetry.
5. **Learning:** harvest → suite → prod loop is automated; evals
   compound instead of eroding.

Most "AI teams" are at 1–2. Everything in this course is the
difference between 2 and 5, and the compounding starts the day the
first production failure becomes case #1 in a set that gates a PR.

## Check yourself

1. Map your (or a hypothetical) product's loop: name the tool/artifact
   at each of the six arrows, and the one missing link.
2. A change passes the suite but trips a canary guardrail. Walk what
   happens next, artifact by artifact.
3. Where is your team on the ladder, and what is the *single* next
   investment with the best ratio of effort to moved-needle?

**Module 7 complete.** Next: [Module 8 — Agents & tool use](../../08-agents-tool-use/lessons/010-what-is-an-agent.md)
