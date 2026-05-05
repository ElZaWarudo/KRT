---
name: krt:compound-master
description: >
  Artifact-first orchestrator for compound-engineering product delivery. Validates project context,
  creates a dependency-aware roadmap, runs brainstorm/plan/document-review loops, derives
  mergeable work packages, and later executes each package through resolved work/code-review roles before
  handing shipping to krt:release-marshal. Use when turning an existing documented software project
  into a sequenced roadmap and PR/Jira delivery program.
argument-hint: >
  [initiative description or docs path]
  [mode:artifacts|mode:execute|mode:full|mode:resume]
  [pr-granularity:auto|roadmap-item|plan-unit]
  [jira-policy:required|optional|skip]
  [parallel:true|false]
  [review-threshold:P0-P2|P0-P1|P0]
  [subagent-model:<runtime-specific-model>]
---

# Compound Master

Compound Master coordinates existing skills. It does **not** replace Compound Engineering and it does **not** duplicate `krt:release-marshal`.

Default posture: **artifact-first**. Generate durable artifacts first, then execute later only when the user explicitly asks.

Core pipeline:

1. Preflight skills, repo, branch, and context readiness.
2. Block if project documentation is insufficient.
3. Generate a medium/high-level roadmap with dependencies, parallelization waves, and preliminary PR strategy.
4. Run one interactive brainstorm skill per roadmap item.
5. Run one planning skill per reviewed brainstorm document.
6. Run document-review loops for roadmap, brainstorms, plans, and work packages.
7. Derive work packages that map to independently reviewable PR/Jira units.
8. Later, execute each package with a work skill or worker that supports implementation-only/no-shipping mode.
9. Review implementation with a code-review skill, looping fixes through the work skill until the configured threshold passes.
10. Hand the finished package to `krt:release-marshal`, which owns gitflow commits, clean rebase, Jira, GitHub PR, reviewer requests, and Jira review transition offer.

## Non-negotiable rules

- Resolve every referenced role from the host platform's available skills, commands, or agents. Never guess short names.
- Treat canonical hyphenated skill names as the portable default. Runtime forms such as `/ce-plan`, `/ce-code-review`, `ce:plan`, or `compound-engineering:ce-plan` are aliases only when the host exposes them.
- Treat `Skill("<role>", "...")` examples in this document as orchestration pseudocode. Translate them to the current runtime's actual skill, command, or agent invocation API.
- Use the resolved document-review role for documents and the resolved code-review role for implementation/diffs. Do not assume `ce:review`, `/ce-code-review`, or `ce-review` exists in every runtime.
- Do not implement before a written and reviewed plan exists.
- Do not generate a roadmap when context is insufficient. Context insufficiency is blocking.
- Do not invent product behavior, authorization rules, data contracts, Jira transitions, release constraints, or branch bases. Ask one blocking question at a time.
- Use repo-relative paths in all generated documents.
- Do not edit CE plan bodies as per-unit progress checklists. Progress lives in `compound-master-state.md`, work-package status, task tracking, commits, Jira, and PRs.
- A PR unit is a **work package**, not every bullet in a plan. Avoid PR-per-microtask.
- Do not let the work phase invoke its own PR/shipping flow in this orchestration. Shipping is delegated to `krt:release-marshal`.
- Do not open PRs from protected branches: `main`, `master`, or `develop`.
- Do not transition Jira automatically. `krt:jira-scribe` must fetch real transitions and require confirmation before `En Revisión` or any other state.
- Never ask for Jira credentials. Missing Jira env vars are a configuration blocker or a user-approved no-Jira exception, depending on `jira-policy`.


## Runtime adapter guidance

The portable core of this skill is role-based. Subagents are optional runtime adapters, not a requirement.

Portable delegated roles:

| Role | Capability |
|---|---|
| `explorer` | read-only repository and context exploration |
| `document_reviewer` | review roadmap, brainstorm, plan, and work-package artifacts |
| `worker` | implement exactly one approved work package without shipping |
| `code_reviewer` | review current implementation/diff without mutating unless explicitly allowed |

