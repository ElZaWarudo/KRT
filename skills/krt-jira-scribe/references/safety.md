# Safety Model

`krt-jira-scribe` works with Jira Server/Data Center, a shared external system. Jira mutations are visible to people and must be explicit.

## Guardrails

- Never ask the user to paste Jira credentials.
- Verify `JIRA_HOST`, `JIRA_API_TOKEN`, and `JIRA_PROJECT_KEY` without printing token values.
- Do not create issues, subtasks, PR backlinks, comments, sprint placement, or transitions without user approval unless an approved release workflow or autonomous ledger covers the exact mutation.
- Do not create issues from fuzzy summary search alone; verify project, type, parent, status, and fit.
- Do not invent required field values when Jira rejects a mutation; show missing fields and ask.
- Keep Jira summaries and descriptions in Spanish unless repo policy says otherwise.
