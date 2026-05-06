---
name: krt-compound-master
description: >
  Artifact-first orchestrator for compound-engineering product delivery. Validates project context,
  creates a dependency-aware roadmap, runs brainstorm/plan/document-review loops, derives
  mergeable work packages, and later executes each package through resolved work/code-review roles before
  handing shipping to krt-release-marshal. Use when turning an existing documented software project
  into a sequenced roadmap and PR/Jira delivery program. Runtime aliases may expose this as
  krt:compound-master.
argument-hint: >
  [initiative description or docs path]
  [mode:artifacts|mode:execute|mode:full|mode:resume]
  [package:<work-package-path>]
  [pr-granularity:auto|roadmap-item|plan-unit]
  [jira-policy:required|optional|skip]
  [parallel:true|false]
  [delegation:auto|ask|inline]
  [review-threshold:P0-P2|P0-P1|P0]
  [subagent-model:<runtime-specific-model>]
---

# Compound Master

Compound Master coordinates existing skills. It does **not** replace Compound Engineering and it does **not** duplicate `krt-release-marshal` (`krt:release-marshal` in alias-friendly runtimes).

Default posture: **artifact-first**. Generate durable artifacts first; execute later only when the user explicitly asks or `mode:full` reaches its execution gate.

Core pipeline:

1. Preflight skills, repo, branch, delegation, Jira readiness, and context.
2. Block if project documentation is insufficient.
3. Create a dependency-aware roadmap.
4. Run one interactive brainstorm per roadmap item.
5. Run one plan per reviewed brainstorm document.
6. Review roadmap, brainstorms, plans, and work packages with the resolved document-review role.
7. Derive work packages that map to independently reviewable PR/Jira units.
8. Execute each ready package with the resolved work role in implementation-only/no-shipping mode.
9. Review implementation with the resolved code-review role, looping fixes until the configured threshold passes.
10. Hand the finished package to `krt-release-marshal`, which owns commits, clean rebase, Jira, GitHub PR, reviewer requests, and approved post-PR Jira transition to `En Revisión`.

## Load References

- Load `references/context-readiness.md` for Step 1 context sufficiency checks and context-blocked reports.
- Load `references/artifact-templates.md` before writing roadmap, work-package, artifact closeout, or summary files.
- Load `references/execution-flow.md` for Steps 6-9 execution, verification, code-review, and release handoff detail.
- Load `references/status-and-failures.md` when updating state, selecting statuses, or producing blocker/closeout output.

## Non-Negotiable Rules

- Resolve every referenced role from the host platform's available skills, commands, or agents. Never guess short names.
- Treat canonical hyphenated skill names as the portable default. Runtime forms such as `krt:release-marshal`, `/ce-plan`, `ce:plan`, or `compound-engineering:ce-plan` are aliases only when the host exposes them.
- Treat `Skill("<role>", "...")` examples as orchestration pseudocode. Translate them to the current runtime's actual skill, command, or agent API.
- Use document-review roles for documents and code-review roles for implementation/diffs.
- Do not implement before a written and reviewed plan exists.
- Do not generate a roadmap when context is insufficient. Context insufficiency is blocking.
- Do not invent product behavior, authorization rules, data contracts, Jira transitions, release constraints, branch bases, or dependency edges. Ask one blocking question at a time.
- Use repo-relative paths in generated documents.
- Do not edit CE plan bodies as progress checklists. Progress lives in `compound-master-state.md`, work-package status, task tracking, commits, Jira, and PRs.
- A PR unit is a **work package**, not every plan bullet. Avoid PR-per-microtask.
- Keep planning IDs out of human-facing release text. `RDM-001`, `U1`, date sequences, and package numbers may appear in metadata, paths, dependency tables, and state, but not in suggested Jira summaries/descriptions, commit messages, PR titles, PR body bullets, or branch names unless the user or repo convention explicitly requires them.
- Do not let the work phase invoke its own PR/shipping flow. Shipping is delegated to `krt-release-marshal`.
- Do not open PRs from protected branches: `main`, `master`, or `develop`.
- Do not transition Jira outside an approved release plan. `krt-jira-scribe` must fetch real transitions and require confirmation before `En Revisión` or any other state; an accepted `krt-release-marshal` plan may count as confirmation for automatic post-PR transition to `En Revisión` when it names the issue, target status, and fallback behavior.
- Treat verification results as release-readiness evidence, not public PR copy. Do not put test commands, test output, or verification summaries in suggested PR body bullets unless the user, repo template, or project convention explicitly requires it.
- Require an Impact Scan before `review-passed` when a package changes an API contract, endpoint, binding, shared helper, schema, payload, auth/tenant/ownership behavior, or test fixture contract. The scan must identify consumers and expand required tests from those consumers.
- For broad packages, provide suggested logical commit grouping to `krt-release-marshal`. Prefer reviewable commits by natural boundary, while keeping each commit internally coherent.
- Never ask for Jira credentials. Missing Jira env vars are a configuration blocker or a user-approved no-Jira exception, depending on `jira-policy`.

