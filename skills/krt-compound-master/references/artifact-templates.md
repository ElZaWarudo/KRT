# Artifact Templates

Use this reference when Compound Master writes work packages, artifact closeouts, or final summaries.

Roadmap and readiness report templates are owned by the resolved `roadmap_generator` role, canonically `krt-roadmap-cartographer`. Compound Master consumes those artifacts; it does not define their canonical shape here.

## Work Package

Path:

```text
docs/work-packages/YYYY-MM-DD-NNN-<rdm-id>-<package-slug>-work-package.md
```

Use a work package as the atomic PR/Jira unit. It may include one roadmap item, one plan U-ID, or a cohesive group of U-IDs.

Split when units have independent value, minimal file overlap, separate risk domains, and clean independent verification. Combine when units share migrations/API contracts/core files, depend tightly on each other, or would create noisy stacked PRs.

```markdown
---
title: [Work package title]
status: ready
roadmap_item: RDM-###
origin_roadmap: docs/roadmaps/...
origin_brainstorm: docs/brainstorms/...
origin_plan: docs/plans/...
units: [U1, U2]
base_branch: [integration branch or parent branch]
pr_strategy: [independent|stacked]
jira_policy: [required|optional|skip]
---

# [Work package title]

## Scope
[Only what this package implements]

## Non-goals
[Explicit exclusions]

## Dependencies
- Requires: [None / package IDs / branch / PR]
- Blocks: [package IDs]

## Implementation Units
[Relevant U-ID summaries]

## Files and Tests
[Repo-relative files and expected tests]

## Impact Scan
- Changed API contracts/endpoints/bindings/helpers/schemas/payloads/auth/tenant/ownership/test fixtures: [None / list]
- Consumer scan patterns: [None / rg/search patterns]
- Consumers found: [None / repo-relative files and flows]
- Required consumer tests: [None / commands or test files]
- Consumer tests run/skipped: [commands/results, or skip reason and whether CI covers it]

## Verification Gate
- [Commands/outcomes that must pass]

## Review Gate
- Code review threshold: [configured `review-threshold`; default P0-P2]
- Findings below threshold: log unless user marks blocking

## Branch and PR Handoff Inputs
- Branch name: [feat/package-slug-without-plan-number]
- PR base: [develop/main/parent branch]
- Suggested commit grouping:
  - [type(scope): summary] - [repo-relative files or surfaces] - [why this is one logical review unit]
  - [Split broad packages by changed surface: persistence/schema/model state; domain service/integration behavior; API/controller/generated contracts; config/deployment wiring; focused tests/fixtures; docs/orchestration. Omit surfaces that did not change.]
- PR title:
- PR body bullets:
- Verification results location:

## Jira Handoff Inputs
- Jira policy: [required|optional|skip]
- Suggested issue type: Tarea
- Suggested subtask behavior: create/reuse subtask when parent is provided
- Jira summary: [semantic title without roadmap/package numbers]
- Jira description: [concise scope/reason without roadmap/package numbers]
```

Review every package with `document_review`. Fix blockers before execution.

## Human-Facing Handoff Text

Keep internal planning identifiers out of public/reviewer-facing text:

- Do not include `RDM-001`, `U1`, date sequences, package numbers, or work-package sequence numbers in Jira summaries/descriptions, commit messages, PR titles, PR body bullets, or branch names.
- Use semantic names that describe the capability or fix: `feat/tenant-permission-bundles`, not `feat/rdm-001-tenant-permission-bundles`.
- Jira summaries should read like work items a teammate would understand without the orchestration plan.
- Jira descriptions should explain scope and reason in concise prose, not restate roadmap IDs or package numbers.
- PR titles and commit messages should be value-oriented and conventional; put traceability in artifact metadata, PR dependency notes, or Jira links instead of the title.
- Keep IDs only in internal fields such as `roadmap_item`, `units`, origin paths, dependency tables, and state.

## Artifact Closeout

When `mode:artifacts` stops, include:

- Roadmap path.
- Brainstorm paths.
- Plan paths.
- Work-package paths.
- State path.
- Dependency waves and recommended first package.
- Branch strategy summary.
- Blockers, or "No blockers".
- Exact next invocation, for example:

```text
Use krt-compound-master mode:execute package:<work-package-path> jira-policy:<required|optional|skip> parallel:false
```

If no package is ready, say exactly why. If packages are ready, say artifact generation is complete and execution is intentionally waiting for an explicit user gate.

For `mode:full`, ask one execution gate after the artifact closeout:

```text
Artifacts are ready. Recommended next package: <work-package-path>.
Proceed with execution now?
```

## Final Summary

At the end, write:

```text
docs/orchestration/YYYY-MM-DD-compound-master-summary.md
```

Include roadmap, brainstorms, plans, packages, waves, branches, Impact Scans, tests, review rounds, Jira tasks, PRs, blockers, residual advisory findings, completed packages, remaining packages by wave, and the next recommended invocation if work remains.
