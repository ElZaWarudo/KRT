# Autonomous Mode

Load only when the user authorizes autonomous external mutation or passes `autonomous-ledger:<path>`.

Autonomous mode is a ledger-bound exception to normal human-gated shipping. `autonomy:high` alone does not authorize PR creation, Jira changes, reviewer requests, branch pushes, or merge. The ledger must be active, in scope, unexpired, bound to the issuer approval, and accepted by the deterministic validator before Release Marshal can call the mutation executor.

## Operating Rules

- Deny every external mutation unless the ledger allows the exact mutation class.
- Route external mutation through Release Marshal's autonomous mutation executor.
- Block if the runtime cannot constrain raw mutation commands or credentials to the executor. In that case, continue only in validation-only/manual-required mode.
- Re-fetch live GitHub or Jira state before mutation. Markdown state is never authority for permission or live status.
- Write an audit event before execution. If the pre-execution audit write fails, do not mutate.
- Write an audit event after execution. If a side effect happened but post-execution audit fails, stop later external mutation until reconciliation.
- Continue safe independent work only when `autonomous-flow-matrix.md` allows it.

## Merge Exception

Compound Master never merges directly. In autonomous mode it may hand a merge candidate to Release Marshal only when the ledger includes `pr_merge`, `pr_merge_queue`, or `pr_auto_merge`. Release Marshal must still prove live human reviewer approval on the current head, green required checks, satisfied branch protection or rulesets, exact PR scope, and audit readiness.

## Jira Completion

Jira may move to `Hecho` only through the Jira transition validator and executor, and only after the linked PR is proven merged from GitHub evidence or a same-contract audit event created from GitHub evidence.
