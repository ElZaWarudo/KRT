---
type: coding-harness
task: "Invoice export"
status: ready
scope: local
confidence: high
created: 2026-05-22
updated: 2026-05-22
---

# Coding Harness

## Objective
Prepare implementation context for invoice CSV export.

## Source Of Truth Ranking
1. `AGENTS.md`
2. `docs/specs/invoices.md`

## Agent Initialization Context
- `AGENTS.md` was inspected for repository rules.

## Context Plan
**Read First**
- `docs/specs/invoices.md` - invoice export behavior.

**Summarize**
- `README.md` - available setup commands.

**Inspect If Needed**
- `app/services/invoices` - implementation examples.

**Ignore For Now**
- `docs/brainstorms` - historical planning context.

## Guardrails
- Keep changes scoped to invoice export.

## Risks
- CSV format drift - verify against existing specs.

## Assumptions And Deferred Verification
- Test command must be confirmed during implementation.

## Validation Expectations
- Add focused coverage for export columns.

## Agent-Ready Instructions
Use this harness to plan or implement invoice export with repo-relative paths only.
