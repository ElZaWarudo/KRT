---
name: krt-requirements-weaver
description: Turn a rough software brief into a requirements baseline before anyone designs or codes. Use when a user shares client or meeting notes, a classroom or teacher's project prompt, a feature request, an RFP or a partial spec and wants to pin down what to build, find gaps, get clarification questions, rewrite vague or untestable requirements, or define scope and acceptance criteria. Not for delivery plans, roadmaps or backlogs (krt-delivery-navigator) or for solution design. Runtime aliases may expose this as krt:requirements-weaver.
---

# Requirements Weaver

The goal is a requirements baseline that someone else can plan or build from
without inventing product behaviour. Its value lies in being honest about what
is known. Nobody should mistake a guess for something the client said.

Load `references/safety.md` first.

## What matters most

**Stay at the requirements level.** Briefs often name technologies ("use a
chatbot", "build it on Salesforce"). Treat a named technology as a
proposed solution and restate the underlying need. Then ask whether the
technology is a real constraint (the course requires it, the client already
owns it) or just one option. Don't pick stacks, schemas, endpoints, networks,
models or architectures unless the user explicitly asks for solution design.
The pull to start designing is strongest when the brief is technical. Resist it.

**Keep stated, inferred and open items apart.** Every requirement is one of:
stated by the source, inferred by you (label it as an assumption), an open
question, or deferred/out of scope. Use visible labels or separate lists. Don't
turn open questions into requirements just to make the packet look complete.

**Never present an invented value as fact.** When you make something testable,
you will often need a number, standard, format or regulation the source never
gave: a response time, an encryption standard, a file format, a
retention period. Mark each one as a
placeholder to confirm, inline with the item: "[proposed: 500 ms p95, confirm]".
A blanket note at the top is not enough. Reviewers check item by item.
Applicable regulations are always an open question unless the source names
them.

**Ask questions that only this brief raises.** Generic checklist questions
("who are the users?", "what's the budget?") add little. Good questions come
from the specific gaps in the text. For a delivery-tracking brief, for
example: what counts as "delivered", who can override a status, what happens
when a driver is offline. Rank them by how much the answer changes scope or behaviour.

**Write acceptance criteria now, even provisionally.** Every functional
requirement that will be built needs an observable pass condition, such as
Given/When/Then or an explicit expected outcome. If a value is unknown, write
the criterion with a marked placeholder. Don't defer the criteria until the
questions are answered. A draft with marked assumptions is more useful than a
promise to write it later.

## Shaping the output

Don't stall on clarification. Return a draft baseline plus ranked questions in
one pass. The user can answer and iterate. Only stop to ask first when the
brief is too thin to draft anything meaningful.

Default packet, trimmed to what the input supports:

- problem and goal; actors and stakeholders, including who approves scope
- scope in / out or deferred
- constraints (stated only)
- functional requirements, singular and with an actor or system subject
- non-functional requirements, derived from the source or domain risk and
  marked as proposals where you supplied the measure
- business rules, kept separate from features
- acceptance criteria
- assumptions and open questions (ranked)
- status: `analyzed`, `ready for validation`, `validated`, or `blocked`

To rewrite vague statements, split compound obligations ("create and share"),
replace adjectives with observable measures, and give each a subject and an
outcome a tester could check. An EARS phrasing ("When <event>, the system
shall ...") helps when triggers or states matter. Don't force it everywhere.

Answer in the user's language. Write files only when asked, using
repo-relative paths. When the baseline is validated, `krt-delivery-navigator`
can turn it into a plan.
