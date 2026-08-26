---
name: krt-real-world-edge-testing
description: Build and safely execute evidence-backed edge-case campaigns across real system boundaries. Use for adversarial or failure-mode testing that needs deterministic fixtures, strong oracles, preflight, and recovery—not narrow unit tests, coverage review, penetration testing, or open-ended chaos engineering. Runtime aliases may expose this as krt:real-world-edge-testing.
---

# KRT Real-World Edge Testing

Turn “test the edge cases” into a reproducible failure campaign that exercises the real system and leaves it recoverable. Produce executable cases and evidence, not a generic checklist.

## Load References

- Load [references/safety.md](references/safety.md) before designing or running a campaign.
- Load [references/campaign-contract.md](references/campaign-contract.md) when defining cases, fixtures, profiles, evidence, state, or completion criteria.
- Load [references/failure-taxonomy.md](references/failure-taxonomy.md) while discovering and prioritizing failure modes. Select relevant categories; do not turn the taxonomy into mandatory busywork.
- Load [references/evaluation-pack.md](references/evaluation-pack.md) only when evaluating this skill's routing or behavior.

## Choose A Mode

- **Design:** inspect the repository and produce the campaign specification without changing or exercising the system.
- **Build:** create fixtures, manifests, validators, runners, profiles, and runbook material; do not perform external operations.
- **Safe execution:** run offline and non-destructive cases after the applicable preflight checks pass.
- **Stateful execution:** run reversible mutations only after proving target isolation, recording affected resources, and validating recovery.
- **Chaos:** inject dependency or infrastructure failures only in a verified disposable environment and with explicit authorization for the exact affected target.

Choose the least invasive mode that satisfies the request. A request for “edge cases” does not authorize stateful, chaos, production, credential, or third-party mutations.

## Workflow

### 1. Discover The Real Path

Inspect the repository before asking for facts that can be discovered locally. Map:

- the primary user workflow and its entry points;
- parsers, APIs, persistence, queues, jobs, external dependencies, and infrastructure crossed by that workflow;
- existing test frameworks, schemas, fixtures, error contracts, timeouts, retries, logs, and reset conventions;
- the available environment, its ownership, and whether it is isolated.

State what remains unknown. Do not invent contracts, credentials, target hosts, permissions, or production behavior.

### 2. Model And Prioritize Failures

Select failure modes from the taxonomy that are plausible for the discovered boundaries. Assign a justified qualitative priority. When evidence supports numerical comparison, optionally score a candidate:

`risk = impact (1–5) × likelihood (1–5) × detectability (1–5)`

Treat 75–125 as critical, 40–74 as high, 15–39 as medium, and 1–14 as low. Record the rationale for each factor; omit the score rather than manufacturing precision from guesses. Record execution risk separately as `read_only`, `reversible_mutation`, `isolated_destructive`, `external_side_effect`, or `production_forbidden`.

Critical cases must be executed or explicitly reported as blocked. Keep low-value permutations out of the primary campaign.

### 3. Build Executable Cases

Every case must contain the contract described in `campaign-contract.md`:

`Fixture → Setup → Action → Oracle → Recovery`

Use deterministic synthetic fixtures with unique canaries. Prefer the project's existing tooling and real production parsers or interfaces over new abstractions or mocks. Every external action needs a timeout.

When the project has no campaign format, copy `assets/starter-kit/`, adapt the templates, and run `python3 scripts/validate_kit.py <kit-directory>`. Keep project-native formats when they already provide equivalent guarantees.

Bind related assertions to the same evidence object. For example, source identity and expected text must match within one result; separate “source exists” and “text exists” checks can pass on unrelated records.

### 4. Verify Offline, Then Preflight

Before contacting the system, verify fixture-manifest integrity, generated paths, canaries, declared duplicates, campaign schema, runner dry-run behavior, and sanitization rules.

Treat preflight as a hard gate. Identify the target, reject ambiguous or shared data, verify dedicated namespaces and mounts, check credentials without printing them, inventory exact affected resources, and prove the recovery mechanism. A renamed database prefix does not prove that a service or bind mount is isolated.

If a required condition fails, stop the affected execution tier and record a concrete blocker. Continue with lower-risk cases when they remain valid.

### 5. Execute In Risk Order

Run offline validation first, then parser fidelity, dry-run validation, read-only baseline, invalid-input and authorization rejection, reversible mutations, dependency failures, restart/recovery, idempotency/convergence, reset, and post-reset verification.

Capture sanitized evidence for each case. Stop escalation when the next tier lacks authorization, isolation, recovery, or a reliable oracle.

### 6. Recover And Report

Run the reset procedure for every stateful case and verify convergence, not merely command success. If recovery fails, preserve the resource inventory, stop further mutation, and report `failed_recovery`.

Report:

- system boundaries and campaign scope;
- cases by pass, fail, blocked, and not run;
- evidence artifact locations and oracle results;
- mutations and recovery status;
- residual risks, manual cases, and missing coverage;
- exact rerun and reset procedures.

Use `partially_executed` or a specific blocked state when credentials, dependencies, isolation, permissions, or recovery prevent execution. Never map those states to complete.

## Guardrails

- Do not mutate production or shared resources without explicit authorization for the exact target and action.
- Do not stop infrastructure, rotate credentials, create public tunnels, change DNS, or delete/trash external data without explicit authorization.
- Never use wildcard deletion or treat an unrelated folder, namespace, database, bucket, or service as disposable.
- Do not print or retain tokens, cookies, authorization headers, private keys, full environment dumps, private documents, or unsanitized infrastructure logs.
- Do not grade subjective generative output without an explicit, observable oracle.
- Do not claim real-path coverage when a case only exercises mocks or a substitute parser.
- Do not hide failed preconditions to continue execution.

## Optional Handoffs

- Use `krt-security-sentinel` to deepen threat modeling or security findings when a campaign crosses authorization, tenancy, secrets, or hostile-content boundaries.
- Use `krt-deploy-summoner` to inspect deployment isolation and prepare explicitly authorized infrastructure-failure actions.

These specialists are optional. Their absence does not block design, fixture generation, offline validation, or other defensible campaign work.
