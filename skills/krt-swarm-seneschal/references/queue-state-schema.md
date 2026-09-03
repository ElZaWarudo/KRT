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
  approval_artifacts:
    - docs/plans/<initiative>/initiative-requirements.md
    - docs/product/roadmap.md
    - docs/jira/seed-plan.md
    - docs/swarm/swarm-startup.md
  approval_receipt: null
  approved_packet_digest: null
  approval_receipt_digest: null
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
      assurance:
        tier: medium
        triggers: [bounded-cli-behavior]
        review_mode: focused-reviewer
        review_demand: 1
      worker_contract_path: docs/orchestration/runs/<run-id>/wp-01-ru-02-worker-contract.json
      worker_contract_hash: null
      evidence_trust: unknown
      role_triggers:
        reviewer: medium-assurance-bounded-cli-behavior
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
      fingerprint_artifact: null
      evidence_registry: "<root-owned-path-outside-worktree>/verification-evidence.json"
      reuse_decision: null
    isolation:
      type: worktree
      workspace_plan: docs/orchestration/runs/<run-id>/workspace-plan.json
      workspace_plan_hash: null
      workspace_id: null
      branch: null
      path: null
      thread: null
      mode: null
      source_revision: null
      baseline_source: null
      baseline_tree: null
      dependency_patch_hashes: []
      candidate_patch_hashes: []
      patch_manifest: null
      patch_manifest_hash: null
      cleanup_status: not-created
    handoff:
      intended_base: main
      pr_grouping: standalone
      release_notes: []
      suggested_jira_transition: null
      release_marshal_packet: null
wave_history:
  - id: wave-2026-06-30-001
    selected_units: []
    staged_topology:
      parent_unit_id: null
      artifact: null
      topology_hash: null
      foundation_unit_id: null
      foundation_baseline:
        base_revision: null
        diff_digest: null
        baseline_tree: null
        patch_manifest_hash: null
        isolation_ref: null
    workspace_plan:
      artifact: docs/orchestration/runs/<run-id>/<wave-id>-workspaces.json
      workspace_plan_hash: null
      consolidation_invocation: null
      invocations:
        - invocation_id: wave-2026-06-30-001-review-backend-01
          unit_id: wp-01-ru-02
          role: reviewer
          status: dispatched
          worker_ref: null
          workspace_id: review-backend-01
          started_at: "2026-06-30T10:00:00Z"
          last_runtime_event_at: null
          terminal_path: null
          terminal_digest: null
          recovery_path: null
          recovery_digest: null
          assessment:
            reasoning_quality: null
            protocol_compliance: not-observed
            completion: partial
            failure_origin: null
    concurrency:
      implementer_cap: 2
      cap_reasons: [default-cap]
      review_capacity: 2
      review_capacity_used: 1
      total_slots: 8
      usable_slots: 7
      reserve_slots: 1
      allocation_artifact: docs/orchestration/runs/<run-id>/<wave-id>-allocation.json
    result: planned
    scope_violations: null
    merge_conflicts: null
    review_lagging: null
    verification_summary: []
    aggregate_verification:
      owner: wave-root
      fingerprint: null
      fingerprint_artifact: null
      commands: []
      evidence: []
      evidence_registry: "<root-owned-path-outside-worktree>/verification-evidence.json"
      reuse_decision: null
      result: not-run
    gates:
      scope: unknown
      verification: not-run
      review: unknown
      security: not-required
      state: unknown
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
Older wave-history entries without explicit `scope_violations`,
`merge_conflicts`, and `review_lagging` remain valid history but never count as
green evidence for raising adaptive concurrency.

Older units without `execution.assurance` remain readable but are not eligible
for new dispatch until root classifies them. Do not infer assurance from the
stored execution lane or a historical `behavior-change` reviewer trigger.
Record the tier, concrete triggers, review mode, and review demand together.

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
- `review-gated`: a medium, high, or critical implementation returned and needs
  its tier-required independent review or validation. Low-assurance work does
  not enter this status merely to record self-review.
- `release-ready`: passed reconciliation gates and can be handed to `krt-release-marshal`.
- `needs-fix`: bounded fixes required before release handoff.
- `blocked`: cannot proceed until blocker is resolved.
- `deferred`: blocked or intentionally postponed, but not fatal to the whole wave.
- `split-required`: unit was too broad or worker scope exceeded safe review size.
- `handed-off`: release packet sent to `krt-release-marshal`.
- `merged`: release flow completed elsewhere and was reconciled locally.

## Staged Decomposition Projection

When `staged-decomposition.md` splits a coupled parent, preserve the compiler
artifact and hash with the run/wave artifacts. Mark the parent `split-required`
and create ordinary child units. Use `depends_on` for emitted edges and
`affects_dependents` on foundation or intermediate units. Do not add a second
queue-state schema for stages.

Record the immutable foundation baseline in wave history before marking
children ready. Child isolation must derive from that baseline. If foundation
changes, mark affected children ineligible, invalidate stale worker contracts,
and re-evaluate their base before dispatch or reconciliation. Generated and
integration paths appear under exactly one child unit's existing `surfaces` and
scope fields.

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

Lifecycle fields are executable state. Apply unit status, documentation
approval, and blocker-resolution transitions with
`scripts/transition_swarm_state.py`, passing SHA-256 digests observed before the
transition. The script locks the pair, rejects stale writers and illegal
edges, validates both documents, and leaves a recovery journal until both
atomic file replacements complete. Do not edit these fields independently.
The generic unit transition is pre-release only and fails closed for
`release-ready`, `handed-off`, and `merged`; those statuses require the named
reconciliation/release gate and cannot be promoted by adjacency alone.

Update queue state when:

- Documentation packet is drafted, moved to review, revised, approved, or has feedback recorded.
- Jira seed plan is proposed, confirmed, or executed by the selected Jira provider skill.
- Jira issue keys are mapped or remapped.
- A wave is planned, dispatched, reconciled, or closed.
- A role invocation is dispatched, returns, is interrupted, or disappears;
  persist its runtime identity, terminal/recovery digests, and separate
  assessment dimensions. Do not include an unobserved reasoning score in team
  averages.
- A worker reports changed files, verification, branch facts, or blockers.
- A unit receives or changes its execution route, lane, profile, or role triggers.
- Aggregate verification is run or reused for a wave fingerprint, or timing
  telemetry is updated.
- A unit becomes release-ready, needs-fix, blocked, deferred, split-required, or handed-off.
- A blocker is resolved and dependent units need readiness recheck.
