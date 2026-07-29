# Blocker Ledger

Use this reference for persistent non-fatal blockers and the `blocker-review` and `blocker-resolve` modes.

## Default Path

```text
docs/swarm/blockers.yaml
```

The blocker ledger lets the swarm continue independent work when one unit needs a decision. In autonomous flow, blockers replace runtime questions: record, defer affected units, and keep draining independent work.

## Schema

```yaml
schema_version: 1
updated_at: "2026-06-30"
blockers:
  - id: BLK-2026-06-30-001
    jira_issue_key: MAP-123
    unit_id: wp-01-ru-02
    title: Clarify billing tax behavior
    wave: wave-1
    type: accounting
    risk: high
    description: Productive accounting rule is unclear for this unit.
    decision_required: Confirm the rule to implement.
    impact_if_ignored: Could implement incorrect production accounting behavior.
    affected_units:
      - wp-01-ru-02
    blocks_dependents: true
    suggested_owner: accountant
    detected_at: "2026-06-30"
    status: open
    evidence: docs/work-packages/example.md#billing-rule
    next_action: Route to accountant before production release.
    resolution:
      decided_at: null
      decided_by: null
      decision: null
      supersedes: null
```

## Required Fields

Every blocker must store:

- Jira issue key.
- Work package or queue unit ID.
- Task title.
- Blocker type.
- Brief description.
- Decision required.
- Impact if ignored.
- Affected dependent units.
- Suggested resolver.
- Detection date.
- Status.
- Evidence link or reference.
- Suggested next action.

Allowed blocker types:

```text
product, auth, data, legal, DIAN, accounting, payroll, infrastructure, security, dependency, unknown
```

Allowed suggested owners:

```text
user, product, accountant, legal, security, tech lead
```

Allowed statuses:

```text
open, answered, superseded, resolved
```

## Worker Reporting

Workers must report blockers in this shape:

```yaml
blockers:
  - type: product
    description: The expected empty-state behavior is not specified.
    decision_required: Choose whether to show an empty state or hide the module.
    impact_if_ignored: The UI could ship with the wrong product behavior.
    affected_units: []
    suggested_owner: product
    evidence: path/or/output
    next_action: Ask product for the desired behavior.
```

If the worker reports a blocker informally, the orchestrator must normalize it before updating the ledger.

## Decision Requests

Treat a nested Compound worker's question as a decision request, not a direct
user interaction. Normalize it into the blocker ledger:

```yaml
blockers:
  - id: DEC-2026-07-28-001
    unit_id: authentication-RU1
    compound_run_id: customer-identity-auth
    compound_state_path: docs/orchestration/compound-master/customer-identity-auth/state.md
    title: Decide session revocation behavior
    type: product
    risk: high
    description: Password-change session behavior is not defined.
    decision_required: Choose whether existing sessions are revoked.
    question: Should password changes revoke existing sessions?
    why_not_inferable: The initiative contract does not define session validity.
    options:
      - id: revoke-all
        consequence: Stronger security; signs out every device.
      - id: keep-existing
        consequence: Less friction; existing sessions remain valid.
    recommendation: revoke-all
    safe_fallback: Block affected units.
    canonical_target: docs/plans/customer-identity/initiative-requirements.md
    affected_units: [authentication-RU1, session-management-RU2]
    status: open
    evidence:
      - docs/plans/customer-identity/initiative-requirements.md
    resolution:
      decided_at: null
      decided_by: null
      decision: null
      canonical_revision: null
```

Before asking:

- deduplicate requests with the same canonical target and decision surface;
- merge conflicting worker proposals into one question;
- identify every affected and dependent unit;
- order open questions by risk and the number of units they unblock;
- ask one decision at a time in manual interactive flow;
- ask only through Seneschal, never through child workers.

After the user answers:

1. Persist the decision in `canonical_target` or a new shared ADR.
2. Record the canonical revision in the resolution.
3. Refresh every affected isolation target to that revision.
4. Mark the blocker `answered` or `resolved`.
5. Refresh affected Compound states and queue projections.
6. Revalidate invalidated discovery, plan, package, and execution gates.
7. Resume the original child when possible; otherwise resume a replacement from
   its canonical state path.

In autonomous flow, keep requests open, defer affected work, and continue
independent units without asking.

## Reconciliation Rules

When a blocker affects only one unit:

- Add or update the blocker ledger.
- Mark that unit `blocked` or `deferred`.
- Continue with other ready independent units.

When a blocker affects a shared dependency, public contract, auth, data, or central technical foundation:

- Add or update the blocker ledger.
- Stop dispatch for dependent units.
- Continue only with units proven independent.

When a blocker affects security, real DIAN compliance, productive accounting, productive payroll, or legal production exposure:

- Record it as high risk.
- Require resolution before production release.
- Continue only with unrelated units that cannot be affected by the decision.

In manual flow, ask only when no ready independent work remains, the decision blocks the full wave, or the user requested interactive approval for that class of decision.

In autonomous flow, do not ask. Stop only when no independent ready work remains or every remaining path would violate the autonomy ledger. Otherwise keep working and leave the blocker for the morning packet.

## Wave Selection Rules

Before selecting every wave:

- Read `docs/swarm/blockers.yaml`.
- Exclude units with open blockers.
- Exclude units that depend on units with open blockers.
- Exclude units listed in `affected_units` of open blockers.
- Permit unrelated units to continue.

## blocker-review Mode

`blocker-review` must:

- List open blockers grouped by type.
- Include Jira key, unit ID, wave, title, suggested owner, and next action.
- Identify high-risk blockers.
- Identify which decisions would unblock the most units.
- Avoid direct Jira mutation. Manual flow routes confirmed mutations through the selected Jira provider skill; autonomous flow routes ledger-covered mutations through that same selected skill.

Review output shape:

```text
Open blockers by type:
- accounting
  - MAP-123 / wp-01-ru-02: <title>
    Owner: accountant
    Blocks: 3 units
    Decision: <decision_required>
Best unlocks:
- Resolve BLK-... to unblock <units>
```

## blocker-resolve Mode

`blocker-resolve` takes a user decision and:

- Finds the blocker by ID, Jira key, or unit ID.
- Records the decision, resolver, and date.
- Persists the decision in the canonical shared or item artifact before a child resumes.
- Records the canonical artifact revision used by resumed Compound runs.
- Sets status to `answered` or `resolved` as appropriate.
- Marks affected units as candidates for readiness check in `docs/swarm/queue-state.yaml`.
- Does not update Jira, comment, transition, or backlink directly. Manual flow requires confirmation through the selected Jira provider skill; autonomous flow requires ledger coverage through that same selected skill.

Resolution entry:

```yaml
resolution:
  decided_at: "2026-06-30"
  decided_by: user
  decision: Use the confirmed accounting rule.
status: answered
```
