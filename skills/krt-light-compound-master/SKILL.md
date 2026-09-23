---
name: krt-light-compound-master
description: Experimentally take a bounded software work package from context through implementation, verification, risk-based review, and release handoff with one compact state record. Use when requested directly or as a krt-light-seneschal child. Use full krt-compound-master when formal initiative artifacts are required.
---

# KRT Light Compound Master

Deliver a bounded software outcome with the same broad stages as
`krt-compound-master`: clarify, plan, implement, verify, review, and hand off
release. This is an experimental sibling, not a replacement for the full
skill's artifact contracts. Do not run both Masters on one active package
without an explicit migration decision.

## Entry and modes

Accept `mode:plan|execute|full|resume|status`, a work-package or review-unit
path when available, and optional `run-id`, `state-path`, `orchestrator:standalone|seneschal`,
`initiative-contract`, and `interaction:direct|brokered`.

- `plan`: produce or refresh a concise execution brief and stop before code.
- `execute`: implement a ready brief or reviewed existing work package.
- `full`: plan and execute when the request already authorizes both.
- `resume`: inspect live facts and the state record before continuing.
- `status`: report current evidence and next action without mutation.

Use the full Compound Master when the request requires a program roadmap,
separate reviewed brainstorm and plan artifacts, formal work-package schema,
or its autonomous artifact pipeline. A clear single task does not need either
Master unless its delivery benefits from the extra coordination.

## Context and one state record

Inspect the repository, current changes, user request, and relevant existing
requirements. Preserve unrelated work. Reuse an approved initiative contract
and assigned roadmap item; do not create a competing roadmap. If scope,
acceptance, dependencies, production posture, or a consequential decision is
unclear, investigate what the repository can settle and raise the remaining
decision. Do not invent product behavior, auth or data rules, compatibility,
or release policy.

For a short standalone run, use the conversation as state. Persist one Markdown
file when resumption, nested operation, or an audit trail is needed. A nested
parent supplies a unique `state-path`; standalone persistent runs default to
`docs/orchestration/light-compound-master/<run-id>.md`. Keep it current:

```text
Run / owner / source base / assigned unit / current phase
Scope, non-goals, acceptance, dependencies, open decisions
Owned paths and implementation approach
Checks: exact command, result, candidate revision, gaps
Review: risk, independent actor when required, revision, findings
Status: ready, needs-fix, blocked, or release-ready; next action
Release: scope/base, known CI gaps, authorization or handoff status
```

An existing reviewed work package can supply the scope and acceptance facts;
link it rather than copying its contents. For a new bounded task, the record's
scope and approach are its execution brief. Review the brief with the user or
a relevant specialist only when an unresolved decision or consequential risk
requires it. Do not create a roadmap, brainstorm, plan, package, and review
document merely because this skill is active.

## Execute and verify

Use one primary implementer. Delegate only when a distinct specialist, long
bounded unit, or genuinely independent workstream has a named benefit. Give a
worker exact ownership, acceptance criteria, focused checks, and stop
conditions. Workers do not ship or alter Jira. Isolate concurrent mutable
workers and keep overlapping auth, data, migrations, public contracts,
generated files, and dependencies serial.

Inspect the actual diff and run focused checks. Check affected consumers,
generated output, migrations, and build or type checks when the change reaches
those surfaces. Run aggregate or CI-equivalent checks once on the final
candidate; reuse passing evidence only when command, base, and relevant
content are unchanged. Record any CI-only gap without predicting a pass.

Review depth follows consequence:

- Routine reversible work: primary-agent final-diff review.
- Material behavior or compatibility: one independent reviewer on the changed
  diff and a named question.
- Auth, privacy, cryptography, data integrity, migration, public contract,
  production, or research-evidence integrity: specialist review plus
  independent validation of the named invariant. Use `krt-security-sentinel`
  for security-sensitive changes when available.
- Destructive, irreversible, legal/compliance, or publication-critical work:
  coordinate independent reviews for distinct risks and satisfy the applicable
  approval gate.

Fix material findings, run their focused checks, and reinspect affected code.
Repeat aggregate checks or review only if the fix invalidates earlier evidence
or changes the reviewed risk boundary. Do not mark failed or missing checks as
passing. Report a blocker after bounded attempts rather than looping without
new information.

## Nested under Light Seneschal

Accept `orchestrator:seneschal`, stable `run-id`, unique `state-path`,
`interaction:brokered`, inherited initiative contract when present, and one
assigned roadmap item, work package, or review unit. Limit work to that target;
do not launch sibling runs or ship. Treat the child state as canonical for its
unit and the parent's run record as a projection.

In brokered mode, return consequential decision requests to the parent with
the question, affected units, evidence, recommendation, and safe fallback.
Pause only affected work and continue independent local work. Resume from a
decision recorded in the initiative contract or other canonical artifact.
Return state path, status, changed paths, candidate revision, checks, review
results, blockers, sibling impact, and release readiness. The parent inspects
the diff, reconciles sibling units, and owns release handoff.

## Release and authority

Standalone release-ready work goes to `krt-release-marshal`; a nested run
returns it to Light Seneschal. The release owner handles commits, pushes, PRs,
Jira transitions, reviewers, and merges. Existing user authorization applies
within its stated scope; obtain approval for an action that lacks it. Local
implementation permission does not grant external, destructive, or production
authority. For unattended external mutations, use the canonical Compound
Master autonomy ledger and validator; otherwise record the action as blocked.
