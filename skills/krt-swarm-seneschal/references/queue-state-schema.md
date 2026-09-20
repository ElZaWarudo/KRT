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
    documentation_gate_exemption: null
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
      contract_protocol: lightweight
      worker_profile: luna
      reasoning_effort: high
      lane_trigger: bounded-local-decisions
      assurance:
        tier: medium
        triggers: [bounded-cli-behavior]
        review_mode: focused-reviewer
        review_demand: 1
      worker_contract_path: null
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

When the approved packet needs review again, use `documentation-status` with
`from: approved` and `to: in_review`, supplying current queue and blocker digests.
Reopening clears `approved_by`, `approved_at`, `approval_receipt`,
`approved_packet_digest`, and `approval_receipt_digest` from the active gate.
Previous receipt files remain on disk as historical evidence and no longer
authorize approval-dependent transitions. The artifact lists are preserved.
After review, use `approve-documentation` with a current receipt and the trusted
authorization-event digest; receipt integrity, current artifact hashes, and
coverage checks still apply. Both steps use the existing transaction lock and
digest preconditions. Rejected transitions leave queue and blocker files unchanged.

When the documentary gate applies to the active broad initiative, do not create
real Jira keys, executable `running` units, implementation wave history, or
release handoff packets unless `documentation_gate.status` is `approved`.
Action-specific authorization does not waive that initiative gate.

For a bounded unit that was already execution-ready, was explicitly authorized
by the user, and was not derived from gate-required source work, persistence
may instead record this exact unit-scoped exemption:

```yaml
documentation_gate_exemption:
  basis: explicit-execution-ready-unit
  authorization_event_digest: sha256:<lowercase digest of the trusted user event>
```

Capture the trusted event digest when admitting the unit. Do not infer or add
the exemption merely because the global gate is unapproved. For each `ready` or
`running` transition, supply the same digest as
`expected_authorization_event_digest`. The transition validator accepts the
exemption only when the stored and trusted handoff digests match; malformed or
mismatched exemptions fail closed.

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
- `documentation_gate.status` from queue state when a documentary gate applies
- `docs/swarm/blockers.yaml`
- the initiative contract and each candidate child's canonical Compound state
- the canonical `docs/orchestration/autonomy-ledgers/<run>.json` when autonomous flow is active; validate it directly because `resume_snapshot` is not authority
- live Jira issue state through the resolved provider skill, when Jira is source
- current git branch/worktree state

Reconcile `cleanup_status` with live Git state before dispatch. Use
`not-created`, `active`, `cleanup-ready`, `removed`, or
`preserved-for-diagnosis`. Only `cleanup-ready` may enter the root-owned cleanup
registry, and only after its patch, manifest, and required evidence are durable.
Unregistered worktrees and branches remain preserved until their owning run
state is identified.

Then mark units with open blockers, dependencies on open blockers, or an
applicable non-approved documentation gate as ineligible for execution.

## Update Moments

### Evidence-bound `reconcile-unit`

The only supported reconciliation edge is `review-gated` → `release-ready`.
`unit-status` still cannot promote release states. `handed-off` and `merged`
remain the responsibility of the separate release gates.

Root must prepare `units.<id>.reconciliation_policy` before requesting the
transition. This is trusted queue configuration, protected by the queue digest;
do not derive or weaken it from a worker's result. It has exactly these fields:

```json
{
  "candidate_revision": "<full Git HEAD commit ID>",
  "candidate_digest": "sha256:<canonical candidate hash>",
  "contract_hash": "sha256:<current unit contract hash>",
  "worker_id": "implementer-runtime-id",
  "required_certifications": ["reviewer", "security-sentinel"],
  "findings_registry": {"path": "/root-owned/findings.json", "digest": "sha256:<file bytes hash>"}
}
```

`candidate_digest` is `canonical_sha256({"candidate_revision": revision,
"fingerprint": fingerprint["fingerprint"]})`, using
`scripts/deterministic_artifacts.py`. The fingerprint uses the existing
`verification_evidence.py` format: a full immutable base commit ID, sorted
changed paths and content hashes, and ordered required verification commands.
HEAD must equal `candidate_revision`. The fingerprint must match the complete
root-observed diff against its base, including untracked, non-ignored files,
and its current worktree contents. Thus a new HEAD, an additional changed file,
a content change, or changed verification commands invalidates the candidate.
This also supports a candidate with uncommitted changes: its identity includes
both HEAD and the complete content fingerprint.

At least `reviewer` is required. Supported roles are `reviewer` and
`security-sentinel`; security is mandatory when `risk.security` is absent or
anything other than `low`, or `execution.role_triggers.security-sentinel` is
set. If `execution.worker_contract_hash` is present, it must match the policy.
Root must carry all contract/assurance-required certification into this policy;
an aggregate reviewer certificate must only be issued after its underlying
review/validation coverage is complete. Actor identifiers are trusted runtime
attribution, not cryptographic signatures or worker-selected labels.

Each unit must explicitly have `depends_on: []` or a unique list of queue unit
IDs. Every referenced dependency must exist, differ from this unit, be
`release-ready`, `handed-off`, or `merged`, and have no open blockers. The unit
itself must have no open blockers. The existing queue/blocker cross-validation
checks both `unit_id` and `affected_units` references in the ledger.

The operation input is an exact JSON object; extra fields are rejected:

