---
name: krt-release-marshal
description: "Orchestrate the full delivery flow for the current project repository: direct krt-gitflow-knight for clean commits, krt-rebase-smith for clean branch history, krt-jira-scribe for Jira Server/Data Center issue work, then open a GitHub pull request with a factual body and Jira link. Use when the user asks to create/open a PR, prepare a pull request, ship current work, publish branch changes for review, or run the full gitflow + rebase + Jira + PR workflow. Runtime aliases may expose this as krt:release-marshal."
---

# Release Marshal

Orchestrate the normal KRT delivery flow: commit -> rebase -> Jira -> push/PR -> reviewers -> Jira review transition. Do not introduce a separate "commit-task-PR" mode.

The marshal directs component skills instead of duplicating them:

- `krt-gitflow-knight` (`krt:gitflow-knight`) owns branch hygiene, staging, and commit planning.
- `krt-rebase-smith` (`krt:rebase-smith`) owns clean branch history and safe rebase decisions.
- `krt-jira-scribe` (`krt:jira-scribe`) owns Jira issue/subtask lookup, creation proposals, sprint handling, and transitions.
- `gh` owns GitHub remote state, push/PR operations, and reviewer requests after release-plan confirmation.

Load `references/github-pr-flow.md` for exact `git`/`gh` commands, PR body details, base resolution, remote branch checks, and reviewer lookup.

## Mandatory Rules

- Use the host runtime's command wrapper only when the current repo requires one.
- Use `gh` for GitHub PR operations.
- Never create a PR from protected branches: `main`, `master`, or `develop`.
- Prefer `develop` as PR base when it exists; otherwise use the repository default branch unless the user or enclosing workflow provided a base.
- Never include LLM attribution in PR title/body or commit messages.
- Never include Compound Master planning IDs or package numbers in PR titles, PR body bullets, branch names, or commit messages unless the user or repo convention explicitly requires them.
- Never put both parent and child Jira references in commit messages. If repo convention requires a Jira reference or link in a commit, use only the immediately relevant issue: usually the subtask/work-package issue; use the parent only when no child issue exists.
- Never include secrets, tokens, credentials, or internal environment dumps in the PR body.
- Treat verification results from upstream workflows as readiness evidence only. Do not include test commands, test output, or verification summaries in the PR body unless the user, repo template, or project convention explicitly requires it.
- Do not run tests, linters, or formatters unless the user explicitly asks; use verification results supplied by the user or upstream workflow.
- Do not ask for Jira credentials. If required Jira env vars are missing, continue without Jira only if the user approves.
- Use `--force-with-lease`, never plain `--force`, when a rewritten branch must be pushed.
- Prefer concise PR bodies: change bullets first, Jira URL last, no section headings unless the repo template requires them.
- Prefer reviewable logical commits over package-sized commits when the pending work has clear boundaries. A work package may be one PR with several commits.
- Use one or two commits only when the change truly has one or two coherent concerns. Do not compress broad feature work into "implementation" plus "docs" when the diff spans persistence, services, API contracts, generated surfaces, tests, and configuration.

## Approval Policy

The workflow has one initial plan acceptance gate. After the user accepts that plan, proceed through local/reversible phases without asking again: branch creation/switching, staging, local commits, local rebase on unpushed branches, reading repo/GitHub/Jira state, and preparing PR text.

Ask before destructive, irreversible, external, or notification-causing work unless that exact action was explicitly included in the accepted plan:

- Jira issue/subtask creation or updates.
- Jira transition.
- Push or `--force-with-lease` push.
- PR creation or update.
- Reviewer requests.
- Remote branch rewrites.

One explicit release-plan approval may cover reviewer requests and automatic post-PR Jira transition to `En Revisión` if the plan names the behavior and fallback. For Jira transition, the plan must name the issue and target status. For reviewer requests, the plan may name explicit reviewers or authorize automatic lookup and request of a clear inferred human reviewer.

## Inputs

Use context already provided by the user or previous skills:

- Desired workflow scope: full flow or PR-only.
- Jira parent issue key, subtask key, or issue URL.
- Target/base branch.
- PR title/body preference.
- Draft vs ready preference.
- Explicit reviewers, or "sin reviewers" / "no reviewers".
- Verification results as internal readiness context only.
- Suggested commit grouping from an enclosing workflow, when provided.

If the user asks simply to create a PR and there are uncommitted changes or no Jira context, propose the full flow and ask before creating Jira artifacts.

## Workflow

### 1. Preflight And Phase Plan

Load `references/github-pr-flow.md` for commands. Inspect branch, working tree, remotes, and repository default branch.

Build and show a phase plan:

