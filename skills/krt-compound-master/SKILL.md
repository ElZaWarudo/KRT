---
name: krt-compound-master
description: >
  Discovery-gated artifact-first orchestrator for compound-engineering product delivery. Resolves roadmap/readiness generation,
  runs brainstorm/plan/document-review loops, derives mergeable work packages with focused review units, executes each review unit
  through resolved work/code-review roles, and hands shipping to krt-release-marshal with CI break-prevention evidence. Use when
  turning an existing documented software project into a sequenced roadmap and PR/Jira delivery program. Runtime aliases may expose
  this as krt:compound-master.
---

# Compound Master

Orchestrate KRT delivery. Do not replace Compound Engineering, duplicate component skills, ship from work phases, open/merge PRs directly, or mutate Jira directly. Hand shipping context to `krt-release-marshal`.

Arguments:

```text
[initiative/docs] [mode:artifacts|execute|full|resume] [package:<path>] [review-unit:<RU#>]
[pr-granularity:auto|review-unit|work-package|roadmap-item|plan-unit]
[jira-policy:required|optional|skip] [production:unknown|live|preprod|prototype]
[parallel:true|false] [delegation:auto|ask|inline] [worktree-policy:avoid|auto|required]
[autonomy:manual|guarded|high] [autonomous-ledger:<path>] [review-threshold:P0-P2|P0-P1|P0]
[subagent-model:<runtime-specific-model>]
```

Default: artifact-first after discovery. Execute only when requested or when `mode:full` reaches its execution gate. Jira is preferred and non-blocking unless `jira-policy:required`.

## Progressive Loading

Load only the current phase. Phase-specific rules live in the owning reference.

| Phase | Load |
|---|---|
| Preflight, roles, arguments, paths | `references/role-and-runtime.md`, `references/fast-contract.md` |
| Artifact workflow and gates | `references/workflow-map.md` |
| Work-package templates/review units | `references/artifact-templates.md` |
| Execution routing | `references/execution-flow.md` |
| Delegation prompts | `references/execution-delegation.md` |
| Impact/verification | `references/impact-verification.md` |
| Review, security, CI | `references/review-security-ci.md` |
| Release handoff | `references/release-handoff.md` |
| State/closeout/failures | `references/status-and-failures.md` |
| Autonomous mutation | `references/autonomous-mode.md`, `references/autonomy-ledger-schema.md`, `references/autonomous-flow-matrix.md` |

Before writing or reviewing a work package:

```bash
python3 <compound-master-skill-dir>/scripts/check_work_package.py <work-package.md>
```

Resolve `<compound-master-skill-dir>` to the directory containing this `SKILL.md`; installed runtimes may use `/home/teb/.agents/skills/krt-compound-master`. Before delegating to weaker/narrower agents, pass the relevant package plus `references/fast-contract.md`.

## Core Pipeline

1. Preflight roles, repo, branch, Jira, production, delegation, and context.
2. Generate exactly one roadmap/readiness report; stop if context is insufficient.
3. Review roadmap, run one brainstorm per roadmap item, review it, plan it, and review the plan.
4. Derive and review work packages, then pass the Reviewability Gate: choose review-unit/PR boundaries for human reviewability and independent mergeability, not atomicity or Jira-fit, and cap open stacked PRs at 2-3.
5. Execute each ready review unit with the resolved work role in implementation-only/no-shipping mode.
6. Run Impact Scan, verification, code review, Security Watch/Sentinel as required, and CI break-prevention evidence.
7. Hand finished review units to `krt-release-marshal`; it owns commits, rebase, Jira, PRs, reviewers, transitions, and ledger-bound autonomous merge execution.

## Universal Rules

- Resolve roles by canonical skill/command/agent. Never guess short names.
- Use document-review roles for documents and code-review roles for diffs.
- No implementation before a written and reviewed plan; no roadmap continuation when context is insufficient; no skipped brainstorm unless explicit and recorded.
- Do not invent product behavior, auth/data contracts, Jira transitions, release constraints, branch bases, dependency edges, or production posture. Use `production:unknown` unless evidence says otherwise; `production:live` is compatibility-preserving.
- Escalate product behavior, auth/data contracts, destructive operations, public contract removal, branch/base strategy, required Jira/PR workflow decisions, and production compatibility breakage.
- Keep state and active artifacts current in the same phase transition that changes their truth; reconcile state before delegation, resume, review handoff, release handoff, or stop.
- Optimize review-unit/PR boundaries for human reviewability and independent mergeability, not atomicity or Jira-fit. Keep at most 2-3 open unmerged PRs in one stacked chain; at the cap, wait for the parent to merge into the integration base or collapse the pending chain onto it, and never resolve an over-deep stack by abandoning it for one mega-consolidation PR. When a later review unit fixes a surface an earlier still-open PR's reviewer flagged, record and surface a downstream-fix note so the prior review is not lost. Jira stays at review-unit granularity: a grouped PR covering several review units backlinks one subtask per review unit under a shared parent, never a single collapsed task.
- Do not produce artifacts or PRs faster than their verifying gate can close them. Every brainstorm, plan, work package, and PR must pass its review/verification gate before the next one is built on top of it; this generalizes the open-stack cap to all phases, not just stacked PRs.
- Do not let work roles ship. Internal review, Security Sentinel, CI evidence, and release-plan acceptance are readiness signals only, not merge authorization.
- `autonomy:high` without an active ledger is local autonomy only; it never authorizes PR, branch, reviewer, Jira, or merge side effects.
- Trust bundled checkers over assumptions. If a checker reports a result, act on it and diagnose the real failure; never ask for Jira credentials.
- With default optional Jira, attempt Jira when context/config exists; otherwise record the omitted handoff. Ask only for required Jira, ambiguous Jira mutation, or release-plan approval naming the action/fallback.

## Stop Discipline

Close out with current phase/status, written paths, ready work, blockers or "No blockers", recommended next action, and exact next invocation. For stacked/sibling PR handoff, include per-PR scope/base context so Release Marshal can emit stable `PR1`/`PR2` blocks. If artifact generation stopped before implementation, do not imply a planning/docs branch should ship independently. Do not stop between a passing work/review loop and `krt-release-marshal`; that approval pause belongs inside Release Marshal.

## Workflow Map

Artifact generation: load `references/workflow-map.md`.
Execution: load `references/execution-flow.md`, then only the phase file it points to.
State/failures: load `references/status-and-failures.md`.
