---
name: krt-swarm-seneschal
description: Meta-orchestrator turning rough initiatives, documented KRT work packages, backlog items, Jira Cloud queues, and roadmap backlogs into approved documentation packets, safe Jira seed plans, isolated Codex worker waves, reconciliation, and release handoffs. Use when the user asks for swarm-style workflow, documentary planning before execution, dispatcher, parallel subagent orchestration, Jira-backed team flow, overnight/no-confirmation autonomous delivery, backlog-to-PR execution, Codex worker waves, or a layer above krt-compound-master without modifying krt-compound-master.
---

# KRT Swarm Seneschal

Coordinate swarm-style delivery flow:

```text
rough brief -> documentation gate -> Jira/queue seed -> isolated workers -> reviewed outputs -> release handoff
```

This skill is a meta-orchestrator. It must not edit `krt-compound-master`, bypass its gates, or replace `krt-release-marshal`. It may invoke existing KRT/Compound skills as workers when the runtime supports subagents, or produce exact prompts and wave plans when it does not.

## Operating Posture

- Treat approved documentation as a formal dependency of Jira mutation, worker dispatch, code mutation, and release handoff.
- Treat `krt-compound-master` as the quality pipeline, not the thing being changed.
- Treat `krt-release-marshal` as the only owner of commits, PR creation, Jira mutation during release, reviewer requests, and merge-related flow.
- Treat `krt-jira-cloud-scribe` as the default Jira role for queue intake, Jira readiness checks, issue/subtask lookup, and Jira Cloud handoff context. Use `krt-jira-scribe` only when the user explicitly says the target is Jira Server/Data Center.
- Treat human approval as a startup policy problem, not a per-action interruption. In manual flow, ask before mutating. In autonomous flow, require an active autonomy mandate/ledger that allows the exact mutation class.
- Even in autonomous flow, do not bypass the documentary planning gate unless the user explicitly authorizes the exact downstream mutation or an existing gate state is already approved.
- Prefer small, independently reviewable units over broad backlog sweeps.
- Cap active mutable implementation work at the smallest safe wave; default to 2 concurrent Implementer workers until repo evidence supports more. Planner, Reviewer, Fixer, Integrator, and Documenter workers use separate role caps.
- Never let production outrun verification: a wave is not complete until worker output, review, verification evidence, and state reconciliation are captured.
- If the user explicitly asks for no human confirmation, convert the instruction into a ledger-bound autonomous run: execute allowed actions after required gates pass, record uncovered decisions as blockers, continue independent work, and leave a morning-ready status packet instead of stopping to ask.

## Reference Router

Load only what the current task needs:

| Need | Load |
|---|---|
| Explain design swarm model | `references/swarm-protocol.md` |
| Produce, review, revise, approve documentation packet | `references/documentary-planning.md` |
| Build queue, choose ready work, plan waves | `references/queue-and-dispatch.md` |
| Launch or prepare subagent prompts | `references/subagent-contracts.md` |
| Reconcile outputs, review gates, hand off release work | `references/gates-and-reconciliation.md` |
| Run Jira Cloud backlog source drain ready waves | `references/jira-team-flow.md` |
| Seed Jira Cloud from roadmap or work-package backlog | `references/jira-seeding.md` |
| Decide parallelism surface isolation | `references/parallel-dispatch-policy.md` |
| Maintain persistent documentation gate, queue, Jira issue mapping | `references/queue-state-schema.md` |
| Record, review, resolve non-fatal blockers | `references/blocker-ledger.md` |
| Run without interactive confirmations | `references/autonomous-team-flow.md` |

## Modes

Supported modes:

- `design-only`: explain or design the swarm delivery model without mutating code, Jira, PRs, or queue state.
- `document-plan`: create only the starting documentation packet and mark the documentation gate `in_review`.
- `document-review`: present the current documentation packet for human review without Jira, worker, or code mutation.
- `document-revise`: adjust documentation packet artifacts from user feedback and mark the documentation gate `changes_requested` or `in_review` as appropriate.
- `document-approve`: mark the documentation packet approved after explicit user approval.
- `wave-plan`: normalize approved backlog into queue units and propose the next safe wave.
- `dispatch`: launch or prepare implementation-only workers for an approved wave.
- `reconcile`: inspect worker outputs, real diffs, verification, blockers, and review gates.
- `resume`: reload persistent queue state, documentation gate, live repo state, and active worker facts before continuing.
- `jira-team-flow`: use Jira Cloud backlog source and drain ready waves after documentation approval.
- `jira-seed-and-drain`: seed Jira Cloud and drain ready work only when documentation is approved or the user explicitly authorizes this exact bypass.
- `overnight-team-flow` or `autonomous-team-flow`: run Jira team flow with an autonomy mandate, still respecting the documentary planning gate.
- `blocker-review`: read blocker ledger and list open blockers grouped by type, Jira key, wave, and suggested owner.
- `blocker-resolve`: apply user-supplied decisions to the blocker ledger and mark affected units as candidates for readiness checks.

