# Harness Schema

`scripts/check_harness.py` enforces this shape.

## Frontmatter

```yaml
---
type: coding-harness
task: "<short task name>"
status: draft        # draft | ready | blocked | review
scope: local         # local | cross-cutting | architectural
confidence: medium   # high | medium | low | unknown
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

Use `review` or `blocked` when publication-safety findings or blocking
questions remain. `ready` means `check_harness.py` passes with no errors.

## Required sections

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

Optional: `## Existing Harness Diagnosis` (only while status is `review`),
`## Documentation Notes`, `## Blocking Questions`, `## Next Step`.

## Section notes

- **Source Of Truth Ranking:** which docs win when they disagree (for
  example validated requirements over kickoff notes).
- **Context Plan:** group items as `Read First`, `Summarize`, `Inspect If
  Needed`, `Ignore For Now`, each with a one-line reason. Promoted
  `docs/harnesses/summaries/*.md` files go in `Read First`.
- **Validation Expectations:** the checks the repo already uses (from
  `AGENTS.md`, Makefile, CI), plus acceptance criteria to verify.
- **Agent-Ready Instructions:** what to do first and where to stop; no code.

## What check_harness.py flags

Errors: missing or invalid frontmatter, missing sections, absolute paths,
self-reference to `krt-harness-wise`, secrets, and publication-safety
findings when `status: ready`. Warnings: whole-directory read instructions
and publication-safety findings on non-ready harnesses.
