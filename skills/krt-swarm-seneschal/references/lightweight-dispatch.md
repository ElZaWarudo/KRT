# Lightweight Dispatch

Use this protocol only when orchestration provides a named benefit but the full
executable worker contract would cost more than the risk it controls.

## Admission

All conditions must hold:

- The user authorized the scoped local work.
- The execution lane is `fast` or `standard`; it is not `deep`.
- Assurance is `low` or `medium`.
- Objective, owned paths, non-goals, acceptance criteria, dependencies, and
  focused checks are already settled.
- The worker will not perform an external, irreversible, destructive,
  production, credential-sensitive, Jira, Git shipping, or release action.
- Repository policy does not require the executable contract.
- The run is interactive rather than autonomous.

If any condition fails, load `executable-worker-contracts.md` and use the
advanced protocol.

## Dispatch Envelope

Give the worker only the unit and the context it needs:

```text
Role and unit: <role, ID, title>
Objective: <one bounded outcome>
Owned paths: <exact paths>
Read-only context: <exact paths or none>
Non-goals and forbidden actions: <short list>
Acceptance criteria: <checkable list>
Focused verification: <exact commands>
Isolation: <workspace/branch/base facts>
Budget and stop condition: <finite bounds>
Return: status, changed paths, criteria evidence, commands and outcomes,
blockers, risks, and remaining actions
```

Do not send the full queue, reference tree, orchestration history, or unused
worker schemas. Workers still follow repository `AGENTS.md` instructions and
may stop for an unowned file, unresolved decision, or unsafe condition.

## Review Depth

- `low`: the implementer runs focused checks and rereads the final diff once
  against the acceptance criteria. No independent reviewer or registry.
- `medium`: after implementation, one independent reviewer answers one named
  question about the affected surface. Record its actor, observed diff digest,
  result, evidence, and findings. Do not create a review council or findings
  registry unless a high-risk boundary is discovered.

A medium finding that exposes auth, data integrity, migration, public-contract,
production, security, concurrency, or destructive risk raises assurance to
`high`; switch to the executable protocol before continuing.

## Root Reconciliation

The worker return is a claim, not certification. Root must:

1. Inspect the actual changed paths and diff against ownership.
2. Capture the exact focused command exit codes, rerunning checks when runtime
   evidence is unavailable.
3. Confirm acceptance criteria and any required medium reviewer result.
4. Classify the unit as release-ready, needs-fix, blocked, deferred, or
   split-required.

Do not create timing, registry, terminal-schema, or evidence-reuse artifacts for
routine lightweight work. Capture them only for a declared evaluation sample or
when a later high-assurance trigger requires the advanced protocol.
