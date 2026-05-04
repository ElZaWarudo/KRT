# Modes

Infer a mode when the user does not specify one. Prefer the smallest mode that can produce a useful harness without hiding important risk.

## Mode Selection

- **quick** - Small, local, low-risk work. Produce a compact harness with minimal scan, core context, guardrails, and validation.
- **deep** - Cross-cutting, architectural, high-risk, or ambiguous work. Include stronger pattern extraction, documentation classification, skill gap analysis, impact estimates, and risks.
- **bugfix** - Error reports, failing tests, regressions, stack traces, or "fix" requests. Prioritize reproduction, nearby tests, and regression coverage.
- **feature** - New behavior or capability. Prioritize existing patterns, contracts, models, UI/API surfaces, docs, and tests.
- **refactor** - Behavior-preserving cleanup. Prioritize public interfaces, callers, tests, compatibility, and characterization coverage when needed.
- **skill-audit** - User asks whether available skills are sufficient. Focus on skill inventory, required expertise, missing skills, and review skills.
- **harness-review** - User provides or references an existing harness. Review it against the harness contract instead of generating a duplicate by default.
- **docs-trim** - User asks to reduce docs/context. Classify docs and produce task-oriented summaries or ignore lists.

## Defaulting

- Start with **quick** for local, low-risk changes.
- Upgrade to **deep** for architecture, security, migrations, external integrations, many affected surfaces, or stale/contradictory docs.
- Use task-specific modes when the user's wording is explicit: "bug", "feature", "refactor", "audit skills", "review this harness", "trim docs".
- If a harness file or pasted harness is present, use **harness-review** unless the user explicitly asks to regenerate from scratch.

## Mode Output Differences

| Mode | Keep Compact | Add Depth |
|------|--------------|-----------|
| quick | Objective, read-first context, core guardrails, validation | Only material risks |
| deep | No | Full source ranking, docs labels, skill gaps, impact matrix, risks |
| bugfix | Reproduction context, target files, tests | Regression and failure-path risks |
| feature | Existing patterns, contracts, tests | Cross-surface impact and rollout/docs impact |
| refactor | Behavior boundary and tests | Compatibility and caller analysis |
| skill-audit | Skill inventory and gaps | Missing skill proposals and review timing |
| harness-review | Findings and recommended patch | Regeneration criteria if weak |
| docs-trim | Doc labels and summaries | Staleness and contradiction checks |

## Blocking Behavior

Block only when product or scope uncertainty would make the harness actively misleading. Do not block on technical unknowns that can be verified later; mark them as assumptions or deferred verification.

## Existing Harness Handling

In `harness-review` mode:

- Review the supplied harness first.
- Do not generate a duplicate harness unless the review concludes regeneration is better than patching.
- Use review labels from `references/harness-review.md`.
- Preserve useful sections and recommend minimal changes when the harness is salvageable.
