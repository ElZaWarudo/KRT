---
name: krt-swarm-seneschal
description: Coordinate explicitly requested multi-worker delivery through dependency-aware planning, isolated worker waves, reconciliation, and release handoff. Use for swarm orchestration, parallel Codex workers, or multiple nested krt-compound-master runs. Do not use for one execution-ready task, generic project planning, Jira administration, or release management.
---

# KRT Swarm Seneschal

Coordinate delivery only when several work units benefit from shared planning,
isolation, parallel execution, or cross-unit reconciliation:

```text
source work -> plan -> dispatch -> reconcile -> release handoff
```

This skill coordinates other workflows. It does not replace
`krt-compound-master`, Jira provider skills, or `krt-release-marshal`.

## Entry Gate

Apply the break-even gate before creating swarm state or loading detailed
references:

1. Keep one small, execution-ready unit in the root task.
2. Route generic planning that does not require worker-wave decomposition, plus
   Jira-only, review-only, and release-only requests, to the skill that owns the
   requested outcome.
3. Use Seneschal only for multiple dependent or concurrent units, multiple
   isolated Compound Master runs, or an explicitly requested worker wave.

Before any code, repository-state, queue-state, Jira, branch, PR, or release
mutation, read [references/safety.md](references/safety.md).

## Four Operations

| Operation | Outcome |
|---|---|
| `plan` | Decide root-direct versus swarm, normalize units, close dependencies, and select the smallest safe wave. |
| `dispatch` | Launch only the admitted workers with bounded ownership, verification, and isolation. |
| `reconcile` | Inspect real changes and evidence, resolve findings or blockers, and prepare release-ready handoff. |
| `status` | Render current gates, units, blockers, and next action without mutation. |

Legacy names remain accepted as aliases, not separate pipelines:

- `design-only`, `document-plan`, `document-review`, `document-revise`,
  `document-approve`, `wave-plan`, and `jira-seed-and-drain` start in `plan`.
- `jira-team-flow`, `overnight-team-flow`, and `autonomous-team-flow` apply an
  external-source or autonomy overlay to `dispatch`.
- `resume` begins with `status`, then continues through `plan`, `dispatch`, or
  `reconcile` from observed state.
- `blocker-review` is `status`; `blocker-resolve` is `reconcile`.
- `wave-status` is `status`.

## Operating Model

### Plan

1. Inspect the repository, source work, live worker facts, and existing state.
   Before creating a wave, load `references/worktree-collaboration.md` and run
   its guarded preflight cleanup in dry-run mode. Apply cleanup only to entries
   already marked cleanup-ready by canonical state; retain and report every
   active, failed, diagnostic, or unregistered workspace.
2. Reject work that lacks checkable acceptance criteria, safe ownership, known
   dependencies, or a resolvable decision boundary.
3. Require a reviewed documentation packet before seeding Jira or dispatching
   a broad initiative, roadmap, program, or rough backlog. Do not manufacture a
   new packet for an already approved, execution-ready unit explicitly requested
   by the user; when persisted, bind that exemption to the trusted request as
   specified in `references/queue-state-schema.md`.
4. Load `references/execution-lanes.md`; classify execution difficulty and
   assurance independently.
5. Prefer the smallest useful wave. Default to at most two concurrent mutable
   implementers and serialize overlapping auth, data, migration, public-contract,
   central-model, dependency, or lockfile work.

### Dispatch

Every worker receives a bounded objective, owned paths, non-goals, acceptance
criteria, exact focused checks, stop conditions, and a finite time/action budget.
Workers do not stage, commit, switch branches, manage worktrees, push, mutate
Jira, request reviewers, open PRs, or merge.

Choose the least costly protocol that preserves the required assurance:

| Condition | Protocol |
|---|---|
| `low` assurance | Root-direct by default; use lightweight dispatch only for a named isolation, concurrency, or duration benefit. |
| `medium` assurance | Lightweight dispatch plus one focused independent reviewer. |
| `high` assurance, `deep` execution, or autonomous mutation | Executable hashed contract, root observation, focused specialist review, and independent validation. |
| `critical` assurance | High protocol plus coordinated review and explicit approval or an exact ledger grant. |

Use `references/lightweight-dispatch.md` for eligible low/medium work. Load
`references/executable-worker-contracts.md` and `references/subagent-contracts.md`
only for the advanced protocol. A worker's prose never certifies its real diff
or readiness; root owns that observation in both protocols.

### Reconcile

1. Inspect the actual diff and changed paths before trusting a worker return.
2. Capture or rerun the checks required by the selected protocol. Run aggregate
   or CI-equivalent verification once for the reconciled wave; reuse only
   content-bound passing evidence.
3. Apply only risk-triggered review. Use the findings registry and coordinated
   validators only for high or critical assurance.
4. Mark each unit `release-ready`, `needs-fix`, `blocked`, `deferred`, or
   `split-required`. Continue independent work when a blocker is local.
5. Once an invocation's patch, manifest, and required evidence are durable,
   mark its workspace cleanup-ready and immediately run the guarded cleanup.
   Preserve failed or contract-violating workspaces for diagnosis.
6. Hand release-ready work to `krt-release-marshal`; do not reproduce its
   commit, PR, Jira-transition, reviewer, or merge workflow.

### Status

Read canonical local state and live external facts when relevant. Run
`scripts/render_swarm_status.py` for the compact panel. Do not create or mutate
state merely to report status.

## Progressive Reference Router

Read the primary reference for the active operation first. Load a secondary
reference only when its trigger is present.

| Trigger | Reference |
|---|---|
| Plan or select a wave | `references/queue-and-dispatch.md` |
| Rough initiative or documentation approval | `references/documentary-planning.md` |
| Nested Compound Master runs | `references/compound-master-nesting.md` |
| Execution lane, assurance, or role admission | `references/execution-lanes.md` |
| Eligible low/medium worker | `references/lightweight-dispatch.md` |
| High/critical, deep, autonomous, or policy-required worker | `references/executable-worker-contracts.md` |
| Complex role prompts or named worker profiles | `references/subagent-contracts.md`, then `references/worker-profiles.md` if needed |
| Concurrent mutable workers | `references/worktree-collaboration.md` |
| Coupled work around a small shared foundation | `references/staged-decomposition.md` |
| Adaptive concurrency or reusable aggregate evidence | `references/automated-wave-control.md` |
| Reconciliation and release readiness | `references/gates-and-reconciliation.md` |
| High/critical coordinated review | `references/review-coordination.md` |
| Interrupted review or disputed verification | `references/role-recoverability.md` |
| Persistent queue or blockers | `references/queue-state-schema.md`, then `references/blocker-ledger.md` if needed |
| Jira source or seeding | `references/jira-team-flow.md`, then `references/jira-seeding.md` if needed |
| No-confirmation run | `references/autonomous-team-flow.md` |
| Design explanation only | `references/swarm-protocol.md` |

## Stop Conditions

Stop the affected path when authority is missing, a required documentation gate
is not approved, ownership overlaps unsafely, a high-risk decision is unresolved,
verification fails, or the selected Jira provider is ambiguous. In autonomous
flow, record the blocker and continue only independent ledger-covered work.

## Closeout

Return the operation, gate status when applicable, units and outcomes, root-owned
verification/review evidence, blockers, branch/worktree references, changed
state artifacts, and one exact next action. Omit machinery that the selected
assurance protocol did not use.
