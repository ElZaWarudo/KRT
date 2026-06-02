# Stacked PRs With Squash Merge

## Trigger

A parent PR in a GitHub stack merged by squash. The child PR still pointed to the parent branch and GitHub could not preserve commit identity across the squash result. The parent branch disappeared before the child was refreshed.

## What Happened

- The stack split was correct: the fix and the feature belonged in separate review units.
- The failure was in GitHub merge choreography, not in Jira or Compound Master.
- The child PR ended up closed/unrecoverable because its base branch disappeared before retarget/rebase happened.

## Durable Learning

Squash merge breaks stacked PR ancestry by commit identity. Even when the content is already absorbed into the final base, GitHub may still treat the child PR as depending on commits or a branch that no longer exists.

## Operational Rule

- `stacked PR + squash merge => refresh the child immediately`
- Do not delete the parent branch until the child has been rebased or retargeted onto the final base.
- After the child is refreshed, treat its approvals and checks as stale until GitHub shows them current on the refreshed head/base.

## Practical Checklist

Before merging the parent PR:

- Decide the parent merge method explicitly.
- If the child is stacked on the parent and the parent will merge by squash, include a downstream refresh plan:
  - rebase child onto the final base, or
  - retarget/reopen the child directly against the final base.

After merging the parent PR by squash:

- Rebase or retarget the child before continuing review/merge work.
- Refresh approvals/checks expectations for the child.
- Delete the parent branch only after the child refresh is complete.

## What This Is Not

- Not a Jira problem.
- Not a Compound Master slicing problem.
- Not a reason to avoid stacked PRs categorically.

It is a release-choreography rule specific to GitHub stacks, especially when squash merge is involved.
