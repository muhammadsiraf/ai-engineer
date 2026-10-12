# Provider comparison: OpenAI / Anthropic / open

**Reading time:** ~6 min · Module 2

"How do I choose a model?" is the wrong question; "what's my decision
process when models keep changing?" is the right one. Specific models age in
months; the *dimensions* below are stable. Use them as your evaluation
rubric, re-run it quarterly, and keep the answer in a decision doc — not in
someone's memory of a blog post.

## The dimensions that actually matter

| Dimension | What to ask | How to measure |
|---|---|---|
| Task quality | wins on MY golden set | your eval harness (Module 7), not leaderboards |
| Latency profile | TTFT + TPS at my prompt sizes | streaming probe (lesson 110) |
| Cost | $/successful task, not $/token | the dashboard from lesson 100 |
| Context | usable (not just advertised) length | needle-tests at MY lengths |
| Structured output | schema adherence rate | validation-pass % on golden set |
| Tool calling | selection + argument accuracy | tool-use evals (Module 8) |
| Reliability | uptime, rate-limit ceilings, regional availability | status pages + your 429 logs |
| Safety/policy | refusal behavior on MY edge cases | red-team set (Module 8) |
| Data terms | training-on-my-data? retention? | contract, in writing |
| Escape hatches | fine-tuning? distillation allowed? | terms + roadmap |

Two honest notes: **leaderboards tell you about average capability on
public tasks; your product is neither.** And **price per token is the least
informative number on the page** until multiplied by your actual
tokens-per-successful-task.

## The hosted trio, characterized honestly

- **OpenAI:** broadest model ladder (flagship → mini → nano), mature tooling,
  JSON-schema outputs, realtime voice. The default choice when you want the
  least integration friction and a clear cheap tier for routing (lesson 100).
- **Anthropic:** strong long-document and agentic behavior (tool use was
  effectively introduced to the industry here), writing quality, safety
  posture. Prompt caching is first-class and generous. If your workload is
  document-heavy or agentic, weight it accordingly.
- **Google:** enormous context windows, strong multimodal, aggressive
  pricing; worth benchmarking for long-context and multimodal niches.

All three speak near-identical chat/tool APIs (OpenAI-compat or thin
wrappers), which is why lesson 010's wrapper discipline pays: **switching
cost is mostly eval + prompt revalidation, not code.**

## The open-weight lane

Llama, Qwen, Mistral, DeepSeek, and friends — weights you download and serve
(vLLM, Module 6). The trade:

| You gain | You pay |
|---|---|
| per-token cost at scale (your GPUs) | ops burden: serving, scaling, upgrades |
| data control (nothing leaves) | you own safety tuning + abuse handling |
| no rate limits but your own | smaller context/tooling gaps vs frontier |
| fine-tune & quantize freely | quality gap on the hardest tasks |

Decision heuristic that works: **frontier-hosted for the hard 20% of
traffic, open-weight for the routine 80%** — the router from lesson 100 —
with the crossover point set by measured quality parity on your golden set
(usually the small tasks hit parity first).

## The fallback ladder (design it before you need it)

```
primary (premium hosted)
  → same-family smaller (degraded quality, still good)
  → other provider's comparable (contractual/geo risk hedge)
  → self-hosted open-weight (quality floor, availability floor)
  → static/queued ("we'll email you the answer")
```

Each rung needs: its own prompt (verified on the golden set — prompts are
not portable across families), its own latency/cost numbers, and an alert
when traffic shifts rungs (that's an incident signal, not a configuration).

## The quarterly re-decision

Models change monthly; your stack shouldn't. The process that keeps you
sane: golden set + harness stay fixed; models are candidates. Quarterly:
re-run the rubric, review price changes, test one challenger against the
incumbent on the golden set, and write a one-page memo. Adoption happens on
*your* schedule, gated by *your* evals — never by a launch-week blog post.

## Check yourself

1. Your CEO wants "the best model." Translate that into the three numbers
   you'll bring to the next review.
2. Why is a prompt written for provider A not automatically portable to
   provider B, and what's the minimal revalidation?
3. Sketch the fallback ladder for a European fintech with data-residency
   requirements — which rungs survive the constraint?

Next: [150 — When to switch to open-weight](150-when-to-switch-to-open-weight.md)
