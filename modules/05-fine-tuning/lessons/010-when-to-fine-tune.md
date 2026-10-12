# When to fine-tune

**Reading time:** ~7 min · Module 5

Fine-tuning is the most expensive intervention in the LLM toolbox and the
most often applied to the wrong problem. This module teaches the mechanics;
this lesson teaches the gate you pass through first, because "should we
fine-tune?" is a question with a boring correct answer most of the time:
no, and here's the cheaper thing that fixes your actual problem.

## The escalation ladder

Climb only when the rung below demonstrably fails on your eval set
(Module 7's discipline, applied before any training run):

1. **Better prompting** (Module 2): instructions, few-shot examples,
   structured output. Fixes a shocking fraction of "the model can't do X."
2. **RAG** (Module 4): the model lacks *knowledge*. Cheapest knowledge fix
   that exists; also the only one with citations and access control.
3. **Fine-tuning**: the model has the knowledge but wrong *behavior* —
   format, tone, latency-shaped brevity, domain style, a narrow skill.

Fine-tuning adds behaviors; it does not cheaply add, update, or cite
knowledge. (It can memorize facts at scale, but unreliably and without
attribution — Module 4 lesson 010's table is the permanent reference.)

## What fine-tuning is genuinely good for

- **Format discipline at scale:** always-valid JSON/schema adherence, fixed
  output templates, strict extraction shapes — cheaper than fighting a
  general model with prompts forever.
- **Style/tone identity:** a brand voice, a persona, consistent register.
- **Distillation for economics:** a frontier model's behavior compressed
  into a small model you can serve at a fraction of the cost (Module 3's
  arithmetic makes the savings concrete). The number-one *production*
  reason to fine-tune.
- **Narrow skills:** classification over your taxonomy, domain-specific
  extraction, a specific code-transformation task.
- **Preference sharpening:** DPO on your product's own preference data
  (lesson 120).

## The decision memo (write it before training anything)

One page, five lines: (1) the behavior, (2) the eval set and current
baseline score, (3) the prompt/RAG attempt and why it fails, (4) the
success threshold, (5) the serving plan (lesson 130). If line 3 is empty,
you're not ready. If line 2 is empty, stop entirely.

## Cost honesty

A LoRA run on a 7B model is hours on one GPU (lesson 050's QLoRA makes it
smaller); the real costs are elsewhere: dataset construction (lesson 060 —
usually the dominant cost), evaluation infrastructure, the maintenance
tail (every base-model upgrade re-runs everything — lesson 140), and the
option value you gave up by specializing.

## Check yourself

1. "Our bot doesn't know our 400-page product manual." Fine-tune? If not,
   what, and which lesson of Module 4 owns it?
2. Name the two lines of the decision memo people skip, and the failure
   each skip produces.
3. You want outputs under 50 tokens, always valid JSON, in your taxonomic
   vocabulary. Which ladder rung do you *start* at, and what would push
   you up one rung?

Next: [020 — Full fine-tuning vs PEFT](020-full-ft-vs-peft.md)
