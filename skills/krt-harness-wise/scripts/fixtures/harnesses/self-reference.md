---
type: coding-harness
task: "Self ref"
status: draft
scope: local
confidence: medium
created: 2026-05-22
updated: 2026-05-22
---

# Coding Harness

## Objective
Avoid self reference.

## Source Of Truth Ranking
1. `AGENTS.md`

## Agent Initialization Context
- `AGENTS.md`

## Context Plan
**Read First**
- `AGENTS.md`

## Guardrails
- Do not loop.

## Risks
- Confusing next agent.

## Assumptions And Deferred Verification
- None.

## Validation Expectations
- Run harness check.

## Agent-Ready Instructions
Use krt-harness-wise before doing the work.
