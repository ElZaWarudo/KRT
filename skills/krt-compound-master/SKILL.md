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

Coordinate existing skills. Do not replace Compound Engineering, do not duplicate `krt-release-marshal`, and do not ship from the work phase. Compound Master may prepare PRs for review through release handoff, but it never owns PR or branch merges.

Arguments:

```text
[initiative description or docs path]
[mode:artifacts|mode:execute|mode:full|mode:resume]
[package:<work-package-path>]
[review-unit:<RU#>]
[pr-granularity:auto|review-unit|work-package|roadmap-item|plan-unit]
[jira-policy:required|optional|skip]
[production:unknown|live|preprod|prototype]
[parallel:true|false]
[delegation:auto|ask|inline]
[worktree-policy:avoid|auto|required]
[autonomy:manual|guarded|high]
[autonomous-ledger:<path>]
[review-threshold:P0-P2|P0-P1|P0]
[subagent-model:<runtime-specific-model>]
```

Default posture: artifact-first after discovery. Generate durable artifacts from explicit context and user decisions; execute later only when the user explicitly asks or `mode:full` reaches its execution gate. Treat Jira as preferred delivery traceability by default: look for existing Jira context and configuration, pass useful Jira handoff inputs forward, and degrade without blocking when Jira is unavailable unless `jira-policy:required` is explicit.

## Progressive Loading

Load only what the current phase needs:

| Phase | Load |
|---|---|
| Preflight, roles, arguments, paths | `references/role-and-runtime.md`, `references/fast-contract.md` |
| Artifact workflow and gates | `references/workflow-map.md` |
| Work-package templates and review-unit shape | `references/artifact-templates.md` |
| Execution routing | `references/execution-flow.md` |
| Delegation and worker prompts | `references/execution-delegation.md` |
| Impact scans and verification evidence | `references/impact-verification.md` |
| Code review, security, and CI handling | `references/review-security-ci.md` |
| Release handoff | `references/release-handoff.md` |
| State, blockers, and closeouts | `references/status-and-failures.md` |
| Autonomous external mutation | `references/autonomous-mode.md`, `references/autonomy-ledger-schema.md`, `references/autonomous-flow-matrix.md` |

Before writing or reviewing a work package, run:

```bash
python3 <compound-master-skill-dir>/scripts/check_work_package.py <work-package.md>
```

Resolve `<compound-master-skill-dir>` to the directory containing this `SKILL.md`; in installed runtimes this may be `/home/teb/.agents/skills/krt-compound-master`, not `skills/krt-compound-master` inside the target repo.

Before delegating to a weaker or narrower agent, pass the relevant package plus the rules from `references/fast-contract.md` instead of expecting the agent to reconstruct the boundary from the full skill tree.

## Core Pipeline

1. Preflight roles, repo, branch, delegation, Jira posture, production posture, and context.
2. Invoke the resolved roadmap generator for exactly one roadmap or readiness report.
3. Review the roadmap or stop on readiness.
4. Run one interactive brainstorm per roadmap item before finalizing requirements.
5. Review each brainstorm/requirements artifact.
6. Run one plan per reviewed requirements artifact.
7. Review each plan.
8. Derive work packages with focused review units; review units are the default PR/Jira units.
9. Review work packages and their review-unit breakdown.
10. Execute each ready review unit with the resolved work role in implementation-only/no-shipping mode.
11. Keep Security Sentinel watch active by default for high-risk review units.
12. Review implementation with the resolved code-review role and loop fixes until the configured threshold passes.
13. Run the resolved security review role for high-risk review units before release handoff.
14. Record CI break-prevention evidence.
15. Hand the finished review unit to `krt-release-marshal`, which owns commits, rebase, Jira, PR creation, reviewers, PR backlinking, Jira transition, and ledger-bound autonomous merge execution when explicitly authorized.

## Non-Negotiable Rules

