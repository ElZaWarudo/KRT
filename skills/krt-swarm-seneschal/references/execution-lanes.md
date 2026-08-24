# Execution Lanes

Load this reference before assigning a worker profile, admitting optional roles,
or deciding who owns verification. The objective is to spend orchestration only
where it buys isolation, parallelism, or risk reduction.

## Break-Even Gate

Do not start a swarm for one small independent unit when the root agent can
safely finish it immediately. Keep the work in the root thread when all are
true:

- there is one implementation unit;
- its decisions are closed and its scope is normally one to three files;
- it does not need isolated parallel work or an independent model mandate; and
- dispatch, context startup, and reconciliation would cost more than the work.

Use a worker when isolation, concurrency, an explicit independent review, or a
long-running bounded task provides a concrete benefit. Record `root-direct` as
the route when the break-even gate keeps work out of the swarm.

## Lane Classification

Classify every dispatched implementation unit exactly once before wave
selection. A higher-risk trigger always wins over file-count heuristics.

| Lane | Admission rule | Worker profile | Reasoning | Compound Master |
|---|---|---|---|---|
| `fast` | Fully decision-closed change, known edit path, normally 1-3 owned files, no demanding trigger | `spark` | `xhigh` | forbidden |
| `standard` | Execution-ready work with bounded local implementation choices and no demanding trigger | `luna` | `high` | normally forbidden |
| `deep` | Any demanding trigger below | `luna_xhigh` | `xhigh` | only when its artifact or quality pipeline is needed |

Spark reasoning is intentionally fixed at `xhigh`. Never lower it, route
exploration to it, or use it to compensate for an incomplete contract. Luna
`high` is the default for normal work. Luna `xhigh` is admitted only by a
concrete deep trigger.

Reasoning depth and execution duration are independent. `xhigh` authorizes
deeper reasoning inside the same bounded contract; it does not authorize more
discovery passes, implementation rounds, verification commands, or closeout
actions. Apply the execution budget from `subagent-contracts.md` to every Luna
lane.

The table selects the implementation worker. Supporting Planner, Reviewer,
Fixer, Integrator, and Documenter roles never use Spark: use Luna `high` for
normal support work and Luna `xhigh` only when that role's own bounded task has
a deep trigger.

### Fast Preconditions

All must be true:

- objective, exact behavior, non-goals, acceptance criteria, ownership, and
  stop conditions are explicit;
- diagnosis or edit path is confirmed, including the existing helper or pattern
  to reuse when relevant;
- no dependency, migration, public-contract, architecture, auth, data, security,
  or production decision remains;
- no dependency or manifest change is allowed;
- focused verification is named literally; and
- the worker can stop instead of choosing among materially different solutions.

Fail closed to `standard` when any fast precondition is absent. Do not make the
Spark contract broader.

### Deep Triggers

Any one trigger selects `deep`:

- a new or cross-cutting architecture, state, or integration decision whose
  compatibility or blast radius cannot be settled by an existing pattern;
- authentication, authorization, tenant isolation, secrets, or security policy;
- schema, migration, transaction, destructive data, or consistency behavior;
- a public API, event, webhook, SDK, compatibility, or deployment contract;
- concurrency, stale-state, ordering, idempotency, or race-sensitive behavior;
- production infrastructure, release safety, compliance, or high blast radius;
- unresolved interaction across frontend, backend, data, and infrastructure.

A difficult local question, broad file count, or desire for extra confidence is
not a deep trigger. Record the exact security, public-contract, migration/data,
concurrency, destructive-action, architecture, or production-risk trigger in
the envelope; `deep_trigger: difficult` is invalid.

Broad file count alone does not force `deep` when the work is routine and
decision-closed. If evidence cannot distinguish `standard` from `deep`, use
`deep` and record the trigger.

For an execution-ready deep package, use the direct two-stage route:
`luna_xhigh_discovery` read-only discovery followed by `luna_xhigh`
implementation after checkpoint validation. Retain the required review/security
gates. Use nested Compound Master only when the
unit still needs its discovery, planning, work-package, multi-stage review, or
security pipeline. Do not wrap every ready unit in Compound Master.

