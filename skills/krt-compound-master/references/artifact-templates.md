# Artifact Templates

Use this reference when Compound Master writes work packages, artifact closeouts, or final summaries.

Roadmap and readiness report templates are owned by the resolved `roadmap_generator` role, canonically `krt-roadmap-cartographer`. Compound Master consumes those artifacts; it does not define their canonical shape here.

## Work Package

Path:

```text
docs/work-packages/RDM-###-<roadmap-item-slug>/YYYY-MM-DD-NNN-<package-slug>-work-package.md
```

Use a work package as a delivery container. Its review units are the default atomic PR/Jira units. A work package may include one roadmap item, one plan U-ID, or a cohesive group of U-IDs, but it should define smaller review units when the package spans multiple review surfaces. Do not store all work packages in one flat directory; organize them under the roadmap item folder they belong to.

Default `jira_policy` to `optional`: review units should carry Jira-ready summaries and descriptions because Jira is important delivery traceability, but lack of Jira role/config/context should not block package creation or execution. Use `required` only when the user, repo, or active delivery contract explicitly makes Jira mandatory; use `skip` only when the user explicitly opts out.

Split review units when units have independent value, minimal file overlap, separate risk domains, clean independent verification, large generated artifacts, large schema dumps, or orchestration docs that would obscure functional review. Combine only when units share migrations/API contracts/core files, depend tightly on each other, or would create noisier stacked PRs than a single review. A package may implement the full roadmap item in one integrated PR only when the plan units have strong integration/dependency coupling; this must be explicit in the grouping rationale.

Review-unit size guardrails:

- Target <=500 human-authored changed lines per PR.
- Treat >900 human-authored changed lines as a warning requiring split consideration.
- Require an explicit split/rationale above ~1,000 human-authored changed lines.
- Count generated artifacts, `*.auto.*` dumps, and orchestration docs separately; separate them from functional logic when they dominate review volume.
- Do not silently drop, stash, or defer related documentation only to keep a PR narrow. If planning/orchestration docs or product/operator/API docs explain the implemented change, clarify stack/base context, or backfill stale docs for nearby landed behavior, keep them in the branch and normally in the PR; split only when they materially obscure review and record the rationale.
- Do not move related documentation into stash-only state, a side worktree, or an unreferenced branch just to protect PR neatness. When a split is explicitly approved, record where the docs will land and how that follow-up will be shipped.
- Do not create a dedicated planning/docs branch just to hold these artifacts. Until execution starts, keep them on the active integration branch; when RU1 begins, move forward on the first semantic implementation branch that ships the related capability.

Work packages must align with origin plan units. A package may combine or split units, but it must make that relationship explicit and justify it. If a plan defines U1-U5, the package must say which of those units are included, excluded, deferred, or split into another package.

