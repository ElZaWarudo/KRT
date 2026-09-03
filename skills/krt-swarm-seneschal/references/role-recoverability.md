# Role Return Recoverability

Load this reference when dispatching Reviewer or Fixer roles, resuming a wave
with unfinished invocations, or classifying a failed verification command. It
preserves useful partial work without turning ordinary roles into chatty,
continuously supervised agents.

## Executable Role Envelopes

Do not hand-compose Reviewer or Fixer closeout instructions. Resolve the
invocation workspace and root-owned artifact directory, then render concrete
paths:

```bash
rtk python3 <seneschal-skill-dir>/scripts/render_role_envelope.py \
  --role reviewer \
  --actor-id <reviewer-worker-id> \
  --surface-id <review-surface-id> \
  --assignment <absolute-review-plan.json> \
  --workspace-root <absolute-read-only-worktree> \
  --terminal-path <absolute-root-owned-candidate.json> \
  --output <reviewer-envelope.json>
```

Use `--role fixer --actor-id <fixer-worker-id>` with its absolute assignment
path for a Fixer. The renderer validates the assignment, binds the actor and
review surface when applicable, rejects relative locators, missing paths, and
terminal paths inside the worker worktree, and supplies the exact terminal
shape and validator. This deterministic preflight replaces an acknowledgement
handshake; the worker sends no acknowledgement or heartbeat.

Canonical paths stored in contracts and plans remain repo-relative. Absolute
paths are invocation locators only and belong in the workspace invocation
record and rendered envelope.

## Conditional Review Recovery

Recovery snapshots are available only for coordinated `high` or `critical`
reviews. Enable `--recovery-path <absolute-root-owned-recovery.json>` when at
least one concrete recoverability trigger is recorded:

- the assignment has two or more risk boundaries;
- its elapsed budget is at least five minutes; or
- a prior invocation for the same role and surface disappeared.

Do not enable recovery for a medium focused review merely because the feature
exists. A recovery-enabled reviewer atomically replaces one candidate after a
completed risk boundary and validates it with
`scripts/validate_review_recovery.py`. It does not send progress messages.

The `review-recovery-v1` artifact binds the contract, diff, plan, reviewer,
surface, checked-boundary subset, candidate findings, candidate feedback, and
stop reason. It must set `certifies_review: false`. It is never ingested into
the findings registry and never satisfies review coverage or certification.

When an invocation disappears or is interrupted:

1. Preserve its workspace, invocation record, and latest valid recovery
   artifact.
2. Mark failure origin as `worker`, `runtime`, `root`, or `unknown`; do not
   infer an infrastructure cause.
3. Prefer a fresh worker with the same immutable contract, diff, plan, and
   recovery artifact. Reuse the same live worker only when the runtime proves
   identity and context continuity.
4. Require the replacement to recheck inherited candidate evidence before it
   includes it in a complete terminal.

Malformed prose or JSON may be retained as diagnostic output, but it is
untrusted and is not converted into canonical findings by root.

## Immediate Terminal Persistence

After root reruns the role validator, immutably persist the exact accepted
terminal before registry ingestion or further dispatch:

```bash
rtk python3 <seneschal-skill-dir>/scripts/persist_role_terminal.py \
  --role reviewer \
  --expected-actor-id <reviewer-worker-id> \
  --assignment <review-plan.json> \
  --input <candidate-terminal.json> \
  --output <durable-root-owned-terminal.json>
```

The command creates the destination once, verifies the terminal actor against
the dispatched identity, returns its digest, and refuses to overwrite it. Use
`--role fixer` for a Fixer assignment. Record the durable path and digest in
the invocation before continuing reconciliation.

## Verification Failure Attribution

Do not accept a worker's label for a failed command. Root captures the current
exit code and failure-output digest, checks dependency availability, and, when
baseline attribution matters, runs the same command on the sealed baseline in
a fresh disposable snapshot. Classify the evidence with:

```bash
rtk python3 <seneschal-skill-dir>/scripts/classify_verification_result.py \
  --input <root-captured-classification-input.json>
```

The classifier distinguishes `passed`, `environment_failure`,
`baseline_failure`, `regression`, and `unclassified_failure`. Missing
dependencies require concrete environment evidence and can never be labeled a
baseline failure. Baseline attribution requires the same failure fingerprint
on the sealed baseline and no relevant owned-surface change; ambiguous cases
remain unclassified.

## Evaluation Dimensions

Keep run outcome separate from worker capability:

- `reasoning_quality`: score only observable semantic work; otherwise `null`;
- `protocol_compliance`: `passed`, `failed`, or `not-observed`;
- `completion`: `returned`, `partial`, `interrupted`, or `disappeared`;
- `failure_origin`: `worker`, `runtime`, `root`, `unknown`, or `null`.

An invocation with no usable output may receive a poor operational outcome,
but it does not receive a fabricated reasoning score and is excluded from
semantic team averages.
