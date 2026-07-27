# Repo Health Rubric

Use this rubric to keep Repo Medic findings actionable.

## Health Areas

| Area | Healthy Signals | Risk Signals |
|---|---|---|
| Contributor path | Setup, test, lint, build, and release instructions match current files | Missing setup, stale commands, undocumented required services |
| Build and CI | CI config matches documented commands; failures are diagnosable | Hidden requirements, flaky jobs, unclear status checks |
| Tests | Critical flows have obvious test homes and commands | Tests absent for core behavior, weak fixtures, no local/CI distinction |
| Documentation | Docs explain why and how, not only what; old docs are labeled or removed | Drift between docs and code, duplicate conflicting sources |
| Ownership | Code owners, review paths, or domain owners are discoverable | PRs depend on tribal knowledge or unclear reviewer routing |
| Delivery | Branch, release, Jira, PR, and rollback expectations are explicit | Release steps live only in memory or old tickets |
| Dependencies | Package managers and lockfiles are consistent; upgrade policy is visible | Unclear runtime versions, stale pinned dependencies, security unknowns |
| Operability | Logs, env vars, service startup, and incident/runbook paths are findable | Production-like behavior cannot be diagnosed from repo context |
| Skill portfolio | Canonical IDs, triggers, safety, scripts, tests/evals, and catalog entries agree | Routing overlap, metadata drift, missing negative/effect tests, unsafe or undocumented procedures |

## Severity

- **P0 acute blocker:** common local setup, CI, release, or security workflow cannot proceed.
- **P1 high friction:** repeated developer/reviewer pain, high risk of bad releases, or serious doc/code drift.
- **P2 maintenance debt:** meaningful cleanup that reduces future carrying cost.
- **P3 advisory:** useful but not urgent; do not let it crowd out higher-value work.

## Evidence Standard

Every finding needs:

- a stable root-cause ID that remains unchanged while the underlying problem remains the same;
- repo-relative evidence path or command observed;
- why it matters now;
- smallest useful next action;
- confidence level.

Suppress findings when evidence is weak and the recommendation would be vague.

Do not duplicate one systemic root cause for every affected skill. Keep affected skill IDs on one finding and use the per-skill matrix for row-level evidence. On a repeated audit, assign `new`, `persistent`, `changed`, or `resolved` only from current evidence.

## Prioritization

Favor prescriptions that:

- unblock common workflows;
- reduce review or release loops;
- make current truth discoverable;
- improve safety without creating heavyweight process;
- can be completed as a small PR or clear work package.
