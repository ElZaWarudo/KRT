# Compound Master Integration

Use this reference when Security Sentinel is invoked by, or to support, `krt-compound-master`.

## When To Invoke

Invoke Security Sentinel for a work package when any of these are true:

- auth, authorization, tenant isolation, ownership, permissions, roles, or scopes change;
- public API contracts, webhooks, callbacks, file upload/download, parsing, redirects, or external integrations change;
- secrets, credentials, tokens, env vars, CI/CD permissions, deploy config, Helm/Kubernetes/Docker security posture, or service exposure changes;
- PII, regulated data, audit logs, retention, encryption, exports, or destructive actions change;
- dependency, package manager, base image, GitHub Action, or generated client surfaces introduce supply-chain risk;
- the package is classified high-risk by Compound Master and the primary `ce-review` pass did not deeply inspect the security surface.

## Security Watch Mode

During Compound Master execution, run Security Watch by default for the same high-risk surfaces. This is a read-only incremental pass during `work`, not the final verdict.

Security Watch should:

- inspect changed files and worker summaries as they appear;
- identify changed trust boundaries and sensitive surfaces;
- suggest negative/security verification while the context is fresh;
- record early concerns for the final Security Sentinel Gate;
- stop immediately only for obvious P0/P1 risk.

Security Watch must not:

- edit files;
- stage, commit, push, create PRs, or transition Jira;
- run intrusive scanners or mutate runtime state;
- decode, print, or store secrets;
- replace the final Security Sentinel Gate.

## Input From Compound Master

Request:

- work package path;
- origin plan path;
- changed files/diff summary;
- Impact Scan summary;
- Security Watch notes, when available;
- surface-aware verification evidence;
- current branch and intended base;
- known skipped tests or local blockers;
- release/Jira/PR context when available.

## Output To Compound Master

Return:

```text
Security status: pass | fixes needed | blocked | advisory only

Blocking findings:
- [P0-P2] <title>
  Evidence:
  Remediation:
  Verification:

Advisory findings:
- [P3] <title>

Required verification:
- <tests, manual checks, scans, config inspections>

Release notes for handoff:
- <internal release-readiness notes only>
```

## Routing Rules

- P0/P1 findings block release handoff.
- P2 findings block when they affect auth, tenant isolation, secrets, public API security, PII, or deployment exposure.
- P3 findings are advisory unless the user or repo policy marks them blocking.
- Route code/config fixes through the normal Compound Master work/review loop.
- Do not ask Release Marshal to hide or bypass unresolved security risk.
