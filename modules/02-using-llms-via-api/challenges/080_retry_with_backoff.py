"""Challenge 080 — Implement retry with backoff.

Lesson: 130-rate-limits-retries-and-idempotency

The production retry policy, fully specified and testable:

    on retryable error:  delay = min(base * 2**attempt + jitter(), cap)
    honor Retry-After if the error carries one (use the LARGER of the two)
    stop after max_retries total attempts; re-raise the last error

Implement:

  class RateLimitError(Exception): retryable, carries optional retry_after
  class ServerError(Exception):    retryable, no retry_after
  class BadRequest(Exception):     NOT retryable

  def is_retryable(e) -> bool

  def call_with_retry(fn, *, max_retries=3, base=0.5, cap=8.0,
                      sleep=time.sleep, jitter=lambda d: 0.0) -> Any
      - fn() on success returns its value immediately.
      - BadRequest propagates immediately (no sleep, no retry).
      - Retryable errors sleep(base * 2**attempt + jitter(delay)) capped at
        `cap`; if the error has retry_after, sleep max(computed, retry_after).
      - attempt numbering starts at 0; total attempts = max_retries + 1.
      - After the final attempt, re-raise the last error.
      - `sleep` and `jitter` are injectable for tests (jitter takes the
        uncapped delay and returns the extra amount to add).

Run:  pytest modules/02-using-llms-via-api/challenges/test_080_retry_with_backoff.py -v
"""

import time


class RateLimitError(Exception):
    def __init__(self, message: str = "", retry_after: float | None = None):
        super().__init__(message)
        self.retry_after = retry_after


class ServerError(Exception):
    pass


class BadRequest(Exception):
    pass


def is_retryable(e: BaseException) -> bool:
    raise NotImplementedError


def call_with_retry(
    fn,
    *,
    max_retries: int = 3,
    base: float = 0.5,
    cap: float = 8.0,
    sleep=time.sleep,
    jitter=lambda delay: 0.0,
):
    raise NotImplementedError
