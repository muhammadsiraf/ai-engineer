# What 'training' actually does

**Reading time:** ~7 min · Module 1

Strip away the mystique and training is a loop you could write in an afternoon:
guess, measure how wrong you were, nudge the numbers, repeat — a few hundred
billion times. This lesson walks that loop precisely, because fine-tuning
(Module 5), eval (Module 7), and half of inference engineering (Module 3) only
make sense once you own it.

## The loop

```python
for batch in data:                     # 1. grab a small chunk of examples
    logits = model(batch.x)            # 2. forward pass: predict
    loss = cross_entropy(logits, batch.y)  # 3. measure wrongness (a single number)
    loss.backward()                    # 4. compute gradient of loss w.r.t. every weight
    optimizer.step()                   # 5. nudge every weight slightly downhill
    optimizer.zero_grad()
```

Five steps. "Learning" is step 5: every weight in the model moves a tiny amount
in the direction that would have reduced this batch's error. Do this a few
hundred thousand times over a few trillion tokens and you get GPT-2 → Llama 3.

## The loss: cross-entropy on next tokens

For language modeling, the target `y` is simply **the actual next token** in the
text. The loss, cross-entropy, has a beautiful interpretation:

```
loss = -log( probability the model assigned to the correct next token )
```

- Model assigns 0.9 to the right token → loss ≈ 0.105 (small penalty)
- Model assigns 0.001 → loss ≈ 6.9 (large penalty)
- Uniform guess over 50k tokens → loss ≈ 10.8 (log 50k)

So "the training loss went from 10.8 to 2.1" translates to: "the model went from
clueless to assigning roughly e^-2.1 ≈ 12% average probability to the correct
next token — and in a 50k-way choice, that's extraordinary." You'll implement
cross-entropy in the challenge; it's three lines and it demystifies the loss
curves you'll stare at in Module 5.

## The gradient: blame assignment at scale

Step 4 is the part that seems magical: how do you know which direction to nudge
*each of billions* of weights? Backpropagation — the chain rule from calculus,
applied efficiently. Each weight gets its own "how much did you contribute to
this error, and which sign of movement helps?" score.

If calculus isn't daily practice for you, this is enough: **backprop = a
systematic way to compute, for every single parameter, the direction and
steepness of the error with respect to that parameter.** Autodiff frameworks
(PyTorch) do the bookkeeping; you'll watch it work in the challenges.

## Vocabulary you need to read the field

| Term | Meaning | Engineering relevance |
|---|---|---|
| batch | examples processed per step | bigger batch = better GPU use, more memory (Module 3/5) |
| step / iteration | one loop pass | throughput metric: tokens/sec |
| epoch | one full pass over the dataset | fine-tunes run 1–3 epochs, no more |
| learning rate | step size for the nudge | the #1 hyperparameter to get wrong |
| overfitting | memorizing training data | shows up as train loss ↓, eval loss ↑ |
| gradient descent | the whole scheme | everything in Module 5 |

## Pretraining vs fine-tuning vs alignment

Same loop, different data and scale:

1. **Pretraining:** next-token prediction over trillions of tokens of web text.
   Months on thousands of GPUs. Produces the "base model" — brilliant and
   feral; it completes text, it doesn't *answer*.
2. **Fine-tuning (SFT):** same loop on curated instruction→response pairs,
   hours-to-days on dozens of GPUs. Teaches format: how to be an assistant.
3. **Preference tuning (RLHF/DPO):** trains on which of two answers humans
   preferred — adjusts *taste*. Module 5 covers the DPO loss hands-on.

The base model already contains the capabilities; SFT and preference tuning
reshape *behavior*. This is why fine-tuning a small model hard can beat
prompting a big model — and also why fine-tuning can't teach facts reliably
(it's a behavior-shaping tool, not a database insert; Module 5's "catastrophic
forgetting" lesson quantifies the cost).

## Check yourself

1. In one sentence each: what do the forward pass, the loss, and the backward
   pass compute?
2. A fine-tune's loss curve: train loss still falling, eval loss rising since
   step 400. What's happening and what do you do?
3. Why does pretraining data scale matter so much more than fine-tuning data
   scale, given they use the same loss function?

Next: [080 — What the weights actually are](080-what-the-weights-actually-are.md)
