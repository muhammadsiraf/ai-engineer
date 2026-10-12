"""Challenge 010 — Count LoRA trainable parameters.

Lesson: 030 — LoRA in one decomposition.

One target matrix W ∈ ℝ^{d×d}:

    full update:  d² trainable params
    LoRA:         2 · r · d          (A: r×d down, B: d×r up)

Model-wide, with T target matrices per layer (e.g. q,k,v,o + gate,up,down
→ T=7):

    full:  n_layers · T · d²
    lora:  n_layers · T · 2·r·d

Implement (pure Python):

  - lora_param_count(d, r) -> int
  - full_param_count(d) -> int
  - model_param_counts(d, n_layers, r, targets) -> tuple[int, int]
        returns (full_total, lora_total) — targets = T per layer
  - compression_ratio(d, n_layers, r, targets) -> float
        full_total / lora_total

Reference numbers (tests encode them):
    d=4096, r=16 → 131,072 LoRA params per matrix vs 16,777,216 full
    (a 128x reduction) — lesson 030's headline.

Run:  pytest modules/05-fine-tuning/challenges/test_010_count_lora_params.py -v
"""


def lora_param_count(d: int, r: int) -> int:
    raise NotImplementedError


def full_param_count(d: int) -> int:
    raise NotImplementedError


def model_param_counts(d: int, n_layers: int, r: int, targets: int) -> tuple[int, int]:
    raise NotImplementedError


def compression_ratio(d: int, n_layers: int, r: int, targets: int) -> float:
    raise NotImplementedError
