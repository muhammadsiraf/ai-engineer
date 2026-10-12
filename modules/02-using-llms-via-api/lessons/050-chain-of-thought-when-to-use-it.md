# Chain-of-thought, when to use it

**Reading time:** ~6 min · Module 2

"Let's think step by step" became a meme because it works — sometimes
dramatically — and fails quietly in other cases. This lesson covers what
chain-of-thought (CoT) actually changes mechanically, where it pays, and the
cost/trust accounting most teams skip.

## The mechanism

An autoregressive model computes its answer using only the tokens available
in context (Module 1 lessons 100/130). Ask for an answer *immediately* and the
model must produce it in one forward pass — everything must happen in the
"thinking" of a single token position. Ask it to write reasoning steps first
and each step becomes *context* for the next token; the model can refer back
to its own intermediate results, effectively giving itself more compute and
working memory.

That's the whole trick: **CoT converts a single-step problem into a
multi-step one where intermediate results persist in context.** It's why the
gains concentrate on multi-step tasks (arithmetic, logic, constraint
tracking, multi-hop lookup) and evaporate on single-step ones (sentiment,
formatting, lookup).

## When CoT pays

| Task | CoT effect | Why |
|---|---|---|
| Multi-step arithmetic | large gains | intermediate partial results |
| Logic/constraint puzzles | large | elimination needs working memory |
| Multi-hop questions ("who founded the company that made X") | moderate–large | chains of recall build on each other |
| Classification with clear criteria | none | single decision, no intermediate state |
| Summarization/translation | none or negative | fluent generation, no steps needed |
| Pure knowledge lookup | none | answer exists or doesn't |

Rule of thumb: **if a smart intern would need scratch paper, CoT helps.**
If they'd just *know*, it doesn't.

## Flavors, from cheap to rich

1. **Trigger phrase:** append "think step by step" / "explain your reasoning
   before answering." Zero prompt-engineering cost, surprisingly effective
   on strong models.
2. **Demonstrated CoT (few-shot):** show one worked example with the
   reasoning style you want. Controls the *shape* of reasoning — valuable
   when steps feed downstream parsers.
3. **Structured decomposition:** you prescribe the steps ("First list
   entities. Then check each against the policy. Then answer."). Most
   reliable; borders on agent design (Module 8).

Modern reasoning models internalize long chains and expose only an answer (or
a paid-for reasoning trace). With those, your CoT prompt may be redundant —
the model is already doing it. Know which regime your provider's model is in.

## The accounting most teams skip

**Cost and latency scale with reasoning length.** A CoT prompt that improves
accuracy 6 points while tripling output tokens has changed your p99 latency
and your bill. Measure both axes (lesson 110). Short-circuit instructions —
"reason in at most 3 sentences" — preserve most of the benefit at a fraction
of the tokens.

**Trust, not truth.** Generated reasoning is *plausible post-hoc narrative*
as often as it is causation. Studies of CoT faithfulness show the final
answer and the stated reasoning can diverge — the chain is partly
rationalization. Practical consequences:

- Never audit *only* the explanation; audit the answer against ground truth
  (Module 7).
- Do use the chain for debugging *your prompt* — where it derails tells you
  what context is missing.
- For compliance-sensitive decisions, CoT text is not an audit trail. The
  audit trail is your eval harness + logged inputs/outputs.

**Answer extraction.** CoT output needs parsing discipline: demand a final
structured line (`Answer: <X>` or a JSON tail) and parse THAT, not the prose.
Otherwise you're regexing English.

## The one-two with self-consistency

For high-stakes single questions: sample the CoT k times (temperature ~0.7)
and take the majority *final answer*. Reasoning paths vary; correct answers
correlate. It multiplies cost by k — reserve it for adjudication of hard
cases (Module 7 uses it as an eval technique too).

## Check yourself

1. Your support classifier is at 91% and a teammate proposes "add 'think
   step by step'." Predict the effect and the cost change; what experiment
   decides it?
2. Why does CoT help arithmetic more than lookup, mechanically?
3. A compliance officer asks to see "the model's reasoning" for a denied
   claim. Draft your two-sentence answer.

Next: [060 — Structured output via JSON mode](060-structured-output-json-mode.md)
