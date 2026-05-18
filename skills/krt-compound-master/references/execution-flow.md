# Execution Flow

Use this reference for Compound Master's execution phase: Execution Wave Planning through Release Marshal Handoff.

## Wave Planning

Before selecting workers or reviewer subagents, resolve `delegation` and `autonomy` from `SKILL.md`.

- If the current invocation explicitly says `delegation:inline` or "sin subagentes", do not launch KRT-owned subagents.
- If it says `delegation:ask`, `autonomy:manual`, `parallel:true` without `autonomy:high`, or "con subagentes", ask the gate before launching KRT-owned mutating subagents.
- If it says `delegation:auto` or omits delegation, use `autonomy:guarded` unless another autonomy value is explicit.
- Under `autonomy:guarded`, launch read-only explorers, security watchers, Impact Scan helpers, and reviewer fan-out without another user gate when useful. Launch one scoped mutating worker without asking only when the work package has clear ownership, expected files/tests, no open product decision, no ambiguous branch/base strategy, and safe isolation.
- Under `autonomy:high`, parallel workers are allowed only when `parallel:true`, isolated worktrees/checkouts, non-overlapping write scopes, dependency order, and fallback branch strategy are all recorded.
- Record the resolved mode in `compound-master-state.md` with scope, selected autonomy, selected delegation, and any runtime limitation.
- If subagents are denied or unavailable, continue inline rather than stopping.

Classify packages:

- Independent: no hard dependency and no dangerous file overlap.
- Dependent: requires another package, branch, PR, schema, API, or merged change.
- Overlapping: touches files also touched by another package.
- High-risk: auth, security, payments, PII, migrations, public API, deployment, permissions, external APIs, shared contracts.
- Production-sensitive: `production:live` or `production:unknown` plus any change to existing behavior, persistence, API contracts, auth/tenant rules, deployment/config, migrations, data deletion, user workflows, or rollback expectations.

Rules:

- Independent packages may branch from the integration base.
- Dependent packages wait for merge or become stacked PRs based on parent branch.
- Overlapping/high-risk packages run serially unless the user explicitly accepts risk and isolation exists.
- Production-sensitive packages run serially by default, require explicit compatibility/rollback evidence, and cannot intentionally break existing behavior without recorded user approval.
- Prototype packages may run with lighter compatibility gates, but still require explicit approval for destructive data operations, credential/security weakening, or public contract removal.
- `parallel:false` forces serial execution.
- `parallel:true` requires isolated worktrees/checkouts and non-overlapping scopes.
- Parallel subagents without isolation must not stage, commit, push, create PRs, transition Jira, or run broad mutation-prone flows.

If execution was requested without `package:`, select the first unblocked package from the earliest safe wave, state why, and continue unless this changes scope, requires a stacked branch decision, or conflicts with user-provided ordering.

## Delegation Decision Matrix

Use this matrix after autonomy/delegation resolution and before launching KRT-owned subagents. Explain the selected path in state and in the user-facing progress update.

| Package shape | Default delegation choice |
|---|---|
| Small package, same-file edits, sequential steps, or tightly coupled decisions | Run inline. The coordination overhead is higher than the benefit. |
| Many files to inspect (roughly 30+), scattered docs/contracts, or uncertain local conventions | Launch one read-only `explorer`; under `guarded`, this does not need a user gate. The explorer returns an execution context packet. |
| Clear implementation scope, defined file ownership, explicit verification, autonomy contract present, and no product decision remaining | Launch at most one mutating `worker` for the package. Under `guarded`, do this without asking when isolation and branch/base are safe. |
| Fresh perspective needed after implementation, or the package touches risky surfaces | Use the main `code_review` role and optional read-only reviewer fan-out within budget. Read-only fan-out is automatic under `guarded` when it materially reduces risk. |
| Independent packages with non-overlapping write sets and isolated worktrees/checkouts | Parallel workers are allowed only when `parallel:true`, `autonomy:high`, and isolation are all present. |
| Overlapping files, unclear ownership, missing isolation, or product/branch decisions still open | Run serially inline or stop for the missing decision. |

## Agent Autonomy Contract

Every work package should give execution agents explicit decision rights.

Agents may decide without asking when the choice is reversible, local to the package, consistent with existing repo patterns, covered by tests or inspection, and does not alter product behavior or release topology. Examples include internal helper names, exact test selector choice, equivalent local verification command, small fixture updates required by the package, and straightforward lint/type/test fixes inside the assigned scope.

