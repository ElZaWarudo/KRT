---
name: jira-scribe
description: Manages Jira Server/Data Center issues on a Spanish-language instance — verifies existing global issues and subtasks, proposes creation (in Spanish) if missing, and asks the user for the final status upon completion. All issue text, types, and transitions are written in Spanish.
---

# Jira Scribe

This skill automates issue management in Jira Server/Data Center, verifying the existence of global issues and subtasks, and proposing their creation if they don't exist.

Since it works against a shared external system, it must never create issues, subtasks, or transition states without explicit user confirmation.

## Language: Spanish Jira Instance

**IMPORTANT**: This skill is designed to work against a **Spanish-language Jira Server/Data Center instance**. This means:

- **Issue types are in Spanish**: `Tarea`, `Subtarea`, `Historia`, `Error`, `Epic` (Epic is typically kept in English even on Spanish Jira). Always use the localized issue type names matching the target Jira instance — do **not** use English types like `Task`, `Sub-task`, `Story`, `Bug`.
- **Issue summaries and descriptions are written in Spanish**: When creating issues or subtasks, write all user-facing text (summary, description, comments) in Spanish.
- **Descriptions are required for new issues/subtasks**: Always include a small, clear Spanish description explaining what needs to be done and why. Keep it concise, usually 1-3 sentences, and derive it from the user's request and available context.
- **Transition names are in Spanish**: Available transitions will have Spanish names like `En Revisión`, `Terminado`, `En Progreso`, `To Do`, etc. Always fetch and display the actual transition names from the API rather than assuming English names.
- **All user interaction is in Spanish**: Confirmations, summaries, and prompts shown to the user are in Spanish.
- **JQL queries work in any language**: JQL keywords (`AND`, `OR`, `project =`, `summary ~`) are always in English regardless of the Jira locale.

## Required Configuration

**IMPORTANT**: Under no circumstances should the skill ask the user for credentials. If credentials are missing, the skill must terminate with an error indicating the problem.

The skill requires the following credentials:

- **JIRA_HOST**: Jira server URL (e.g. `your-company.atlassian.net`)
- **JIRA_API_TOKEN**: Bearer token for Jira Server/Data Center
- **JIRA_PROJECT_KEY**: Project key — e.g. `PROJ`

Optional:

- **JIRA_EMAIL**: Jira user, only as local metadata if the team needs it. Not used for authentication.
- **JIRA_BOARD_ID**: Jira Software board ID to use for resolving the active sprint when multiple boards are candidates.

### Session startup

At the start of each execution, the skill uses environment variables exclusively:

- `JIRA_HOST`
- `JIRA_API_TOKEN`
- `JIRA_PROJECT_KEY`
- `JIRA_EMAIL` optional, only as local metadata if the team needs it

Do not look for Jira configuration in repo files. Do not read, create, suggest, or modify local configuration files for Jira.

If required variables are missing, terminate with an error indicating which ones are missing. **Never ask for credentials**.

## REST API with curl

**IMPORTANT**: Always use the REST API directly with `curl`. Do NOT use the `jira` CLI — it has limitations on many servers.
Use raw JSON by default for `POST` and transitions; do not depend on `jq`. Substitute example values before executing.

This skill uses Jira Server/Data Center exclusively:

- API base: `/rest/api/2`
- Authentication: `Authorization: Bearer $JIRA_API_TOKEN`

Never print `JIRA_API_TOKEN`. Do not show full commands that include tokens.

Normalize `JIRA_HOST` to `JIRA_BASE_URL`:

- Accept `jira.company.com` or `https://jira.company.com`
- Add `https://` if no scheme is present
- Remove trailing `/`

### Authentication

```bash
# Use Bearer Token
curl -sS -f -H "Authorization: Bearer $JIRA_API_TOKEN" \
  "$JIRA_BASE_URL/rest/api/2/myself"
```

### Verify project exists

```bash
# List all projects
curl -sS -f -H "Authorization: Bearer $JIRA_API_TOKEN" \
  "$JIRA_BASE_URL/rest/api/2/project"

# Get issue types for a project
curl -sS -f -H "Authorization: Bearer $JIRA_API_TOKEN" \
  "$JIRA_BASE_URL/rest/api/2/project/$JIRA_PROJECT_KEY"
```

