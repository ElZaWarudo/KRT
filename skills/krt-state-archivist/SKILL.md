---
name: krt-state-archivist
description: Compact Compound Master state artifacts while preserving full historical detail in linked archive files. Use when compound-master-state.md or other Compound Master orchestration state has grown too large for efficient context loading, when Compound Master live-context entrypoints such as SKILL/router docs have become diluted, when krt-compound-master is about to resume from a long state file, after major Compound Master gates, before long closeouts, or when the user asks to clean, compact, archive, trim, or curate Compound Master generated documents.
---

# State Archivist

State Archivist keeps Compound Master state usable as a resume entrypoint. It preserves the full record, but moves old narrative and evidence out of the live context path. The same pattern applies to explicit Compound Master instruction compaction: keep the live router short and move phase-specific detail into loaded references instead of deleting it.

## Load References

- Load `references/safety.md` before beginning the workflow.
- Load `references/state-contract.md` before compacting or reviewing a Compact State scaffold.

## Workflow

### Step 1 - Identify The State File

Prefer `docs/orchestration/compound-master-state.md`. If the user points to another file, use that path. If only `compound-master-state.md` exists at the repo root, use it and keep all generated archive paths repo-relative.

Do not compact unrelated project documentation. This skill is for Compound Master orchestration state, adjacent generated state artifacts, and explicit Compound Master live-context entrypoints when the user asks to reduce context load.

For Compound Master instruction compaction, do not run the state script. Apply the same live/archive split manually:

- Keep `SKILL.md` as a short router: purpose, arguments, progressive-loading map, core pipeline, universal hard rules, and stop discipline.
- Move phase-specific PR, Jira, execution, review, CI, autonomous, and delegation detail into the reference file loaded by that phase.
- Keep guardrails next to the action they prevent; checker-trust rules belong both in the orchestrator handoff and in the owning skill reference.
- Preserve behavior by moving or tightening rules, not deleting them. If a rule no longer belongs in live context, link to the reference that now owns it.
- Validate edited skills with the repository's skill validator before considering compaction complete.

### Step 2 - Run The Structural Harness

Use the script first unless the state is tiny or clearly malformed:

```bash
python3 skills/krt-state-archivist/scripts/compact_compound_state.py --state <state-path> --dry-run
```

Inspect the dry-run output. If it reports an ambiguous state, do not write. Ask for or infer the missing active phase only when there is enough evidence elsewhere in the repo.

When the dry-run is safe, run:

```bash
python3 skills/krt-state-archivist/scripts/compact_compound_state.py --state <state-path>
```

The script is a structural harness. It archives the full pre-compaction state, builds a compact scaffold, and refuses to write when it cannot identify an operational resume signal. It does not replace agent judgment.

### Step 3 - Curate The Compact State

Review the scaffold before considering the job done:

- Keep current initiative, mode, source paths, active package, branch/base, open PR/Jira references, blockers, required user decisions, and exact next invocation/action.
- Prefer the latest detected Phase/Fase block for scaffold signals. Treat older branch, PR, Jira, blocker, and review sections as historical unless they are repeated in the latest-phase window or confirmed from current repo/GitHub/Jira state.
- Keep historical phases as short summaries with links to archived detail.
- Remove repeated verification logs, old review loops, merged PR/Jira details, and decisions that are already captured in linked brainstorm/plan/work-package artifacts.
- Preserve repo-relative links to canonical artifacts.
- Do not delete detail that was not already archived.

If the scaffold misses an important active decision, add it concisely. If it includes historical noise, trim it and point to the archive.

### Step 4 - Update Compound Master State Expectations

When called from `krt-compound-master`, record that state archiving happened, including:

- compact state path;
- archive path;
- whether the script completed normally or the agent used a manual fallback;
- any ambiguity the next resume should know about.

If this skill is missing or blocked, Compound Master may continue inline, but it should record the degraded path.

## Guardrails

- Never treat compaction as permission to drop audit history.
- Never overwrite a state file unless a full archive snapshot has been written first.
- Never compact when the active phase, blocker, or next action is unclear and cannot be recovered from linked artifacts.
- Never trust scaffolded `Active Signals To Review` as final truth when the script marks `CURATION REQUIRED`; reconcile it with the latest phase, current branch/base, and current PR/Jira state first.
- Do not archive secrets or credentials into a new location if the state accidentally contains them; stop and ask for a redaction decision.
- Do not run formatters or broad cleanup against generated docs as part of state archiving.
- Keep the live state short enough to load before work resumes; the archive can stay long.

## Final Output

Return:

```text
State archive status: compacted | already-compact | blocked

State:
- <path>

Archive:
- <path or none>

Resume entrypoint:
- <current phase/status>
- <next action>

Notes:
- <ambiguities, manual edits, or "No blockers">
```
