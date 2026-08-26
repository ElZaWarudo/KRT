# Campaign Contract

Use this contract to keep campaigns executable, evidence-backed, and restartable. Adapt field names to established project conventions rather than introducing a new framework solely to match this document. The bundled JSON Schemas define the portable structural interchange shape; `validate_kit.py` is the authoritative semantic and filesystem-safety validator. Schema validity alone never authorizes execution or proves a kit safe.

## First-Class Concepts

Every case defines:

1. **Fixture:** synthetic data or state that activates the condition.
2. **Setup:** environment and prerequisites.
3. **Action:** bounded request, mutation, event, or failure injection.
4. **Oracle:** observable evidence that determines pass or fail.
5. **Recovery:** exact restoration or proof that the environment is disposable.

## Case Record

At minimum record:

```json
{
  "id": "EC-AREA-001",
  "title": "A concrete failure behavior",
  "category": "state_and_lifecycle",
  "risk": {
    "impact": 4,
    "likelihood": 3,
    "detectability": 4,
    "score": 48,
    "rationale": "A retry race can duplicate a normal user transaction"
  },
  "priority": "high",
  "executionRisk": "reversible_mutation",
  "fixtures": ["D01"],
  "preconditions": ["Dedicated test namespace is empty"],
  "action": {
    "type": "project_native_request",
    "description": "Submit the synthetic duplicate request twice"
  },
  "oracle": {
    "expectedCardinality": 1,
    "requiredState": "accepted_once"
  },
  "timeoutMs": 10000,
  "evidence": ["sanitized_response", "state_checksum"],
  "recovery": {
    "required": true,
    "procedure": "reset the named synthetic resource",
    "verification": "baseline checksum restored"
  }
}
```

The action and oracle may use project-native schemas. Reject cases that lack a deterministic outcome, bounded timeout, or recovery disposition. Numerical risk is optional; when present, require evidence-based rationale and verify the product and derived priority. A justified qualitative priority is preferable to unsupported numerical precision.

## Strong Oracles

Assert relationships within the evidence record that establishes them:

```json
{
  "requiredMatches": [
    {
      "where": {"source.name": "expected.pdf"},
      "assert": {
        "textAll": ["CANARY-42"],
        "textNone": ["OLD-CANARY"]
      }
    }
  ]
}
```

Independent checks that `expected.pdf` exists somewhere and `CANARY-42` exists somewhere are not equivalent.

Useful oracle families include:

- protocol: status, error code, schema, headers, size, and latency;
- collection: cardinality, membership, uniqueness, ordering, and pagination;
- state: existence, version/checksum transition, absence of duplicates, and convergence after reconciliation;
- security: denial, tenant/object absence, no secret echo, and hostile content treated as data;
- recovery: baseline restored and a second reset/reconciliation creates no further change.

## Fixture Manifest

Fixtures must be synthetic, deterministic, reproducible, private-data-free, and identifiable by unique canaries. A manifest records an ID, filename or resource name, kind, expected treatment, canaries, provenance and reproduction instructions, a SHA-256 digest, and any intentional duplicate relationship.

Validate:

- unique IDs and filenames unless duplication is declared;
- valid duplicate references and byte identity where claimed;
- recognized expected-treatment classifications;
- required canaries in generated content;
- generated paths contained beneath the dedicated output root;
- exact agreement between the manifest and generated artifacts.

Generated binary fixtures should normally be ignored when a versioned generator reproduces them exactly.

## System Profile

Keep project-specific interfaces and safety boundaries in a profile rather than in the general skill. Record:

- system name and type;
- interface type, method, and path or resource address;
- dedicated data root, namespace/project, collection prefix, and port allocation;
- action, dependency, and convergence timeouts;
- production policy, HTTPS requirements, allowed mutation tiers, and recovery inventory policy.

Do not place credentials in the profile. Reference protected environment variables or a secret store.

## Preflight Result

Preflight is machine-readable where practical:

```json
{
  "schemaVersion": 1,
  "status": "blocked",
  "checks": [
    {
      "condition": "isolated_vector_namespace",
      "status": "failed",
      "evidence": "The configured prefix is the production default"
    }
  ],
  "blockers": [
    {
      "condition": "isolated_vector_namespace",
      "reason": "The configured prefix is the production default"
    }
  ]
}
```

No stateful execution proceeds while a critical condition fails.

## Evidence Record

Record case ID, duration, result, observed values, sanitized artifact paths, mutations, and recovery status. Executed records (`pass` or `fail`) also require an RFC 3339 `startedAt` timestamp, the evaluated `oracleResult`, and an `oracleDigest` that binds the evidence to the campaign oracle. Evidence must be sufficient to replay the oracle without relying on prose memory.

The digest is lowercase SHA-256 of the oracle serialized as UTF-8 JSON with recursively sorted keys and compact separators (`,` and `:`). Generate digests from a campaign instead of reproducing this algorithm manually:

```bash
python3 scripts/validate_kit.py /path/to/edge-tests --oracle-digests
```

An executed record has this shape:

```json
{
  "caseId": "EC-AREA-001",
  "result": "pass",
  "startedAt": "2026-08-26T10:30:00Z",
  "durationMs": 241,
  "observed": {"acceptedCount": 1},
  "artifacts": ["evidence/EC-AREA-001-response.json"],
  "mutations": [],
  "recoveryStatus": "recovered",
  "sanitized": true,
  "oracleDigest": "<generated by --oracle-digests>",
  "oracleResult": {
    "passed": true,
    "details": ["One request was accepted and one was identified as a duplicate"]
  }
}
```

Never store access tokens, private keys, cookies, authorization headers, unrelated private data, full environment dumps, or unsanitized logs. A validator pass is conservative screening, not proof that arbitrary artifacts contain no secrets.

## State And Completion

Use observable states such as:

`discovered → designed → built → offline_verified → preflight_passed → baseline_executed → stateful_executed → chaos_executed → recovered → reported`

Valid non-success terminal states include `blocked_credentials`, `blocked_permissions`, `blocked_isolation`, `blocked_dependencies`, `partially_executed`, and `failed_recovery`.

A campaign is complete only when applicable high-priority cases have executable actions and strong oracles, safe cases were run, stateful cases were recovered, evidence was sanitized, blockers were recorded, and rerun/reset instructions are executable.

Report quality using useful ratios where data exists: executable cases, evidence-bound oracles, real-path coverage, stateful safety coverage, failure-path coverage, reproducible fixtures, and manual dependency ratio. Do not optimize a metric by weakening safety or assertions.
