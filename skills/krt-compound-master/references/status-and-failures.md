# Status And Failures

Use this reference when updating `docs/orchestration/compound-master-state.md`, setting statuses, or producing closeouts.

## State Fields

Track:

- Initiative, mode, date.
- Resolved roles and aliases.
- Runtime adapter/delegation availability.
- Autonomy mode and package autonomy contracts.
- Delegation decisions and telemetry: selected mode, reason, roles used, read-only/mutating classification, autonomous decisions made, escalations avoided or raised, outcome, confidence, approximate duration, and loop effect.
- Source docs and context readiness result.
- State archive status: compact state path, archive snapshot path, and whether `krt-state-archivist` completed or the run used a degraded inline/no-archive path.
- Roadmap, brainstorm, planning input, plan, and work-package paths. Work packages should be grouped by roadmap item folder under `docs/work-packages/RDM-###-<roadmap-item-slug>/`.
- Review status for each gate artifact: roadmap, planning input, plan, and work package. Track `pending`, `passed`, `fix-needed`, or `blocked` separately from artifact creation status.
- Plan implementation units included in the selected package, with per-unit status: pending, in-progress, implemented, verified, skipped, or blocked.
- Dependency waves.
- Branch names and base branches.
- Impact Scan status: required yes/no, changed contracts, scan patterns, consumers found, contract-drift tests searched, required consumer tests, run/skipped results.
- Surface-aware verification results, code-review status, Security Watch notes, security review status, review fan-out roles, deduplicated findings, and advisory findings.
- Jira URLs, PR URLs, reviewers, CI break-prevention evidence, and CI incident/escalation reports when a failure is surfaced.
- Blockers and required user decisions.
- Agent assumptions and safe local decisions that affected implementation, verification, or review.

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
blocked
completed
```

## Failure Behavior

Stop and write the blocker into `compound-master-state.md` when:

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
- Review blockers remain after three loops.
- Security review is required after the work-review loop and P0/P1 findings remain unresolved, or a P2 finding affects auth, tenant isolation, secrets, public API security, PII, supply chain, or deployment exposure.
- Branch base is ambiguous or would degrade the git tree.
- Jira is required but configuration is missing.
- PR handoff would duplicate a PR or target the wrong base.
- The resolved `work` role already shipped and `krt-release-marshal` would duplicate it.
- A CI failure is surfaced by the user or release workflow and remains untriaged, package-owned without a fix plan, external/unknown without evidence, or requires a user-approved bypass.

Tell the user exactly what input or action is needed before continuing.

## Closeout Shape

Every closeout must include:

- Current phase and status.
- Artifact/state paths written or updated.
- What is ready now.
- What is blocked, or "No blockers".
- Recommended next action.
- Exact next invocation or command when one exists.

For review-blocked closeouts, also include latest findings path, unresolved findings grouped by severity, verification status, and the recommended resolver invocation.

For security-blocked closeouts, include the security finding evidence, affected asset/actor, required remediation, verification path, and whether `krt-security-sentinel` or a fallback reviewer produced the finding.

For shipping-blocked closeouts, include the exact missing input, missing role, Jira config issue, duplicate PR, or base/branch ambiguity.

For CI-blocked closeouts, include PR URL, failing check/run, likely reason if known, ownership classification, evidence, current confidence, and the exact next action: invoke `krt-ci-questor`, provide missing run/log context, or approve a focused fix/bypass decision.
