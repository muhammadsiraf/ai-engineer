# Versioning

**Reading time:** ~6 min · Module 7

Every number in this module is only interpretable against its
*provenance*: which set, which judge, which model, which prompt, which
temperature. Versioning is the discipline that makes evaluation results
reproducible and every artifact in the stack diffable, rollable, and
ownable. It's unglamorous and it's the difference between an eval
program and a folder of screenshots.

## What has a version (the full inventory)

- **Prompts & templates** — the most-changed artifact, the least
  versioned in practice. Template version rides on every request
  (Module 6 lesson 110) and every log line.
- **Models** — base + fine-tune + quantization (Module 5 lesson 130's
  merge artifacts; Module 3's quant re-eval rule). Content hash, not
  "latest".
- **Eval sets** — versioned, with a changelog (lesson 020's case
  records carry `version`).
- **Judges** — the judge prompt IS code: version it; re-validate on
  change (lesson 050).
- **Retrieval configs** — k, reranker, chunker params, embedding model
  (Module 4 lesson 040's pin-and-re-embed).
- **Engines/containers** — Module 6 lesson 080's matrix.

Rule of thumb: if changing it changes behavior and you can't say what
changed, it's missing a version.

## Reproducibility contracts

Every stored eval result carries: `{set_version, judge_version,
model_version, template_version, temperature, seed?, date}`. That
tuple is what makes "regressed 2 points" a *finding* rather than a
guess — and what makes lesson 070's diff-table possible (same tuple on
both sides except the candidate).

Reproduction honesty: sampling models don't reproduce bit-exactly
unless you pin temperature/seed *and* the provider guarantees
stability (they rarely do — Module 1 lesson 150's nondeterminism). The
contract is therefore *statistical*: same versions ⇒ scores within
noise, and "noise" has the confidence bounds from lesson 060's math.

## The dependency graph (and its storms)

Artifacts depend on each other: template → model → judge → set. A
change anywhere re-invalidates downstream results (the judge changed ⇒
all historical scores shift by the judge's drift ⇒ re-run the baseline
or annotate the break). Version bumps propagate:

- **Patch** (typo fix): no re-eval needed, changelog line.
- **Minor** (wording, an added case): smoke suite re-run.
- **Major** (rubric change, model swap, set restructure): full
  re-baseline — new results only comparable *within* the new version.

The invisible killer is the *undeclared* major: editing the judge
prompt without bumping anything. Every historical comparison is now
quietly wrong. The CI check from lesson 070 covers this too — version
bumps are required by the diff, not by memory.

## Storage layout (the boring part that works)

```
evals/
  sets/billing_v3.jsonl          + CHANGELOG.md
  judges/groundedness_v2.md
  results/
    2026-10-12_pr482/
      manifest.json              ← the full tuple
      summary.csv, cases/*.json
```

Results directories are immutable; baselines are pointers (`baseline →
2026-10-04_pr455/`). Any engineer can reconstruct any number ever
reported. That's the whole bar.

## Check yourself

1. The judge prompt was edited Monday; Wednesday's report shows −3
   everywhere. What happened, which artifact prevents it, and what's
   the recovery?
2. Why is "same versions ⇒ scores within noise" the honest contract,
   rather than bit-exact reproduction?
3. List the five version fields in a result manifest and name the
   artifact that most teams forget (hint: it judges you back).

Next: [130 — Shipping end-to-end](130-shipping-end-to-end.md)
