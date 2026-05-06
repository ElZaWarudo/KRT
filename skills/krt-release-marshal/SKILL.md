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
- `gh` owns GitHub remote state, push/PR operations, and reviewer requests after confirmation.

Load `references/github-pr-flow.md` for exact `git`/`gh` commands, PR body details, base resolution, remote branch checks, and reviewer lookup.

## Mandatory Rules

- Use the host runtime's command wrapper only when the current repo requires one.
- Use `gh` for GitHub PR operations.
- Never create a PR from protected branches: `main`, `master`, or `develop`.
- Prefer `develop` as PR base when it exists; otherwise use the repository default branch unless the user or enclosing workflow provided a base.
- Never include LLM attribution in PR title/body or commit messages.
- Never include secrets, tokens, credentials, or internal environment dumps in the PR body.
- Do not run tests, linters, or formatters unless the user explicitly asks; use verification results supplied by the user or upstream workflow.
- Do not ask for Jira credentials. If required Jira env vars are missing, continue without Jira only if the user approves.
- Use `--force-with-lease`, never plain `--force`, when a rewritten branch must be pushed.
- Prefer concise PR bodies: change bullets first, Jira URL last, no section headings unless the repo template requires them.

## Approval Policy

The workflow has one initial plan acceptance gate. After the user accepts that plan, proceed through local/reversible phases without asking again: branch creation/switching, staging, local commits, local rebase on unpushed branches, reading repo/GitHub/Jira state, and preparing PR text.

Ask before destructive, irreversible, external, or notification-causing work unless that exact action was explicitly included in the accepted plan:

- Jira issue/subtask creation or updates.
- Jira transition.
- Push or `--force-with-lease` push.
- PR creation or update.
- Reviewer requests.
- Remote branch rewrites.

One explicit release-plan approval may cover automatic post-PR Jira transition to `En Revisión` if the plan names the issue, target status, and fallback behavior.

## Inputs

Use context already provided by the user or previous skills:

- Desired workflow scope: full flow or PR-only.
- Jira parent issue key, subtask key, or issue URL.
- Target/base branch.
- PR title/body preference.
- Draft vs ready preference.
- Explicit reviewers, or "sin reviewers" / "no reviewers".
- Verification results.

If the user asks simply to create a PR and there are uncommitted changes or no Jira context, propose the full flow and ask before creating Jira artifacts.

## Workflow

### 1. Preflight And Phase Plan

Load `references/github-pr-flow.md` for commands. Inspect branch, working tree, remotes, and repository default branch.

Build and show a phase plan:

- Commit phase: needed if there are staged/unstaged changes or branch hygiene issues.
- Rebase phase: recommended before PR unless the user explicitly skips.
- Jira phase: needed if the user wants a Jira link or the project requires it.
- PR phase: always included.
- Reviewer phase: propose reviewers after PR creation unless skipped.
- Jira transition phase: after PR creation, move the associated Jira task to `En Revisión` when Jira context exists and the accepted plan included that transition; otherwise ask.

When commit work is needed, include proposed branch and commit grouping when practical. If grouping needs more inspection, make that the next local step inside the same acceptance gate rather than adding another branch/commit confirmation.

Ask the user to accept the phase plan before changing local state.

### 2. Commit Phase

If there are staged/unstaged changes or the current branch is protected/off-convention, load and follow `krt-gitflow-knight`. Let it use the accepted release plan or commit plan as the single local gate. Return here after commits complete.

### 3. Rebase Phase

Unless the user explicitly skips history cleanup, load and follow `krt-rebase-smith`. Resolve target/base from current context when unambiguous. Use `rebase --onto` when the branch was derived from another feature branch whose commits should be dropped. Ask before any `--force-with-lease`.

### 4. Jira Phase

If Jira context was provided, keep it.

If Jira context is missing and Jira should be included, load and follow `krt-jira-scribe`. Use Jira Server/Data Center only. Create or reuse a parent issue and subtask only after confirmation. Capture the final Jira URL for the PR body.

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
- Reviewer plan: explicit reviewers, inferred reviewers to propose after PR creation, or skipped.

Ask for approval before the next remote mutation.

### 6. Push And Create PR

After approval, push if needed and create the PR with `gh`. Use a temporary body file rather than passing long body text inline.

If an open PR already exists for the branch, stop and ask whether to view/update it instead of creating a duplicate.

### 7. Reviewer Phase

If the user explicitly requested no reviewers, skip.

If the user provided reviewers, show them and ask before adding them because this notifies people.

If no reviewers were provided, infer candidates from recent merged PR approvals against the same base. Exclude bots, duplicates, and the author/current GitHub user. If no clear reviewers remain, say so and skip assignment. Ask before adding inferred reviewers.

### 8. Closeout And Jira Review Transition

After PR creation, return PR number, URL, base branch, head branch, Jira link if included, and draft/ready state.

If Jira context was included and the approved plan included review transition, use `krt-jira-scribe` to inspect real transitions and move the associated Jira issue to `En Revisión` without asking again. If `En Revisión` is unavailable, the issue key is ambiguous, or the approved plan did not include automatic transition, ask before transitioning.

## PR-Only Mode

If the user explicitly asks for PR-only mode:

- Do not run commit, rebase, or Jira phases.
- Still refuse protected branches.
- Still stop on uncommitted changes unless the user confirms they should be ignored.
- Still ask before push and PR creation.
