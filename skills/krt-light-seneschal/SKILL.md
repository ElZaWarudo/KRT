---
name: krt-light-seneschal
description: Experimentally coordinate multiple ready work units with small worker assignments, risk-based review, and one concise run record. Use when the user requests the light Seneschal or wants to compare it with krt-swarm-seneschal. Do not use for ordinary single-task implementation.
---

# KRT Light Seneschal

Coordinate the same delivery outcomes as `krt-swarm-seneschal`: plan ready units,
dispatch bounded work, reconcile the combined result, and report status. This is
an experimental alternative to its orchestration protocol. Keep the existing
Seneschal skill and its state untouched; do not run both protocols on the same
active work package without an explicit migration decision.

## Entry decision

- A clear task with one implementation owner stays with the primary agent,
  regardless of size or technical depth. Add a specialist for a named review
  risk without creating a worker wave.
- Use this skill when multiple ready units benefit from independent execution,
  isolation, shared dependency tracking, or consolidation. Start with one
  mutable worker; use two only when ownership and dependencies are disjoint.
- A rough initiative needs settled scope, acceptance criteria, and decisions
  before implementation. Use the project's planning owner for that work. Do
  not manufacture a planning packet for a ready unit the user has authorized.

## One run record

For a short interactive run, the task conversation is the record. Persist one
run file only when the work spans sessions or waves, needs shared queue state,
or needs an audit trail. Put it at
`docs/orchestration/light-seneschal/<run-id>.md`; update it in place. Use one row
per unit and concise notes for decisions that affect the run:

```text
Run: <id> | source/base: <ref> | authority: <scope or ledger>
Unit | owner/paths | depends on | acceptance/checks | status | finding/next action
Combined diff: <base and current revision or digest>
Aggregate checks: <command, result, revision; or justified gap>
Risk reviews: <risk, independent actor, reviewed revision, result>
Release: <ready, blocked, or handoff; remaining approval or authorization>
```

Reuse existing work-package and Jira IDs. Do not create a contract, envelope,
terminal schema, observation, patch manifest, findings registry, timing log,
or review plan by default. Add a machine-readable artifact only when a tool,
external worker runtime, or consequential boundary actually needs it. State
what failure that artifact prevents in the run record.

## Plan

Inspect the live repository state, the source work, dependencies, and any
existing run record. For each unit, settle its objective, owned paths,
acceptance criteria, focused checks, dependency base, and stop condition.
Serialize overlapping auth, data, migrations, public contracts, central
models, generated files, dependencies, and lockfiles. Keep blocked units
visible and continue independent ready work. For nested Compound Master work,
read its canonical state and gates; this run record is only a projection.

Classify assurance from the consequence of a mistake, not task size:

- Routine: focused checks and primary-agent inspection of the final diff.
- Material behavior or compatibility: one independent reviewer with a named
  question and the exact candidate diff.
- Auth, privacy, cryptography, data integrity, migration, public contract,
  production, or research-evidence integrity: relevant specialist review and
  independent validation of the named risk.
- Destructive, irreversible, legal/compliance, or publication-critical work:
  coordinated review of distinct risks and the applicable approval gate.

## Compound Master children

Send a ready implementation unit to a bounded worker directly. Use
`krt-light-compound-master` when one bounded unit needs its own planning,
implementation, verification, and review loop. Use full
`krt-compound-master` only when the unit needs formal initiative artifacts or
its multi-stage quality pipeline. For either child, pass
`orchestrator:seneschal`, a stable `run-id`, a unique `state-path`,
`interaction:brokered`, the assigned roadmap item or work package, shared
initiative contract if one exists, and dependencies. Give a full Compound
Master child `parallel:false`. Count any mutating child as one worker slot.
The child owns its canonical state, artifacts, and internal checks; the light
parent records only their paths, current status, and observed revision.

Broker child decision requests through the parent. Resolve shared decisions in
the initiative contract or applicable decision artifact, then give every
affected child the recorded answer and current revision. Inspect the child's
actual diff, verification, review, and applicable inner gates before accepting release readiness. The
child returns a release-ready packet to the parent; only the parent reconciles
siblings and hands the combined work to `krt-release-marshal`. Follow the
child's own nested-run instructions. For a full Compound Master child, use
[`krt-compound-master` nested orchestration](../krt-compound-master/references/nested-orchestration.md).

## Dispatch

Give each worker a short assignment: outcome, owned paths, read-only context,
acceptance criteria, focused checks, dependency base, forbidden actions, and
what to return. Workers may edit only owned paths. They do not commit, push,
merge, alter Jira, or manage worktrees.

The primary agent owns worktrees and consolidation. Give concurrent mutable
workers separate worktrees and disjoint ownership. A serial worker can use one
isolated checkout when it protects existing changes. Record the starting Git
revision and preserve unrelated user work. Do not create a new worktree for a
read-only review unless isolation has a concrete benefit.

## Reconcile

Inspect the actual changed paths and consolidated diff; worker prose is not
evidence of scope or readiness. Check acceptance criteria, focused command
results, and the risk review required above. Run aggregate or CI-equivalent
checks once on the consolidated candidate. Reuse a passing result only when
its command, base, and relevant content are unchanged. After a fix, run its
focused check; repeat aggregate checks or review only when the change makes
earlier evidence stale or changes the reviewed risk boundary.

Record findings in the unit row. A fixer receives one bounded defect cluster.
Reinspect the resulting diff and close or defer each material finding. Mark
units ready, needs-fix, blocked, deferred, or split-required. Report the
combined result and remaining risks before release handoff.

## Status and downstream actions

Report live unit states, blockers, evidence, and the next action from the run
record and current Git state; do not create state merely to answer status.
Use the selected Jira provider skill for Jira reads or mutations. Use
`krt-release-marshal` for commits, pushes, PRs, reviewer requests, transitions,
and merge. An earlier user authorization remains valid for its stated scope;
obtain approval only for an action that lacks authorization. Do not infer
external or destructive authority from local implementation permission.

For an unattended run, use the canonical Compound Master autonomy ledger and
validator before ledger-governed mutations. Continue independent local work
when an external action is not covered; record the blocked action. Do not
replace an applicable planning or approval gate with the run record.

Before deleting a worktree, verify its resolved path and that its changes are
durable in the consolidated candidate. Preserve failed or disputed workspaces
for diagnosis. Never delete unrelated or unregistered workspaces.

## Experiment report

When comparing this protocol with `krt-swarm-seneschal`, use the same work
package and risk classification. Count artifacts, tool calls, repeated checks,
and elapsed time from observed runs. Identify which safeguards caught a real
problem and any assurance lost. Do not claim savings from a hypothetical
walkthrough as measured results.
