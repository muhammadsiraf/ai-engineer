# When prompting stops working

**Reading time:** ~6 min · Module 2

Prompting is the first tool you reach for and the first one that runs out.
Knowing *where its ceiling is* — and which escalation to buy next — is the
difference between a system that plateaus gracefully and a codebase
entombed in 6,000-token prompts. This lesson is the diagnosis manual.

## The five symptoms of ceiling

1. **Accuracy plateaus below the bar.** You've tried prompt variants, few-shot
   curation, better phrasing; eval numbers (Module 7) move ±1 point, noise.
2. **Consistency, not quality, is the problem.** Each output is defensible;
   the *style/format/depth* varies in ways users notice. Prompting conditions;
   it doesn't guarantee.
3. **The prompt has become a rules engine.** Fifteen if-this-then-that
   clauses, special cases per customer, a changelog. You're programming in
   English — the worst of both worlds.
4. **Context cost is winning.** You're stuffing ever-more examples and rules
   into every request; latency and $ per call creep (lesson 100) while
   accuracy doesn't.
5. **The task needs knowledge the model doesn't reliably hold.** Domain
   jargon, house style, private formats — per-request conditioning keeps
   re-teaching what should be baked in.

If you tick one, plan an escalation. Two or more: you're overdue.

## The escalation ladder, with costs

```
Level 0  Better prompt hygiene (lessons 020–060)        ~hours
Level 1  Few-shot curation, task decomposition           ~days
Level 2  RAG — move knowledge out of the prompt          ~weeks   (Module 4)
Level 3  Fine-tune — move behavior into the weights      ~weeks   (Module 5)
Level 4  Model change: bigger host, or self-hosted       ~weeks   (lesson 150)
```

Work *up* the ladder in order: each rung is cheaper to try than the next,
and each leaves reusable infrastructure (retrieval, evals, routers). The
classic anti-pattern is jumping to fine-tuning to fix what is actually a
knowledge problem (fine-tuning teaches *behavior*, retrieval supplies
*facts* — Module 5's intro dissects this).

## Choosing the right rung for the actual disease

| Disease | Right treatment | Wrong treatment |
|---|---|---|
| Model lacks the *facts* (they change often) | RAG | fine-tuning (freezes facts, still hallucinates) |
| Model lacks the *behavior* (format, tone, policy) | fine-tuning | more RAG (context bloat) |
| Output varies run-to-run | structured output + temp 0 + FT | longer prompts |
| Task too big for one pass | decomposition (Module 8 agents) | one giant prompt |
| Small model fails, big model works | self-host fine-tuned small (Module 5) | pay flagship for everything |
| Long-tail edge cases | eval-driven prompt fixes + fallbacks | blanket escalation |

The knowledge/behavior distinction is the load-bearing decision of your
quarter. Test it empirically: give the model the fact in context — if it
then performs, it was knowledge (RAG). If it fails even *with* the fact,
it's behavior (fine-tune, or accept and route around).

## Decomposition: the underrated rung

Half of "prompting stopped working" is actually **task overload** — one call
asked to read, decide, extract, format, and explain. Split it:

```
one mega-prompt (inconsistent, plateaued)
  → extract (structured, cheap model)
  → decide (reasoning model, narrow job)
  → format (template, no LLM at all)
```

Each stage gets a small focused prompt, its own eval, and a model sized to
its difficulty. This is the gateway to Module 8's agent patterns, and it
frequently makes Level 3 unnecessary.

## Accepting the ceiling honestly

Some tasks don't clear the bar at any rung worth their cost. The
professional moves: reframe the product (human-in-the-loop review; the LLM
drafts, people approve), narrow the domain (85% of cases automated beats
100% attempted badly), or don't ship the feature. "The model can't do this
reliably yet" is an engineering *finding*, delivered with eval numbers.

## Check yourself

1. Classify: "our legal-summarizer keeps missing jurisdiction-specific
   caveats that ARE in our knowledge base." Which rung, and why?
2. Your classifier format-drifts 1 in 20 calls despite strict prompts.
   Order the fixes: temperature, structured output, fine-tune, few-shot.
3. Design the experiment that decides RAG vs fine-tuning for a support bot
   with a big policy wiki and a strict answer-format requirement (hint:
   it's usually both — which order?).

Next: [180 — The minimum-viable LLM app architecture](180-minimum-viable-llm-app-architecture.md)
