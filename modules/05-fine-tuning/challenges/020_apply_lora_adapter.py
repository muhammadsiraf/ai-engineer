"""Challenge 020 — Apply a LoRA adapter.

Lesson: 030 — the decomposition, computed by hand in pure Python.

    h = W₀x + (α/r) · B(Ax)

    W₀: d×d (frozen)      A: r×d (down)      B: d×r (up)

Implement (lists of lists, row-major; pure Python):

  - matvec(W, x) -> list[float]          # W @ x
  - apply_lora(W0, A, B, alpha, r, x) -> list[float]
  - merge(W0, A, B, alpha, r) -> list[list[float]]
        W₀ + (α/r)·B@A

Properties the tests encode:
  - B all zeros  → apply_lora == W₀x          (training starts AT the base)
  - merge(W0,...) @ x == apply_lora(W0,...,x) (folding in is exact)
  - doubling alpha doubles the delta, leaves W₀x untouched
  - shape errors raise ValueError

Run:  pytest modules/05-fine-tuning/challenges/test_020_apply_lora_adapter.py -v
"""


def matvec(W: list, x: list) -> list[float]:
    raise NotImplementedError


def apply_lora(
    W0: list, A: list, B: list, alpha: float, r: int, x: list
) -> list[float]:
    raise NotImplementedError


def merge(W0: list, A: list, B: list, alpha: float, r: int) -> list[list[float]]:
    raise NotImplementedError