Delegation policy:

- Use delegated agents only when the host runtime supports them and the work can be isolated safely.
- `subagent-model:<value>` is advisory and runtime-specific. It may guide model selection where the runtime supports it, but it never blocks the portable workflow.
- Missing agent definitions, missing TOML files, or different model names are not blockers. Continue inline or artifact-only when delegation is unavailable.
- Parallel or delegated mutation requires isolated worktrees/checkouts and non-overlapping scopes. Without isolation, reviewers must be read-only and workers must not stage, commit, push, create PRs, transition Jira, or run broad mutation-prone flows.

Codex adapter examples are bundled in `assets/codex-agents/`. They currently recommend `gpt-5.3-codex`, but that is a Codex-specific default, not a universal contract.

Suggested Codex installation in a repo:

```bash
mkdir -p .codex/agents
cp <compound-master-skill>/assets/codex-agents/*.toml .codex/agents/
```

## Skill dependency map

Resolve these logical roles during preflight:

| Role | Canonical portable skill | Required when | Known runtime aliases |
|---|---|---|---|
| `brainstorm` | `ce-brainstorm` | artifact generation | `/ce-brainstorm`, `ce:brainstorm`, `compound-engineering:ce-brainstorm` |
| `plan` | `ce-plan` | artifact generation | `/ce-plan`, `ce:plan`, `compound-engineering:ce-plan` |
| `document_review` | `document-review` | artifact generation | `/ce-doc-review`, `ce-doc-review`, `compound-engineering:document-review` |
| `work` | `ce-work` | execution | `/ce-work`, `ce:work`, `compound-engineering:ce-work` |
| `code_review` | `ce-review` | execution | `/ce-code-review`, `ce:review`, `ce-code-review`, `compound-engineering:ce-review` |
| `project_pr` | `krt:release-marshal` | shipping | runtime command/skill with equivalent release marshal capability |
| `gitflow_commit` | `krt:gitflow-knight` | shipping component | runtime command/skill with equivalent gitflow commit capability |
| `clean_rebase` | `krt:rebase-smith` | shipping component | runtime command/skill with equivalent clean rebase capability |
| `jira_workflow` | `krt:jira-scribe` | shipping with Jira | runtime command/skill with equivalent Jira workflow capability |
| `strategy` | `ce-strategy` | optional product anchor | `/ce-strategy`, `ce:strategy` |
| `worktree` | `ce-worktree` | optional isolated parallelism | `git-worktree`, runtime worktree/isolation tool |
| `fallback_pr` | `ce-commit-push-pr` | optional, only with user-approved no-Jira fallback | `git-commit-push-pr`, runtime PR fallback |

Resolution order:

1. Resolve by exact canonical portable skill name.
2. If absent, resolve by a documented runtime alias that the host exposes.
3. If still unresolved, stop for required roles and write a blocker that names the role, canonical skill, aliases checked, and blocked phase.

Blocking policy:

- Missing `brainstorm`, `plan`, or `document_review`: stop immediately.
- Missing `work` or `code_review`: complete artifact generation if possible, then stop before execution.
- Missing `project_pr` or its component skills: stop before shipping.
- Missing `jira_workflow` with `jira-policy:required`: stop before shipping.
- `ce-commit-push-pr` is not equivalent to `krt:release-marshal`; use only if the user explicitly accepts no Jira/status orchestration.

## Argument semantics

