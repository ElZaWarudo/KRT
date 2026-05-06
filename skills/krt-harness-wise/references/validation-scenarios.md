# Validation Scenarios

Use these scenarios when changing the skill. The goal is to test whether the skill produces compact, grounded harnesses without leaking expected answers into the prompt.

Across all scenarios, the skill should stay a helper for coding harnesses. It should not introduce an `agentic-system` mode, runtime architecture checklists, tracing stacks, sandbox platforms, evaluation platforms, or self-recommendations for `$krt:harness-wise` unless the user explicitly asks for those topics.

When changing the harness structure itself, expected qualities should be justified against `harness-structure-research.md` rather than personal preference alone.

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
- Proposes saving the harness to a concrete path if the repo scan suggests the feature spans enough surfaces to benefit from a persistent handoff, but does not write the file unless asked.

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
- Identifies reusable context gaps or optional persistent project artifacts only when they would help repeated future work.
- Frames `docs/project-map.md` and `docs/conventions.md` as follow-up proposals for planning/work execution, not files created by the skill itself.
- Does not add a new formal mode or recommend `$krt:harness-wise` inside the generated harness.

## Scenario 10: Saved Harness File

Prompt:

> Use $krt:harness-wise and generate a harness file for adding invoice CSV export.

Expected qualities:

- Creates a markdown harness file rather than only returning the harness in chat.
- Uses an existing harness directory if present, otherwise defaults to `docs/harnesses/invoice-csv-export.md`.
- Includes the required `type: coding-harness` frontmatter with task, status, scope, confidence, created, and updated.
- Uses the Coding Harness Template with required saved-file sections.
- Does not create application source files, tests, migrations, configs, or general project docs.
- Reports the created file path and any blocking questions or deferred verification.

## Scenario 11: Ambiguous Generated Files

Prompt:

> Use $krt:harness-wise to generate the files for the billing refactor.

Expected qualities:

- Interprets "files" as harness artifacts because the request is in a harness-wise context, unless the user clearly asks for application code.
- Creates one compact harness file for the billing refactor, or asks one blocking question if the refactor scope is too vague to create a useful harness.
- Does not start implementing billing refactor code.
- Keeps project intelligence task-relevant and avoids whole-repo project maps unless needed for the handoff.

## Scenario 12: Proactive Saved Harness Proposal

Prompt:

> Use $krt:harness-wise before modernizing the billing architecture.

Expected qualities:

- Produces a response-only harness unless the user asks to save it.
- Proposes a saved harness path such as `docs/harnesses/billing-architecture-modernization.md` because the work is architectural and likely to span sessions or handoffs.
- Explains in one sentence why persistence helps.
- Does not write the harness file without user confirmation.
- Does not propose project maps or convention docs as already-created files.

## Scenario 13: No Saved Harness Proposal For Tiny Work

Prompt:

> Use $krt:harness-wise before renaming one private helper method.

Expected qualities:

- Produces a compact quick-mode harness.
- Does not propose a saved harness file unless the repo scan shows unusual risk, repeated handoffs, or broad impact.
- Keeps context and validation proportional to the tiny local change.
