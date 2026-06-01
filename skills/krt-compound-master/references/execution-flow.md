# Execution Flow Router

Load this file at the start of execution. It is a router, not the full execution manual.

## Load By Need

| Need | Load |
|---|---|
| Wave planning, dependency classification, delegation, worker prompt | `execution-delegation.md` |
| Impact Scan, consumer tests, verification ladder, surface-aware evidence | `impact-verification.md` |
| Code review loop, security watch/review, optional reviewer fan-out, CI escalation | `review-security-ci.md` |
| Release Marshal handoff prompt and stacked PR handling | `release-handoff.md` |
| State transitions, blockers, closeouts | `status-and-failures.md` |
| Autonomous ledger/executor policy | `autonomous-mode.md`, `autonomous-flow-matrix.md` |

## Execution Skeleton

1. Select one review unit, not an entire work package, unless the package explicitly has a single integrated review unit.
2. Classify the selected review unit: independent, dependent, overlapping, high-risk, and production-sensitive.
3. Resolve delegation/autonomy and whether the work runs inline or through a scoped worker.
4. Run implementation-only work for the selected review unit.
5. Run/attempt review-unit verification.
6. Run Impact Scan when contracts, schemas, APIs, bindings, auth/tenant behavior, shared helpers, payloads, or fixtures changed.
7. Run code review and fix loop.
8. Run security review for high-risk review units.
9. Record CI break-prevention evidence.
10. If autonomous external mutation is requested, validate ledger/executor readiness and record executor mode before handoff.
11. Handoff the selected review unit to `krt-release-marshal`.

## Review-Unit Discipline

- A work package is a delivery container; a review unit is the normal PR/Jira unit.
- Execute one review unit at a time unless coupling makes that less reviewable and the rationale is recorded.
- Keep orchestration docs and generated artifacts separate when they would obscure functional review, but do not exclude related documentation from the branch/PR solely to make the diff look cleaner. When the docs explain the change, stack context, or stale adjacent behavior, keep them with the review unit unless the user asks to defer them.
- Do not "solve" review noise by parking related documentation in stash, another worktree, or a side branch without an explicit user-approved split plan and a visible follow-up path.
- Keep stack/dependency context in state or handoff notes, not PR body.
