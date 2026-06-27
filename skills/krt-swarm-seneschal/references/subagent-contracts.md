# Subagent Contracts

Use this reference when launching subagents or preparing prompts for separate Codex threads.

## Worker Envelope

Every worker prompt must contain:

```text
Role: <role>
Unit: <id and title>
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
Unit: <id>
Branch/worktree/thread: <ref if known>
Changed files:
- ...
Verification:
- <command>: <pass|fail|not-run> <short reason>
Scope notes:
- <inside scope|outside scope concern>
Blockers:
- <none or list>
Release readiness:
- ready | not ready | unknown
```

If a worker omits the return contract, inspect the diff before trusting its status.

## Parallel Safety

Launch in parallel only when:

- each worker has isolated filesystem state
- each worker has a distinct branch or cloud task
- dependency edges are absent or already merged
- changed surfaces are non-overlapping
- the factory can reconcile all outputs before release handoff

If any condition is missing, serialize.
