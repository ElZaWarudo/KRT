# Nested Orchestration

Use this reference when `krt-compound-master` runs as a child of
`krt-swarm-seneschal`.

## Invocation

Accept these optional arguments:

- `orchestrator:standalone|seneschal`: default `standalone`.
- `run-id:<stable-id>`: required when `orchestrator:seneschal`.
- `state-path:<repo-relative-path>`: required when `orchestrator:seneschal`.
- `initiative-contract:<repo-relative-path>`: shared requirements-only product
  contract inherited by the run.
- `interaction:direct|brokered`: default `direct`; require `brokered` under
  Seneschal.

For a nested run, require a target roadmap item, work package, or review unit.
Do not choose unrelated backlog work.

Default to `parallel:false`. Seneschal owns cross-flow concurrency and counts
this run as one mutable slot. Use at most one mutating worker for the assigned
target; bounded read-only specialists remain allowed. Do not launch sibling
Compound flows.

## State Isolation

Use the supplied state path as the only live resume truth for the run:

```text
docs/orchestration/compound-master/<run-id>/state.md
```

Keep standard standalone behavior backward compatible:

```text
docs/orchestration/compound-master-state.md
```

Never let two active runs write the same state file. Treat any repository-level
Compound state index as a directory or pointer only; do not store mutable child
progress there.

Track the parent orchestrator, run ID, interaction mode, initiative contract,
target roadmap item, artifact namespace, and last parent decision applied in
the child state.

## Inherited Product Contract

Read the initiative contract before focused discovery. Treat settled global
decisions, invariants, terminology, non-goals, and escalation boundaries as
binding. A child may refine item-local behavior but must not contradict or
silently rewrite shared decisions.

Reuse the reviewed roadmap and assigned item from Seneschal. Do not invoke the
roadmap generator to create a competing program roadmap. Validate inherited
dependencies and return any conflict through the decision broker.

If the child needs a shared decision changed, return a decision request and
mark affected work blocked. Do not edit the global contract unless Seneschal
assigns this run ownership of that update.

## Brainstorm And Planning Inputs

Resolve brainstorm outputs by artifact metadata, not directory name. Accept a
requirements artifact anywhere under the configured docs root when it declares:

```yaml
artifact_contract: ce-unified-plan/v1
artifact_readiness: requirements-only
product_contract_source: ce-brainstorm
```

Support legacy `docs/brainstorms/**` inputs. New `ce-brainstorm` artifacts may
live under `docs/plans/**`. `brainstorm_path` and `planning_input_path` may point
to the same unified artifact.

Perform focused discovery for the assigned roadmap item when no reviewed
item-level planning input exists. Do not rerun the initiative brainstorm.
Reuse an existing reviewed item-level artifact on execute or resume.

## Brokered Interaction

When `interaction:brokered`:

- do not ask the user directly;
- search inherited contracts, shared decisions, item artifacts, repository
  evidence, and recorded resolutions first;
- decide reversible, package-local, convention-following choices under the
  work package autonomy contract and record the assumption;
- emit a structured decision request for product, auth, data, public contract,
  security, production, branch/base, Jira/PR, credential, or scope decisions;
- pause only the affected item or review unit;
- continue safe local work that does not depend on the decision;
- return control to Seneschal.

Use this shape:

```yaml
decision_request:
  id: null
  type: product
  question: Should password changes revoke existing sessions?
  why_not_inferable: The inherited contract does not define session validity.
  affected_units: [authentication-RU1, session-management-RU2]
  options:
    - id: revoke-all
      consequence: Stronger security; signs out every device.
    - id: keep-existing
      consequence: Less friction; existing sessions remain valid.
  recommendation: revoke-all
  safe_fallback: Block affected units.
  canonical_target: docs/plans/customer-identity/initiative-requirements.md
  evidence:
    - docs/plans/customer-identity/initiative-requirements.md
```

Seneschal assigns the durable decision ID, deduplicates it, asks the user when
policy permits, and persists the answer. Resume only from the canonical answer,
not from an unrecorded parent message.

## Resume After Decision

On resume:

1. Read the canonical decision artifact and the supplied decision ID.
2. Record the decision source and revision in child state.
3. Revalidate affected brainstorm, planning, package, and execution gates.
4. Update stale artifacts before continuing.
5. Report any sibling or shared contract impact to Seneschal.

## Parent Return Contract

Return:

```text
Run ID:
Canonical state:
Status:
Artifact paths:
Observed revision:
Changed files:
Verification:
Inner gates:
Decision requests:
Affected sibling units:
Release readiness:
Recommended resume invocation:
```

Do not commit, push, create or update PRs, mutate Jira, request reviewers,
transition issues, or merge. Seneschal owns scheduling and reconciliation;
`krt-release-marshal` owns release mutations.

Do not invoke `krt-release-marshal` directly from the child. Return the
release-ready packet to Seneschal so it can reconcile sibling outputs,
conflicts, dependencies, and shared revisions before choosing release order.
