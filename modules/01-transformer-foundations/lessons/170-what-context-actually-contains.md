# What 'context' actually contains

**Reading time:** ~7 min · Module 1

"The model knows X" is almost always false in an interesting way: the model
*was shown* X recently. Context is the model's entire working memory, and as the
engineer you assemble it. This lesson dissects what's actually in there for a
real production request — because every cost, latency, safety, and quality
property of your app is determined by this inventory.

## The anatomy of a request

Here's what the token stream for a realistic chat completion looks like, front
to back:

```
┌────────────────────────────────────────────────────────┐
│ 1. System prompt / platform instructions    500–3k tok │   provider's + yours
│ 2. Tool/function definitions               200–5k tok  │   schemas for every tool
│ 3. Retrieved documents (RAG)               ??? tok     │   the flexible block
│ 4. Conversation history                    ??? tok     │   grows every turn
│ 5. The new user message                    ??? tok     │   what just came in
│ 6. [generation happens here]               reserved    │   your max_tokens budget
└────────────────────────────────────────────────────────┘
```

Every part of 1–5 is resent, token-for-token, on **every single call** of the
conversation. A 20-turn support chat with a 1,500-token system prompt and tools
defined doesn't send 20 × (message length); it sends the full accumulated stack
20 times, with growing history. That's the cost curve from lesson 020, now with
names on the blocks.

## Blocks 1–2: the expensive constants

System prompt and tool definitions are *fixed costs amortized over the whole
product*. Two disciplines follow:

- **Measure them.** Tokenize your real system prompt + worst-case tool set.
  Teams are routinely surprised: 4k tokens of preamble × every request × your
  QPS = real money and real prefill latency (lesson 130's TTFT).
- **Earn every token.** Duplicate instructions, defensive fluff, and unused
  tool definitions are pure tax. Prompt compression is legitimate engineering.

(Prompt caching — Module 2 — exists precisely to discount these stable prefixes.
It works because blocks 1–2 rarely change within a deployment.)

## Block 3: retrieved context is a claim, not a fact

When you put five documents in context, you've made the model an implicit
promise: *the answer is in here*. Quality determines whether the promise is
kept — wrong or noisy retrieval produces confident answers grounded in the
wrong text (hallucination with citations, arguably worse than without). And
attention's middle-blindness (lesson 050) means *placement* matters: critical
documents go early or late, not buried at token 40,000. Module 4's reranking
exists to make this block small and dense.

## Block 4: history is state you own

The model has none (lesson 010). Your options, in escalating effort:

| Strategy | Mechanism | Cost |
|---|---|---|
| Full history | resend everything | token cost grows every turn |
| Sliding window | keep last k turns | loses old constraints silently |
| Summarize-then-keep | compress old turns into a summary | summary can drop the wrong details |
| Structured memory | extract facts to a store, re-inject selectively | engineering (Module 8) |

The silent failure to design against: **a 30-turn conversation where the user's
step-2 constraint ("never mention pricing") sits outside the window at turn
28.** Nothing errors. The model just... mentions pricing. Context management
bugs degrade gracefully-then-catastrophically, never loudly.

## Block 6: headroom is a correctness feature

Reserve output budget explicitly. If blocks 1–5 fill a 128k window, your
completion truncates (lesson 040) or the request fails. Budget:
`context_limit ≥ Σ(blocks 1–5) + max_tokens_output + safety margin`. Make this
an assertion in your request path, not a hope.

## The security reading of this diagram

Everything in context is (a) visible to the model, which will *use* it
instruction-likes and all, and (b) potentially echoed into output. Retrieved
documents can contain adversarial instructions (prompt injection — Module 2's
threat-model lesson); conversation history can carry PII you're about to log or
send to a third party. Context assembly is your app's real attack and compliance
surface. You'll build the defenses (injection hardening, PII hygiene) in
Modules 2 and 8.

## Check yourself

1. Compute, roughly, the token cost per call at turn 15 of a chat with a 2k
   system prompt, 1k of tools, ~300-token exchanges, and 800 tokens of
   retrieved docs per turn. What's the total input across the conversation?
2. Your users report the bot "forgot" an instruction from early in long
   sessions. Diagnose with the anatomy diagram; propose the cheapest fix.
3. Why does prompt caching discount blocks 1–2 but not blocks 3–4?

Next: [180 — The math you don't need to know](180-the-math-you-dont-need-to-know.md)
