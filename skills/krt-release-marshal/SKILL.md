---
name: krt-release-marshal
description: "Ship the current repository's work for review: atomic commits via krt-gitflow-knight, history cleanup via krt-rebase-smith, Jira Cloud or Server/Data Center linking, then a GitHub pull request with reviewers and bidirectional Jira/PR links. Use when the user asks to create, open, or update a PR (including pushing new or amended commits to a PR branch), ship or publish branch changes for review, or merge an existing PR. Runtime aliases may expose this as krt:release-marshal."
---

# Release Marshal

Take finished work to an open pull request that a human can review, in this
order: commits, rebase, Jira, push and PR, reviewers, Jira backlink and
transition to `En Revisión`. Merging is a separate step the user asks for
later. User instructions override anything here.

Component skills own their parts: `krt-gitflow-knight` for branches and
commits, `krt-rebase-smith` for history, `krt-jira-cloud-scribe` or
`krt-jira-scribe` for Jira. Load them when their phase is needed instead of
redoing their work. Use `gh` for GitHub. `references/github-pr-flow.md` has the
exact commands and the PR body format. Resolve script paths relative to this
skill's directory, which may be the installed copy rather than the target
repo. Load `references/safety.md` before mutating anything.

## The release plan is the approval gate

Inspect first (branch, working tree, remotes, base, existing PR, Jira
readiness, scope), then show one release plan in the user's language and stop
until they accept it. Keep it short and concrete. The user is deciding whether
the release looks right, so the plan should not narrate tooling. Include:

- current and base branch, and the proposed branch name if one is needed;
- proposed commit messages with the files in each;
- Jira: issue to reuse or create, or why it is omitted;
- the exact push command, e.g. `git push -u origin feat/order-export`;
- PR title and body as they will be published, ready or draft;
- reviewers, and what happens in Jira after the PR opens;
- the remote actions this approval covers, and that merge is not included.

After acceptance, do the local, reversible steps without asking again.
Anything that leaves the machine or notifies people needs approval for that
exact action: pushes, PR creation or edits, PR comments, reviewer requests,
Jira writes and transitions. The accepted plan counts only for what it named
explicitly. If the push target or mode changes, or the diff grows materially,
show the new plan and ask again. In PR-only mode, skip commit, rebase and Jira,
but still stop on uncommitted changes and still ask before pushing.

## Conventions

- **Base branch:** the user's choice, else `develop` if it exists on origin,
  else the GitHub default branch. Never open a PR from `main`, `master` or
  `develop`; move the work to a feature branch first.
- **Names:** branches, titles and commits describe the capability
  (`feat/order-csv-export`), not planning artifacts. Work-package numbers,
  review-unit markers and Compound Master IDs stay out of them unless the repo
  convention requires them.
- **Language:** talk to the user in their language. Write GitHub-visible text
  (titles, bodies, reviewer messages) in English unless the user or repo says
  otherwise. Always write PR comments in English. Write Jira summaries and
  descriptions in Spanish.
- **PR body:** one factual English bullet per change, a blank line, then the
  relevant Jira URL. No headings and no verification, test or CI results.
  Leave out stacking, retargeting and reviewer notes, because the body is the
  permanent record of what changed. Upstream agents often draft `## Summary` or
  `## Verification` sections, so rewrite those. Run `scripts/format_pr_body.py`
  then `scripts/check_pr_body.py` on the final body, and re-run both after any
  edit.
- **No AI attribution and no secrets** in commits, PR text or comments.
- **Tests:** don't run tests, linters or formatters unless asked; treat
  upstream results as readiness context. Exception: before pushing a CI fix,
  have evidence that the local equivalent of the failing CI job passed, or show
  the gap and get an explicit override.
- **Force pushes:** only `--force-with-lease`, shown in the plan.
- **Existing PR:** if the branch already has an open PR, update it rather than
  opening a duplicate.

## Scope

Run `scripts/check_pr_scope.py --base <base>...HEAD` before planning. If it
prints `BLOCKING:`, or generated files dominate, or the diff is around 1,000+
human-written lines, the plan must say either "split before PR" or "approve
large PR because <reason>". A PR should be one focused review unit. Keep
related docs in the PR. Never hide them in a stash, worktree or side branch to
make the numbers look better.

## Jira

Jira is optional unless the user or enclosing workflow says it is required.
Pass `jira-provider:cloud|server-datacenter|none` along when known. Otherwise
run `scripts/resolve_jira_provider.py --root <repo>` and never guess a
provider. If it doesn't resolve to exactly one ready provider, either note in
the plan that Jira is omitted (when optional) or ask whether to continue
without it (when required). Keep the resolved `jira_provider` in every
handoff.

Reuse open or in-progress issues before proposing new ones. Use a standalone
task for a single unit; create a parent with subtasks only when there are two
or more children. After the PR is ready, add the PR link to the issue and move
it to `En Revisión` if the plan included that. When a PR covers several
review-unit subtasks, do this for each one. Put only the immediately relevant
issue in commits and the PR body, never both parent and child.

## Reviewers

Use the reviewers the user named. Otherwise infer them from approvals on
recent merged PRs to the same base, excluding bots and the author. Request
them only if the plan said so, or after asking.

## Merging

Merge only when the user asks. First inspect the PR (`gh pr view <n> --json
state,isDraft,reviewDecision,reviews,statusCheckRollup,mergeStateStatus,baseRefName`)
and report what you find. A merge needs all of the following:

- a human approval visible on GitHub, from someone other than the author or
  agent. Internal reviews and CI do not count. The only exception is a base
  under `experimental/`, `experiment/`, `spike/`, `sandbox/`, `prototype/` or
  `playground/` whose protection requires no reviews;
- required checks passing;
- no outstanding change requests;
- the user's go-ahead given after seeing that state, for that PR. A bare "ok"
  or "dale" counts only as an answer to your merge question. Approval of the
  release plan never covers a merge.

If something is missing, say what and stop. Don't offer admin merges, local
merges, or turning off protection.

For stacked PRs: when a parent merges by squash, rebase or retarget the child
onto the final base before continuing. Treat its approvals and checks as stale
until they refresh, and don't delete the parent branch before then.
`scripts/check_stack_choreography.py` verifies this.

## Autonomous mode

Only an `autonomous-ledger:<path>` handoff (issued by Compound Master or
Swarm Seneschal) permits unattended remote actions. The ledger format is
`references/autonomy-ledger-schema.md`, validated by
`scripts/check_autonomy_ledger.py`. All such actions go through
`scripts/autonomous_mutation.py`; see
`references/autonomous-mutation-executor.md` and
`references/autonomous-validator-registry.md`. Without a valid ledger,
everything above applies.

## Closeout

Report the PR number and URL, base and head, draft or ready, the Jira link, and
any action you deferred or that still needs the user.
