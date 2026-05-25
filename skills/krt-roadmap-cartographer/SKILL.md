---
name: krt-roadmap-cartographer
description: >
  Generate exactly one roadmap or readiness report for a documented initiative.
  Validates context sufficiency, maps source-backed roadmap items, dependencies,
  waves, and branch/PR strategy, or blocks with actionable readiness guidance.
  Use when a user needs a roadmap before compound delivery, or when
  krt-compound-master resolves its required roadmap_generator role. Runtime
  aliases may expose this as krt:roadmap-cartographer.
metadata:
  argument_hint: "[initiative description or docs path]"
---

# Roadmap Cartographer

Roadmap Cartographer turns existing project context into exactly one primary artifact:

- a roadmap when context is sufficient;
- a readiness report when context is insufficient.

It does not orchestrate the rest of Compound Engineering. It does not update Compound Master state, review documents, invoke brainstorm/plan/work skills, commit changes, open PRs, or touch Jira.

## Load References

- Load `references/context-readiness.md` before deciding whether roadmap generation is safe.
- Load `references/artifact-templates.md` before writing either primary artifact.

## Non-Negotiable Rules

- Generate exactly one primary artifact per run: either a roadmap or a readiness report.
- Do not generate a draft roadmap when context is insufficient.
- Do not create auxiliary primary artifacts such as separate source inventories. Include necessary source inventory inside the single primary artifact.
- Do not convert uncertainty into roadmap scope. Record uncertainty as a blocker, user decision, risk, or readiness gap.
- Use repo-relative paths in generated documents.
- Source roadmap items from discovered context. If a claim is inferred, label it as an inference and include confidence.
- Ask one blocking question only when the answer determines whether roadmap generation is safe and cannot be inferred from available docs.
- Keep human-facing roadmap names semantic. Internal IDs such as `RDM-001` are for artifact traceability, not release text.

## Sources To Scan

Match scan depth to the initiative. Prefer existing context over broad exploration.

- Repo instructions: `AGENTS.md`, `CLAUDE.md` only as compatibility fallback.
- Product docs: `STRATEGY.md`, `README.md`, `docs/`, `specs/`, `architecture/`, `adr/`, `docs/adr/`.
- Execution docs: PRDs, feature specs, API contracts, schemas, migrations, runbooks, roadmaps, plans, brainstorms.
- Tooling and delivery docs: package/build/test configs, branch conventions, CI, releases, Jira, and PR conventions.

## Workflow

### Step 1 - Context Scan

Collect the source inventory and summarize what each source contributes. Keep this scan targeted to the initiative.

### Step 2 - Context Sufficiency Decision

Load `references/context-readiness.md`. Decide whether the minimum context is sufficiently covered.

If context is insufficient, create the readiness report from `references/artifact-templates.md` and stop.

If context is sufficient, continue to roadmap generation.

### Step 3 - Roadmap Generation

Load `references/artifact-templates.md`. Create the next roadmap path:

```text
docs/roadmaps/YYYY-MM-DD-NNN-<initiative-slug>-roadmap.md
```

Map roadmap items in dependency order. For each item, include outcome, why now, scope boundary, dependencies, risk, expected brainstorm path, expected plan path, and suggested package granularity.

### Step 4 - Closeout

Return a visible closeout with exactly one primary artifact classification:

```text
artifact_kind: roadmap | readiness-report
artifact_path: docs/...
blockers: <No blockers / concise blockers>
recommended_next_action: <exact next action>
```

When `artifact_kind` is `roadmap`, the recommended next action should be review by the caller's document-review role or the next Compound Master step.

When `artifact_kind` is `readiness-report`, the recommended next action must include an exact next prompt that helps the user produce the missing context.

## Output Ownership

Cartographer owns the canonical roadmap and readiness report shapes. Callers such as `krt-compound-master` consume the artifact path and kind, update their own state, review roadmaps, and decide whether to continue or stop.
