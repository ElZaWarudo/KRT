# Queue And Dispatch

Use this reference to normalize source work, decide readiness, and plan the
smallest safe wave. Load `queue-state-schema.md` only when persistent state is
actually needed.

## Unit Minimum

Every candidate unit needs:

- stable ID, title, and source;
- included and excluded scope;
- checkable acceptance criteria;
- dependencies and blockers;
- writable and read-only surfaces;
- intended base and isolation need;
- exact focused verification or a justified gap;
- execution lane and its trigger;
- assurance tier and its trigger;
- contract protocol: `lightweight`, `executable`, or `root-direct`;
- optional Jira key and resolved provider; and
- release-handoff notes when already known.

Reuse existing work-package or review-unit IDs. Do not invent a second planning
taxonomy. The canonical persisted shape is in `queue-state-schema.md`.

## Ready Criteria

A unit is ready only when:

- its scope, non-goals, acceptance, and verification are settled;
- dependencies are merged or explicitly supplied on the intended base;
- no unresolved product, auth, data, deployment, or public-contract decision
  blocks the proposed implementation;
- ownership does not overlap another active mutable unit;
- no open blocker affects the unit or its dependencies;
- execution lane, assurance, protocol, and triggered roles are recorded;
- the required isolation can be created; and
- live Jira facts have been read through the selected Jira provider skill when
  Jira is the source.

An applicable documentation gate must be approved for a rough initiative,
roadmap, program, unrefined backlog, or Jira seed/drain. Do not manufacture a
new gate for an explicitly requested execution-ready unit. If that unit needs
persistent queue state, record the validated unit-scoped exemption from
`queue-state-schema.md`; never use it for work derived from gate-required source.

For a nested Compound unit, also require a unique run ID and state path, a fresh
observed projection, and the relevant inner gate. The child state remains
authoritative.

## Break-Even And Classification

Load `execution-lanes.md` and apply its break-even gate before forming a wave.
Keep one small low-assurance unit root-direct. For dispatched work, record:

```text
lane / profile / reasoning / lane trigger
assurance / review mode / assurance trigger
contract protocol / admitted roles and their triggers
```

Use `lightweight-dispatch.md` only for eligible interactive fast/standard
low/medium work. Deep, high, critical, autonomous, or policy-mandated work uses
`executable-worker-contracts.md`.

## Dependencies And Coupling

Select only dependency-ready units. When a broad parent is coupled through a
small shared interface, load `staged-decomposition.md`:

1. Run the smallest testable foundation alone.
2. Freeze its accepted baseline.
3. Fan out only dependency-ready children with disjoint ownership.
4. Reconcile every child before integration and aggregate verification.

If the topology compiler rejects the split, record the guardrail and serialize
the parent. A changed foundation invalidates undispatched or active dependent
bases.

## Wave Selection

Start with the smallest useful wave:

- Default to one mutable implementer for an uncertain queue.
- Default to at most two when units are independent, isolated, verifiable, and
  the review queue can absorb them.
- Raise above two only from green observed history plus explicit scale authority
  in manual flow or an exact autonomy-ledger grant.
- Count Planner, Reviewer, Fixer, Integrator, Documenter, Security, and nested
  Compound roles against their separate capacity and the global slot budget.

Load `parallel-dispatch-policy.md` and `automated-wave-control.md` only when
adaptive allocation or concurrency above the basic cap is needed.

Treat these surfaces as conflicting unless concrete evidence proves otherwise:

- auth or permission paths;
- schemas, migrations, transactions, or central data models;
- public APIs, events, generated contracts, or compatibility layers;
- dependency manifests, build configuration, or lockfiles; and
- the same central orchestration or generated file.

Docs may run concurrently only with distinct ownership. A stable foundation may
be read by downstream units, but any proposed edit returns that path to the
foundation stage.

## Compact Wave Plan

Before dispatch, return only decision-bearing fields:

```text
Wave and operation
Applicable documentation/autonomy state
Concurrency and isolation plan
Units:
- ID, source, dependencies
- owned paths and intended base
- lane/profile and assurance/protocol
- admitted roles and triggers
- acceptance and exact focused checks
- risks, blockers, and stop conditions
Aggregate verification owner and commands
Release/Jira handoff context when relevant
```

Do not include empty registry, timing, schema, Compound, Jira, or release fields
when the selected route does not use them.

## Authority And State

An explicit user request authorizes its scoped local implementation. Ask before
an external, irreversible, notification-causing, production, Jira, or shipping
mutation that is not already authorized. Autonomous work executes only exact
ledger-covered mutation classes.

Create queue or blocker state only when persistence, resume, Jira mapping, or
cross-wave coordination needs it. Update it when a material gate, status,
blocker, evidence fingerprint, or handoff fact changes. Apply guarded lifecycle
transitions through `scripts/transition_swarm_state.py`; never treat cached state
as live Git, Jira, or worker authority.
