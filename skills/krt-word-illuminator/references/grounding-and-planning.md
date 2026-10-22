# Grounding and planning

## Content states

Every factual block in a request carries a provenance state:

| State | Meaning | Treatment |
|---|---|---|
| `source` | Supported by an inspected source | Name one or more source IDs |
| `user` | Explicitly supplied by the user | Preserve meaning |
| `inference` | Reasoned from available evidence | Phrase cautiously; record the inference |
| `pending` | Important fact lacks evidence | Insert `[PENDING CONFIRMATION]` and list it in the reply |
| `editorial` | Framing, transitions, creative copy | Must not introduce factual claims |

Confident prose must not upgrade an inference into a sourced fact. Never
fabricate citation details, dates, figures, names, standards, approvals,
budgets, results, or implementation status.

## Source IDs

Use short stable IDs such as `requirements`, `meeting-2026-07-21`, or
`architecture-v3`. A block with `provenance: source` must name at least one ID
from the request's source inventory; unknown IDs fail validation.

## What the plan needs before layout

Objective, audience, type, language, tone, length; source inventory; required
sections with the evidence feeding each; tables, figures, citations,
appendices, orientation; title page, header, footer, numbering; template styles
to reuse; privacy and final-variant requirements; unknowns needing
confirmation. A section without evidence is explicitly editorial, intentionally
empty, or pending.

## Drafting details

Define abbreviations at first use unless universal for the audience. Keep units
attached to figures and one notation throughout. Use descriptive link text
instead of raw URLs.