## Stop Discipline

Whenever this skill intentionally stops, pauses for a gate, or cannot continue, return a visible closeout. Include current phase/status, written or updated paths, ready work, blockers or "No blockers", recommended next action, and the exact next invocation when one exists.

If the next step is obvious and safe, do it instead of stopping. Ask only for choices that affect scope, product behavior, destructive actions, external systems, notifications, or decisions the agent cannot infer.

The lead owns orchestration continuity. When a worker returns, the lead must integrate the result, run or attempt local verification, continue to review, and hand off to release when gates pass. Do not stop merely because local stack startup, test execution, linting, or review remains.

Do not stop between a passing `work`/verification/review loop and the start of `krt-release-marshal`. Starting the marshal is not shipping; it is the step that prepares and presents the release plan. The user-facing pause belongs inside `krt-release-marshal` when it shows its workflow/PR/Jira plan and asks for owned approvals.

## Runtime Adapter Guidance

The portable core is role-based. Subagents are optional runtime adapters.

Portable delegated roles:

| Role | Capability |
|---|---|
| `explorer` | read-only repository and context exploration |
| `document_reviewer` | review roadmap, brainstorm, plan, and work-package artifacts |
| `worker` | implement exactly one approved work package without shipping |
| `code_reviewer` | review current implementation/diff without mutating unless explicitly allowed |

Delegation policy:

- Use delegated agents only when the host supports them and the work can be isolated safely.
- Keep the lead as the centralized supervisor. The lead synthesizes subagent output, decides the next step, owns state updates, and controls release handoff.
- Subagents must not coordinate with each other or hand work directly to another subagent unless the runtime provides an explicit team/task system and the current run approved that team workflow.
- Do not add or imply a free-form swarm mode. Use bounded delegation and reviewer fan-out only when the package shape justifies it and the decision is recorded.
- During preflight, record whether direct KRT-owned agent launch is `automatic`, `requires-approval`, or `unavailable`.
- Distinguish direct KRT-owned agent launch from invoking another resolved skill. Do not preemptively downgrade `document_review`, `work`, or `code_review` just because that skill may internally launch agents.
- At the start of any execution phase (`mode:execute`, `mode:resume` when resuming execution/review/release, or `mode:full` after the artifact execution gate), ask one explicit execution delegation gate before deciding whether KRT itself will launch subagents. Do this even when the runtime might support automatic launch, unless the user already included `delegation:inline`, `delegation:ask`, `parallel:true`, "con subagentes", or "sin subagentes" in the current invocation.
- If the user approves subagents, record the approval scope in state and use KRT-owned delegated agents only for isolated, useful roles.
- If the user declines, direct launch is unavailable, or the answer is unclear, set delegation mode to `inline` for this run, continue inline, and record the fallback.
- `subagent-model:<value>` is advisory and runtime-specific.
- Initial delegation budget: at most one mutating worker per work package and at most three read-only reviewer subagents in any review fan-out.
- If a subagent returns low confidence, incomplete context, or unresolved scope assumptions, the lead performs one targeted follow-up exploration/review rather than launching more generic agents.
- Parallel/delegated mutation requires isolated worktrees/checkouts and non-overlapping scopes. Without isolation, reviewers must be read-only and workers must not stage, commit, push, create PRs, transition Jira, or run broad mutation-prone flows.