- `mode:artifacts` default: run steps 0-5 and stop.
- `mode:execute`: load `compound-master-state.md` and execute ready work packages.
- `mode:full`: generate artifacts, ask for an execution gate, then execute.
- `mode:resume`: continue from the next incomplete state item.
- `pr-granularity:auto` default: choose based on dependency, file overlap, risk, and reviewability.
- `pr-granularity:roadmap-item`: one package per roadmap item unless too large.
- `pr-granularity:plan-unit`: one package per U-ID only when independently mergeable/testable.
- `jira-policy:required` default for shipping.
- `jira-policy:optional`: prefer Jira; allow user-approved PR without Jira if config is missing.
- `jira-policy:skip`: do not create or transition Jira artifacts.
- `parallel:false` default: execute packages serially, even when they are independent.
- `parallel:true`: allow parallel execution only when hard dependencies are clear, file scopes do not overlap dangerously, and isolated worktrees/checkouts are available.
- `review-threshold:P0-P2` default: P0, P1, and P2 findings block review passage.
- `review-threshold:P0-P1`: P0 and P1 findings block review passage; P2 findings are logged as residual work unless the user marks them blocking.
- `review-threshold:P0`: only P0 findings block review passage; P1/P2 findings are logged as residual work unless the user marks them blocking.
- `subagent-model:<value>`: advisory runtime-specific model guidance for delegated agents. Ignore when the runtime does not support model selection.
- Invalid argument values fall back to the documented defaults and should be noted in state.

## Artifact layout

Create as needed:

```text
docs/orchestration/
docs/roadmaps/
docs/work-packages/
docs/review-findings/
```

CE skills normally create:

```text
docs/brainstorms/
docs/plans/
```

Maintain:

```text
docs/orchestration/compound-master-state.md
```

State must track: initiative, mode, date, resolved roles and aliases, runtime adapter/delegation availability, source docs, context readiness result, roadmap path, brainstorm paths, plan paths, work-package paths, dependency waves, branch names, base branches, verification results, code-review status, Jira URLs, PR URLs, blockers, and required user decisions.

## Step 0 — Preflight

1. Resolve every required role from available skills, commands, or agents using the resolution order above.
2. Record runtime adapter and delegation availability. Missing optional agents or model settings do not block the portable workflow.
3. Confirm the current directory is a git repo unless artifact-only docs mode is explicitly intended.
4. Identify integration base:
   - prefer explicit repo docs;
   - else prefer `develop` if present;
   - else use GitHub default branch.
5. Inspect working tree state. If unrelated uncommitted changes exist, ask whether to commit, stash, ignore for artifact-only mode, or abort.
6. Check for `STRATEGY.md`. If absent and product intent is unclear, recommend `ce-strategy` when available.
7. Write/update `docs/orchestration/compound-master-state.md`.
8. For shipping readiness, check only presence/absence of Jira env vars (`JIRA_HOST`, `JIRA_API_TOKEN`, `JIRA_PROJECT_KEY`). Never print values and never ask for credentials.

## Step 1 — Context sufficiency gate

Scan repo docs and relevant source. Look for:

- `AGENTS.md`, `CLAUDE.md` compatibility fallback, `STRATEGY.md`, `README.md`
- `docs/`, `specs/`, `architecture/`, `adr/`, `docs/adr/`
- PRDs, feature specs, API contracts, schemas, migrations, runbooks, existing roadmaps/plans/brainstorms
- package/build/test config files
- delivery docs for branches, CI, releases, Jira, and PR conventions

Minimum context required:

1. Product intent: target problem, users/personas, outcomes, success criteria, non-goals.
2. Current system shape: major modules/services, core flows, integration boundaries.
3. Technical execution context: stack, package managers, run/test/build commands, conventions.
4. Data/interface context when applicable: schemas, migrations, APIs/events, auth/permissions.
5. Delivery context: branch/release conventions, CI expectations, deployment constraints, tracker conventions.
6. Existing scope context: backlog/roadmap/known gaps or enough specs to identify missing work without inventing direction.

If insufficient, write:

```text
docs/orchestration/YYYY-MM-DD-context-readiness.md
```

Include found docs, missing categories, why roadmap generation is unsafe, and minimum docs to create. Recommend concrete next docs such as `STRATEGY.md`, `docs/architecture.md`, `docs/api-contracts.md`, `docs/data-model.md`, and `docs/delivery-workflow.md`. Then stop.

## Step 2 — Roadmap generation

If context is sufficient, create:

```text
docs/roadmaps/YYYY-MM-DD-NNN-<initiative-slug>-roadmap.md
```

