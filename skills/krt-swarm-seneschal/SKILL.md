---
name: krt-swarm-seneschal
description: Meta-orchestrator for turning ready KRT work packages, backlog items, or issue queues into safe waves of isolated Codex subagents and PR handoffs. Use when the user asks for a swarm-style workflow, dispatcher, parallel subagent orchestration, backlog-to-PR execution, Codex worker waves, or a layer above krt-compound-master without modifying krt-compound-master.
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
- Treat human approval as required before launching mutating parallel work unless the user supplied an active autonomy ledger that allows the exact mutation class.
- Prefer small, independently reviewable units over broad backlog sweeps.
- Cap active mutable work to the smallest safe wave; default to 2 concurrent workers until repo evidence supports more.
- Never let production outrun verification: a wave is not complete until worker output, review, verification evidence, and state reconciliation are captured.

## Reference Router

Load only what the current task needs:

| Need | Load |
|---|---|
| Explain or design the swarm model | `references/swarm-protocol.md` |
| Build a queue, choose ready work, plan waves | `references/queue-and-dispatch.md` |
| Launch or prepare subagent prompts | `references/subagent-contracts.md` |
| Reconcile outputs, review gates, hand off release work | `references/gates-and-reconciliation.md` |

## Workflow

1. **Preflight**
   - Confirm the user's requested mode: design-only, wave-plan, dispatch, reconcile, or resume.
   - Inspect repo state and active orchestration artifacts before mutating anything.
   - Identify the source of work: `docs/work-packages/`, GitHub Issues, Linear, a backlog file, or user-provided tasks.
   - When Jira is involved, resolve Jira posture as Cloud by default and load `krt-jira-cloud-scribe` rules before reading or mutating Jira state. Do not use the Server/Data Center scribe unless explicitly requested.
   - Resolve isolation: worktrees, cloud environments, or manual branches. If isolation is unavailable, plan serial execution.

2. **Normalize Work**
   - Convert candidate work into executable units with scope, acceptance criteria, dependencies, touched surfaces, verification commands, and intended base.
   - Prefer existing `krt-compound-master` review units. If only high-level backlog items exist, route discovery/planning through the existing requirements, roadmap, and compound-master skills rather than inventing hidden scope.
   - Reject units that are too broad, lack acceptance criteria, share a risky surface with another active unit, or need unresolved product/auth/data decisions.

3. **Plan A Wave**
   - Load `references/queue-and-dispatch.md`.
   - Select only dependency-ready, non-overlapping units.
   - Keep the wave within the open-stack and reviewability limits already enforced by `krt-compound-master`.
   - Produce a short wave plan with unit IDs, worker prompts, isolation target, verification gates, risks, and stop conditions.

4. **Dispatch Workers**
   - Load `references/subagent-contracts.md`.
   - If the runtime exposes subagents, launch each worker with only its unit contract and relevant artifact paths.
   - If subagents are unavailable, write exact prompts the user can run in separate Codex threads/worktrees.
   - Each worker must operate in implementation-only/no-shipping mode unless the explicit task is artifact-only.

5. **Review And Reconcile**
   - Load `references/gates-and-reconciliation.md`.
   - Read each worker result, changed-file summary, verification output, blockers, and branch/base facts.
   - Run or require review and verification gates before marking a unit release-ready.
   - Update the queue and any active orchestration state in the same turn that status changes.

6. **Release Handoff**
   - Hand release-ready units to `krt-release-marshal`; do not duplicate its commit, PR, Jira, reviewer, or merge procedure.
   - Carry enough context for grouped PRs, stacked PRs, downstream-fix notes, and Jira Cloud subtask mapping.
   - State that Jira handoff context was prepared under `krt-jira-cloud-scribe` unless the user explicitly selected Jira Server/Data Center.
   - In manual or guarded flow, stop at release-plan approval. In autonomous flow, only pass ledger-scoped mutation candidates.

## Stop Conditions

Stop and ask for direction when:

- A unit needs product, auth, data, branch-base, Jira, or production-behavior decisions not present in artifacts.
- Two ready units touch the same risky surface and cannot be safely isolated.
- The wave would exceed the open stacked PR cap.
- Verification or review cannot run and the missing gate materially changes release risk.
- A worker changed scope beyond its contract.
- External mutation would be required without explicit user approval or a valid ledger.

## Closeout

End with:

- Current mode and wave status.
- Units dispatched, blocked, release-ready, or handed off.
- Branch/worktree/thread references when available.
- Verification and review evidence.
- Queue/state files updated.
- Exact next invocation.
