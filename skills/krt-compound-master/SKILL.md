---
name: krt-compound-master
description: Take one bounded software work package from context through plan, implementation, verification, risk-based review, and release handoff, keeping one compact state record. Use when the user asks to deliver, implement, or fix something end to end and get it ready for review or a PR, to split a work package into PRs and Jira tickets or execute one of its review units, or to resume or report a Compound Master run; also runs as a child of krt-swarm-seneschal. Use krt-swarm-seneschal for several parallel units, krt-release-marshal when only shipping existing changes, and krt-delivery-navigator for roadmaps or project plans. Runtime aliases may expose this as krt:compound-master.
---

# KRT Compound Master

Deliver one bounded software outcome: clarify, plan, implement, verify, review,
and hand release to `krt-release-marshal`. The point is a change a human can
review and merge with confidence, not a pile of planning documents. Read
[references/safety.md](references/safety.md) before any mutation.

## Modes

Accept `mode:plan|execute|full|resume|status`, an optional work-package or
review-unit path, and when nested: `orchestrator:seneschal`, `run-id`,
`state-path`, `initiative-contract`, `interaction:brokered`.

- `plan`: produce or refresh the execution brief and stop before code.
- `execute`: implement a ready brief or reviewed work package.
- `full` (default when the request authorizes both): plan, then execute.
- `resume`: check live repository facts against the state record, then continue.
- `status`: report evidence and next action without changing anything.

A clear one-line fix does not need this skill's ceremony; just do it well and
hand off.

## Context and decisions

Inspect the repository, current changes, the request, and existing requirements
or work packages. Preserve unrelated work. Settle what the repository can
answer; raise the rest. Do not invent product behavior, auth or data rules,
retention or deletion semantics, compatibility guarantees, or release policy:
those are the user's calls, and a wrong guess ships silently. Ask once, with a
recommendation and a safe default, and continue any independent work meanwhile.

Reuse an approved initiative contract or assigned roadmap item; do not create a
competing roadmap. Roadmaps and project plans belong to
`krt-delivery-navigator`.

## One state record

For a short run, the conversation is the state. Persist one Markdown file only
when the run must survive a session, is nested, or needs an audit trail. A
Seneschal parent supplies a unique `state-path`; otherwise use
`docs/orchestration/compound-master/<run-id>.md`. Keep it current:

```text
Run / owner / base / assigned unit / phase
Scope, non-goals, acceptance, dependencies, open decisions
Owned paths and approach
Checks: command, result, revision, gaps
Review: risk, reviewer, revision, findings
Status: ready | needs-fix | blocked | release-ready; next action
Release: PR/review-unit split, base, Jira mapping, CI gaps, approval status
```

Link an existing work package instead of copying it. Do not generate separate
roadmap, brainstorm, plan, package, and review documents just because this skill
is active.

## Review units and PRs

These are the user's conventions; follow them when splitting work:

- Size a review unit (one PR) for human reviewability and independent
  mergeability, not for atomicity or to match Jira tickets.
- Keep at most 2–3 open, unmerged PRs in one stacked chain (aim for 2). At the
  cap, wait for the bottom PR to merge, or collapse the pending chain onto the
  integration base. Never fix an over-deep stack by abandoning it for one
  mega-PR.
- When a later unit fixes something a reviewer flagged on an earlier open PR,
  carry a downstream-fix note ("addresses finding from PR #X") into the handoff.
- Jira stays at review-unit granularity: a PR covering several review units
  links one subtask per unit under a shared parent, not one collapsed task.
- Keep planning IDs, run IDs, and stack notes out of PR titles, bodies, commits,
  and branch names unless the repo requires them.
- Don't build the next artifact or PR on top of one whose review hasn't closed.

## Implement and verify

Use one primary implementer. Delegate only for a named benefit (a specialist, a
long independent unit) and give the worker exact owned paths, acceptance
criteria, focused checks, and a stop condition. Workers never commit, push, or
touch Jira.

Inspect the real diff; a worker's summary is a claim, not evidence. Run focused
checks, then the aggregate or CI-equivalent suite once on the final candidate.
Reuse a passing result only if the command, base, and relevant content are
unchanged. Check affected consumers, migrations, generated files, and type or
build steps when the change reaches them. Never report a failed or skipped
check as passing; record CI-only gaps instead of predicting green.

## Review by consequence

- Routine, reversible: your own review of the final diff.
- Material behavior or compatibility change: one independent reviewer with the
  diff and a named question.
- High-risk (auth, permissions, secrets, PII, payments, crypto, data integrity,
  migrations, public contracts, deployment, dependencies): keep a security watch
  while implementing, then run the security gate after code review passes,
  however small the diff. Invoke `krt-security-sentinel` when it is installed;
  only when it isn't, do a direct evidence-based security pass and record the
  degraded path. Blockers go back through the fix and review loop before
  release.
- Destructive, irreversible, or legal/compliance work: separate reviews for
  distinct risks and an explicit approval.

Fix material findings, rerun their focused checks, and re-inspect. Repeat
aggregate checks or review only when the fix makes earlier evidence stale. Stop
and report a blocker after bounded attempts instead of looping.

## Release handoff

Standalone: when the review loop passes, go straight to `krt-release-marshal`
with the review-unit split, base, Jira mapping, verification summary, and CI
gaps. Don't pause between a passing review and the handoff; the approval stop
for commits, pushes, PRs, and Jira lives inside Release Marshal. Do not commit,
push, open PRs, or move Jira yourself.

Don't poll CI. Prevent predictable failures before handoff (lint, types, tests
the CI runs). If CI breaks later, investigate the failing job as its own task.

A missing specialist skill (security, CI, Jira) never blocks the pipeline:
resolve an equivalent or do the step inline and note the degraded path.

## Nested under Swarm Seneschal

With `orchestrator:seneschal`, work only on the assigned unit, write only the
supplied `state-path`, run one mutable worker at most, and do not launch sibling
runs or ship. Treat the initiative contract as binding; if a shared decision
needs to change, return a decision request (question, affected units, evidence,
recommendation, safe fallback) instead of asking the user, and pause only the
affected work.

Return: state path, status, changed paths, candidate revision, checks, review
results, blockers, sibling impact, and release readiness. The parent inspects
the diff, reconciles siblings, and invokes Release Marshal.

## Authority

Implementation permission is not permission to push, open PRs, change Jira,
merge, deploy, or delete. Unattended external actions need an active autonomy
ledger (`krt-release-marshal/references/autonomy-ledger-schema.md`), validated
and executed by Release Marshal; without one, record the action as blocked and
continue local work.

## Closeout

Report phase and status, changed or written paths, checks with results, review
outcome, blockers or "No blockers", and the exact next action or invocation.
