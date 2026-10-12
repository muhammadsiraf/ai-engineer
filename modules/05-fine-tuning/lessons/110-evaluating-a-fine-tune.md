# Evaluating a fine-tune

**Reading time:** ~6 min · Module 5

The fine-tune's report card has three sections, and skipping any one is
how bad models ship: (1) did the task improve, (2) what did it cost
elsewhere, (3) what will it cost to run. Module 7 owns the general eval
machinery; this lesson is the fine-tuning-specific version of it.

## 1. Task eval: against the *right* baselines

The comparison set that decides everything:

- **Base model + your best prompt** (often with few-shot examples) —
  the incumbent you'd otherwise ship. Fine-tuning must beat *this*, not
  the base model with a lazy one-liner.
- **A bigger/stronger model + same prompt** — what "just use a better
  model" costs; the fine-tune has to beat its economics too (lesson 010's
  distillation math).
- **The previous fine-tune** (if iterating) — regression detection.

Score on the golden set with per-category breakdowns (Module 4 lesson
110's discipline verbatim): averages hide the exact failures fine-tuning
introduces.

## 2. Capability eval: the forgetting table

Lesson 100's general-capability slice, base vs fine-tune, one table.
Additionally probe: **format overfitting** — does the fine-tune handle
slightly different input shapes (longer inputs, unusual formatting,
multiple questions) or did it learn one rigid shape? Fifty adversarial
variations of golden-set inputs is an afternoon and catches the most
common fine-tune fragility.

## 3. Serving eval: the model you trained vs the model you deploy

The eval artifact and the deployed artifact must be byte-identical:
same merge decision (lesson 130), same quantization (Module 3 lessons
080/090 — quantizing a fine-tune re-runs its eval, no exceptions), same
template (lesson 070), same sampling defaults. The classic failure:
evaluated at BF16, deployed a 4-bit quantization nobody re-checked.

Plus the Module 3 arithmetic on the *new* model: does your distilled 7B
actually serve the concurrency the 70B did? (Often yes — that's the
point — but you measure it, lesson 120.)

## The decision doc

One page: task table (with baselines), forgetting table, serving config
+ cost per million tokens, and the verdict against the threshold you
wrote in lesson 010's memo. If the memo's threshold isn't met, the
default answer is *don't ship it* — the incumbent prompt/RAG stack keeps
working, and the fine-tune goes back for another data iteration (lesson
060), not another hyperparameter sweep.

## Check yourself

1. Your fine-tune beats the base model by 12 points. Why is that number
   nearly meaningless, and what number replaces it?
2. The fine-tune wins on task, drops 3 points on the general slice, and
   serves at 1/4 the cost of the incumbent frontier setup. Who decides,
   and what's written in the doc?
3. Why must quantized fine-tunes be re-evaluated, and which module's
   lesson told you quantization failures concentrate where?

Next: [120 — DPO and preference data](120-dpo-and-preference-data.md)
