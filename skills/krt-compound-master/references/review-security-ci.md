# Review, Security, And CI

Load for code review loops, high-risk security gates, optional reviewer fan-out, and CI incident handling.

## Code Review Loop

Preferred invocation:

```text
Skill("<code_review>", "mode:autofix plan:<origin-plan-path> base:<base-branch>")
```

Read-only fallback:

```text
Skill("<code_review>", "mode:report-only plan:<origin-plan-path> base:<base-branch>")
```

Loop:

1. Run review.
2. If safe autofixes were applied, rerun relevant tests.
3. Leave review-fix changes for `krt-release-marshal` commit planning unless project policy requires immediate commits.
4. If findings at or above threshold remain, route fixes through work/inline changes and rerun review.
5. Stop after three blocked rounds with clear blocker and next question.

Review pass requirements:

- No findings at or above configured threshold.
- Verification evidence complete for changed surfaces.
- Impact Scan complete when required.
- Security Watch notes, if any, have an owner or gate input.

## Cross-PR Finding Trace

At agentic speed a stacked chain can fix an earlier reviewer's finding before they re-read it. Keep that visible:

- Record each at/above-threshold finding in state keyed to its open PR.
- Before reviewing a new stacked unit, check whether it changes a surface flagged by an earlier still-open PR. If it fixes that surface, record `addresses finding from PR #X` and surface it in the earlier PR's review/release notes so the prior reviewer sees it is handled.
- Do not let a later unit silently resolve an earlier flagged issue; an unsurfaced downstream fix is a review-traceability gap, not a clean review.

## Security Watch During Work

Enable by default when a review unit touches auth, authorization, tenant isolation, secrets, PII, audit logs, destructive actions, public APIs, external integrations, deployment exposure, CI/CD permissions, dependencies, generated clients, or supply-chain surfaces.

Security Watch is read-only. It must not edit files, stage, commit, push, create PRs, transition Jira, run intrusive scanners, decode secrets, or mutate runtime state.

Record notes in state and feed them into the final security gate. P0/P1 risks may stop execution; P2/P3 concerns should not interrupt normal work.

## Security Sentinel Gate

After code review passes, run a focused security review for high-risk review units. Prefer `krt-security-sentinel`; otherwise resolve another security-review skill or perform a direct evidence-based security pass.

Required output:

- Reviewed surfaces.
- Security Watch notes considered.
- Findings by severity.
- Required fixes or advisory notes.
- Required security verification.
- Pass/fail/blocker.

Security blockers loop back through work and code review before release handoff.

## Optional Review Fan-Out

Use optional read-only fan-out when materially reducing risk:

- API contract or generated binding changes.
- Auth/tenant/permissions changes.
- Persistence/migration or production-sensitive changes.
- Large review unit that could not be split further.

Budget: at most three read-only reviewers. The lead deduplicates findings and decides which fixes are required.

## CI Break-Prevention And Escalation

Before release handoff, record predictable CI risk surfaces:

- build/typecheck/lint;
- unit/function/API tests;
- generated artifacts;
- migrations/schema dumps;
- permissions/config;
- project-specific checks.

For each surface, record local evidence or explicit CI-only gap. Do not poll CI in a loop.

If CI breaks later, use `krt-ci-questor` when available, resolve another CI investigator if possible, or perform direct evidence-first triage. Keep a release-follow-up blocker until the incident has cause, owner, and next action.

CI report shape:

```text
CI incident: reported | investigating | fix-needed | external | unknown
Provider/run:
Workflow/job/step:
Likely reason:
Evidence:
Ownership:
Recommended next action:
Verification:
Confidence:
```

Do not disable checks, widen retries, bypass red CI, or mark Jira done without explicit user approval.
