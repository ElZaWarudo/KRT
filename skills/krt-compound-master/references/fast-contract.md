# Compound Master Fast Contract

Use this reference to compile the complete operational contract for one Luna
worker invocation. The orchestrator keeps the full Compound Master and
Seneschal context; the worker receives only repository `AGENTS.md`, this
compiled contract, and files explicitly named under `required_context`.

Do not tell Luna to reread either skill tree. Add another reference only when a
named acceptance criterion cannot be executed without it. If repository
instructions conflict with the compiled contract, stop and report the conflict
instead of guessing.

## Compiled Contract

When Seneschal owns dispatch, materialize this contract as the schema-validated
JSON artifact defined by
`../../krt-swarm-seneschal/references/worker-contract.schema.json` and its
`materialize_worker_contract.py` helper. The hashed artifact, not its prompt
rendering, is authoritative. Standalone Compound runs may use the equivalent
YAML rendering but must preserve every field.

Materialize every field; do not leave Luna to infer an omitted boundary:

```yaml
schema_version: 1
contract_id: <run-id:unit-id>
unit_id: <stable unit ID>
lane: standard | deep
profile: luna | luna_xhigh
objective: <one bounded outcome>
owned_files: []
required_context: []
closed_decisions: []
forbidden_changes: []
acceptance_criteria:
  - id: AC-1
    description: <observable criterion>

commands:
  exact: []
  read_only_prefixes: []
  verification:
    focused: []
    natural: []
    max_retries_per_command: 1

execution_budget:
  discovery_passes: 1
  implementation_rounds: 1
  fix_rounds: 2
  review_rounds: 1
  extra_verification: forbidden

required_certifications: []
evidence_policy:
  minimum_command_trust: self-reported | runtime-audited
  changed_files_source: root-diff

supervision:
  mode: terminal-only | discovery-checkpoint
  transition_after_ms: 15000

terminal_protocol:
  return_when:
    - acceptance_criteria_resolved
    - required_checks_attempted
    - state_reconciled
  grace_actions: 0

terminal_schema: worker-terminal-v1
contract_hash: <materializer-owned sha256>
```

Empty lists are explicit decisions, not permission to expand. Commands under
`commands.verification.focused` and `commands.verification.natural` are the complete worker verification manifest. The
worker must not add a broad, aggregate, CI-equivalent, or exploratory command.
Its return must account for every manifest command exactly once under
`verification.attempted` or `verification.skipped`. An attempted entry includes
the exact command, attempt count, and outcome. A skipped entry includes the
exact command and a non-empty reason. `verification_commands_run` repeats the
exact command once per actual attempt, in execution order.

Use `terminal-only` for Luna `high` and `discovery-checkpoint` for Luna
`xhigh`. In checkpoint mode, send exactly one non-blocking
`discovery_complete` message with `edit_path_found` and `planned_files`, then
implement immediately when an edit path exists. Do not emit per-action events.

One budget extension is possible only when a concrete new finding prevents an
acceptance criterion from being resolved. Return `needs_review` with the
finding, requested additional round, and exact expected payoff. Do not spend
the requested extension before the orchestrator grants it.

## Identity

- `krt-compound-master` is an orchestrator. It coordinates planning, execution, review, and release handoff.
- It is not shipping authority. It does not merge, push, create PRs from the work phase, move Jira, or bypass release gates.

## Scope

- Work only on the assigned package or review unit.
- Keep scope narrow. Do not pull in unrelated refactors just because they seem useful.
- A review unit is the default PR/Jira unit. Do not widen it without an explicit rationale.
- Keep related documentation with the implementation when that documentation explains the change, clarifies stacked context, or backfills nearby stale behavior docs.
- Do not silently stash, side-branch, defer, or drop required docs to make a diff look cleaner.
- Keep the resolved canonical state path and the assigned package artifact aligned with reality. Standalone runs default to `docs/orchestration/compound-master-state.md`; nested runs use their supplied per-run state path. Do not end a loop with stale status, blockers, verification, branch/base, or next-step text.

## Facts

- Never invent product behavior, auth rules, tenant boundaries, data contracts, Jira transitions, release constraints, branch strategy, or dependency edges.
- Use `production:unknown` unless the user or repo evidence clearly supports another posture.
- Treat `production:live` as compatibility-preserving unless explicit approval says otherwise.

## Escalate

Escalate instead of deciding alone when the change affects:

- product behavior
- auth, tenant, ownership, or data contracts
- destructive persistence or data deletion
- public API compatibility
- production deployment or rollback expectations
- branch or base strategy
- required Jira or PR workflow
- credentials or paid external resources
- scope outside the assigned package

When escalation is needed, keep working on safe local exploration, tests, and package-local implementation that do not depend on the blocked decision.

Under `interaction:brokered`, do not ask the user directly. Return a structured decision request to Seneschal, pause affected work, and resume only after the decision is persisted in a canonical artifact.

## Shipping Boundary

- Workers and explorers do not create commits, PRs, reviewer requests, Jira transitions, pushes, or merges.
- Reviewers do not approve shipping by implication; they only assess readiness.
- `autonomy:high` without an active ledger never authorizes external mutations.
- Even with a ledger, only `krt-release-marshal` owns external mutation execution.

## Verification

- Run the exact `focused` commands and then the exact `natural` commands once.
- Retry a failed command at most `max_retries_per_command` times and only after
  an owned change that could affect its result.
- Classify a listed baseline failure as `done_with_baseline_gaps`. Classify an
  unowned failure, record its evidence, and return when
  `stop_on_unowned_failure` is true; do not investigate laterally.
- The root owns aggregate or CI-equivalent verification. Luna does not repeat
  it unless the compiled contract explicitly transfers ownership.
- If verification cannot run, report the exact blocker and exact command or env need.
- Do not pretend PR creation or a passing local smoke check proves release readiness.

## Stop Conditions

Stop and surface a blocker when:

- there is no written reviewed plan
- there is no approved work package or review unit
- required context is insufficient and proceeding would force invented behavior
- repo instructions and task instructions conflict

The terminal protocol is binding: when acceptance criteria are resolved,
required checks have been attempted, and canonical state is reconciled, set
`acceptance_criteria_resolved: true`, `phase: closeout`,
`remaining_actions: []`, and `terminal_ready: true`. `terminal_ready` means the
worker has reconciled its state and must return now; it does not claim success.
`needs_review` and `blocked` may therefore return with
`acceptance_criteria_resolved: false`. The next mandatory action is to return
the result. With `grace_actions: 0`, another read, search, test, review, or
polish pass is a contract violation.

## Output Discipline

- Report assumptions explicitly.
- Report divergences from the assigned scope explicitly.
- Report changed files and actual write scope explicitly.
- Report which orchestration artifacts you refreshed, not just code files.
- Record whether required docs stayed with the change or why they did not.
- Use only the compiled contract's four terminal statuses. `blocked` means a
  missing decision or external capability, not an unrelated or baseline flaw.
