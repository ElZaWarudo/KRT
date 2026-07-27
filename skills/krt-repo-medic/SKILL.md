---
name: krt-repo-medic
description: Diagnose repository and skill-portfolio health and produce focused maintenance prescriptions. Use for repo health checks, maintenance audits, stale docs, broken scripts, doc/code drift, CI/test hygiene, onboarding friction, dependency risk, delivery bottlenecks, skill catalog/metadata drift, routing overlap, missing safety wiring, weak skill tests/evals, or "what should we clean up" analysis. Runtime aliases may expose this as krt:repo-medic.
---

# Repo Medic

Repo Medic inspects a repository like a maintenance clinic: observe symptoms, check vital signs, separate acute blockers from chronic drift, and prescribe small, high-leverage follow-up work.

It does not implement fixes by default. It may propose concrete patches only when the user explicitly asks to fix or update files.

## Load References

- Load `references/safety.md` before beginning the workflow.
- Load `references/health-rubric.md` before scoring or prioritizing findings.
- Load `references/skill-portfolio-profile.md` for repositories containing a portfolio of agent skills.
- Load `references/source-literature.md` when explaining the reasoning model or when the user asks what the audit is based on.

## Workflow

### Step 1 - Intake

Classify the visit:

- **Quick check:** obvious drift, one area, or pre-PR confidence.
- **Standard audit:** repo-wide health across docs, tests, scripts, dependencies, and delivery.
- **Deep audit:** multi-service repo, repeated delivery pain, CI instability, stale onboarding, or release risk.
- **Skill-portfolio audit:** inventory every skill, trigger/overlap, metadata, safety, tests/evals, docs, and maintenance status.

Ask one blocking question only when the audit target is ambiguous enough to make findings misleading.

### Step 2 - Scan Vitals

Use targeted local reads before broad exploration:

- Inventory root docs, instructions, package/build/test config, CI, scripts, and skill/workflow docs.
- Compare docs against observable files and commands before claiming staleness.
- Check for missing or weak contributor paths: setup, test, lint, build, release, deployment, ownership, troubleshooting.
- Inspect recent git history only when it helps identify churn, stale branches, or recurring failure surfaces.
- Treat current code, tests, and executable config as stronger evidence than old prose.

For a skill portfolio:

- Build one matrix row per discovered skill using the portfolio profile.
- Check canonical folder/frontmatter/autocomplete identity, description-based routing, negative triggers, references, scripts, safety loading, tests/evals, catalog rows, and overlap.
- Consolidate repeated symptoms into one root-cause finding with a stable finding ID.
- Do not create or update portfolio snapshots automatically. Current evidence and an explicitly requested report are sufficient for this profile.

Do not run expensive tests or destructive commands unless the user asks. If a check would be useful but unsafe or slow, list it as a prescription.

### Step 3 - Diagnose

Use the rubric to classify findings:

- **Acute:** blocks setup, CI, releases, security, or common development workflows.
- **Chronic:** creates repeated friction, drift, unclear ownership, or slow review/maintenance.
- **Preventive:** low-cost cleanup that reduces future carrying cost.
- **Cosmetic:** nice but not worth interrupting delivery.

Each finding must include evidence, impact, confidence, and a recommended next action. Do not create a dumping ground of every imperfection.

For repeated audits, retain a finding's stable ID while its root cause remains the same. Mark it `new`, `persistent`, `changed`, or `resolved` only after checking current evidence; do not infer state from an old report.

### Step 4 - Prescribe

Return a compact health report:

```text
Overall status: healthy | watch | attention needed | blocked

Top findings:
- [severity] [area] Finding
  Evidence: path or command observed
  Impact: why this matters
  Prescription: smallest useful next action
  Confidence: high/medium/low

Deferred checks:
- [check] [why not run]

Suggested follow-up:
- [skill/workflow/task]
```

Prefer 3-7 findings. If there are more, group them by theme and recommend a roadmap/plan instead of overwhelming the user.

For a skill-portfolio audit, include the complete per-skill matrix before the deduplicated finding register. The 3-7 preference applies to root-cause findings, not matrix rows.

## Guardrails

- Do not shame the repo. Be concrete, calm, and evidence-based.
- Do not optimize metrics as goals. Use delivery metrics to guide improvement, not to pressure teams into gaming numbers.
- Do not recommend broad rewrites when a small documented fix would restore trust.
- Do not report a missing dependency, command, or doc without checking likely locations first.
- Do not mix implementation with diagnosis unless explicitly asked.
