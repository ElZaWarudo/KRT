---
name: krt-compound-master
description: >
  Discovery-gated artifact-first orchestrator for compound-engineering product delivery. Resolves roadmap/readiness generation,
  runs brainstorm/plan/document-review loops, derives
  mergeable work packages, and later executes each package through resolved work/code-review roles before
  handing shipping to krt-release-marshal with CI break-prevention evidence. Use when turning an existing documented software project
  into a sequenced roadmap and PR/Jira delivery program. Runtime aliases may expose this as
  krt:compound-master.
argument-hint: >
  [initiative description or docs path]
  [mode:artifacts|mode:execute|mode:full|mode:resume]
  [package:<work-package-path>]
  [pr-granularity:auto|roadmap-item|plan-unit]
  [jira-policy:required|optional|skip]
  [production:unknown|live|preprod|prototype]
  [parallel:true|false]
  [delegation:auto|ask|inline]
  [review-threshold:P0-P2|P0-P1|P0]
  [subagent-model:<runtime-specific-model>]
---

# Compound Master

Compound Master coordinates existing skills. It does **not** replace Compound Engineering and it does **not** duplicate `krt-release-marshal` (`krt:release-marshal` in alias-friendly runtimes).

Default posture: **artifact-first after discovery**. Generate durable artifacts from explicit context and user decisions; execute later only when the user explicitly asks or `mode:full` reaches its execution gate. The brainstorm step is the main product-discovery gate, not a paperwork shortcut.

Core pipeline:

1. Preflight skills, repo, branch, delegation, Jira readiness, and context.
1. Resolve production posture: whether this is a live production system, pre-production system, prototype, or unknown.
2. Invoke the required roadmap generator to create either a roadmap or a readiness report.
3. Review the roadmap or stop on readiness.
4. Run one interactive brainstorm per roadmap item before writing or finalizing that item's requirements.
5. Run one plan per reviewed brainstorm document.
6. Review roadmap, brainstorms, plans, and work packages with the resolved document-review role.
7. Derive work packages that map to independently reviewable PR/Jira units.
8. Execute each ready package with the resolved work role in implementation-only/no-shipping mode.
9. Keep Security Sentinel watch active by default for high-risk packages during execution, collecting read-only notes as files change.
10. Review implementation with the resolved code-review role, looping fixes until the configured threshold passes.
11. After the work-review loop finishes, run the resolved security review role for high-risk packages before release handoff, using watch notes as input.
12. Hand the finished package to `krt-release-marshal`, which owns commits, clean rebase, Jira, GitHub PR, reviewer requests, and approved post-PR Jira transition to `En Revisión`.
13. Record CI break-prevention evidence before handoff; if CI later breaks, escalate to the dedicated CI investigation workflow.

## Load References

- Roadmap/readiness criteria and templates are owned by the resolved `roadmap_generator` role.
- Load `references/artifact-templates.md` before writing work-package, artifact closeout, or summary files.
- Load `references/execution-flow.md` for Steps 6-9 execution, verification, code-review, and release handoff detail.
- Load `references/status-and-failures.md` when updating state, selecting statuses, or producing blocker/closeout output.

## Non-Negotiable Rules

