# GitHub Operations

Use this reference when Review Herald needs to read from or write to GitHub. Prefer the GitHub CLI (`gh`) before GitHub plugins/connectors so the skill behaves consistently across runtimes and leaves a command-shaped audit trail.

## Source Basis

- GitHub REST Pull Requests docs list endpoints for PR files, review comments, review requests, reviews, and replies to review comments: `https://docs.github.com/en/rest/pulls`.
- GitHub REST Pull Request Reviews docs expose review state such as `APPROVED`, `CHANGES_REQUESTED`, `COMMENTED`, and `DISMISSED`: `https://docs.github.com/en/rest/pulls/reviews`.
- GitHub GraphQL mutations expose thread-level actions such as `addPullRequestReviewThreadReply`, `resolveReviewThread`, and `unresolveReviewThread`: `https://docs.github.com/en/graphql/reference/mutations`.

## Preferred Read Order

1. Use `gh pr view`, `gh pr diff`, `gh pr status`, `gh pr checks`, and `gh api` for PR metadata, changed files, reviews, review comments, checks, and thread data.
2. Use `gh api graphql` when thread-level fields or mutations require GraphQL, such as resolved conversation state or thread replies.
3. Use an available GitHub connector/plugin only when `gh` is unavailable, unauthenticated, missing required fields, or blocked by the runtime.
4. Use pasted comments when no authenticated path is available; report that remote state could not be verified.

## Data To Capture

- PR title, branch, base, head SHA, author, review decision, and merge/check state when available.
- Changed files and current diff.
- Review submissions, especially requested changes.
- Inline review threads with resolved/unresolved state when available.
- Top-level PR comments that mention required changes.
- CI/check failures only enough to know whether `krt-ci-questor` should take over.

To bootstrap that data into a writable action plan, use:

```bash
rtk python3 skills/krt-review-herald/scripts/build_thread_plan.py --repo <owner/repo> --pr <number> --output thread-plan.json
```

Behavior:

- Fetches review threads through `gh api graphql`.
- Paginates across all thread pages.
- Excludes already resolved threads by default.
- Use `--include-resolved` when old resolved conversations still need auditing.
- Leaves `classification`, `decision`, `reply`, `resolve`, `verification`, and `resolution_reason` blank for later completion.

## Remote Write Policy

Never perform these actions without explicit approval or an enclosing release workflow:

- push commits;
- create, update, or close PRs;
- post PR comments or review replies;
- resolve or unresolve review threads;
- request re-review or reviewers;
- dismiss reviews;
- merge.

When a remote write is approved, prefer the equivalent `gh` command or `gh api` call before connector/plugin mutation APIs. Use connector/plugin writes only when they are the only available authenticated path or the runtime explicitly requires them.

For review-thread replies and resolution, use:

```bash
rtk python3 skills/krt-review-herald/scripts/apply_review_threads.py --plan-file <thread-plan.json> --execute
```

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
      "verification": "rtk pytest tests/normalize_test.py"
    }
  ]
}
```

Script guardrails:

- `resolve: true` requires a reply.
- `resolve: true` requires either `verification` or `resolution_reason`.
- `clarify` and `blocked` decisions cannot auto-resolve.
- Dry-run is the default; add `--execute` only after approval.

Prepare the exact intended remote actions instead:

```text
Remote actions pending approval:
- Reply to thread <id>: "<reply>"
- Resolve thread <id> after reply
- Request re-review from <reviewer>
```

## Practical Notes

- REST review comments and GraphQL review threads are related but not identical. Use thread IDs when resolving conversations.
- `gh api` can call both REST and GraphQL; prefer that route before switching to a plugin/connector.
- A review state of `CHANGES_REQUESTED` is not automatically cleared by local fixes; a reviewer or repository rule may still require re-review.
- Top-level PR comments may contain blockers even when no inline thread is unresolved.
- Resolved threads can still matter if the PR changed again after resolution.
