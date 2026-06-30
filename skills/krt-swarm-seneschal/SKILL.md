---
name: krt-swarm-seneschal
description: Meta-orchestrator for turning ready KRT work packages, backlog items, Jira Cloud queues, or whole roadmap backlogs into safe waves of isolated Codex subagents and release handoffs. Use when the user asks for a swarm-style workflow, dispatcher, parallel subagent orchestration, Jira-backed team flow, overnight/no-confirmation autonomous delivery, backlog-to-PR execution, Codex worker waves, or a layer above krt-compound-master without modifying krt-compound-master.
---

# KRT Swarm Seneschal

Coordinate a swarm-style delivery flow:

```text
backlog/work-packages -> small executable units -> isolated subagents -> reviewed outputs -> release handoff
```

This skill is a meta-orchestrator. It must not edit `krt-compound-master`, bypass its gates, or replace `krt-release-marshal`. It may invoke existing KRT/Compound skills as workers when the current runtime supports subagents, or produce exact prompts and wave plans when it does not.

## Operating Posture

- Treat `krt-compound-master` as the quality pipeline, not the thing being changed.
- Treat `krt-release-marshal` as the only owner of commits, PR creation, Jira mutation, reviewer requests, and merge-related flow.
- Treat `krt-jira-cloud-scribe` as the default Jira role for queue intake, Jira readiness checks, issue/subtask lookup, and Jira Cloud handoff context. Use `krt-jira-scribe` only when the user explicitly says the target is Jira Server/Data Center.
- Treat human approval as a startup policy problem, not a per-action interruption. In manual flow, ask before mutating. In autonomous flow, require an active autonomy mandate/ledger that allows the exact mutation class, then proceed without asking again.
- Prefer small, independently reviewable units over broad backlog sweeps.
- Cap active mutable implementation work to the smallest safe wave; default to 2 concurrent Implementer workers until repo evidence supports more. Planner, Reviewer, Fixer, Integrator, and Documenter workers use separate role caps.
- Never let production outrun verification: a wave is not complete until worker output, review, verification evidence, and state reconciliation are captured.
- If the user explicitly asks for no human confirmation, convert that instruction into a ledger-bound autonomous run: execute allowed actions, record uncovered decisions as blockers, continue independent work, and leave a morning-ready status packet instead of stopping to ask.

## Reference Router

Load only what the current task needs:

| Need | Load |
|---|---|
| Explain or design the swarm model | `references/swarm-protocol.md` |
| Build a queue, choose ready work, plan waves | `references/queue-and-dispatch.md` |
| Launch or prepare subagent prompts | `references/subagent-contracts.md` |
| Reconcile outputs, review gates, hand off release work | `references/gates-and-reconciliation.md` |
| Run Jira Cloud as the backlog source and drain ready waves | `references/jira-team-flow.md` |
| Seed Jira Cloud from a roadmap or work-package backlog | `references/jira-seeding.md` |
| Decide parallelism and surface isolation | `references/parallel-dispatch-policy.md` |
| Maintain persistent queue and Jira issue mapping | `references/queue-state-schema.md` |
| Record, review, or resolve non-fatal blockers | `references/blocker-ledger.md` |
| Run without interactive confirmations | `references/autonomous-team-flow.md` |

## Modes

Supported modes:

- `design-only`: explain or design a swarm delivery model without mutating code, Jira, PRs, or queue state.
- `wave-plan`: normalize backlog into queue units and propose the next safe wave.
- `dispatch`: launch or prepare implementation-only workers for an approved wave.
- `reconcile`: inspect worker outputs, real diffs, verification, blockers, and review gates.
- `resume`: reload persistent queue state, live repo state, and active worker facts before continuing.
- `jira-team-flow` or `jira-seed-and-drain`: use Jira Cloud as the backlog source, optionally seed it from a roadmap, then drain ready waves through safe dispatch and reconciliation.
- `overnight-team-flow` or `autonomous-team-flow`: run Jira team flow with a startup autonomy mandate and no runtime confirmation prompts.
- `blocker-review`: read the blocker ledger and list open blockers grouped by type, Jira key, wave, and suggested owner.
- `blocker-resolve`: apply a user-supplied decision to the blocker ledger and mark affected units as candidates for readiness check.

## Workflow

1. **Preflight**
   - Resolve the user's requested mode: design-only, wave-plan, dispatch, reconcile, resume, jira-team-flow, jira-seed-and-drain, overnight-team-flow, autonomous-team-flow, blocker-review, or blocker-resolve.
   - Inspect repo state and active orchestration artifacts before mutating anything.
   - Identify the source of work: `docs/work-packages/`, GitHub Issues, Linear, a backlog file, or user-provided tasks.
   - When Jira is involved, resolve Jira posture as Cloud by default and load `krt-jira-cloud-scribe` rules before reading or mutating Jira state. Do not use the Server/Data Center scribe unless explicitly requested.
   - For Jira team flow, load `references/jira-team-flow.md`, `references/queue-state-schema.md`, `references/blocker-ledger.md`, and `references/parallel-dispatch-policy.md`.
   - For autonomous or no-confirmation flow, load `references/autonomous-team-flow.md` and resolve an autonomy ledger before external or irreversible mutations.
   - Read persistent state from `docs/swarm/queue-state.yaml` and `docs/swarm/blockers.yaml` when they exist. Create them only after the requested mode needs local state.
   - Resolve isolation: worktrees, cloud environments, or manual branches. If isolation is unavailable, plan serial execution.

