# Artifact Templates

Use this reference when Compound Master writes roadmaps, work packages, artifact closeouts, or final summaries.

## Roadmap

Path:

```text
docs/roadmaps/YYYY-MM-DD-NNN-<initiative-slug>-roadmap.md
```

Use the next available zero-padded sequence for the date and slug. Resume/update only when explicit; never overwrite silently.

```markdown
---
title: [Roadmap title]
status: active
date: YYYY-MM-DD
source_docs:
  - path/to/source.md
---

# [Roadmap title]

## Context Sufficiency Summary
- [What was found]
- [Why this is enough]

## Source Inventory
| Source | Contribution | Confidence |
|---|---|---|

## Roadmap Items
- RDM-001. **[Item name]**
  - Outcome: [user/system outcome]
  - Why now: [reason from docs]
  - Scope boundary: [included/excluded]
  - Hard depends on: [None / RDM-###]
  - Soft sequencing preference: [None / RDM-###]
  - Blocks/enables: [RDM-###]
  - Risk: [low/medium/high + why]
  - Expected brainstorm: `docs/brainstorms/...`
  - Expected plan: `docs/plans/...`
  - Suggested package: [roadmap-item / split by U-ID later]

## Dependency Graph
[Mermaid graph or bullet dependency map]

## Parallelization Waves
- Wave 1: [independent items]
- Wave 2: [items depending on Wave 1]

## Branch and PR Strategy
| Package candidate | Base branch | PR type | Dependency | Notes |
|---|---|---|---|---|

## Blockers and User Decisions
- [Decision needed before brainstorm/plan/work]
```

Dependency rules:

- Hard dependency = cannot safely implement dependent item before prerequisite.
- Soft sequencing = preference, not blocker.
- Mark independent items for possible parallel work.
- If uncertainty affects branch strategy or product behavior, ask before execution.

Review the roadmap with resolved `document_review`, apply safe fixes, and ask only when findings change scope, behavior, dependency order, or PR strategy.

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

## Verification Gate
- [Commands/outcomes that must pass]

## Review Gate
- Code review threshold: [configured `review-threshold`; default P0-P2]
- Findings below threshold: log unless user marks blocking

## Branch and PR Handoff Inputs
- Branch name: [feat/rdm-001-slug]
- PR base: [develop/main/parent branch]
- PR title:
- PR body bullets:
- Verification results location:

## Jira Handoff Inputs
- Jira policy: [required|optional|skip]
- Suggested issue type: Tarea
- Suggested subtask behavior: create/reuse subtask when parent is provided
- Jira summary:
- Jira description:
```

Review every package with `document_review`. Fix blockers before execution.

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

Include roadmap, brainstorms, plans, packages, waves, branches, tests, review rounds, Jira tasks, PRs, blockers, residual advisory findings, completed packages, remaining packages by wave, and the next recommended invocation if work remains.
