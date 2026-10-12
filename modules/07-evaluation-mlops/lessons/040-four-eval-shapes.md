# Four eval shapes

**Reading time:** ~6 min · Module 7

Almost every LLM evaluation is one of four shapes. Naming them turns
"how should we evaluate this?" from a philosophy seminar into a routing
decision — and tells you the cost, the failure modes, and the tooling
each requires.

## Shape 1: Exact match (the programmer's eval)

Output is checked mechanically: field values, schema validity, unit
tests on extracted data, "does the SQL parse," "is the JSON valid per
this Pydantic model." From Module 2's structured-output tooling.

- **Cost:** near zero. **Reliability:** perfect *for what it checks*.
- **Use for:** extraction, classification, routing, tool-call arguments,
  anything you've constrained to a schema.
- **Blind to:** everything outside the schema — a perfectly-shaped JSON
  full of wrong values passes.

## Shape 2: Reference comparison (the diff eval)

Output vs a gold answer via containment, overlap, or embedding
similarity (lesson 030's toolkit).

- **Cost:** cheap. **Reliability:** moderate; paraphrase-blind or
  detail-blind depending on method.
- **Use for:** bulk regression triage, summarization pipelines where
  references exist, ranking many candidates before a human pass.
- **Blind to:** correctness of novel phrasings; rewards lexical mimicry.

## Shape 3: Rubric judgment (the eval that scales)

A judge — LLM or human — scores output against a written rubric:
binary checks ("does the answer cite a source for every claim?"),
Likert scales, or pairwise preferences. The workhorse for open-ended
generation; lesson 050 owns the judge-bias machinery.

- **Cost:** moderate (LLM judge calls; human review for calibration).
- **Reliability:** as good as your rubric and your judge's validation —
  both are artifacts you version and test like code.
- **Use for:** chat quality, groundedness (Module 4 lesson 120),
  style/tone, fine-tune comparisons (Module 5 lesson 110).

## Shape 4: End-to-end outcome (the business eval)

Did the *system* achieve the goal: ticket resolved without escalation,
user's question answered (measured by downstream behavior), agent task
completed (Module 8's scoring), task completed within budget. Usually
measured on live traffic or simulations.

- **Cost:** high ( instrumentation, time-to-signal). **Reliability:**
  it's the only shape that measures what the business bought.
- **Use for:** the weekly scorecard; validating that proxy metrics
  still proxy. **Blind to:** *why* — pair it with shapes 1–3 for
  attribution (lesson 100's traces).

## The routing table

| Output type | Primary shape | Fallback |
|---|---|---|
| Structured/extractive | exact match | LLM judge for disputes |
| Free text w/ references | reference metrics (triage) | rubric judge |
| Open-ended quality | rubric judge | human review sample |
| Whole product | end-to-end outcome | all of the above for attribution |

Real systems compose all four: exact-match gates in CI, reference
metrics on every commit, judge samples in prod, outcome dashboards
weekly. The composition is the practice; any single shape alone is a
blind spot with a dashboard.

## Check yourself

1. Classify: "did the model return valid JSON matching TicketTriage?"
   — and name what this eval cannot see.
2. Your end-to-end resolution rate dropped 3 points while all judge
   scores held. Which layer does that indict, and which shape locates
   the cause?
3. Why is pairwise preference (a shape-3 variant) more reliable than
   absolute 1–10 scoring for the same judge model?

Next: [050 — LLM-as-judge](050-llm-as-judge.md)
