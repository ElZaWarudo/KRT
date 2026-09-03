# Execution Lanes

Load this reference before selecting a worker, protocol, or review depth. Spend
orchestration only when it buys isolation, concurrency, or risk reduction.

Classify two independent axes:

- **Execution lane** describes implementation difficulty and selects a worker.
- **Assurance tier** describes the consequence of being wrong and selects the
  contract, review, and approval depth.

A difficult internal refactor can remain medium assurance. A mechanical auth
change can require critical assurance.

## Break-Even Gate

Keep a unit `root-direct` when all are true:

- it is one decision-closed implementation unit;
- scope is normally one to three files;
- assurance is `low`;
- it needs no isolated parallel work or independent mandate; and
- dispatch and reconciliation would cost more than implementation.

Use a worker only for a named isolation, concurrency, duration, or independent
review benefit. Do not start a swarm merely because Seneschal is active.

## Lane Classification

Classify each dispatched unit from its own writable surface. Do not inherit a
parent or foundation lane automatically.

| Lane | Admission rule | Worker profile | Reasoning | Compound Master |
|---|---|---|---|---|
| `fast` | Fully decision-closed change with a confirmed edit path, normally 1–3 files, and no demanding trigger | `spark` | `xhigh` | forbidden |
| `standard` | Execution-ready work with bounded local choices and no demanding trigger | `luna` | `high` | normally forbidden |
| `deep` | Any concrete deep trigger below | `luna_xhigh` | `xhigh` | only when its artifact or quality pipeline is incomplete |

Spark reasoning is intentionally fixed at `xhigh`. Luna `high` is the default for normal work.
Luna `xhigh` is admitted only by a concrete deep trigger.
Reasoning depth and execution duration are independent; higher reasoning never
expands ownership, rounds, commands, or elapsed budget.

### Fast Preconditions

All must be true:

- objective, behavior, non-goals, acceptance, ownership, and stop conditions
  are explicit;
- the edit path and existing pattern are confirmed;
- no architecture, dependency, auth, data, migration, security, production, or
  public-contract decision remains; and
- focused verification is named literally.

Otherwise use `standard`. Spark does not perform discovery.

### Deep Triggers

Any one selects `deep`:

- unresolved cross-cutting architecture or integration compatibility;
- authentication, authorization, tenant isolation, secrets, or security policy;
- schema, migration, transaction, destructive data, or consistency behavior;
- public API, event, webhook, SDK, deployment, or compatibility contracts;
- concurrency, stale-state, ordering, idempotency, or race-sensitive behavior;
- production infrastructure, compliance, or high blast radius; or
- unresolved interaction across frontend, backend, data, and infrastructure.

Broad file count or a desire for confidence is not a trigger. Record the exact
reason; `deep_trigger: difficult` is invalid.

For an execution-ready deep unit, use read-only `luna_xhigh_discovery` followed
by `luna_xhigh` implementation after the checkpoint narrows ownership. Load
`worker-profiles.md` and `lightweight-supervision.md`. Use nested Compound Master
only when its discovery, planning, work-package, review, security, or CI pipeline
is actually missing.

## Assurance Classification

Start at `low` and raise only for a concrete consequence or integrity trigger.
File count, implementation difficulty, worker failure, or generic confidence do
not raise assurance.

| Tier | Admission rule | Review depth |
|---|---|---|
| `low` | Reversible bounded local change with no hard assurance trigger | Focused tests plus one implementer final-diff self-review |
| `medium` | Local recoverable behavior, CLI, serialization, compatibility, or control-flow change | Exactly one focused independent reviewer |
| `high` | Security, auth, data integrity, migration, public contract, production, or research-evidence integrity | Relevant specialist plus independent validation of named risks |
| `critical` | Irreversible/destructive effect, legal/compliance exposure, publication-critical claim, or several coupled high-risk boundaries | Coordinated review, evidence reconciliation, and explicit approval |

If classification facts are missing, perform one bounded inspection or mark the
unit not ready. Do not use a review council as a substitute for classification.

## Protocol Selection

- Interactive `fast` or `standard` work at `low` or `medium` assurance uses
  `lightweight-dispatch.md` when all its admission conditions hold.
- Any `deep`, `high`, `critical`, autonomous, or repository-mandated unit uses
  `executable-worker-contracts.md`.
- Never raise protocol depth merely because the skill is active, and never
  lower it to avoid a real trigger.

The lightweight protocol retains bounded ownership, acceptance criteria, exact
checks, root diff inspection, and root-observed results. It omits terminal
schemas, hashed contracts, timing, and registries from ordinary work.

## Role Admission

Start with one Implementer. Add another role only for its trigger:

- **Planner:** scope, acceptance, dependencies, or decisions remain open.
- **Reviewer:** assurance is medium or higher, or acceptance explicitly requires
  independent review.
- **Fixer:** a concrete finding or failed check names one bounded defect cluster.
- **Integrator:** multiple units have dependencies, shared/generated surfaces,
  stack choreography, or a cross-unit compatibility question.
- **Documenter:** documentation is explicitly owned or maintained documentation
  became inaccurate.
- **Compound Master Worker:** a deep unit still lacks a required artifact or
  quality pipeline.

For `medium`, one reviewer answers one named question. Under the lightweight
protocol, root records actor, diff digest, result, evidence, and findings. Under
the executable protocol, use the certificate shape. A disputed finding or newly
exposed high-risk boundary raises the unit to `high` before work continues.

For `high` or `critical`, load `review-coordination.md`. Admit reviewers by
distinct risk boundary, not persona count or file count. Compile required
certifications into the executable contract; implementer self-approval never
satisfies them.

High-risk direct deep work runs Security Watch during execution and the Security
Sentinel Gate after review. If those stages are unavailable, use Compound Master.

## Verification Ownership

There are only two verification owners:

1. The leaf worker runs only the exact contract-specific focused checks and at
   most one declared natural affected suite.
2. Seneschal/root runs aggregate or CI-equivalent verification once after the
   mutable wave is reconciled.

Reuse root evidence only when `automated-wave-control.md` proves the fingerprint
is unchanged. A reviewer reads existing evidence rather than repeating the same
suite. Root runs any readiness-bearing focused command not independently
observed and not covered by aggregate verification; a conflicting root result
wins.

Record timing only for advanced, autonomous, adaptive-concurrency, or declared
evaluation samples. Load `lightweight-supervision.md` for checkpoint and timing
details; do not load telemetry mechanics for routine lightweight work.
