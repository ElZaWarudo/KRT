# Documentary Planning

Use this reference for `document-plan`, `document-review`, `document-revise`, and `document-approve`.

## Purpose

Create a human-reviewable planning packet before Jira seeding or worker dispatch
from a rough initiative, roadmap, program, swarm startup, or unrefined backlog.

```text
rough brief -> initiative contract -> roadmap/Compound artifacts -> composition review -> approval -> execution
```

When this gate applies, documentation approval is a formal dependency rather
than a courtesy summary. Do not manufacture a packet for an execution-ready
unit that the user explicitly authorized and whose scope, acceptance criteria,
dependencies, and verification are already settled.

## Gate State

Persist the gate in `docs/swarm/queue-state.yaml`:

```yaml
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
  feedback_log:
    - at: "YYYY-MM-DDTHH:MM:SSZ"
      by: user
      summary: "Requested MVP boundary changes."
      affected_artifacts:
        - docs/product/roadmap.md
```

Statuses:

- `draft`: documentation is being created or is incomplete.
- `in_review`: all required packet artifacts exist and are ready for user review.
- `changes_requested`: user requested revisions; do not proceed to Jira or execution.
- `approved`: user explicitly approved the documentation packet for Jira seed/drain and worker execution.

## Required Artifacts

Produce these artifacts for a new initiative, rough brief, roadmap, Jira
program, swarm startup, or autonomous program-level run:

- `docs/plans/<initiative>/initiative-requirements.md`: reviewed requirements-only general brainstorm containing shared intent, actors, global scope/non-goals, terminology, success criteria, invariants, settled decisions, escalation boundaries, and open decisions. Accept another configured-docs-root path when the artifact declares `artifact_contract: ce-unified-plan/v1` and `artifact_readiness: requirements-only`.
- `docs/product/roadmap.md`: product framing, MVP boundary, phase 2 epics, dependencies, risks, and implementation start criteria.
- `docs/jira/seed-plan.md`: proposed Jira hierarchy, issue shapes, reuse candidates, blocked/deferred items, labels/statuses/sprint placement, and exact mutation classes that would be needed after approval.
- `docs/swarm/swarm-startup.md`: source context, operating mode, concurrency policy, worker role caps, isolation approach, verification gates, release handoff policy, and stop conditions.
- `docs/swarm/queue-state.yaml`: documentation gate, provisional queue units when useful for review, proposed Jira map, wave candidates, and no executable `running` state before approval.
- `docs/swarm/blockers.yaml`: initial blockers, decisions needed, risk owners, dependent units, and whether each blocker is fatal or non-fatal.

Do not create implementation branches, worktrees, commits, PRs, Jira issues, Jira comments, Jira transitions, or worker dispatch state while producing the packet.

## Ready For Review

Mark the packet `in_review` only when:

- MVP boundary and non-goals are explicit.
- Phase 2 or deferred epics are separated from MVP.
- Jira hierarchy is proposed but not executed.
- Initial blockers are recorded.
- The initiative contract is reviewed and every child Compound run references it.
- Child planning or execution candidates have unique run IDs and collision-free canonical state paths.
- Each proposed child has a complete invocation envelope. Existing child artifacts, when present, have passed their relevant Compound gate; new artifact-planning children are not required to exist before this gate approves their launch.
- Shared initiative, roadmap, and ADR artifacts have one revision that every planned isolation target can read.
- Concurrency policy and worker caps are written.
- Implementation start criteria are checkable.
- Verification and review gates are named.
- Every artifact listed in `documentation_gate.source_artifacts` exists or the absence is intentionally explained in the review packet.

## Review Packet Output

When planning finishes, stop with:

```text
Documentation status: in_review

Artifacts:
- docs/product/roadmap.md
- docs/jira/seed-plan.md
- docs/swarm/swarm-startup.md
- docs/swarm/queue-state.yaml
- docs/swarm/blockers.yaml

Review focus:
- MVP boundary
- Phase 2 epics
- Proposed Jira hierarchy
- Initial blockers
- Concurrency policy
- Implementation start criteria

Blocked until:
- User approves the documentation packet or requests changes.
```

## Feedback And Revision

For `document-revise`:

- Read the user's feedback and update only documentation packet artifacts.
- Append a short `feedback_log` entry in `documentation_gate`.
- Set `status: changes_requested` while revisions are incomplete.
- Set `status: in_review` when revised artifacts are ready for another review.
- Keep Jira, worker, code, branch, PR, and release state untouched.

## Approval

For `document-approve`:

- Require explicit user approval such as "approve documentation", "approved, seed Jira", or equivalent.
- Materialize a receipt over every `approval_artifacts` entry with
  `scripts/materialize_approval_receipt.py`, binding it to the digest of the
  root-observed user approval event. The event digest must come from the
  trusted conversation handoff, never from the receipt being created.
- Apply `approve-documentation` with `scripts/transition_swarm_state.py`; it
  validates current artifact bytes before setting status, approver, timestamp,
  receipt path, and packet digest.
- Preserve `source_artifacts` and `feedback_log`.
- After approval, Jira seed/drain, wave planning, dispatch, and release handoff may proceed only through their own gates.

## Forbidden Before Approval

The restrictions below apply when this documentary gate is required by the
source-work criteria above or already exists for the active initiative.

An action-specific request does not waive a gate that applies to rough source
work. A unit is outside this gate only when it was already execution-ready,
the user explicitly authorized that bounded unit, and it was not derived from
the gate-required initiative. If that unit enters persistent queue state,
record the validated unit-scoped exemption described in
`queue-state-schema.md`.

While the gate applies, do not:

- Seed, create, update, comment on, link, or transition Jira issues.
- Create executable queue state such as `running` units or active wave history.
- Dispatch Planner, Implementer, Reviewer, Fixer, Integrator, or Documenter workers for execution.
- Mutate product code, tests, configs, or generated artifacts.
- Create branches, commits, pushes, PRs, reviewer requests, merge actions, or release handoffs.

Allowed without approval:

- Create or revise documentation packet artifacts.
- Record blockers and decision needs.
- Propose Jira hierarchy without executing it.
- Propose worker waves without dispatching them.
