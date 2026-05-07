---
name: krt-docs-chronicler
description: Maintain durable project knowledge without creating documentation sprawl. Use when a user asks to update docs after a feature, incident, release, review, or architecture decision; reconcile stale README/runbook/ADR/changelog content; capture lessons learned; write lightweight ADRs; audit documentation drift; or decide where a new piece of project knowledge belongs. Runtime aliases may expose this as krt:docs-chronicler.
---

# Docs Chronicler

Docs Chronicler keeps the project's memory useful: current enough to trust, small enough to read, and placed where future humans and agents will actually find it.

It edits docs when asked. When the user asks only for analysis, return a documentation plan and do not modify files.

## Load References

- Load `references/documentation-rubric.md` before deciding where information belongs or updating docs.
- Load `references/source-literature.md` when explaining the documentation model or when the user asks what the workflow is based on.

## Workflow

### Step 1 - Classify The Knowledge

Identify the documentation job:

- **How-to/runbook:** operational steps, setup, deploy, rollback, incident response.
- **Reference:** commands, configuration, API shape, env vars, permissions, schemas.
- **Concept/explanation:** why the system works this way, mental model, tradeoffs.
- **ADR/decision:** decision, context, considered options, consequences.
- **Changelog/release note:** what changed for users/operators/reviewers.
- **Learning/postmortem:** what happened, what was learned, what should change.
- **Cleanup:** stale, duplicate, contradictory, or misleading docs.

If the destination is unclear, inspect existing docs before creating a new file.

### Step 2 - Find The Canonical Home

Prefer updating the existing durable home over creating new prose:

- README for entry points, setup, common usage, and install paths.
- `docs/` for deeper guides, architecture, runbooks, and project knowledge.
- ADR directories or existing decision logs for architectural choices.
- CHANGELOG/release notes only for user/operator-visible changes.
- Skill `references/` for reusable agent procedure, not project history.

Do not duplicate truth across multiple files unless one is a summary that links to the canonical source.

### Step 3 - Reconcile With Reality

Before writing, compare docs against observable repo context:

- current files, commands, scripts, config, manifests, tests, and examples;
- recent diffs or commits when documenting completed work;
- existing terminology and style;
- stale instructions, old paths, contradictory setup, or missing prerequisites.

When reality cannot be verified, mark the claim as an assumption or ask for the missing source.

### Step 4 - Write The Smallest Durable Update

Use the right artifact shape:

- **README/update:** concise entry-point text and links.
- **Runbook:** prerequisites, safe read-only checks, action steps, rollback, verification.
- **ADR:** status, context, decision, consequences, alternatives when helpful.
- **Learning:** trigger, root cause or insight, durable change, follow-up owner.
- **Changelog:** added/changed/fixed/deprecated/removed/security when the repo uses that style.

Prefer clear headings, imperative commands, repo-relative paths, and explicit verification. Avoid long narrative when a table or short checklist is enough.

### Step 5 - Close The Loop

Return:

```text
Docs status: updated | plan only | blocked

Changes:
- <file> - <what changed and why>

Canonical truth:
- <where future readers should look>

Open questions:
- <only if unresolved>
```

## Guardrails

- Do not create docs just because information exists; create docs when it will reduce future confusion.
- Do not preserve stale docs for nostalgia. Update, consolidate, archive, or delete when appropriate.
- Do not bury decisions only in PR descriptions or chat summaries.
- Do not write release notes as internal implementation logs.
- Do not invent commands, env vars, architecture, or operational guarantees.
- Keep docs agent-friendly: stable paths, exact commands, and clear ownership beat prose flourish.