Agents must record as assumptions when they infer repo conventions, choose one equivalent implementation path over another, skip verification because of a concrete local blocker, or make a low-risk compatibility-preserving adjustment.

Agents must escalate to the lead when a decision changes product behavior, authorization/tenant/data contract rules, public API compatibility, destructive persistence behavior, production deployment/rollback expectations, branch/base strategy, Jira/PR workflow, credentials, paid external resources, or broad scope outside the package.

An agent that hits an escalation point should pause only that decision. It should still complete safe exploration, tests, and implementation work that does not depend on the blocked choice.

Delegation budgets:

- At most one mutating worker per work package.
- At most three read-only reviewer subagents in review fan-out.
- Do not add a second user gate for read-only exploration, Impact Scan helpers, security watchers, or reviewer fan-out after autonomy has been resolved.
- Do not launch more generic agents to compensate for low-confidence output. Perform one targeted follow-up exploration or review with a narrower prompt.

Delegation telemetry to record in `compound-master-state.md`:

- Decision: inline, explorer, worker, reviewer fan-out, or parallel workers.
- Reason: autonomy mode, package shape, risk surface, expected benefit, and why inline was or was not sufficient.
- Roles used and whether each was read-only or mutating.
- Outcome: completed, blocked, degraded to inline, or skipped.
- Confidence: high/medium/low with the reason supplied by the lead or subagent.
- Duration: approximate elapsed time when available.
- Loop effect: whether delegation reduced follow-up loops, added review/fix loops, or had no clear effect.

## Work Invocation

Before executing, verify that the resolved `work` role supports implementation-only/no-shipping mode. Stop before duplicate shipping if it cannot.

Carry production posture into every worker prompt. For `production:live` or `production:unknown`, instruct the worker to preserve existing behavior by default, prefer additive/compatible changes, call out any possible breaking change before implementing it, and return migration, rollback, deployment, and regression-test implications. For `production:prototype`, instruct the worker which compatibility gates are intentionally relaxed and which safety boundaries still apply.

Carry the work package's autonomy contract into every worker prompt. Tell the worker to decide reversible, package-local, convention-following choices directly; record assumptions and low-risk deviations; and escalate only the blocked decision categories named in the contract.

Preserve plan-unit granularity during execution. A work package is the PR/Jira unit, not a license to flatten the origin plan. Before invoking `work`, extract the package's implementation units from the work package and origin plan. Track each unit's status in `compound-master-state.md` as pending, in-progress, implemented, verified, skipped, or blocked.

When a package contains multiple units, choose one of these execution shapes and record why:

- **Sequential unit loop:** invoke `work` one unit at a time when units have different risk surfaces, separate verification gates, unclear boundaries, or likely review/fix loops.
- **Single worker, explicit unit checklist:** invoke one worker for the whole package only when the units are tightly coupled and one pass is more coherent. The prompt must still list each U-ID/unit separately and require a per-unit result.
- **Parallel workers:** only when `parallel:true`, isolation exists, dependencies allow it, and write scopes do not overlap.

## Security Watch During Work

Security Watch is enabled by default for high-risk packages during Step 7 execution. It is read-only and incremental. Its job is to notice risk while work is still moving, then provide structured input to the final Security Sentinel Gate.

Enable watch when the package touches:

- auth, authorization, tenant isolation, ownership, permissions, roles, or scopes;
- secrets, credentials, tokens, env vars, CI/CD permissions, or deploy credentials;
- PII, regulated data, audit logs, retention, encryption, exports, or destructive actions;
- public API contracts, webhooks, callbacks, uploads/downloads, parsing, redirects, or external integrations;
- deployment exposure, Helm/Kubernetes/Docker security posture, public ingress, service accounts, RBAC, or network policy;
- dependency, package manager, base image, GitHub Action, generated client, or other supply-chain surface.

Execution modes:

- If KRT-owned read-only subagents are approved/available, run one `security_watcher` alongside or immediately after each worker return.
- If subagents are unavailable or delegation is inline, the lead performs the same watch pass after each worker return or meaningful diff update.
- The watcher must not edit files, stage, commit, push, create PRs, transition Jira, run intrusive scanners, decode secrets, or mutate runtime state.
- The watcher should not interrupt normal work for P2/P3 concerns. Record notes for the final gate.
- Obvious P0/P1 risk may stop the execution loop immediately with a `security-blocked` closeout.

Security watch note shape:

```text
Security watch notes:
- Surface: <auth/tenant/secrets/API/deploy/supply-chain/etc.>
  Files:
  Early concern:
  Suggested verification:
  Gate input:
  Severity estimate: P0/P1/P2/P3/advisory
```

