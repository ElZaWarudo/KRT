# Subagent Contracts

Use this reference when launching subagents or preparing prompts for separate Codex threads.

## Worker Envelope

Every worker prompt must contain:

```text
Role: <role>
Worker profile: <registered profile ID or runtime-default>
Model class: <declared class or runtime-default>
Unit execution lane: <fast|standard|deep|not-applicable>
Reasoning effort: <high|xhigh>
Lane trigger: <deterministic admission reason>
Profile source: <project-agent|user-agent|runtime-default>
Unit: <id and title>
Executable contract: <repo-relative worker-contract.json path>
Contract hash: <sha256:...>
Jira issue: <subtask or standalone issue key, when applicable>
Source artifact: <path or issue URL>
Intended base: <branch/ref>
Isolation target: <branch/worktree/cloud task>
Scope included:
- ...
Scope excluded:
- ...
Acceptance criteria:
- ...
Verification commands:
- focused: <exact leaf commands>
- natural: <exact affected-suite commands or []>
- aggregate_owner: root
- max_retries_per_command: 1
- baseline_failures: []
- stop_on_unowned_failure: true
Command evidence:
- minimum_trust: <self-reported|runtime-audited>
- exact_commands: []
- read_only_prefixes: []
Wave verification owner: Seneschal/root
Execution budget:
- discovery_passes: 1
- implementation_rounds: 1
- fix_rounds: 2
- review_rounds: 1
- extra_verification: forbidden
- max_elapsed_ms: <role-sized positive deadline>
Terminal protocol:
- return_when: acceptance criteria resolved, required checks attempted, state reconciled
- grace_actions: 0
Supervision:
- mode: <terminal-only|read-only-discovery|manifested-implementation>
- accepted_checkpoint: <none|structured discovery_complete payload>
Required skills:
- ...
Forbidden actions:
- ...
Return contract:
- Return exactly the validated JSON object from `worker-terminal.schema.json`.
- Run the contract-bound `validate_worker_terminal.py` command immediately
  before returning it.
```

Pass artifact paths and repo-relative paths. Avoid flooding workers with the entire queue.
The prompt is not the authority. First materialize and validate the executable
artifact through `executable-worker-contracts.md`; render this envelope from
that immutable artifact and require the worker to echo its hash.

For Luna, compile this envelope using
`krt-compound-master/references/fast-contract.md`. The compiled envelope is the
only operational contract Luna loads besides repository `AGENTS.md` and the
files named in `required_context`. Do not send the worker back through the
Seneschal or Compound Master reference trees. Empty lists must be explicit.
Use `terminal-only` for `luna`. Deep units first use `read-only-discovery` with
`luna_xhigh_discovery`, then `manifested-implementation` with `luna_xhigh` only
after root accepts the terminal checkpoint.

When `Worker profile` names a registered Codex profile, load
`worker-profiles.md` and pass its static preflight before launching the worker.
The worker envelope remains mandatory: a profile supplies stable runtime
behavior, not the unit-specific contract.

Load `execution-lanes.md` before composing the envelope. Its implementation
mapping is fixed: `fast` -> `spark`/`xhigh`, `standard` -> `luna`/`high`, and
`deep` -> `luna_xhigh_discovery` then `luna_xhigh`, both at `xhigh`. Spark
remains `xhigh` and receives only decision-closed contracts. Supporting roles
use Luna `high` normally and Luna `xhigh` only when their own bounded task has a
deep trigger.

Set a short elapsed limit proportional to the literal assignment, not the
worker profile. Ordinary review, mechanical fixing, and targeted validation
stay at Luna `high`; reserve Luna `xhigh` for security, concurrency, auth/data,
public-contract, or similarly demanding decisions. Root interrupts at the
limit or earlier when the worker repeats settled discovery, runs an undeclared
check, or has enough evidence to satisfy its return contract. If only a small
deterministic validation remains and root can finish it faster than another
dispatch interval, interrupt and execute it at root.

## Standard Roles

Use the Implementer as the default role and add only triggered support:

```text
Planner when needed -> Implementer -> Reviewer/Fixer when triggered -> Integrator/Documenter when triggered
```

Not every unit needs every role. The seneschal chooses the smallest role chain that preserves quality gates.
Start with the Implementer and add no optional role without its admission
trigger from `execution-lanes.md`. Record the trigger in the wave plan and
worker envelope.

Security and CI/platform specialists are functional capacity roles rather than
default implementation-chain stages. Admit Security only from the existing
security gate trigger. Admit CI/platform only for a concrete failing pipeline,
runner, dependency, or environment investigation; it diagnoses without
expanding the implementation unit. Both consume the global slot budget in
`parallel-dispatch-policy.md`.

### Planner

Use only when broad or ambiguous work still needs decomposition, acceptance
criteria, dependency mapping, or decision closure. Do not use it for an
execution-ready package.

```text
Decompose only the provided epic/backlog item into small executable queue units.
For each unit return scope, non-goals, acceptance criteria, dependencies, touched surfaces, risk flags, verification commands, and suggested Jira shape.
Do not implement code.
Do not mutate Jira, commit, push, open PRs, request reviewers, merge, or transition issues.
Return units small enough for one Implementer and one focused PR unless grouping is explicitly justified.
```

