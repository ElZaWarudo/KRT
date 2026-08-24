# Execution Delegation

Load for wave planning, delegation decisions, and worker invocation.

## Wave Planning

Classify packages and review units:

- Independent: no hard dependency and no dangerous file overlap.
- Dependent: requires another package, branch, PR, schema, API, or merged change.
- Overlapping: touches files also touched by another package/review unit.
- High-risk: auth, security, payments, PII, migrations, public API, deployment, permissions, external APIs, shared contracts.
- Production-sensitive: `production:live` or `production:unknown` plus changes to existing behavior, persistence, API contracts, auth/tenant rules, deployment/config, migrations, data deletion, user workflows, or rollback expectations.

Rules:

- Prefer changing branches in the current checkout for serial work. Do not create a worktree just to move between review units or bases.
- With default `worktree-policy:avoid`, do not create worktrees/checkouts. If parallel execution would need them, downgrade to serial execution or ask for an explicit policy change.
- Independent review units may branch from the integration base.
- The first executable review unit should use a semantic capability branch, not a planning-only branch. If artifact generation happened on a docs/planning branch, switch back to a fresh integration base for RU1 and carry the related roadmap/brainstorm/plan/work-package/state artifacts on that first implementation branch.
- Dependent review units wait for merge or become stacked PRs based on parent branch.
- Overlapping/high-risk/production-sensitive review units run serially unless the user explicitly accepts risk and isolation exists.
- `parallel:true` with mutating workers requires `worktree-policy:auto|required`, isolated worktrees/checkouts, non-overlapping scopes, safe dependencies, and `autonomy:high`.
- Use worktrees/checkouts only when the worktree policy allows it and isolation is required for parallel mutation, overlapping branches, unsafe branch switching, or an explicit user/runtime isolation constraint.
- Without isolation, delegated workers must not stage, commit, push, create PRs, transition Jira, or run broad mutation-prone flows.
- Delegated workers never perform autonomous external mutation. They may produce implementation output and validator-ready facts; Release Marshal's executor owns PR, branch, reviewer, Jira, and merge side effects.

If execution has no `package:`, select the first unblocked package and first ready review unit from the earliest safe wave. If the package has no review units, derive them before execution using `artifact-templates.md`.

## Delegation Matrix

| Review-unit shape | Default choice |
|---|---|
| Small/same-file/tightly coupled | Run inline |
| Many files or uncertain conventions | Launch one read-only explorer |
| Clear scope, ownership, verification, autonomy contract, and no open decision | Launch at most one worker |
| Risky or fresh perspective needed | Use code review plus optional read-only fan-out |
| Independent, isolated, non-overlapping units | Parallel workers only with explicit safe mode |
| Ambiguous ownership, overlap, missing isolation, or product/branch decision | Run inline or stop for decision |
| Serial branch/base change | Switch branch in current checkout |
| Parallel work needs worktrees but `worktree-policy:avoid` is active | Run serially or ask for policy change |

## Autonomy Contract

Every work package/review unit should state:

- Agent may decide: reversible, package-local, convention-following choices.
- Agent must record: inferred conventions, low-risk path choices, skipped verification with blocker, compatible adjustments.
- Agent must escalate: product behavior, auth/tenant/data contract rules, public API compatibility, destructive persistence, production deployment/rollback, branch/base strategy, Jira/PR workflow, credentials, paid resources, or scope outside the review unit.
- Autonomous external mutation requires ledger linkage, validator pass, audit write, and Release Marshal executor handoff. Work agents cannot self-authorize it.

For a Seneschal-nested run, pass `run-id`, canonical `state-path`,
`initiative-contract`, and `interaction:brokered` to every mutating or planning
worker. Require decision requests in the parent return contract. Workers must
not ask the user directly or continue through a decision that changes inherited
product, architecture, auth, data, public-contract, security, or production
rules.

## Work Invocation

Before invoking work, verify the resolved `work` role supports implementation-only/no-shipping mode.

Compile one exact verification manifest into the worker contract:

```yaml
verification:
  focused:
    - <exact targeted command>
  natural:
    - <exact affected-suite command>
  aggregate_owner: root
  max_retries_per_command: 1
  baseline_failures: []
  stop_on_unowned_failure: true
```

Do not use phrases such as "appropriate checks" or "tests you can run". Empty
command lists are explicit. The worker may execute only the listed focused and
natural commands. Root runs aggregate or CI-equivalent verification once after
reconciliation. A Reviewer consumes the evidence and adds only a newly
identified risk-specific check through a revised manifest.

The terminal return accounts for every manifest command exactly once. Put an
executed command under `verification.attempted` with its attempt count and
outcome, or put an unexecuted command under `verification.skipped` with a
concrete reason. Repeat the exact command in `verification_commands_run` once
per actual invocation and in execution order. Root rejects omitted commands,
retries beyond the manifest limit, and a `last_required_command` that does not
match the last actual invocation.

When a command fails outside the worker's ownership, the worker records the
command, short evidence, ownership classification, and whether it matches a
declared baseline. With `stop_on_unowned_failure: true`, it returns immediately
after state reconciliation; it does not diagnose or fix the unrelated failure.

Prompt shape:

```text
Skill("<work>", "<work-package-path>

Review unit: <RU# and title>

Execution constraint: implement only the selected review unit and run only the exact focused and natural commands in the compiled verification manifest. Use the package autonomy contract: decide reversible, package-local, convention-following choices; record assumptions; escalate only non-inferable product, contract, security, production, branch/base, Jira/PR, credential, or scope decisions. Preserve the origin plan's implementation units: for each included U-ID/unit, report status, changed files, verification attempted/results/skips, and blockers. Do not implement later review units unless required to keep this unit coherent and explicitly recorded. Do not invoke PR creation, ce-commit-push-pr, Jira transitions, or any shipping workflow. Leave pending commits/changes for the lead and krt-release-marshal. Return changed files, API/contract changes detected, manifest verification results, skipped verification with reasons, decisions made autonomously, and structured decision requests. After the last required command and state reconciliation, return immediately. Do not ask the user to take over normal local verification or review.")
```

Under brokered interaction, replace free-form unresolved questions with
structured `decision_request` entries from `nested-orchestration.md` and return
them to Seneschal.

## Completion Gate

Mark a review unit implementation-complete only when:

- Expected files changed/created for the selected review unit.
- Each included plan unit has disposition: implemented, verified, skipped with reason, or blocked.
- Production posture evidence is satisfied or explicit gap/rationale is recorded.
- Impact Scan complete when required.
- Relevant tests run or no-test justification recorded.
- Consumer-derived tests from Impact Scan run or skipped with concrete blocker.
- Pending changes/commits are coherent for one review unit.
- No unresolved product decision remains.

After worker return, inspect summary/diff by review unit and plan unit, update state, collect Security Watch notes, run verification or closest targeted tests, fix straightforward failures inline or through work, and continue only when the selected review unit has a non-pending disposition.