## Workflow

1. **Preflight**
- Resolve the user's requested mode: design-only, document-plan, document-review, document-revise, document-approve, wave-plan, dispatch, reconcile, resume, jira-team-flow, jira-seed-and-drain, overnight-team-flow, autonomous-team-flow, blocker-review, or blocker-resolve.
- Inspect repo state and active orchestration artifacts before mutating anything.
- Identify source work: `docs/work-packages/`, GitHub Issues, Linear, backlog file, Jira Cloud queue, or user-provided tasks.
- Read persistent state from `docs/swarm/queue-state.yaml` and `docs/swarm/blockers.yaml` when they exist. Create them only when the requested mode needs local state.
- When Jira is involved, resolve Jira posture as Cloud by default and load `krt-jira-cloud-scribe` rules before reading or mutating Jira state. Do not use Server/Data Center scribe unless explicitly requested.
- For Jira team flow, load `references/jira-team-flow.md`, `references/queue-state-schema.md`, `references/blocker-ledger.md`, and `references/parallel-dispatch-policy.md`.
- For autonomous or no-confirmation flow, load `references/autonomous-team-flow.md` and resolve an autonomy ledger before external or irreversible mutations.
- Resolve isolation: worktrees, cloud environments, or manual branches. If isolation is unavailable, plan serial execution.

2. **Documentary Planning Gate**
- Load `references/documentary-planning.md`.
- If the user is starting a new initiative, roadmap, Jira program, swarm, overnight run, or implementation request from a rough brief, enter `document-plan` first.
- Produce the documentation packet before Jira mutation, queue execution state, worker dispatch, code mutation, or release handoff.
- Persist the gate in `docs/swarm/queue-state.yaml`:

```yaml
documentation_gate:
  status: draft | in_review | approved | changes_requested
  approved_by: null
  approved_at: null
  source_artifacts:
    - docs/product/roadmap.md
    - docs/jira/seed-plan.md
    - docs/swarm/swarm-startup.md
    - docs/swarm/queue-state.yaml
    - docs/swarm/blockers.yaml
```

- Mark documentation `in_review` when the packet is ready and stop with a review packet.
- In `document-review`, present the packet and review focus; do not mutate Jira, queue execution state, workers, or code.
- In `document-revise`, update only the documentation packet and gate status based on feedback.
- In `document-approve`, require explicit user approval, then set `status: approved`, `approved_by`, and `approved_at`.
- If `documentation_gate.status != approved`, do not seed Jira, dispatch workers, mutate code, or hand off release work unless the user explicitly authorizes that exact action in the current request.

3. **Normalize Work**
- Convert candidate work into executable units with scope, acceptance criteria, dependencies, touched surfaces, verification commands, and intended base.
- Use Planner workers when a roadmap, epic, or Jira parent issue must be decomposed into small executable units before implementation.
- Prefer existing `krt-compound-master` review units. If only high-level backlog items exist, route discovery/planning through existing requirements, roadmap, and compound-master skills rather than inventing hidden scope.
- Reject units that are too broad, lack acceptance criteria, share a risky surface with another active unit, or need unresolved product/auth/data decisions.
- For Jira Cloud queues, maintain persistent mapping from Jira issue key to work package, review unit, queue unit, current status, dependencies, and handoff facts.

4. **Seed Jira When Requested**
- Confirm `documentation_gate.status == approved` before any Jira seed or drain. If not approved, stop with the documentation review packet unless the user explicitly authorized Jira seeding in the current request.
- Load `references/jira-seeding.md`.
- Convert roadmap into proposed Jira hierarchy: product epic, parent issues by wave/domain, subtasks per work package or executable unit.
- Mark units that depend on expert decisions as blocked/deferred in local queue state and include intended Jira status/labels in the seed plan.
- In manual flow, do not create, update, comment on, link, or transition Jira issues unless the user confirms the exact mutation plan.
- In autonomous flow, execute only mutation classes covered by the autonomy ledger through `krt-jira-cloud-scribe`; record uncovered mutation needs as blockers and keep draining independent approved work.