- Resolve every referenced role from the host platform's available skills, commands, or agents. Never guess short names.
- Treat canonical hyphenated skill names as the portable default. Runtime forms such as `krt:release-marshal`, `/ce-plan`, `ce:plan`, or `compound-engineering:ce-plan` are aliases only when the host exposes them.
- Treat `Skill("<role>", "...")` examples as orchestration pseudocode. Translate them to the current runtime's actual skill, command, or agent API.
- Use document-review roles for documents and code-review roles for implementation/diffs.
- Do not implement before a written and reviewed plan exists.
- Do not continue past roadmap generation when context is insufficient. Context insufficiency is blocking and should come from the resolved `roadmap_generator` readiness report.
- Do not skip the interactive brainstorm for a roadmap item merely because the roadmap, existing docs, or prior references look detailed. Existing context can seed the questions, but the user owns product and architecture decisions.
- Treat "continue", "resume", "next step", or "siguiente paso" as permission to advance to the next required gate, not as permission to bypass the brainstorm conversation.
- Skip or compress brainstorm only when the current invocation explicitly asks to skip discovery, run non-interactively, or use existing decisions as final. Record that override in state and list the risks.
- Do not invent product behavior, authorization rules, data contracts, Jira transitions, release constraints, branch bases, or dependency edges. Ask one blocking question at a time.
- Do not invent production posture. If the repo or user context does not make clear whether the system is live, pre-production, prototype, or unknown, record `production:unknown` and ask before making risky compatibility, migration, deletion, rollback, or data-shape decisions.
- Treat `production:live` as a compatibility-preserving default: prefer additive changes, feature flags, migrations with rollback/forward plans, backwards-compatible API changes, explicit deployment notes, and stronger regression evidence. Breaking pre-existing behavior requires explicit user/product approval and recorded rationale.
- Treat `production:prototype` as permission to move faster only after recording that posture. Even then, do not remove user data, credentials, security controls, or documented contracts without explicit approval.
- Use repo-relative paths in generated documents.
- Do not edit CE plan bodies as progress checklists. Progress lives in `compound-master-state.md`, work-package status, task tracking, commits, Jira, and PRs.
- A PR unit is a **work package**, not every plan bullet. Avoid PR-per-microtask.
- A work package may contain multiple plan implementation units. It may implement all units from a roadmap item in one integrated PR only when there is strong integration/dependency coupling, and that rationale must be recorded. Executing one package in one run must not erase that structure: preserve the U-ID/unit sequence in prompts, progress state, verification, review, release handoff, and summary. If the plan defines three units, the execution should report those three unit outcomes even when one worker implements them in a single pass.
- Keep planning IDs out of human-facing release text. `RDM-001`, `U1`, date sequences, and package numbers may appear in metadata, paths, dependency tables, and state, but not in suggested Jira summaries/descriptions, commit messages, PR titles, PR body bullets, or branch names unless the user or repo convention explicitly requires them.
- Do not let the work phase invoke its own PR/shipping flow. Shipping is delegated to `krt-release-marshal`.
- Do not open PRs from protected branches: `main`, `master`, or `develop`.
- Do not transition Jira outside an approved release plan. `krt-jira-scribe` must fetch real transitions and require confirmation before `En Revisión` or any other state; an accepted `krt-release-marshal` plan may count as confirmation for automatic post-PR transition to `En Revisión` when it names the issue, target status, and fallback behavior.
- Treat verification results as release-readiness evidence, not public PR copy. Do not put test commands, test output, or verification summaries in suggested PR body bullets unless the user, repo template, or project convention explicitly requires it.
- Require an Impact Scan before `review-passed` when a package changes an API contract, endpoint, binding, shared helper, schema, payload, auth/tenant/ownership behavior, or test fixture contract. The scan must identify consumers and expand required tests from those consumers.
- When the Impact Scan touches auth, permissions, roles, scopes, tenant ownership/isolation, endpoint gates, payload contracts, or fixtures, explicitly search for contract-drift tests before release. Look for exact-list expectations, snapshots, allowlists, `deepStrictEqual`/`toEqual`, role bundles, permission normalization, generated bindings, seeded tenants/users, and fixture setup that may encode the old contract.
- Verification evidence must be surface-aware for broad packages. Do not record only "tests pass"; record the changed surfaces and the evidence for each relevant surface, such as permissions/role-bundle checks, normalization checks, endpoint gates, tenant isolation, generated client contracts, migrations, config, and docs.
- For broad packages, provide suggested logical commit grouping to `krt-release-marshal`. Prefer reviewable commits by natural boundary, while keeping each commit internally coherent. Do not collapse persistence/schema, service/integration behavior, API/generated contracts, config/deployment wiring, focused tests, and docs into one or two package-sized commits when those surfaces changed separately.
- Treat PR creation as a handoff milestone, not proof that CI is healthy. Compound Master should prevent predictable CI breaks before handoff by expanding contract tests, verification evidence, and release notes. If CI later fails, do not spin in an observation loop; invoke or recommend the dedicated CI investigation workflow and keep the package marked as release-follow-up until the incident has an owner.
- Never ask for Jira credentials. Missing Jira env vars are a configuration blocker or a user-approved no-Jira exception, depending on `jira-policy`.

## Stop Discipline

Whenever this skill intentionally stops, pauses for a gate, or cannot continue, return a visible closeout. Include current phase/status, written or updated paths, ready work, blockers or "No blockers", recommended next action, and the exact next invocation when one exists.

