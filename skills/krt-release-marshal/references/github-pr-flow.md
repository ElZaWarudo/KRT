# GitHub PR Flow

Use this reference when `krt-release-marshal` needs exact `git`/`gh` commands or PR content details.

## Preflight

Inspect local and remote state:

```bash
git branch --show-current
git status --porcelain=v1 -b
git remote -v
gh repo view --json nameWithOwner,defaultBranchRef
```

## Resolve Base Branch

Check for `develop` and the GitHub default branch:

```bash
git show-ref --verify --quiet refs/remotes/origin/develop
gh repo view --json defaultBranchRef
```

Selection rule:

- Use user-provided base if present.
- Else use `develop` if `origin/develop` exists.
- Else use repository default branch from GitHub.

Show the selected base in the PR plan.

## Check Remote Branch State

Check whether current branch exists on origin:

```bash
git ls-remote --heads origin <current-branch>
```

If it does not exist, plan:

```bash
git push -u origin <current-branch>
```

If it exists, inspect ahead/behind:

```bash
git status --porcelain=v1 -b
```

If history was rewritten, show and require explicit approval for:

```bash
git push --force-with-lease origin <current-branch>
```

## Gather PR Content

Collect concise context:

```bash
git log --oneline <base>..HEAD
git diff --name-status <base>...HEAD
git diff --stat <base>...HEAD
```

Check for existing PR:

```bash
gh pr list --head <current-branch> --json number,title,url,state
```

If an open PR exists for the branch, stop and ask whether to view/update it instead of creating a duplicate.

## PR Title

Prefer a concise title derived from branch and commits. Use sentence case or Conventional Commit style depending on repo convention. Do not include Jira key unless the repo already does. Avoid vague titles like `updates`, `fix stuff`, or `changes`.

Examples:

```text
feat: add delegated registry deployment flow
fix: preserve product filters in registry search
docs: clarify local Jira workflow setup
```

## PR Body

Default template:

```md
- <change>
- <change>

<JIRA_URL>
```

Rules:

- Put changes first and Jira URL last.
- Omit headings by default.
- Do not distinguish parent vs subtask unless the user asks.
- Omit Jira URL if Jira context is missing.
- Include verification only if the user asks, the repo requires it, or the PR template requires it.
- Keep the body factual.

## Create PR

Use a temporary body file:

```bash
mktemp
```

Ready PR:

```bash
gh pr create --base <base> --head <current-branch> --title "<title>" --body-file <tmp-body-file>
```

Draft PR:

```bash
gh pr create --draft --base <base> --head <current-branch> --title "<title>" --body-file <tmp-body-file>
```

## Reviewer Lookup

If reviewers were not provided, inspect recent merged PRs:

```bash
gh pr list --base <base> --state merged --limit 3 --json number,title,author,reviews
```

Prefer users who approved the most recent merged PR. If that PR has no useful approvals, inspect up to three merged PRs and choose frequent human approvers. Exclude bots, duplicates, and the author/current GitHub user.

Add reviewers only after confirmation:

```bash
gh pr edit <number> --add-reviewer user-a,user-b
```

## Closeout

After creation, show:

```bash
gh pr view --json number,title,url,state,baseRefName,headRefName
```
