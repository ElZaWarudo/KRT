# Document Classification

Classify docs by usefulness for the current task. Do not treat documentation as authoritative when code or tests contradict it.

## Labels

- **KEEP** - Short, directly relevant, and safe to keep in context.
- **SUMMARIZE** - Relevant but too long or broad; summarize for the task.
- **IGNORE** - Not relevant to this task.
- **STALE** - Likely obsolete based on age, naming, warnings, or contradiction with current code.
- **ASK/VERIFY** - Potentially important but conflicts with code/tests or needs user/project confirmation.

## Freshness Signals

Higher confidence:

- Recent ADRs, specs, or plans that match current code.
- Docs referenced by tests, CI, or current README.
- Docs with concrete examples that still exist in the repo.

Lower confidence:

- Legacy/archive paths.
- Docs referencing deleted files, old commands, or old package names.
- Contradiction with current code, tests, or config.
- Broad docs with no clear owner or date.

## Summary Rules

- Summarize from the task perspective, not generically.
- Include only decisions, constraints, contracts, patterns, and warnings relevant to the task.
- Preserve contradictions explicitly.
- If a doc is stale but historically useful, label it `STALE` and extract only the part that explains why old behavior exists.

## Output Format

Use this compact table when docs matter:

| Document | Label | Use | Confidence |
|----------|-------|-----|------------|
| `path` | KEEP/SUMMARIZE/IGNORE/STALE/ASK/VERIFY | [task-specific reason] | high/medium/low/unknown |
