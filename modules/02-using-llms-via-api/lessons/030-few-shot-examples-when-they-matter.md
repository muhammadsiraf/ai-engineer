# Few-shot examples: when they matter

**Reading time:** ~6 min · Module 2

Few-shot prompting — showing the model input→output examples before asking
for a new one — is the highest-leverage technique in day-to-day LLM work.
It's also the most misused: teams cargo-cult examples into prompts where the
model didn't need them, and skip them where they'd have saved a fine-tune.
This lesson is the decision framework plus the mechanics.

## The mechanism

The model is a continuation engine (Module 1 lesson 010). Alternating
user/assistant turns ending in a fresh user turn create a *pattern*; the
highest-probability continuation is to complete the pattern. You are not
"teaching" the model — you are **conditioning** it. Three properties follow:

1. **Effects are immediate and stateless.** No training call, no weights
   touched; it lives and dies with the request.
2. **Format transfers almost perfectly; reasoning only partially.** Examples
   reliably teach *shape* (JSON schema, tone, length). They weakly teach
   *skill* (a model that can't do arithmetic won't learn it from examples).
3. **Order and selection are hyperparameters.** Changing which examples
   you show is changing the prompt — evaluate it like one (Module 7).

## When few-shots are worth their tokens

**Reach for them when:**

- **Output format is unusual or strict.** Three examples of your exact JSON
  beat a paragraph of schema description.
- **The task has consistent idiom/style.** Classification labels ("billing"
  vs "BILLING" vs "Billing issue"), tone matching, abbreviation conventions.
- **Edge-case behavior needs demonstrating.** One example showing the
  ambiguous case handled correctly ("unclear → return UNKNOWN, don't guess")
  encodes a policy sentence can't.
- **Small models.** For 7–8B-class models (your self-hosted tier), examples
  substitute for a lot of instruction-following the big models have baked in.

**Skip them when:**

- The task is generic and the model is strong (summarizing prose, answering
  from context) — instructions alone suffice; examples just burn context.
- You'd need >5 examples to cover the space — you're reimplementing
  fine-tuning badly. Curate 3–5 *diverse* examples or move to Module 5.
- Examples would leak sensitive data into every request.

## Mechanics that matter

**Delimit the real input.** After examples, make the actual request
unmistakable — a final user turn with fresh text, ideally inside explicit
fences (`<ticket>...</ticket>`) used consistently *in the examples too*.
Consistent delimiters are the difference between conditioning and confusion.

**Balance the labels.** Four examples where the answer is always "positive"
teaches the model to answer "positive." Class distribution in your examples
is a prior you're injecting.

**Match the production distribution.** Examples from last year's tickets
teach last year's format. Treat the example set as a versioned artifact with
an owner, not a paste from a chat.

**Cost math.** Each example costs its tokens on *every* request (lesson 100).
An 800-token few-shot block on a 10k-request/day endpoint is ~8M tokens/day
of pure conditioning — fine if it's load-bearing, waste if instructions
would do. Measure: does accuracy with examples beat accuracy without, beyond
noise? That's an A/B (Module 7), not a vibe.

## Zero-shot vs few-shot, honestly

Modern frontier models close much of the gap on *common* tasks — for plain
summarization or standard JSON, zero-shot with a good system prompt is often
statistically indistinguishable from few-shot, at lower cost. The durable
uses are exactly the cases above: idiosyncratic formats, edge-case policy,
small/cheap models. Few-shot is a tool with a scope, not a default seasoning.

## Check yourself

1. Your classifier is 94% accurate zero-shot; 94.5% with 1,200 tokens of
   examples. Traffic: 50k requests/day. Justify keep or drop in one sentence
   of arithmetic.
2. Why does one *counterexample* ("here's an ambiguous ticket → UNKNOWN")
   often outperform a rule like "if ambiguous, say UNKNOWN"?
3. A teammate pastes 12 examples into the prompt "to cover all cases." What
   are two failure modes of that approach, and what's the better escalation
   path?

Next: [040 — Prompt engineering 101](040-prompt-engineering-101.md)
