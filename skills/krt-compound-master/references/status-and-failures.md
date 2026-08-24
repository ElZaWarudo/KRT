# Status And Failures

Use this reference when updating the resolved Compound Master state path, setting statuses, or producing closeouts. Standalone runs default to `docs/orchestration/compound-master-state.md`; Seneschal children require a collision-free per-run state path.

## State Fields

Track:

- Initiative, mode, date.
- Parent orchestrator, run ID, interaction mode, canonical state path, inherited initiative contract, target roadmap item, artifact namespace, and last parent decision applied.
- Resolved roles and aliases.
- Runtime adapter/delegation availability.
- Autonomy mode and package autonomy contracts.
- Autonomous ledger path, contract ID, contract status, allowed mutation classes, expiry, last contract hash checked, latest audit event hash, and current executor mode (`manual-required`, `validation-only`, or `executor-enabled`) when autonomous mode is requested.
- Delegation decisions and telemetry: selected mode, reason, roles used, read-only/mutating classification, autonomous decisions made, escalations avoided or raised, outcome, confidence, approximate duration, and loop effect.
- Source docs and context readiness result.
- State archive status: compact state path, archive snapshot path, and whether `krt-state-archivist` completed or the run used a degraded inline/no-archive path.
- Roadmap, brainstorm, planning input, plan, and work-package paths. Work packages should be grouped by roadmap item folder under `docs/work-packages/RDM-###-<roadmap-item-slug>/`.
- Review status for each gate artifact: roadmap, planning input, plan, and work package. Track `pending`, `passed`, `fix-needed`, or `blocked` separately from artifact creation status.
- Plan implementation units included in the selected package, with per-unit status: pending, in-progress, implemented, verified, skipped, or blocked.
- Dependency waves.
- Reviewability Gate result: chosen granularity, reviewer-experience rationale, and whether the decomposition passed before execution.
- Open stacked-PR depth per chain, the cap (target <=2, max 3), and the at-cap action taken: wait-for-parent-merge or collapse-to-integration-base.
- Per-open-PR review-finding register and downstream-fix notes (`addresses finding from PR #X`) so cross-PR feedback stays traceable.
- PR-to-Jira unit mapping: for each PR, the review units it covers, whether Jira is a standalone `Tarea` or a parent plus per-review-unit subtasks, the subtask keys backlinked, and the transition fan-out applied.
- Branch names and base branches.
- Impact Scan status: required yes/no, changed contracts, scan patterns, consumers found, contract-drift tests searched, required consumer tests, run/skipped results.
- Surface-aware verification results, code-review status, Security Watch notes, security review status, review fan-out roles, deduplicated findings, and advisory findings.
- Jira URLs, PR URLs, reviewers, CI break-prevention evidence, and CI incident/escalation reports when a failure is surfaced.
- Autonomous PR/Jira snapshots: PR URL, Jira URL, reviewer approval status, required-check summary, merge eligibility, merge outcome, Jira completion eligibility, transition outcome, and audit event links. These are history and resume hints, not permission authority.
- Jira policy and posture: required/optional/skip, existing issue context, role/config availability, created/reused URL, or non-blocking omitted reason.
- Blockers and required user decisions.
- Agent assumptions and safe local decisions that affected implementation, verification, or review.
- Execution closeout: current phase, remaining actions, terminal readiness,
  last required command, unowned failures, and budget rounds consumed.


## Freshness Requirements

- Treat the resolved canonical state path as the live resume truth. Update it at every phase/gate transition, blocker or unblock, package/review-unit selection, branch/base change, verification/review/security result, PR/Jira mutation, and next-invocation change.
- Never let two active Compound runs share one mutable state path. Seneschal snapshots are observations and must not replace child state.
- When a roadmap, brainstorm, planning input, plan, or work package changes status or operational facts, update that artifact in the same turn as the state file. Do not leave one current and the other stale.
- Before closeout, resume, review handoff, or release handoff, reconcile state and the active artifact set against repo reality: status, blockers, next action, branch/base, dependencies, verification, review/security posture, and PR/Jira references.
- If implementation or review made adjacent product/operator/API docs stale, update them or record the explicit split/blocker path; never leave the drift implicit.
- Do not edit CE plan bodies as progress checklists; progress belongs in state, active work-package status, task tracking, commits, Jira, and PRs.
- If related docs must be split out, keep the destination and next action visible in state/closeout so documentation is not orphaned.

## Status Values

Use these statuses in state and work-package frontmatter:

```text
context-blocked
roadmap-ready
brainstorm-ready
roadmap-review-passed
planning-input-review-passed
plan-ready
plan-review-passed
package-ready
package-review-passed
execution-ready
in-progress
implementation-complete
review-fix-needed
review-passed
security-watch-active
security-review-needed
security-blocked
pr-handoff-started
pr-opened
ci-prevention-ready
ci-incident-reported
ci-incident-escalated
ci-blocked
autonomous-validation-only
autonomous-blocked
autonomous-audit-reconcile
decision-needed
blocked
completed
```

