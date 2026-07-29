# Parallel Dispatch Policy

Use this reference when selecting wave size and deciding which units may run concurrently.

## Role Pools

Do not treat "2 workers" as the total factory size. It is the default cap for concurrent mutable implementation units.

Use separate role pools:

```yaml
planner_workers: 4-8
implementer_workers: 2
reviewer_workers: 2-4
fixer_workers: 1-3
integrator_workers: 1
documenter_workers: 1-3
```

Adjust these caps to runtime capacity, repo size, and available isolation. The seneschal may run Planner, Reviewer, Fixer, Integrator, and Documenter work around the Implementer pool as long as shared-state and quality gates stay coherent.

## Nested Compound Capacity

Count each active Compound Master flow that may mutate files as one Implementer
slot, regardless of how many internal roles it invokes. Start nested children
with `parallel:false`; Seneschal owns cross-flow concurrency. A child may use
bounded read-only reviewers and one mutating worker for its assigned unit, but
must not create sibling Compound flows or expand the factory's mutable
concurrency. Increase inner parallelism only through an explicit wave plan with
separate isolation and capacity accounting.

## Default Implementation Concurrency

Default to 2 concurrent Implementer workers when:

- Worktree, branch, cloud, or thread isolation exists for each worker.
- Units have no dependency edge between them.
- Surfaces do not materially overlap.
- Verification can run for each unit.
- The team can reconcile all outputs before release handoff.

Use serial implementation when isolation is missing or surface ownership is unclear.

Planner workers may run higher concurrency because they do not mutate product code. Reviewer workers may run in parallel over distinct diffs. Fixer workers are bounded by the failed units they fix. Integrator is normally single-threaded because it reasons over the whole wave. Documenter workers may run in parallel only when they edit distinct docs or one owner is assigned for shared release notes.

## Raising Implementation Concurrency

Raise Implementer concurrency above 2 only when all are true:

- At least two recent waves finished green.
- No unresolved merge conflicts or scope creep came from those waves.
- Review and verification gates completed within the same orchestration cycle.
- Queue state and blocker ledger stayed current.
- Manual flow: the user approved the higher concurrency.
- Autonomous flow: the autonomy ledger permits higher concurrency and wave history is green.

Suggested Implementer cap progression:

```text
2 implementers -> 3 implementers after 2 green waves -> 4 implementers after 4 green waves
```

Do not exceed the repo's review capacity or stacked PR cap. If Reviewers or Integrator cannot keep up, reduce Implementer concurrency.

## Never Parallelize When Overlapping

Do not run units in parallel when they overlap on:

- Auth, permissions, identity, session, tenant, or access-control behavior.
- Database migrations, schema ownership, seed data, or data model changes.
- Public API contracts, events, webhooks, SDK surfaces, or integration payloads.
- Central domain models, shared orchestration code, core state machines, or cross-cutting validators.
- Lockfiles, dependency manifests, build config, generated clients, or generated artifacts.
- Release infrastructure, CI config, deployment config, or environment config.
- Real DIAN compliance, productive accounting, productive payroll, or security-sensitive production flows.

If overlap exists, serialize, split, or create an explicit dependency edge.

## Usually Safe To Parallelize

Parallelism is usually acceptable for:

- Isolated frontend views or components with distinct routes/state.
- Documentation files that do not edit the same shared document.
- Domain modules with separate ownership and no shared contracts.
- Tests for distinct modules when test fixtures are not shared.
- Low-risk internal refactors inside disjoint packages.
- Independent bug fixes that touch unrelated files and have narrow verification.

## Selection Algorithm

1. Start with ready implementation units sorted by dependency depth, priority, risk, and age.
2. Remove units with open blockers or dependencies on open blockers.
3. Remove units lacking isolation or verification.
4. Build a surface set for each unit: code, contracts, data, auth, docs, tests, config, generated, dependencies.
5. Select the first unit.
6. Add the next unit only if its surface set is compatible with all selected units.
7. Stop when the Implementer concurrency cap is reached or no compatible units remain.
8. Record why skipped units were not selected.

For non-implementation roles, use role caps instead of the Implementer cap:

- Dispatch Planner workers by roadmap/domain boundaries.
- Dispatch Reviewer workers by completed independent diffs.
- Dispatch Fixer workers only for bounded findings or failing checks.
- Dispatch one Integrator for a wave or PR stack unless the surfaces are fully disjoint.
- Dispatch Documenter workers by distinct documentation surfaces.

## Wave Decision Record

Record for each wave:

```yaml
wave_history:
  - id: wave-2026-06-30-001
    concurrency:
      implementers: 2
      planners: 4
      reviewers: 2
      fixers: 1
      integrators: 1
      documenters: 1
    selected_units: []
    skipped_units:
      - unit_id: example
        reason: open-blocker | dependency | surface-overlap | no-isolation | not-ready
    result: planned | running | green | partial | failed
    green: false
```