Use the next available zero-padded sequence for the date and slug. If a matching artifact already exists, resume/update only when that is the explicit mode or user intent; otherwise create the next sequence. Never overwrite an existing roadmap silently.

Template:

```markdown
---
title: [Roadmap title]
status: active
date: YYYY-MM-DD
source_docs:
  - path/to/source.md
---

# [Roadmap title]

## Context Sufficiency Summary
- [What was found]
- [Why this is enough]

## Source Inventory
| Source | Contribution | Confidence |
|---|---|---|

## Roadmap Items
- RDM-001. **[Item name]**
  - Outcome: [user/system outcome]
  - Why now: [reason from docs]
  - Scope boundary: [included/excluded]
  - Hard depends on: [None / RDM-###]
  - Soft sequencing preference: [None / RDM-###]
  - Blocks/enables: [RDM-###]
  - Risk: [low/medium/high + why]
  - Expected brainstorm: `docs/brainstorms/...`
  - Expected plan: `docs/plans/...`
  - Suggested package: [roadmap-item / split by U-ID later]

## Dependency Graph
[Mermaid graph or bullet dependency map]

## Parallelization Waves
- Wave 1: [independent items]
- Wave 2: [items depending on Wave 1]

## Branch and PR Strategy
| Package candidate | Base branch | PR type | Dependency | Notes |
|---|---|---|---|---|

## Blockers and User Decisions
- [Decision needed before brainstorm/plan/work]
```

Dependency rules:

- Hard dependency = cannot safely implement dependent item before prerequisite.
- Soft sequencing = preference, not blocker.
- Mark independent items for possible parallel work.
- If dependency uncertainty affects branch strategy or product behavior, ask before execution.

Review the roadmap with the resolved `document_review` role:

```text
Skill("<document_review>", "mode:headless <roadmap-path>")
```

Apply safe document fixes. If findings change scope, behavior, dependency order, or PR strategy, ask the user one blocking question at a time. Rerun until no blocking doc findings remain.

## Step 3 — Brainstorm per roadmap item

For each roadmap item in dependency order:

```text
Skill("<brainstorm>", "Roadmap item RDM-### from <roadmap-path>. Generate or update a requirements document for this item only. Use repo-relative paths. Do not implement. Preserve dependencies, non-goals, and scope boundaries from the roadmap.")
```

Rules:

- User participates actively.
- Do not parallelize interactive brainstorms.
- Subagents may inspect repo/source docs read-only, but may not replace user product decisions.
- Decisions about actors, scope, product behavior, permissions, data handling, UX, or success criteria must come from existing docs or the user.

After each requirements doc:

```text
Skill("<document_review>", "mode:headless <requirements-doc-path>")
```

Loop safe fixes and user decisions until no blocking document findings remain.

## Step 4 — Plan per brainstorm

For each reviewed requirements doc:

```text
Skill("<plan>", "<requirements-doc-path>")
```

Then verify the generated plan has stable U-IDs, dependencies, repo-relative files/references, test scenarios, and verification criteria.

Run explicit plan review:

```text
Skill("<document_review>", "mode:headless <plan-path>")
```

Loop until blocking findings are resolved. Do not invent product behavior to satisfy review. Route product gaps back to brainstorm or ask the user.

A plan is work-ready only when product blockers are resolved, implementation units are clear, test expectations are explicit enough for the resolved `work` role, and document review has no blocking findings.

## Step 5 — Derive work packages

A work package is the atomic PR/Jira unit for this orchestration. It can include one roadmap item, one plan U-ID, or a cohesive group of U-IDs.

Granularity heuristics:

- Split when units have independent value, minimal file overlap, separate risk domains, and clean independent verification.
- Combine when units share migrations/API contracts/core files, depend tightly on each other, or would create noisy stacked PRs.
- High-risk surfaces may deserve smaller packages but must remain mergeable and testable.

Write each package to:

```text
docs/work-packages/YYYY-MM-DD-NNN-<rdm-id>-<package-slug>-work-package.md
```

Use the next available zero-padded sequence for the date and slug. Resume/update only when that is explicit; otherwise create the next sequence.

