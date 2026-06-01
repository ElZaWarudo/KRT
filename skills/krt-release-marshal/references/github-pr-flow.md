# GitHub PR Flow

Use this reference when `krt-release-marshal` needs exact `git`/`gh` commands or PR content details. Prefer `gh` before GitHub plugins/connectors for all GitHub reads and writes.

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

Show the selected base in the visible release/PR plan.

## Check Remote Branch State

Check whether current branch exists on origin:

```bash
git ls-remote --heads origin <current-branch>
```

If it does not exist, summarize in the visible release plan that the branch will be published on origin:

```bash
git push -u origin <current-branch>
```

In autonomous mode, do not run this command directly. Pass the exact push operation through `scripts/autonomous_mutation.py` with mutation class `branch_push`, state file, expected old/new SHAs, and enforcement confirmation. If no registered execution template is available, report validation-only/manual-required.

If it exists, inspect ahead/behind:

```bash
git status --porcelain=v1 -b
```

If history was rewritten, summarize that a `--force-with-lease` push will be required and ask for explicit approval:

```bash
git push --force-with-lease origin <current-branch>
```

In autonomous mode, force-with-lease push requires mutation class `branch_force_push`, a ledger entry for the exact branch, expected old/new SHAs, and the branch validator. Plain `--force` remains forbidden.

## Gather PR Content

Collect concise context:

```bash
git log --oneline <base>..HEAD
git diff --name-status <base>...HEAD
git diff --stat <base>...HEAD
```

Run the PR scope guardrail before presenting the release plan:

```bash
python3 <release-marshal-skill-dir>/scripts/check_pr_scope.py --base <base>...HEAD --fail-on-blocking
```

If it prints `BLOCKING:`, the release plan must ask for an explicit split decision or oversized-PR approval before any PR creation/update. Advisory `WARNING:` output may proceed only when it is visible in the plan. Documentation-related warnings are not blocking by themselves, and they must not be "resolved" by hiding docs in stash/worktree/side-branch state. In the visible message, summarize the guardrail result in plain language instead of dumping raw script output.

Check for existing PR:

```bash
gh pr list --head <current-branch> --json number,title,url,state
```

If an open PR exists for the branch, stop and ask whether to view/update it instead of creating a duplicate.

## PR Title

Prefer a concise title derived from branch and commits. Use sentence case or Conventional Commit style depending on repo convention. Do not include Jira key unless the repo already does. Do not include Compound Master IDs, package numbers, or date sequences unless the user or repo convention explicitly requires them. Avoid vague titles like `updates`, `fix stuff`, or `changes`.

Examples:

```text
feat: add delegated registry deployment flow
fix: preserve product filters in registry search
docs: clarify local Jira workflow setup
```

When presenting the title to the user, wrap it inside a short PR proposal that also explains scope and status. The visible message should feel like an editor proposing a PR, not a CLI preview.

## PR Body

Normalize draft copy before validating it:

```bash
python3 <release-marshal-skill-dir>/scripts/format_pr_body.py --file <draft-body-file> > <tmp-body-file>
```

Before creation or update, validate the body with:

```bash
python3 <release-marshal-skill-dir>/scripts/check_pr_body.py --file <tmp-body-file>
```

Default template:

```md
- <Change sentence.>
- <Change sentence.>

<JIRA_URL>
```

Rules:

- Put only the changes contained in this PR first, one factual markdown bullet per line, and the Jira URL last after a blank line.
- Omit headings.
- Do not distinguish parent vs subtask unless the user asks.
- Include only the immediately relevant Jira URL: the standalone task for one-PR work, or the subtask only when a real multi-child parent exists. Do not include both parent and child links unless the user or repo template asks.
- Omit Jira URL if Jira context is missing.
- Do not mention stacked PR relationships, temporary bases, future retargeting, dependency PRs, reviewer instructions, or merge sequencing.
- Do not include verification unless the repo template requires it. Treat upstream test results as readiness context, not body content.
- Keep the body factual.
- If an upstream agent produced `Summary`, `Verification`, or stacked-context copy, run the formatter and use only its cleaned output.

Example:

```md
Adds central regulatory summary publishing with central-client API key and tenant ownership checks.
Adds regulator metadata/proof query API with scoped pseudonyms, no-payload validation, and audit records.
Adds regulatory-api manifest discovery, central-client publishing support, and generated API bindings.

$JIRA_HOST/browse/PDP-93
```

Before remote mutation, present the body under a short `**Cuerpo de la PR**` section and summarize validation as a confidence note such as `cuerpo validado` unless the checker is failing.

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

In autonomous mode, these commands are execution templates only. First call `scripts/autonomous_mutation.py` with mutation class `pr_create` or `pr_update`, the PR state file, exact base/head/head SHA, title/body payload hash, and audit path. If validator or execution template support is unavailable, stop with validation-only/manual-required instead of running `gh pr create` directly.

## Reviewer Lookup

If reviewers were not provided, inspect recent merged PRs:

```bash
gh pr list --base <base> --state merged --limit 3 --json number,title,author,reviews
```

Prefer users who approved the most recent merged PR. If that PR has no useful approvals, inspect up to three merged PRs and choose frequent human approvers. Exclude bots, duplicates, and the author/current GitHub user.

Add reviewers after confirmation, or without a second prompt when the accepted release plan approved automatic reviewer lookup/request and exactly one clear human reviewer was inferred:

```bash
gh pr edit <number> --add-reviewer user-a,user-b
```

In autonomous mode, reviewer requests must use mutation class `reviewer_request` through the executor. The reviewer validator must prove the reviewer/team is in scope, not the author/current agent/bot, and not already requested except as an audited no-op.

## Closeout

After creation, show:

```bash
gh pr view --json number,title,url,state,baseRefName,headRefName
```

## Merge Gate

Merging is not part of the normal release flow. If the user explicitly asks to merge a PR, inspect state before any merge command:

```bash
gh pr view <number> --json number,title,url,state,isDraft,mergeStateStatus,reviewDecision,statusCheckRollup,reviews,baseRefName,headRefName
```

Required before merge:

- The user gave merge authorization for this PR after review state was inspected. Generic approval such as `dale`, `ok`, or `sí` is sufficient only when it directly answers an explicit pending merge prompt for the already resolved PR number.
- The PR is open and not draft.
- `reviewDecision` is `APPROVED`, with at least one visible human reviewer approval that is not from the PR author/current agent account.
- No unresolved `CHANGES_REQUESTED` review remains after the latest approval.
- Required checks are passing or the user explicitly overrides a non-required/check-unavailable condition after seeing the state.

If any required gate is missing, report the missing approval/check/change-request state and stop. Do not run `gh pr merge`, do not enable auto-merge, and do not merge a branch locally.

## Autonomous Merge Gate

Autonomous merge is a ledger-bound exception to the normal merge gate. It is allowed only through `scripts/autonomous_mutation.py` and the validators in `autonomous-validator-registry.md`.

Before an autonomous merge/queue/auto-merge attempt:

```bash
python3 <release-marshal-skill-dir>/scripts/check_merge_eligibility.py --mutation-class <pr_merge|pr_merge_queue|pr_auto_merge> --fixture <live-state-fixture-or-fetched-json>
```

The validator must prove:

- PR is open, not draft, on the expected base/head, and has a current head SHA.
- Human approval is on the current head by a non-author, non-agent, non-bot reviewer.
- No unresolved change request remains.
- Required checks are green; pending, failure, skipped-required, neutral-required, stale, unavailable, or unknown states block.
- Branch protection and ruleset state are available and satisfied.
- Merge queue and auto-merge are treated as distinct mutation classes and audit events.

If live state cannot be fetched or represented for the validator, autonomous merge blocks. Do not fall back to agent judgment.

## Autonomous Stack Merge Checkpoint

When a ledger allows autonomous merge for a stack:

1. Fetch PRs in the contract scope and order them parent before child.
2. Validate and merge/enqueue/auto-merge at most one PR at a time through the executor.
3. After each successful parent merge, refresh downstream base, head SHA, review decision, required checks, branch protection/rulesets, and Jira binding.
4. Treat downstream approvals/checks as stale until live state proves they are current after retarget/rebase.
5. Run `jira_transition_done` only after GitHub evidence or same-contract audit proves the linked PR merged.
6. Stop the stack on the first blocker and record whether independent PR/Jira work may continue according to Compound Master's autonomous flow matrix.