If the next operational step is obvious and safe, do it instead of stopping. The brainstorm gate is different: ask even when there is enough context to draft, because its purpose is to surface and confirm product and architecture choices before artifacts harden.

The lead owns orchestration continuity. When a worker returns, the lead must integrate the result, run or attempt local verification, continue to review, and hand off to release when gates pass. Do not stop merely because local stack startup, test execution, linting, or review remains.

Do not stop between a passing `work`/verification/review loop and the start of `krt-release-marshal`. Starting the marshal is not shipping; it is the step that prepares and presents the release plan. The user-facing pause belongs inside `krt-release-marshal` when it shows its workflow/PR/Jira plan and asks for owned approvals.

If the current package is waiting on an already-open PR to merge and the user says "continue", "resume", "next", or similar, treat that as permission to consider the next ready package, but do not advance until the integration base has been refreshed and inspected. Fetch and inspect the branch that receives PRs (`develop` when present, otherwise the GitHub default or recorded release base), compare it with the current/parent PR branch, and record whether new upstream changes, conflicts, or release-follow-up blockers affect the next package. Continue only when that base check supports a clean strategy. Prefer a stacked PR from the parent PR branch, or another explicit branch strategy that `krt-rebase-smith` can later rebase cleanly onto the refreshed base. Stop when the next package requires the merged artifact, the parent PR has unresolved release-follow-up blockers, the refreshed base introduces incompatible changes or likely conflicts, or no clean branch/base strategy can be named.

## Runtime Adapter Guidance

The portable core is role-based. Subagents are optional runtime adapters.

Portable delegated roles:

| Role | Capability |
|---|---|
| `explorer` | read-only repository and context exploration |
| `document_reviewer` | review roadmap, brainstorm, plan, and work-package artifacts |
| `worker` | implement exactly one approved work package without shipping |
| `code_reviewer` | review current implementation/diff without mutating unless explicitly allowed |
| `security_watcher` | read-only incremental security watch during execution for high-risk packages |
| `security_reviewer` | read-only focused security review for high-risk packages or system slices |

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
| `roadmap_generator` | `krt-roadmap-cartographer` | artifact generation | `krt:roadmap-cartographer`, runtime roadmap cartographer equivalent |
| `brainstorm` | `ce-brainstorm` | artifact generation | `/ce-brainstorm`, `ce:brainstorm`, `compound-engineering:ce-brainstorm` |
| `plan` | `ce-plan` | artifact generation | `/ce-plan`, `ce:plan`, `compound-engineering:ce-plan` |
| `document_review` | `document-review` | artifact generation | `/ce-doc-review`, `ce-doc-review`, `compound-engineering:document-review` |
| `work` | `ce-work` | execution | `/ce-work`, `ce:work`, `compound-engineering:ce-work` |
| `code_review` | `ce-review` | execution | `/ce-code-review`, `ce:review`, `ce-code-review`, `compound-engineering:ce-review` |
| `security_review` | `krt-security-sentinel` | optional high-risk package security review | `krt:security-sentinel`, runtime security sentinel equivalent |
| `project_pr` | `krt-release-marshal` | shipping | `krt:release-marshal`, runtime release marshal equivalent |
| `ci_investigator` | `krt-ci-questor` | optional escalation when CI breaks | `krt:ci-questor`, runtime CI investigator equivalent |
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

- Missing `roadmap_generator`, `brainstorm`, `plan`, or `document_review`: stop immediately.
- Missing `work` or `code_review`: complete artifact generation if possible, then stop before execution.
- Missing `security_review`: do not block normal execution. If a high-risk package needs security review, search for another available security-review skill first; if none exists, perform a direct evidence-based security pass using the same expected output.
- Missing `project_pr` or component skills: stop before shipping and suggest:
  `npx -y skills add ElZaWarudo/krt --skill krt-release-marshal --skill krt-gitflow-knight --skill krt-rebase-smith --skill krt-jira-scribe -g`
- Missing `ci_investigator`: do not block release handoff or CI incident handling. If CI breaks later, search for another available CI/log/check investigation skill first. If none is available, Compound Master performs direct evidence-first triage itself using the same report shape.
- Missing `jira_workflow` with `jira-policy:required`: stop before shipping and suggest installing `krt-jira-scribe` or rerunning with `jira-policy:optional|skip`.
- `ce-commit-push-pr` is not equivalent to `krt-release-marshal`; use only if the user explicitly accepts no Jira/status orchestration.

