"""Challenge 020 — Size the KV cache.

Lesson: 030/040 — the KV cache formula and the full VRAM budget.

    kv_bytes_per_token = 2 × L × H_kv × d_head × bytes_per_elem
    weights_bytes      = params × bytes_per_param
    kv_pool            = gpu_bytes − weights_bytes − overhead_bytes
    capacity_tokens    = kv_pool ÷ kv_bytes_per_token
    max_concurrent(C)  = floor(kv_pool ÷ (kv_bytes_per_token × C))

Implement class `VRAMBudget`:

  - __init__(layers, kv_heads, d_head, params, gpu_bytes,
             weight_bytes_per_param=2, kv_bytes_per_elem=2,
             overhead_bytes=1_500_000_000)
  - kv_bytes_per_token() -> float
  - weights_bytes() -> int
  - kv_pool_bytes() -> float          (never negative: clamp at 0)
  - capacity_tokens() -> int          (floor)
  - max_concurrent(context_tokens) -> int   (floor; 0 if pool is 0)
  - fits(gpu_bytes=None) -> bool      # weights + overhead <= gpu budget

Reference model (tests encode it):
  Llama-3-8B-ish: layers=32, kv_heads=8, d_head=128, params=8e9,
  FP16 (2 B/param), FP16 KV, overhead 1.5 GB on a 24 GB GPU.

Run:  pytest modules/03-inference-fundamentals/challenges/test_020_size_the_kv_cache.py -v
"""


class VRAMBudget:
    def __init__(
        self,
        layers: int,
        kv_heads: int,
        d_head: int,
        params: float,
        gpu_bytes: float,
        weight_bytes_per_param: int = 2,
        kv_bytes_per_elem: int = 2,
        overhead_bytes: float = 1_500_000_000,
    ):
        self.L = layers
        self.H_kv = kv_heads
        self.d_head = d_head
        self.params = params
        self.gpu_bytes = gpu_bytes
        self.w_bytes = weight_bytes_per_param
        self.kv_bytes = kv_bytes_per_elem
        self.overhead_bytes = overhead_bytes

    def kv_bytes_per_token(self) -> float:
        raise NotImplementedError

    def weights_bytes(self) -> float:
        raise NotImplementedError

    def kv_pool_bytes(self) -> float:
        raise NotImplementedError

    def capacity_tokens(self) -> int:
        raise NotImplementedError

    def max_concurrent(self, context_tokens: int) -> int:
        raise NotImplementedError

    def fits(self, gpu_bytes: float | None = None) -> bool:
        raise NotImplementedError
