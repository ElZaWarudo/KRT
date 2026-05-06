# Harness Artifacts

Use this reference when deciding whether to propose, create, write, save, generate, or update harness files.

A harness artifact is a markdown handoff for agents. It is not application source code, generated project code, migration code, test code, config, or general project documentation.

## Value Model

Saved harness files add value when they reduce handoff loss, repeated discovery, or execution drift. They should make a later agent faster and safer by preserving:

- The interpreted objective and task boundary.
- The source-of-truth ranking behind the plan.
- A bounded context plan instead of a broad repo scan.
- Observed project rules and guardrails.
- Risks, assumptions, and deferred verification.
- Agent-ready instructions that survive context resets.

Saved harness files do not add enough value when the task is tiny, single-turn, low-risk, unlikely to resume later, or already fully captured in the immediate chat.

## Design Basis

The file standard is derived from the existing Coding Harness Template, the skill's stated contract, and the external principles summarized in `harness-structure-research.md`:

- Frontmatter makes harness files discoverable, sortable, and reviewable without reading the whole body.
- `task`, `status`, `scope`, and `confidence` capture whether the harness is ready to execute or still needs clarification.
- `created` and `updated` let agents detect stale handoffs.
- Required sections preserve the minimum information needed for safe execution: objective, classification, source ranking, context, guardrails, risks, assumptions, plan, and agent-ready instructions.
- Optional sections stay optional to avoid turning every harness into a repository dump.

This is an internal operational standard, not an external framework claim. If a repository already has a stronger harness convention, follow the local convention and keep these fields only where they remain useful.

## When To Propose

Propose a saved harness file, even if the user did not ask for one, when any of these are true:

- The task is cross-cutting, architectural, high-risk, or likely to span more than one session.
- The harness contains project intelligence that future agents would otherwise rediscover.
- Multiple agents, work packages, review passes, or handoffs are likely.
- The user is preparing work but has not asked for immediate implementation.
- The harness includes many assumptions or deferred verification items that should remain visible.

The proposal should include the suggested path and one sentence explaining why persistence helps. Do not write the file until the user asks or confirms.

## When To Write

Write a harness file when:

- The user asks to create, write, save, generate, persist, or update a harness.
- The user accepts a proposed saved harness file.
- The user asks for "files" in a harness-wise context and does not clearly mean application code.
- The user asks for multiple agent handoff files, work package harnesses, or implementation harnesses.

Do not write a harness file when:

- The user only asks for a harness in chat.
- The user asks for application changes, generated code, tests, migrations, or config.
- The task scope is too ambiguous to produce a useful harness; ask one blocking scope question first.

## Default Location

Prefer an existing local convention if one is already present, such as:

- `docs/harnesses/`
- `harnesses/`
- `.harnesses/`
- `docs/agents/`

If no convention exists, use:

```text
docs/harnesses/<task-slug>.md
```

Use lowercase kebab-case for `<task-slug>`, for example `invoice-csv-export.md` or `billing-refactor.md`. If multiple harnesses are requested, use one file per distinct task or agent handoff.

## Required Frontmatter

Every saved harness file must start with YAML frontmatter:

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

Use the current date for `created` and `updated`. When updating an existing harness, preserve `created` if present and change `updated`.

## Content Standard

After frontmatter, use the Coding Harness Template. Keep the body compact and operational.

Required sections for saved harness files:

- `# Coding Harness`
- `## Objective`
- `## Task Type`
- `## Source Of Truth Ranking`
- `## Context Plan`
- `## Guardrails`
- `## Risks`
- `## Assumptions And Deferred Verification`
- `## Execution Plan`
- `## Agent-Ready Instructions`

Optional sections should appear only when relevant:

- `## Documentation Classification`
- `## Project Rules Detected`
- `## Skills`
- `## Change Impact Estimate`
- `## Blocking Questions`

## Multi-File Harness Sets

When creating several harness files, add an index only if the user asks for a harness pack or if more than three harnesses are created.

Default index path:

```text
docs/harnesses/README.md
```

The index should list each harness, its purpose, status, and intended order. Keep it as an agent navigation document, not a project architecture guide.

## Update Rules

When updating an existing harness:

- Read the existing file first.
- Preserve still-valid task evidence and useful context.
- Replace stale context instead of appending contradictory sections.
- Keep findings or review notes out of the harness unless the harness itself is in `review` status.
- Do not silently convert a harness into project documentation.

## Final Response

After writing harness files, report:

- Path(s) created or updated.
- Status of each harness: `draft`, `ready`, `blocked`, or `review`.
- Any blocking questions or deferred verification that affect the next agent.

After only proposing harness files, report:

- Proposed path(s).
- Why persistence would help.
- Whether the current harness is ready to save or blocked by a scope question.
