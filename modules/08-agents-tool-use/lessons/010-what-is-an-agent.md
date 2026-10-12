# What is an agent?

**Reading time:** ~7 min · Module 8

An agent is a language model in a loop with tools: it decides which
tool to call, sees the result, decides again, and stops when it judges
the goal met. The defining property is *who steers*. In a workflow,
your code fixes the path and the model fills in the steps. In an
agent, the model steers — choosing the order, the tools, and the
stopping point. That transfer of control is the entire feature and the
entire risk.

## The three ingredients

1. **A model** that can emit structured decisions (Module 2's
   structured output is what makes this reliable rather than lucky).
2. **Tools** — functions the model can invoke: search, read a file,
   call an API, run code. Each has a name, a description, and a
   parameter schema (lesson 020).
3. **A loop** — call the model, execute its tool choice, append the
   result, repeat until it answers instead of calling (lesson 030).

Everything else — planning patterns, memory, multi-agent
architectures — is elaboration on that skeleton.

## Workflow, router, agent: the autonomy dial

- **Fixed pipeline:** prompt A → prompt B → done. Your code owns all
  control flow. Cheapest, most predictable, most testable.
- **Router:** the model makes *one* control decision (which branch,
  which specialist — Module 7's classification shapes) and your code
  takes over again.
- **Agent:** the model makes a control decision every turn until
  done. Maximum flexibility on open-ended problems where the step
  sequence can't be known in advance ("research X and draft a memo"),
  maximum variance in cost and path.

Most production "agents" are routers plus pipelines, and that's fine.
Use the least autonomy that solves the problem — each step up the dial
buys coverage of messier tasks and pays in tokens, latency, and
failure modes you don't control (lesson 040).

## When the agent is worth it

The honest test: **can you enumerate the steps?** If yes, write the
pipeline — deterministic paths are cheaper and debuggable. If the
correct sequence depends on what the tools *find* (unknown number of
lookups, branches revealed mid-task), the loop earns its keep. The
second test is economic: an agent run costs multiples of a single
call, so the task needs to be valuable or frequent enough to carry
that (Module 7 lesson 090's unit economics apply per *run*, not per
token).

## Check yourself

1. Your task: "given a refund policy question, look up the customer's
   orders, then answer." Pipeline or agent? What about "figure out
   why this customer is churning and draft a retention offer"?
2. Name the three ingredients and where each can fail.
3. Your team wants "an agent" for a form-filling flow with 6 known
   fields. Argue for the cheaper design that probably wins.

Next: [020 — The tool-calling protocol](020-tool-calling-protocol.md)
