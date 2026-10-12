"""Challenge 050 — Estimate cost with a tokenizer.

Lesson: 090-token-counting-before-you-call

Pre-flight counting: messages + per-message overhead + tool overhead ->
tokens -> dollars. To keep this challenge runnable offline, the tokenizer is
INJECTABLE: anything with `encode(text) -> list[int]`. Tests use a
deterministic fake; in production you'd pass a tiktoken or HF tokenizer.

Implement `CostEstimator`:

  - __init__(tokenizer, models: dict[str, ModelConfig])
      ModelConfig has: input_price_per_m, output_price_per_m,
      context_limit, msg_overhead (default 4), tool_overhead (default 8).
  - count_message(msg) -> int       # len(encode(content)) + msg_overhead
  - count_request(messages, tools=None) -> int
      # sum of count_message + tool_overhead per tool + per-model-indep base 3
  - fits(messages, model, max_output_tokens) -> bool
      # count_request + max_output_tokens <= context_limit
  - estimate_cost(model, in_tokens, out_tokens) -> float   # dollars
  - quote(messages, model, expected_output_tokens) -> dict:
      {"input_tokens", "output_tokens", "cost_usd", "fits"}

Raise KeyError on unknown model names. All money math in float, rounded to
6 decimals at the END (not during).

Run:  pytest modules/02-using-llms-via-api/challenges/test_050_cost_estimator_tiktoken.py -v
"""

from dataclasses import dataclass, field
from typing import Any, Protocol


class Tokenizer(Protocol):
    def encode(self, text: str) -> list[int]: ...


@dataclass
class ModelConfig:
    input_price_per_m: float
    output_price_per_m: float
    context_limit: int
    msg_overhead: int = 4
    tool_overhead: int = 8


@dataclass
class FakeTokenizer:
    """Deterministic offline tokenizer: 1 token per 4 chars. For tests."""

    def encode(self, text: str) -> list[int]:
        return [0] * (len(text) + 3) // 4  # noqa: PLR2004 — keep floor behavior


MODELS = {
    "flagship": ModelConfig(3.0, 15.0, 128_000),
    "mini": ModelConfig(0.15, 0.6, 16_000),
}


class CostEstimator:
    def __init__(self, tokenizer: Tokenizer, models: dict[str, ModelConfig]):
        self.tok = tokenizer
        self.models = models

    def count_message(self, msg: dict) -> int:
        raise NotImplementedError

    def count_request(self, messages: list[dict], tools: list[Any] | None = None) -> int:
        raise NotImplementedError

    def fits(self, messages: list[dict], model: str, max_output_tokens: int) -> bool:
        raise NotImplementedError

    def estimate_cost(self, model: str, in_tokens: int, out_tokens: int) -> float:
        raise NotImplementedError

    def quote(
        self, messages: list[dict], model: str, expected_output_tokens: int
    ) -> dict:
        raise NotImplementedError
