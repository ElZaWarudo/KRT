---
type: coding-harness
task: "Bad path"
status: draft
scope: local
confidence: medium
created: 2026-05-22
updated: 2026-05-22
---

# Coding Harness

## Objective
Avoid absolute paths.

## Source Of Truth Ranking
1. `/workspace/project/app/models/user.rb`

## Agent Initialization Context
- `AGENTS.md`

## Context Plan
**Read First**
- `/workspace/project/app/models/user.rb`

## Guardrails
- Use repo-relative paths.

## Risks
- Non-portable paths.

## Assumptions And Deferred Verification
- None.

## Validation Expectations
- Run harness check.

## Agent-Ready Instructions
Use repo-relative paths.
