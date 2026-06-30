# Queue State Schema

Use this reference for `docs/swarm/queue-state.yaml`.

## Purpose

The queue state file is the seneschal's persistent local memory for Jira issue mapping, executable units, wave history, verification, and release handoff facts.

It is not live Jira authority. Re-fetch Jira Cloud through `krt-jira-cloud-scribe` before seed execution, release handoff, backlinks, comments, or transitions.

## Default Path

```text
docs/swarm/queue-state.yaml
```

Create the file when a queue or Jira team flow first needs persistence.

## Schema

```yaml
schema_version: 1
updated_at: "2026-06-30"
mode: jira-team-flow
autonomy:
  mode: manual
  ledger_path: null
jira:
  mode: cloud
  project_key: null
  base_url: null
  last_read_at: null
source_artifacts:
  - path: docs/work-packages/backlog-cobertura-total.md
    kind: roadmap
jira_issue_map:
  MAP-123:
    queue_unit_id: wp-01-ru-02
    work_package: docs/work-packages/example.md
    review_unit: RU-02
    wave: wave-1
    domain: billing
    jira_parent: MAP-100
    jira_epic: MAP-1
    jira_status: "Por hacer"
    local_status: planned
    blocker_refs: []
proposed_jira:
  epics: []
  parents: []
  subtasks: []
units:
  wp-01-ru-02:
    title: Example executable unit
    jira_key: MAP-123
    source: docs/work-packages/example.md
    status: planned
    depends_on: []
    blocked_by: []
    affects_dependents: []
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
      production: unknown
      security: low
      compliance: low
      overlap: low
    verification:
      commands: []
      evidence: []
    isolation:
      type: worktree
      branch: null
      path: null
      thread: null
    handoff:
      intended_base: main
      pr_grouping: standalone
      release_notes: []
      suggested_jira_transition: null
      release_marshal_packet: null
wave_history:
  - id: wave-2026-06-30-001
    selected_units: []
    concurrency: 2
    result: planned
    verification_summary: []
    review_summary: []
    blockers_recorded: []
```

## Unit Statuses

- `planned`: known but not ready.
- `ready`: eligible for wave selection.
- `running`: dispatched to a worker.
- `review-gated`: implementation returned and needs review or verification.
- `release-ready`: passed reconciliation gates and can be handed to `krt-release-marshal`.
- `needs-fix`: bounded fixes are required before release handoff.
- `blocked`: cannot proceed until a blocker is resolved.
- `deferred`: blocked or intentionally postponed, but not fatal to the whole wave.
- `split-required`: unit was too broad or worker scope exceeded safe review size.
- `handed-off`: release packet sent to `krt-release-marshal`.
- `merged`: release flow completed elsewhere and was reconciled locally.

## Jira Issue Map Rules

- Keep one canonical `queue_unit_id` for each Jira issue key.
- Prefer one Jira subtask per worker.
- Standalone Jira issues are allowed when hierarchy would be artificial.
- Preserve historical handoff and verification facts when live Jira status changes.
- Replace provisional Jira IDs only after `krt-jira-cloud-scribe` confirms creation or reuse.

## Read Before Wave Selection

Before every wave, read:

- `docs/swarm/queue-state.yaml`
- `docs/swarm/blockers.yaml`
- `docs/orchestration/autonomy-ledgers/<run>.yaml` when autonomous flow is active
- live Jira Cloud issue state, when Jira is the source
- current git branch/worktree state

Then mark units with open blockers or dependencies on open blockers as ineligible for selection.

## Update Moments

Update queue state when:

- Jira seed plan is proposed, confirmed, or executed by Jira Cloud Scribe.
- Jira issue keys are mapped or remapped.
- A wave is planned, dispatched, reconciled, or closed.
- A worker reports changed files, verification, branch facts, or blockers.
- A unit becomes release-ready, needs-fix, blocked, deferred, split-required, or handed-off.
- A blocker is resolved and dependent units need readiness recheck.