Record notes in `compound-master-state.md` and, when useful, under the work package's Security Gate section. The final Security Sentinel Gate owns the formal finding decision; watch notes are leads, not final verdicts.

Do not mark the package `implementation-complete` merely because a worker returned once. Mark it complete only after every included unit has an explicit implemented/verified/skipped/blocked disposition, with skipped verification justified.

Invocation shape:

```text
Skill("<work>", "<work-package-path>

Execution constraint: implement this package only and run the verification you can run inside your assigned scope. Use the package autonomy contract: decide reversible, package-local, convention-following choices; record assumptions; escalate only non-inferable product, contract, security, production, branch/base, Jira/PR, credential, or scope decisions. Preserve the origin plan's implementation units: for each included U-ID/unit, report status, changed files, verification attempted/results/skips, and blockers. Do not invoke PR creation, ce-commit-push-pr, Jira transitions, or any shipping workflow. Leave pending commits/changes for the lead and krt-release-marshal. Return changed files, API/contract changes detected, verification attempted, verification results, skipped verification with reasons, decisions made autonomously, and any unresolved questions. Do not ask the user to take over normal local verification or review.")
```

Completion gate:

- Expected files changed/created.
- Every implementation unit included in the package has an explicit disposition: implemented, verified, skipped with reason, or blocked.
- Production posture satisfied: live/unknown packages include compatibility, migration/deployment, rollback, and regression evidence for touched surfaces, or a recorded approval for intentional breakage.
- Impact Scan complete when API contracts, endpoints, bindings, shared helpers, schemas, payloads, auth/tenant/ownership behavior, or test fixture contracts changed.
- Relevant tests run or a no-test justification recorded.
- Consumer-derived tests from the Impact Scan run, or documented as skipped with concrete local blocker and CI coverage expectation.
- Verification gate passes or a documented gap is acceptable under package risk.
- Task tracker shows implementation complete.
- Pending changes/commits are coherent and ready for `krt-release-marshal`.
- No unresolved product decision remains.

Verification ladder:

- Run the narrowest useful targeted command to diagnose a failure or changed behavior.
- When tests depend on global hooks, shared fixtures, seeded state, or suite-level setup, run the natural sub-suite for the affected area before trusting the result.
- Before release handoff or PR update for a CI fix, run the repo-specific command equivalent to the affected CI job, derived from workflow config, package scripts, Makefiles, task runners, or documented local commands.
- If the CI-equivalent command cannot run locally, record the concrete blocker and pass that as an explicit verification gap to `krt-release-marshal`; do not treat targeted-only evidence as enough for a PR update.

After worker return, the lead must inspect the summary/diff by unit, update unit statuses, collect Security Watch notes when enabled, start documented local services when safe, run the package verification gate or closest targeted tests, fix straightforward failures inline or through `work`, and continue to review only when all units have a non-pending disposition. Stop only for missing credentials, destructive setup, paid external resources, unclear environment decisions, non-inferable product/technical decisions, or obvious P0/P1 security risk.

## Impact Scan Gate

Run this gate after implementation and before code review whenever the diff changes an API contract, endpoint, binding, shared helper, schema, payload, auth/tenant/ownership behavior, or test fixture contract.

Under `autonomy:guarded` or `autonomy:high`, delegate the Impact Scan to a read-only explorer/reviewer when the scan spans multiple modules, generated clients, fixture setup, or broad test surfaces. The helper owns discovery only: consumer paths, likely drift tests, and recommended verification. The lead still records the final gate result.

Required output:

