# Autonomous Team Flow

Use this reference for `overnight-team-flow`, `autonomous-team-flow`, or any user instruction equivalent to "do not ask for confirmation".

## Goal

Convert an ambitious delivery request into an unattended run:

```text
autonomy mandate -> complete task definition -> Jira/queue seed -> safe waves -> reconciliation -> release handoff -> morning packet
```

The core rule is no runtime interruption for decisions that can be encoded, deferred, or skipped. The swarm should wake the user with completed work, release-ready units, blockers, and exact remaining decisions.

## Autonomy Mandate

Before external or irreversible mutations, resolve an autonomy ledger under:

```text
docs/orchestration/autonomy-ledgers/
```

If the user explicitly requests no confirmations, create or reuse a run ledger that captures:

```yaml
schema_version: 1
run_id: swarm-overnight-YYYY-MM-DD
created_at: "YYYY-MM-DD"
user_mandate: "User asked for no human confirmation during this run."
mode: autonomous-team-flow
source_artifacts: []
allowed_mutation_classes:
  local_files: true
  local_branches: true
  local_commits: true
  jira_seed_create_update: true
  jira_comments: true
  jira_pr_backlinks: true
  jira_transitions_to_review: true
  push_branches: true
  create_or_update_prs: true
  request_reviewers: true
  merge_prs: true
deny_rules:
  - do_not_commit_secrets
  - do_not_bypass_failing_required_checks
  - do_not_merge_without_platform_eligibility
  - do_not_ship_high_risk_compliance_without_resolution
risk_policy:
  product: decide_from_artifacts_else_block_unit
  auth: block_dependents_if_foundational
  data: block_dependents_if_foundational
  DIAN: high_risk_blocker_before_production
  accounting: high_risk_blocker_before_production
  payroll: high_risk_blocker_before_production
  security: high_risk_blocker_before_production
fallback_policy:
  no_ready_work: close_with_blocker_review
  failed_verification: mark_needs_fix_and_dispatch_fixer_if_safe
  scope_creep: mark_split_required
  missing_external_authority: skip_mutation_record_blocker_continue
audit:
  append_only_log: docs/orchestration/autonomy-ledgers/swarm-overnight-YYYY-MM-DD.audit.md
```

The ledger is the replacement for per-action human confirmation. It does not remove quality gates; it defines what the agent may do after gates pass.

## Task Definition First

For overnight work, spend the first phase making work executable:

- Dispatch Planner workers for broad epics, roadmap sections, and Jira parent issues before Implementer workers run.
- Parse the roadmap/backlog into the smallest useful work packages.
- Create or update the Jira issue map.
- Identify acceptance criteria and verification for every unit.
- Detect dependencies before dispatch.
- Detect overlapping surfaces before dispatch.
- Pre-classify high-risk areas: auth, data, public contracts, migrations, central models, lockfiles, DIAN, accounting, payroll, security.
- Write unclear decisions to the blocker ledger instead of asking immediately.

If task definition is weak, do not improvise a broad platform. Create the backlog map, seed what can be seeded, implement independent foundations, and leave blocked units explicit.

## No-Interruption Rules

During autonomous execution:

- Do not ask the user for confirmation.
- Do not stop because one unit is blocked.
- Do not stop because one external mutation class is not ledger-covered.
- Do not stop because one worker needs product/legal/accounting/security input.
- Record blockers, defer affected units, and continue independent work.
- Dispatch fixers for bounded verification or review failures when surfaces remain isolated.
- Dispatch Integrator workers before release handoff when two or more units may interact through dependencies, stack order, contracts, migrations, lockfiles, or shared generated artifacts.
- Split broad or scope-creeping work instead of forcing one large PR.

Stop only when no independent ready work remains or when every remaining path would violate the ledger deny rules.

## External Mutations

The seneschal still does not directly own release side effects:

- Jira Cloud mutations go through `krt-jira-cloud-scribe`.
- Commits, pushes, PRs, reviewer requests, Jira PR backlinks, transitions, and merge flow go through `krt-release-marshal`.

In autonomous flow, pass the ledger path to those skills and instruct them to use their autonomous executors/validators where available. If a downstream skill cannot execute a covered mutation autonomously, record the limitation as a blocker or handoff gap and continue other work.

Merge PRs only when the ledger explicitly allows merge and platform-visible merge eligibility is satisfied. A user's "no confirmations" preference authorizes unattended work; it does not authorize bypassing branch protection, failing checks, missing credentials, or unsafe production compliance.

## Morning Packet

End an unattended run with:

```text
Autonomous run: <run id>
Source backlog: <paths/Jira filters>
Completed locally:
- <unit>
Release-ready:
- <unit> -> <release handoff/PR if created>
Needs fix:
- <unit>: <reason>
Blocked/deferred:
- <blocker id>: <decision needed>
Jira seed/drain:
- created/reused/updated/skipped counts
Verification:
- <command/result>
Review gates:
- <result>
Autonomy ledger:
- <path>
Queue state:
- docs/swarm/queue-state.yaml
Blocker ledger:
- docs/swarm/blockers.yaml
Next best action:
- <single highest-leverage unblock>
```
