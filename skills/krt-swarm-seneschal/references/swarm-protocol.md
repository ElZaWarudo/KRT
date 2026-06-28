# Swarm Protocol

Use this reference when explaining, designing, or governing KRT Swarm Seneschal.

## Core Thesis

The healthy shape is not one giant Codex session with an entire backlog. The healthy shape is a controlled swarm:

```text
stable context -> executable queue -> isolated workers -> review gates -> release marshal handoff
```

The swarm seneschal optimizes for reviewable, mergeable output. It does not optimize for raw task count.

## Layers

1. **Stable context**
   - `AGENTS.md`
   - KRT skill rules
   - existing planning, roadmap, and work-package artifacts
   - repo-specific verification commands

2. **Executable queue**
   - `docs/work-packages/**`
   - GitHub Issues, Linear issues, or `backlog.yaml`
   - each unit must have scope, non-goals, acceptance criteria, dependencies, and verification commands

3. **Dispatcher**
   - selects ready units
   - enforces dependency and overlap rules
   - caps concurrency
   - creates worker prompts or launches subagents

4. **Workers**
   - one Codex worker per unit
   - isolated branch/worktree/cloud task
   - no shipping authority
   - no scope expansion without escalation

5. **Quality control**
   - local verification
   - code review
   - security review when required
   - CI break-prevention evidence
   - release handoff
   - Jira Cloud reconciliation through `krt-jira-cloud-scribe` when Jira is part of the queue or release trace

## Non-Negotiables

- One worker owns one executable unit.
- One unit should map to one reviewable PR unless grouping is more reviewable and explicitly recorded.
- No worker edits the same risky surface as another active worker without a dependency edge or a coordination note.
- No worker performs release actions.
- No dispatcher creates a deeper stack than humans can review.
- No backlog item enters the queue until it is written as a contract of work.
- No Jira operation uses `krt-jira-scribe` unless the user explicitly identifies the target as Jira Server/Data Center. For Jira Cloud, use `krt-jira-cloud-scribe`.

## Relationship To Existing KRT Skills

- `krt-compound-master` remains the artifact and quality pipeline.
- `krt-release-marshal` remains the release mutation owner.
- `krt-jira-cloud-scribe` is the default Jira integration role for Cloud issue lookup, readiness, subtask mapping, and handoff context.
- `krt-review-herald`, `krt-security-sentinel`, and `krt-ci-questor` remain specialists used when their gates are triggered.
- This skill coordinates when and how those roles are invoked across multiple units.

## Factory Maturity

Start conservative:

```text
M0: design-only wave plan
M1: serial execution with queue state
M2: two isolated workers in parallel
M3: bounded worker pool with reconciliation
M4: ledger-bound autonomous mutation handoff
```

Do not skip straight to high concurrency. Increase concurrency only after repeated waves finish with low conflict, clear review results, and no stale state.