- Changed contract: concise description such as `POST /api/v1/wallet now requires active tenant context`.
- Consumer scan patterns: endpoint paths, exported names, helper names, bindings, schema names, and error codes likely to find callers.
- Consumers found: source files, tests, fixtures, setup flows, docs, and generated clients affected by the changed contract.
- Required consumer tests: all relevant tests discovered by the scan, not only tests in the package's primary area.
- Contract-drift test scan: when auth, permissions, roles, scopes, tenant ownership/isolation, endpoint gates, payload contracts, or fixtures changed, search for tests that encode old exact expectations. Include exact arrays, snapshots, allowlists, seeded fixtures, permission bundle tests, normalization tests, and generated-contract assertions.
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
Contract-drift test scan:
- rg "deepStrictEqual|toEqual|permissions|role.*bundle|tenant.*permission" web-application/backend/test
- web-application/backend/test/mocha/function-tests/test-tenant-permissions.ts
Run/skipped results:
- <commands/results or local blocker with CI coverage expectation>
```

Do not mark `review-passed` until this gate is complete for every API/contract change. If the scan finds additional consumers, update legacy setup/fixtures as needed and rerun affected tests before review.

## Surface Verification Evidence

For broad packages, record verification by changed surface instead of only by command. Use this shape in state, work-package updates, and release handoff context:

```text
Changed surfaces:
- Permissions/roles: verified by <test/inspection> or skipped because <reason>
- Tenant isolation/ownership: verified by <test/inspection> or skipped because <reason>
- API/generated contract: verified by <test/inspection> or skipped because <reason>
- Persistence/schema: verified by <test/inspection> or skipped because <reason>
- Config/deployment: verified by <test/inspection> or skipped because <reason>
- Docs/orchestration: verified by <review/inspection> or skipped because <reason>
- Production compatibility: verified by <regression/backward compatibility/migration/rollback evidence> or intentionally relaxed because <prototype/approved rationale>
```

Omit unchanged surfaces. If a surface changed and no evidence exists, keep the package out of `review-passed` unless the gap is explicitly acceptable for the package risk and CI is expected to cover it.

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

Passing gate: Impact Scan complete when required, no actionable finding at or above threshold, no unresolved security/data/contract finding, tests pass or an acceptable verification gap is recorded, advisory findings recorded. For high-risk packages, this means the work-review loop is ready for the Security Sentinel Gate, not release handoff.

## Security Sentinel Gate

Run this gate after the main work-review loop passes and before `krt-release-marshal`.

Use the gate when the package or Impact Scan touches one or more of:

- auth, authorization, tenant isolation, ownership, permissions, roles, or scopes;
- secrets, credentials, tokens, env vars, CI/CD permissions, or deploy credentials;
- PII, regulated data, audit logs, retention, encryption, exports, or destructive actions;
- public API contracts, webhooks, callbacks, file upload/download, parsing, redirects, or external integrations;
- deployment exposure, Helm/Kubernetes/Docker security posture, public ingress, service accounts, RBAC, or network policy;
- dependency, package manager, base image, GitHub Action, generated client, or other supply-chain surface;
- any package classified high-risk where the primary review did not deeply inspect the security surface.

Prefer `krt-security-sentinel` as the specialized security reviewer when available. If it is not available, use another security-review skill or perform a direct evidence-based security pass with the same output expectations.

Security gate input:

- work package path;
- origin plan path;
- changed files/diff summary;
- Impact Scan summary;
- Security Watch notes collected during work;
- surface-aware verification evidence;
- current branch/base;
- known skipped tests or local blockers.

Security gate output:

```text
Security status: pass | fixes needed | blocked | advisory only
Blocking findings:
- [P0-P2] <title> -- evidence, remediation, verification
Advisory findings:
- [P3] <title>
Required verification:
- <tests/checks/manual review>
Release notes for handoff:
- <internal release-readiness notes only>
```

Routing:

- P0/P1 findings block release handoff.
- P2 findings block when they affect auth, tenant isolation, secrets, public API security, PII, deployment exposure, or supply chain.
- P3 findings are advisory unless the user or repo policy marks them blocking.
- Security blockers loop through `work`, targeted verification, and the main `code_review` role before rerunning the Security Sentinel Gate.
- Do not ask `krt-release-marshal` to hide, bypass, or explain away unresolved security risk.

## Optional Review Fan-Out

Keep the resolved `code_review` role as the primary review. Fan-out supplements it; it does not replace the main review, the lead's synthesis, or the post-review Security Sentinel Gate.

Use read-only reviewer fan-out inside the code-review loop when the package or Impact Scan touches one or more of:

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

## CI Break-Prevention And Escalation

Compound Master's CI responsibility is prevention first, escalation second.

Prevention rules:

- Before handoff, name the CI surfaces most likely to fail because of the package: build/typecheck/lint, unit/function/API tests, generated artifacts, migrations, permissions/auth/tenant tests, snapshots, and deployment/config checks.
- For each changed surface, record local verification or a concrete reason it is CI-only.
- For each affected CI job, identify the repo-specific local equivalent command from workflow/job definitions or documented scripts; use it as the release-readiness command when runnable.
- For auth/permission/tenant/contract changes, run the contract-drift test scan before release rather than waiting for CI to discover stale expectations.
- Pass CI risk notes to `krt-release-marshal` as internal release-readiness context, not PR-body noise.
- Do not poll PR checks repeatedly from Compound Master. The release workflow or user can surface broken checks.

Escalation rules:

- If the user reports a broken check, or the release workflow returns a failed check during its own process, invoke `krt-ci-questor` when available with the PR/run/check context.
- If `krt-ci-questor` is unavailable, search the host for another CI/log/check investigation skill or tool before falling back.
- If no specialist is available, Compound Master performs direct evidence-first triage itself using the same report shape. Do not stop just because the optional specialist is missing.
- The selected investigator, whether Questor, another skill, or Compound Master inline, owns the investigation report: cause, evidence, flake assessment, ownership, and next action.
- If the failure is package-owned, route the fix through a focused follow-up change on the PR branch using the normal release/gitflow context.
- Before pushing a package-owned CI fix, review neighboring tests/assertions and likely chained failures in the same affected area, then run the affected CI job's local equivalent command when runnable.
- If the failure is flaky, external, infra, or unknown, record a release-follow-up blocker instead of silently rerunning or bypassing.
- Do not disable checks, widen retries, bypass red CI, or mark Jira done without explicit user approval.

CI escalation report shape:

```text
CI incident: reported | investigating | fix-needed | external | unknown
Provider/run:
Workflow/job/step:
Likely reason:
Evidence:
- <log/check/artifact/history signal>
Ownership:
- package-owned | pre-existing | flaky/transient | external/infra | unknown
Recommended next action:
Verification:
Confidence:
```

State updates:

- `ci-prevention-ready`: predictable CI risk surfaces have evidence or explicit CI-only gaps.
- `ci-incident-reported`: a broken check was surfaced by the user or release workflow.
- `ci-incident-escalated`: `krt-ci-questor`, another resolved CI investigator, or Compound Master inline triage owns investigation.
- `ci-blocked`: failure is unknown, external, or needs user/project decision.
- `completed`: release handoff completed and no release-follow-up blocker is recorded by Compound Master.

## Release Marshal Handoff

When CI break-prevention evidence is recorded and implementation and review gates pass, invoke `krt-release-marshal`; do not duplicate its procedures and do not stop with "next step" when the role is available.

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
- Split broad packages by changed surface when applicable: persistence/schema/model state; domain service/integration behavior; API/controller/generated contracts; config/deployment wiring; focused tests/fixtures; docs/orchestration. Do not default to one implementation commit plus one docs commit for multi-surface feature work.
Verification results for release-readiness only, not PR body copy:
- <command/result>
Impact Scan for release-readiness only:
- <changed contracts/consumer tests summary or Not required>
CI risk notes for release-readiness only:
- <changed CI surface/local equivalent command/result or CI-only gap>

Use krt-release-marshal exactly. Do not run tests unless the user explicitly asks; use the verification results and CI risk notes above only to decide readiness. Do not include tests, verification summaries, or CI risk notes in the PR body unless the user, repo template, or project convention explicitly requires them. Include automatic reviewer handling in the release plan: use explicit reviewers if provided, otherwise infer a clear reviewer after PR creation and request review without asking a second time; skip reviewer assignment if no clear human reviewer exists. Include automatic post-PR Jira transition to En Revisión in the release plan when Jira context exists; after PR creation, use krt-jira-scribe and the real transition list to perform that approved transition without asking a second time.")
```

