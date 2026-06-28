# Jira Cloud API Reference

Use this reference for exact Jira Cloud API calls, payload shapes, and HTTP error handling.

Source basis:

- Atlassian Basic Auth for REST APIs: https://developer.atlassian.com/cloud/jira/platform/basic-auth-for-rest-apis/
- Jira Cloud REST API v3 intro: https://developer.atlassian.com/cloud/jira/platform/rest/v3/intro/
- Issue search: https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-search/
- Issues: https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issues/
- Issue remote links: https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-remote-links/
- Jira Software Cloud sprints: https://developer.atlassian.com/cloud/jira/software/rest/api-group-sprint/
- Atlassian Document Format: https://developer.atlassian.com/cloud/jira/platform/apis/document/structure/

## Setup

Consumer projects keep Jira Cloud configuration local to each checkout:

```bash
python3 <jira-cloud-scribe-skill-dir>/scripts/setup_jira_env.py --root <consumer-project-root>
```

This creates:

```text
.krt/env/.gitignore
.krt/env/jira-cloud-scribe.env
.krt/env/jira-cloud-scribe.env.example
```

Projects using `direnv` can load:

```bash
dotenv_if_exists .krt/env/jira-cloud-scribe.env
```

Otherwise run commands through:

```bash
python3 <jira-cloud-scribe-skill-dir>/scripts/run_with_jira_env.py --root <consumer-project-root> -- <command ...>
```

## Required Variables

```bash
JIRA_CLOUD_HOST=example.atlassian.net
JIRA_CLOUD_EMAIL=person@example.com
JIRA_CLOUD_API_TOKEN=...
JIRA_CLOUD_PROJECT_KEY=KRT
JIRA_CLOUD_BOARD_ID= # optional
```

Normalize host:

```bash
JIRA_CLOUD_BASE_URL="$JIRA_CLOUD_HOST"
case "$JIRA_CLOUD_BASE_URL" in
  http://*|https://*) ;;
  *) JIRA_CLOUD_BASE_URL="https://$JIRA_CLOUD_BASE_URL" ;;
esac
JIRA_CLOUD_BASE_URL="${JIRA_CLOUD_BASE_URL%/}"
```

Never print `JIRA_CLOUD_API_TOKEN`.

## Authentication

Use Basic Auth with email and API token:

```bash
curl -sS -f -u "$JIRA_CLOUD_EMAIL:$JIRA_CLOUD_API_TOKEN" \
  "$JIRA_CLOUD_BASE_URL/rest/api/3/myself"
```

Verify project access:

```bash
curl -sS -f -u "$JIRA_CLOUD_EMAIL:$JIRA_CLOUD_API_TOKEN" \
  "$JIRA_CLOUD_BASE_URL/rest/api/3/project/$JIRA_CLOUD_PROJECT_KEY"
```

## JQL Search

Prefer POST search when JQL contains quoting or non-ASCII text:

```bash
curl -sS -f -X POST -u "$JIRA_CLOUD_EMAIL:$JIRA_CLOUD_API_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{
    "jql": "project = \"KRT\" AND summary ~ \"texto\" ORDER BY updated DESC",
    "maxResults": 10,
    "fields": ["summary", "status", "issuetype", "parent", "subtasks"]
  }' \
  "$JIRA_CLOUD_BASE_URL/rest/api/3/search"
```

If the Cloud tenant has migrated to enhanced search endpoints, follow Atlassian's current issue-search reference and use the tenant-supported v3 search endpoint. Keep the same JQL and field discipline.

Get issue:

```bash
curl -sS -f -u "$JIRA_CLOUD_EMAIL:$JIRA_CLOUD_API_TOKEN" \
  "$JIRA_CLOUD_BASE_URL/rest/api/3/issue/$ISSUE_KEY?fields=summary,status,issuetype,parent,subtasks,description"
```

## Atlassian Document Format

Jira Cloud descriptions and comments use Atlassian Document Format. Minimal paragraph:

```json
{
  "type": "doc",
  "version": 1,
  "content": [
    {
      "type": "paragraph",
      "content": [
        {
          "type": "text",
          "text": "Explicación breve de lo que hay que hacer y por qué."
        }
      ]
    }
  ]
}
```

## Create Issue Or Subtask

Create issue:

```bash
curl -sS -f -X POST -u "$JIRA_CLOUD_EMAIL:$JIRA_CLOUD_API_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{
    "fields": {
      "project": {"key": "KRT"},
      "summary": "Resumen de la tarea",
      "description": {
        "type": "doc",
        "version": 1,
        "content": [
          {"type": "paragraph", "content": [{"type": "text", "text": "Explicación breve de lo que hay que hacer y por qué."}]}
        ]
      },
      "issuetype": {"name": "Tarea"}
    }
  }' \
  "$JIRA_CLOUD_BASE_URL/rest/api/3/issue"
```

Create subtask:

