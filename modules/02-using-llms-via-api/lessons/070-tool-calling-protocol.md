# Tool calling at the protocol level

**Reading time:** ~6 min · Module 2

Tool calling is the bridge from "text generator" to "system that acts." It
looks magical and is actually a simple, strict protocol: the model never
executes anything — it *requests* a function call as structured output, and
**your code** decides whether and how to run it. Master the protocol here;
Module 8 builds full agents on it.

## The protocol, end to end

```
you → API:     messages + tools=[{name, description, parameters(JSON schema)}]
API → you:     assistant message with tool_calls=[{id, name, arguments(JSON str)}]
you:           validate args → execute the real function → get result
you → API:     append assistant msg + tool result message (role="tool", tool_call_id=...)
API → you:     assistant message, likely natural language using the result
```

Key facts that trip people up:

- **The model emits a *request*, not an action.** `arguments` is a JSON
  *string* (parse it — and expect occasional invalid JSON despite the
  schema constraint).
- **Execution is 100% your job.** Nothing runs on the provider. The model
  can "call" a function that doesn't exist in your registry — you get to
  reject that.
- **The loop is stateless.** The follow-up request must carry the full
  history: the assistant's tool_call message AND the tool result message,
  matched by `tool_call_id`. Forget the tool message and the API errors.
- **One response can request multiple calls.** Execute all (or decide not
  to — see budgets, Module 8) and return one `role="tool"` message per id.

## Declaring a tool well

```python
{
    "type": "function",
    "function": {
        "name": "get_order_status",
        "description": "Look up the shipping status of an order by order ID. "
                       "Use for any question about where an order is.",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string", "description": "e.g. 'A-1042'"},
            },
            "required": ["order_id"],
        },
    },
}
```

The description is the *prompt* for tool selection (lesson 040 applies in
full): say **what it does** and **when to use it**. The single most common
tool-calling bug is a vague description making the model guess between two
similar tools — or never call the right one. Parameter descriptions matter
for argument quality (formats, examples, units).

## The dispatch loop, skeleton

```python
def run_with_tools(messages, registry, max_rounds=3):
    for _ in range(max_rounds):
        resp = client.chat.completions.create(
            model=MODEL, messages=messages, tools=tool_specs(registry))
        msg = resp.choices[0].message
        if not msg.tool_calls:
            return msg.content                      # final natural-language answer
        messages.append(msg)                        # keep the tool_call message
        for call in msg.tool_calls:
            result = registry.safe_execute(call.name, call.arguments)  # try/except!
            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": json.dumps(result)[:8000],   # cap result size!
            })
    raise AgentLoopError("tool rounds exhausted")
```

Every line flagged by a comment is a production incident category: unvalidated
arguments, unhandled exceptions in tools, unbounded result sizes blowing the
context (lesson 100), and loops without budgets. Module 8 hardens all of it.

## Errors belong in the tool result

If the function raises — bad order ID, downstream API down — **don't** crash
and don't hide it: return a tool message like
`{"error": "order_id A-9999 not found"}`. The model reads it and handles it
conversationally ("I couldn't find that order..."). The tool result is the
model's only sensory input about the world; errors are information.

## Tool choice control

`tool_choice` parameter: `"auto"` (model decides — default), `"none"` (text
only), or force a specific tool (deterministic flows: "always call
`extract_fields` here"). Forcing is underrated — it turns the model into a
reliable argument-filler for a fixed pipeline step, which is 80% of what
people want from "agents" in production anyway.

## Security posture, stated early

Tool execution = code execution triggered by model output, conditioned on
user input. The trust chain is: user → model → tool call → **your executor
must re-verify everything** (authz, argument validation, rate limits).
Module 8's guardrails lesson expands this; the habit starts now: treat
`call.arguments` like untrusted user input, because it is.

## Check yourself

1. The model returns a tool call for `delete_user` — a tool you never
   declared. What happened, and what does your registry do?
2. Why must tool results be size-capped before going back in `messages`?
3. In the loop above, why `max_rounds`? What user-visible bug does it prevent?

Next: [080 — Streaming responses](080-streaming-responses.md)