Suggested Jira summary/description, PR title/body bullets, branch name, suggested commit groups, and eventual commit messages must be semantic. Do not include roadmap IDs, U-IDs, package numbers, date sequences, or other Compound Master numbering unless the user or repo convention explicitly requires them.

PR tree safety:

- Independent PRs target integration/default branch.
- Stacked PRs target parent package branch and declare dependency in PR body.
- When the user asks to continue while a parent PR is pending merge, prefer the next ready package as a stacked PR from the parent PR branch when dependencies and review scope allow it.
- If stacked PRs are awkward but the next package can proceed, record the exact clean-tree strategy and intended `krt-rebase-smith` normalization path before starting work.
- Waiting for merge is a blocker only when the next package needs the merged artifact, the parent PR has unresolved release-follow-up blockers, or no clean branch/base strategy can be named.
- Do not retarget stacked PRs silently.
- Do not combine unrelated roadmap items unless grouped in one package.
- If an open PR exists for the branch, do not create a duplicate.
- If Jira is required and config is missing, stop with a configuration blocker.
- If Jira is optional and config is missing, let `krt-release-marshal` ask whether to continue without Jira.

After handoff, record Jira URL, PR URL, status, branch, base, reviewers, CI break-prevention evidence, blockers, and any stacked/clean-tree continuation strategy in state. Do not start a CI polling loop from Compound Master.
