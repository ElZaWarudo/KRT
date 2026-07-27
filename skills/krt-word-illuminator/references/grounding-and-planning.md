# Grounding and planning

## Content states

Classify factual material before drafting:

| State | Meaning | Treatment |
|---|---|---|
| `source` | Supported by an inspected source | Record one or more source IDs |
| `user` | Explicitly supplied by the user | Preserve meaning; identify it as user input internally |
| `inference` | Reasoned from available evidence | Phrase cautiously and record the inference |
| `pending` | Important fact lacks evidence | Insert `[PENDING CONFIRMATION]` |
| `editorial` | Framing, transitions, or creative copy | Do not let it introduce new factual claims |

Do not convert an inference into a source-backed fact through confident prose.
Never fabricate citation details, dates, figures, names, standards, approvals,
budgets, results, or implementation status.

## Planning artifact

Before creating DOCX, record:

- objective, audience, document type, language, tone, and length;
- source inventory with stable source IDs;
- required sections and evidence feeding each section;
- tables, figures, citations, appendices, and orientation needs;
- unknowns and claims requiring confirmation;
- title-page, header, footer, and numbering requirements;
- semantic styles to reuse from a template or create when absent;
- privacy and final-variant requirements.

For each section, map facts to source IDs. A section without evidence must be
explicitly editorial, intentionally empty, or marked pending.

## Drafting rules

- Draft content before Word layout.
- Define abbreviations at first use unless the audience makes them universal.
- Keep units attached to figures and use one notation consistently.
- Use descriptive link text instead of raw URLs where possible.
- Keep a list of unverified claims in the request and creation report.
- Do not mark a section complete when its required evidence is missing.

## Source IDs

Use short stable IDs such as `requirements`, `meeting-2026-07-21`, or
`architecture-v3`. A block with `provenance: source` must name at least one ID
present in the request source inventory. Treat unknown IDs as validation
errors.