```bash
curl -sS -f -X POST -u "$JIRA_CLOUD_EMAIL:$JIRA_CLOUD_API_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{
    "fields": {
      "project": {"key": "KRT"},
      "summary": "Resumen de la subtarea",
      "description": {
        "type": "doc",
        "version": 1,
        "content": [
          {"type": "paragraph", "content": [{"type": "text", "text": "Explicación breve de lo que hay que hacer en esta subtarea."}]}
        ]
      },
      "issuetype": {"name": "Subtarea"},
      "parent": {"key": "KRT-32"}
    }
  }' \
  "$JIRA_CLOUD_BASE_URL/rest/api/3/issue"
```

For required-field errors, fetch create metadata or ask the user. Do not guess custom field IDs.

## Active Sprint

Find boards for project:

```bash
curl -sS -f -u "$JIRA_CLOUD_EMAIL:$JIRA_CLOUD_API_TOKEN" \
  --get \
  --data-urlencode "projectKeyOrId=$JIRA_CLOUD_PROJECT_KEY" \
  "$JIRA_CLOUD_BASE_URL/rest/agile/1.0/board"
```

Find active sprint:

```bash
curl -sS -f -u "$JIRA_CLOUD_EMAIL:$JIRA_CLOUD_API_TOKEN" \
  "$JIRA_CLOUD_BASE_URL/rest/agile/1.0/board/$BOARD_ID/sprint?state=active"
```

Add issue to active sprint:

```bash
curl -sS -f -X POST -u "$JIRA_CLOUD_EMAIL:$JIRA_CLOUD_API_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{"issues":["KRT-123"]}' \
  "$JIRA_CLOUD_BASE_URL/rest/agile/1.0/sprint/$SPRINT_ID/issue"
```

## PR Remote Links And Optional Comments

Add or update a GitHub PR remote link:

```bash
curl -sS -f -X POST -u "$JIRA_CLOUD_EMAIL:$JIRA_CLOUD_API_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{
    "globalId": "github-pr:https://github.com/example/repo/pull/123",
    "object": {
      "url": "https://github.com/example/repo/pull/123",
      "title": "GitHub PR #123",
      "icon": {
        "url16x16": "https://github.githubassets.com/favicons/favicon.png",
        "title": "GitHub"
      }
    }
  }' \
  "$JIRA_CLOUD_BASE_URL/rest/api/3/issue/$ISSUE_KEY/remotelink"
```

Only add a Spanish comment when explicitly requested:

```bash
curl -sS -f -X POST -u "$JIRA_CLOUD_EMAIL:$JIRA_CLOUD_API_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{
    "body": {
      "type": "doc",
      "version": 1,
      "content": [
        {"type": "paragraph", "content": [{"type": "text", "text": "PR lista para revisión: https://github.com/example/repo/pull/123"}]}
      ]
    }
  }' \
  "$JIRA_CLOUD_BASE_URL/rest/api/3/issue/$ISSUE_KEY/comment"
```

## Transitions

Get transitions:

```bash
curl -sS -f -u "$JIRA_CLOUD_EMAIL:$JIRA_CLOUD_API_TOKEN" \
  "$JIRA_CLOUD_BASE_URL/rest/api/3/issue/$ISSUE_KEY/transitions"
```

Perform transition:

```bash
curl -sS -f -X POST -u "$JIRA_CLOUD_EMAIL:$JIRA_CLOUD_API_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{"transition":{"id":"41"}}' \
  "$JIRA_CLOUD_BASE_URL/rest/api/3/issue/$ISSUE_KEY/transitions"
```

## Autonomous Validators

Before autonomous Jira Cloud mutation, Release Marshal's executor must call the matching validator:

```bash
python3 <jira-cloud-scribe-skill-dir>/scripts/check_jira_text.py --text "<Spanish text>"
python3 <jira-cloud-scribe-skill-dir>/scripts/check_jira_issue_mutation.py --mutation-class jira_create --fixture <live-state-json>
python3 <jira-cloud-scribe-skill-dir>/scripts/check_jira_binding.py --mutation-class jira_backlink --fixture <live-state-json>
python3 <jira-cloud-scribe-skill-dir>/scripts/check_jira_transition.py --mutation-class jira_transition_done --fixture <live-state-json>
```

Autonomous completion to `Hecho` requires an exact ledger-bound Jira key, a one-to-one PR remote link, GitHub evidence that the linked PR is merged, and an exact transition ID when multiple done-like transitions exist.

## HTTP Error Handling

- Use `curl -sS -f` for reads where any error should stop the flow.
- For `POST`, capture and inspect status/body on failure.
- If `401` appears, verify email/token pair and site URL without printing token values.
- If `403` appears, report missing Jira Cloud permission or missing app/API scope context.
- If `400` appears with required fields, show Jira Cloud's message and ask for missing fields.
- Never guess custom field IDs.