### Search issues

```bash
# Search by JQL
curl -sS -f -H "Authorization: Bearer $JIRA_API_TOKEN" \
  -H "Content-Type: application/json" \
  --get \
  --data-urlencode "jql=project = $JIRA_PROJECT_KEY AND summary ~ \"search text\"" \
  --data-urlencode "maxResults=10" \
  "$JIRA_BASE_URL/rest/api/2/search"

# Get issue by key
curl -sS -f -H "Authorization: Bearer $JIRA_API_TOKEN" \
  "$JIRA_BASE_URL/rest/api/2/issue/$ISSUE_KEY"
```

### Create issue

```bash
# Create issue (use the type in the Jira instance's language — Spanish: Tarea, Subtarea, Historia, Error, Epic)
curl -sS -f -X POST -H "Authorization: Bearer $JIRA_API_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{
    "fields": {
      "project": {"key": "PDP"},
      "summary": "Resumen de la tarea",
      "description": "Explicación breve de lo que hay que hacer y el contexto necesario para entender la tarea.",
      "issuetype": {"name": "Tarea"}
    }
  }' \
  "$JIRA_BASE_URL/rest/api/2/issue"

# Create subtask
curl -sS -f -X POST -H "Authorization: Bearer $JIRA_API_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{
    "fields": {
      "project": {"key": "PDP"},
      "summary": "Resumen de la subtarea",
      "description": "Explicación breve de lo que hay que hacer en esta subtarea y el contexto necesario.",
      "issuetype": {"name": "Subtarea"},
      "parent": {"key": "PDP-32"}
    }
  }' \
  "$JIRA_BASE_URL/rest/api/2/issue"
```

### Add issue to active sprint

When creating a global issue/parent task, assume by default that it should be added to the active sprint, unless the user indicates otherwise.

Resolve the active sprint using the Jira Software Agile API:

```bash
# Find boards for the project
curl -sS -f -H "Authorization: Bearer $JIRA_API_TOKEN" \
  --get \
  --data-urlencode "projectKeyOrId=$JIRA_PROJECT_KEY" \
  "$JIRA_BASE_URL/rest/agile/1.0/board"

# Find active sprint for the chosen board
curl -sS -f -H "Authorization: Bearer $JIRA_API_TOKEN" \
  "$JIRA_BASE_URL/rest/agile/1.0/board/$BOARD_ID/sprint?state=active"

# Add issue to active sprint
curl -sS -f -X POST -H "Authorization: Bearer $JIRA_API_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{"issues":["PDP-123"]}' \
  "$JIRA_BASE_URL/rest/agile/1.0/sprint/$SPRINT_ID/issue"
```

If `JIRA_BOARD_ID` is defined, use it directly. If it is not defined and there is a single board candidate for the project, use that board. If there are multiple boards or no active sprint, do not guess: show the options/status and ask, or report that the issue was created without a sprint if the user already asked not to block.

### Update status

```bash
# Get available transitions
curl -sS -f -H "Authorization: Bearer $JIRA_API_TOKEN" \
  "$JIRA_BASE_URL/rest/api/2/issue/$ISSUE_KEY/transitions"

# Perform transition (by transition ID)
curl -sS -f -X POST -H "Authorization: Bearer $JIRA_API_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{"transition":{"id":"41"}}' \
  "$JIRA_BASE_URL/rest/api/2/issue/$ISSUE_KEY/transitions"
```

## Workflow

### 1. Load credentials

```bash
# Normalize host
JIRA_BASE_URL="$JIRA_HOST"
case "$JIRA_BASE_URL" in
  http://*|https://*) ;;
  *) JIRA_BASE_URL="https://$JIRA_BASE_URL" ;;
esac
JIRA_BASE_URL="${JIRA_BASE_URL%/}"

# Verify they are defined
if [[ -z "$JIRA_API_TOKEN" || -z "$JIRA_HOST" || -z "$JIRA_PROJECT_KEY" ]]; then
    echo "ERROR: Missing required variables: JIRA_HOST, JIRA_API_TOKEN, JIRA_PROJECT_KEY"
    exit 1
fi
```

