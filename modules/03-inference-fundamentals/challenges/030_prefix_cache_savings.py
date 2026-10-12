"""Challenge 030 — Count the prefill you save.

Lesson: 070 — prefix caching.

Engines reuse KV state only for *exact, contiguous, block-aligned* prefixes.
Your job: quantify what a shared prefix saves, at block granularity.

    cacheable_prefix      = floor(prefix_tokens / block_size) * block_size
    prefill per request
      cold (no cache)     = prefix_tokens + novel_tokens
      warm (steady state) = (prefix + novel) − cacheable_prefix
    totals over N requests
      uncached            = N × cold
      cached              = cold + (N−1) × warm     (request 1 is always a miss)
    savings_fraction      = 1 − cached_total / uncached_total

Implement class `PrefixCacheSavings`:

  - __init__(prefix_tokens, novel_tokens, num_requests, block_size=1)
  - cacheable_prefix_tokens() -> int
  - prefill_tokens_uncached() -> int        (one cold request)
  - prefill_tokens_cached() -> int          (one warm request, steady state)
  - total_prefill_uncached() -> int
  - total_prefill_cached() -> int
  - savings_fraction() -> float             (0.0 when num_requests <= 1)
  - ttft_seconds(prefill_tok_per_s, warm) -> bool->float
        warm=False → cold prefill time; warm=True → steady-state time.
        Raise ValueError if rate <= 0.

Reference scenario (tests encode it):
  system+tools prefix 1,800 tokens on EVERY request, 400 novel tokens,
  10,000 requests → prefill work drops ~82% (0.818 to be exact).

Run:  pytest modules/03-inference-fundamentals/challenges/test_030_prefix_cache_savings.py -v
"""


class PrefixCacheSavings:
    def __init__(
        self,
        prefix_tokens: int,
        novel_tokens: int,
        num_requests: int,
        block_size: int = 1,
    ):
        self.prefix_tokens = prefix_tokens
        self.novel_tokens = novel_tokens
        self.num_requests = num_requests
        self.block_size = block_size

    def cacheable_prefix_tokens(self) -> int:
        raise NotImplementedError

    def prefill_tokens_uncached(self) -> int:
        raise NotImplementedError

    def prefill_tokens_cached(self) -> int:
        raise NotImplementedError

    def total_prefill_uncached(self) -> int:
        raise NotImplementedError

    def total_prefill_cached(self) -> int:
        raise NotImplementedError

    def savings_fraction(self) -> float:
        raise NotImplementedError

    def ttft_seconds(self, prefill_tok_per_s: float, warm: bool) -> float:
        raise NotImplementedError
