---
name: krt-swarm-seneschal
description: Coordinate several ready work units across parallel or sequential workers (Codex subagents, Muse Code, Claude subagents, or nested krt-compound-master runs), then reconcile the combined diff and hand it to release. Use when the user asks for a swarm, a worker wave, parallel workers, or to split work across multiple agents, or to resume or report such a run. Do not use for a single task (use krt-compound-master or just do it), for roadmaps or backlog planning (krt-delivery-navigator), Jira administration, or shipping (krt-release-marshal).
---

# KRT Swarm Seneschal

Coordinate several units of work so the combined result is correct, reviewable,
and ready for release: plan ready units, dispatch bounded workers, reconcile
what they actually changed, and report. Read
[references/safety.md](references/safety.md) before any mutation.

## Entry decision

- One clear task with one implementation owner stays with the primary agent,
  however large it is, even if the user says "swarm". Say so briefly and do it
  directly (or through `krt-compound-master`); don't build a wave or a run
  record for it. Add a specialist reviewer for a named risk if needed.
- Use a wave when several ready units benefit from isolation, concurrency,
  shared dependency tracking, or consolidation.
- A rough initiative needs settled scope, acceptance, and decisions first; send
  it to `krt-delivery-navigator` or `krt-requirements-weaver`. Don't invent a
  planning packet for a ready unit the user has already authorized.

## Plan

Inspect live repository state, the source work, and any existing run record. For
each unit settle: objective, owned paths, acceptance criteria, focused checks,
dependency base, and stop condition. Reject a unit that lacks checkable
acceptance or safe ownership; keep it visible as blocked and continue the rest.

- Start with one mutable worker; run two at once only when ownership and
  dependencies are disjoint. Two is the default ceiling.
- Serialize units that overlap on auth, data, migrations, public contracts,
  central models, generated files, dependencies, or lockfiles, even if their
  file lists differ. Parallel edits there conflict in ways tests miss.
- Classify assurance by the consequence of a mistake, not by size:
  - routine: focused checks plus your inspection of the final diff;
  - material behavior or compatibility: one independent reviewer with the
    candidate diff and a named question;
  - auth, privacy, crypto, data integrity, migration, public contract,
    production: specialist review (`krt-security-sentinel` for security) and
    independent validation of the named invariant;
  - destructive, irreversible, or legal/compliance: separate reviews for each
    risk plus explicit approval.

## Choosing workers

The user's preferred routing:

- **Muse Code** (`krt-muse-artificer`) for fast units (confirmed edit path,
  exact files, closed decisions, named checks) and for standard units whose
  product and architecture decisions are settled. If Muse or its model is
  unavailable, choose another worker before dispatch; never swap the worker
  under a running assignment.
- **Codex Luna workers** (GPT-6): `luna_worker` for fast and standard units;
  for deep units (ambiguous diagnosis, cross-cutting or risky surfaces) run
  `luna_xhigh_discovery_worker` read-only first, then `luna_xhigh_worker` on
  the confirmed path. Profiles live in `assets/codex-workers/`; copy any
  missing one into the project's `.codex/agents/` or `~/.codex/agents/`.
- In Claude Code, use subagents with the same assignment shape.
- **Nested `krt-compound-master`** when a unit needs its own plan, implement,
  verify, and review loop. Pass `orchestrator:seneschal`, a stable `run-id`, a
  unique `state-path`, `interaction:brokered`, the assigned unit, the shared
  initiative contract if any, and dependencies. A mutating child counts as one
  worker slot and owns its own state; you track only its path, status, and
  revision.

Deep, ambiguous, or high-risk decisions never go to Muse or a fast worker.

## Dispatch

Give each worker a short assignment: outcome, owned paths, read-only context,
acceptance criteria, focused checks, dependency base, forbidden actions, and
what to return. Workers edit only owned paths and never commit, push, merge,
touch Jira, or manage worktrees.

You own worktrees and consolidation. Concurrent mutable workers get separate
worktrees with disjoint ownership; a single serial worker can use one isolated
checkout when that protects existing changes. Record each starting revision.
Read-only reviewers don't need a worktree unless isolation buys something.

## Reconcile

Inspect each worker's real changed paths; worker reports are claims. Bring the
accepted changes together into one candidate, normally the user's checkout as
uncommitted changes on its current branch unless the user asked for something
else, because that is what Release Marshal ships. Check every acceptance
criterion, then run the aggregate or CI-equivalent suite once on that combined
candidate; a wave isn't release-ready until you have seen it pass there. Reuse a
passing result only when the command, base, and relevant content are unchanged.

Broker decisions from nested children: settle shared ones in the initiative
contract and give every affected child the answer and current revision. Give a
fixer one bounded defect cluster, then re-inspect. Mark each unit `ready`,
`needs-fix`, `blocked`, `deferred`, or `split-required`, and continue
independent work around local blockers.

Before deleting a worktree, confirm its resolved path and that its changes are
in the consolidated candidate. Keep failed or disputed worktrees for diagnosis.
Never delete unregistered or unrelated workspaces.

## Run record

For a short interactive run, the conversation is the record. Persist one file
only when the run spans sessions or waves, or needs an audit trail:
`docs/orchestration/seneschal/<run-id>.md`, updated in place.

```text
Run: <id> | base: <ref> | authority: <scope or ledger>
Unit | worker | owned paths | depends on | checks | status | next action
Combined diff: <base..revision>
Aggregate checks: <command, result, revision, or gap>
Risk reviews: <risk, reviewer, revision, result>
Release: <ready | blocked | handed off; pending approval>
```

Reuse existing work-package and Jira IDs. Don't add contracts, manifests,
registries, or timing logs unless a tool actually needs them.

## Release and authority

Hand the reconciled, verified result to `krt-release-marshal`; it owns commits,
pushes, PRs, reviewers, Jira transitions, and merges. Follow the PR-sizing,
stack-cap (2–3 open), and Jira-per-review-unit conventions in
`krt-compound-master`. Don't poll CI; investigate breakages as their own task.

Earlier user authorization holds for its stated scope; ask for anything beyond
it. Local implementation permission never implies external or destructive
authority. Unattended runs need an active autonomy ledger
(`krt-release-marshal/references/autonomy-ledger-schema.md`); record uncovered
external actions as blocked and keep doing local work.

## Status and closeout

Answer status from the run record and live Git state without creating state.
Close out with units and outcomes, the verification and review evidence you
observed yourself, blockers, worktree or branch references, and one next action.