5. **Plan A Wave**
- Confirm `documentation_gate.status == approved` before selecting executable work.
- Load `references/queue-and-dispatch.md`.
- For Jira team flow, read active Jira Cloud issues through `krt-jira-cloud-scribe`, convert them into queue units, and reconcile them with the local Jira issue map.
- Read `docs/swarm/blockers.yaml` before selection. Do not select units with open blockers or units depending on open blockers.
- Select only dependency-ready, non-overlapping units.
- Apply concurrency algorithm in `references/parallel-dispatch-policy.md`: default to 2 mutable Implementer workers, role-specific caps for non-implementation workers, increase implementation concurrency only after green wave history, and never parallelize overlapping auth, migrations, public contracts, central models, or lockfiles.
- Keep the wave within open-stack reviewability limits already enforced by `krt-compound-master`.
- Produce a short wave plan with unit IDs, worker prompts, isolation target, verification gates, risks, and stop conditions.

6. **Dispatch Workers**
- Confirm `documentation_gate.status == approved` before dispatch.
- Load `references/subagent-contracts.md`.
- If runtime exposes subagents, launch each worker only with the relevant unit contract and artifact paths.
- If subagents are unavailable, write exact prompts the user can run in separate Codex threads/worktrees.
- Use role-specific workers: Planner, Implementer, Reviewer, Fixer, Integrator, Documenter. Use Compound Master Worker when a unit should go through the existing KRT quality pipeline.
- Each worker must operate in implementation-only/no-shipping mode unless the task is explicitly artifact-only.
- Assign exactly one Jira subtask or standalone Jira issue per worker when Jira is the backlog source.
- Forbid workers from committing, pushing, opening PRs, mutating Jira, requesting reviewers, merging, or transitioning issues.
- Require structured blocker reporting in the worker return contract.

7. **Review Reconcile**
- Load `references/gates-and-reconciliation.md`.
- Read each worker result, changed-file summary, verification output, blockers, and branch/base facts.
- Inspect real diff filesystem state before trusting worker reports.
- Run required review and verification gates before marking any unit release-ready.
- Reconcile blockers using `references/blocker-ledger.md`: record non-fatal blockers, mark only affected units blocked/deferred, and continue independent ready units.
- Use Integrator workers to inspect merge order, dependency edges, stacked PR choreography, and cross-worker conflicts before release handoff.
- Decide each unit status: `release-ready`, `needs-fix`, `blocked`, `deferred`, or `split-required`.
- Update queue and active orchestration state in the same turn as status changes.

8. **Release Handoff**
- Confirm `documentation_gate.status == approved` before release handoff.
- Hand release-ready units to `krt-release-marshal`; do not duplicate its commit, PR, Jira, reviewer, or merge procedure.
- Carry Jira key, work package review unit, suggested PR grouping, verification evidence, release notes, downstream-fix notes, and suggested Jira transition.
- Suggested Jira transitions are handoff context only. Seneschal does not execute them directly.
- State that Jira handoff context was prepared under `krt-jira-cloud-scribe` unless the user explicitly selected Jira Server/Data Center.
- In manual or guarded flow, stop at release-plan approval.
- In autonomous flow, pass the autonomy ledger path and only ledger-scoped mutation candidates to `krt-release-marshal`; do not ask the user during the run.

## Stop Conditions

Stop or ask direction when:

- Documentation gate is not approved and the requested action would seed Jira, dispatch workers, mutate code, or hand off release work.
- Manual flow requires direction for mutations, risky ambiguity, failed gates, unsafe overlap, scope creep, or no ready work.
- Autonomous flow must not interrupt for questions. Instead, record decision needs in `docs/swarm/blockers.yaml`, mark affected units blocked/deferred, skip uncovered mutation classes, and continue independent approved work.
- Autonomous flow stops only on runtime impossibility: no runnable independent work remains, credentials/tools are absent for every remaining path, isolation cannot be achieved for any unit, or continuing would violate an explicit deny rule in the autonomy ledger.

## Closeout

End with:

- Current mode and documentation gate status.
- Units dispatched, blocked, release-ready, or handed off.
- Non-fatal blockers recorded, high-risk blockers, and whether independent work remains.
- Branch/worktree/thread references when available.
- Verification and review evidence.
- Queue/state files updated.
- Exact next invocation.
