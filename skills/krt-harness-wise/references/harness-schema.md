# Harness Schema

Load for creating, patching, or validating a harness.

## Default Path

```text
docs/harnesses/<task-slug>.md
```

Use lowercase kebab-case for `<task-slug>`.

## Frontmatter

```yaml
---
type: coding-harness
task: "<short task name>"
status: draft
scope: local
confidence: medium
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

Allowed values:

- `status`: `draft`, `ready`, `blocked`, `review`
- `scope`: `local`, `cross-cutting`, `architectural`
- `confidence`: `high`, `medium`, `low`, `unknown`

## Required Sections

```markdown
# Coding Harness

## Objective
## Source Of Truth Ranking
## Agent Initialization Context
## Context Plan
## Guardrails
## Risks
## Assumptions And Deferred Verification
## Validation Expectations
## Agent-Ready Instructions
```

Optional sections:

- `## Existing Harness Diagnosis`
- `## Documentation Notes`
- `## Blocking Questions`
- `## Next Step`

## Content Rules

- Use repo-relative paths only.
- Do not include absolute local filesystem paths.
- Do not include raw/source/image/staging/provenance paths, hashes, manifests, or private sidecar data.
- Do not instruct the next agent to invoke `krt-harness-wise`.
- Do not ask the next agent to read whole directories unless the reason and boundary are explicit.
- Keep execution guidance high level; do not write implementation code or commit/push instructions.
- Include confidence and deferred verification for uninspected technical facts.
