# Jira Seeding

Use this reference when `jira-team-flow` needs to seed Jira Cloud from a roadmap, backlog, or work-package file.

## Documentation Gate

Before producing anything beyond a proposed seed plan:

- Read `documentation_gate` from `docs/swarm/queue-state.yaml`.
- If no gate exists and the source is a rough brief, new initiative, roadmap, Jira program, or swarm startup, return to `document-plan`.
- If `documentation_gate.status != approved`, do not create, update, comment on, link, or transition Jira issues.
- In that case, stop with the documentation review packet from `references/documentary-planning.md`.
- Proceed to Jira mutation only when documentation is approved or the user explicitly authorizes the exact Jira mutation in the current request.

## Seed Shape

Convert roadmap into proposed Jira hierarchy:

```text
Product epic
Parent issue by wave/domain
Subtask per work package, review unit, or executable queue unit
```

Collapse unnecessary hierarchy. If a parent would have exactly one child and no plausible sibling work, propose a standalone issue instead, following `krt-jira-cloud-scribe` issue-shape rules.

## Inputs To Extract

For every candidate item, capture:

- Roadmap source path anchor.
- Work package review unit ID.
- Domain or wave.
- Title in Spanish for Jira summary.
- 1-3 sentence Spanish description.
- Acceptance criteria.
- Dependencies.
- Touched surfaces.
- Verification expectation.
- Risk flags: auth, data, public contract, migration, central model, security, DIAN, accounting, payroll, infrastructure.
- Expert decisions required before implementation.

## Local Mapping

Before creating or proposing Jira issues, prepare the local queue map:

```yaml
jira_issue_map:
  MAP-123:
    queue_unit_id: wp-01-ru-02
    work_package: docs/work-packages/example.md
    review_unit: RU-02
    wave: wave-1
    domain: billing
    jira_parent: MAP-100
    jira_epic: MAP-1
    status: planned
```

If Jira keys do not exist yet, use stable provisional IDs:

```yaml
proposed_jira:
  product_epic:
    provisional_id: epic-mapale-roadmap
  parents:
    - provisional_id: parent-wave-1-billing
  subtasks:
    - provisional_id: subtask-wp-01-ru-02
```

Replace provisional IDs with real Jira keys only after `krt-jira-cloud-scribe` confirms creation or reuse and documentation approval exists.

## Blocked Seed Items

If an item depends on expert decisions, keep it in the seed plan but mark it blocked/deferred locally:

```yaml
status: blocked
blocker_refs:
  - BLK-2026-06-30-001
```

Use `references/blocker-ledger.md` to create the blocker record.

Examples:

- Product behavior undecided.
- Auth/permission model unknown.
- Data source migration decision missing.
- Real DIAN compliance interpretation required.
- Productive accounting or payroll rule needs expert validation.
- Security design required.

In manual flow, ask only when an unresolved decision blocks all seed/drain work or risks the wrong foundation. In autonomous flow after documentation approval, do not ask; record blocker, mark affected units blocked/deferred, and continue seeding/draining independent units.

## Mutation Guard

Documentation approval is required before Jira mutation. A Jira seed plan may exist while documentation is `draft`, `in_review`, or `changes_requested`, but real Jira creates/updates/comments/links/transitions must not run.

In manual flow, a seed plan may propose Jira creates/updates, but it must not execute them without confirmation. Before any Jira Cloud mutation, show:

- Jira Cloud project base URL.
- Proposed epic, parent issues, subtasks, labels, sprint placement, and blocked markers.
- Reuse candidates and why they match.
- New issue summaries and Spanish descriptions.
- Exact mutation classes requested.
- Documentation gate status and approval facts.

In autonomous flow, route covered execution through `krt-jira-cloud-scribe` only after the documentation gate is approved. If the ledger does not cover a mutation class, skip mutation, record a blocker or handoff gap, and continue independent approved work.

## Seed Output

End seed pass with:

```text
Seed status: proposed | confirmed | executed-by-jira-cloud-scribe | autonomous-executed | blocked
Documentation status: <draft|in_review|approved|changes_requested>
Roadmap source: <path>
Jira hierarchy:
- Epic: <key or provisional>
- Parents: <keys/provisional IDs>
- Subtasks: <keys/provisional IDs>
Blocked/deferred units:
- <unit>: <blocker ref>
Updated local state:
- docs/swarm/queue-state.yaml
- docs/swarm/blockers.yaml
Next drain invocation:
- Use krt-swarm-seneschal in modo jira-team-flow ...
```
