# Jira API Reference

Use this reference for exact Jira Server/Data Center API calls, payload shapes, and HTTP error handling.

## Setup

Normalize host:

```bash
JIRA_BASE_URL="$JIRA_HOST"
case "$JIRA_BASE_URL" in
  http://*|https://*) ;;
  *) JIRA_BASE_URL="https://$JIRA_BASE_URL" ;;
esac
JIRA_BASE_URL="${JIRA_BASE_URL%/}"
```

Verify env vars:

```bash
if [[ -z "$JIRA_API_TOKEN" || -z "$JIRA_HOST" || -z "$JIRA_PROJECT_KEY" ]]; then
    echo "ERROR: Missing required variables: JIRA_HOST, JIRA_API_TOKEN, JIRA_PROJECT_KEY"
    exit 1
fi
```

## Authentication And Project

Test credentials:

```bash
curl -sS -f -H "Authorization: Bearer $JIRA_API_TOKEN" \
  "$JIRA_BASE_URL/rest/api/2/myself"
```

List projects:

```bash
curl -sS -f -H "Authorization: Bearer $JIRA_API_TOKEN" \
  "$JIRA_BASE_URL/rest/api/2/project"
```

Get project issue types:

```bash
curl -sS -f -H "Authorization: Bearer $JIRA_API_TOKEN" \
  "$JIRA_BASE_URL/rest/api/2/project/$JIRA_PROJECT_KEY"
```

## Search

Search by JQL:

```bash
curl -sS -f -H "Authorization: Bearer $JIRA_API_TOKEN" \
  -H "Content-Type: application/json" \
  --get \
  --data-urlencode "jql=project = $JIRA_PROJECT_KEY AND summary ~ \"search text\"" \
  --data-urlencode "maxResults=10" \
  "$JIRA_BASE_URL/rest/api/2/search"
```

Get issue:

```bash
curl -sS -f -H "Authorization: Bearer $JIRA_API_TOKEN" \
  "$JIRA_BASE_URL/rest/api/2/issue/$ISSUE_KEY"
```

Subtask search:

```bash
curl -sS -f -H "Authorization: Bearer $JIRA_API_TOKEN" \
  -H "Content-Type: application/json" \
  --get \
  --data-urlencode "jql=project = $JIRA_PROJECT_KEY AND parent = \"$PARENT_KEY\" AND summary ~ \"search text\"" \
  --data-urlencode "maxResults=10" \
  "$JIRA_BASE_URL/rest/api/2/search"
```

## Create Issue Or Subtask

Create issue:

```bash
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
```

Create subtask:

```bash
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

For `POST`, capture status code and response body so Jira field errors can be shown to the user.

## Active Sprint

Find boards for project:

```bash
curl -sS -f -H "Authorization: Bearer $JIRA_API_TOKEN" \
  --get \
  --data-urlencode "projectKeyOrId=$JIRA_PROJECT_KEY" \
  "$JIRA_BASE_URL/rest/agile/1.0/board"
```

Find active sprint:

```bash
curl -sS -f -H "Authorization: Bearer $JIRA_API_TOKEN" \
  "$JIRA_BASE_URL/rest/agile/1.0/board/$BOARD_ID/sprint?state=active"
```

Add issue to active sprint:

```bash
curl -sS -f -X POST -H "Authorization: Bearer $JIRA_API_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{"issues":["PDP-123"]}' \
  "$JIRA_BASE_URL/rest/agile/1.0/sprint/$SPRINT_ID/issue"
```

If `JIRA_BOARD_ID` is defined, use it directly. If not and a single board candidate exists, use it. If multiple boards or no active sprint exist, ask or continue without sprint only when the user already approved not blocking.

## Transitions

Get transitions:

```bash
curl -sS -f -H "Authorization: Bearer $JIRA_API_TOKEN" \
  "$JIRA_BASE_URL/rest/api/2/issue/$ISSUE_KEY/transitions"
```

Perform transition by ID:

```bash
curl -sS -f -X POST -H "Authorization: Bearer $JIRA_API_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{"transition":{"id":"41"}}' \
  "$JIRA_BASE_URL/rest/api/2/issue/$ISSUE_KEY/transitions"
```

## HTTP Error Handling

- Use `curl -sS -f` for reads where any error should stop the flow.
- For `POST`, capture and inspect status/body on failure.
- If `401` or `403` appears, report authentication/authorization failure without printing tokens.
- If `400` appears with required fields, show Jira's message and ask for missing fields.
- Never guess custom field IDs.
