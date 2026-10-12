# Tokens: what one token actually is

**Reading time:** ~7 min · Module 1

Every price quote, latency figure, context limit, and rate limit in LLM
engineering is denominated in tokens. You cannot do cost math, debug truncation,
or reason about context without an exact feel for what a token is. Ten minutes
here saves you from a career of "why is the bill 3x my estimate?"

## The problem tokenization solves

Neural networks consume fixed-size numeric vectors. Text is variable-length
strings of characters. You need an invertible text → integer-sequence mapping.
The naive options both fail:

- **Per character:** sequences get huge (and computation scales with sequence
  length), and individual characters carry too little meaning.
- **Per word:** vocabulary explodes (millions of forms: "run", "runs", "running",
  "ran"...), and any word not in the vocab is unrepresentable.

The industry answer: **subword units** — chunks between a character and a word.
Common words stay whole (" the", " and"); rarer words split into reusable pieces
("tokenization" → "token" + "ization").

## BPE: how the vocabulary gets built

Byte-Pair Encoding, the dominant scheme (used by GPT models, Llama 3, and most
others in some variant), builds its vocabulary by a greedy merge procedure over
the training corpus:

1. Start with every byte as a token (256 of them — this is why *no input is
   ever unrepresentable*).
2. Count adjacent token pairs across the corpus.
3. Merge the most frequent pair into a new token.
4. Repeat until you hit the target vocabulary size (e.g., 50k, 128k).

After "th" + "e" merge because they're everywhere, " the" becomes a token, then
" there", " there ", and so on — frequency-driven coalescence. You'll implement
one merge step by hand in the challenge for this lesson; it's three lines of
Python and it makes the whole thing click.

## The rule of thumb, calibrated

English prose: **~1 token ≈ 4 characters ≈ 0.75 words.** So:

- 500-word essay ≈ 650–700 tokens
- 8k-token context ≈ 6,000 words ≈ 24 pages

Calibrate your instincts on the outliers:

| Text | Token efficiency |
|---|---|
| English prose | good (~0.75 words/token) |
| Code | worse — punctuation and identifiers split heavily |
| Non-English (some tokenizers) | can be 2–4x more tokens for the same meaning |
| Base64, hashes, UUIDs, minified JSON | terrible — near 1 token per 2–3 chars |

That last row is a production landmine. Stuffing a 50 KB base64 image blob or a
minified bundle into a prompt can cost more tokens than the entire rest of your
app. Preprocess or refuse.

## Why this matters operationally

**Cost.** You're billed per token, input and output separately (output usually
3–5x pricier). Every token in the conversation is resent every turn (lesson 020),
so cost grows quadratically-ish with conversation length unless you manage
context.

**Limits.** "128k context" means 128k tokens for prompt + completion combined.
An over-limit request either errors or silently truncates depending on the
provider — a truncation you didn't choose is a correctness bug.

**Latency.** Time-to-first-token is dominated by processing your prompt
(prefill — lesson Prefill/Decode in Module 3); completion speed is per-token.
Two prompts with the same word count can have very different prefill costs
if one tokenizes densely.

## Counting before you call

Never estimate in production — count. The `tiktoken` library gives you the
exact count for OpenAI models offline:

```python
import tiktoken
enc = tiktoken.get_encoding("cl100k_base")
len(enc.encode("def hello(): return 'world'"))   # exact count
```

The challenge set includes building a cost estimator on top of this. For
non-OpenAI models, `transformers.AutoTokenizer` serves the same role.

## Check yourself

1. Why can BPE represent *any* string, including binary junk and rare Unicode,
   without an OOV (out-of-vocabulary) token?
2. A user pastes a 2 MB minified JavaScript file. Rough token cost, and what do
   you do about it?
3. Same paragraph, translated from English into Japanese: why might the token
   count double, and what two operational impacts does that have?

Next: [040 — Tokenization edge cases that bite you](040-tokenization-edge-cases-that-bite-you.md)
