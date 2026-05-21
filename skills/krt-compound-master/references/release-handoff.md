# Release Handoff

Load only when a selected review unit has passed implementation, verification, review, and required security gates.

Do not duplicate `krt-release-marshal`; hand off with enough context for it to build the visible release plan.

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

Use krt-release-marshal exactly. Do not run tests unless the user explicitly asks; use verification and CI notes only to decide readiness. Do not include tests, verification summaries, stack/dependency context, future retargeting notes, or CI risk notes in the PR body unless the user, repo template, or project convention explicitly requires them. Include automatic reviewer handling in the release plan. Treat jira-policy:optional as Jira-preferred but non-blocking: include Jira lookup/creation/backlink/transition when context and configuration are available, and otherwise state the no-Jira fallback in the release plan without asking a separate Jira-usage question. Include automatic post-PR Jira backlinking and Jira transition to En Revisión when Jira context exists.")
```

Suggested Jira summary/description must be semantic Spanish text. PR title/body bullets, branch name, suggested commit groups, and commit messages must be semantic and follow repo conventions. Do not include roadmap IDs, U-IDs, package numbers, date sequences, or other Compound Master numbering unless the user or repo convention explicitly requires them.

## PR Tree Safety

- Independent PRs target the integration/default branch.
- Stacked PRs target the parent review-unit branch.
- Keep dependency, stack, and future-retarget context in state, Jira/internal notes, or the release plan; do not put it in PR body.
- If the current unit waits on a parent PR and the user says continue, fetch and inspect the integration base before picking the next ready unit.

## Handoff Status

After handoff, update state with:

- Review unit.
- PR URL if created.
- Jira URL if created/reused.
- Reviewer behavior.
- Jira backlink/transition behavior.
- CI break-prevention evidence location.
- Release-follow-up blockers, if any.
