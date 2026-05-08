# Security Rubric

Use this rubric for focused work-package reviews and broader system diagnosis.

## Review Surfaces

| Surface | What To Check |
|---|---|
| Authn/Authz | identity source, session/token handling, permission checks, object/function-level authorization, default deny |
| Tenancy/Ownership | tenant scoping, ownership filters, cross-tenant reads/writes, admin bypasses, fixtures/tests |
| Input/Output | validation, parsing, encoding, injection, file upload, SSRF, redirects, deserialization |
| Secrets/Config | env vars, secret refs, logs, token scope, rotation assumptions, defaults, .env examples |
| Data Protection | PII, encryption, retention, backups, audit logs, export/download paths |
| API Contracts | BOLA/BFLA, rate limits, mass assignment, error leaks, pagination/filter abuse |
| Dependencies | lockfiles, known risky packages, unpinned images/actions, supply-chain trust |
| Runtime/Deploy | containers, Kubernetes/Helm values, RBAC, network exposure, probes, resource limits |
| CI/CD | secrets in workflows, permissions, artifact exposure, untrusted PR execution, provenance |
| Observability | security-relevant logs, audit trails, alertable events, sensitive log redaction |

## Slice Review Checklist

For a changed work package, answer:

- What new or changed trust boundary exists?
- What actor can reach it?
- What asset/data can be affected?
- What prevents unauthorized use?
- Are denial/negative tests present for the security boundary?
- Are secrets and sensitive data kept out of logs/errors/artifacts?
- Did deployment/config changes widen exposure?
- Does the release handoff need a security note, migration constraint, or rollback caveat?

## System Diagnosis Checklist

For whole-system diagnosis, inventory:

- entry points: web, API, jobs, queues, webhooks, admin tools, CLIs;
- identity and trust model;
- data classification and storage;
- secret/config sources;
- dependency and build chain;
- deployment/runtime topology;
- logging/audit/incident evidence;
- documented security assumptions and runbooks.

Then prioritize by exploitable paths, not by checklist coverage.

## Finding Quality Bar

Each finding needs:

- evidence path, line, command, manifest, or observed behavior;
- attacker/actor and affected asset;
- why the current control is insufficient;
- concrete remediation;
- verification path;
- confidence level.

Suppress vague findings that cannot name impact or remediation.
