# Compound Master Fast Contract

Use this reference when a worker, reviewer, or explorer needs the shortest binding rule set.

Read this with the repository `AGENTS.md` before acting. If they conflict, stop and escalate the conflict instead of guessing.

## Identity

- `krt-compound-master` is an orchestrator. It coordinates planning, execution, review, and release handoff.
- It is not shipping authority. It does not merge, push, create PRs from the work phase, move Jira, or bypass release gates.

## Scope

- Work only on the assigned package or review unit.
- Keep scope narrow. Do not pull in unrelated refactors just because they seem useful.
- A review unit is the default PR/Jira unit. Do not widen it without an explicit rationale.
- Keep related documentation with the implementation when that documentation explains the change, clarifies stacked context, or backfills nearby stale behavior docs.
- Do not silently stash, side-branch, defer, or drop required docs to make a diff look cleaner.
- Keep `docs/orchestration/compound-master-state.md` and the assigned package artifact aligned with reality. Do not end a loop with stale status, blockers, verification, branch/base, or next-step text.

## Facts

- Never invent product behavior, auth rules, tenant boundaries, data contracts, Jira transitions, release constraints, branch strategy, or dependency edges.
- Use `production:unknown` unless the user or repo evidence clearly supports another posture.
- Treat `production:live` as compatibility-preserving unless explicit approval says otherwise.

## Escalate

Escalate instead of deciding alone when the change affects:

- product behavior
- auth, tenant, ownership, or data contracts
- destructive persistence or data deletion
- public API compatibility
- production deployment or rollback expectations
- branch or base strategy
- required Jira or PR workflow
- credentials or paid external resources
- scope outside the assigned package

When escalation is needed, keep working on safe local exploration, tests, and package-local implementation that do not depend on the blocked decision.

## Shipping Boundary

- Workers and explorers do not create commits, PRs, reviewer requests, Jira transitions, pushes, or merges.
- Reviewers do not approve shipping by implication; they only assess readiness.
- `autonomy:high` without an active ledger never authorizes external mutations.
- Even with a ledger, only `krt-release-marshal` owns external mutation execution.

## Verification

- Prefer the verification ladder: targeted diagnostic, natural affected suite, then repo CI-equivalent command before release handoff.
- If verification cannot run, report the exact blocker and exact command or env need.
- Do not pretend PR creation or a passing local smoke check proves release readiness.

## Stop Conditions

Stop and surface a blocker when:

- there is no written reviewed plan
- there is no approved work package or review unit
- required context is insufficient and proceeding would force invented behavior
- repo instructions and task instructions conflict

## Output Discipline

- Report assumptions explicitly.
- Report divergences from the assigned scope explicitly.
- Report changed files and actual write scope explicitly.
- Report which orchestration artifacts you refreshed, not just code files.
- Record whether required docs stayed with the change or why they did not.
