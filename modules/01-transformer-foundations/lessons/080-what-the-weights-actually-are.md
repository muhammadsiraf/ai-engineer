# What the weights actually are

**Reading time:** ~7 min · Module 1

"Weights" gets said a hundred times a day in this field. For an engineer, vagueness
here is expensive — quantization (Module 3), LoRA (Module 5), and VRAM sizing all
require knowing exactly what these numbers are, how they're organized, and how
big they are. So: concretely, with shapes.

## A weight is a number in a matrix. That's the whole secret.

A "parameter" is one entry in one of the matrices inside the model. A 7B model
has ~7 × 10⁹ of these entries. In FP16, each entry is 2 bytes. 7B × 2 bytes ≈
14 GB — which is exactly why an "8B model" is a ~16 GB file and needs a 24 GB
card to serve with headroom. Every VRAM calculation you'll ever do starts from
this multiplication. (Module 3 builds the full formula.)

## Where the matrices live: anatomy of a transformer

Every layer of the model contains the same small set of matrices. For a model
with hidden size `d` (e.g., 4096):

| Component | Shape | What it does |
|---|---|---|
| Embedding table | `vocab × d` | token ID → vector |
| Attention Q, K, V projections | `d × d` each | build queries/keys/values (lesson 100) |
| Attention output projection | `d × d` | mixes head outputs |
| MLP up/down projections | `d × 4d` and `4d × d` | per-token thinking |
| LayerNorm | `d` (vectors) | keep activations stable |
| LM head | `d × vocab` | final vector → next-token logits |

Multiply those shapes out for a 32-layer, d=4096, 32k-vocab model and you land
within spitting distance of the published parameter count. Doing this arithmetic
once by hand is worth an hour of reading model cards forever.

Two observations with big consequences:

- **The MLP blocks hold most of the parameters** (the 4x expansion). When
  people say fine-tuning "updates knowledge," they mostly mean nudging MLPs.
- **The same weight matrices are used for every token.** The model is one
  function, not a pile of rules. LoRA works because behavior changes can be
  expressed as *low-rank edits* to these matrices (Module 5).

## What the values look like

Not mystical — small floats, mostly:

```
W[0,0] =  0.0131    W[0,1] = -0.0087    W[0,2] =  0.0202 ...
```

Typical magnitudes ~0.001–0.1, roughly symmetric around zero, initialized
randomly at birth. Training then carves structure into them: directions in
weight space corresponding to syntax, facts, style, code idioms. Remarkably,
simple linear directions for interpretable concepts have been found in these
spaces — but there is no line you can grep. The structure is real and
statistical, not symbolic.

## The formats you'll ship

A model file = architecture metadata + the numbers, stored per-tensor:

| Format | Precision | Bytes/param | Notes |
|---|---|---|---|
| FP32 | 32-bit float | 4 | training, rarely serving |
| BF16 / FP16 | 16-bit | 2 | the serving default |
| INT8 | 8-bit int | 1 | quantized, ~2x smaller |
| INT4 (GPTQ/AWQ) | 4-bit | 0.5 | QLoRA base, budget serving |

Quantization (Module 3) = re-encoding these numbers at lower precision with
minimal quality loss. LoRA (Module 5) = freezing the big matrices and training
tiny additive ones. Both only make sense with today's concrete picture:

- The model **is** a folder of named tensors (`model.layers.12.mlp.up_proj.weight`...)
- You can load it, inspect shapes, and do arithmetic on any of them

## Touch one

```python
# pip install transformers torch
from transformers import GPT2LMHeadModel
m = GPT2LMHeadModel.from_pretrained("gpt2")
for name, p in list(m.named_parameters())[:6]:
    print(f"{name:55s} {tuple(p.shape)}")
# wte.weight                    (50257, 768)   <- embedding table
# wpe.weight                    (1024, 768)    <- position table
# h.0.ln_1.weight               (768,)
# h.0.attn.c_attn.weight        (768, 2304)    <- QKV in one matrix
# ...
sum(p.numel() for p in m.parameters())   # 124,439,808 — the "124M"
```

Twelve lines, and "the weights" is now a thing you have inspected, not heard about.

## Check yourself

1. Estimate the file size of a 13B model in FP16 and in INT4. Which fits on a
   16 GB GPU with 4 GB of headroom?
2. Why does the MLP `4d` expansion dominate parameter count, and what does that
   imply about where LoRA adapters are usually attached?
3. Your framework reports a loaded model using 9.5 GB, but the file is 16 GB.
   Give two plausible explanations (hint: precision, and what `from_pretrained`
   does with memory mapping).

Next: [090 — The transformer block in one diagram](090-the-transformer-block-in-one-diagram.md)
