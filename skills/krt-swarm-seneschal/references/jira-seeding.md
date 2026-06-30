# Jira Seeding

Use this reference when `jira-team-flow` needs to seed Jira Cloud from a roadmap, backlog, or work-package file.

## Seed Shape

Convert the roadmap into this proposed Jira hierarchy:

```text
Product epic
  Parent issue by wave/domain
    Subtask per work package, review unit, or executable queue unit
```

Collapse unnecessary hierarchy. If a parent would have exactly one child and no plausible sibling work, propose a standalone issue instead, following `krt-jira-cloud-scribe` issue-shape rules.

## Inputs To Extract

For every candidate item, capture:

- Roadmap source path and anchor.
- Work package or review unit ID.
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

Before creating or proposing Jira issues, prepare or update the local queue map:

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

Replace provisional IDs with real Jira keys only after `krt-jira-cloud-scribe` confirms creation or reuse.

## Blocked Seed Items

If an item depends on expert decisions, keep it in the seed plan but mark it blocked/deferred locally:

```yaml
status: blocked
blocker_refs:
  - BLK-2026-06-30-001
```

Use `references/blocker-ledger.md` to create the blocker record. Examples:

- Product behavior undecided.
- Auth/permission model unknown.
- Data source or migration decision missing.
- Real DIAN compliance interpretation required.
- Productive accounting or payroll rule needs expert validation.
- Security design required.

In manual flow, ask only when the unresolved decision blocks all seed/drain work or risks a wrong foundation. In autonomous flow, do not ask; record the blocker, mark affected units blocked/deferred, and continue seeding or draining independent units.

## Mutation Guard

In manual flow, the seed plan may propose Jira creates/updates, but it must not execute them without confirmation. Before any Jira Cloud mutation, show:

- Jira Cloud project and base URL.
- Proposed epic, parent issues, subtasks, labels, sprint placement, and blocked markers.
- Reuse candidates and why they match.
- New issue summaries and Spanish descriptions.
- The exact mutation classes requested.

In autonomous flow, route covered execution through `krt-jira-cloud-scribe` with the autonomy ledger. If the ledger does not cover a mutation class, skip that mutation, record a blocker or handoff gap, and continue with independent work.

## Seed Output

End a seed pass with:

```text
Seed status: proposed | confirmed | executed-by-jira-cloud-scribe | autonomous-executed | blocked
Roadmap source: <path>
Jira hierarchy:
- Epic: <key or provisional>
- Parents: <keys or provisional IDs>
- Subtasks: <keys or provisional IDs>
Blocked/deferred units:
- <unit>: <blocker ref>
Updated local state:
- docs/swarm/queue-state.yaml
- docs/swarm/blockers.yaml
Next drain invocation:
Use krt-swarm-seneschal in modo jira-team-flow ...
```
