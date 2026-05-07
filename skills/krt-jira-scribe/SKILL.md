---
name: krt-jira-scribe
description: Manages Jira Server/Data Center issues on a Spanish-language instance. Verifies existing global issues and subtasks, checks whether new work belongs under an existing parent, proposes Spanish issue/subtask creation when missing, handles active sprint placement, and manages Spanish transitions. Runtime aliases may expose this as krt:jira-scribe.
---

# Jira Scribe

Manage Jira Server/Data Center issues safely in Spanish. This skill verifies existing global issues and subtasks, prefers fitting new work under existing parent issues, proposes creation only when the right Jira shape is clear, and handles final status transitions.

Since Jira is a shared external system, never create issues, subtasks, comments, or transitions without explicit confirmation. Confirmation may come from the current Jira prompt or from an accepted `krt-release-marshal` plan that explicitly names the issue, target status, and automatic post-PR transition behavior.

Load `references/jira-api.md` for exact `curl` commands, JSON payloads, active sprint API calls, transition calls, and HTTP error handling.

## Spanish Jira Rules

- Issue types are localized: `Tarea`, `Subtarea`, `Historia`, `Error`, `Epic` (Epic is often kept in English).
- Summaries, descriptions, comments, confirmations, and prompts must be in Spanish.
- Descriptions are required for new issues/subtasks: write 1-3 concise Spanish sentences explaining what needs to be done and why.
- Transition names are localized. Always fetch and display actual transition names from the API; do not assume English names.
- JQL keywords remain English (`AND`, `OR`, `project =`, `summary ~`) regardless of Jira locale.

## Configuration

Use environment variables exclusively:

- `JIRA_HOST`
- `JIRA_API_TOKEN`
- `JIRA_PROJECT_KEY`
- `JIRA_EMAIL` optional metadata only
- `JIRA_BOARD_ID` optional board override for active sprint resolution

Never ask for credentials. If `JIRA_HOST`, `JIRA_API_TOKEN`, or `JIRA_PROJECT_KEY` is missing, terminate with an error naming the missing variables. Never print `JIRA_API_TOKEN` or commands containing it.

When verifying whether Jira variables exist, do not rely on filtered environment searches that may hide variables. Some command wrappers, including `rtk`, can filter or summarize `env`/search output in ways that make Jira variables look absent. Use a direct shell presence check such as `[[ -n "$JIRA_HOST" ]]`, `printenv JIRA_HOST`, or the verification snippet in `references/jira-api.md`; never print token values.

Normalize `JIRA_HOST` to `JIRA_BASE_URL` by adding `https://` if no scheme exists and trimming trailing `/`.

Use Jira Server/Data Center only:

- API base: `/rest/api/2`
- Authentication: `Authorization: Bearer $JIRA_API_TOKEN`
- Jira Software Agile API for boards/sprints: `/rest/agile/1.0`

## Workflow

### 1. Startup

Load `references/jira-api.md`. Normalize host, verify required env vars, test credentials with `/rest/api/2/myself`, and verify project/issue types for `JIRA_PROJECT_KEY`.

### 2. Resolve Issue Shape Before Creating Anything

Before proposing a new global issue, decide whether the requested work should be a subtask under an existing issue or under a new parent issue.

1. Search for possible parents first using project, type, and meaningful summary/context terms.
2. Inspect plausible parents by key, including summary, status, description, and existing subtasks.
3. Prefer reuse when scope fits: if an open parent clearly covers the work, propose creating or reusing a subtask under that parent instead of creating a standalone `Tarea`.
4. If no parent fits and the work is a pull request/work package that may have sibling tasks, prefer proposing a new parent `Tarea` plus a `Subtarea` for the immediate PR/work package. This is the default shape for Compound Master work packages and multi-PR delivery. The new parent should be added to the active sprint unless the user explicitly says `sin sprint`, `no sprint`, `fuera del sprint`, or equivalent.
5. Ask when ambiguous: show candidate parents and ask which one to use, whether to create a new parent plus subtask, or whether the work is truly standalone.
6. Create a standalone global issue only after ruling out parent fit and sibling-task likelihood. Do not propose a standalone task just because no exact summary match exists.

