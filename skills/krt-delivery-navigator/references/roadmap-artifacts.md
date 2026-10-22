# Roadmap Artifacts

File shapes for roadmaps and readiness reports. `krt-compound-master` reads
the closeout block and the artifact path, so keep those exact.

## Roadmap

Path: `docs/roadmaps/YYYY-MM-DD-NNN-<initiative-slug>-roadmap.md`. Use the next
free zero-padded `NNN` for that date and slug. Update an existing roadmap only
when asked; never overwrite silently.

```markdown
---
title: <Roadmap title>
status: active
date: YYYY-MM-DD
source_docs:
  - path/to/source.md
---

# <Roadmap title>

## Source Inventory
| Source | Contribution | Confidence (high/medium/low) |
|---|---|---|

## Roadmap Items
- RDM-001. **<Semantic item name>**
  - Outcome:
  - Why now: <reason from the docs>
  - Scope boundary: <included / excluded>
  - Hard depends on: <None / RDM-###>
  - Soft sequencing preference: <None / RDM-###>
  - Risk: <low/medium/high + why>
  - Expected brainstorm: `docs/brainstorms/...`
  - Expected plan: `docs/plans/...`
  - Suggested package: <whole item / split later>

## Dependency Graph
<Mermaid or bullet map>

## Parallelization Waves
- Wave 1: <independent items>

## Branch and PR Strategy
| Package candidate | Base branch | PR type | Dependency | Notes |
|---|---|---|---|---|

## Blockers and User Decisions
- <decision needed, or "None">
```

`RDM-###` IDs are for traceability only; release text uses the semantic names.
Hard dependency means the dependent item cannot safely ship first; soft
sequencing is a preference.

## Readiness report

Path: `docs/orchestration/YYYY-MM-DD-NNN-<initiative-slug>-readiness-report.md`.
It is terminal for the run: do not also write a roadmap.

Sections: `Context Found` (source, contribution, confidence), `Missing
Context`, `Why Roadmap Generation Is Unsafe`, `Blocking Questions`,
`Recommended Documents`, `Exact Next Prompt`.

Write a readiness report when missing context would change roadmap items,
dependency order, branch strategy or product scope, typically when several of
these are absent: product intent and non-goals, current system shape,
technical execution context (stack, test commands), data or interface
contracts, delivery conventions (branching, CI, release), or existing scope
(specs, backlog). If only one decision is missing and the rest is strong, ask
that question instead.

## Closeout

```text
artifact_kind: roadmap | readiness-report
artifact_path: docs/...
blockers: No blockers | <concise blockers>
recommended_next_action: <exact next action or prompt>
```

For a roadmap, the next action is review by the caller's document-review step.
For a readiness report, it is the exact prompt that produces the missing doc.
