# Release Handoff

Load only when a selected review unit has passed implementation, verification, review, and required security gates.

Do not duplicate `krt-release-marshal`; hand off with enough context for it to build the visible release plan. Normal handoff may authorize preparation for review only; it must not authorize or suggest merging a PR. Autonomous handoff may include a merge candidate only when an active ledger allows that exact mutation class, and Release Marshal's executor still owns the merge decision.

## Handoff Prompt

```text
Skill("<project_pr>", "Run the full krt-release-marshal workflow for this completed review unit.

Work package: <work-package-path>
Review unit: <RU# and title>
Roadmap item: RDM-###
Origin plan: <origin-plan-path>
Current branch: <branch-name>
Intended base: <base-branch>
Jira policy: <required|optional|skip>
Autonomous ledger: <none|path>
Autonomous executor mode: <manual-required|validation-only|executor-enabled>
Autonomous mutation classes requested: <none|pr_merge|pr_merge_queue|pr_auto_merge|jira_transition_done|...>
Latest audit event hash: <none|hash>
Suggested Jira summary: <Spanish summary>
Suggested Jira description: <Spanish description>
Suggested PR title: <title>
Suggested PR body bullets:
- <change sentence>
- <change sentence>
Suggested commit grouping for this review unit:
- <type(scope): summary> -- <files/surfaces> -- <why this is one logical review unit>
- <type(scope): summary> -- <files/surfaces> -- <why this is separate or bundled>
Verification results for release-readiness only, not PR body copy:
- <command/result>
Impact Scan for release-readiness only:
- <changed contracts/consumer tests summary or Not required>
CI risk notes for release-readiness only:
- <changed CI surface/local equivalent command/result or CI-only gap>
Stack choreography, when stacked:
- Parent merge method: <merge|rebase|squash|unknown>
- Child refresh after parent merge: <rebase|retarget|not needed|unknown>
- Parent branch deletion timing: <after child refresh|not applicable|unknown>

Use krt-release-marshal exactly. Do not run tests unless the user explicitly asks; use verification and CI notes only to decide readiness. Do not include tests, verification summaries, stack/dependency context, future retargeting notes, or CI risk notes in the PR body unless the user, repo template, or project convention explicitly requires them. Include automatic reviewer handling in the release plan. Treat jira-policy:optional as Jira-preferred but non-blocking: include Jira lookup/creation/backlink/transition when context and configuration are available, and otherwise state the no-Jira fallback in the release plan without asking a separate Jira-usage question. Include automatic post-PR Jira backlinking and Jira transition to En Revisión when Jira context exists. In manual/guarded flow, do not merge, request merge, or treat this handoff as merge approval. In autonomous flow, attempt merge/Jira completion only through the ledger-bound mutation executor when validators pass; otherwise the closeout must leave the PR awaiting the exact missing gate.")
```

Suggested Jira summary/description must be semantic Spanish text. PR title/body bullets, branch name, suggested commit groups, and commit messages must be semantic and follow repo conventions. Do not include roadmap IDs, U-IDs, package numbers, date sequences, or other Compound Master numbering unless the user or repo convention explicitly requires them.
If the current branch is a planning/docs-only branch, do not hand it off as the shipping branch. Rebase or switch onto the intended fresh integration base first, use a semantic feature branch for the completed review unit, and carry any related planning artifacts there instead of opening a docs-only delivery branch.

## PR Tree Safety

- Independent PRs target the integration/default branch.
- Stacked PRs target the parent review-unit branch.
- Keep dependency, stack, and future-retarget context in state, Jira/internal notes, or the release plan; do not put it in PR body.
- If a stacked parent is expected to merge by squash, hand off an explicit child refresh plan. Do not assume GitHub will preserve downstream commit identity automatically.
- If the current unit waits on a parent PR and the user says continue, fetch and inspect the integration base before picking the next ready unit.

## Handoff Status

After handoff, update state with:

- Review unit.
- PR URL if created.
- Jira URL if created/reused.
- Reviewer behavior.
- Merge status: not attempted; requires the normal GitHub-visible merge gate plus separate exact user merge authorization. On protected/normal bases that means reviewer approval; on experimental bases it may instead be review-optional branch protection.
- Autonomous merge status when applicable: not requested, validation-only, blocked with reasons, enqueued, auto-merge enabled, or merged with audit event.
- Jira backlink/transition behavior.
- CI break-prevention evidence location.
- Release-follow-up blockers, if any.
