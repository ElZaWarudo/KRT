# Compound Master Nesting

Use this reference when Seneschal starts, observes, resumes, or reconciles
multiple `krt-compound-master` flows.

## Topology

Treat Seneschal as the factory supervisor and each Compound Master run as an
independent quality pipeline:

```text
initiative contract
        |
        v
Seneschal queue
        |
        +-- Compound run A -> artifacts -> work/review/security gates
        +-- Compound run B -> artifacts -> work/review/security gates
        +-- Compound run C -> artifacts -> work/review/security gates
        |
        v
wave reconciliation -> krt-release-marshal
```

Do not reproduce Compound Master's artifact, implementation, review, security,
or CI-prevention procedures in Seneschal. Do not let a child Compound run
schedule sibling runs or perform release mutations.

## Root Discovery

For a new initiative:

1. Produce or reuse one requirements-only initiative contract through the
   resolved brainstorm role.
2. Review the initiative contract before deriving a roadmap.
3. Record global scope, non-goals, actors, terminology, success criteria,
   invariants, cross-cutting constraints, settled decisions, and open decisions.
4. Derive or review the roadmap from that contract.
5. Give each child Compound run the initiative contract, one roadmap item, its
   dependencies, shared decisions, artifact namespace, and state path.

Keep the initiative contract broad enough to govern all children without
pre-planning every local behavior. Each child still performs focused discovery
for its roadmap item when no reviewed item-level planning input exists.

## Artifact Authority

Assign one owner to each fact:

| Fact | Authority |
|---|---|
| Initiative intent and shared decisions | initiative contract or shared ADR |
| Item requirements, plans, work packages, and inner gates | child Compound run |
| Scheduling, concurrency, isolation, and cross-run dependencies | Seneschal |
| External release mutations | `krt-release-marshal` |

Treat Compound artifacts as canonical. Store only paths, observed status,
revision, and observation time in Seneschal state. Never copy their substantive
content into `docs/swarm/queue-state.yaml`.

While a child runs in an isolated worktree or cloud task, resolve its
repo-relative state path against that isolation root, not Seneschal's checkout.
After integration, reconcile the same path on the intended base.

## Child Invocation Contract

Nested Compound is a `deep`-lane route, not the default implementation route.
Before creating a child, apply `execution-lanes.md`. Use direct Spark or Luna
dispatch for execution-ready fast and standard units, and direct `luna_xhigh`
for a deep unit whose required artifacts and quality gates are already settled.
Create a child only when the deep unit still needs Compound Master's artifact or
multi-stage quality pipeline.

Give every child a stable envelope:

```yaml
orchestrator: seneschal
run_id: customer-identity-auth
state_path: docs/orchestration/compound-master/customer-identity-auth/state.md
interaction: brokered
initiative_contract: docs/plans/customer-identity/initiative-requirements.md
target:
  roadmap: docs/roadmaps/customer-identity/roadmap.md
  roadmap_item: RDM-001
  work_package: null
  review_unit: null
artifact_namespace: customer-identity/RDM-001-authentication
shared_decisions:
  - docs/architecture/decisions/ADR-012-tenant-isolation.md
depends_on: []
```

Use `mode:artifacts` or `mode:full` when the item still needs the Compound
artifact pipeline. Use `mode:execute package:<path> review-unit:<RU#>` only when
the deep unit explicitly requires Compound's remaining execution/review gates;
otherwise dispatch the execution-ready package directly. Keep shipping disabled
in the child.

Treat the selected mode as exact phase authority. Use `mode:artifacts` when only
planning is approved. Launch `mode:full` or `mode:execute` only after manual
wave-dispatch approval or applicable autonomous authority covers implementation.
A documentation approval alone does not silently authorize code mutation.

Set child `parallel:false` by default. Count every child that may mutate as one
Seneschal Implementer slot. Allow the child one mutating worker for its target
and bounded read-only specialists, but do not let it launch sibling Compound
flows or silently increase factory concurrency.

## Composition Gate

Treat Seneschal's documentation gate as a composition gate. It does not repeat
the child's document review.

Mark a child eligible for an artifact-planning wave when:

- its initiative contract is reviewed;
- its target roadmap item is stable enough for the selected phase;
- its invocation envelope, run ID, state path, and artifact namespace are fixed;
- dependencies and shared decisions are current;
- no open decision blocks the unit;
- isolation and concurrency are safe.
- the initiative contract, roadmap, and shared decisions are available at the
  same immutable revision in every child isolation target.

For an execution wave, additionally require the child artifacts to exist, the
active Compound state and work package to agree, and the relevant inner gate to
have passed. Require `package-review-passed` or `execution-ready`.
For release handoff, require all inner implementation, verification, review,
security, and CI-prevention gates.

## Shared Artifact Availability

Before parallel dispatch, prove that every worktree, cloud task, or branch can
read the same approved initiative contract, roadmap, and shared ADR revisions.
Prefer artifacts already present on the intended integration base. If they are
not on a shared revision, either:

- route creation of a stable local base through the repository's owning git
  workflow;
- provide a runtime-managed read-only artifact bundle with a content hash; or
- serialize work until the shared artifacts are available.

Do not have each child recreate or independently edit the same shared
artifacts. Record the shared revision in queue state and child envelopes.

## State Projection

Project child state into the queue without making it a second authority:

```yaml
compound:
  run_id: customer-identity-auth
  state_path: docs/orchestration/compound-master/customer-identity-auth/state.md
  interaction: brokered
  observed:
    status: execution-ready
    at: "2026-07-28T10:30:00Z"
    artifact_revision: "<git-object-or-content-hash>"
```

Refresh the projection before wave selection, after a child returns, after a
decision is resolved, and before release handoff. If the projection disagrees
with the canonical state, mark it stale and trust the canonical state after
reconciling it against repository reality.

## Decision Broker

In brokered interaction, child Compound runs never ask the user directly.
Require them to return a structured `decision_request` and pause only affected
work. Seneschal must:

1. Normalize the request into `docs/swarm/blockers.yaml`.
2. Deduplicate requests that ask for the same product or contract decision.
3. Merge conflicting child proposals into one decision surface.
4. Order questions by risk and number of units unblocked.
5. Ask the user one decision at a time in manual interactive flow.
6. Persist the answer in the canonical initiative contract, shared ADR,
   item-level planning input, or work package before resuming children.
7. Record the blocker resolution and refresh every affected child projection.
8. Refresh each affected isolation target to the recorded canonical revision.
9. Resume the original child when possible; otherwise start a replacement from
   the persisted state path and decision source.

In autonomous flow, do not ask. Record requests, block or defer affected work,
and continue independent units.

## Shared Decision Escalation

When a child proposes a change to shared architecture, auth, data, public
contracts, or cross-run dependencies:

- stop affected and dependent units;
- keep unrelated units running;
- promote the decision to the initiative contract or a shared ADR;
- identify every artifact invalidated by the decision;
- require affected Compound runs to refresh focused discovery, plans, packages,
  and gates before execution resumes.

Do not allow one child to silently redefine another child's foundation.

## Reconciliation Return

Require each child to return:

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

Use this return to update queue state. Inspect canonical artifacts and the real
diff before accepting the child's status.