- Commit phase: needed if there are staged/unstaged changes or branch hygiene issues.
- Rebase phase: recommended before PR unless the user explicitly skips.
- Jira phase: needed if the user wants a Jira link or the project requires it.
- PR phase: always included.
- Reviewer phase: after PR creation, request explicit reviewers or infer one clear reviewer when the accepted plan includes automatic reviewer handling; otherwise ask or skip according to user preference.
- Jira transition phase: after PR creation, move the associated Jira task to `En Revisión` when Jira context exists and the accepted plan included that transition; otherwise ask.

When commit work is needed, include proposed branch and commit grouping when practical. If grouping needs more inspection, make that the next local step inside the same acceptance gate rather than adding another branch/commit confirmation.

Commit grouping guidance for the phase plan:

- Inspect the changed file list before proposing grouping. If the enclosing workflow supplied grouping, validate it against the actual changed surfaces and refine it when it is too coarse.
- Prefer three to six logical commits for broad packages with natural seams.
- Natural commit boundaries include data/model/schema changes, domain/service or integration behavior, API/controller/generated contract surfaces, configuration/deployment surfaces, focused tests/fixtures, and docs/orchestration artifacts.
- For multi-surface feature work, explicitly consider separate commits for persistence, service/integration behavior, API/generated contract surfaces, config/deployment wiring, focused tests, and docs.
- Avoid broad catch-all messages such as `feat(epcis): add bridge foundation` when the files naturally split into narrower review units like model state, bridge service, API endpoint, tests, and docs.
- Keep tests with the behavior commit when splitting them out would leave an intermediate commit obviously broken or hard to review. Use a separate `test(...)` commit only when the test change is a coherent review unit and earlier commits remain sensible.
- Keep docs/orchestration state in a separate `docs(...)` commit when it does not need to be bundled with runtime behavior.
- If more than six commits seem necessary, call out that the package may be too broad or that some commits should be combined.

Ask the user to accept the phase plan before changing local state.

### 2. Commit Phase

If there are staged/unstaged changes or the current branch is protected/off-convention, load and follow `krt-gitflow-knight`. Pass along any suggested commit grouping from the accepted release plan. Let it use the accepted release plan or commit plan as the single local gate. Return here after commits complete.

### 3. Rebase Phase

Unless the user explicitly skips history cleanup, load and follow `krt-rebase-smith`. Resolve target/base from current context when unambiguous. Use `rebase --onto` when the branch was derived from another feature branch whose commits should be dropped. Ask before any `--force-with-lease`.

### 4. Jira Phase

If Jira context was provided, keep it.

If Jira context is missing and Jira should be included, load and follow `krt-jira-scribe`. Use Jira Server/Data Center only. For PRs that look like a work package or one item in a larger delivery sequence, prefer finding or creating a parent task plus a subtask for the PR. Create a standalone task only when the work is clearly standalone or the user requests it. Create or reuse Jira issues only after confirmation. Capture the immediately relevant Jira URL for the PR body, usually the subtask for this PR.

If required Jira env vars are missing, stop the Jira phase and ask whether to continue PR creation without Jira links.

### 5. PR Preparation

Load `references/github-pr-flow.md` for base selection, remote branch state, PR content gathering, and body construction.

Before push or PR creation/update, show:

- Current branch.
- Base branch.
- Push command, including `--force-with-lease` if required.
- PR title.
- PR body.
- Draft or ready status.
- Jira links included.
- Jira transition plan: issue key, current status if known, target `En Revisión`, and whether it will run automatically after PR creation.
- Reviewer plan: explicit reviewers, automatic inferred reviewer lookup/request, or skipped.

Ask for approval before the next remote mutation.

### 6. Push And Create PR

After approval, push if needed and create the PR with `gh`. Use a temporary body file rather than passing long body text inline.

If an open PR already exists for the branch, stop and ask whether to view/update it instead of creating a duplicate.

### 7. Reviewer Phase

If the user explicitly requested no reviewers, skip.

If the accepted release plan already included the exact reviewer request behavior, do not ask again.

If the user provided reviewers and the accepted plan did not already approve reviewer requests, show them and ask before adding them because this notifies people.

If no reviewers were provided, infer candidates from recent merged PR approvals against the same base. Exclude bots, duplicates, and the author/current GitHub user. If no clear reviewers remain, say so and skip assignment. If the accepted plan included automatic inferred reviewer lookup/request, add the single clear reviewer without asking a second time; otherwise ask before adding inferred reviewers.

### 8. Closeout And Jira Review Transition

After PR creation, return PR number, URL, base branch, head branch, Jira link if included, and draft/ready state.

If Jira context was included and the approved plan included review transition, use `krt-jira-scribe` to inspect real transitions and move the associated Jira issue to `En Revisión` without asking again. If `En Revisión` is unavailable, the issue key is ambiguous, or the approved plan did not include automatic transition, ask before transitioning.

## PR-Only Mode

If the user explicitly asks for PR-only mode:

- Do not run commit, rebase, or Jira phases.
- Still refuse protected branches.
- Still stop on uncommitted changes unless the user confirms they should be ignored.
- Still ask before push and PR creation.
