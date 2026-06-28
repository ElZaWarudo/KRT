# Jira Cloud Safety

- Do not print `JIRA_CLOUD_API_TOKEN`, Basic Auth headers, full env dumps, or commands with literal token values.
- Do not use `.krt/env/jira-scribe.env`; that file belongs to Jira Server/Data Center.
- Do not create, transition, backlink, or comment on Jira Cloud issues without explicit confirmation, release-plan approval, or a valid autonomy ledger.
- Do not guess custom field IDs, transition IDs, board IDs, sprint IDs, or issue type names. Fetch them or ask.
- Do not store PR URLs in descriptions or custom fields unless explicitly requested; use remote issue links by default.
- Do not treat markdown state as live authority for Jira Cloud. Re-fetch issue status, transitions, and remote links before mutation.
