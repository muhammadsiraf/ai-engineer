# Why models hallucinate

**Reading time:** ~7 min · Module 1

Hallucination — confident, fluent, false output — is the failure mode that
dominates LLM risk lists. It is not a bug someone forgot to fix; it's a
predictable property of the training objective. Understanding the mechanism
tells you which defenses actually work and which are superstition.

## The mechanism: plausible beats true

The training objective (lesson 070) is next-token prediction. The loss rewards
**high-probability continuations**, not **true** ones. Training text contains
both, and the model has no internal truth-meter — only a probability meter.
When these diverge, probability wins:

- More sentences are *shaped like* correct answers than are actually correct.
- The model has seen a thousand confident explanations; fluency is just the
  local style of the genre "explanation."
- For rare facts, the honest state of the model is genuine uncertainty spread
  across possibilities — but the output format (pick tokens, sound coherent)
  launders that uncertainty into confident prose.

Corollary worth internalizing: **hallucination is strongest exactly where you
want the model most** — specific facts (names, citations, numbers, APIs)
carrying low training frequency. The model fills the gap with the most
statistically plausible completion of the *shape* of an answer. Fake citations
with real-looking DOIs; plausible-but-nonexistent function names; invented
policy numbers. The genre is learned; the referent isn't there.

## Why it can't just "say I don't know"

On the training distribution, "I don't know" is rare and low-reward relative to
attempting an answer (and RLHF tuning reduces but doesn't eliminate this).
There's also no clean internal signal to threshold on: the model's uncertainty
is distributed across its probability landscape, not a Boolean flag it can
report. Calibration (does p=0.9 actually mean 90% correct?) is imperfect and
varies wildly by domain. This is why "just ask the model to be honest" has such
a weak effect — you're asking a probability machine to change its objective.

## What actually reduces hallucination, ranked by mechanism

**1. Change the input so the answer is in context (RAG).** Lesson 100's
mechanism: attending to real retrieved text *mechanically injects* those tokens'
representations into the computation. Grounding moves the answer from
"recalled-with-noise" to "copied-with-comprehension." Module 4 is this
implemented properly — with reranking and citations so you can *verify* the
grounding.

**2. Constrain the output space (structured output, tools).** Schema-enforced
decoding makes inventing field values harder but still possible — pair it with
validation. For facts, give the model a *retrieval or search tool* so
"generate" becomes "look up" (Module 8). Tools convert hallucination-prone
recall tasks into verification-friendly lookup tasks.

**3. Make the model's job prediction-shaped, not recall-shaped.** Summarize
*provided* text: near-zero hallucination surface, because everything needed is
in context. Extract structured fields from *provided* text: same. Open-domain
"What year did X happen?": maximal surface. Task design is hallucination
policy.

**4. Verify after generation.** Self-consistency (sample k times, keep
majority), judge models (Module 7), citation-checking against sources. These
catch hallucinations post hoc; they're your safety net, not your fix.

**5. Fine-tune for honesty / abstention.** Training on calibrated refusal
("answer when confident, flag uncertainty otherwise") measurably improves
abstention — a behavior change, which is exactly what fine-tuning is for
(Module 5). It cannot make the model *know* more.

**Not on the list:** lower temperature (variance ↓, same errors), "be accurate"
in the system prompt (weak, worth doing anyway), bigger model (fewer errors per
token, same mechanism, higher-stakes fluency).

## The engineering posture

Treat every generated fact as **untrusted input from a component you operate** —
the same way you treat user input, or a third-party API's response. The
architecture that survives: generate → validate → ground → cite → log. Modules
4, 7, and 8 are that pipeline, built.

## Check yourself

1. A model invents a plausible API method name. Explain via the training
   objective why the *shape* was right but the referent wrong.
2. Why does RAG reduce hallucination *mechanically* rather than just
   "reminding" the model? Reference the attention mechanism.
3. Rank these tasks by hallucination risk and say why: (a) summarize this
   ticket, (b) what's our refund policy?, (c) extract invoice totals from this
   PDF.

Next: [160 — Why outputs are non-deterministic by default](160-why-outputs-are-non-deterministic-by-default.md)
