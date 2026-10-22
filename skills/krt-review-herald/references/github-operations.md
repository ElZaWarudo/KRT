# GitHub Operations

Prefer `gh` over connectors or plugins; fall back to them only when `gh` is
unavailable or missing a field.

## Reading

- `gh pr view <n> --json title,headRefName,baseRefName,reviewDecision,reviews,comments,statusCheckRollup`
  for state, review submissions, top-level comments and checks.
- `scripts/build_thread_plan.py --repo <owner/repo> --pr <n> [--output plan.json] [--include-resolved]`
  for inline review threads with resolved/outdated state. It pages through
  `gh api graphql` and leaves `classification`, `decision`, `reply`, `resolve`,
  `verification` and `resolution_reason` blank.
- `gh api repos/<owner>/<repo>/pulls/<n>/comments` returns REST review comments.
  These are not threads: resolving needs the GraphQL thread ID (`PRRT_...`).

Notes:

- `CHANGES_REQUESTED` doesn't clear when you push fixes; the reviewer or a
  re-review request does.
- A resolved thread can matter again if later commits reintroduced the issue.

## Writing

Every write below needs approval of the exact action: replies, resolutions,
unresolving, PR comments, reviewer or re-review requests, review dismissal,
pushes and merges.

Thread replies and resolutions go through
`scripts/apply_review_threads.py --plan-file plan.json [--execute]`. Without
`--execute` it only validates and prints the operations. With it, it calls the
GraphQL `addPullRequestReviewThreadReply` and `resolveReviewThread` mutations.

Plan shape:

```json
{
  "repository": "owner/repo",
  "pull_request": 123,
  "threads": [
    {
      "thread_id": "PRRT_xxx",
      "path": "src/file.ts",
      "line": 42,
      "classification": "blocking_fix",
      "decision": "fix",
      "reply": "Fixed by reusing the shared normalizer.",
      "resolve": true,
      "verification": "pytest tests/test_normalize.py"
    }
  ]
}
```

`decision` is one of `fix`, `reply`, `decline`, `already-addressed`, `stale`,
`clarify`, `blocked`. Validation errors: `resolve: true` without a reply,
without `verification` or `resolution_reason`, or on a `clarify`/`blocked`
decision.
