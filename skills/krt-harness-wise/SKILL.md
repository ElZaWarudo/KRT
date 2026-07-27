---
name: krt-harness-wise
description: Create versionable coding harness artifacts from project documentation and agent initialization context, or diagnose and improve an existing harness. Use when a user asks to prepare a coding handoff, create/update a harness file, inspect current harness quality, or make implementation context compact before planning/work. Runtime aliases may expose this as krt:harness-wise.
---

# Harness Wise

Create or improve coding harness artifacts. A harness is a compact, versionable markdown handoff that tells a later planning or coding agent what objective to pursue, which project documentation and initialization rules matter, what context to read, what guardrails apply, what risks remain, and how to validate safely.

Harness Wise has two jobs:

1. **Create a harness** from project documentation, agent initialization context, and task-relevant evidence.
2. **Diagnose and improve a harness** when an existing harness is referenced or discovered.

It does not implement application changes, write tests, edit migrations, change deployment config, create general project docs, commit, push, open PRs, or mutate external systems.

## Arguments

```text
[task description or harness path]
[mode:create|mode:diagnose|mode:auto]
[harness:<repo-relative-path>]
[local-only:true|false]
```

Defaults:

- `mode:auto`: diagnose when a harness path is provided or a strong candidate exists; otherwise create.
- `local-only:false`: write versionable harnesses under `docs/harnesses/` unless the user explicitly requests temporary/local-only output.

## Core Rules

- Load `references/safety.md` before beginning the workflow.
- Keep the canonical skill identity `krt-harness-wise`.
- Build harnesses from documentation, initialization files, and narrowly relevant project evidence. Do not read the whole source tree by default.
- When the source evidence is still in `.pdf` or `.docx`, use `krt-document-forge` first and consume the generated Markdown artifacts instead of converting binary documents inline.
- Treat `docs/harnesses/sources/`, `images/`, `staging/`, and `provenance/` as local-only evidence.
- Never use an unpromoted staged summary as a versionable read target. Validate its sidecar and promote it deterministically first.
- Classify promoted `docs/harnesses/summaries/*.md` as `Read First`; never add raw source, image, manifest, provenance, hash, or staging paths to a versionable harness.
- Before writing versionable harnesses from client, commercial, internal planning, or converted source evidence, load `references/publication-safety.md` and sanitize business-sensitive and personal information.
- Do not write generated source Markdown, raw converted text, source document hashes, exact budgets, named RACI/escalation paths, personal contact details, or unnecessary client identifiers into versionable harnesses.
- Always inspect relevant agent initialization context before finalizing a harness: `AGENTS.md`, local agent config, and skill/runtime metadata when present.
- When confidence is high, task scope is clear, and the output path is obvious, write or patch the harness artifact without asking another confirmation.
- Ask one focused question before writing when the objective, harness target, or update/regeneration decision is ambiguous.
- Diagnose an existing harness before replacing it.
- Use deterministic scripts for mechanical discovery and validation; treat script output as evidence, not semantic judgment.
- Do not recommend or instruct the next agent to invoke `krt-harness-wise` from inside the generated harness.
- Writing a harness file never implies commit, push, Jira, PR, merge, or release approval.

## Progressive Loading

Load only what the current flow needs:

| Need | Load |
|---|---|
| Create a new harness | `references/create-harness.md`, `references/harness-schema.md`, `references/agent-initialization-context.md`, `references/context-budget.md` |
| Diagnose or patch existing harness | `references/diagnose-harness.md`, `references/harness-schema.md`, `references/deterministic-validation.md` |
| Client/commercial/internal evidence may become versionable | `references/publication-safety.md` |
| Use scripts | `references/deterministic-validation.md` |
| Validate expected behavior | `references/validation-scenarios.md` |

Bundled scripts:

```text
scripts/find_agent_init.py
scripts/find_harness.py
scripts/check_harness.py
scripts/check_evidence.py
scripts/promote_evidence.py
scripts/publication_safety.py
```

Resolve `<harness-wise-skill-dir>` to the directory containing this `SKILL.md`; in installed runtimes this may not be the repository checkout.

## Workflow

1. Interpret the user's request and choose `create` or `diagnose`.
2. Run deterministic discovery when useful:
   - `find_agent_init.py` to locate initialization context.
   - `find_harness.py` to find likely existing harnesses.
3. Load the flow-specific reference.
4. Load `references/publication-safety.md` when the evidence includes client, commercial, internal planning, converted document, or potentially sensitive material.
5. For converted evidence, complete `inspect → classify → redact → promote`: require a staged summary plus sidecar, run `check_evidence.py`, resolve warnings explicitly, and run `promote_evidence.py`.
6. Read only the promoted summary, project docs, initialization files, and narrow evidence needed for the harness decision.
7. Create, patch, or recommend regeneration. Never copy ignored evidence into the harness.
8. Run `check_harness.py` on any written or reviewed harness when a file path is available.
9. Return the harness path/status, diagnosis summary if applicable, validation and promotion results, publication-safety status, and any deferred verification.

## Output Discipline

For created or updated files, report:

- Harness path.
- Status: `draft`, `ready`, `blocked`, or `review`.
- Initialization context used.
- Validation result.
- Publication-safety result.
- Remaining blocking questions or deferred verification.

For diagnosis-only output, lead with findings and verdict before any summary.
