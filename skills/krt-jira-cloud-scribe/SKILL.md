---
name: krt-jira-cloud-scribe
description: Manages Jira Cloud issues in Spanish using REST API v3, Basic Auth with email plus API token, project-local cloud env files, Atlassian Document Format payloads, active sprint placement, PR remote links, and localized workflow transitions. Use when the target Jira instance is Atlassian Jira Cloud rather than Jira Server/Data Center, especially for creating or reusing issues/subtasks, adding GitHub PR backlinks, moving issues through review/done states, or preparing Jira handoff context for KRT release workflows.
---

# Jira Cloud Scribe

Manage Jira Cloud safely in Spanish. This is the Cloud sibling of `krt-jira-scribe`; use `krt-jira-scribe` for Jira Server/Data Center and this skill for `*.atlassian.net` Cloud sites.

Since Jira Cloud is a shared external system, never create issues, subtasks, PR backlinks, comments, or transitions without explicit confirmation. Confirmation may come from the current Jira Cloud prompt, from an accepted `krt-release-marshal` plan that explicitly names the issue, PR backlink behavior, target status, and automatic post-PR behavior, or from an active autonomy ledger executed through Release Marshal's deterministic mutation executor.

Load `references/safety.md` before beginning the workflow.
Load `references/jira-cloud-api.md` for exact `curl` commands, REST API v3 payloads, Atlassian Document Format examples, active sprint calls, transition calls, and HTTP error handling.
For autonomous Jira mutation, use bundled scripts in `scripts/`: text, issue payload, backlink binding, and transition validators. These scripts validate; Release Marshal's executor performs audited mutation.

## Cloud Boundaries

- Use Jira Cloud REST API v3 for platform calls: `/rest/api/3`.
- Use Jira Software Cloud Agile API for boards and sprints: `/rest/agile/1.0`.
- Authenticate scripts with Basic Auth using `JIRA_CLOUD_EMAIL` and `JIRA_CLOUD_API_TOKEN`.
- Do not use Server/Data Center Bearer-token examples from `krt-jira-scribe`.
- Use Atlassian Document Format for `description` and `comment.body` fields.
- Use `accountId` for users; do not rely on username/user key.

## Spanish Jira Rules

- Issue type names may be localized or custom. Prefer the exact issue type names returned by the target Cloud project's create metadata. Common Spanish names are `Tarea`, `Subtarea`, `Historia`, `Error`, and often `Epic`.
- Summaries, descriptions, comments, confirmations, and prompts must be in Spanish.
- Autonomous summaries/descriptions/comments must also pass `scripts/check_jira_text.py`; planning IDs, package IDs, date sequences, conventional commit prefixes, and PR operation chatter are blocked.
- Descriptions are required for new issues/subtasks: write 1-3 concise Spanish sentences explaining what needs to be done and why.
- Transition names are workflow-local and may be Spanish. Always fetch and display actual transition names from the API; do not assume English names.
- JQL keywords remain English (`AND`, `OR`, `project =`, `summary ~`) regardless of Jira locale.

## Configuration

Use environment variables exclusively at runtime. The only supported project-local source is `.krt/env/jira-cloud-scribe.env` for the current checkout:

- `JIRA_CLOUD_HOST` such as `example.atlassian.net`
- `JIRA_CLOUD_EMAIL`
- `JIRA_CLOUD_API_TOKEN`
- `JIRA_CLOUD_PROJECT_KEY`
- `JIRA_CLOUD_BOARD_ID` optional board override for active sprint resolution

Do not assume Jira Cloud variables are already present in the console context. Prefer loading them through `direnv`; otherwise use the bundled loader scripts. Do not parse credentials from project files inside prompts or one-off shell snippets.

If the user explicitly asks to set up project-local Jira Cloud configuration, run:

```bash
python3 <jira-cloud-scribe-skill-dir>/scripts/setup_jira_env.py --root <consumer-project-root>
```

The setup script creates `.krt/env/.gitignore`, verifies `.krt/env/jira-cloud-scribe.env` is ignored with `git check-ignore`, refuses tracked secrets, writes placeholders only after the ignore check passes, and creates `.krt/env/jira-cloud-scribe.env.example` for non-secret documentation.

Never ask for credentials. If required variables are missing, or if `.krt/env/jira-cloud-scribe.env` is absent for the active checkout, terminate with an error naming the missing runtime variables or missing project-local env file. Never print `JIRA_CLOUD_API_TOKEN` or commands containing its value.

When startup context is ambiguous, run:

```bash
python3 <jira-cloud-scribe-skill-dir>/scripts/check_jira_env.py --root <consumer-project-root> --strict
```

When the shell is not already loaded, run Jira Cloud verification and API commands through:

