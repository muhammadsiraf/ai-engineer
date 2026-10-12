# Instruction format and chat templates

**Reading time:** ~6 min · Module 5

A chat model never sees a "conversation" — it sees one token stream with
special markers dividing the roles. The chat template is the function that
renders `(system, user, assistant)` into that stream, and fine-tuning data
MUST be rendered with the same template the serving path will use. Mismatch
here quietly destroys otherwise-good runs.

## What a template actually is

```
<|im_start|>system
You are a helpful assistant.<|im_end|>
<|im_start|>user
What is LoRA?<|im_end|>
<|im_start|>assistant
A low-rank adaptation method.<|im_end|>
```

(ChatML shape; Llama-3, Mistral, Gemma each have their own markers and
layout.) The markers are *learned* — the base model was pretrained with
this exact format, which is why using the wrong one feels like speaking
gibberish to the model: the conditioning distribution is off, and even a
perfect dataset trains the wrong mapping.

## The rules that break runs

1. **Use the tokenizer's template.** `tokenizer.apply_chat_template(...)`
   — never hand-roll the string. Exception: when your *serving path*
   formats differently (e.g., an OpenAI-compatible server with its own
   renderer), train on THAT rendered shape; the serving template is the
   one that counts.
2. **The generation prompt must match at inference.** The template
   determines what tokens precede the model's first output token
   (`<|im_start|>assistant\n`). If training examples end with the
   assistant turn's `<|im_end|>` (they should) but your server's prompt
   omits the header, the model starts mid-format.
3. **Consistency across the dataset:** one template version, applied
   identically to every example. Mixing formats teaches the average of
   two mappings.

## Special tokens, added tokens, and the tokenizer trap

If your format introduces markers the base tokenizer splits weirdly
(the classic: leading whitespace differences, or a marker like
`<|eot_id|>` that isn't a single token), every example's tokenization is
subtly wrong. Verify once with: render one example, tokenize it, decode
it back, diff. Thirty seconds; saves a week.

## Why Module 2's lessons suddenly apply to training data

Everything from Module 2 lesson 100 (stable structure) and 120
(deterministic serialization) applies to your *dataset rendering*: the
training pipeline is just another client producing prompts. The same
determinism discipline — same template, same whitespace, same ordering —
is what makes the model's learned mapping unambiguous.

## Check yourself

1. Your run trains fine but serving output starts with a stray
   `<|im_end|>`. Diagnose it precisely with the generation-prompt rule.
2. Why is hand-rolling a template string worse than it sounds? Give the
   failure that's invisible in loss curves.
3. Your dataset mixes ChatML and Llama-3 formats (two annotation batches).
   What behavior do you expect at serving time, and what's the cheapest
   fix?

Next: [080 — Training loop and loss mask](080-training-loop-and-loss-mask.md)
