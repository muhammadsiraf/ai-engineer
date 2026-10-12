"""Challenge 030 — Typed output with Pydantic.

Lesson: 060-structured-output-json-mode

Production tier of structured output: parse -> validate -> one repair retry.
Implement `parse_triage(raw)` and `parse_with_retry(call_fn)`.

The schema (TicketTriage) is given. Your job:

  1. strip_fences(raw) — remove markdown code fences and any prose before/
     after the JSON object. Accept both ```json fences and bare JSON.
  2. parse_triage(raw) -> TicketTriage — strip, parse, validate. Raise
     pydantic.ValidationError on schema violations and json.JSONDecodeError
     on unparseable text (after stripping).
  3. parse_with_retry(call_fn, max_attempts=2) — call_fn(feedback: str | None)
     invokes the LLM; on the first attempt feedback is None; on retry, pass
     a feedback string containing the validation error. Return the first
     valid TicketTriage; re-raise the last error after exhausting attempts.

If pydantic is unavailable in your environment, a minimal stub is NOT
provided — install it (it's in requirements for Module 2+ work: the point
of this challenge is real validation).

Run:  pytest modules/02-using-llms-via-api/challenges/test_030_typed_output_pydantic.py -v
"""

from typing import Callable, Literal

from pydantic import BaseModel, Field


class TicketTriage(BaseModel):
    category: Literal["billing", "shipping", "product", "other"]
    priority: Literal["low", "medium", "high"]
    confidence: float = Field(ge=0.0, le=1.0)
    rationale: str = Field(max_length=200)


def strip_fences(raw: str) -> str:
    """Return only the JSON object substring of `raw`.

    Handles: bare JSON, ```json ...``` fences, prose around the object.
    Implementation hint: find the first '{' and the LAST '}'.
    """
    raise NotImplementedError


def parse_triage(raw: str) -> TicketTriage:
    raise NotImplementedError


def parse_with_retry(
    call_fn: Callable[[str | None], str],
    max_attempts: int = 2,
) -> TicketTriage:
    raise NotImplementedError
