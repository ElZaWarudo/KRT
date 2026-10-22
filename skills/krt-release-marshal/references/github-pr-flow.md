# GitHub PR Flow

Commands and formats for `krt-release-marshal`. Policy lives in `SKILL.md`.

## Inspect

```bash
git branch --show-current
git status --porcelain=v1 -b
git remote -v
gh repo view --json nameWithOwner,defaultBranchRef
git ls-remote --heads origin develop          # base candidate
git ls-remote --heads origin <branch>         # already published?
gh pr list --head <branch> --state open --json number,title,url
git log --oneline <base>..HEAD
git diff --stat <base>...HEAD
python3 <skill-dir>/scripts/check_pr_scope.py --base origin/<base>...HEAD --fail-on-blocking
```

## Push

- New branch: `git push -u origin <branch>`
- Rewritten history on a published branch: `git push --force-with-lease origin <branch>`

## PR title

Name the shipped capability in sentence case or Conventional Commit style,
following the repo. Add a Jira key only if the repo already does. Avoid vague
titles such as `updates`.

```text
feat: add delegated registry deployment flow
fix: preserve product filters in registry search
```

## PR body

```md
- Adds central regulatory summary publishing with tenant ownership checks.
- Adds regulator metadata query API with scoped pseudonyms and audit records.

https://<jira-host>/browse/PDP-93
```

When one PR covers several review-unit subtasks, list each subtask URL at the
end. Normalize and validate the body file:

```bash
python3 <skill-dir>/scripts/format_pr_body.py --file <draft> > <body>
python3 <skill-dir>/scripts/check_pr_body.py --file <body>
```

## Create, update, comment

```bash
gh pr create [--draft] --base <base> --head <branch> --title "<title>" --body-file <body>
gh pr edit <n> --title "<title>" --body-file <body>
gh pr comment <n> --body-file <comment>
```

Replies to inline review threads belong to `krt-review-herald`.

## Reviewers

```bash
gh pr list --base <base> --state merged --limit 3 --json number,author,reviews
gh pr edit <n> --add-reviewer <login>[,<login>]
```

Prefer the approvers of the most recent merged PRs. Exclude bots, duplicates,
the PR author, and the current `gh` user.

## Merge state

```bash
gh pr view <n> --json number,url,state,isDraft,mergeStateStatus,reviewDecision,reviews,statusCheckRollup,baseRefName,headRefName
gh api repos/<owner>/<repo>/branches/<base>/protection   # required reviews on experimental bases
```

After a parent PR in a stack is squash-merged:

```bash
python3 <skill-dir>/scripts/check_stack_choreography.py \
  --parent-merge-method squash --parent-state merged \
  --parent-branch <parent> --child-branch <child> \
  --child-base <child-base> --final-base <integration-base> \
  --child-rebased-onto-final-base --approvals-refreshed --checks-refreshed
```

Before a stacked PR exists, run the same script with
`--parent-merge-method <merge|rebase|squash|unknown> --refresh-planned` to
check the plan.

## Autonomous mode

`gh pr create`, `gh pr merge`, reviewer requests and pushes are only
templates here. The executor runs them through `scripts/autonomous_mutation.py`
(mutation classes `branch_push`, `branch_force_push`, `pr_create`, `pr_update`,
`reviewer_request`, `pr_merge`, `pr_merge_queue`, `pr_auto_merge`). For merge
validation it uses `scripts/check_merge_eligibility.py`. If live state can't be
validated, the action blocks. See `autonomous-mutation-executor.md`.
