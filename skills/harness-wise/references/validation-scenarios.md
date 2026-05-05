# Validation Scenarios

Use these scenarios when changing the skill. The goal is to test whether the skill produces compact, grounded harnesses without leaking expected answers into the prompt.

Across all scenarios, the skill should stay a helper for coding harnesses. It should not introduce an `agentic-system` mode, runtime architecture checklists, tracing stacks, sandbox platforms, evaluation platforms, or self-recommendations for `$krt:harness-wise` unless the user explicitly asks for those topics.

## Scenario 1: Small Bugfix

Prompt:

> Use $krt:harness-wise for a bug where `orders total` is wrong when a discount is zero.

Expected qualities:

- Mode is `bugfix`.
- Prioritizes reproduction, target code, nearby tests, and regression coverage.
- Does not ask for broad architecture docs unless the repo scan makes them relevant.
- Keeps reading scope compact and bounded to likely symbols, code paths, tests, and documents.
- Technical unknowns such as exact test command are deferred verification, not blockers.

## Scenario 2: Medium Feature

Prompt:

> Use $krt:harness-wise before adding CSV export for invoices.

Expected qualities:

- Mode is `feature` or `deep` if multiple surfaces are detected.
- Identifies contracts, models/services, UI/API entry points, tests, and docs.
- Estimates impact across backend, frontend, API, tests, docs, and deployment.
- Includes a compact task-relevant project or module map when several areas must coordinate.
- Summarizes observed conventions the next agent should follow when they affect implementation.
- Separates inspected evidence from assumptions and deferred verification.
- Includes validation boundaries that match the touched surfaces.
- Recommends relevant skills only when they reduce risk.

## Scenario 3: Docs Trim

Prompt:

> Use $krt:harness-wise docs-trim for this repo before implementing billing changes.

Expected qualities:

- Mode is `docs-trim`.
- Classifies docs as KEEP, SUMMARIZE, IGNORE, STALE, or ASK/VERIFY.
- Produces task-oriented summaries rather than generic doc summaries.
- Protects context by ignoring unrelated deployment, legacy, or theme docs unless relevant.

## Scenario 4: Vague Architecture Request

Prompt:

> Use $krt:harness-wise to prepare a harness for improving the architecture.

Expected qualities:

- Does not invent scope.
- Asks one product/scope question if the target architecture concern is unclear.
- If enough context exists, marks classification confidence low and identifies verification items.
- Avoids coding or prescribing a new architecture without evidence.

## Scenario 5: Skill Audit

Prompt:

> Use $krt:harness-wise skill-audit for a task involving database migrations and backward compatibility.

Expected qualities:

- Mode is `skill-audit`.
- Separates available, missing, review-only, and unverified skills.
- Suggests specific missing skills such as migration safety or backward compatibility review when not visible.
- Includes confidence on skill inventory.

## Scenario 6: Existing Harness Review

Prompt:

> Use $krt:harness-wise to review this harness before coding:
>
> # Coding Harness
> Objective: Add invoice CSV export.
> Context: Read the entire repo and all docs.
> Plan: Implement it.

Expected qualities:

- Mode is `harness-review`.
- Produces findings before replacement.
- Marks broad "read the entire repo and all docs" as `Overloaded`.
- Includes an existing harness summary before recommending changes.
- Marks missing source-of-truth ranking, bounded reading scope, evidence/confidence, risks, and validation.
- Recommends patching or regenerating based on severity.

## Scenario 7: Sparse Repo

Prompt:

> Use $krt:harness-wise before creating the first feature in this empty repo.

Expected qualities:

- Produces a useful low-confidence harness.
- Avoids inventing architecture.
- Recommends first conventions/files to establish.
- Proposes persistent project maps or conventions docs only as opt-in next steps.
- Clearly separates assumptions from verified facts.

## Scenario 8: Shell Or Infrastructure Risk

Prompt:

> Use $krt:harness-wise before adding a CLI command that shells out to deploy generated artifacts.

Expected qualities:

- Identifies shell, filesystem, network, infrastructure, and external side effects as risk surfaces.
- States what the next agent may inspect or implement directly after summarizing intended changes versus what needs confirmation because it is destructive, affects external systems, or cannot be recovered with git.
- Includes relevant validation and review steps for command behavior and failure handling.
- Does not require a production sandbox, tracing system, or evaluation platform unless the repository task itself calls for one.

## Scenario 9: Project Intelligence Request

Prompt:

> Use $krt:harness-wise to map the project structure and conventions before adding billing reports.

Expected qualities:

- Produces task-relevant project intelligence, not a whole-repo inventory.
- Summarizes relevant entry points, modules, tests, docs, and observed conventions.
- Identifies reusable context gaps or optional persistent artifacts only when they would help repeated future work.
- Frames `docs/project-map.md`, `docs/conventions.md`, or saved harness files as follow-up proposals for planning/work execution, not files created by the skill itself.
- Does not add a new formal mode or recommend `$krt:harness-wise` inside the generated harness.
