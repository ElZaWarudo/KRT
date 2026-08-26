# Safety Contract

Real-world edge testing deliberately exercises failure paths, so authorization, isolation, and recovery are part of correctness.

## Permission Tiers

Always permitted within the user's repository, local environment, or already authorized target and requested scope:

- read-only discovery;
- deterministic synthetic fixture generation;
- static validation, local unit tests, dry-runs, and offline verifier execution;
- read-only environment inspection and sanitized health checks.

Permitted only after the preflight proves a dedicated target and recovery:

- uploading synthetic fixtures to a dedicated location;
- creating a dedicated test namespace;
- reversible mutation of synthetic test data;
- authenticated test requests to the approved host;
- sanitized evidence capture.

Require explicit authorization immediately before:

- deleting or trashing existing external data;
- stopping or restarting infrastructure;
- rotating credentials;
- changing DNS, proxy, tunnel, or Cloudflare configuration;
- modifying shared environments;
- any production execution, including nominally read-only campaigns when the user has not approved the target.

## Preflight Gate

Before external writes or stateful execution, verify:

- the exact environment, host, account, namespace, data root, and resource IDs;
- production rejection and an allowlist for remote hosts;
- HTTPS for remote authenticated requests and no credentials embedded in URLs;
- dedicated folders, stores, collections, projects, ports, volumes, and bind mounts;
- absence of unrelated data and production-default prefixes;
- required capabilities and quotas without printing credential values;
- a snapshot, backup, trash/restore path, disposable environment, or tested inverse operation;
- an explicit, validated reset procedure using exact targets and no wildcards.

The bundled preflight document and validator output are evidence, never authorization. `validate_kit.py` always reports `executionAuthorized: false`; independently confirm the current user authority, exact target, and permitted mutation tier immediately before execution.

The validator checks structure, cross-record consistency, conservative secret patterns, and filesystem containment. It reports `executionResultsVerified: false` because it does not execute project-native actions or replay project-native oracles. A structurally valid `pass` or `fail` remains a recorded claim until a project adapter independently evaluates the oracle against captured evidence.

A distinct name or prefix alone does not prove isolation. A service account's ability to create a child resource does not prove it can upload content or recover it.

## Stop Conditions

Pause the affected tier when interactive login is required, permissions or ownership are unclear, unrelated data is present, the target is production-like, recovery is unproven, a public endpoint must be created, or the next action exceeds existing authorization.

If recovery fails, stop all further mutations, retain the private resource inventory, avoid speculative cleanup, and report `failed_recovery` with the safest next action.

## Prohibited Defaults

- permanent or wildcard deletion;
- stopping a stack whose isolation is unproven;
- sending credentials to arbitrary or unapproved URLs;
- printing secrets or full environment/configuration dumps;
- treating a shared folder, database, bucket, namespace, or service as disposable;
- suppressing preflight failures or calling a blocked campaign complete.
