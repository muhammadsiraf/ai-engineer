# Self-attention in five minutes

**Reading time:** ~6 min · Module 1

Attention is the transformer's core operation. It has a reputation for being
mathy, but for an engineer it's a retrieval mechanism you already know from
databases — queries, keys, and a soft sort of lookup. This lesson builds it in
three moves; the challenge has you implement it from scratch.

## Move 1: every token gets three vectors

From each token's embedding `x` (a row of the residual stream), three linear
projections produce:

- **Query (Q):** "what am I looking for?"
- **Key (K):** "what do I contain / advertise?"
- **Value (V):** "what I'll hand over if you attend to me"

```python
Q = X @ Wq   # (n, d) @ (d, dk) -> (n, dk)
K = X @ Wk   # (n, dk)
V = X @ Wv   # (n, dk)
```

All n tokens get all three. (In real models one fused matrix produces Q, K, V
in a shot — lesson 080 showed the `(768, 2304)` matrix.)

## Move 2: scores = every query against every key

Token `i` asks: how relevant is token `j` to me? Dot product of i's query with
j's key. Doing it for all pairs:

```python
scores = Q @ K.T          # (n, n)  — the relevance matrix
scores = scores / sqrt(dk)  # scale down: keeps softmax from saturating
```

The `1/sqrt(dk)` scaling is not cosmetic. Dot products of high-dimensional
random vectors have variance ~dk; without dividing, scores get large, softmax
outputs saturate to one-hot, and gradients die. The formula
`softmax(QKᵀ/√dk)` is the single most quotable line in deep learning — now
you know what each piece is for.

## Move 3: soft lookup over values

Turn each row of scores into a probability distribution (softmax), and mix the
values accordingly:

```python
A = softmax(scores, dim=-1)   # (n, n) — each row sums to 1
out = A @ V                   # (n, dk) — each token's new vector
```

Token `i`'s output = weighted average of all tokens' V vectors, weighted by
relevance to i. If row `i` of A is `[0.7 on j, 0.2 on k, 0.1 elsewhere]`, then
i's new vector is 70% j's value + 20% k's value + ....

## The database analogy, made precise

| DB concept | Attention equivalent |
|---|---|
| query | Q vector of the asking token |
| index keys | K vectors of all tokens |
| matching | dot product (a *soft*, graded match) |
| returned record | V vectors, mixed in proportion to match strength |

A database returns the best match, hard. Attention returns a **weighted blend
of everything**, softly. That softness is what makes the whole thing
differentiable — gradients flow through the mixing weights, which is what makes
training it possible (lesson 070's loop needs every operation to be smooth).

## What it buys you, concretely

In "The animal that fetches sticks is a **dog** because it is loyal," the token
`dog` can attend strongly back to `animal` (for referent) and `fetches` (for
role). After attention, `dog`'s vector literally contains contributions from
those tokens' values — context is *mechanically injected into the vector*, not
remembered somewhere off to the side. This is the answer to "where does the
model keep the conversation?" It doesn't keep it; every token's representation
is a weighted compilation of everything before it.

## Cost, and the catch

The `QKᵀ` step builds an `n × n` matrix — quadratic in sequence length. This
one line is why context is expensive (lesson 050), why KV caching exists
(Module 3), and why every "efficient attention" paper of the last five years is
an attempt to avoid materializing that matrix. Attention is simultaneously the
source of the transformer's power and its bill.

## Check yourself

1. Why must softmax be applied row-wise (per query), not over the whole matrix?
2. If row `i` of the attention matrix were exactly uniform, what would token
   i's output be? What would that mean functionally?
3. Where does the sequence-length quadratic cost come from in the code above —
   which line, and which shape?

Next: [110 — Why attention is causal at inference time](110-why-attention-is-causal-at-inference-time.md)
