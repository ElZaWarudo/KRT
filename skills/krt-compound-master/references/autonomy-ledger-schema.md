# Autonomy Ledger JSON v1

Load when `autonomy:high` or an autonomous shipping request includes `autonomous-ledger:<path>`.

## Ledger Contract

The Compound Master ledger JSON schema version `1` is the canonical permission source for autonomous external mutation across Compound Master, Swarm Seneschal, and Release Marshal. Reject any other version. Markdown or YAML state may link to it and keep a non-authoritative resume snapshot, but it must not redefine mutation classes, scope, expiry, deny rules, or lifecycle. Scripts must read and validate the JSON ledger directly.

Required top-level fields:

| Field | Meaning |
|---|---|
| `schema_version` | Exact integer `1`; other versions block until a compatible validator exists. |
| `contract_id` | Stable unique ID for this authorization. |
| `issued_at` | ISO timestamp for the visible authorization. |
| `expires_at` | ISO timestamp after which every external mutation blocks. |
| `status` | One of the lifecycle states below. |
| `issuer` | User identity or approval artifact binding. |
| `scope` | Repository, branch, Jira, package, and review-unit bounds. |
| `allowed_mutations` | Deny-by-default mutation classes. |
| `stop_conditions` | Events that immediately stop affected mutation classes. |
| `audit` | Audit path and expected latest event hash. |
| `contract_hash` | SHA-256 of the canonical ledger JSON excluding this field. |

Active ledgers require issuer binding: an identity or approval reference plus an approval artifact hash from the visible user authorization message. Execution mode also requires the caller to provide the expected contract hash from a trusted handoff/state context; the local ledger contents alone are not enough.

Lifecycle states:

```text
pending-authorization
active
expired
revoked
scope-mismatch
superseded
resume-blocked
```

Mutation classes:

```text
branch_push
branch_force_push
branch_cleanup
pr_create
pr_update
pr_ready
reviewer_request
jira_create
jira_update
jira_backlink
jira_transition_review
jira_transition_done
pr_merge
pr_merge_queue
pr_auto_merge
```

Shared validator result schema:

```json
{
  "allowed": false,
  "mutation_class": "pr_merge",
  "target": {"repository": "owner/repo", "base_branch": "main"},
  "payload_hash": "sha256-hex-or-null",
  "block_reasons": ["required_checks_not_green"],
  "warnings": [],
  "live_state_summary": {},
  "audit_required": true
}
```

## Resume Checks

Treat the run as materially changed and block external mutation when any of these values drift:

- Repository or base branch differs from ledger scope.
- Target branch, Jira key, package, or review unit is outside scope.
- Ledger expired, revoked, superseded, or contract ID changed.
- Expected contract hash no longer matches.
- Expected audit head no longer matches the last immutable event.
- Live GitHub or Jira state contradicts recorded assumptions.

State files may record only a resume snapshot such as `ledger_path`, `schema_version`, `contract_id`, `contract_status`, `contract_hash`, `latest_audit_event`, and `captured_at`. These fields are hints only; re-read the JSON and run `scripts/check_autonomy_ledger.py` before every external mutation and after resume.
