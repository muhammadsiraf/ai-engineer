# The tool-calling protocol

**Reading time:** ~7 min · Module 8

Tool use is a trained behavior, not magic: the model has learned to
emit structured "call this function with these arguments" output when
tools are in scope. Your harness validates the call, executes it, and
returns the result as a new message. The model never runs anything —
it *asks*, and your code *does*. That split is the security boundary
and the debugging boundary.

## Anatomy of a tool

```python
{
  "name": "get_order_status",
  "description": "Look up an order by ID. Use for 'where is my
    order' questions. Do NOT use for refunds — use refund_order.",
  "parameters": {
    "type": "object",
    "properties": {
      "order_id": {"type": "string"},
      "include_tracking": {"type": "boolean", "default": false}
    },
    "required": ["order_id"]
  }
}
```

The description is a prompt (lesson 050): it says what the tool does,
*when to reach for it*, and — often most valuable — when not to.
The schema is a contract: flat, typed, enums over free text wherever
possible, so validation catches the model's bad guesses before they
become runtime errors.

## The transcript shape

```
system:    You are a support agent. Tools available: ...
user:      Where is order A-1024?
assistant: tool_call → get_order_status {order_id: "A-1024"}
tool:      {"status": "shipped", "eta": "2026-10-14"}
assistant: Good news — order A-1024 shipped and arrives Oct 14.
```

Each turn appends; the model re-reads the whole transcript every turn
(Module 3's prefix cache is why the growing prefix is affordable).
Errors go back into the transcript too: `tool: {"error": "unknown
order_id"}` — the model can then correct itself, which is why errors
should be *actionable strings*, not exceptions that kill the loop
(lesson 050's error design rule).

## The harness's half of the contract

- **Validate before executing:** JSON-schema check on arguments;
  unknown tool name; missing required fields. Reject with a message
  the model can recover from.
- **Never trust arguments:** `order_id` is user-influenced text that
  will reach your backend — treat it like any untrusted input
  (lesson 110).
- **Determinism where it matters:** tool-routing surfaces get
  temperature 0 (Module 2), same as Module 7's judge setups.
- **Parallel calls:** models may emit several tool calls in one turn;
  execute them all before the next model turn, or you'll feed it a
  half-updated world.

Everything in this module is this loop with better engineering
around it.

## Check yourself

1. Write the description field for a `search_docs` tool in two
   sentences: one for what it does, one for when NOT to use it.
2. The model calls `get_order_status(order_id=1024)` (integer, schema
   says string). What should happen, exactly, in what message?
3. Why is returning `{"error": "..."}` to the model better than
   raising in your harness? When is raising correct anyway?

Next: [030 — The ReAct loop](030-the-react-loop.md)
