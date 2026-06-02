# Autonomous GitHub Fixtures

Load when reviewing or extending GitHub-side autonomous validators.

Fixture directory:

```text
skills/krt-release-marshal/scripts/fixtures/github-autonomy/
```

Validator coverage:

| Scenario | Fixture | Validator outcome |
|---|---|---|
| Immediate merge with current-head human approval and green required checks | `merge_allowed.json` | `check_merge_eligibility.py` allows `pr_merge` |
| Experimental base does not require approving reviews | `merge_experimental_review_optional.json` | Allows `pr_merge` without human approval |
| Experimental base still requires approving reviews | `merge_experimental_review_required.json` | Blocks reviewless merge on protected experimental branches |
| Approval was for an old head SHA | `merge_stale_approval.json` | Blocks `current-head-human-approval-missing` |
| Required check is pending | `merge_pending_check.json` | Blocks `required-check-not-green:<name>` |
| Merge queue is required | `merge_queue_required.json` | Blocks `pr_merge`; allows `pr_merge_queue` as `enqueue` |
| PR create has no duplicate | `pr_create_valid.json` | Allows PR mutation/ready paths |
| PR create would duplicate an open PR | `pr_create_duplicate.json` | Blocks `duplicate-open-pr` |
| Branch belongs to run-owned namespace | `branch_valid.json` | Allows normal branch cleanup, blocks force without ledger enablement |
| Reviewer already requested | `reviewer_noop.json` | Allows no-op with warning |
| Parent PR merged but child not refreshed | `stack_after_parent_merge.json` | Blocks retarget/approval/check freshness |

These fixtures intentionally mirror `gh pr view` concepts: `headRefOid`, `isDraft`, `reviewDecision`, `latestReviews`, `statusCheckRollup`, `mergeStateStatus`, base/head refs, branch protection, and merge queue requirement. Live implementations should prefer `gh` and `gh api` before plugins/connectors or direct REST/GraphQL clients. Unavailable data must block instead of being inferred.

Historical scenario basis: stacked PR, Jira transition, and CI evidence patterns from `docs/orchestration/archive/compound-master-state/2026-05-11-productpass-delegated-architecture-full-state.md`.
