"""Challenge 040 — Make the model call a tool.

Lesson: 070-tool-calling-protocol

Implement the dispatch side of the tool protocol against a mock model that
emits tool_call requests (see MockToolModel). You build the registry and the
executor — the part that MUST be safe, because it's the part that acts.

  1. ToolRegistry: register(name, fn, schema) / get / specs.
     - `specs()` returns provider-style tool definitions.
     - Duplicate registration raises ValueError.
  2. safe_execute(name, arguments_json, call_id) -> dict for the tool
     message, with EXACTLY one of:
        {"tool_call_id": ..., "result": <fn return, JSON-serializable>}
        {"tool_call_id": ..., "error": "<message>"}
     - Unknown tool name -> error entry (never raise).
     - Invalid JSON arguments -> error entry.
     - Arguments not matching the registered schema -> error entry
       (validate: required keys present, no unexpected keys, types match).
     - fn raising -> error entry with str(e).
     - Arguments are validated BEFORE fn runs.
  3. run_loop(client, registry, messages, max_rounds=3) -> final string:
     call client.complete(messages); if it returns a ToolCall, execute via
     safe_execute, append the assistant tool_call message AND the tool
     message, and continue; else return the text. Raise RuntimeError if
     max_rounds tool rounds are exhausted.

Run:  pytest modules/02-using-llms-via-api/challenges/test_040_tool_call_dispatch.py -v
"""

import json
from typing import Any, Callable


class ToolCall:
    """What a 'model' returns when it wants a function. Provided."""

    def __init__(self, call_id: str, name: str, arguments_json: str):
        self.id = call_id
        self.name = name
        self.arguments_json = arguments_json


class MockToolModel:
    """Scripted 'model'. Provided; do not modify.

    complete(messages) pops the next item from its script: a str = final
    answer; a ToolCall = a tool request. Records everything it was sent in
    `.history`.
    """

    def __init__(self, script: list):
        self.script = list(script)
        self.history: list[list[dict]] = []

    def complete(self, messages: list[dict]):
        self.history.append(messages)
        return self.script.pop(0)


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, tuple[Callable[..., Any], dict]] = {}

    def register(self, name: str, fn: Callable[..., Any], schema: dict) -> None:
        """schema: {"type":"object","properties":{...},"required":[...]}
        Types checked: string, number, boolean. (Keep it small; that's the point.)"""
        raise NotImplementedError

    def get(self, name: str) -> Callable[..., Any] | None:
        raise NotImplementedError

    def specs(self) -> list[dict]:
        """Provider-style: [{"type":"function","function":{"name":...,
        "parameters":<schema>}}] — descriptions optional."""
        raise NotImplementedError

    def safe_execute(self, name: str, arguments_json: str, call_id: str) -> dict:
        raise NotImplementedError


def run_loop(
    client: MockToolModel,
    registry: ToolRegistry,
    messages: list[dict],
    max_rounds: int = 3,
) -> str:
    raise NotImplementedError
