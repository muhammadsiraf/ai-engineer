# Training loop and loss mask

**Reading time:** ~7 min · Module 5

The fine-tuning loop is Module 1's cross-entropy loss (lesson 030) run in
a circle: predict next token, score against the actual next token, backprop,
step. What's new is *where* you compute the loss — and the answer is the
single most common silent bug in instruction fine-tuning.

## The loop, compressed

```
for batch in dataloader:
    tokens, labels = render_and_mask(batch)        # this lesson
    logits = model(tokens)                          # forward
    loss = cross_entropy(logits[:, :-1], labels[:, 1:])   # shift!
    loss.backward(); optimizer.step(); optimizer.zero_grad()
```

Two details worth naming:

- **The shift:** the model predicts token t+1 from tokens ≤ t, so logits
  position i is scored against labels position i+1. Get the offset wrong
  and you train on a scrambled objective that *still lowers loss*, just
  teaches nothing useful.
- **Labels = -100 masks:** PyTorch's cross-entropy ignores targets of
  -100. Which tokens get -100 is the whole design decision.

## The loss mask: train on responses, not prompts

Instruction tuning computes loss **only on the assistant's response
tokens** (and its end marker). Prompt tokens are *conditioning*, not
targets:

```
tokens:   [system prompt][user question][assistant response][im_end]
labels:   [-100 -100 ...][-100 ...][response tokens][im_end]
```

Why: you don't want to pay the model for *generating questions or system
prompts* — you want it to be a better *answerer*. Computing loss on
prompts (the "train on everything" default in naive scripts) spends
capacity imitating your prompt distribution and dilutes the response
signal; results range from mild quality loss to a model that starts
completing your prompts instead of answering them.

Exceptions to know, not fear: continued pretraining masks nothing
(everything is a target); some completion-style tasks (e.g., fill-in
templates) mask partially. The principle: **loss on exactly the tokens
whose generation you want to teach.**

## The hyperparameters that matter, in order

1. **Learning rate:** 1e-4 to 2e-4 for LoRA, 1e-5 to 2e-5 for full FT.
   The #1 knob; wrong by 10x and everything else is noise.
2. **Warmup + cosine decay:** a few % of steps warmup, standard decay.
3. **Epochs: 1–3.** Instruction fine-tuning overfits *fast* (lesson 090's
   curves show it): epoch 2 often improves training loss while degrading
   eval. Save a checkpoint per epoch; eval each.
4. **Batch size via accumulation:** effective batch 16–128 sequences;
   with QLoRA-sized VRAM you accumulate (lesson 050's batch memory note).
5. **Max sequence length:** your dataset's realistic p99, not the model's
   max — activation memory scales with it (lesson 050).

## Check yourself

1. A teammate's run shows loss falling nicely, but outputs echo the user's
   question before answering. Diagnose with the loss-mask lens.
2. Why does the shifted cross-entropy *look* fine (loss decreases) even
   when the shift is implemented wrong?
3. Epoch 3 halves training loss vs epoch 1 but eval gets worse. What is
   happening, and which two interventions are standard?

Next: [090 — Reading loss curves honestly](090-reading-loss-curves-honestly.md)
