# Review guide

Use for system-wide diagnosis, supply-chain and CI review, and severity calibration. Frameworks such as OWASP Top 10 and API Top 10, ASVS, NIST SSDF, and CIS Controls guide where to look; a category is never a finding by itself.

## System diagnosis inventory

Entry points (web, API, admin, CLI, jobs, queues, webhooks), identities (users, admins, services, CI and deploy actors), data stores and sensitivity, trust boundaries and network exposure, secret and config sources, build/release/deploy chain, logs and audit trails, runbooks and owners. Then rank by exploitable path, not checklist coverage.

## Tenant and object authorization

Check every path that reads or writes tenant data, not only request handlers: background jobs, exports, report generation, signed or generated URLs, caches keyed without tenant, admin impersonation, and test fixtures that share ids across tenants. Return the same "not found" for foreign and missing objects so ids can't be enumerated.

## Secrets

Verify references, scopes, and owners, not values. A committed credential needs rotation; history rewrite only helps if the commit was never pushed or cloned. Look for secrets in CI logs, error messages, example env files, container layers, and Helm values. Deploy and CI tokens should be least-privilege and per environment.

## Supply chain and CI

- Unpinned GitHub Actions, base images, or packages; lockfiles missing or ignored in CI.
- `pull_request_target` / `workflow_run` running PR-head code with secrets or a write token.
- `${{ github.event.* }}` (titles, branch names, bodies) interpolated into `run:` steps.
- Workflow `permissions` broader than needed; artifacts that expose secrets or build outputs to forks.
- Install scripts and generated clients from untrusted registries.

Name the trusted component, how trust is established, and what happens if it is compromised.

## Severity calibration

Raise severity for sensitive data, multi-tenant boundaries, admin actions, public exposure, and release or deploy credentials. Lower it when exploitation needs unrealistic access, the asset is low impact, or strong compensating controls are evidenced in the repo.
