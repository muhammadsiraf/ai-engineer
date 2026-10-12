"""Challenge 030 — Budget VRAM for QLoRA.

Lesson: 050 — QLoRA (and 020 for the full-FT comparison).

Byte conventions (tests encode them):

    QLoRA base (NF4):                0.5 bytes per param
    Full fine-tuning (Adam, mixed):  16 bytes per param
        4 master + 4 gradient + 8 optimizer (m, v)
    LoRA adapter per TRAINABLE param:
        2 (BF16 weights) + 4 (FP32 grads) + 8 (Adam) = 18 bytes

Implement:

  - qlora_base_bytes(params) -> float
  - adapter_train_bytes(trainable) -> float
  - full_ft_bytes(params) -> float
  - qlora_total_bytes(params, trainable, activation_bytes) -> float
        base + adapter + activations
  - vram_ratio(params, trainable, activation_bytes) -> float
        full_ft_bytes / qlora_total_bytes

Reference numbers (tests encode them):
    7B model, ~29.4M trainable adapters, 2 GB activations
      → QLoRA total ≈ 3.5 GB base + 0.53 GB adapters + 2 GB ≈ 6.03 GB
      → full FT = 112 GB → ratio ≈ 18.6x

Run:  pytest modules/05-fine-tuning/challenges/test_030_qlora_vram_budget.py -v
"""


def qlora_base_bytes(params: float) -> float:
    raise NotImplementedError


def adapter_train_bytes(trainable: float) -> float:
    raise NotImplementedError


def full_ft_bytes(params: float) -> float:
    raise NotImplementedError


def qlora_total_bytes(params: float, trainable: float, activation_bytes: float) -> float:
    raise NotImplementedError


def vram_ratio(params: float, trainable: float, activation_bytes: float) -> float:
    raise NotImplementedError