```json
{
  "schema_version": 1,
  "operation": "reconcile-unit",
  "unit_id": "wp-01-ru-02",
  "from": "review-gated",
  "to": "release-ready",
  "evidence": {"path": "/root-owned/reconciliation.json", "digest": "sha256:<file bytes hash>"}
}
```

Every evidence reference is exactly `{ "path": "...", "digest": "sha256:..." }`.
Digests hash the file bytes, not parsed JSON. Paths may be absolute (including
Windows paths) or relative to `--repo-root`; traversal and symlinks are rejected.
Use root-owned storage outside the candidate worktree for queue, blockers,
receipts and evidence, or ignore untracked operational artifacts deliberately.
Tracked state edits are part of the complete diff and invalidate verification;
the operation does not silently exclude files from coverage.

The referenced reconciliation bundle has exactly these fields:

```json
{
  "schema_version": 1,
  "unit_id": "wp-01-ru-02",
  "candidate_revision": "<same full Git HEAD commit ID>",
  "fingerprint": {"path": "/root-owned/fingerprint.json", "digest": "sha256:..."},
  "verification": {"path": "/root-owned/passing-record.json", "digest": "sha256:..."},
  "verification_logs": [{"path": "/root-owned/command-01-exit-0.log", "digest": "sha256:..."}],
  "certificates": [
    {"path": "/root-owned/reviewer.json", "digest": "sha256:..."},
    {"path": "/root-owned/security.json", "digest": "sha256:..."}
  ],
  "findings_registry": {"path": "/root-owned/findings.json", "digest": "sha256:..."}
}
```

`verification` references one existing `verification_evidence.py` record, not
the registry wrapper. Its canonical record digest must validate; result must
be `passed`, with fingerprint, base, paths and commands exactly matching the
candidate. `verification_logs` must contain one hashed log per command in the
same order and resolve to the record's evidence paths. Root is responsible for
capturing the passing record from actual execution; reconciliation reads
evidence and never executes commands from it. Freshness here means exact
candidate identity, not a wall-clock expiration policy.

Certificates use the existing exact independent-certificate format:

```json
{
  "role": "reviewer",
  "actor_id": "independent-runtime-id",
  "status": "passed",
  "contract_hash": "sha256:<same policy contract hash>",
  "diff_digest": "sha256:<same candidate_digest>",
  "findings": []
}
```

For this gate, certificate `diff_digest` binds the revision plus fingerprint
through `candidate_digest`. Required roles must all be present exactly once,
each actor must differ from the implementer, and every supplied certificate
must pass and contain no actionable findings. Renew certificates after fixes.
The findings reference must equal the policy-pinned reference; its contents
must validate using `finding_registry.py` and bind the same contract and
candidate digest. Only `fixed` or `rejected` findings permit promotion; fixed
findings must resolve against this candidate. Proposed, confirmed, revised,
and deferred findings block reconciliation.

The current documentation receipt is validated before and after evidence
inspection, even for units with execution-only documentation exemptions.
The accepted unit gains `reconciliation` containing the bundle reference,
candidate revision/digest, fingerprint, verification record digest, findings
registry digest, every accepted artifact reference/hash, and the documentation
approval receipt reference and digests. The policy and dependencies remain in
the unit. Validation runs inside the existing state lock and before journal
creation; rejected operations leave both state files byte-for-byte unchanged.
Writers must keep candidate content and root-owned evidence stable during the
transaction: the state lock coordinates queue writers, not arbitrary Git or
filesystem writers. Evidence and candidate content are rechecked before return.

Executable PowerShell example, after root has prepared the policy and evidence
files described above (run from the candidate repo; adjust the four paths):

```powershell
$skillScripts = Join-Path $env:USERPROFILE '.agents/skills/krt-swarm-seneschal/scripts'
$repoRoot = (Get-Location).Path
$queuePath = Join-Path $repoRoot '../root-evidence/queue-state.yaml'
$blockersPath = Join-Path $repoRoot '../root-evidence/blockers.yaml'
$bundlePath = Join-Path $repoRoot '../root-evidence/reconciliation.json'
$transitionPath = Join-Path $repoRoot '../root-evidence/reconcile-unit.json'
$bundle = Get-Content -LiteralPath $bundlePath -Raw | ConvertFrom-Json
$operation = @{
    schema_version = 1
    operation = 'reconcile-unit'
    unit_id = $bundle.unit_id
    from = 'review-gated'
    to = 'release-ready'
    evidence = @{
        path = (Resolve-Path -LiteralPath $bundlePath).Path
        digest = 'sha256:' + (Get-FileHash -LiteralPath $bundlePath -Algorithm SHA256).Hash.ToLowerInvariant()
    }
}
$json = $operation | ConvertTo-Json -Depth 5
[IO.File]::WriteAllText($transitionPath, $json, [Text.UTF8Encoding]::new($false))
$queueDigest = 'sha256:' + (Get-FileHash -LiteralPath $queuePath -Algorithm SHA256).Hash.ToLowerInvariant()
$blockerDigest = 'sha256:' + (Get-FileHash -LiteralPath $blockersPath -Algorithm SHA256).Hash.ToLowerInvariant()
python (Join-Path $skillScripts 'transition_swarm_state.py') `
    --repo-root $repoRoot --queue $queuePath --blockers $blockersPath `
    --transition $transitionPath --expected-queue-digest $queueDigest `
    --expected-blockers-digest $blockerDigest
if ($LASTEXITCODE -ne 0) { throw 'Reconciliation rejected; inspect the reported precondition.' }
```

### Other lifecycle updates

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
