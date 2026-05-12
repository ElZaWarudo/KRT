---
name: krt-state-archivist
description: Compact Compound Master state artifacts while preserving full historical detail in linked archive files. Use when compound-master-state.md or other Compound Master orchestration state has grown too large for efficient context loading, when krt-compound-master is about to resume from a long state file, after major Compound Master gates, before long closeouts, or when the user asks to clean, compact, archive, trim, or curate Compound Master generated documents.
---

# State Archivist

State Archivist keeps Compound Master state usable as a resume entrypoint. It preserves the full record, but moves old narrative and evidence out of the live context path.

## Load References

- Load `references/state-contract.md` before compacting or reviewing a Compact State scaffold.

## Workflow

### Step 1 - Identify The State File

Prefer `docs/orchestration/compound-master-state.md`. If the user points to another file, use that path. If only `compound-master-state.md` exists at the repo root, use it and keep all generated archive paths repo-relative.

Do not compact unrelated project documentation. This skill is for Compound Master orchestration state and adjacent generated state artifacts.

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