Execution delegation gate prompt:

```text
KRT can run this package inline or with delegated subagents.
Recommended delegated roles for this execution: <roles/reason>.
Should KRT launch subagents for this execution run, or continue inline?
```

Codex adapter examples are bundled in `assets/codex-agents/`. Suggested installation:

```bash
mkdir -p .codex/agents
cp <compound-master-skill>/assets/codex-agents/*.toml .codex/agents/
```

## Role Resolution

Resolve these logical roles during preflight:

| Role | Canonical portable skill | Required when | Known runtime aliases |
|---|---|---|---|
| `brainstorm` | `ce-brainstorm` | artifact generation | `/ce-brainstorm`, `ce:brainstorm`, `compound-engineering:ce-brainstorm` |
| `plan` | `ce-plan` | artifact generation | `/ce-plan`, `ce:plan`, `compound-engineering:ce-plan` |
| `document_review` | `document-review` | artifact generation | `/ce-doc-review`, `ce-doc-review`, `compound-engineering:document-review` |
| `work` | `ce-work` | execution | `/ce-work`, `ce:work`, `compound-engineering:ce-work` |
| `code_review` | `ce-review` | execution | `/ce-code-review`, `ce:review`, `ce-code-review`, `compound-engineering:ce-review` |
| `project_pr` | `krt-release-marshal` | shipping | `krt:release-marshal`, runtime release marshal equivalent |
| `gitflow_commit` | `krt-gitflow-knight` | shipping component | `krt:gitflow-knight`, runtime gitflow commit equivalent |
| `clean_rebase` | `krt-rebase-smith` | shipping component | `krt:rebase-smith`, runtime clean rebase equivalent |
| `jira_workflow` | `krt-jira-scribe` | shipping with Jira | `krt:jira-scribe`, runtime Jira workflow equivalent |
| `strategy` | `ce-strategy` | optional product anchor | `/ce-strategy`, `ce:strategy` |
| `worktree` | `ce-worktree` | optional isolated parallelism | `git-worktree`, runtime worktree/isolation tool |
| `fallback_pr` | `ce-commit-push-pr` | optional, only with user-approved no-Jira fallback | `git-commit-push-pr`, runtime PR fallback |

Resolution order:

1. Resolve by exact canonical portable skill name.
2. If absent, resolve by a documented runtime alias the host exposes.
3. If still unresolved, stop for required roles and name the role, canonical skill, aliases checked, and blocked phase.

Blocking policy:

- Missing `brainstorm`, `plan`, or `document_review`: stop immediately.
- Missing `work` or `code_review`: complete artifact generation if possible, then stop before execution.
- Missing `project_pr` or component skills: stop before shipping and suggest:
  `npx -y skills add ElZaWarudo/krt --skill krt-release-marshal --skill krt-gitflow-knight --skill krt-rebase-smith --skill krt-jira-scribe -g`
- Missing `jira_workflow` with `jira-policy:required`: stop before shipping and suggest installing `krt-jira-scribe` or rerunning with `jira-policy:optional|skip`.
- `ce-commit-push-pr` is not equivalent to `krt-release-marshal`; use only if the user explicitly accepts no Jira/status orchestration.

## Arguments

- `mode:artifacts` default: run artifact steps and stop with an artifact closeout.
- `mode:execute`: load state and execute ready work packages. If no `package:` is provided, choose the first unblocked package from the earliest safe wave and continue unless that changes scope/order.
- `mode:full`: generate artifacts, return the artifact closeout, ask one execution gate, then execute the recommended first package or first safe wave.
- `mode:resume`: continue from the next incomplete state item; first summarize why it was selected.
- `package:<work-package-path>`: execute or resume only that package.
- `pr-granularity:auto|roadmap-item|plan-unit`: default `auto`, based on dependency, file overlap, risk, and reviewability.
- `jira-policy:required|optional|skip`: default `required`; `optional` allows user-approved PR without Jira if config is missing.
- `parallel:false|true`: default `false`; `true` requires safe dependencies, no dangerous overlap, and isolated worktrees/checkouts.
- `delegation:auto|ask|inline`: default `auto`; during execution, `auto` asks the execution delegation gate once before KRT-owned launches, `ask` always asks even if prior state recorded approval, and `inline` disables KRT-owned agent launches. Resolved skills still own their internal behavior.
- `review-threshold:P0-P2|P0-P1|P0`: default `P0-P2`.
- `subagent-model:<value>`: runtime-specific advisory only.
- Invalid values fall back to defaults and should be recorded in state.

