# Summarization Policy

Use this policy to inspect, classify, and redact converted Markdown before any summary becomes versionable.

## Artifact Layout

```text
docs/harnesses/
├── sources/
│   └── <base>.md
├── staging/
│   └── <base>.md
├── provenance/
│   └── <base>.json
└── summaries/
    └── <base>.md  # created only by successful promotion
```

`sources/`, `staging/`, and `provenance/` are ignored. Only a deterministically checked staged summary may be copied to `summaries/`.

## Inspect, Classify, Redact

1. Inspect extraction gaps, image-only pages, malformed tables, and conversion warnings.
2. Classify secrets, personal data, commercial detail, private URLs, source paths, hashes, and client identifiers.
3. Redact to the minimum implementation-relevant facts. Express sensitive values as roles or technical implications.
4. Record private traceability and warnings in the sidecar, not the summary.

## Staged Summary

Start every staged summary with:

```yaml
---
summary_type: harness-ready
provenance_id: prov-<random-uuid4>
---
```

Generate the UUID4 randomly. Never derive it from source bytes, a filename, a source hash, or other source metadata. Do not include source paths, hashes, warning text, private URLs, contacts, or fallback links in the staged summary.

Use these sections:

```markdown
# <Document Title>

## Purpose
## Agent-Ready Facts
## Requirements And Constraints
## Decisions And Assumptions
## Risks And Open Questions
## Figures And Tables
```

## Private Sidecar

Create `docs/harnesses/provenance/<base>.json` with the same opaque ID:

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

Set `classification` explicitly to `public`, `internal`, `confidential`, `restricted`, or `unknown`. Promotion requires `redaction_status: completed` and a non-empty `publication_rationale`. The sidecar may also record private source paths, hashes, manifest references, or classification notes. For every warning, add a non-empty decision under the exact warning key before promotion. Missing or empty decisions block publication.

## Writing Rules

- Keep the summary short enough for a model to read by default.
- Preserve implementation-relevant names, identifiers, dates, constraints, and acceptance criteria only when safe.
- Replace personal names and private identifiers with roles or implementation-safe descriptions.
- Do not invent requirements, decisions, or certainty that the source does not support.
- Mark uncertainty in `Risks And Open Questions`.
- Describe relevant figures and tables without linking ignored images or raw sources.