```markdown
---
title: [Work package title]
status: ready
roadmap_item: RDM-###
origin_roadmap: docs/roadmaps/...
origin_brainstorm: docs/brainstorms/...
origin_planning_input: docs/brainstorms/...
origin_plan: docs/plans/...
units: [U1, U2]
unit_alignment: complete|partial|split
review_units: [RU1, RU2]
base_branch: [integration branch or parent branch]
pr_strategy: [independent|stacked]
jira_policy: [required|optional|skip]
production_posture: [unknown|live|preprod|prototype]
autonomy: [manual|guarded|high]
autonomous_ledger: [none|docs/orchestration/autonomy-ledgers/<contract-id>.json]
allowed_mutation_classes: []
---

# [Work package title]

## Scope
[Only what this package implements]

## Non-goals
[Explicit exclusions]

## Autonomy Contract
- Mode: [manual|guarded|high]
- Agent may decide without asking: [reversible, package-local choices such as internal naming, equivalent verification commands, small fixture/test updates, convention-following implementation details]
- Agent must record as assumptions: [repo conventions inferred, low-risk path choices, skipped verification with blocker, compatible adjustments]
- Agent must escalate: [product behavior, authorization/tenant/data contracts, destructive data operations, public API breakage, production deployment/rollback impact, branch/base strategy, Jira/PR workflow, credentials, paid external resources, or scope outside this package]
- Safe fallback: [continue exploration/tests/implementation that do not depend on the blocked decision; otherwise return the blocked decision and exact next question]
- Autonomous ledger: [none / repo-relative ledger path]
- Allowed external mutation classes: [only when a valid ledger authorizes them; otherwise none]

## Dependencies
- Requires: [None / package IDs / branch / PR]
- Blocks: [package IDs]

## Production Posture
- Posture: [unknown|live|preprod|prototype]
- Evidence: [user statement, docs/config/release evidence, or "not established"]
- Confidence: [high|medium|low]
- Consequences for this package: [compatibility expectations, migration/deployment caution, or speed/flexibility allowed]
- Breaking existing behavior allowed: [no / only with explicit approval / yes because prototype and approved]

## Plan Unit Alignment
| Plan unit | Included in this package | Reason |
|---|---|---|
| U1 | yes/no/partial | [Why included, excluded, deferred, or split] |

Grouping rationale:
- [Why these units belong in this package, where review-unit boundaries are drawn, and why any integrated PR is justified]

## Implementation Units
[Relevant U-ID summaries, preserving origin plan unit names and order]

## Review Units
| Review unit | Scope | Expected changed surfaces | PR base | Jira issue/subtask | Size/risk note |
|---|---|---|---|---|---|
| RU1 | [focused reviewable change] | [runtime/tests/generated/docs/etc.] | [develop/parent branch] | [new/reuse/skip] | [line estimate, generated/docs separated yes/no, split rationale if broad] |

Rules:
- Review units are the default PR/Jira handoff units.
- Keep docs/orchestration and large generated artifacts in separate review units only when that improves review more than it harms context. If the docs are part of explaining, operating, or backfilling the shipped behavior, prefer keeping them with the related review unit and split by commit only when that is enough.
- A separate review unit is still part of the same delivery story, not a dumping ground. Never leave the docs behind in a worktree or local branch without a named follow-up path in the artifact and closeout.
- If one review unit includes runtime logic plus generated files, require separate commit grouping for generated files and keep PR body sentences focused on user/reviewer-visible changes.

## Files and Tests
[Repo-relative files and expected tests]

## Impact Scan
- Changed API contracts/endpoints/bindings/helpers/schemas/payloads/auth/tenant/ownership/test fixtures: [None / list]
- Consumer scan patterns: [None / rg/search patterns]
- Consumers found: [None / repo-relative files and flows]
- Contract-drift tests searched: [None / exact-list expectations, snapshots, allowlists, role/permission bundle tests, normalization tests, seeded fixtures]
- Required consumer tests: [None / commands or test files]
- Consumer tests run/skipped: [commands/results, or skip reason and whether CI covers it]

## Verification Gate
- [Commands/outcomes that must pass]
- Surface-aware evidence: [changed surfaces and the test/inspection evidence for each]
- Production posture evidence: [for live/unknown systems, regression/compatibility/migration/rollback evidence required for touched surfaces; for prototype, note any intentionally relaxed checks]

## Review Gate
- Code review threshold: [configured `review-threshold`; default P0-P2]
- Findings below threshold: log unless user marks blocking

## Security Gate
- Run after work-review loop: [not required / required because auth, secrets, PII, public API, deployment, dependency, or other high-risk surface changed]
- Security Watch during work: [enabled/disabled and why]
- Security Watch notes: [None / early concerns, suggested verification, gate inputs]
- Security reviewer: [krt-security-sentinel / fallback security reviewer / inline]
- Security review result: [pending / pass / fixes needed / blocked / advisory only]
- Required security verification: [tests/checks/manual inspection]

## CI Break-Prevention And Escalation
- CI risk surfaces: [build/typecheck/lint/tests/generated artifacts/migrations/permissions/config/etc.]
- Preventive evidence: [local verification or explicit CI-only gap for each changed surface]
- If CI breaks: [invoke krt-ci-questor with PR/run/check context; do not poll checks in Compound Master]
- Escalation rule: [record release-follow-up blocker until the CI incident has cause, owner, and next action]

## Branch and PR Handoff Inputs
- Review unit: [RU# and title]
- Branch name: [feat/semantic-capability-slug-without-plan-or-review-unit-ids]
- Branch/docs rule: first executable review unit carries related planning artifacts on the same semantic branch; do not ship a separate `docs/*-planning` branch unless explicitly requested
- PR base: [develop/main/parent branch]
- Suggested commit grouping for this review unit:
  - [type(scope): summary] - [repo-relative files or surfaces] - [why this is one logical review unit]
  - [Split broad packages by changed surface: persistence/schema/model state; domain service/integration behavior; API/controller/generated contracts; config/deployment wiring; focused tests/fixtures; docs/orchestration. Omit surfaces that did not change.]
- PR title:
- PR body bullets:
- Verification results location:
- Production/deployment notes: [required for live/unknown systems when behavior, schema, config, or deployment changes; otherwise none]
- Autonomous mutation request: [none / mutation classes plus ledger path and latest audit hash]

## Jira Handoff Inputs
- Jira policy: [required|optional|skip]
- Suggested issue type: Tarea
- Suggested subtask behavior: create/reuse subtask when a real parent already exists or when this package has two or more sibling review units/work packages that should share one parent. Never plan a single parent task with a single child subtask; if there is only one Jira child, collapse to one standalone `Tarea` and attach PR backlink/comments/transition there. If a new parent is justified by multiple children, add the parent to the active sprint unless explicitly skipped
- Jira summary: [Spanish semantic title without roadmap/package numbers]
- Jira description: [Spanish concise scope/reason without roadmap/package numbers]
- Optional-policy fallback: if Jira role/config/context is missing, record "Jira omitted: <reason>" in state/release closeout and continue without asking solely whether Jira should be used
```

Review every package with `document_review`. Fix blockers before execution.

Before document review, run the mechanical package checker:

```bash
python3 <compound-master-skill-dir>/scripts/check_work_package.py <work-package.md>
```

## Human-Facing Handoff Text

Keep internal planning identifiers out of public/reviewer-facing text:

- Do not include `RDM-001`, `U1`, date sequences, package numbers, or work-package sequence numbers in Jira summaries/descriptions, commit messages, PR titles, PR body bullets, or branch names.
- Use semantic names that describe the capability or fix: `feat/tenant-permission-bundles`, not `feat/rdm-001-tenant-permission-bundles`.
- Jira summaries should be in Spanish and read like work items a teammate would understand without the orchestration plan.
- Jira descriptions should be in Spanish and explain scope and reason in concise prose, not restate roadmap IDs or package numbers.
- PR titles and commit messages should be value-oriented and conventional; put traceability in artifact metadata, PR dependency notes, or Jira links instead of the title.
- When commit messages or PR bodies include Jira traceability, include only the immediately relevant issue link/key. Use a subtask only when a real multi-child parent exists; otherwise use the standalone task. Do not include both parent and child unless the user or repo convention explicitly asks.
- Keep IDs only in internal fields such as `roadmap_item`, `units`, origin paths, dependency tables, and state.

## Artifact Closeout

When `mode:artifacts` stops, include:

- Roadmap path.
- Brainstorm paths.
- Plan paths.
- Work-package paths.
- State path.
- Dependency waves and recommended first package.
- Branch strategy summary.
- Blockers, or "No blockers".
- Exact next invocation, for example:

```text
Use krt-compound-master mode:execute package:<work-package-path> review-unit:<RU#> jira-policy:optional parallel:false
```

If no package is ready, say exactly why. If packages are ready, say artifact generation is complete and execution is intentionally waiting for an explicit user gate.

For `mode:full`, ask one execution gate after the artifact closeout:

```text
Artifacts are ready. Recommended next package: <work-package-path>.
Proceed with execution now?
```

## Final Summary

At the end, write:

```text
docs/orchestration/YYYY-MM-DD-compound-master-summary.md
```

Include roadmap, brainstorms, plans, packages, waves, branches, Impact Scans, security reviews, CI break-prevention evidence, surface-aware verification, review rounds, Jira tasks, PRs, surfaced CI incidents/escalations, blockers, residual advisory findings, completed packages, remaining packages by wave, and the next recommended invocation if work remains.
