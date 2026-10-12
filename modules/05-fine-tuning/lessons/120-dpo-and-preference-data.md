# DPO and preference data

**Reading time:** ~7 min · Module 5

SFT teaches *what to output*. Preference optimization teaches *which of
two outputs is better* — the axis where "both are fluent, one is actually
good" lives. DPO (Direct Preference Optimization, Rafailov et al. 2023)
is the method that made this trainable without the RLHF apparatus, and
it's the standard next step after SFT.

## The data shape

Triples: `(prompt, chosen_response, rejected_response)`.

Sources, best first: **production logs** (user picks/edits/abandons are
preference signal at scale), **human review pairs** (annotators choose
between two candidate responses), **model-generated pairs** (sample two
responses from the SFT model, label the better — cheap and self-correcting,
since the pair comes from the same distribution the deployment will see).

Quality bar mirrors lesson 060's, with one addition: the *pair* must
differ in quality for a *recognizable reason* (correctness, groundedness,
instruction adherence) — not style noise. If annotators agree ~100% of
the time, your pairs are too easy; ~60–80% agreement usually means real
signal with hard pairs.

## The loss, in one look

DPO trains the model directly against a frozen reference (your SFT
checkpoint) with a classification loss over the preference:

```
L = −log σ( β · [ Δθ(chosen) − Δθ(rejected) ] )

Δθ(y) = log π_θ(y|x) − log π_ref(y|x)     (log-prob gain vs reference)
β    ~ 0.1      (how sharply to push apart)
```

Reading it: *raise the reference-relative likelihood of chosen responses,
lower it for rejected, gently* (the sigmoid saturates; β sets the
pressure). No reward model, no RL loop — it's a logistic regression on
log-probability differences. The frozen reference is what anchors the
model and prevents the drift-to-ruin failure mode of naive RLHF — DPO's
whole trick.

## The SFT-first pipeline and why

Standard recipe: **SFT → DPO.** SFT installs the target behavior/format;
DPO sharpens quality *within* that behavior. DPO on a raw base model
wastes the preference signal teaching basics it could have learned from
plain SFT — and lesson 060's data rules still apply: thousands of pairs
for a meaningful effect, pairs from the deployment distribution.

Failure signatures to know: **chosen log-prob collapsing** (the model
punishes rejected so hard it distorts language — lower β or more data)
and **both deltas shrinking to zero** (model and reference diverged too
far — too many steps; the fix is fewer epochs, DPO converges quickly).

## Where it sits with everything else

DPO optimizes *behavior preferences* (tone, format, correctness-flavored
judgment calls). It does not add knowledge (Module 4's line again), and
it inherits the whole evaluation discipline: the forgetting slice, the
golden set, the same decision doc. Its eval twist: pairwise win-rate vs
the SFT model, judged per lesson 120 of Module 4's rubric rules — with
position-bias swapping (the Module 7 challenge implements it).

## Check yourself

1. Why is the frozen reference model essential — what failure does its
   presence prevent?
2. Your DPO run made responses *worse* on the golden set while win-rate
   vs rejected pairs looked fine in training. Name the two most likely
   data-level causes.
3. Order SFT and DPO for a support-bot project and justify in two
   sentences, referencing what each stage's data teaches.

Next: [130 — Merging vs serving adapters](130-merging-vs-serving-adapters.md)
