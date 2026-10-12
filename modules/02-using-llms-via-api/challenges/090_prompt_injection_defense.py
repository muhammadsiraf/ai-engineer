"""Challenge 090 — Defend against prompt injection.

Lesson: 160-prompt-injection-the-threat-model

Layered defenses as pure functions — the layer that actually catches things
is validation and fencing, so that's what you build:

  1. fence_content(text, source_label) -> str
     Wrap untrusted text in delimiters + provenance + instruction.
       Format:
         <untrusted source="{label}">
         {text}
         </untrusted>
  2. scan_content(text) -> list[str]
     Heuristic injection scanner: return a list of flags (empty = clean).
     Flag (case-insensitive) if the text contains, as a substring:
       - "ignore previous instructions"
       - "ignore all instructions"
       - "disregard the above"
       - "reveal your system prompt"
       - "you are now" (role reassignment attempts)
     Each flag is the matched phrase, lowercased, in match order of the
     SCAN_PATTERNS list.
  3. validate_tool_args(schema, args) -> list[str]
     Structural validation of tool arguments (returns error list, empty=ok):
       - required keys present
       - no unexpected keys
       - type check for "string", "number", "boolean" properties
       - (recursion into nested objects NOT required)
  4. safe_tool_execute(registry, name, args_json, call_id, allowed: set)
     Like Module 2's safe_execute, PLUS: the tool must be in `allowed`
     (least privilege) and scan_content must find nothing in the RAW args
     string. Violations return an error entry, never raise.

Run:  pytest modules/02-using-llms-via-api/challenges/test_090_prompt_injection_defense.py -v
"""

import json
from typing import Any, Callable


SCAN_PATTERNS = [
    "ignore previous instructions",
    "ignore all instructions",
    "disregard the above",
    "reveal your system prompt",
    "you are now",
]


def fence_content(text: str, source_label: str) -> str:
    raise NotImplementedError


def scan_content(text: str) -> list[str]:
    raise NotImplementedError


def validate_tool_args(schema: dict, args: dict) -> list[str]:
    """schema: {"type":"object","properties":{name:{"type":...}}, "required":[...]}"""
    raise NotImplementedError


def safe_tool_execute(
    registry: dict[str, tuple[Callable[..., Any], dict]],
    name: str,
    args_json: str,
    call_id: str,
    allowed: set[str],
) -> dict:
    """Returns {"tool_call_id", plus exactly one of "result"/"error"}."""
    raise NotImplementedError