### 2. Verify/Create Global Issue

1. **Search for candidates**: JQL with project, type, and `summary ~ "text"`.
2. **Show candidates**: list key, status, summary, and URL.
3. **If it exists**: ask the user to confirm which one to use.
4. **If it doesn't exist**: present the proposed project, type, summary, and sprint plan. Create only if the user confirms.

For new global issues/parent tasks:

- Assume `Sprint: active sprint` by default.
- Do not add to sprint if the user explicitly says `sin sprint`, `no sprint`, `fuera del sprint`, or equivalent.
- Include in the pre-creation confirmation that the issue will be added to the active sprint.
- After creating the issue, add it to the active sprint with `/rest/agile/1.0/sprint/{sprintId}/issue` without asking for a second confirmation if that action was already part of the confirmed plan.
- If a unique active sprint cannot be resolved, do not invent IDs: show the found boards/sprints and ask for guidance, or report that the issue was created without a sprint if the user had asked to continue without blocking.
- Do not apply this rule to subtasks: subtasks inherit the parent's context and must not be moved to a sprint independently unless explicitly requested.

Do not automatically create issues based solely on a fuzzy search by `summary ~`.

### 3. Verify/Create Subtask

1. **Search for candidates**: JQL with `parent = "PARENT_KEY" AND summary ~ "text"`.
2. **Show candidates**: list key, status, summary, and URL.
3. **If it exists**: ask the user to confirm which one to use.
4. **If it doesn't exist**: present the proposed parent, type, and summary; create only if the user confirms.

If Jira returns required field errors when creating an issue or subtask, show the missing fields and ask the user. Do not guess custom field IDs.

When the user provides a parent key (e.g. `PDP-32`):
1. Get the parent by key and show summary, status, and URL.
2. Search for existing subtasks with `parent = "PARENT_KEY"`.
3. Show candidates with key, status, summary, and URL.
4. Propose reusing an open subtask if there's a clear match, or creating a new one if the scope doesn't fit.
5. Create a new subtask only with explicit user confirmation.

### 4. Confirm Final Status

When completing work:
1. Show summary (issue + subtask)
2. Get available transitions
3. Show actual options by name and ID
4. Ask whether to move to "En Revisión", "Terminado", or another available transition
5. Execute transition only if confirmed

After creating or updating an associated PR, offer to move the Jira task to review:
1. Get the actual transitions for the issue/subtask.
2. If a transition named "En Revisión" exists, propose it with its ID and target status.
3. Execute only with explicit confirmation.

## Required confirmations

Before creating an issue or subtask, show:

- Project
- Type
- Summary
- Description
- Parent, if applicable
- Sprint plan, for new global issues/parent tasks (`active sprint` by default or `no sprint` if the user indicated so)
- Jira base URL

Before transitioning an issue, show:

- Issue key
- Current status
- Target transition
- Transition ID

Do not execute remote changes until the user confirms.

## HTTP error handling

- Use `curl -sS -f` for reads where any error should stop the flow.
- For `POST`, capture and check status code and body if Jira responds with an error.
- If `401` or `403` appears, terminate indicating an authentication/authorization problem without printing tokens.
- If `400` appears with required fields, show Jira's message and ask for the missing fields.

## Final summary

Always end with:

- Parent issue: key, URL, status, created yes/no
- Subtask: key, URL, status, created yes/no
- Transitioned: yes/no
- Next action

## Important notes

- **Bearer Token**: For Jira Server/Data Center, use `Authorization: Bearer $JIRA_API_TOKEN`
- **Localized types**: A Spanish Jira uses `Tarea`, `Subtarea`, `Historia`, `Error`, `Epic`
- **Project key**: Not the task number. `PDP-35` → project `PDP`, task `35`
- **Testing**: Always test credentials with `/rest/api/2/myself` first
- **Secrets**: Never print `JIRA_API_TOKEN`, credentials, or files/configs that may contain them
