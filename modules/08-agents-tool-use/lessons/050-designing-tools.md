# Designing tools

**Reading time:** ~7 min · Module 8

Tools are APIs whose caller is non-deterministic, reads the
documentation imperfectly, and recovers from errors by *reading the
error*. Every API-design instinct still applies; three adjustments
dominate: fewer and coarser endpoints, descriptions written as
prompts, and errors written as instructions.

## Few, coarse, high-level

A tool per CRUD verb multiplies the model's choices and its chances
of composing them wrong. `create_user`, `set_user_email`,
`set_user_name` lose to `upsert_user(profile)` — one decision instead
of a plan. The model is excellent at filling in a rich argument
object and mediocre at orchestrating five stateful calls in the right
order. Expose *tasks*, not endpoints; your code handles sequencing
inside the tool.

## Descriptions are prompts

The description is the only documentation the model reads at decision
time. It must answer three questions: what it does, **when to use
it**, and **when NOT to use it** (the highest-value line — most
misuse is a near-miss between two tools). Name tools for intent:
`search_orders` beats `query_orders_table_v2`. Keep the parameter
schema flat and typed; enums instead of free text; required fields
explicit. Every parameter the model must invent is a failure surface
(lesson 040's misuse shape).

## Errors are the recovery mechanism

The error string goes back into the transcript as the model's only
signal for its next move. Compare:

- `"Error: E422"` — model guesses, often re-issues the same call
  (thrash).
- `"order_id 'A-999' not found. Valid IDs look like 'A-1234'.
  Call list_orders(customer_id=...) to find valid IDs."` — model
  recovers in one turn.

Write errors as if the model will follow them, because it will.

## Side effects and safety

Split read tools from write tools in *naming and permissions*, not
just implementation. Destructive or irreversible tools get a confirm
gate: the harness pauses for human approval or a scoped token
(lesson 110). Make writes idempotent with client-supplied keys —
retries after timeouts are normal, duplicate $500 refunds are not
(Module 6's reliability discipline applies to tools first).

## Version and test them like code

A tool's schema+description is an artifact: version it, and re-run
the tool-use eval suite when it changes (Module 7 lesson 120 — the
judge-you-back artifact here is the tool spec). Unit-test tools
directly: given a realistic call, does it return results the model
can act on? The challenge builds the validation half of this
contract.

## Check yourself

1. Your agent misuses `search_docs` when it should use
   `get_customer_record`. Rewrite both descriptions' "use when / not
   when" lines to separate them.
2. Why is `upsert_user(profile)` safer for an agent than three
   granular setters — give two reasons.
3. Design the error string for a rate-limited tool so the model's
   next move is correct and cheap.

Next: [060 — Budgets and step limits](060-budgets-and-step-limits.md)