```bash
python3 <jira-cloud-scribe-skill-dir>/scripts/run_with_jira_env.py --root <consumer-project-root> -- <command ...>
```

## Workflow

### 1. Startup

Load `references/jira-cloud-api.md`. Run `scripts/check_jira_env.py --root <consumer-project-root> --strict` when Jira Cloud readiness is unknown or the caller may depend on project-local `.krt/env` setup. All Jira Cloud API calls must go through `scripts/run_with_jira_env.py --root <consumer-project-root> -- <command ...>` unless the shell is already loaded with `direnv`.

Normalize `JIRA_CLOUD_HOST` to a base URL by adding `https://` if no scheme exists and trimming trailing `/`. Verify credentials with `/rest/api/3/myself`, then verify project access with `/rest/api/3/project/$JIRA_CLOUD_PROJECT_KEY`.

### 2. Resolve Issue Shape Before Creating Anything

Before proposing a new global issue, decide whether the requested work should be a subtask under an existing issue or under a new parent issue.

Never propose a one-parent/one-child Jira shape. If the plan would create exactly one parent `Tarea` and exactly one child `Subtarea` with no likely sibling tasks, collapse it into one standalone `Tarea` and put the PR backlink and transition on that task.

1. Search possible parents first using project, issue type, and meaningful summary/context terms.
2. Inspect plausible parents by key, including summary, status, description, and existing subtasks.
3. Prefer reuse when scope fits, but only from active work. Do not reuse parents already in done/closed-like statuses unless the user explicitly asks to reopen or continue that exact issue.
4. If no parent fits and the work has two or more likely sibling tasks, prefer proposing a new parent plus one subtask per immediate PR/work package.
5. Ask when ambiguous.
6. Create a standalone issue only after ruling out parent fit and sibling-task likelihood.

### 3. Verify Or Create Global Issue

1. Search candidates with project, issue type, and `summary ~ "text"`.
2. Show key, status, summary, and URL.
3. Treat reuse candidates as eligible only when their current status is open or in progress.
4. If an eligible active issue exists, ask the user to confirm which one to use.
5. If no eligible active issue exists, present project, type, summary, ADF description rendered in Spanish prose, sprint plan, and Jira base URL. Create only after confirmation.

For new global issues/parent tasks, assume `Sprint: active sprint` unless the user says `sin sprint`, `no sprint`, `fuera del sprint`, or equivalent. Do not apply sprint placement to subtasks unless explicitly requested; subtasks inherit the parent's context.

If Jira Cloud returns required-field errors, show missing fields and ask. Do not guess custom field IDs.

### 4. Verify Or Create Subtask

1. Search candidates with `parent = "PARENT_KEY" AND summary ~ "text"`.
2. Show key, status, summary, and URL.
3. Reuse only active subtasks that clearly match.
4. If no eligible active subtask exists, present parent, type, summary, ADF description, and Jira base URL. Create only after confirmation.

### 5. Add PR Backlink

When a PR exists and the associated Jira issue/subtask should point back to it:

1. Verify the issue key and fetch summary/status.
2. Prefer a Jira Cloud remote issue link with a stable `globalId` such as `github-pr:$PR_URL`.
3. Add a Spanish comment only when the user explicitly asked for one. The default backlink path is the remote link alone.
4. Do not edit description or custom fields to store the PR URL unless the user explicitly asks.
5. If the PR is draft and the caller asked to update Jira only when ready for review, report the backlink as deferred.

### 6. Confirm Final Status

When completing work:

1. Show issue/subtask summary and current status.
2. Fetch available transitions.
3. Show real transition names and IDs.
4. Ask whether to move to `En Revisión`, `Terminado`, or another available transition.
5. Execute only after confirmation.

If called by `krt-release-marshal` after PR creation and the accepted release plan already approved automatic transition to `En Revisión`, require an exact available transition named `En Revisión`. Stop and ask if unavailable or ambiguous.

## Required Confirmations

Before creating an issue or subtask, show:

- Project.
- Type.
- Summary.
- Description in Spanish.
- Parent, if applicable.
- Sprint plan for new global issues/parent tasks.
- Jira Cloud base URL.

Before transitioning an issue, show:

- Issue key.
- Current status.
- Target transition.
- Transition ID.

Before adding a PR backlink/comment, show:

- Issue key.
- PR URL.
- Remote link title.
- Comment text, if adding a comment.

For autonomous mode, the ledger plus executor validation counts as confirmation only for the exact issue key, PR URL, transition ID/status, and mutation class in scope. Markdown state is never enough authority for Jira Cloud mutation.

## Final Summary

Always end with:

- Parent issue: key, URL, status, created yes/no.
- Subtask: key, URL, status, created yes/no.
- PR backlink: yes/no/deferred.
- Transitioned: yes/no.
- Next action.
