# Why agents fail: the four shapes

**Reading time:** ~7 min · Module 8

Agent failures look infinite and are actually four. Naming the shape
of a failure is most of the fix, because each shape has a distinct
signature in the transcript and a distinct remedy. Evaluate agents
*by shape*, not just success rate (lesson 120) — "87% success" hides
which repair will move the number.

## The taxonomy

1. **Under-triggering:** the model answers from its own weights when
   it should have called a tool — plausible, confident, wrong.
   Signature: final answer, zero or too-few tool calls. Fix: tool
   descriptions that say *when to use*, system-prompt rules
   ("always check X before answering Y"), and eval cases that catch
   it (the failure needs ground truth about which tools were
   required — which is why the eval set records it).
2. **Misuse:** right idea, wrong call — unknown tool, invalid
   arguments, wrong enum, hallucinated parameter names. Signature:
   validation errors in the transcript. Fix: schemas that are flatter
   and stricter (lesson 050), validation errors written as
   recoverable instructions, examples in the description.
3. **Thrash:** the same failing call repeats — the model re-issues
   identical (tool, args) hoping for a different result. Signature:
   duplicated call signatures. Fix: loop guards (lesson 060's
   circuit breaker), error messages that say what to change, and
   stopping rather than paying for attempt four.
4. **Premature stop:** the model declares success without the work —
   answers while the last tool errored, or fabricates the result it
   didn't get. Signature: "done" with an un-recovered error in the
   tail of the transcript. Fix: forced grounding (the answer must
   cite tool outputs), verification passes (lesson 090's reflexion),
   and evals that check *verified* success, not declared success
   (lesson 120's completion vs. success distinction).

## Reading traces like a doctor

Symptoms cluster: an agent that under-triggers on lookups also
hallucinates parameters (both are "answered from weights instead of
the environment"). An agent that thrashes usually has vague errors —
it isn't dumb, it's unguided. The challenge builds the classifier;
once runs are labeled automatically, Module 7's per-category
regression gates apply to failure modes too ("misuse rate must not
increase by more than 2 points").

## The meta-lesson

None of the four fixes is "better prompt" alone. They're schema
design, error design, budgets, grounding rules, and eval coverage —
*engineering*. That's the recurring claim of this course, and agents
are where it pays most visibly.

## Check yourself

1. A run ends with "Your refund was processed" and a transcript
   containing `refund_order → {"error": "insufficient_permissions"}`.
   Which shape, and what are the two cheapest fixes?
2. Why can under-triggering only be measured with a labeled eval set?
3. Your agent thrashes on pagination. Which artifact is wrong — the
   tool's design or the guard's threshold — and why is it the tool?

Next: [050 — Designing tools](050-designing-tools.md)