Worker terminal status is a separate, smaller vocabulary:

- `done`: all contracted work and required checks resolved.
- `done_with_baseline_gaps`: only declared baseline or clearly unowned failures remain.
- `needs_review`: allowed rounds are exhausted or one budget extension needs approval.
- `blocked`: a required decision or external capability is missing.

Do not translate every baseline imperfection into `blocked`.

## Terminal Closeout Gate

Before returning, write and reconcile these fields in the canonical state and
worker result:

```yaml
phase: closeout
remaining_actions: []
terminal_ready: true
acceptance_criteria_resolved: true | false
last_required_command: <exact command or none>
unowned_failures: []
```

Set `terminal_ready: true` after every manifest command was attempted or has a
concrete skip reason, state matches repo reality, and no worker action remains.
It means ready to return, not successful acceptance. Set
`acceptance_criteria_resolved: true` for `done` and
`done_with_baseline_gaps`. `needs_review` and `blocked` may use false. When
`terminal_ready` is true and `remaining_actions` is empty, the next mandatory
action is to return. Another read, search, command, review, or polish pass
violates the contract.

If an allowed round is exhausted first, reconcile state and return
`needs_review`; do not silently begin a new round. If a decision or external
capability is missing, return `blocked`. Baseline or unowned failures use
`done_with_baseline_gaps` when the owned acceptance criteria are resolved.

## Failure Behavior

Stop and write the blocker into the resolved canonical state path and the affected active artifact when that artifact is the blocked execution surface:

- Required artifact roles are missing.
- Execution roles are missing for requested execution.
- A required role cannot be resolved by canonical name or documented runtime alias.
- Requested delegation or parallel execution lacks safe isolation.
- The resolved work role cannot support implementation-only/no-shipping behavior.
- PR/Jira skills are missing for shipping.
- Context is insufficient.
- Product decisions cannot be inferred.
- Plans lack units/dependencies/tests after review.
- A package changes an API contract, endpoint, binding, shared helper, schema, payload, auth/tenant/ownership behavior, or test fixture contract and lacks a complete Impact Scan.
- Roadmap, plan, or code review blockers remain after three loops.
- Security review is required after the work-review loop and P0/P1 findings remain unresolved, or a P2 finding affects auth, tenant isolation, secrets, public API security, PII, supply chain, or deployment exposure.
- Branch base is ambiguous or would degrade the git tree.
- A stacked chain would exceed the open-PR cap and neither a parent merge into the integration base nor a collapse onto it is available.
- The Reviewability Gate cannot be met within the cap and the packages cannot be restructured without a user decision.
- Jira is required but role, context, or configuration needed for safe mutation is missing.
- Autonomous external mutation is requested but the ledger is missing, expired, revoked, superseded, scope-mismatched, missing issuer binding, or has a contract/audit hash mismatch.
- Autonomous external mutation is requested but the executor, validator, live-state input, runtime enforcement boundary, or pre-execution audit write is unavailable.
- PR handoff would duplicate a PR or target the wrong base.
- The resolved `work` role already shipped and `krt-release-marshal` would duplicate it.
- A CI failure is surfaced by the user or release workflow and remains untriaged, package-owned without a fix plan, external/unknown without evidence, or requires a user-approved bypass.

Tell the user exactly what input or action is needed before continuing.

When `interaction:brokered`, replace the direct user question with the
structured decision request from `nested-orchestration.md`, return it to
Seneschal, and continue only safe work independent of that decision.

## Closeout Shape

Every closeout must include:

- Current phase and status.
- Artifact/state paths written or updated.
- What is ready now.
- What is blocked, or "No blockers".
- Recommended next action.
- Exact next invocation or command when one exists.
- The terminal fields, consumed execution budget, last required command, and
  any unowned failures.

For review-blocked closeouts, also include latest findings path, unresolved findings grouped by severity, verification status, and the recommended resolver invocation.

For security-blocked closeouts, include the security finding evidence, affected asset/actor, required remediation, verification path, and whether `krt-security-sentinel` or a fallback reviewer produced the finding.

For shipping-blocked closeouts, include the exact missing input, missing role, Jira config issue, duplicate PR, or base/branch ambiguity.

For autonomous-blocked closeouts, include ledger path, contract ID, mutation class, target, validator block reasons, latest audit event hash, whether safe independent work may continue, and the exact manual approval or reconciliation needed.

For CI-blocked closeouts, include PR URL, failing check/run, likely reason if known, ownership classification, evidence, current confidence, and the exact next action: invoke `krt-ci-questor`, provide missing run/log context, or approve a focused fix/bypass decision.
