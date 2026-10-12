# When to switch to open-weight

**Reading time:** ~6 min · Module 2

Self-hosting an open-weight model is a real option — sometimes the obvious
one, often a trap. This lesson is the decision framework: the four triggers
that justify the move, the costs people forget, and the migration path that
doesn't end in a two-month detour.

## The four triggers that actually justify it

**1. Data control is contractual, not aspirational.** Regulated industries,
customer contracts, jurisdictions: if "prompts never leave our
infrastructure" is a requirement, open-weight on your GPUs (or a
private-tenancy host) is often the *only* compliant shape. Note: enterprise
tiers of hosted providers with zero-retention terms can also satisfy many
requirements — read the contract before buying GPUs.

**2. Volume economics flip.** At high sustained volume, hosted per-token
pricing loses to amortized GPUs. The crossover depends on utilization:
a GPU earns its keep when busy. Rough shape (2020s pricing, redo the math
when you read this): if you're spending five figures monthly on one
model family and utilization math says 40%+ GPU busy-time, price the
self-hosted path seriously. Below that, hosted almost always wins once you
count ops.

**3. Customization depth.** Heavy fine-tuning (Module 5), unusual
quantization targets, modified architectures, custom sampling internals —
hosted APIs cap how far you can bend the model. Owning weights means owning
every knob, including the ones Module 3 teaches (quantization, batching).

**4. Availability/isolation.** No provider rate limits, no multi-tenant
noisy neighbors, no regional outages you can't fix — but also no one to
page but you. This trigger is really "we're big enough to run an inference
platform anyway."

## The costs that break naive ROI spreadsheets

The spreadsheet says: `GPU-hours × rate < hosted tokens`. Reality adds:

- **Serving engineering:** vLLM deployment, autoscaling, version upgrades
  (Module 6 is essentially this cost itemized — ~the whole module).
- **Quality maintenance:** open models release often; each upgrade re-runs
  your eval gauntlet; each *new* model may need prompt rework.
- **The long tail of tasks:** frontier hosted models still win on the
  hardest 5–10%. Self-hosting one model means your worst cases get worse.
  Mitigation: keep a hosted fallback rung (lesson 140's ladder).
- **Safety/compliance burden:** refusal behavior and abuse resistance are
  now your configuration problem, not a provider's roadmap item.
- **GPU procurement lead time** and capacity planning (peak vs average).

## Picking the model: the boring checklist

- **License:** permissive vs community vs research-only; commercial terms
  for your use case; sub-licensing for SaaS.
- **Size vs your GPUs:** parameter count × precision bytes (Module 1 lesson
  080) + KV cache (Module 3) must fit with headroom. A model that barely
  fits serves one request at a time — false economy.
- **Ecosystem:** does it have solid vLLM support, a good tokenizer story,
  fine-tuning recipes (Module 5), and an active community? A great model
  with a broken serving story is a bad model for you.
- **Context length *usable*:** advertised vs needle-tested at your lengths.
- **Benchmark the family's small siblings too:** often an 8B fine-tuned
  beats a 70B prompted for a narrow task at 1/8 the serving cost — this is
  the Module 5 payoff.

## The migration path that works

1. **Golden set first** (Module 7): 100–500 real inputs with judged outputs.
   No set, no migration — that's the rule that saves you from yourself.
2. **Shadow-run** the open model: same traffic mirrored, compare outputs on
   the set; find the task categories where it loses (there are some).
3. **Route, don't switch:** move the winning categories to self-hosted;
   keep the rest hosted (lesson 100's router again — it's the reusable
   pattern of this whole module).
4. **Re-evaluate quarterly** — open models improve fast; your routing mix
   is a living config, not a one-time decision.

## What "switch" should mean

Almost never "replace." The durable architecture is **portfolio**: hosted
flagship for hard traffic, fine-tuned open-weight for your high-volume
specific tasks, small open-weight for trivial ones. The switch is per-task,
continuous, and reversible — which is only possible if you built the
wrapper (010), router (100), and evals (Module 7) first. Build those; the
switch becomes a config change.

## Check yourself

1. A startup at $4k/month hosted spend proposes buying GPUs "to save money."
   Write the three-line rebuttal.
2. Your compliance team requires zero data egress. List the two viable
   architectures and one question to ask each provider/vendor.
3. Which task categories usually migrate to self-hosted *first*, and why
   does the hard 10% stay hosted?

Next: [160 — Prompt injection: the threat model](160-prompt-injection-the-threat-model.md)
