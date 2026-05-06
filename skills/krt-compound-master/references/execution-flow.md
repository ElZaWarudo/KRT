# Execution Flow

Use this reference for Compound Master Steps 6-9.

## Wave Planning

Before selecting workers or reviewer subagents, resolve the execution delegation gate from `SKILL.md`.

- If the current invocation explicitly says `delegation:inline` or "sin subagentes", do not launch KRT-owned subagents.
- If it says `parallel:true`, `delegation:ask`, or "con subagentes", treat that as intent to discuss/approve subagents and ask the gate before launching.
- If it says `delegation:auto` or omits delegation, ask the gate once at the start of execution.
- Record the answer in `compound-master-state.md` with scope, selected mode, and any runtime limitation.
- If subagents are denied or unavailable, continue inline rather than stopping.

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

## Delegation Decision Matrix

Use this matrix after the execution delegation gate and before launching KRT-owned subagents. Explain the selected path in state and in the user-facing progress update.

| Package shape | Default delegation choice |
|---|---|
| Small package, same-file edits, sequential steps, or tightly coupled decisions | Run inline. The coordination overhead is higher than the benefit. |
| Many files to inspect (roughly 30+), scattered docs/contracts, or uncertain local conventions | Launch one read-only `explorer`, then the lead decides whether work stays inline or moves to a worker. |
| Clear implementation scope, defined file ownership, explicit verification, and no product decision remaining | Launch at most one mutating `worker` for the package. |
| Fresh perspective needed after implementation, or the package touches risky surfaces | Use the main `code_review` role and optional read-only reviewer fan-out within budget. |
| Independent packages with non-overlapping write sets and isolated worktrees/checkouts | Parallel workers are allowed only when `parallel:true` and isolation are both present. |
| Overlapping files, unclear ownership, missing isolation, or product/branch decisions still open | Run serially inline or stop for the missing decision. |

Delegation budgets:

- At most one mutating worker per work package.
- At most three read-only reviewer subagents in review fan-out.
- Do not add a second user gate for read-only exploration or reviewer fan-out after the execution delegation gate is already accepted.
- Do not launch more generic agents to compensate for low-confidence output. Perform one targeted follow-up exploration or review with a narrower prompt.

Delegation telemetry to record in `compound-master-state.md`:

- Decision: inline, explorer, worker, reviewer fan-out, or parallel workers.
- Reason: package shape, risk surface, expected benefit, and why inline was or was not sufficient.
- Roles used and whether each was read-only or mutating.
- Outcome: completed, blocked, degraded to inline, or skipped.
- Confidence: high/medium/low with the reason supplied by the lead or subagent.
- Duration: approximate elapsed time when available.
- Loop effect: whether delegation reduced follow-up loops, added review/fix loops, or had no clear effect.

## Work Invocation

Before executing, verify that the resolved `work` role supports implementation-only/no-shipping mode. Stop before duplicate shipping if it cannot.

Invocation shape:

```text
Skill("<work>", "<work-package-path>

Execution constraint: implement this package only and run the verification you can run inside your assigned scope. Do not invoke PR creation, ce-commit-push-pr, Jira transitions, or any shipping workflow. Leave pending commits/changes for the lead and krt-release-marshal. Return changed files, API/contract changes detected, verification attempted, verification results, skipped verification with reasons, and any unresolved questions. Do not ask the user to take over normal local verification or review.")
```

Completion gate:

- Expected files changed/created.
- Impact Scan complete when API contracts, endpoints, bindings, shared helpers, schemas, payloads, auth/tenant/ownership behavior, or test fixture contracts changed.
- Relevant tests run or a no-test justification recorded.
- Consumer-derived tests from the Impact Scan run, or documented as skipped with concrete local blocker and CI coverage expectation.
- Verification gate passes or a documented gap is acceptable under package risk.
- Task tracker shows implementation complete.
- Pending changes/commits are coherent and ready for `krt-release-marshal`.
- No unresolved product decision remains.

After worker return, the lead must inspect the summary/diff, start documented local services when safe, run the package verification gate or closest targeted tests, fix straightforward failures inline or through `work`, and continue to review. Stop only for missing credentials, destructive setup, paid external resources, unclear environment decisions, or non-inferable product/technical decisions.

## Impact Scan Gate

Run this gate after implementation and before code review whenever the diff changes an API contract, endpoint, binding, shared helper, schema, payload, auth/tenant/ownership behavior, or test fixture contract.

Required output:

- Changed contract: concise description such as `POST /api/v1/wallet now requires active tenant context`.
- Consumer scan patterns: endpoint paths, exported names, helper names, bindings, schema names, and error codes likely to find callers.
- Consumers found: source files, tests, fixtures, setup flows, docs, and generated clients affected by the changed contract.
- Required consumer tests: all relevant tests discovered by the scan, not only tests in the package's primary area.
- Run/skipped results: command/result for each required test, or explicit skip reason including missing local service/dependency and whether CI is expected to cover it.

Example shape:

```text
Changed contract:
- POST /api/v1/wallet now requires active tenant context.
Consumer scan patterns:
- CreateWallet
- ApiWallet
- /api/v1/wallet
Consumers found:
- web-application/backend/test/mocha/api-tests/tests-api-wallet.ts
- web-application/backend/test/mocha/api-tests/tests-api-did.ts
- web-application/backend/test/mocha/api-tests/tests-api-vc.ts
- web-application/backend/test/mocha/api-tests/tests-api-anchor-registry.ts
Required consumer tests:
- Wallet, DID, VC, and Anchor Registry API tests.
Run/skipped results:
- <commands/results or local blocker with CI coverage expectation>
```

Do not mark `review-passed` until this gate is complete for every API/contract change. If the scan finds additional consumers, update legacy setup/fixtures as needed and rerun affected tests before review.

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

Passing gate: Impact Scan complete when required, no actionable finding at or above threshold, no unresolved security/data/contract finding, tests pass or an acceptable verification gap is recorded, advisory findings recorded.

## Optional Review Fan-Out

Keep the resolved `code_review` role as the primary review. Fan-out supplements it; it does not replace the main review or the lead's synthesis.

Use read-only reviewer fan-out when the package or Impact Scan touches one or more of:

- auth, authorization, tenant isolation, ownership, or permissions;
- database schema, migrations, backfills, or persistent data integrity;
- public API contracts, generated clients, payloads, bindings, or shared helpers;
- async jobs, queues, retries, ZKP/proof result handling, or external service callbacks;
- performance-sensitive loops, queries, caching, or I/O-heavy paths;
- security-sensitive input handling, secrets, PII, or exposed endpoints.

Fan-out rules:

- Run at most three specialized read-only reviewers.
- Tell each reviewer the work package, origin plan, Impact Scan summary, current branch/base, and exact risk surface to inspect.
- Require each reviewer to return severity, evidence path/line when available, blocking status against `review-threshold`, missing tests, confidence, and recommended next action.
- The lead deduplicates findings, resolves contradictions, and writes one coherent findings document when blockers remain.
- Reopen the work loop only for findings at or above `review-threshold`, or any unresolved security/data/contract/test blocker.
- Log advisory findings below threshold unless the user marks them blocking.

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
Suggested commit grouping:
- <type(scope): summary> -- <files/surfaces> -- <why this is one logical review unit>
- <type(scope): summary> -- <files/surfaces> -- <why this is separate or bundled>
Verification results for release-readiness only, not PR body copy:
- <command/result>
Impact Scan for release-readiness only:
- <changed contracts/consumer tests summary or Not required>

Use krt-release-marshal exactly. Do not run tests unless the user explicitly asks; use the verification results above only to decide readiness. Do not include tests or verification summaries in the PR body unless the user, repo template, or project convention explicitly requires them. Include automatic reviewer handling in the release plan: use explicit reviewers if provided, otherwise infer a clear reviewer after PR creation and request review without asking a second time; skip reviewer assignment if no clear human reviewer exists. Include automatic post-PR Jira transition to En Revisión in the release plan when Jira context exists; after PR creation, use krt-jira-scribe and the real transition list to perform that approved transition without asking a second time.")
```

Suggested Jira summary/description, PR title/body bullets, branch name, suggested commit groups, and eventual commit messages must be semantic. Do not include roadmap IDs, U-IDs, package numbers, date sequences, or other Compound Master numbering unless the user or repo convention explicitly requires them.

PR tree safety:

- Independent PRs target integration/default branch.
- Stacked PRs target parent package branch and declare dependency in PR body.
- Do not retarget stacked PRs silently.
- Do not combine unrelated roadmap items unless grouped in one package.
- If an open PR exists for the branch, do not create a duplicate.
- If Jira is required and config is missing, stop with a configuration blocker.
- If Jira is optional and config is missing, let `krt-release-marshal` ask whether to continue without Jira.

After handoff, record Jira URL, PR URL, status, branch, base, reviewers, and blockers in state.