### Compound Master Worker

Use `compound-master-nesting.md`. A Compound worker may own one roadmap item
through the full artifact and quality pipeline, or one existing work
package/review unit during execution. Always limit it to one assigned target.

Use only for a `deep` unit whose required Compound artifact or quality pipeline
is incomplete. An execution-ready package/review unit is not sufficient reason
to nest Compound Master; route it directly to the selected Luna profile.

```text
Use krt-compound-master for only the assigned target.

Mode: <artifacts|full|execute|resume>
Parallel: false
Orchestrator: seneschal
Run ID: <stable-id>
State path: docs/orchestration/compound-master/<run-id>/state.md
Interaction: brokered
Initiative contract: <requirements-only artifact path>
Target roadmap item: <RDM# or none>
Package: <work-package-path or none>
Review unit: <RU# or none>
Artifact namespace: <initiative/item namespace>
Shared decisions: <paths>
Parallel context: this worker owns only this unit.
Shipping: artifact-only or implementation-only/no-shipping as assigned.
Do not rerun the general initiative brainstorm.
Run focused item discovery only when no reviewed item planning input exists.
Do not ask the user directly. Return structured decision requests and pause
only affected work.
Do not commit, push, open PRs, mutate Jira, request reviewers, or merge.
Return: run ID, canonical state, artifact paths, observed revision, changed
files, commands run, inner gates, decision requests, affected sibling units,
branch/base facts, release readiness, and recommended resume invocation.
```

### Implementer

Use when the unit is execution-ready. Select Spark only for `fast`, Luna `high`
for `standard`, and Luna `xhigh` for `deep`.

```text
Implement only the described unit.
Follow AGENTS.md and local skill rules.
Do not change public contracts, auth/data behavior, dependencies, or release configuration outside scope without stopping.
Add or update tests when the unit changes behavior.
Return only the exact validated `worker-terminal.schema.json` object. Root adds
the real changed files, command evidence, risks, and blockers during
reconciliation.
After the last required command and state update, return immediately. Do not add
an exploratory, aggregate, or confidence-building verification pass.
Do not commit, push, open PRs, mutate Jira, request reviewers, or merge.
```

For a deep unit, first launch `luna_xhigh_discovery` under its read-only profile.
It returns exactly one terminal checkpoint after the single discovery pass:

```yaml
event: discovery_complete
edit_path_found: true | false
planned_files: []
evidence_digest: brief concrete evidence
```

The checkpoint is closed to extra fields. Discovery narrows multi-file
ownership and justifies every planned edit with an
`edit <repo-relative-path> | symbol=<name>, pattern=<pattern>, or
callers=<evidence>; why=<reason>` line in
`evidence_digest`; it separates read-only dependencies and contingencies there.
For CRITICAL hubs, it prefers an additive path or gives symbol-level impact
evidence. Root validates the checkpoint and, when the edit path exists, immediately
launches a fresh `luna_xhigh` with the checkpoint attached and editable
ownership narrowed to `planned_files`. The implementation worker does not repeat
discovery or send a checkpoint. If another file is required, it returns
`needs_review` with `scope_extension.additional_files` and a concrete reason
without editing that file. If discovery reports no edit path, reconcile
`needs_review` without launching implementation. No profile emits per-read,
per-edit, or per-command events.

### Reviewer

Use only when behavior/control flow changed, risk is elevated, a sensitive or
public contract surface changed, acceptance requires independent review, or the
diff exceeds the narrow mechanical lane. Do not add a Reviewer to pure
formatting, generated refreshes, or decision-closed docs-only edits by default.

```text
Review the diff against the unit contract.
Prioritize functional bugs, scope creep, missing tests, regressions, security risk, and architecture violations.
Report findings as P0/P1/P2 with file/line evidence.
Do not rewrite the implementation unless explicitly asked to fix.
```

For a coordinated multi-surface review, load `review-coordination.md` and give
the reviewer one compiled surface assignment. Require the exact terminal
accepted by `validate_review_terminal.py`. Every assigned risk boundary must be
checked. P0/P1 findings are uncapped; return at most three evidence-backed P2
findings and suppress speculative preferences.

On recertification, give the reviewer the latest diff digest, registry state,
and changed finding surfaces. Recheck affected risk boundaries without
rediscovering already resolved findings or rereading unchanged surfaces.

### Targeted Validator

Use only after the root-owned registry assigns canonical IDs and the compiled
review plan requires a validation wave. This is a bounded Reviewer or Security
Sentinel assignment, not a new standing role.

```text
Validate only the supplied canonical finding IDs against the bound contract and
root-observed diff. For each return confirmed, revised, or rejected with
evidence. Do not repeat open-ended review. You may report a newly observed P0 or
P1 encountered during reproduction, but do not expand the batch with a new P2.
Do not edit implementation files or the shared findings registry.
Return immediately after every supplied ID has one evidence-backed verdict.
Do not broaden reproduction into coverage review, and do not continue after
the elapsed limit; root may finish a small remaining deterministic validation.
```

