# Queue And Dispatch

Use this reference when selecting ready work and planning execution waves.

## Queue Unit Contract

Every queued unit needs:

```yaml
id: semantic-id
title: short human title
source: docs/work-packages/... | jira issue | github issue | linear issue | backlog file
jira_key: null
status: planned | ready | running | review-gated | release-ready | needs-fix | handed-off | merged | blocked | deferred | split-required
depends_on: []
blocked_by: []
scope:
  included: []
  excluded: []
acceptance_criteria: []
surfaces:
  code: []
  contracts: []
  data: []
  auth: []
  docs: []
  tests: []
  config: []
  generated: []
dependencies: []
risk:
  production: unknown | prototype | preprod | live
  security: low | elevated | high
  compliance: low | elevated | high
  overlap: low | elevated | high
verification:
  commands: []
  evidence: []
handoff:
  intended_base: main
  branch: null
  pr: null
  pr_grouping: standalone
  suggested_jira_transition: null
  notes: []
```

If a work package already defines review units, use those IDs and paths instead of inventing new ones. For the full persistent schema, load `queue-state-schema.md`.

## Ready Criteria

A unit is ready only when:

- Documentation gate is approved for any Jira seed/drain, worker dispatch, code mutation, or release handoff.
- Dependencies are merged or explicitly available on the intended base.
- Scope and non-goals are written.
- Acceptance criteria are checkable.
- Verification commands or a justified verification gap exist.
- No unresolved product, auth, data, deployment, or public-contract decision blocks implementation.
- Branch/base strategy is known.
- Overlap with active units is low or explicitly coordinated.
- Jira source state, when applicable, has been read through the selected Jira provider skill and has an unambiguous issue/subtask key.
- No open blocker exists in `docs/swarm/blockers.yaml` for the unit or its dependencies.

## Wave Selection

Default wave size is 1 for uncertain queues. In established Jira team flow, default to 2 workers when:

- Documentation gate is approved.
- Units are dependency-ready.
- Changed surfaces do not materially overlap.
- Isolation exists.
- Verification can run for both.
- Open stacked PR cap remains respected.
- Blocker ledger has no open blockers affecting either unit.

Raise above 2 only after successful prior waves and explicit user approval in manual flow, or when the autonomy ledger permits scaling in autonomous flow. Load `parallel-dispatch-policy.md` for the complete algorithm.

## Overlap Rules

Treat as conflicting unless strong evidence says otherwise:

- same migration/data model
- same auth/permission path
- same public API contract
- same generated artifact
- same central orchestration skill or shared reference
- same build/dependency/config file

Docs-only overlap can run in parallel when each unit edits distinct docs or one worker is clearly designated owner of the shared doc.

Never parallelize overlapping auth, migrations, public contracts, central models, or lockfiles. Treat DIAN, productive accounting, productive payroll, legal, and security-sensitive production surfaces as high-risk until proven otherwise.

## Wave Plan Shape

Before dispatch, produce:

```text
Wave: <name>
Mode: design-only | dispatch | reconcile | resume
Documentation status: <draft|in_review|approved|changes_requested>
Concurrency: <n>
Isolation: branch | worktree | cloud | manual
jira_provider: cloud | server-datacenter | none
Blocker ledger: docs/swarm/blockers.yaml
Units:
- <id>: <title>
  Jira: <key or none>
  Source: <path/link>
  Worker role: <compound-master|implementer|reviewer|documenter|fixer>
  Intended base: <branch>
  Expected branch/worktree: <name/path>
  Verification: <commands or gap>
  Risks: <short list>
Stop conditions:
- <condition>
```

Ask approval before mutating or dispatching in manual flow. In autonomous flow, do not ask after documentation approval; dispatch only ledger-covered mutation classes, record uncovered needs, and continue.

## State Updates

Update queue state immediately when:

- Documentation gate changes status or receives feedback.
- A unit is dispatched.
- A worker reports blockers.
- Verification fails or passes.
- Review creates at-or-above-threshold findings.
- A unit becomes release-ready.
- Release handoff creates PR/Jira links.
- A dependency merges or changes base.
- blocker-review or blocker-resolve changes eligibility.

Never let markdown state pretend to be live authority. Re-fetch GitHub/Jira state before release decisions and use only the selected Jira provider skill.