2. **Normalize Work**
   - Convert candidate work into executable units with scope, acceptance criteria, dependencies, touched surfaces, verification commands, and intended base.
   - Use Planner workers when a roadmap, epic, or Jira parent issue must be decomposed into small executable units before implementation.
   - Prefer existing `krt-compound-master` review units. If only high-level backlog items exist, route discovery/planning through the existing requirements, roadmap, and compound-master skills rather than inventing hidden scope.
   - Reject units that are too broad, lack acceptance criteria, share a risky surface with another active unit, or need unresolved product/auth/data decisions.
   - For Jira Cloud queues, maintain a persistent mapping from Jira issue key to work package, review unit, queue unit, current status, dependencies, and handoff facts.

3. **Seed Jira When Requested**
   - Load `references/jira-seeding.md`.
   - Convert the roadmap into a proposed Jira hierarchy: product epic, parent issues by wave/domain, and subtasks per work package or executable unit.
   - Mark units that depend on expert decisions as blocked/deferred in local queue state and include the intended Jira status or label in the seed plan.
   - In manual flow, do not create, update, comment on, link, or transition Jira issues unless the user confirms the exact mutation plan.
   - In autonomous flow, execute only mutation classes covered by the autonomy ledger through `krt-jira-cloud-scribe`; record uncovered mutation needs as blockers and keep draining independent work.

4. **Plan A Wave**
   - Load `references/queue-and-dispatch.md`.
   - For Jira team flow, read active Jira Cloud issues through `krt-jira-cloud-scribe`, convert them to queue units, and reconcile them with the local Jira issue map.
   - Read `docs/swarm/blockers.yaml` before selection. Do not select units with open blockers or units depending on open blockers.
   - Select only dependency-ready, non-overlapping units.
   - Apply the concurrency algorithm in `references/parallel-dispatch-policy.md`: default 2 mutable Implementer workers, role-specific caps for non-implementation workers, increase implementation concurrency only after green wave history, and never parallelize overlapping auth, migrations, public contracts, central models, or lockfiles.
   - Keep the wave within the open-stack and reviewability limits already enforced by `krt-compound-master`.
   - Produce a short wave plan with unit IDs, worker prompts, isolation target, verification gates, risks, and stop conditions.

5. **Dispatch Workers**
   - Load `references/subagent-contracts.md`.
   - If the runtime exposes subagents, launch each worker with only its unit contract and relevant artifact paths.
   - If subagents are unavailable, write exact prompts the user can run in separate Codex threads/worktrees.
   - Use role-specific workers: Planner, Implementer, Reviewer, Fixer, Integrator, and Documenter. Use Compound Master Worker when the unit should go through the existing KRT quality pipeline.
   - Each worker must operate in implementation-only/no-shipping mode unless the explicit task is artifact-only.
   - Assign exactly one Jira subtask or standalone Jira issue to each worker when Jira is the backlog source.
   - Forbid workers from committing, pushing, opening PRs, mutating Jira, requesting reviewers, merging, or transitioning issues.
   - Require structured blocker reporting in the worker return contract.

6. **Review And Reconcile**
   - Load `references/gates-and-reconciliation.md`.
   - Read each worker result, changed-file summary, verification output, blockers, and branch/base facts.
   - Inspect the real diff and filesystem state before trusting a worker report.
   - Run or require review and verification gates before marking a unit release-ready.
   - Reconcile blockers using `references/blocker-ledger.md`: record non-fatal blockers, mark only affected units blocked/deferred, and continue with independent ready units.
   - Use Integrator workers to inspect merge order, dependency edges, stacked PR choreography, and cross-worker conflicts before release handoff.
   - Decide each unit status as `release-ready`, `needs-fix`, `blocked`, `deferred`, or `split-required`.
   - Update the queue and any active orchestration state in the same turn that status changes.

7. **Release Handoff**
   - Hand release-ready units to `krt-release-marshal`; do not duplicate its commit, PR, Jira, reviewer, or merge procedure.
   - Carry Jira key, work package or review unit, suggested PR grouping, verification evidence, release notes, downstream-fix notes, and suggested Jira transition.
   - Suggested Jira transitions are handoff context only. The seneschal does not execute them directly.
   - State that Jira handoff context was prepared under `krt-jira-cloud-scribe` unless the user explicitly selected Jira Server/Data Center.
   - In manual or guarded flow, stop at release-plan approval.
   - In autonomous flow, pass the autonomy ledger path and only ledger-scoped mutation candidates to `krt-release-marshal`; do not ask the user during the run.

## Stop Conditions

Stop and ask for direction when:

- Manual flow requires direction for mutations, risky ambiguity, failed gates, unsafe overlap, scope creep, and no ready work.
- Autonomous flow must not interrupt for questions. Instead, record the decision need in `docs/swarm/blockers.yaml`, mark affected units blocked/deferred, skip uncovered mutation classes, and continue with independent ready work.
- Autonomous flow stops only for runtime impossibility: no runnable independent work remains, credentials/tools are absent for every remaining path, isolation cannot be achieved for any unit, or continuing would violate an explicit deny rule in the autonomy ledger.

Do not stop the whole goal for questions that can be recorded as non-fatal blockers. Record the blocker, mark affected units blocked/deferred, and continue with independent ready work.

## Closeout

End with:

- Current mode and wave status.
- Units dispatched, blocked, release-ready, or handed off.
- Non-fatal blockers recorded, high-risk blockers, and whether independent work remains.
- Branch/worktree/thread references when available.
- Verification and review evidence.
- Queue/state files updated.
- Exact next invocation.
