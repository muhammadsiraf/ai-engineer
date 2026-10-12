# Structured output via JSON mode

**Reading time:** ~6 min · Module 2

The moment an LLM's output feeds code, prose is the enemy. Structured output —
JSON that matches a schema you define — is the interface between the model
and the rest of your system. Done right, it's reliable enough to build on;
done wrong, it's a 3 a.m. pager. Here's the production playbook.

## The three tiers of structure enforcement

**Tier 1 — Ask nicely (prompt-only).** System prompt says "return only JSON,"
few-shot shows the shape. Works ~95–99% of the time on strong models.
Unacceptable in production *alone* — the 1% is a crash.

**Tier 2 — Provider JSON mode / response_format.** Most major APIs accept a
schema (`response_format` with a JSON schema) or at minimum a "JSON only"
switch. Under the hood this is **constrained decoding**: sampling is
restricted to tokens that keep the output syntactically valid against the
schema. This kills syntax errors (trailing commas, fences, prose prefixes)
but — critical nuance — **does not guarantee semantic correctness**. The
model can still put the wrong string in the right string-typed field.

**Tier 3 — Validate + repair on your side.** Parse → validate against your
actual contract (Pydantic) → on failure, one bounded retry with the validation
error fed back. This is the production tier; tiers 1–3 are additive, not
alternatives.

## The Pydantic pattern (the challenge for this lesson)

```python
from pydantic import BaseModel, Field

class TicketTriage(BaseModel):
    category: Literal["billing", "shipping", "product", "other"]
    priority: Literal["low", "medium", "high"]
    confidence: float = Field(ge=0, le=1)
    rationale: str = Field(max_length=200)

def parse_triage(raw: str) -> TicketTriage:
    return TicketTriage.model_validate_json(strip_fences(raw))
```

What validation buys beyond the provider's schema: your contract lives in
*your* code (portable across providers), fields can cross-validate (confidence
range, enum membership, string caps), and failures become typed exceptions
your retry logic can use. Build a `parse_or_retry` wrapper: validate, and on
`ValidationError`, re-ask once with "Your previous output failed validation:
<error>. Return only corrected JSON." One retry fixes the large majority of
near-miss failures; unbounded retries just burn money on hopeless cases.

## Failure taxonomy, so your tests can be specific

| Failure | Looks like | Tier that catches it |
|---|---|---|
| Prose wrapper | "Here's the JSON you asked for: {...}" | strip + parse (Tier 3) |
| Markdown fences | ```json {...} ``` | strip + parse |
| Syntax error | truncated, trailing comma | JSON mode (Tier 2) |
| Schema mismatch | missing key, wrong enum | Pydantic (Tier 3) |
| Semantic garbage | right shape, wrong values | nothing but evals (Module 7) |
| Truncation | cut mid-object | finish_reason check (Module 1 lesson 020) |

The last two deserve emphasis: **no amount of JSON machinery fixes a model
that doesn't know the answer or a budget that cut the output.** Structure
enforcement is plumbing, not truth.

## Schema design tips from the field

- **Enums over free text** wherever the domain allows — `Literal` types are
  your friend; every free-text field is a parsing surface.
- **Cap lengths** (`max_length`): unbounded rationale fields blow token
  budgets and invite rambling.
- **Flat beats deep.** Nested schemas have higher decode-constraint
  complexity and higher model error rates. `{"a": ..., "b": ...}` outperforms
  four levels of nesting.
- **No optional-mania.** Every `| None` field is a coin the model can flip.
  Default to required + an explicit enum sentinel (`"unknown"`).

## Streaming + structured = a real pattern

You can stream JSON and parse at the end — or do partial parsing on the
stream for progressive UI. That's advanced (the provider's chunking doesn't
respect object boundaries); start with buffer-everything-then-parse, and
check `finish_reason` before you do.

## Check yourself

1. JSON mode is on and outputs parse. Name two things that can still be wrong.
2. Your extraction endpoint fails validation on 2% of requests. Design the
   retry policy: what's fed back, how many attempts, and what happens after
   the last one?
3. Rewrite this schema to be model-friendly: `{description: string,
   amount: string|null, date: string|null, notes: string}` for invoice
   extraction.

Next: [070 — Tool calling at the protocol level](070-tool-calling-protocol.md)
