---
name: krt:release-marshal
description: "Orchestrate the full delivery flow for the current project repository: direct krt:gitflow-knight for clean commits, krt:rebase-smith for clean branch history, krt:jira-scribe for Jira Server/Data Center issue work, then open a GitHub pull request with a factual body and Jira link. Use when the user asks to create/open a PR, prepare a pull request, ship current work, publish branch changes for review, or run the full gitflow + rebase + Jira + PR workflow."
---

# Release Marshal

## Overview

Orchestrate the full delivery flow for the current project. Calling this skill is the normal commit → Jira → PR workflow; do not introduce a separate "commit-task-PR" mode.

1. Prepare clean gitflow commits.
2. Rebase safely onto `develop` or the selected base branch.
3. Create or reuse Jira Server/Data Center issue and subtask.
4. Create a GitHub pull request with a factual body and Jira link.
5. Offer to move the associated Jira task to review after the PR is created.

The marshal directs specialized skills instead of duplicating their detailed workflows:

- `krt:gitflow-knight` owns branch hygiene, staging, and commit planning.
- `krt:rebase-smith` owns clean branch history and safe rebase decisions.
- `krt:jira-scribe` owns Jira issue/subtask lookup, creation proposals, sprint handling, and transitions.
- `gh` owns GitHub remote state, push/PR operations, and reviewer requests after confirmation.

## Mandatory rules

- Use the host runtime's command wrapper only when the current repo requires one. The command examples below use plain `git` and `gh` for portability.
- Use `gh` for GitHub PR operations.
- Never create a PR from protected branches: `main`, `master`, `develop`.
- Never assume the base branch. Prefer `develop` if it exists, otherwise use the repository default branch.
- Only require user approval for destructive/irreversible actions or mutating/notification-causing external-system actions: push, force-with-lease push, PR creation/update, reviewer requests, Jira issue creation/update/transition, or remote branch rewrites.
- Never include LLM attribution in the PR title or body.
- Never include secrets, tokens, credentials, or internal environment dumps in the PR body.
- Do not run tests, linters, or formatters unless the user explicitly asks.
- Do not ask for Jira credentials. If required Jira env vars are missing, continue without Jira only if the user approves.
- Use `--force-with-lease`, never plain `--force`, if a rewritten branch must be pushed.
- Prefer concise PR bodies by default: change bullets first, Jira URL last, no section headings unless the user asks for them or the repo requires a template.
- Do not ask approval for local, reversible work when intent is clear: branch creation/switching, staging, local commits, local rebases on unpushed branches, reading repo/GitHub/Jira state, and preparing PR text. Ask only when required information is missing or the action crosses the approval policy above.
- The workflow should have one initial plan acceptance gate. After the user accepts that plan, proceed through local/reversible phases without asking again. Add extra approval gates only for destructive/irreversible work or external mutations/notifications.

## Component skills

Use these skills as sub-workflows when their conditions apply:

- `krt:gitflow-knight`: when there are staged or unstaged changes, or the branch is protected/off-convention.
- `krt:rebase-smith`: before PR creation, to clean branch history onto `develop` or another confirmed base.
- `krt:jira-scribe`: when the PR should reference a Jira parent issue or subtask.

Do not copy their full procedures here. Load and follow the component skill when that phase is needed.

## Inputs

Use any context already provided by the user or previous skills:

- Desired workflow scope: full flow or PR-only
- Jira parent issue key
- Jira subtask key
- Jira issue URL
- Target/base branch
- PR title preference
- Draft vs ready PR preference
- Explicit reviewers to request, or "sin reviewers" / "no reviewers" to skip reviewer suggestions
- Verification results supplied by the user

If the user asks simply to "create a PR" and there are uncommitted changes or no Jira context, propose the full flow but ask before creating Jira artifacts.

## Workflow

### 1) Preflight and workflow plan

Run:

```bash
git branch --show-current
git status --porcelain=v1 -b
git remote -v
gh repo view --json nameWithOwner,defaultBranchRef
```

Build and show a plan with the phases that apply:

- Commit phase: needed if there are staged/unstaged changes or branch hygiene issues.
- Rebase phase: recommended before PR unless user explicitly skips.
- Jira phase: needed if the user wants a Jira link or the project requires it.
- PR phase: always included.
- Reviewer phase: propose reviewers after PR creation unless skipped.
- Jira transition phase: offer after PR creation when Jira context exists.

When commit work is needed, include the proposed branch and commit grouping in this plan whenever practical. If the grouping requires more inspection, say that the next local step is to produce the commit plan, and treat that commit plan as the same acceptance gate rather than adding separate branch/commit confirmations.

Ask the user to accept the phase plan before changing local state. This is the main workflow gate. Once accepted, do not ask again for local/reversible actions such as branch creation, staging, local commits, or local rebase. Still ask before later external mutations such as Jira creation, push, PR creation, reviewer requests, or Jira transitions.

### 2) Commit phase

If there are staged or unstaged changes, or the current branch is protected/off-convention:

- Load and follow `krt:gitflow-knight`.
- Let `krt:gitflow-knight` use the accepted workflow plan or the commit plan as the single local acceptance gate. Do not add separate branch-name confirmations when the branch name is clear.
- Return to this workflow after commits are complete.

If there are no changes to commit, continue.

### 3) Rebase phase

Unless the user explicitly skips history cleanup:

- Load and follow `krt:rebase-smith`.
- Resolve target branch and base branch from current context when unambiguous.
- Use `rebase --onto` when the branch was derived from another feature branch whose commits should be dropped.
- If the current branch was just created from another feature branch, prefer a clean history plan that replays only branch-owned commits onto `origin/develop`, for example `git rebase --onto origin/develop <parent-feature-branch> <current-branch>`.
- If the remote branch needs rewriting, require explicit approval before `--force-with-lease`.

Return to this workflow after rebase is complete or explicitly skipped.

### 4) Jira phase

If the user provided Jira context, keep it.

If Jira context is missing and Jira should be included:

- Load and follow `krt:jira-scribe`.
- Use Jira Server/Data Center only.
- Create or reuse a parent issue and subtask only after user confirmation.
- Capture the final Jira issue URL for the PR body. The PR body does not need to label whether the issue is a parent or subtask unless the user asks.

If required Jira environment variables are missing, stop the Jira phase and ask whether to continue PR creation without Jira links.

### 5) Resolve PR base branch

Determine candidate base branch:

```bash
git show-ref --verify --quiet refs/remotes/origin/develop
gh repo view --json defaultBranchRef
```

Selection rule:

- Use user-provided base if present.
- Else use `develop` if `origin/develop` exists.
- Else use repository default branch from GitHub.

Show the selected base branch in the PR plan.

### 6) Check remote branch state

Check whether current branch exists on origin:

```bash
git ls-remote --heads origin <current-branch>
```

If it does not exist, plan:

```bash
git push -u origin <current-branch>
```

If it exists, inspect whether the branch appears ahead or behind:

```bash
git status --porcelain=v1 -b
```

If a normal push is needed, show the exact push command and ask for approval before running it because it mutates a remote system.

If history was rewritten during the rebase phase and the remote branch exists, show the exact `git push --force-with-lease origin <current-branch>` command and ask for explicit approval.

### 7) Gather PR content

Collect concise context:

```bash
git log --oneline <base>..HEAD
git diff --name-status <base>...HEAD
git diff --stat <base>...HEAD
```

Check whether an open PR already exists:

```bash
gh pr list --head <current-branch> --json number,title,url,state
```

If an open PR already exists for the branch, stop and ask whether to view/update it instead of creating a duplicate.

### 8) Build PR title

Prefer a concise title derived from the branch name and commits.

Rules:

- Use sentence case or Conventional Commit style depending on repo convention.
- Keep it specific.
- Do not include Jira key in the title unless the project convention already does.
- Avoid vague titles like `updates`, `fix stuff`, or `changes`.

Examples:

```text
feat: add delegated registry deployment flow
fix: preserve product filters in registry search
docs: clarify local Jira workflow setup
```

### 9) Build PR body

Use this concise default template:

```md
- <change>
- <change>

<JIRA_URL>
```

Rules:

- Put changes first and the Jira URL last.
- Do not add section headings by default.
- Do not distinguish parent vs subtask in the body by default.
- If Jira context is missing, omit the Jira URL.
- Include verification only if the user asks, the repo requires it, or the PR template requires it.
- Keep the body factual. Do not oversell.

### 10) Final approval gate

Before pushing or creating/updating the PR, show:

- Current branch
- Base branch
- Push command, if needed, including `--force-with-lease` if required after rebase
- PR title
- PR body
- Draft or ready status
- Jira links included
- Reviewer plan: explicit reviewers, inferred reviewers to propose after PR creation, or skipped

Ask the user to approve.

Do not continue until approved because the next actions mutate external systems and may notify people.

### 11) Push and create PR

If push is approved and needed:

```bash
git push -u origin <current-branch>
```

Write the approved PR body to a temporary file outside the repo, for example:

```bash
mktemp
```

Create ready PR:

```bash
gh pr create --base <base> --head <current-branch> --title "<title>" --body-file <tmp-body-file>
```

Create draft PR if requested:

```bash
gh pr create --draft --base <base> --head <current-branch> --title "<title>" --body-file <tmp-body-file>
```

Use a temporary body file rather than passing a long body inline.

### 12) Reviewer phase

If the user explicitly requested no reviewers, skip this phase.

If the user provided explicit reviewers:

1. Show the exact reviewers and ask for confirmation before adding them.
2. Add them after the PR exists:

```bash
gh pr edit <number> --add-reviewer user-a,user-b
```

If the user did not provide reviewers, propose reviewers from recent merged PRs against the same base:

1. Query merged PRs, newest first:

```bash
gh pr list --base <base> --state merged --limit 3 --json number,title,author,reviews
```

2. Prefer users who approved the most recent merged PR.
3. If the latest merged PR has no useful approvals, inspect up to the latest 3 merged PRs and choose the most frequent human approvers.
4. Exclude bots, duplicate users, and the author/current GitHub user when known.
5. If no clear reviewers remain, say so and skip reviewer assignment.
6. If reviewers are found, show them and ask for confirmation before adding them with `gh pr edit <number> --add-reviewer ...`.

Never add reviewers automatically without confirmation; this can notify people.

### 13) Closeout

After creation, show:

```bash
gh pr view --json number,title,url,state,baseRefName,headRefName
```

Return:

- PR number
- PR URL
- Base branch
- Head branch
- Jira link if included
- Whether it is draft or ready

After returning the PR, if Jira context was included, ask whether to move the associated Jira issue to review. Use `krt:jira-scribe` to inspect real transitions and execute only after confirmation.

## PR-only mode

If the user explicitly asks for PR-only mode:

- Do not run commit, rebase, or Jira phases.
- Still refuse protected branches.
- Still stop on uncommitted changes unless the user confirms they should be ignored.
- Still ask before push and PR creation.