### 3. Verify Or Create Global Issue

1. Search candidates with project, issue type, and `summary ~ "text"`.
2. Show key, status, summary, and URL.
3. If it exists, ask the user to confirm which one to use.
4. If it does not exist, present project, type, summary, description, sprint plan, and Jira base URL. Create only after confirmation.

For new global issues/parent tasks:

- Assume `Sprint: active sprint` unless the user says `sin sprint`, `no sprint`, `fuera del sprint`, or equivalent.
- Include active sprint placement in pre-creation confirmation.
- After creation, add it to the active sprint without a second confirmation if that was part of the confirmed plan.
- If a unique active sprint cannot be resolved, do not invent IDs. Show boards/sprints and ask, or report creation without sprint only when the user already approved non-blocking continuation.
- Do not apply sprint placement to subtasks unless explicitly requested; subtasks inherit the parent's context.

Do not create issues based solely on fuzzy `summary ~` search.

When creating both a parent and subtask, confirm both summaries/descriptions together. Create the parent first, then create the subtask under it. Return the subtask as the immediately relevant issue for PR bodies and commit references; keep the parent for context and future sibling tasks.

For parent-plus-subtask creation, include the active sprint plan in the same confirmation. After creating the parent, add the parent to the active sprint before or after creating the subtask without asking a second time when that sprint placement was confirmed. Do not add the subtask directly to the sprint unless the user explicitly asks; the subtask inherits the parent's sprint context.

### 4. Verify Or Create Subtask

1. Search candidates with `parent = "PARENT_KEY" AND summary ~ "text"`.
2. Show key, status, summary, and URL.
3. If it exists, ask the user to confirm which one to use.
4. If it does not exist, present parent, type, summary, description, and Jira base URL. Create only after confirmation.

When the user provides a parent key:

1. Get the parent and show summary, status, and URL.
2. Search existing subtasks.
3. Show candidates.
4. Propose reusing an open subtask if there is a clear match, or creating a new one if scope does not fit.
5. Create only with explicit confirmation.

If Jira returns required-field errors, show missing fields and ask. Do not guess custom field IDs.

### 5. Confirm Final Status

When completing work:

1. Show parent issue and subtask summary.
2. Get available transitions.
3. Show real options by name and ID.
4. Ask whether to move to `En Revisión`, `Terminado`, or another available transition.
5. Execute only after confirmation.

After creating or updating an associated PR without a pre-approved release-marshal transition, offer to move the Jira task to review:

1. Get actual transitions for the issue/subtask.
2. If a transition named `En Revisión` exists, propose it with ID and target status.
3. Execute only with explicit confirmation.

If called by `krt-release-marshal` after PR creation and the accepted release plan already approved automatic transition to `En Revisión`:

1. Get actual transitions for the issue/subtask.
2. Require an exact available transition named `En Revisión`.
3. Execute that transition without asking a second time.
4. Report issue key, previous status, transition ID/name, and resulting status.
5. If the exact transition is unavailable or issue key is ambiguous, stop and ask instead of guessing.

## Required Confirmations

Before creating an issue or subtask, show:

- Project.
- Type.
- Summary.
- Description.
- Parent, if applicable.
- Sprint plan for new global issues/parent tasks.
- Jira base URL.

Before transitioning an issue, show:

- Issue key.
- Current status.
- Target transition.
- Transition ID.

Do not execute remote changes until the user confirms. For release-marshal initiated post-PR transitions, the accepted release plan counts as confirmation only when it explicitly approved automatic transition of the named Jira issue to `En Revisión`.

## Final Summary

Always end with:

- Parent issue: key, URL, status, created yes/no.
- Subtask: key, URL, status, created yes/no.
- Transitioned: yes/no.
- Next action.