### Fixer

Use only for concrete bounded review findings or verification failures.

```text
Fix only the listed canonical findings from one defect cluster.
Edit only the exact owned paths and do not perform additional review.
Do not opportunistically refactor.
Run only the exact narrow verification named in the assignment.
Return only the canonical finding-ID-to-change mapping, including every
assigned ID, changed paths, and its focused command accounting.
Return immediately after the mapping is complete; do not add a confidence pass.
Do not commit, push, open PRs, mutate Jira, request reviewers, or merge.
```

Root rejects a Fixer return that uses headings or a generic completion report,
omits an assigned ID, combines unrelated defects, names an unowned path, or
lacks assigned focused-command accounting. Materialize the closed assignment
with `contract_hash`, `registry_digest`, `finding_ids`, `owned_paths`, and
`verification_commands`, then require the Fixer to run:

```bash
rtk python3 <seneschal-skill-dir>/scripts/validate_fixer_terminal.py \
  --assignment <fixer-assignment.json> \
  --input <fixer-terminal.json>
```

It returns the exact JSON object that passed. Correct protocol-only shape errors
in the same Fixer session; do not infer the mapping at root. Root reruns the
validator and independently captures the assigned command results before
resolving findings.

### Integrator

Use only when at least two units have dependencies, shared surfaces, generated
outputs, stack/merge choreography, or a cross-unit compatibility question.

```text
Inspect dependency order, merge order, stack shape, branch/base facts, conflicting surfaces, generated artifacts, lockfiles, API contracts, migrations, and Jira grouping.
Recommend standalone, grouped, or stacked PR handoff.
Identify conflicts, stale bases, missing downstream refreshes, and units that must wait.
Do not implement broad changes. Do not commit, push, open PRs, mutate Jira, request reviewers, transition issues, or merge.
Return release sequencing, conflict findings, and handoff notes for krt-release-marshal.
```

### Documenter

Use when documentation is explicitly in scope or changed behavior makes a
maintained user, developer, API, changelog, or release document inaccurate.

```text
Update only the documentation surfaces named in the unit.
Keep repo terminology and KRT skill naming canonical.
Do not change implementation unless the unit explicitly includes it.
Return changed docs and any verification performed.
```

## Return Contract

Implementation workers return exactly one JSON object matching
`worker-terminal.schema.json`. Do not ask them to translate it into a prose or
YAML report. Use the schema's field names and nesting literally; every required
array is present even when empty. In particular, `phase` is always `closeout`
and `unowned_failures` is always present.

Before return, require the contract-bound command from
`executable-worker-contracts.md`. The worker writes its candidate terminal to
the unique `/tmp` path in that command, runs the validator, corrects only
validator-reported protocol errors when necessary, reruns it, and returns the
exact JSON that passed. The passing validator invocation is the final observed
command. The root later attaches the contract hash, worker identity,
root-observed changed files, command evidence, and independent certificates to
the authoritative observation; those root-owned fields do not belong in the
terminal object.

Planner, Reviewer, Fixer, Integrator, Documenter, Security, and nested Compound
Master workers retain the role-specific returns defined above; they do not
pretend to be implementation terminals. A brokered nested Compound return must
include:

```text
Decision requests:
- question: <single decision>
  why_not_inferable: <missing authority or evidence>
  affected_units: []
  options: []
  recommendation: <option or none>
  safe_fallback: <pause/defer behavior>
  canonical_target: <shared or item artifact path>
  evidence: <paths/output/links>
```

Status meanings are strict:

- `done`: every required criterion and check is resolved.
- `done_with_baseline_gaps`: only declared baseline or clearly unowned gaps remain.
- `needs_review`: the allowed implementation, fix, or review rounds are exhausted,
  or the worker requests its single justified budget extension.
- `blocked`: a decision or external capability is required.

When `terminal_ready: true` and `remaining_actions: []`, the worker must return
without another action. The orchestrator treats further exploration or
verification as a contract violation. `terminal_ready` means ready to return;
`acceptance_criteria_resolved` separately records whether the owned criteria
were satisfied. It must be true for `done` and `done_with_baseline_gaps`, but
may be false for `needs_review` and `blocked`.

If a worker omits the return contract or pre-return validation evidence,
inspect the diff before trusting its status.
An omitted or mismatched contract hash, incomplete acceptance evidence, command
outside the executable contract, or root-observed changed file outside
`owned_files` is a contract violation. Preserve the changes but do not count the
terminal, tests, or status as readiness evidence.

If a blocker affects only the worker's unit, the orchestrator records it and continues with independent units. If it affects security, DIAN, accounting, payroll, auth, data, public contracts, or shared foundations, the orchestrator stops dependent dispatch and records a high-risk blocker.

## Parallel Safety

Launch in parallel only when:

- each worker has isolated filesystem state
- each worker has a distinct branch or cloud task
- dependency edges are absent or already merged
- changed surfaces are non-overlapping
- the factory can reconcile all outputs before release handoff
- no open blocker affects a selected unit or its dependencies

If any condition is missing, serialize.
