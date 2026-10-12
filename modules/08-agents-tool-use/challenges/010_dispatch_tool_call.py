"""Challenge 010 — Dispatch a tool call.

Lesson: 020 — the harness's half of the tool-calling contract.

    the model asks; your code validates, executes, and reports.
    validation failures and unknown tools go back to the model as
    {"ok": False, "error": <actionable string>} — never as exceptions
    that kill the loop. the error string is the model's recovery path.

JSON-schema subset to support:
    parameters: {"properties": {name: {"type": "string"|"integer"|
                 "number"|"boolean", optional "enum": [...]}},
                 "required": [names]}

Implement (pure Python):

  - validate_args(spec, args) -> None
        raises ValueError with a message that names the offending
        argument; checks in order: unknown arguments, missing
        required, type, enum membership
        (bool is NOT an integer — Python's subclassing is a trap)
  - dispatch(registry, call) -> dict
        registry: {name: (spec, fn)};  call: {"name", "arguments"}
        → {"ok": True, "result": fn(**args)}
        → {"ok": False, "error": msg} for an unknown tool or any
          validation failure — the function is never called then
  - dispatch_all(registry, calls) -> list[dict]
        every call executed independently; one failure does not stop
        the rest (parallel tool calls land together)

Reference (tests encode them):
    get_order_status(order_id: string, required; units: enum [c, f])
    dispatch(registry, {"name": "get_order_status",
                        "arguments": {"order_id": "A-1024"}})
      → {"ok": True, "result": "order A-1024: shipped"}

Run:  pytest modules/08-agents-tool-use/challenges/test_010_dispatch_tool_call.py -v
"""


def validate_args(spec: dict, args: dict) -> None:
    raise NotImplementedError


def dispatch(registry: dict, call: dict) -> dict:
    raise NotImplementedError


def dispatch_all(registry: dict, calls: list[dict]) -> list[dict]:
    raise NotImplementedError
