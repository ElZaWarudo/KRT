# Subagent Contracts

Use this reference when launching subagents or preparing prompts for separate Codex threads.

## Worker Envelope

Every worker prompt must contain:

```text
Role: <role>
Unit: <id and title>
Jira issue: <subtask or standalone issue key, when applicable>
Source artifact: <path or issue URL>
Intended base: <branch/ref>
Isolation target: <branch/worktree/cloud task>
Scope included:
- ...
Scope excluded:
- ...
Acceptance criteria:
- ...
Verification commands:
- ...
Required skills:
- ...
Forbidden actions:
- ...
Return contract:
- ...
```

Pass artifact paths and repo-relative paths. Avoid flooding workers with the entire queue.

## Standard Roles

Use these roles as the normal team model:

```text
Planner -> Implementer -> Reviewer -> Fixer when needed -> Integrator -> Documenter
```

Not every unit needs every role. The seneschal chooses the smallest role chain that preserves quality gates.

### Planner

Use before implementation when an epic, roadmap item, Jira parent issue, or broad backlog item must be decomposed.

```text
Decompose only the provided epic/backlog item into small executable queue units.
For each unit return scope, non-goals, acceptance criteria, dependencies, touched surfaces, risk flags, verification commands, and suggested Jira shape.
Do not implement code.
Do not mutate Jira, commit, push, open PRs, request reviewers, merge, or transition issues.
Return units small enough for one Implementer and one focused PR unless grouping is explicitly justified.
```

### Compound Master Worker

Use when the unit is already a `krt-compound-master` review unit or needs the existing KRT artifact/review pipeline.

```text
Use krt-compound-master for this single review unit only.

Mode: execute
Package: <work-package-path>
Review unit: <RU#>
Parallel context: this worker owns only this unit.
Shipping: implementation-only/no-shipping. Do not commit, push, open PRs, mutate Jira, request reviewers, or merge.
Return: changed files, commands run, blockers, review findings, branch/base facts, and release-readiness notes.
```

### Implementer

Use when the unit is already fully specified and does not need the full compound-master artifact pipeline.

```text
Implement only the described unit.
Follow AGENTS.md and local skill rules.
Do not change public contracts, auth/data behavior, dependencies, or release configuration outside scope without stopping.
Add or update tests when the unit changes behavior.
Return a concise implementation report with files touched, verification, risks, and blockers.
Do not commit, push, open PRs, mutate Jira, request reviewers, or merge.
```

### Reviewer

Use after a worker finishes or when a PR/diff needs independent review.

```text
Review the diff against the unit contract.
Prioritize functional bugs, scope creep, missing tests, regressions, security risk, and architecture violations.
Report findings as P0/P1/P2 with file/line evidence.
Do not rewrite the implementation unless explicitly asked to fix.
```

### Fixer

Use only for bounded review findings or CI failures.

```text
Fix only the listed findings.
Do not opportunistically refactor.
Run the narrow verification that proves the fix.
Return the finding-to-change mapping.
Do not commit, push, open PRs, mutate Jira, request reviewers, or merge.
```

### Integrator

Use after implementation/review, before release handoff, or whenever multiple workers may interact.

```text
Inspect dependency order, merge order, stack shape, branch/base facts, conflicting surfaces, generated artifacts, lockfiles, API contracts, migrations, and Jira grouping.
Recommend standalone, grouped, or stacked PR handoff.
Identify conflicts, stale bases, missing downstream refreshes, and units that must wait.
Do not implement broad changes. Do not commit, push, open PRs, mutate Jira, request reviewers, transition issues, or merge.
Return release sequencing, conflict findings, and handoff notes for krt-release-marshal.
```

### Documenter

Use when the unit is docs, API docs, changelog, or release notes.

```text
Update only the documentation surfaces named in the unit.
Keep repo terminology and KRT skill naming canonical.
Do not change implementation unless the unit explicitly includes it.
Return changed docs and any verification performed.
```

## Return Contract

Require every worker to return:

```text
Status: done | blocked | needs-review | failed
Role: <planner|implementer|reviewer|fixer|integrator|documenter|compound-master-worker>
Unit: <id>
Jira issue: <key or none>
Branch/worktree/thread: <ref if known>
Changed files:
- ...
Verification:
- <command>: <pass|fail|not-run> <short reason>
Scope notes:
- <inside scope|outside scope concern>
Blockers:
- type: <product|auth|data|legal|DIAN|accounting|payroll|infrastructure|security|dependency|unknown>
  description: <brief blocker>
  decision_required: <decision needed>
  impact_if_ignored: <risk>
  affected_units: []
  suggested_owner: <user|product|accountant|legal|security|tech lead>
  evidence: <path/output/link>
  next_action: <suggested next step>
Release readiness:
- ready | not ready | unknown
Next role:
- <implementer|reviewer|fixer|integrator|documenter|release-marshal|none>
```

If a worker omits the return contract, inspect the diff before trusting its status.

If a blocker affects only the worker's unit, the orchestrator records it and continues with independent units. If it affects security, DIAN, accounting, payroll, auth, data, public contracts, or shared foundations, the orchestrator stops dependent dispatch and records a high-risk blocker.

## Parallel Safety

Launch in parallel only when:

- each worker has isolated filesystem state
- each worker has a distinct branch or cloud task
- dependency edges are absent or already merged
- changed surfaces are non-overlapping
- the factory can reconcile all outputs before release handoff
- no open blocker affects a selected unit or its dependencies

If any condition is missing, serialize.
