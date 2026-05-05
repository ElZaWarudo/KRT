---
name: rebase-smith
description: >
  Safe workflow to keep history clean by rebasing a child branch onto develop
  before merging. Resolve which branch will be rebased, verify whether develop
  exists, support rebase --onto for branches derived from another
  feature branch, and if develop does not exist, ask for an alternative base
  branch first.
---

# Rebase Smith

## Overview

Use this skill when the user wants to merge a derived branch without dragging
history from another branch that was already merged (typical case: `a` branched
from `develop`, `b` branched from `a`, and `a` is already merged).

Goal: keep the target branch clean by replaying only its own commits on top of
the correct base branch.

## Mandatory rules

- Never guess the branch to rebase. Use the current branch or enclosing accepted workflow when unambiguous; otherwise ask.
- Never assume `develop` exists: verify both local and remote.
- If `develop` does not exist, ask which base branch to use (`main`, `master`, or another).
- Refuse to rebase protected branches directly: `main`, `master`, `develop`.
- Require a clean working tree before rebasing. If there are staged or unstaged changes, stop and ask whether to commit, stash, or cancel. Do not auto-stash unless explicitly approved.
- Determine whether the target branch was branched from another feature branch whose commits should be dropped from the rewritten history. Ask only when this cannot be inferred.
- Use `rebase --onto` when the target contains parent-branch commits that should not be replayed.
- If the branch was already pushed, use `--force-with-lease` (never plain `--force`).
- Show the exact push command and ask for confirmation before any force-with-lease push.
- Avoid destructive commands (`reset --hard`, `push --force`) unless explicitly requested.
- Do not resolve conflicts silently. Present conflicted files and ask for direction unless the fix is obvious and the user asked for autonomous resolution.
- Use the host runtime's command wrapper only when the current repo requires one. The command examples below use plain `git` for portability.
- Use a single rebase-plan acceptance gate when acting standalone. If running inside an already accepted `release-marshal` workflow, and target/base/upstream are unambiguous, proceed with local rebase without a second approval gate. Still ask before `--force-with-lease`, conflict resolution choices, stash/drop operations, or any remote mutation.

## Workflow

### 1) Preflight and branch discovery

Run:

```bash
git fetch origin --prune
git branch --show-current
git status --porcelain=v1 -b
git branch --list
git branch -r
```

Check whether `develop` exists locally or remotely:

```bash
git show-ref --verify --quiet refs/heads/develop || git show-ref --verify --quiet refs/remotes/origin/develop
```

If the working tree has staged or unstaged changes, stop before rebasing. Ask the user whether to commit, stash, or cancel.

### 2) Target branch resolution

If the target branch is obvious from the current branch or an enclosing accepted workflow, use it. Otherwise ask directly:

- "Which branch do you want to rebase onto `develop`?"

Do not continue until the branch is known.

If the confirmed target is `main`, `master`, or `develop`, refuse to rebase it directly and ask for a non-protected feature branch.

### 3) Resolve base branch

If `develop` exists:

- Base = `origin/develop` (preferred) or local `develop` if remote is not available.

If `develop` does not exist:

- Ask: "I cannot find `develop`. Which base branch should we use for the rebase?"
- Use the branch provided by the user.

### 4) Decide simple rebase vs rebase --onto

Determine whether `<target>` was branched from another feature branch whose commits
are already merged into `<base>` and should be excluded. If this is not clear from branch history or an enclosing accepted workflow, ask.

If no parent feature branch needs to be dropped:

```bash
git log --oneline <base>..<target>
```

Plan a simple rebase:

```bash
git rebase <base>
```

If a parent feature branch or upstream commit should be dropped, resolve
`<upstream-to-drop>`. This is usually the parent feature branch name,
or the commit where `<target>` started.

Inspect the target-owned commits before planning:

```bash
git log --oneline <upstream-to-drop>..<target>
```

Plan a rebase --onto:

```bash
git rebase --onto <base> <upstream-to-drop> <target>
```

Use `--fork-point` only when normal merge-base detection would replay commits
that are not owned by the target branch. Do not use it by default.

Present the selected rebase command as the rebase plan. Ask for approval when this skill is acting standalone. If an enclosing `release-marshal` plan already accepted this exact rebase shape, proceed without a second approval gate.

### 5) Safe rebase

With `<target>` and `<base>` confirmed:

```bash
git switch <target>
```

Then run the planned command:

- Simple rebase: `git rebase <base>`
- Rebase onto: `git rebase --onto <base> <upstream-to-drop> <target>`

If conflicts appear:

```bash
git status
# resolve files
git add <resolved-files>
git rebase --continue
```

If the user decides to cancel:

```bash
git rebase --abort
```

### 6) Sync rewritten branch to remote

Check whether `<target>` exists on remote:

```bash
git ls-remote --heads origin <target>
```

If `<target>` already exists on remote:

```bash
git push --force-with-lease origin <target>
```

Before running this command, show it to the user and ask for explicit
confirmation because it rewrites the remote branch history.

If it does not exist yet:

```bash
git push -u origin <target>
```

### 7) Closeout and merge recommendation

Explain to the user that after rebasing, the PR from `<target>` to the selected
base should show only commits owned by `<target>`.

Recommend merge strategy based on preference:

- `Squash and merge`: one clean commit in final history.
- `Rebase and merge`: preserves branch commits.
- Avoid `Merge commit` if linear history is preferred.

## Short response template

```text
Plan:
1) Fetch origin and confirm the working tree is clean.
2) Resolve the target branch to rebase and refuse protected branches.
3) Verify whether develop exists; otherwise ask for an alternative base branch.
4) Decide whether this is a simple rebase or rebase --onto.
5) Present the exact rebase command as the plan; ask for approval only when standalone.
6) Resolve conflicts with you if they appear.
7) Ask before pushing with --force-with-lease.
```
