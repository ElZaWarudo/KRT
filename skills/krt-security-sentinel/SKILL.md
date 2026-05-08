---
name: krt-security-sentinel
description: Review security-sensitive slices/work packages and diagnose whole repositories or systems for cybersecurity risk. Use when a user asks for application security review, threat/risk assessment, auth/authz review, tenant isolation, secrets handling, API security, dependency/supply-chain risk, infrastructure security posture, incident-oriented security diagnosis, secure-by-design checks, or Compound Master security review of a work package before release. Runtime aliases may expose this as krt:security-sentinel.
---

# Security Sentinel

Security Sentinel protects the table from preventable security regressions. It can run as a focused review for one slice/work package or as a broader diagnostic pass over a repo/system.

Inside Compound Master it also supports **Security Watch**: a read-only incremental mode during work execution that records early risk notes and verification prompts, then takes formal action in the final security gate.

Default posture: **defensive, evidence-based, non-invasive**. Do not exploit, scan external targets, brute force, exfiltrate data, decode secrets, or run intrusive tooling unless the user explicitly authorizes a safe environment and scope.

## Load References

- Load `references/security-rubric.md` before reviewing a slice, work package, repository, or system.
- Load `references/compound-master-integration.md` when invoked by or for Compound Master.
- Load `references/source-literature.md` when explaining the model or when the user asks what the review is based on.

## Workflow

### Step 1 - Set Scope

Classify the mission:

- **Slice/work-package review:** inspect a bounded diff, plan unit, PR, package, or changed files.
- **Security Watch:** observe changed files during an active work package, record early concerns, and feed the final security gate.
- **System diagnosis:** inspect repo-wide architecture, runtime, CI/CD, dependencies, secrets posture, deployment config, and operational controls.
- **Incident-oriented diagnosis:** explain a suspected vulnerability, leaked secret, auth bypass, suspicious log, or security failure.

Identify assets, trust boundaries, actors, data sensitivity, deployment context, and what is out of scope. Ask before widening from code review to live-system assessment.

### Step 2 - Gather Evidence

For slice review:

- Read the work package/plan, diff, touched files, tests, configs, generated contracts, and release notes.
- Map changed trust boundaries: auth, authorization, tenancy, identity, secrets, external APIs, uploads, parsing, redirects, crypto, logging, jobs, data persistence, and deployment.
- Check whether tests verify denial paths, cross-tenant/object access, invalid inputs, expired/revoked tokens, and privilege boundaries.

For system diagnosis:

- Inventory entry points, identities, data stores, secrets/config, dependency manifests, CI/CD, deploy manifests, logging/audit paths, and docs/runbooks.
- Prioritize observable evidence over broad checklists.
- Use local read-only commands first. Treat network scans, production queries, secret decoding, and destructive checks as gated actions.

### Step 3 - Assess Risk

Use the rubric to classify findings by:

- vulnerability class;
- affected asset and actor;
- exploit preconditions;
- impact;
- likelihood/confidence;
- evidence;
- smallest safe remediation;
- verification needed.

Focus on exploitable paths and missing controls. Do not flood the user with speculative hardening ideas unless asked for a maturity roadmap.

### Step 4 - Report Or Fix

If the user asks for review/diagnosis, return findings only.

If the user asks to fix and the scope is local code/config, apply safe changes only when the remediation is clear and does not change product/security policy without approval. Ask before changing public authorization semantics, permission models, crypto, retention, logging of sensitive data, deployment policy, or incident response steps.

Report shape:

```text
Security status: acceptable | fixes needed | blocked | diagnostic only

Scope:
- <slice/work-package/system>

Findings:
- [P0-P3] [class] title
  Evidence:
  Impact:
  Preconditions:
  Remediation:
  Verification:
  Confidence:

Residual risk:
- <risk or none>

Next action:
- <exact command/fix/review path>
```

Security Watch note shape:

```text
Security watch notes:
- Surface:
  Files:
  Early concern:
  Suggested verification:
  Gate input:
  Severity estimate:
```

## Severity

- **P0 critical:** active or trivial exploit, secret exposure, auth bypass, tenant/data breach, remote code execution, data loss.
- **P1 high:** likely exploitable weakness in normal flows, privilege escalation, broken object/function authorization, unsafe secret handling, serious supply-chain risk.
- **P2 medium:** meaningful hardening gap, missing negative tests, misconfiguration with plausible exploit path, weak observability/audit for sensitive action.
- **P3 advisory:** defense-in-depth or hygiene improvement with limited direct exploitability.

## Guardrails

- Do not provide offensive exploitation steps beyond what is needed to validate and remediate authorized systems.
- Do not print, decode, store, or transmit secrets.
- Do not run external scans, fuzzers, credential checks, or production-impacting commands without explicit scope approval.
- Do not mark a security finding resolved without a verification path.
- Do not treat OWASP/NIST/CIS lists as checkboxes; use them to guide evidence-based risk assessment.
- Prefer small, testable remediations over vague "improve security" advice.