High-risk security work remains subject to the repository security policy. A
direct deep route must run Security Watch during execution and the Security
Sentinel Gate after the work-review loop. If those stages are unavailable
outside Compound Master, route the unit through Compound Master instead.

Do not keep a Luna `xhigh` worker alive for mechanical cleanup after the deep
decision and owned implementation are complete. Its next action is closeout.
If a separate decision-closed documentation or mechanical unit remains, return
it to root for aggregation or dispatch it as a new Spark contract.

## Role Admission Triggers

Start with one Implementer. Add a role only when its trigger is present:

- **Planner:** broad or ambiguous work still requires decomposition, acceptance
  criteria, dependency mapping, or decision closure. Never admit it for an
  execution-ready work package.
- **Reviewer:** behavior or control flow changed; risk is elevated; auth, data,
  security, concurrency, public contracts, compatibility, or architecture is
  touched; acceptance explicitly requires independent review; or the diff
  exceeds the narrow mechanical lane. Pure formatting, generated refreshes,
  and decision-closed docs-only edits do not admit a Reviewer by default.
- **Fixer:** a concrete review finding or failed verification names a bounded
  correction. Never dispatch a speculative Fixer.
- **Integrator:** at least two units have dependency edges, shared surfaces,
  generated outputs, stack/merge choreography, or a cross-unit compatibility
  question. Independent standalone units do not need an Integrator.
- **Documenter:** documentation is an explicit unit surface, or changed behavior
  makes a maintained user/developer/release document inaccurate. Do not add a
  Documenter merely to narrate the run.
- **Compound Master Worker:** the lane is `deep` and the required artifact or
  quality pipeline is incomplete, or high-risk security work cannot receive
  Security Watch and Security Sentinel on the direct route. A complete,
  execution-ready contract alone is not a trigger.

Record each admitted optional role and its trigger in the wave plan. Omitted
roles need no synthetic placeholder or handoff.

## Verification Ownership

Verification has two owners, with no third duplicate pass:

1. The leaf worker runs only the exact contract-specific focused checks and at
   most one declared natural affected suite for its owned change.
2. The Seneschal/root runs aggregate or CI-equivalent verification once after
   all mutable units in the wave are reconciled.

Compute a wave verification fingerprint from the intended base revision, the
ordered changed paths and content digests, and the ordered aggregate commands.
Reuse passing root evidence when that fingerprint is unchanged. Rerun only when
the fingerprint changed, prior evidence failed, or project policy declares the
evidence stale. A Reviewer reads existing verification evidence; it does not
rerun the same suite unless review introduces a new risk-specific check.

Record focused leaf evidence per unit and authoritative aggregate evidence on
the wave. A nested Compound run remains owner of its required inner gates; the
Seneschal consumes those results and runs only genuinely cross-unit checks.

## Timing Telemetry

Write compact run timing records with `scripts/record_run_timing.py`, normally
under `docs/orchestration/runs/<run-id>-timing.json`. Record lane, selected
profile, reasoning effort, context bytes, review/fix rounds, verification
fingerprint, and milliseconds spent in `preflight`, `context`,
`implementation`, `verification`, `review`, and `reconciliation`.

Also record time to first change, discovery/implementation ratio, commands
outside the verification manifest, milliseconds from the last required command
to return, and root actions. Follow `lightweight-supervision.md`:
`luna_xhigh_discovery` returns one terminal checkpoint from a read-only sandbox.
Seneschal validates it and immediately launches `luna_xhigh` with ownership
narrowed to the accepted manifest. A missing edit path completes as
`needs_review`; an implementation that needs another file returns a scope
extension without editing it. Collect repeated-read counts only in explicitly
sampled diagnostics with native runtime evidence.

Only the Seneschal/root writes the timing artifact after collecting leaf timing
reports. Leaf workers never write the shared file. The recorder also locks its
read-modify-write transaction so overlapping root/resume processes cannot lose
unit records.

Telemetry must not contain prompts, source text, command output, credentials,
or URLs with secrets. Compare median end-to-end time and phase shares by lane;
do not optimize only worker implementation time while startup and repeated
verification dominate the run.