## Arguments

- `mode:artifacts` default: run artifact steps and stop with an artifact closeout.
- `mode:execute`: load state and execute ready work packages. If no `package:` is provided, choose the first unblocked package from the earliest safe wave and continue unless that changes scope/order.
- `mode:full`: generate artifacts, return the artifact closeout, ask one execution gate, then execute the recommended first package or first safe wave.
- `mode:resume`: continue from the next incomplete state item; first summarize why it was selected.
- `package:<work-package-path>`: execute or resume only that package.
- `production:unknown|live|preprod|prototype`: sets the production posture. Default `unknown` unless explicit user context or strong repo evidence supports another value.
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
docs/work-packages/RDM-###-<roadmap-item-slug>/
docs/review-findings/
```

CE skills normally create:

```text
docs/brainstorms/
docs/plans/
```

Maintain `docs/orchestration/compound-master-state.md`. State must track initiative, mode, date, resolved roles, runtime/delegation availability, delegation decisions and telemetry, source docs, context readiness, production posture, roadmap, brainstorms, plans, work packages, waves, branch/base choices, Impact Scan status, security watch notes, security review status, CI break-prevention checks, surface-aware verification, review status, Jira/PR URLs, release-follow-up blockers, and required user decisions.

## Workflow

### Step 0 - Preflight

Resolve roles, record runtime/delegation availability, confirm repo status, identify integration base (`develop` if present, otherwise GitHub default), inspect working tree, check for `STRATEGY.md` when product intent is unclear, resolve production posture, update state, and check only the presence of Jira env vars (`JIRA_HOST`, `JIRA_API_TOKEN`, `JIRA_PROJECT_KEY`).

Production posture resolution:

- Accept an explicit argument first: `production:live`, `production:preprod`, `production:prototype`, or `production:unknown`.
- Otherwise infer only from strong evidence such as production deploy docs, live environment config, incident/runbook docs, release history, real user/data language, or explicit prototype/sandbox language.
- If evidence is mixed or weak, set `production:unknown` and ask a single blocking question before any package would change persistence, API compatibility, auth, tenant behavior, deployment, data deletion, irreversible migrations, or existing user workflows.
- Record the posture, evidence, confidence, and consequences in `compound-master-state.md`.
- Feed the posture into roadmap review, brainstorm questions, work-package risk classification, verification gates, release handoff, and rollback/deployment notes.

### Step 1 - Roadmap Generator Gate

Invoke the resolved `roadmap_generator` role for the initiative. The role must return exactly one primary artifact classification:

```text
artifact_kind: roadmap | readiness-report
artifact_path: docs/...
```

If `artifact_kind` is `readiness-report`, update `compound-master-state.md` with the readiness path, missing context summary, and recommended next prompt. Stop with a context-blocked closeout.

If `artifact_kind` is `roadmap`, update `compound-master-state.md` with the roadmap path and continue to Step 2.

### Step 2 - Roadmap Review

Review the roadmap from `roadmap_generator` with the resolved `document_review` role and fix blockers without inventing product behavior. Ask only when findings change scope, behavior, dependency order, or PR strategy.

### Step 3 - Brainstorm Per Roadmap Item

For each roadmap item in dependency order, invoke the resolved `brainstorm` role for that item only. The brainstorm must be interactive unless the user explicitly requested non-interactive discovery in the current invocation.

Use existing docs, roadmap details, and references to prepare a focused mini-discovery, then ask the highest-leverage question first. Continue through enough questions to settle the decisions that would otherwise be invented in the requirements document. For non-trivial items, expect at least one product question and one architecture/integration question before writing or finalizing requirements.

When the user asks to resume or continue into the next roadmap item, start the brainstorm gate instead of drafting requirements directly. A good response shape is:

```text
Next required gate is the brainstorm for <roadmap item>. Existing context suggests <brief summary>, but these decisions still need confirmation:
- <decision 1>
- <decision 2>

