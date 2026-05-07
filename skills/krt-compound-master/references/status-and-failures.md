# Status And Failures

Use this reference when updating `docs/orchestration/compound-master-state.md`, setting statuses, or producing closeouts.

## State Fields

Track:

- Initiative, mode, date.
- Resolved roles and aliases.
- Runtime adapter/delegation availability.
- Delegation decisions and telemetry: selected mode, reason, roles used, read-only/mutating classification, outcome, confidence, approximate duration, and loop effect.
- Source docs and context readiness result.
- Roadmap, brainstorm, plan, and work-package paths.
- Plan implementation units included in the selected package, with per-unit status: pending, in-progress, implemented, verified, skipped, or blocked.
- Dependency waves.
- Branch names and base branches.
- Impact Scan status: required yes/no, changed contracts, scan patterns, consumers found, required consumer tests, run/skipped results.
- Verification results, code-review status, review fan-out roles, deduplicated findings, and advisory findings.
- Jira URLs, PR URLs, reviewers.
- Blockers and required user decisions.

## Status Values

Use these statuses in state and work-package frontmatter:

```text
context-blocked
roadmap-ready
brainstorm-ready
plan-ready
package-ready
execution-ready
in-progress
implementation-complete
review-fix-needed
review-passed
pr-handoff-started
pr-opened
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
- Branch base is ambiguous or would degrade the git tree.
- Jira is required but configuration is missing.
- PR handoff would duplicate a PR or target the wrong base.
- The resolved `work` role already shipped and `krt-release-marshal` would duplicate it.

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

For shipping-blocked closeouts, include the exact missing input, missing role, Jira config issue, duplicate PR, or base/branch ambiguity.