## Artifact And State Paths

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

Maintain `docs/orchestration/compound-master-state.md`. State must track initiative, mode, date, resolved roles, runtime/delegation availability, delegation decisions and telemetry, source docs, context readiness, roadmap, brainstorms, plans, work packages, waves, branch/base choices, Impact Scan status, verification, review status, Jira/PR URLs, blockers, and required user decisions.

## Workflow

### Step 0 - Preflight

Resolve roles, record runtime/delegation availability, confirm repo status, identify integration base (`develop` if present, otherwise GitHub default), inspect working tree, check for `STRATEGY.md` when product intent is unclear, update state, and check only the presence of Jira env vars (`JIRA_HOST`, `JIRA_API_TOKEN`, `JIRA_PROJECT_KEY`).

### Step 1 - Context Sufficiency Gate

Load `references/context-readiness.md`. If context is insufficient, write a readiness report and stop with a context-blocked closeout.

### Step 2 - Roadmap Generation

Load `references/artifact-templates.md`. Create the next `docs/roadmaps/YYYY-MM-DD-NNN-<initiative-slug>-roadmap.md`. Review it with the resolved `document_review` role and fix blockers without inventing product behavior.

### Step 3 - Brainstorm Per Roadmap Item

For each roadmap item in dependency order, invoke the resolved `brainstorm` role for that item only. User product decisions remain with existing docs or the user. Review each requirements doc with `document_review` and loop safe fixes.

### Step 4 - Plan Per Brainstorm

Invoke the resolved `plan` role for each reviewed requirements doc. Verify stable U-IDs, dependencies, repo-relative paths, test scenarios, and verification criteria. Review plans with `document_review` until no blocking findings remain.

### Step 5 - Derive Work Packages

Load `references/artifact-templates.md`. Create independently reviewable packages under `docs/work-packages/`. Review every package with `document_review`. If `mode:artifacts`, stop only after an explicit artifact closeout and exact next invocation.

### Step 6 - Execution Wave Planning

Load `references/execution-flow.md`. Ask/resolve the execution delegation gate before planning KRT-owned subagents. Apply the delegation decision matrix, budget, and telemetry rules before launching any subagent. Classify packages as independent, dependent, overlapping, or high-risk. Execute serially unless `parallel:true` and isolation make parallel work safe.

### Step 7 - Execute Package

Invoke the resolved `work` role in implementation-only/no-shipping mode. The worker returns changed files, verification attempted/results/skips, and questions. The lead inspects the diff, starts documented local services when safe, runs/attempts verification, fixes straightforward failures inline or via `work`, and continues to review.

### Step 8 - Code Review And Fix Loop

Invoke the resolved `code_review` role normally. Prefer autofix when safe; retry with documented report-only/inline mode only if the runtime refuses agent launch. For high-risk packages, use optional read-only reviewer fan-out only after the main review path is clear and within the delegation budget. Findings at or above `review-threshold`, or any unresolved security/data/contract/test blocker, loop through `work` and review. Stop after three blocked rounds.

### Step 9 - Release Marshal Handoff

When implementation and review gates pass, invoke `krt-release-marshal`. Do not stop after saying it is the next step. Include work package path, roadmap item, origin plan, current branch, intended base, Jira policy, suggested Jira summary/description, PR title/body bullets, suggested commit grouping when natural boundaries exist, verification results as internal release-readiness context, and instruction to include automatic reviewer handling and automatic post-PR Jira transition to `En Revisión` in the release plan when Jira context exists.

### Step 10 - Continue Waves Or Finish

Refresh state and dependencies after each PR handoff. Dependent packages wait for merge or branch from the parent PR branch. At the end, write `docs/orchestration/YYYY-MM-DD-compound-master-summary.md`.

## Failure And Status

Load `references/status-and-failures.md` for statuses, blocker rules, closeout shape, and summary requirements.
