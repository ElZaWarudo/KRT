# Execution Lanes

Load this reference before assigning a worker profile, admitting optional roles,
or deciding who owns verification. The objective is to spend orchestration only
where it buys isolation, parallelism, or risk reduction.

Classify two independent axes. The execution lane describes implementation
difficulty and selects the worker profile. The assurance tier describes the
consequence of being wrong and selects review depth. Never infer one from the
other: a mechanical auth edit can need critical assurance, while a difficult
internal refactor can remain medium assurance.

## Break-Even Gate

Do not start a swarm for one small independent unit when the root agent can
safely finish it immediately. Keep the work in the root thread when all are
true:

- there is one implementation unit;
- its decisions are closed and its scope is normally one to three files;
- its assurance tier is `low`;
- it does not need isolated parallel work or an independent model mandate; and
- dispatch, context startup, and reconciliation would cost more than the work.

Use a worker when isolation, concurrency, an explicit independent review, or a
long-running bounded task provides a concrete benefit. Record `root-direct` as
the route when the break-even gate keeps work out of the swarm.

A single low-assurance unit routes `root-direct` by default. Override that
default only for a named isolation, concurrency, or duration benefit—not merely
because the Seneschal skill is active.

## Lane Classification

Classify every dispatched implementation unit exactly once before wave
selection. A higher-risk trigger always wins over file-count heuristics.

When `staged-decomposition.md` splits a coupled parent, do not classify the
parent and copy that lane to its children. Classify foundation and every
dependent from their own writable surface after ownership is partitioned. A
settled contract in `required_context` is not a public-contract mutation trigger;
editing that contract remains a deep trigger and belongs back in foundation.

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

## Assurance Classification

Assign every unit exactly one assurance tier before admitting review roles.
Start at `low` and raise it only for a concrete consequence or integrity
trigger. File count, number of code surfaces, implementation difficulty, prior
worker failure, or a generic desire for confidence do not raise the tier.

| Tier | Admission rule | Review mode | Review demand |
|---|---|---|---|
| `low` | Reversible, decision-closed, bounded local change with no hard assurance trigger | implementation, focused tests, and one implementer self-review | `0` |
| `medium` | Bounded behavior, control-flow, CLI, serialization, or compatibility change whose failure remains local and recoverable | exactly one focused independent Reviewer | `1` |
| `high` | Security, auth, data integrity, migration, public contract, production, or research-evidence integrity can be affected | one relevant specialist plus independent validation of named risks, invariants, claims, or findings | `2` |
| `critical` | Irreversible or destructive production/data effect, publication-critical empirical claim, legal/compliance exposure, or several coupled high-risk boundaries | coordinated review council, evidence reconciliation, and explicit approval | `3` minimum |

The highest matched trigger wins. If the facts needed to classify the unit are
missing, perform one bounded root inspection or mark the unit not ready; do not
use a review council as a substitute for classification.

Research integrity is a hard floor based on consequence, not filename. Code
that selects evidence, transforms result-bearing data, changes evidence
lineage or provenance, mutates raw data, or controls cross-paper reuse is at
least `high`. Destructive raw-data changes and publication-critical empirical
claims are `critical`. File discovery, YAML serialization, status rendering,
scaffolding, and CLI mechanics remain `low` or `medium` when they cannot alter
evidence selection, meaning, lineage, or a public compatibility contract.

Before admitting any independent reviewer, state:

- the unique question that reviewer will resolve;
- the evidence unavailable from focused tests and self-review;
- the affected surface or risk boundary; and
- the result that would change readiness.

Omit the reviewer when these cannot be named. Several reviewers are justified
only by distinct high-risk boundaries, not by several directories or personas.

For a dispatched low-assurance unit, the Implementer rereads the exact final
diff against the contract after focused tests and records the result in the
existing acceptance evidence. This is the one self-review; it creates no
independent certificate, review plan, findings registry, or validator artifact.

Ordinary correctness review, targeted validation, and mechanical fixes use
Luna `high`. Security review and work whose assigned question itself concerns
auth, data integrity, public contracts, concurrency, or another deep trigger
use Luna `xhigh`. A difficult history, prior worker failure, or desire for more
confidence does not by itself raise effort. Higher effort never expands the
role's finding set, fix batch, command manifest, or elapsed-time budget.

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
- **Reviewer:** assurance is `medium` or higher, or acceptance explicitly
  requires independent review. `medium` admits exactly one reviewer chosen for
  the affected surface. `high` admits the relevant specialist and independent
  validation. `critical` admits coordinated review. A behavior or control-flow
  change alone is not a Reviewer trigger.
- **Fixer:** a concrete review finding or failed verification names a bounded
  correction. Group only findings that share one defect cause and owned
  surface; otherwise use separate passes. Never dispatch a speculative Fixer.
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

For `medium`, issue one direct certificate using the shape in
`executable-worker-contracts.md`; do not create a coordinated review plan or
findings registry. If the finding is disputed or exposes a high-risk boundary,
raise the unit to `high` before continuing.

For `high` or `critical`, load `review-coordination.md` and partition primary
reviewers by distinct risk boundary. Code-surface ownership prevents duplicate
coverage but does not itself justify another reviewer. Admit cross-cutting
security, public-contract, or evidence-integrity review only for its named hard
trigger. Validators receive named invariants, claims, or canonical finding IDs
instead of an open-ended rediscovery prompt.

Compile admitted `Reviewer` and `Security Sentinel` triggers into the executable
worker contract's `required_certifications`; `low` uses an empty list. The
implementer may finish its terminal, but a `medium`, `high`, or `critical` unit
remains `awaiting_certification` until the required different actor certifies
the same contract hash and root-observed diff digest. A failed certificate
routes to `needs-fix`; it is never converted into implementer self-approval.

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

A leaf's self-reported passing result is diagnostic evidence, not gate
evidence. When native command events are unavailable, root executes any
contract-required focused check not covered by the aggregate command set and
captures its exact argv, exit code, and output. Do not mark the unit
ready from the leaf's prose or reconstructed command summary. A conflicting
root result wins and routes the unit to `needs-fix`.

Do not compute or compare fingerprints manually. Load
`automated-wave-control.md` and use `scripts/verification_evidence.py` to
compute, decide, and record. Only its `reuse` action authorizes reuse.

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

For every lane also record command-evidence trust, root-observed scope
violations, repeated verification commands, P0/P1/P2 findings from independent
certificates, and elapsed time through final acceptance. Compare these metrics
by `worker_profile`; do not mix self-reported and runtime-audited samples.

Only the Seneschal/root writes the timing artifact after collecting leaf timing
reports. Leaf workers never write the shared file. The recorder also locks its
read-modify-write transaction so overlapping root/resume processes cannot lose
unit records.

Telemetry must not contain prompts, source text, command output, credentials,
or URLs with secrets. Compare median end-to-end time and phase shares by lane;
do not optimize only worker implementation time while startup and repeated
verification dominate the run.

Summarize comparable samples by worker profile and evidence trust:

```bash
rtk python3 <seneschal-skill-dir>/scripts/summarize_worker_metrics.py \
  --input docs/orchestration/runs/<run-id>-timing.json
```

Never combine `self-reported` and `runtime-audited` samples into one performance
or compliance claim.
