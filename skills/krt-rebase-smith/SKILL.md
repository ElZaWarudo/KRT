---
name: krt-rebase-smith
description: >
  Rebase a feature branch onto its correct base so its PR shows only its own
  commits: onto develop when it exists, otherwise a base the user picks, using
  rebase --onto when the branch was cut from another feature branch (especially
  one that was squash-merged), then publish with an approved push or
  --force-with-lease. Use when the user asks to rebase, update a branch with
  develop, clean up branch history, drop a merged parent branch's commits, or
  fix a PR that shows someone else's commits. Opening or merging the PR belongs
  to krt-release-marshal. Runtime aliases may expose this as krt:rebase-smith.
---

# Rebase Smith

Replay only the commits the target branch owns on top of the right base, so
the PR diff is exactly that branch's work. Rebasing rewrites history, so be
explicit about which branch, which base, and how it reaches the remote. Load
`references/safety.md` before starting.

## Approval

Standalone, inspect first and show one rebase plan: target branch, base,
upstream to drop if any, the exact rebase command, the commits that will be
replayed, and the exact push command. Rebase after the user accepts it.

Inside an accepted `krt-release-marshal` plan, or when the user's message
already approves the rebase, do the local rebase without a second gate as long
as target, base and upstream are unambiguous.

Every push needs approval of the **exact push command**: first publication
(`git push -u origin <target>`) and rewritten history
(`git push --force-with-lease origin <target>`). An earlier approval covers
the push only if it named the same command, remote, branch and mode as what is
needed now. The usual mismatch: a plan approved `git push origin <target>` or
`git push -u origin <target>`, but the branch already exists on origin, so the
rebased history now needs `--force-with-lease`. Show the new command and ask
instead of pushing.

## Preconditions

- **Target:** the current branch, or the one named by the user or the enclosing
  plan. If that is unclear, ask. Never rebase `main`, `master` or `develop`
  themselves.
- **Base:** `origin/develop` if `develop` exists locally or on origin (fetch
  first so you rebase onto the current tip). If it doesn't exist, ask which
  base to use rather than silently picking `main`.
- **Clean tree:** with staged or unstaged changes, stop before rebasing and ask
  whether to commit, stash or cancel. Don't stash, commit or discard on your
  own, even if the user asked you to rebase and push in one breath.

## Choosing the rebase

Check what `git log --oneline <base>..<target>` would replay. If those are all
the target's own commits, `git rebase <base>` is enough.

If the target was branched from another feature branch, the parent's commits
show up in that range. When the parent was merged normally, git skips them on
its own. When it was **squash- or rebase-merged**, the original parent commits
are not in the base, so a plain rebase replays them, usually with conflicts,
and drags them into the PR. Drop them with:

```bash
git rebase --onto <base> <upstream-to-drop> <target>
```

`<upstream-to-drop>` is the parent branch tip, or the commit where the target's
own work starts. Confirm with `git log --oneline <upstream-to-drop>..<target>`
that only the target's commits remain. Use `--fork-point` only when the normal
merge base would replay commits the target doesn't own.

## Conflicts

Show the conflicted files and ask for direction, unless the resolution is
obvious and the user asked you to resolve conflicts yourself. `git rebase
--abort` returns to the original state if the user wants to stop.

## Publishing

Check `git ls-remote --heads origin <target>`. If the branch exists remotely,
the push is `git push --force-with-lease origin <target>`; never a plain
`--force` or `-f`. If it doesn't, the push is `git push -u origin <target>`.
Apply the approval rule above to whichever command it is.

## Closeout

Report the new base, the replayed commits and whether the branch was pushed.
Don't merge the branch or the PR. If asked how to merge, squash-and-merge or
rebase-and-merge keeps history linear; the merge itself needs the user's
explicit approval and is `krt-release-marshal`'s job.
