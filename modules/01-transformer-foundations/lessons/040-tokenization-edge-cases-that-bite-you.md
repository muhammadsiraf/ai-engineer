# Tokenization edge cases that bite you

**Reading time:** ~6 min · Module 1

Tokenizer behavior produces some of the weirdest, hardest-to-debug LLM failures.
This lesson is a field guide to the ones you'll actually meet, with the
mechanism behind each so you can predict new ones.

## 1. The leading-space convention

Most BPE vocabularies were trained on text where words are typically preceded by
a space. The tokenizer therefore has tokens like `" hello"` (with the space
baked in) and *also* `"hello"` (without). These are different tokens:

```python
import tiktoken
enc = tiktoken.get_encoding("cl100k_base")
enc.encode("hello")    # [15339]
enc.encode(" hello")   # [25393]  <-- different!
```

Consequence: **string concatenation changes tokenization.** Build a prompt by
gluing pieces together and a word that used to be one token can become two
(meaning the model sees subtly different input), or two can merge. This is why
prompt templates are guarded obsessively and why trailing/leading whitespace in
retrieved chunks matters (Module 4).

## 2. Numbers split unpredictably

In many tokenizers, digits group inconsistently: `1234567` might become
`123` + `45` + `67`. Two effects:

- **Arithmetic is handicapped.** The model never sees clean column alignment of
  digits; each digit-group is just a symbol. This is a deep reason LLMs are
  unreliable at long multiplication and digit-precise tasks.
- **Counting is unreliable.** Asking "how many times does 'the' appear" requires
  exactly the kind of token-level bookkeeping the architecture doesn't do well.

Production rule: never trust the model with precise numeric/character
computation you can do in code. Give it a calculator tool (Module 8) or
precompute.

## 3. Inverse scaling on rare strings

Ask a model to repeat the string `"SolidGoldMagikarp"` (a famous pathological
token) or a random hash and it may glitch, hallucinate, or refuse — rare
tokens had almost no training signal, so the model's representation of them is
noise. UUIDs and API keys pasted into prompts are in this category.

## 4. Non-English and code density

The same *meaning* can cost wildly different token counts across languages
because the vocabulary is English-heavy. Consequences: non-English prompts are
more expensive and fit less context; code (dense punctuation, long identifiers
like `calculate_cumulative_distribution_function`) splits into many tokens.
This asymmetry matters when you pick a deployment language or estimate costs
for international traffic.

## 5. Truncation is not sentence-aware

`max_tokens` truncation cuts the token stream wherever it hits the limit —
mid-word, mid-JSON, mid-fence. The model never gets a chance to close its
quote. (Lesson 020's `finish_reason: "length"` is the tell.) Anything that
requires *well-formed* output needs a completion budget with headroom plus
validation-and-retry.

## 6. The tokenizer is model-specific — cache it correctly

Counting tokens for model A with model B's tokenizer gives you approximately
wrong numbers, which is worse than obviously wrong. Two production notes:

- Pin the exact tokenizer version alongside the model version; vocabularies
  change between model generations.
- For cost dashboards, count with the real tokenizer, never the ÷4 heuristic.

## A debugging recipe

When output seems inexplicable, *look at the tokens*:

```python
enc = tiktoken.get_encoding("cl100k_base")
for tok in enc.encode(your_prompt):
    print(repr(enc.decode([tok])))
```

Half the time you'll find a surprise: a stray newline collapsing two words, an
invisible unicode character, a template variable that didn't interpolate.
Tokenizers don't lie; templates do.

## Check yourself

1. Your prompt template joins a user name with `"\nQuestion: " + q`. The model
   sometimes treats the question's first word oddly. Mechanism?
2. Why is asking an LLM to count the words in its own previous answer
   unreliable, mechanically speaking?
3. Design the completion-budget policy for an endpoint that must return valid
   JSON: how much headroom, what check, what fallback?

Next: [050 — Why context windows are finite](050-why-context-windows-are-finite.md)