First question: <single focused question>
```

If the user explicitly skips brainstorm, record the override and assumptions in `compound-master-state.md`, mark the generated requirements as assumption-backed, and include follow-up decisions in the document. User product decisions remain with existing docs or the user. Review each requirements doc with `document_review` and loop safe fixes.

### Step 4 - Plan Per Brainstorm

Invoke the resolved `plan` role for each reviewed requirements doc. Verify stable U-IDs, dependencies, repo-relative paths, test scenarios, and verification criteria. Review plans with `document_review` until no blocking findings remain.

### Step 5 - Derive Work Packages

Load `references/artifact-templates.md`. Create independently reviewable packages under roadmap-item folders in `docs/work-packages/RDM-###-<roadmap-item-slug>/`. Each package must align explicitly to the origin plan units it includes, excludes, splits, or combines. Review every package with `document_review`. If `mode:artifacts`, stop only after an explicit artifact closeout and exact next invocation.

### Step 6 - Execution Wave Planning

Load `references/execution-flow.md`. Ask/resolve the execution delegation gate before planning KRT-owned subagents. Apply the delegation decision matrix, budget, and telemetry rules before launching any subagent. Classify packages as independent, dependent, overlapping, or high-risk. Execute serially unless `parallel:true` and isolation make parallel work safe.

### Step 7 - Execute Package

Invoke the resolved `work` role in implementation-only/no-shipping mode. For high-risk packages, start Security Sentinel watch by default before or alongside work execution. The watch is read-only and tracks changed files, risky surfaces, missing negative tests, and likely gate inputs without mutating code or blocking normal progress except for obvious P0/P1 risk. The worker returns changed files, verification attempted/results/skips, and questions. The lead inspects the diff, integrates security watch notes, starts documented local services when safe, runs/attempts verification, fixes straightforward failures inline or via `work`, and continues to review.

### Step 8 - Code Review And Fix Loop

Invoke the resolved `code_review` role normally. Prefer autofix when safe; retry with documented report-only/inline mode only if the runtime refuses agent launch. For high-risk packages, use optional read-only reviewer fan-out only after the main review path is clear and within the delegation budget. Findings at or above `review-threshold`, or any unresolved security/data/contract/test blocker, loop through `work` and review. Stop after three blocked rounds.

### Step 9 - Security Sentinel Gate

After the work-review loop passes, load `references/execution-flow.md` and run the security review gate for packages that touch auth/authz, tenant isolation, secrets, PII, public API security, external integrations, deployment exposure, CI/CD permissions, supply chain, or other high-risk surfaces. Prefer `krt-security-sentinel` when available; otherwise resolve another security-review skill or perform a direct evidence-based security pass. Feed all Security Watch notes into this gate. Security blockers loop back through `work` and `code_review` before release handoff.

### Step 10 - Release Marshal Handoff

When implementation and review gates pass, invoke `krt-release-marshal`. Do not stop after saying it is the next step. Include work package path, roadmap item, origin plan, current branch, intended base, Jira policy, suggested Jira summary/description, PR title/body bullets, suggested commit grouping when natural boundaries exist, verification results as internal release-readiness context, and instruction to include automatic reviewer handling and automatic post-PR Jira transition to `En Revisión` in the release plan when Jira context exists.

### Step 11 - CI Break-Prevention And Escalation

Load `references/execution-flow.md`. Before and during release handoff, record the CI break-prevention evidence that should keep predictable checks green: contract-drift scan, consumer tests, surface-aware verification, and known CI-only gaps. Do not poll CI in a loop. If the user reports a broken check or the release workflow surfaces one, use `krt-ci-questor` when available, resolve another CI investigator if possible, or perform direct evidence-first triage inline. Record a release-follow-up blocker until the CI incident has a cause, owner, and next action.

### Step 12 - Continue Waves Or Finish

Refresh state, dependencies, and the integration base after each PR handoff. Before continuing while a parent PR is pending, fetch and inspect the branch that receives PRs (`develop` when present, otherwise the GitHub default or recorded release base). Compare it with the current/parent PR branch, note new commits or likely conflicts in state, and only then decide whether to continue from the parent PR branch as a stacked PR or record another explicit clean-tree strategy that `krt-rebase-smith` can normalize later. Dependent packages wait for merge when the next package needs the merged artifact, the refreshed base changes package assumptions, or the package cannot be stacked cleanly. At the end, write `docs/orchestration/YYYY-MM-DD-compound-master-summary.md`.

## Failure And Status

Load `references/status-and-failures.md` for statuses, blocker rules, closeout shape, and summary requirements.
