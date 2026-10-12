# Why outputs are non-deterministic by default

**Reading time:** ~6 min · Module 1

You send the identical prompt twice and get different completions. For a
database-brained engineer this feels like corruption. It isn't — and knowing
*exactly* where the nondeterminism comes from (and where it *doesn't*) is what
separates reproducible LLM systems from flaky ones.

## Source 1: sampling — intentional randomness

Lesson 140's pipeline ends in `np.random.choice(probs)`. At T=0.7, the second-best
token wins some fraction of the time. **This is by design**: the distribution's
tail carries the diversity that makes brainstorming work and paraphrase
possible. At T=0 (greedy), this source vanishes entirely.

## Source 2: floating-point non-associativity — the sneaky one

Even at T=0, providers (and your own GPU runs) can return different tokens for
identical requests. The cause is that floating-point addition is not
associative:

```
(a + b) + c  ≠  a + (b + c)   (in floats, often by tiny amounts)
```

GPU matmuls process many elements in nondeterministic *order* — parallel
reductions, atomics, kernel selection. Batch composition changes (a different
user's request batched with yours!), and the tiny rounding differences shift a
logit by 1e-6. Normally irrelevant — until two tokens were separated by 1e-7,
and the argmax flips. Rare, real, and effectively unfixable at the provider;
it's the price of fast hardware.

So even "deterministic" means "usually identical," not "bitwise reproducible."

## Source 3: provider-side mutables

The model behind a stable-looking name is a moving target: silent version
bumps, quantization changes on their serving stack, system-prompt adjustments,
safety-layer updates. Your request is a function of *their* infrastructure,
which you don't control and often aren't told about. This is the strongest
argument for snapshotting/pinning model versions in anything long-lived — and
for eval regression suites (Module 7) that catch silent drift before users do.

## What reproducibility you can actually buy

| Want | How | Residual risk |
|---|---|---|
| Same output for same input, today | T=0, top_p=1, fixed seed (if supported) | FP reordering, batching |
| Cross-run stability for tests | Mock/cache responses; record-replay | none (that's the point) |
| Stable *behavior* over months | Pin model version | provider may deprecate |
| Audit trail of what was produced | Log request+response+params+version | storage discipline |

Note the pattern: **you cannot force determinism; you can engineer around its
absence.** Systems that need reproducibility (evals, golden sets, snapshots)
achieve it by *recording* and *replaying*, not by re-rolling the dice.

## Design implications, concretely

1. **Test behavior, not exact text.** Assert on parsed structure, classifier
   labels, or judge scores — not `assert output == "Paris is..."`. Exact-match
   tests at T>0 are a fixture of doomed LLM test suites.
2. **Idempotency keys and dedup** belong in your client (Module 2's retry
   design), not in hopes that the provider dedups.
3. **Evaluation needs k samples.** Pass@1 at T=0.8 underestimates capability;
   mean-over-k with confidence bounds (Module 7) is the honest number.
4. **Cache aggressively** (Module 2's caching lesson): identical request +
   identical params → serve from cache. Cheaper *and* deterministic as a bonus.

## Check yourself

1. Rank the three nondeterminism sources by how often they'll bite an app at
   T=0.8 vs T=0, and justify.
2. Your integration suite asserts exact output equality and fails 1 in 30 runs.
   Redesign it: what do you assert, and what do you mock?
3. A procurement contract requires "identical outputs for identical inputs"
   from an LLM vendor. Draft the one-paragraph technical response.

Next: [170 — What 'context' actually contains](170-what-context-actually-contains.md)
