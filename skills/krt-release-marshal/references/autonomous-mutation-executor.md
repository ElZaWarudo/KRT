# Autonomous Mutation Executor

Release Marshal owns autonomous external mutation execution. Compound Master can request work, but it does not call `gh`, Jira, or branch mutation commands directly in autonomous mode.

## Lifecycle

```text
planned
validated
executing
executed
audit-recorded
validation-failed
execution-failed-before-side-effect
execution-failed-after-side-effect
audit-write-failed
```

The executor requires:

- Ledger path.
- Mutation class.
- Exact target identifiers.
- Payload file or payload hash when the mutation has text/body/ref content.
- Class-specific live-state file or fetched JSON state.
- Owning validator resolved from the registry. Caller-supplied validator paths are not allowed for autonomous execution.
- Audit directory.
- Explicit execution flag, trusted expected contract hash, registered execution template, and enforcement confirmation for real side effects.

Dry-run is the default test and planning behavior. Execution is unavailable when the mutation class lacks a validator, when the ledger blocks, when live-state validation blocks, when the expected audit head does not match the ledger, when a trusted expected contract hash is missing, when no registered execution template exists, or when the runtime cannot confirm raw mutation commands and credentials are constrained to the executor.

## Audit Requirements

Write one immutable event JSON before mutation and one after validation/execution. Each event includes the previous event hash and its own event hash. If the pre-execution write fails, block the mutation. If a side effect happens and the post-execution write fails, stop further external mutation and record reconciliation required.
