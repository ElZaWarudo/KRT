---
name: krt-ci-questor
description: Investigate CI/CD failures and produce concise cause reports. Use when a user asks why a GitHub Actions, GitLab CI, CircleCI, Jenkins, or other pipeline failed; needs log triage, flaky-test assessment, runner/dependency/config diagnosis, failed-check summaries, rerun guidance, or a simple report explaining what happened and what to do next. Runtime aliases may expose this as krt:ci-questor.
---

# CI Questor

CI Questor investigates failed pipelines like a court examiner: gather the run evidence, isolate the first useful failure, separate real regressions from CI instability, and return a short report with cause, confidence, and next action.

It may suggest fixes, reruns, or deeper diagnostics. It does not change CI configuration, rerun jobs, push commits, approve bypasses, or mutate remote CI state unless the user explicitly asks.

## Load References

- Load `references/investigation-playbook.md` before diagnosing a CI failure.
- Load `references/report-template.md` before writing the final report.
- Load `references/source-literature.md` when explaining the diagnostic model or when the user asks what the workflow is based on.

## Workflow

### Step 1 - Establish The Run

Identify the failing system and exact run:

- provider, repository, branch, commit SHA, PR/MR, workflow/pipeline, job, step, and timestamp;
- whether the run is current, rerun, cancelled, skipped, timed out, or infrastructure-failed;
- whether the failure blocks merge, release, deployment, or only an optional check.

If the user gives only "CI failed", inspect available local context first: `.github/workflows/`, `.gitlab-ci.yml`, `.circleci/config.yml`, Jenkinsfiles, package scripts, lockfiles, and recent git diff. Ask only if no run or log source can be determined.

### Step 2 - Gather Evidence

Prefer structured evidence over broad guessing:

- fetch or read job logs, annotations, check summaries, artifacts, test reports, and workflow configuration;
- inspect the first failing step and the first actionable error above generic exit-code lines;
- after the first actionable failure is understood, inspect neighboring tests/assertions and likely related cases before recommending a PR update; deterministic failures can be hidden behind the first red assertion;
- for domain normalization, serialization, contract, fixture, or status/value changes, search adjacent concepts and aliases across the affected test area, not only the exact failed line;
- compare the failing commit with the previous passing run when available;
- check whether dependencies, images, runners, caches, secrets, variables, or external services changed;
- preserve secret hygiene: never print tokens, credentials, masked values, or full environment dumps.

Use provider CLIs when available (`gh`, `glab`, `circleci`, Jenkins CLI/API), but keep the report useful when only pasted logs are available.

### Step 3 - Classify Cause

Assign one primary class and optional secondary factors:

- **Code regression:** changed code broke tests, build, lint, typecheck, packaging, or deployment.
- **Test issue:** test expectation, fixture, selector, timing, isolation, or nondeterminism problem.
- **Dependency/toolchain drift:** package, lockfile, image, runtime, action, plugin, registry, or transitive version changed.
- **CI configuration:** trigger, path filter, rules/conditions, matrix, cache, artifact, permissions, timeout, or job wiring issue.
- **Runner/infrastructure:** runner capacity, filesystem, network, DNS, service container, resource limits, or hosted-provider incident.
- **Secret/environment:** missing, renamed, scoped, expired, masked, or unavailable variable/secret.
- **External service:** API, database, package registry, browser service, cloud provider, or test dependency outage.
- **Unknown:** evidence is insufficient; state exactly what evidence would reduce uncertainty.

Do not call a failure flaky just because rerunning is easy. Require evidence such as pass/fail on the same commit, known flaky signature, nondeterministic symptom, resource contention, network/dependency errors, or history of the same test/job alternating outcomes.

### Step 4 - Decide Action

Choose the smallest useful next move:

- local reproduction command when the job maps cleanly to repo scripts;
- verification ladder for deterministic test/build fixes: use a minimal targeted command for diagnosis, then a natural sub-suite when the test depends on shared setup, then the repo-specific command equivalent to the affected CI job before saying the fix is ready to push;
- targeted rerun when evidence points to transient flake or infrastructure;
- CI config patch when the pipeline definition is wrong;
- code/test fix when the failure is deterministic and tied to the diff;
- dependency pin/update when a version drift caused the break;
- follow-up issue when the build can be unblocked but the underlying flake needs ownership.

Derive the CI-equivalent command from the repository's workflow/job definition, package scripts, Makefile, task runner, or documented local commands. Do not hardcode commands from another project. If the equivalent command cannot run locally, report the blocker and say the PR update would be unvalidated unless the user explicitly overrides.

Targeted selectors are diagnostic evidence, not shipping evidence, when the test has global hooks, shared fixtures, seeded state, or suite-level setup. If a selector fails differently from CI because setup is incomplete, treat the selector result as inconclusive and validate with the natural suite or CI-equivalent job command.

Ask before recommending a red-build bypass, disabling tests, widening retries, changing release gates, or accepting a reviewer-visible risk.

### Step 5 - Report

Return a concise report using `references/report-template.md`. Include:

- what failed;
- most likely reason;
- supporting evidence;
- confidence;
- whether this looks flaky/transient or deterministic;
- recommended next action;
- verification performed or skipped.

Keep the report readable enough to paste into a PR, Jira issue, or team chat.

## Guardrails

- Start from evidence, not provider folklore.
- Prefer the first actionable error over the last noisy line.
- Diagnostic runs may be targeted; PR-ready fixes need parity with the affected CI job or an explicit unvalidated gap.
- Never expose secrets or full environment output.
- Do not hide an unresolved deterministic failure behind retries.
- Do not propose disabling a failing check unless there is a linked follow-up and explicit user approval.
- Keep reports short; put raw logs only in evidence references, not in the narrative.
