# Queue State Schema

Use this reference for `docs/swarm/queue-state.yaml`.

## Purpose

The queue state file is Seneschal's persistent local memory for the documentation gate, Jira issue mapping, executable units, wave history, verification, and release handoff facts.

It is not live Jira authority. Re-fetch Jira through the selected Jira provider skill before seed execution, release handoff, backlinks, comments, or transitions.

## Default Path

```text
docs/swarm/queue-state.yaml
```

Create the file when document planning, queue planning, or Jira team flow first needs persistence.

## Schema

```yaml
schema_version: 2
updated_at: "2026-06-30"
mode: jira-team-flow
documentation_gate:
  status: draft
  approved_by: null
  approved_at: null
  initiative_contract: docs/plans/<initiative>/initiative-requirements.md
  source_artifacts:
    - docs/plans/<initiative>/initiative-requirements.md
    - docs/product/roadmap.md
    - docs/jira/seed-plan.md
    - docs/swarm/swarm-startup.md
    - docs/swarm/queue-state.yaml
    - docs/swarm/blockers.yaml
  feedback_log: []
initiative:
  contract_path: docs/plans/<initiative>/initiative-requirements.md
  artifact_contract: ce-unified-plan/v1
  artifact_readiness: requirements-only
  shared_revision: null
  shared_decisions: []
compound_runs:
  customer-identity-auth:
    run_id: customer-identity-auth
    state_path: docs/orchestration/compound-master/customer-identity-auth/state.md
    interaction: brokered
    initiative_contract: docs/plans/<initiative>/initiative-requirements.md
    roadmap: docs/product/roadmap.md
    roadmap_item: RDM-001
    artifact_namespace: customer-identity/RDM-001-authentication
    status: planning-input-review-passed
    observed_at: "2026-07-28T10:30:00Z"
    artifact_revision: null
autonomy:
  mode: manual
  ledger_path: null
  resume_snapshot:
    authority: false
    schema_version: 1
    contract_id: null
    contract_status: null
    contract_hash: null
    latest_audit_event: null
    captured_at: null
jira:
  provider: null
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
    compound:
      run_id: customer-identity-auth
      state_path: docs/orchestration/compound-master/customer-identity-auth/state.md
      interaction: brokered
      observed_status: execution-ready
      observed_at: "2026-07-28T10:30:00Z"
      artifact_revision: null
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
    execution:
      route: swarm
      lane: standard
      worker_profile: luna
      reasoning_effort: high
      lane_trigger: bounded-local-decisions
      role_triggers:
        reviewer: behavior-change
    risk:
      production: unknown
      security: low
      compliance: low
      overlap: low
    verification:
      focused_commands: []
      focused_evidence: []
      aggregate_owner: wave-root
      aggregate_fingerprint: null
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
    aggregate_verification:
      owner: wave-root
      fingerprint: null
      commands: []
      evidence: []
      result: not-run
    timing_artifact: docs/orchestration/runs/<run-id>-timing.json
    review_summary: []
    blockers_recorded: []
```

## Schema Migration

Treat version 1 files as valid standalone-worker queues. Upgrade to version 2
only when the run needs an initiative contract or nested Compound flows.
Preserve existing Jira mappings, unit history, blockers, verification, and
handoff facts. Add `initiative`, `compound_runs`, and per-unit `compound`
projections without rewriting canonical Compound artifacts.
Older unit-level `verification.commands` and `verification.evidence` remain
valid. Migrate them to focused or aggregate ownership when the next wave touches
the unit; do not rerun passing evidence merely to reshape state.

## Compound Projection Rules

- Use a unique `run_id` and collision-free `state_path` for every active child.
- Treat the child state path as authority and `observed_*` fields as a cache.
- Refresh observations before wave selection, after child return, after a
  decision resolution, and before release handoff.
- Mark a projection stale when its revision or operational facts disagree with
  the canonical child state.
- Store decision detail in `docs/swarm/blockers.yaml`, not in both state files.

## Documentation Gate Rules

- `draft`: documentation packet is being created or incomplete.
- `in_review`: packet artifacts are ready for human review; Jira mutation, worker dispatch, code mutation, and release handoff remain blocked.
- `changes_requested`: user requested revisions; only documentation and blocker records may change.
- `approved`: explicit approval exists; downstream Jira seed/drain, wave planning, dispatch, and release handoff may proceed through their own gates.

Do not create real Jira keys, executable `running` units, implementation wave history, or release handoff packets unless `documentation_gate.status` is `approved` or the user explicitly authorized the exact bypass in the current request.

## Unit Statuses

- `planned`: known but not ready.
- `ready`: eligible for wave selection.
- `running`: dispatched worker.
- `review-gated`: implementation returned and needs review verification.
- `release-ready`: passed reconciliation gates and can be handed to `krt-release-marshal`.
- `needs-fix`: bounded fixes required before release handoff.
- `blocked`: cannot proceed until blocker is resolved.
- `deferred`: blocked or intentionally postponed, but not fatal to the whole wave.
- `split-required`: unit was too broad or worker scope exceeded safe review size.
- `handed-off`: release packet sent to `krt-release-marshal`.
- `merged`: release flow completed elsewhere and was reconciled locally.

## Jira Issue Map Rules

- Keep one canonical `queue_unit_id` for each Jira issue key.
- Prefer one Jira subtask per worker.
- Standalone Jira issues are allowed when hierarchy would be artificial.
- Preserve historical handoff verification facts when live Jira status changes.
- Replace provisional Jira IDs only after the selected Jira provider skill confirms creation or reuse.

## Read Before Wave Selection

Before every wave, read:

- `docs/swarm/queue-state.yaml`
- `documentation_gate.status` from queue state
- `docs/swarm/blockers.yaml`
- the initiative contract and each candidate child's canonical Compound state
- the canonical `docs/orchestration/autonomy-ledgers/<run>.json` when autonomous flow is active; validate it directly because `resume_snapshot` is not authority
- live Jira issue state through the resolved provider skill, when Jira is source
- current git branch/worktree state

Then mark units with open blockers, dependencies on open blockers, or a non-approved documentation gate as ineligible for execution.

## Update Moments

Update queue state when:

- Documentation packet is drafted, moved to review, revised, approved, or has feedback recorded.
- Jira seed plan is proposed, confirmed, or executed by the selected Jira provider skill.
- Jira issue keys are mapped or remapped.
- A wave is planned, dispatched, reconciled, or closed.
- A worker reports changed files, verification, branch facts, or blockers.
- A unit receives or changes its execution route, lane, profile, or role triggers.
- Aggregate verification is run or reused for a wave fingerprint, or timing
  telemetry is updated.
- A unit becomes release-ready, needs-fix, blocked, deferred, split-required, or handed-off.
- A blocker is resolved and dependent units need readiness recheck.
