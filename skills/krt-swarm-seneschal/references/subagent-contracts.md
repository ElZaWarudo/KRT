# Subagent Contracts

Use this reference when launching subagents or preparing prompts for separate Codex threads.

## Worker Envelope

Every worker prompt must contain:

```text
Role: <role>
Worker profile: <registered profile ID or runtime-default>
Model class: <declared class or runtime-default>
Unit execution lane: <fast|standard|deep|not-applicable>
Reasoning effort: <high|xhigh>
Lane trigger: <deterministic admission reason>
Profile source: <project-agent|user-agent|runtime-default>
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
- <focused leaf checks only>
Wave verification owner: Seneschal/root
Required skills:
- ...
Forbidden actions:
- ...
Return contract:
- ...
```

Pass artifact paths and repo-relative paths. Avoid flooding workers with the entire queue.

When `Worker profile` names a registered Codex profile, load
`worker-profiles.md` and pass its static preflight before launching the worker.
The worker envelope remains mandatory: a profile supplies stable runtime
behavior, not the unit-specific contract.

Load `execution-lanes.md` before composing the envelope. Its implementation
mapping is fixed: `fast` -> `spark`/`xhigh`, `standard` -> `luna`/`high`, and
`deep` -> `luna_xhigh`/`xhigh`. Spark remains `xhigh` and receives only
decision-closed contracts. Supporting roles use Luna `high` normally and Luna
`xhigh` only when their own bounded task has a deep trigger.

## Standard Roles

Use the Implementer as the default role and add only triggered support:

```text
Planner when needed -> Implementer -> Reviewer/Fixer when triggered -> Integrator/Documenter when triggered
```

Not every unit needs every role. The seneschal chooses the smallest role chain that preserves quality gates.
Start with the Implementer and add no optional role without its admission
trigger from `execution-lanes.md`. Record the trigger in the wave plan and
worker envelope.

### Planner

Use only when broad or ambiguous work still needs decomposition, acceptance
criteria, dependency mapping, or decision closure. Do not use it for an
execution-ready package.

```text
Decompose only the provided epic/backlog item into small executable queue units.
For each unit return scope, non-goals, acceptance criteria, dependencies, touched surfaces, risk flags, verification commands, and suggested Jira shape.
Do not implement code.
Do not mutate Jira, commit, push, open PRs, request reviewers, merge, or transition issues.
Return units small enough for one Implementer and one focused PR unless grouping is explicitly justified.
```

### Compound Master Worker

Use `compound-master-nesting.md`. A Compound worker may own one roadmap item
through the full artifact and quality pipeline, or one existing work
package/review unit during execution. Always limit it to one assigned target.

Use only for a `deep` unit whose required Compound artifact or quality pipeline
is incomplete. An execution-ready package/review unit is not sufficient reason
to nest Compound Master; route it directly to the selected Luna profile.

```text
Use krt-compound-master for only the assigned target.

Mode: <artifacts|full|execute|resume>
Parallel: false
Orchestrator: seneschal
Run ID: <stable-id>
State path: docs/orchestration/compound-master/<run-id>/state.md
Interaction: brokered
Initiative contract: <requirements-only artifact path>
Target roadmap item: <RDM# or none>
Package: <work-package-path or none>
Review unit: <RU# or none>
Artifact namespace: <initiative/item namespace>
Shared decisions: <paths>
Parallel context: this worker owns only this unit.
Shipping: artifact-only or implementation-only/no-shipping as assigned.
Do not rerun the general initiative brainstorm.
Run focused item discovery only when no reviewed item planning input exists.
Do not ask the user directly. Return structured decision requests and pause
only affected work.
Do not commit, push, open PRs, mutate Jira, request reviewers, or merge.
Return: run ID, canonical state, artifact paths, observed revision, changed
files, commands run, inner gates, decision requests, affected sibling units,
branch/base facts, release readiness, and recommended resume invocation.
```

### Implementer

Use when the unit is execution-ready. Select Spark only for `fast`, Luna `high`
for `standard`, and Luna `xhigh` for `deep`.

```text
Implement only the described unit.
Follow AGENTS.md and local skill rules.
Do not change public contracts, auth/data behavior, dependencies, or release configuration outside scope without stopping.
Add or update tests when the unit changes behavior.
Return a concise implementation report with files touched, verification, risks, and blockers.
Do not commit, push, open PRs, mutate Jira, request reviewers, or merge.
```

### Reviewer

Use only when behavior/control flow changed, risk is elevated, a sensitive or
public contract surface changed, acceptance requires independent review, or the
diff exceeds the narrow mechanical lane. Do not add a Reviewer to pure
formatting, generated refreshes, or decision-closed docs-only edits by default.

```text
Review the diff against the unit contract.
Prioritize functional bugs, scope creep, missing tests, regressions, security risk, and architecture violations.
Report findings as P0/P1/P2 with file/line evidence.
Do not rewrite the implementation unless explicitly asked to fix.
```

### Fixer

Use only for concrete bounded review findings or verification failures.

```text
Fix only the listed findings.
Do not opportunistically refactor.
Run the narrow verification that proves the fix.
Return the finding-to-change mapping.
Do not commit, push, open PRs, mutate Jira, request reviewers, or merge.
```

### Integrator

Use only when at least two units have dependencies, shared surfaces, generated
outputs, stack/merge choreography, or a cross-unit compatibility question.

```text
Inspect dependency order, merge order, stack shape, branch/base facts, conflicting surfaces, generated artifacts, lockfiles, API contracts, migrations, and Jira grouping.
Recommend standalone, grouped, or stacked PR handoff.
Identify conflicts, stale bases, missing downstream refreshes, and units that must wait.
Do not implement broad changes. Do not commit, push, open PRs, mutate Jira, request reviewers, transition issues, or merge.
Return release sequencing, conflict findings, and handoff notes for krt-release-marshal.
```

### Documenter

Use when documentation is explicitly in scope or changed behavior makes a
maintained user, developer, API, changelog, or release document inaccurate.

```text
Update only the documentation surfaces named in the unit.
Keep repo terminology and KRT skill naming canonical.
Do not change implementation unless the unit explicitly includes it.
Return changed docs and any verification performed.
```

## Return Contract

Require every worker to return:

```text
Status: done | blocked | needs-decision | needs-review | failed
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
Decision requests:
- question: <single decision>
  why_not_inferable: <missing authority or evidence>
  affected_units: []
  options: []
  recommendation: <option or none>
  safe_fallback: <pause/defer behavior>
  canonical_target: <shared or item artifact path>
  evidence: <paths/output/links>
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
