"""Challenge 010 — Time a request.

Lesson: 020-prefill-and-decode

Build the two-phase latency model from lesson 020 and calibrate it from
measurements. This is the arithmetic behind every latency budget you'll write.

    total = queue + prefill + steps × decode_step
    prefill(n_in)  = k1 × n_in          (compute-bound: ~linear in tokens)
    decode         = k2 per token       (bandwidth-bound: ~constant per token)

Implement class `LatencyModel`:

  - __init__(queue_s=0.0)
  - calibrate(measurements) — measurements is a list of dicts with keys
    {"input_tokens", "output_tokens", "total_s"}; fit k1 and k2 by least
    squares over: total = queue + k1*in + k2*out  (assume queue known).
    Set self.k1, self.k2.
  - predict(input_tokens, output_tokens) -> dict with keys
    "ttft_s" (queue + prefill), "decode_s", "total_s".
  - report(measurements) -> dict of max absolute prediction error:
    {"ttft_max_err_s", "total_max_err_s"} using predicted totals vs actuals.

All floats; no rounding until the return values.

Run:  pytest modules/03-inference-fundamentals/challenges/test_010_time_a_request.py -v
"""

from typing import Any


class LatencyModel:
    def __init__(self, queue_s: float = 0.0):
        self.queue_s = queue_s
        self.k1: float | None = None  # seconds per input token
        self.k2: float | None = None  # seconds per output token

    def calibrate(self, measurements: list[dict[str, float]]) -> None:
        """Least-squares fit of k1, k2 (closed form for 2 unknowns).

        Hint: minimize sum((y - k1*a - k2*b)^2); solve the 2x2 normal
        equations. You may use numpy or plain Python.
        """
        raise NotImplementedError

    def predict(self, input_tokens: float, output_tokens: float) -> dict[str, float]:
        raise NotImplementedError

    def report(self, measurements: list[dict[str, float]]) -> dict[str, float]:
        raise NotImplementedError
