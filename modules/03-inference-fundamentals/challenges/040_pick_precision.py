"""Challenge 040 — Pick the precision that fits.

Lesson: 080 — quantization (and 090 for the format axes).

The decision rule from the lesson:

    Ship the smallest precision whose worst-case quality drop is within
    product tolerance — not the best average.

Given candidate precisions, a model size, and a GPU budget:

    fits        : weights + overhead <= gpu_bytes
                  where weights = params × bytes_per_param
    acceptable  : fits AND quality_drop_pct <= max_quality_drop_pct
    pick        : acceptable option with the SMALLEST bytes_per_param
                  (tie → the higher speedup); None if nothing qualifies

Implement:

  - dataclass `PrecisionOption(name, bytes_per_param, quality_drop_pct,
    speedup)`  — speedup = decode speed vs FP16 on the same hardware
  - `weights_bytes(params, bytes_per_param) -> float`
  - `pick_precision(options, params, gpu_bytes, overhead_bytes=1.5e9,
    max_quality_drop_pct=2.0) -> PrecisionOption | None`

What would you measure to confirm the pick in real life? (Answer in prose,
not code: golden-set quality per category, VRAM, TTFT/TPS — the lesson's
step 2 sweep.)

Run:  pytest modules/03-inference-fundamentals/challenges/test_040_pick_precision.py -v
"""

from dataclasses import dataclass


@dataclass
class PrecisionOption:
    name: str
    bytes_per_param: float
    quality_drop_pct: float
    speedup: float


def weights_bytes(params: float, bytes_per_param: float) -> float:
    raise NotImplementedError


def pick_precision(
    options: list,
    params: float,
    gpu_bytes: float,
    overhead_bytes: float = 1_500_000_000,
    max_quality_drop_pct: float = 2.0,
) -> PrecisionOption | None:
    raise NotImplementedError
