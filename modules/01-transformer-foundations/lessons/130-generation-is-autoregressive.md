# Generation is autoregressive

**Reading time:** ~7 min · Module 1

The model predicts one token at a time, feeds its own output back in, and
repeats. That loop — autoregressive generation — explains streaming, explains
why long outputs are slow and expensive, and defines the failure mode where a
model talks itself into nonsense. Let's make the loop precise.

## The loop

```python
tokens = tokenize(prompt)
while True:
    logits = model(tokens)            # forward pass over the WHOLE sequence
    next_id = sample(logits[-1])      # pick ONE token from the last position
    if next_id == EOS or len(tokens) >= max_tokens:
        break
    tokens.append(next_id)            # append; next iteration includes it
```

Three properties fall straight out of this code:

1. **One token per forward pass at inference.** The API's "tokens per second"
   is literally how fast this loop spins. 50 tok/s = the model runs 50 forward
   passes to write one second of text.
2. **Every token conditions on all previous ones**, including the model's own
   past choices. There's no planning ahead at all. (The much-misreported
   "hidden reasoning" is just more tokens in the same loop — Module 8's
   plan-and-execute patterns cover the engineering versions of planning.)
3. **Cost grows with output length** — linearly in tokens, and (naively)
   quadratically in attention across the growing context. The KV cache tames
   the latter (Module 3).

## The sentence-level view: joint probability by chain rule

When the model generates "The cat sat", what it's computing is:

```
P("The") · P(" cat" | "The") · P(" sat" | "The cat")
```

A whole-sentence probability is the product of next-token probabilities — the
chain rule from probability class. Two engineering corollaries:

- **Errors compound.** Each factor ≤ 1; a long generation is a long product.
  There's no mechanism to go back and revise an early bad factor (in vanilla
  sampling — beam search and tree methods trade this off, at a cost).
- **Log-probabilities add.** This is why all scoring in this field (perplexity
  in Module 7, reranking in Module 4, logprob APIs) works in log space.

## Drift: how models talk themselves into corners

Because each token conditions on its own outputs, a mediocre choice at step 20
becomes *context* at step 21. The probability landscape shifts; mild errors can
amplify — repetition loops, drifting persona, forgetting an earlier constraint.
You've seen it: the model that was perfect for 400 tokens and then spirals.

Mitigations you'll meet in this course, in order of appearance:

- **Sampling controls** (next lesson): penalize repetition, cap the tail
- **Structured decomposition** (Module 8): shorter generations, each with fresh
  clean context, stitched by an agent loop
- **Eval harnesses** (Module 7): measure drift on long outputs before users do

## Why "just generate everything in parallel" doesn't work

The natural engineer question: GPUs are parallel — parallelize the loop! You
can't, because iteration t+1's *input* is iteration t's *output*. The sequence
dimension is inherently serial; that's a dependency, not an implementation
weakness. What *is* parallelized: the math within one pass (big matmuls), and —
critically, at scale — **many different users' sequences batched together in
one pass** (continuous batching, Module 3). Serving economics live entirely in
that second kind of parallelism.

## The two numbers this lesson predicts

Your latency SLO decomposes exactly as this loop predicts:

- **TTFT (time to first token):** one prefill pass over your prompt
- **TPS (tokens per second):** the decode loop's spin rate

Every serving optimization in Module 3 targets one of those two numbers. When
someone reports "the API feels slow," your first diagnostic split is: slower
first token (prompt problem — prefill) or slow trickle (decode problem)?

## Check yourself

1. Why can't you generate a 500-token completion by running one forward pass
   over 500 slots, like training does? What's different about the input?
2. Write the chain-rule expression for P(" Quick brown fox"). Which factor do
   you expect to be smallest, and why does that matter for drift?
3. Your product needs 2-second responses. TTFT is 300 ms; output averages 200
   tokens. What minimum TPS do you need, and which part of the pipeline would
   you optimize first?

Next: [140 — Temperature, top-k, and top-p](140-temperature-top-k-and-top-p.md)
