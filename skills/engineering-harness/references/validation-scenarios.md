# Validation Scenarios

Use these scenarios when changing the skill. The goal is to test whether the skill produces compact, grounded harnesses without leaking expected answers into the prompt.

## Scenario 1: Small Bugfix

Prompt:

> Use $engineering-harness for a bug where `orders total` is wrong when a discount is zero.

Expected qualities:

- Mode is `bugfix`.
- Prioritizes reproduction, target code, nearby tests, and regression coverage.
- Does not ask for broad architecture docs unless the repo scan makes them relevant.
- Technical unknowns such as exact test command are deferred verification, not blockers.

## Scenario 2: Medium Feature

Prompt:

> Use $engineering-harness before adding CSV export for invoices.

Expected qualities:

- Mode is `feature` or `deep` if multiple surfaces are detected.
- Identifies contracts, models/services, UI/API entry points, tests, and docs.
- Estimates impact across backend, frontend, API, tests, docs, and deployment.
- Recommends relevant skills only when they reduce risk.

## Scenario 3: Docs Trim

Prompt:

> Use $engineering-harness docs-trim for this repo before implementing billing changes.

Expected qualities:

- Mode is `docs-trim`.
- Classifies docs as KEEP, SUMMARIZE, IGNORE, STALE, or ASK/VERIFY.
- Produces task-oriented summaries rather than generic doc summaries.
- Protects context by ignoring unrelated deployment, legacy, or theme docs unless relevant.

## Scenario 4: Vague Architecture Request

Prompt:

> Use $engineering-harness to prepare a harness for improving the architecture.

Expected qualities:

- Does not invent scope.
- Asks one product/scope question if the target architecture concern is unclear.
- If enough context exists, marks classification confidence low and identifies verification items.
- Avoids coding or prescribing a new architecture without evidence.

## Scenario 5: Skill Audit

Prompt:

> Use $engineering-harness skill-audit for a task involving database migrations and backward compatibility.

Expected qualities:

- Mode is `skill-audit`.
- Separates available, missing, review-only, and unverified skills.
- Suggests specific missing skills such as migration safety or backward compatibility review when not visible.
- Includes confidence on skill inventory.

## Scenario 6: Existing Harness Review

Prompt:

> Use $engineering-harness to review this harness before coding:
>
> # Coding Harness
> Objective: Add invoice CSV export.
> Context: Read the entire repo and all docs.
> Plan: Implement it.

Expected qualities:

- Mode is `harness-review`.
- Produces findings before replacement.
- Marks broad "read the entire repo and all docs" as `Overloaded`.
- Marks missing source-of-truth ranking, skills, risks, confidence, and validation.
- Recommends patching or regenerating based on severity.

## Scenario 7: Sparse Repo

Prompt:

> Use $engineering-harness before creating the first feature in this empty repo.

Expected qualities:

- Produces a useful low-confidence harness.
- Avoids inventing architecture.
- Recommends first conventions/files to establish.
- Clearly separates assumptions from verified facts.
