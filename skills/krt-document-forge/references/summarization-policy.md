# Summarization Policy

How to write the staged summary and private sidecar that Harness Wise checks
and promotes.

## Redact before anything becomes versionable

1. Inspect extraction gaps, image-only pages, malformed tables, and converter
   warnings.
2. Classify secrets, personal data, commercial terms, private URLs, source
   paths, hashes, and client identifiers.
3. Keep the minimum implementation-relevant facts. Express sensitive values as
   roles or technical implications ("client operations contact", "fixed-price
   contract").
4. Put private traceability and warnings in the sidecar, not the summary.

## Staged summary: `docs/harnesses/staging/<base>.md`

```yaml
---
summary_type: harness-ready
provenance_id: prov-<random-uuid4>
---
```

Generate the UUID4 randomly (`python3 -c "import uuid; print(uuid.uuid4())"`).
Never derive it from source bytes, filenames, or hashes. No source paths,
hashes, warning text, private URLs, contacts, or links to ignored images or raw
sources.

```markdown
# <Document Title>

## Purpose
## Agent-Ready Facts
## Requirements And Constraints
## Decisions And Assumptions
## Risks And Open Questions
## Figures And Tables
```

Keep it short enough for a model to read by default. Preserve identifiers,
dates, constraints, and acceptance criteria when safe. Do not invent
requirements or certainty; put uncertainty under Risks And Open Questions.
Describe relevant figures in words.

## Private sidecar: `docs/harnesses/provenance/<base>.json`

```json
{
  "provenance_id": "prov-<same-random-uuid4>",
  "classification": "internal",
  "redaction_status": "completed",
  "publication_rationale": "Only implementation-relevant facts remain after redaction.",
  "warnings": [],
  "warning_decisions": {}
}
```

`classification` is one of `public`, `internal`, `confidential`, `restricted`,
`unknown`. Promotion requires `redaction_status: completed`, a non-empty
`publication_rationale`, and a non-empty decision under the exact key of every
warning. The sidecar may also hold source paths, hashes, and manifest
references.

## Handoff note

```text
Use krt-harness-wise to validate and promote:
- Staged Summary: docs/harnesses/staging/<base>.md
- Private Sidecar: docs/harnesses/provenance/<base>.json

Objective: <user's goal>

Converted by krt-document-forge; --check passed. Run check_evidence.py, resolve
every sidecar warning, then promote_evidence.py. Only the resulting
docs/harnesses/summaries/<base>.md is versionable; never copy raw sources,
images, manifests, hashes, or sidecars.
```
