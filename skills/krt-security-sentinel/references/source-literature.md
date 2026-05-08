# Security Guidance Synthesis

This file is the stable working synthesis for Security Sentinel. It distills the external guidance listed in "Source Basis" into review principles that should remain useful even when external pages move or expand.

## Core Model

Security review asks five questions:

1. **What asset is at risk?** Data, identity, money, availability, integrity, secrets, customer trust, or release integrity.
2. **Who can act?** Anonymous user, authenticated user, tenant user, admin, service account, CI job, dependency, operator, or external integration.
3. **What boundary changed or failed?** Authentication, authorization, tenant ownership, input parsing, secret boundary, API contract, deployment exposure, supply chain, audit/monitoring, or recovery.
4. **What prevents misuse?** Explicit checks, default-deny policy, validation, escaping/encoding, rate limits, scoping, least privilege, isolation, logging, tests, or operational guardrails.
5. **How do we verify the control?** Negative tests, config inspection, dependency evidence, runtime checks, audit logs, or documented manual verification.

Findings should be evidence-backed. A framework category is not a finding by itself.

## Application And API Review

Prioritize broken access control and authorization failures:

- object-level authorization: can an actor access another user's or tenant's object?
- function-level authorization: can a lower-privileged actor call an admin/system action?
- tenant isolation: are reads, writes, jobs, exports, and generated references scoped?
- mass assignment and over-posting: can clients set fields they should not control?
- unsafe API consumption: do external inputs become trusted internal state?

Input and output risks:

- injection through SQL, shell, template, NoSQL, LDAP, log, expression, or command boundaries;
- SSRF and unsafe URL fetching;
- unsafe redirects and callback URLs;
- insecure file uploads/downloads;
- deserialization and parser abuse;
- sensitive data exposure in errors, logs, exports, artifacts, and telemetry.

Verification expectations:

- positive tests prove intended access;
- negative tests prove denial paths;
- cross-tenant/object tests prove isolation;
- malformed input tests prove validation and error handling;
- logs/errors are inspected for sensitive data leakage.

## Identity, Secrets, And Data

Authentication and session/token handling:

- tokens should be scoped, expiring, revocable where needed, and validated against the right issuer/audience/context;
- session and password flows should avoid leaking account existence or sensitive state;
- privileged actions should have explicit authorization checks close to the action.

Secrets:

- never print, decode, or store secrets in review output;
- verify secret references and scopes, not secret values;
- check that CI/CD tokens, deploy tokens, webhooks, and service credentials use least privilege;
- prefer rotation paths and documented ownership for high-value credentials.

Data protection:

- identify PII/regulatory data paths;
- check encryption/storage/retention assumptions where relevant;
- verify auditability for sensitive actions;
- ensure exports and downloads preserve authorization and logging.

## Secure Software Delivery

For development and release practices, check whether the change weakens:

- dependency trust: lockfiles, package managers, registries, GitHub Actions, base images, generated clients;
- build integrity: untrusted PR execution, artifact exposure, broad CI permissions, script injection;
- review gates: tests, code review, security review, and release approvals;
- deploy safety: RBAC, network exposure, public ingress, secret references, image tags, Helm values, Kubernetes service accounts.

Supply-chain findings should name the trusted component, how trust is established, and what would happen if that component is compromised.

## System Diagnosis

For whole-system assessment, inventory before judging:

- entry points: web, API, admin, CLI, jobs, queues, webhooks, integrations;
- identities: users, admins, services, CI jobs, deploy actors;
- data stores and data sensitivity;
- trust boundaries and network exposure;
- secrets/config sources;
- build/release/deploy chain;
- logs, audit trails, alerts, and incident evidence;
- runbooks and ownership for recovery.

Then prioritize exploitable paths over completeness. A small number of high-confidence risks is better than a long maturity checklist with no evidence.

## Severity Calibration

- **P0:** active or trivial exploit, secret exposure, auth bypass, tenant/data breach, RCE, destructive data loss, or release integrity compromise.
- **P1:** likely exploitable in normal flows: privilege escalation, broken object/function authorization, unsafe token/secret handling, serious supply-chain issue.
- **P2:** meaningful security gap with plausible exploit path or missing verification around sensitive behavior.
- **P3:** defense-in-depth or hygiene improvement with limited direct exploitability.

Raise severity when sensitive data, multi-tenant boundaries, admin actions, public exposure, or release/deploy credentials are involved.

Lower severity when exploitation requires unrealistic access, the affected asset is low impact, or strong compensating controls are evidenced.

## Source Basis

This synthesis is based on these external bodies of guidance, consulted during skill creation:

- OWASP Top 10 2021.
- OWASP API Security Top 10 2023.
- OWASP Application Security Verification Standard.
- OWASP Cheat Sheet Series.
- NIST Cybersecurity Framework 2.0.
- NIST Secure Software Development Framework SP 800-218.
- CIS Critical Security Controls.
- OWASP SAMM.

Use these sources for deeper detail when needed, but do not require live web access for normal Security Sentinel operation.
