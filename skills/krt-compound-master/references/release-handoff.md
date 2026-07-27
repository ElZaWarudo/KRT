# Release Handoff

Load only when a selected review unit has passed implementation, verification, review, and required security gates.

Do not duplicate `krt-release-marshal`; hand off with enough context for it to build the visible release plan. Normal handoff may authorize preparation for review only; it must not authorize or suggest merging a PR. Autonomous handoff may include a merge candidate only when an active ledger allows that exact mutation class, and Release Marshal's executor still owns the merge decision.

## Handoff Hard Rules

- Release handoff is not merge authority. Do not merge PRs or branches, imply merge approval, or pass merge intent in manual/guarded flow. In autonomous flow, pass only a ledger-scoped merge candidate to `krt-release-marshal`; Release Marshal's executor must still validate live state, reviewer approval, required checks, branch protection, exact scope, and audit readiness.
- Do not open PRs from protected branches. If the current branch is protected or planning/docs-only, create or switch to the semantic implementation branch before handoff.
- Keep planning IDs out of public release text. PR titles, PR body bullets, commit messages, branch names, and Jira text should be semantic unless the repo convention explicitly requires IDs.
- Treat verification, Impact Scan, Security Sentinel, CI evidence, and internal review as readiness context, not PR body copy or merge proof.
- Trust bundled checker results over assumptions. If Jira readiness reports `ok: true`, credentials are present for that checkout; diagnose the real Jira API failure instead of asking for credentials. If PR/body/scope checks pass or fail, act on the checker result and do not invent ad-hoc PR structure.
- Never ask for Jira credentials. With `jira-policy:optional`, attempt Jira when context/configuration is present; otherwise record the no-Jira fallback and continue after the normal release-plan approval.

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
jira_provider: <cloud|server-datacenter|none|unresolved>
Autonomous ledger: <none|path>
Autonomous executor mode: <manual-required|validation-only|executor-enabled>
Autonomous mutation classes requested: <none|pr_merge|pr_merge_queue|pr_auto_merge|jira_transition_done|...>
Latest audit event hash: <none|hash>
Jira unit mapping for this PR:
- PR covers review units: <RU#[, RU#...]>
- Jira shape: <standalone Tarea | parent + one subtask per covered review unit>
- Subtasks to backlink and transition with this PR: <none | RU# -> Spanish subtask summary, ...>
- Transition fan-out: En Revision on open and Hecho on merge apply to every linked subtask
Suggested Jira summary (per Jira unit): <Spanish summary, one per standalone Tarea or per subtask>
Suggested Jira description (per Jira unit): <Spanish description, one per Jira unit>
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
- Open-stack depth before this PR: <n> of max 3 (target <=2)
- At-cap action if exceeded: <wait-for-parent-merge|collapse-to-integration-base|not-applicable>
- Parent merge method: <merge|rebase|squash|unknown>
- Child refresh after parent merge: <rebase|retarget|not needed|unknown>
- Parent branch deletion timing: <after child refresh|not applicable|unknown>
- Downstream-fix notes: <none|addresses finding from PR #X: surface>

Use krt-release-marshal exactly. Preserve `jira_provider` in every release handoff and autonomous Jira mutation; never silently substitute the sibling Jira provider. Do not run tests unless the user explicitly asks; use verification and CI notes only to decide readiness. Do not include tests, verification summaries, stack/dependency context, future retargeting notes, or CI risk notes in the PR body unless the user, repo template, or project convention explicitly requires them. Include automatic reviewer handling in the release plan. Treat jira-policy:optional as Jira-preferred but non-blocking: include Jira lookup/creation/backlink/transition when provider, context, and configuration are available, and otherwise state the no-Jira fallback in the release plan without asking a separate Jira-usage question. Include automatic post-PR Jira backlinking and Jira transition to En Revisión when Jira context exists; when the PR groups several review units, backlink and transition every covered review-unit subtask, not just one. In manual/guarded flow, do not merge, request merge, or treat this handoff as merge approval. In autonomous flow, attempt merge/Jira completion only through the ledger-bound mutation executor when validators pass; otherwise the closeout must leave the PR awaiting the exact missing gate.")
```

Suggested Jira summary/description must be semantic Spanish text. PR title/body bullets, branch name, suggested commit groups, and commit messages must be semantic and follow repo conventions. Do not include roadmap IDs, U-IDs, package numbers, date sequences, or other Compound Master numbering unless the user or repo convention explicitly requires them.
If the current branch is a planning/docs-only branch, do not hand it off as the shipping branch. Rebase or switch onto the intended fresh integration base first, use a semantic feature branch for the completed review unit, and carry any related planning artifacts there instead of opening a docs-only delivery branch.

## PR Tree Safety

- Independent PRs target the integration/default branch.
- Stacked PRs target the parent review-unit branch.
- Cap open stacked PRs at 2-3 (target <=2). When a new stacked unit would exceed the cap, do not open it: wait for the parent PR to merge into the integration base and re-base on the refreshed base, or collapse the pending chain onto the integration base first. Never hand off a deep unmerged stack, and never resolve one by abandoning it for a single mega-consolidation PR.
- When the unit fixes a surface an earlier still-open stacked PR's reviewer flagged, include a downstream-fix note (`addresses finding from PR #X`) in the handoff so the earlier review is not lost.
- Keep dependency, stack, and future-retarget context in state, Jira/internal notes, or the release plan; do not put it in PR body.
- If a stacked parent is expected to merge by squash, hand off an explicit child refresh plan. Do not assume GitHub will preserve downstream commit identity automatically.
- If the current unit waits on a parent PR and the user says continue, fetch and inspect the integration base before picking the next ready unit.

## Handoff Status

After handoff, update state with:

- Review unit(s) covered by this PR.
- PR URL if created.
- Jira URL(s) if created/reused, and the PR-to-Jira mapping: standalone `Tarea`, or parent key plus the review-unit subtask(s) this PR backlinks.
- Reviewer behavior.
- Merge status: not attempted; requires the normal GitHub-visible merge gate plus separate exact user merge authorization. On protected/normal bases that means reviewer approval; on experimental bases it may instead be review-optional branch protection.
- Autonomous merge status when applicable: not requested, validation-only, blocked with reasons, enqueued, auto-merge enabled, or merged with audit event.
- Jira backlink/transition behavior.
- CI break-prevention evidence location.
- Release-follow-up blockers, if any.
