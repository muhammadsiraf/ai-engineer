# Why LLM eval is different

**Reading time:** ~7 min · Module 7

Classical ML eval: fixed test set, deterministic model, one accuracy
number. LLM eval breaks each of those assumptions — the model is
nondeterministic, outputs are open-ended, quality is multidimensional,
and the *system* being evaluated includes prompts, retrieval, and tools
that change weekly. This module builds the evaluation practice that the
previous six modules kept promising ("golden set first," "the judge,"
"regression gates").

## The five differences that shape everything

1. **No single metric.** An answer can be fluent and wrong, correct and
   unverifiable, faithful to bad sources. You evaluate *dimensions*
   (correctness, groundedness, style, safety) — and per-category, not
   just average (Module 4 lesson 110's per-task discipline).
2. **Reference-free by necessity.** For open-ended generation there is no
   "the" right answer to diff against — evaluation becomes *judging*
   (rubrics, comparisons), which has its own failure modes.
3. **Nondeterminism.** Same prompt, different outputs. Single samples
   lie; you need multiple samples or distributional checks (and Module
   1 lesson 150's temperature choices become eval-protocol decisions).
4. **The system drifts under you.** Prompts, retrieval corpora, models —
   any can change silently. Eval isn't a one-time gate; it's a *monitor*
   (lesson 080) with regression tests (lesson 070) and drift detection
   (lesson 110).
5. **Evaluation is expensive and approximate.** Every eval call costs
   tokens and latency; every judge is itself a model with biases. The
   meta-skill: knowing how much measurement you can afford for the
   decision at hand.

## The payoff frame

Everything earlier in the course leaned on eval: Module 3's "no eval, no
quantization," Module 4's golden-set-first RAG, Module 5's decision
memo, Module 6's canary guardrails. This module is the machinery those
promises assumed — and the reason teams that skip it ship regressions
they literally cannot see.

## The three questions any eval must answer

1. **Compared to what?** (baseline: previous version, competitor,
   simpler prompt)
2. **Measured how, on whom?** (metric + rubric, on which set, judged by
   whom/what — and how much that judge can be trusted)
3. **What decision does the number gate?** (ship/no-ship, promote
   checkpoint, alert on-call). An eval that gates no decision is
   decoration.

## Check yourself

1. Your model scores 92% on your benchmark. Name two questions that
   number cannot answer.
2. Why does nondeterminism break "re-run the test, compare to last
   time" — and what's the minimal protocol fix?
3. Pick one feature from Modules 2–6 and name the eval artifact it
   assumed.

Next: [020 — Building an eval set](020-building-an-eval-set.md)
