# Context Readiness

Use this reference for Compound Master Step 1.

## Sources To Scan

- Repo instructions: `AGENTS.md`, `CLAUDE.md`, compatibility fallbacks.
- Product docs: `STRATEGY.md`, `README.md`, `docs/`, `specs/`, `architecture/`, `adr/`, `docs/adr/`.
- Execution docs: PRDs, feature specs, API contracts, schemas, migrations, runbooks, roadmaps, plans, brainstorms.
- Tooling: package/build/test configs and delivery docs for branches, CI, releases, Jira, and PR conventions.

## Minimum Context

Roadmap generation is safe only when these categories are sufficiently covered:

1. Product intent: target problem, users/personas, outcomes, success criteria, non-goals.
2. Current system shape: major modules/services, core flows, integration boundaries.
3. Technical execution context: stack, package managers, run/test/build commands, conventions.
4. Data/interface context when applicable: schemas, migrations, APIs/events, auth/permissions.
5. Delivery context: branch/release conventions, CI expectations, deployment constraints, tracker conventions.
6. Existing scope context: backlog/roadmap/known gaps or enough specs to identify missing work without inventing direction.

## Context-Blocked Report

If context is insufficient, write:

```text
docs/orchestration/YYYY-MM-DD-context-readiness.md
```

Include:

- Found docs and what each contributes.
- Missing categories from the minimum-context list.
- Why roadmap generation is unsafe.
- Minimum docs or decisions needed to continue.
- Concrete next docs to create, such as `STRATEGY.md`, `docs/architecture.md`, `docs/api-contracts.md`, `docs/data-model.md`, or `docs/delivery-workflow.md`.

Then stop with a closeout that includes the readiness path, missing docs/decisions, and one recommended next prompt, for example:

```text
Use ce-brainstorm to draft docs/architecture.md for <initiative> from the context-readiness report.
```