Template:

```markdown
---
title: [Work package title]
status: ready
roadmap_item: RDM-###
origin_roadmap: docs/roadmaps/...
origin_brainstorm: docs/brainstorms/...
origin_plan: docs/plans/...
units: [U1, U2]
base_branch: [integration branch or parent branch]
pr_strategy: [independent|stacked]
jira_policy: [required|optional|skip]
---

# [Work package title]

## Scope
[Only what this package implements]

## Non-goals
[Explicit exclusions]

## Dependencies
- Requires: [None / package IDs / branch / PR]
- Blocks: [package IDs]

## Implementation Units
[Relevant U-ID summaries]

## Files and Tests
[Repo-relative files and expected tests]

## Verification Gate
- [Commands/outcomes that must pass]

## Review Gate
- Code review threshold: [configured `review-threshold`; default P0-P2]
- Findings below threshold: log unless user marks blocking

## Branch and PR Handoff Inputs
- Branch name: [feat/rdm-001-slug]
- PR base: [develop/main/parent branch]
- PR title:
- PR body bullets:
- Verification results location:

## Jira Handoff Inputs
- Jira policy: [required|optional|skip]
- Suggested issue type: Tarea
- Suggested subtask behavior: create/reuse subtask when parent is provided
- Jira summary:
- Jira description:
```

Run the resolved `document_review` role in headless mode on every work package. Fix document blockers before execution.

If `mode:artifacts`, stop here and return artifact paths, waves, branch strategy, and blockers.

## Step 6 — Execution wave planning

Classify packages:

- Independent: no hard dependency and no dangerous file overlap.
- Dependent: requires another package, branch, PR, schema, API, or merged change.
- Overlapping: touches files also touched by another package.
- High-risk: auth, security, payments, PII, migrations, public API, deployment, permissions, external APIs, shared contracts.

Parallelism rules:

- Independent packages may branch from integration base.
- Dependent packages wait for merge or become stacked PRs based on parent branch.
- Overlapping/high-risk packages run serially unless the user explicitly accepts risk and isolation exists.
- `parallel:false` forces serial execution.
- `parallel:true` only permits parallel work when isolated worktrees/checkouts exist and package scopes do not overlap dangerously.
- Parallel subagents require worktree isolation. If no isolation, subagents must not stage, commit, push, create PRs, transition Jira, or run broad mutation-prone flows.

## Step 7 — Execute package with the resolved work role

Before executing a package, verify the resolved `work` role or worker supports implementation-only/no-shipping mode. If that capability cannot be confirmed, stop before execution and continue artifact-only unless the user explicitly chooses a different workflow.

For each package in safe order:

```text
Skill("<work>", "<work-package-path>\n\nExecution constraint: implement and validate this package only. Do not invoke PR creation, ce-commit-push-pr, Jira transitions, or any shipping workflow. Leave pending commits/changes for krt:release-marshal. Stop after implementation, relevant tests, and a concise verification summary.")
```

Completion gate:

- Expected files changed/created.
- Relevant tests run or a no-test justification recorded.
- Verification gate passes.
- Task tracker shows implementation complete.
- Pending changes/commits are coherent and ready for `krt:release-marshal`.
- No unresolved product decision remains.

If the resolved `work` role cannot avoid its own PR/shipping flow, stop before duplicate shipping. If it already created or found an open PR, record it and ask whether to use/update that PR rather than invoking `krt:release-marshal` again.

## Step 8 — Code review and fix loop

Preferred review:

```text
Skill("<code_review>", "mode:autofix plan:<origin-plan-path> base:<base-branch>")
```

Use read-only review when mutation is unsafe:

```text
Skill("<code_review>", "mode:report-only plan:<origin-plan-path> base:<base-branch>")
```

Loop:

1. Run review.
2. If safe autofixes were applied, rerun relevant tests.
3. Leave review-fix changes for `krt:release-marshal` commit planning unless project policy requires immediate commits.
4. For findings at or above the configured `review-threshold`, or any gated/manual correctness, security, data, contract, or test coverage finding:
   - write `docs/review-findings/<package-slug>-round-N.md`;
   - ask the user only for non-inferable decisions;
   - invoke the resolved `work` role on the findings doc with the same no-shipping constraint;
   - rerun tests and review.
