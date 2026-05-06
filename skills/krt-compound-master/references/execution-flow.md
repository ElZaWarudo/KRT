# Execution Flow

Use this reference for Compound Master Steps 6-9.

## Wave Planning

Classify packages:

- Independent: no hard dependency and no dangerous file overlap.
- Dependent: requires another package, branch, PR, schema, API, or merged change.
- Overlapping: touches files also touched by another package.
- High-risk: auth, security, payments, PII, migrations, public API, deployment, permissions, external APIs, shared contracts.

Rules:

- Independent packages may branch from the integration base.
- Dependent packages wait for merge or become stacked PRs based on parent branch.
- Overlapping/high-risk packages run serially unless the user explicitly accepts risk and isolation exists.
- `parallel:false` forces serial execution.
- `parallel:true` requires isolated worktrees/checkouts and non-overlapping scopes.
- Parallel subagents without isolation must not stage, commit, push, create PRs, transition Jira, or run broad mutation-prone flows.

If execution was requested without `package:`, select the first unblocked package from the earliest safe wave, state why, and continue unless this changes scope, requires a stacked branch decision, or conflicts with user-provided ordering.

## Work Invocation

Before executing, verify that the resolved `work` role supports implementation-only/no-shipping mode. Stop before duplicate shipping if it cannot.

Invocation shape:

```text
Skill("<work>", "<work-package-path>

Execution constraint: implement this package only and run the verification you can run inside your assigned scope. Do not invoke PR creation, ce-commit-push-pr, Jira transitions, or any shipping workflow. Leave pending commits/changes for the lead and krt-release-marshal. Return changed files, verification attempted, verification results, skipped verification with reasons, and any unresolved questions. Do not ask the user to take over normal local verification or review.")
```

Completion gate:

- Expected files changed/created.
- Relevant tests run or a no-test justification recorded.
- Verification gate passes or a documented gap is acceptable under package risk.
- Task tracker shows implementation complete.
- Pending changes/commits are coherent and ready for `krt-release-marshal`.
- No unresolved product decision remains.

After worker return, the lead must inspect the summary/diff, start documented local services when safe, run the package verification gate or closest targeted tests, fix straightforward failures inline or through `work`, and continue to review. Stop only for missing credentials, destructive setup, paid external resources, unclear environment decisions, or non-inferable product/technical decisions.

## Code Review Loop

Preferred invocation:

```text
Skill("<code_review>", "mode:autofix plan:<origin-plan-path> base:<base-branch>")
```

Read-only fallback when mutation is unsafe:

```text
Skill("<code_review>", "mode:report-only plan:<origin-plan-path> base:<base-branch>")
```

Invoke the resolved review role normally. Do not force inline/report-only just because the skill may launch agents internally. If a resolved review invocation fails because the runtime refused agent launch, retry once with that review skill's documented inline/report-only mode and record the degraded path in state.

Loop:

1. Run review.
2. If safe autofixes were applied, rerun relevant tests.
3. Leave review-fix changes for `krt-release-marshal` commit planning unless project policy requires immediate commits.
4. For findings at or above `review-threshold`, or any gated/manual correctness, security, data, contract, or test finding:
   - write `docs/review-findings/<package-slug>-round-N.md`;
   - ask only for non-inferable decisions;
   - invoke `work` on the findings doc with the same no-shipping constraint;
   - rerun tests and review.
5. Log P3/advisory findings unless the user marks them blocking.
6. Stop after three rounds if blockers remain.

Passing gate: no actionable finding at or above threshold, no unresolved security/data/contract finding, tests pass or an acceptable verification gap is recorded, advisory findings recorded.

## Release Marshal Handoff

When implementation and review gates pass, invoke `krt-release-marshal`; do not duplicate its procedures and do not stop with "next step" when the role is available.

Handoff prompt shape:

```text
Skill("<project_pr>", "Run the full krt-release-marshal workflow for this completed work package.

Work package: <work-package-path>
Roadmap item: RDM-###
Origin plan: <origin-plan-path>
Current branch: <branch-name>
Intended base: <base-branch>
Jira policy: <required|optional|skip>
Suggested Jira summary: <summary>
Suggested Jira description: <description>
Suggested PR title: <title>
Suggested PR body bullets:
- <change>
- <change>
Verification results:
- <command/result>

Use krt-release-marshal exactly. Do not run tests unless the user explicitly asks; use the verification results above. Ask before external mutations or notifications according to krt-release-marshal. Include automatic post-PR Jira transition to En Revisión in the release plan when Jira context exists; after PR creation, use krt-jira-scribe and the real transition list to perform that approved transition without asking a second time.")
```

PR tree safety:

- Independent PRs target integration/default branch.
- Stacked PRs target parent package branch and declare dependency in PR body.
- Do not retarget stacked PRs silently.
- Do not combine unrelated roadmap items unless grouped in one package.
- If an open PR exists for the branch, do not create a duplicate.
- If Jira is required and config is missing, stop with a configuration blocker.
- If Jira is optional and config is missing, let `krt-release-marshal` ask whether to continue without Jira.

After handoff, record Jira URL, PR URL, status, branch, base, reviewers, and blockers in state.