- Resolve every referenced role from available skills, commands, or agents. Never guess short names.
- Treat canonical hyphenated skill names as portable; runtime aliases are optional.
- Treat `Skill("<role>", "...")` examples as pseudocode and translate them to the current runtime.
- Use document-review roles for documents and code-review roles for implementation/diffs.
- Do not implement before a written and reviewed plan exists.
- Do not continue past roadmap generation when context is insufficient.
- Do not skip interactive brainstorm unless explicitly asked to skip discovery or run non-interactively; record the override and risks.
- Do not invent product behavior, authorization rules, data contracts, Jira transitions, release constraints, branch bases, or dependency edges.
- Give agents explicit decision rights before execution; escalate product behavior, auth/data contracts, destructive operations, public contract removal, branch/base strategy, required Jira/PR workflow decisions, and production compatibility breakage.
- Do not invent production posture. Use `production:unknown` unless explicit user context or strong repo evidence supports another value.
- Treat `production:live` as compatibility-preserving; breaking existing behavior requires explicit approval and rationale.
- Use repo-relative paths in generated documents.
- Do not edit CE plan bodies as progress checklists; progress lives in state, work-package status, task tracking, commits, Jira, and PRs.
- A PR unit is a review unit, not automatically a work package and not every plan bullet.
- Split broad work packages into review units when review would otherwise be noisy.
- Target <=500 human-authored changed lines per review-unit PR, warn above 900, and require split/rationale above ~1,000. Count generated artifacts, schema dumps, and orchestration docs separately.
- Do not silently drop, stash, or defer related documentation only to keep a functional PR cosmetically narrow. If `docs/brainstorms`, `docs/plans`, `docs/work-packages`, `docs/orchestration/compound-master-state.md`, or product/operator/API docs explain the implemented change, clarify stacked context, or backfill nearby stale behavior docs, keep them in the branch by default and usually in the PR unless the user explicitly wants a split.
- Do not move related documentation into a stash, separate worktree, side branch, or abandoned local diff just to keep the functional PR cleaner. If the user explicitly wants a split, keep both destinations visible in the plan and closeout so the documentation is not orphaned.
- Do not create planning-only branches such as `docs/*-planning` as the normal artifact output. Keep roadmap/brainstorm/plan/work-package/state artifacts on the current integration branch during artifact generation; once the first executable review unit starts, carry the related planning artifacts forward on that first semantic implementation branch unless the user explicitly requests a separate docs shipment.
- Put large generated artifacts or mechanical `*.auto.*` outputs in a separate review unit/commit when practical.
- Keep planning IDs out of human-facing release text.
- Do not let work invoke PR creation, Jira transitions, or shipping workflows.
- Do not open PRs from protected branches.
- Avoid creating worktrees by default. Use the current checkout with normal branch switching for serial work. Create or require worktrees only when the user explicitly requests `worktree-policy:required`, or when `worktree-policy:auto` plus explicit parallel mutating execution makes isolation necessary and safe.
- Do not merge PRs or branches, imply that merge is authorized, or pass merge intent to another role in manual/guarded flow. In autonomous flow, Compound Master may pass a merge candidate only to `krt-release-marshal` when an active `autonomous-ledger:<path>` allows the exact mutation class and the deterministic executor still proves reviewer approval, green required checks, branch protection/ruleset satisfaction, exact target scope, and audit readiness.
- Treat internal code-review, Security Sentinel, CI break-prevention evidence, and an accepted release plan as readiness signals only. They never substitute for GitHub reviewer approval or explicit human merge authorization.
- Treat `autonomy:high` without an active ledger as local autonomy only. It never authorizes PR, branch, reviewer, Jira, or merge side effects.
- Treat verification results as release-readiness evidence, not public PR copy.
- Require an Impact Scan before `review-passed` when a review unit changes API contracts, endpoints, bindings, shared helpers, schemas, payloads, auth/tenant/ownership behavior, or fixture contracts.
- Use a verification ladder: targeted diagnostic, natural affected suite, then repo-specific CI-equivalent command before release handoff or CI-fix PR update.
- Treat PR creation as a handoff milestone, not proof that CI is healthy.
- Never ask for Jira credentials.
- Do not repeatedly ask whether Jira should be used. With the default optional policy, attempt Jira when context/configuration is already present; otherwise record Jira as a non-blocking omitted handoff and continue. Ask only for `jira-policy:required`, ambiguous Jira mutations, or user-visible release-plan approval that already names the intended Jira action and fallback.

## Stop Discipline

Whenever this skill stops, return a visible closeout with current phase/status, written or updated paths, ready work, blockers or "No blockers", recommended next action, and exact next invocation.

When the next action is a `krt-release-marshal` handoff that will likely produce two or more stacked/sibling PRs, preserve release-ready structure in the closeout: summarize `Estado local`, call out stack/base dependencies explicitly, and hand off enough per-PR scope detail that Release Marshal can emit stable `PR1` / `PR2` / `PR3` blocks without reconstructing the split from scratch.
If artifact generation stopped before implementation and no semantic feature branch exists yet, the closeout must not imply that the current planning/docs branch should ship independently. Recommend the first ready review unit invocation from a fresh integration base and state that the related planning artifacts should be carried inside that first implementation branch.

Do not stop between a passing work/verification/review loop and `krt-release-marshal`; the user-facing approval pause for commits, push, PR creation, reviewer requests, Jira backlinking, and Jira transition belongs inside `krt-release-marshal`. Never treat that pause as merge approval unless an active autonomous ledger and Release Marshal executor make that exact merge mutation eligible.

When a package waits on an open parent PR and the user says "continue", fetch and inspect the integration base before choosing the next review unit. Prefer a stacked PR from the parent review-unit branch only when the base check supports it; record dependency context in state, not PR body.

## Workflow Map

For artifact generation, load `references/workflow-map.md`.

For execution, load `references/execution-flow.md`, then only the phase file it points to.

For state and failure handling, load `references/status-and-failures.md`.