5. Log P3/advisory findings unless the user marks them blocking.
6. Stop after three rounds if blockers remain. Do not open PR unless the user explicitly accepts residual risk.

Passing gate: no actionable finding at or above the configured `review-threshold`, no unresolved security/data/contract finding, tests pass, advisory findings recorded.

## Step 9 — Handoff to krt:release-marshal

When implementation and review gates pass, invoke `krt:release-marshal`. Do not duplicate its internal procedures.

`krt:release-marshal` owns:

- branch/commit hygiene via `krt:gitflow-knight`;
- clean rebase via `krt:rebase-smith`;
- Jira issue/subtask create-or-reuse via `krt:jira-scribe`;
- PR body/title construction;
- push and PR creation via `gh`;
- reviewer proposal/request with confirmation;
- Jira transition offer after PR creation.

Invocation shape:

```text
Skill("<project_pr>", "Run the full krt:release-marshal workflow for this completed work package.\n\nWork package: <work-package-path>\nRoadmap item: RDM-###\nOrigin plan: <origin-plan-path>\nCurrent branch: <branch-name>\nIntended base: <base-branch>\nJira policy: <required|optional|skip>\nSuggested Jira summary: <summary>\nSuggested Jira description: <description>\nSuggested PR title: <title>\nSuggested PR body bullets:\n- <change>\n- <change>\nVerification results:\n- <command/result>\n\nUse krt:release-marshal exactly. Do not run tests unless the user explicitly asks; use the verification results above. Ask before external mutations or notifications according to krt:release-marshal. After PR creation, offer Jira transition to En Revisión using krt:jira-scribe and the real transition list.")
```

PR tree safety:

- Independent PRs target integration/default branch.
- Stacked PRs target parent package branch and declare dependency in PR body.
- Do not retarget stacked PRs silently.
- Do not combine unrelated roadmap items unless grouped in one work package.
- If an open PR exists for the branch, do not create a duplicate.
- If Jira is required and Jira config is missing, stop with a configuration blocker.
- If Jira is optional and config is missing, let `krt:release-marshal` ask whether to continue without Jira.

After handoff, record Jira URL, PR URL, status, branch, base, reviewers, and blockers in state.

## Step 10 — Continue waves or finish

After each wave:

- Refresh roadmap/work-package status.
- Recompute dependencies based on open/merged PRs.
- For dependent packages, wait for merge or branch from parent PR branch.
- Do not start dependent work from the wrong base.

At the end, write:

```text
docs/orchestration/YYYY-MM-DD-compound-master-summary.md
```

Include roadmap, brainstorms, plans, packages, waves, branches, tests, review rounds, Jira tasks, PRs, blockers, residual advisory findings, and next actions.

## Status model

Use these statuses in state and work-package frontmatter:

```text
context-blocked
roadmap-ready
brainstorm-ready
plan-ready
package-ready
execution-ready
in-progress
implementation-complete
review-fix-needed
review-passed
pr-handoff-started
pr-opened
blocked
completed
```

## Failure behavior

Stop and write the blocker into `compound-master-state.md` when:

- required artifact roles are missing;
- execution roles are missing for requested execution;
- a required role cannot be resolved by canonical name or documented runtime alias;
- requested delegation or parallel execution lacks safe isolation;
- the resolved work role cannot support implementation-only/no-shipping behavior;
- PR/Jira skills are missing for shipping;
- context is insufficient;
- product decisions cannot be inferred;
- plans lack units/dependencies/tests after review;
- review blockers remain after three loops;
- branch base is ambiguous or would degrade the git tree;
- Jira is required but configuration is missing;
- PR handoff would duplicate a PR or target the wrong base;
- the resolved `work` role already shipped and `krt:release-marshal` would duplicate it.

Tell the user exactly what input or action is needed before continuing.
