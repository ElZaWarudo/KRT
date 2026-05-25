# Jira API Reference

Use this reference for exact Jira Server/Data Center API calls, payload shapes, and HTTP error handling.

## Setup

Consumer projects can keep Jira configuration local to each checkout by loading ignored secret files before the skill runs. When the user explicitly asks to set this up, run:

```bash
python3 <jira-scribe-skill-dir>/scripts/setup_jira_env.py --root <consumer-project-root>
```

The setup script deterministically creates:

```bash
.krt/env/.gitignore
.krt/env/jira-scribe.env
.krt/env/jira-scribe.env.example
```

It writes this ignore rule before creating the secret file:

```gitignore
*
!.gitignore
!*.example
```

It refuses to write `.krt/env/jira-scribe.env` unless `git check-ignore` proves that exact path is ignored, and it refuses to continue if the file is already tracked. The user must fill the secret file locally after setup.

Projects that use `direnv` can load the file from their own `.envrc`:

```bash
dotenv_if_exists .krt/env/jira-scribe.env
```

Jira Scribe still consumes only environment variables and must not read token files directly.

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

Avoid filtered environment searches for this check. Command wrappers such as `rtk` may summarize or filter `env` output and can make Jira variables look missing. Prefer the direct presence check above, or check individual non-secret values with `printenv JIRA_HOST` and `printenv JIRA_PROJECT_KEY`. Never print `JIRA_API_TOKEN`.

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

## PR Backlinks And Comments

Add or update a Jira remote link to the GitHub PR:

```bash
curl -sS -f -X POST -H "Authorization: Bearer $JIRA_API_TOKEN" \
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
  "$JIRA_BASE_URL/rest/api/2/issue/$ISSUE_KEY/remotelink"
```

If the same `globalId` already exists, Jira updates that remote link instead of creating a duplicate. Use a deterministic `globalId` such as `github-pr:$PR_URL`.

Add a Spanish comment with the PR URL:

```bash
curl -sS -f -X POST -H "Authorization: Bearer $JIRA_API_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{"body":"PR lista para revisión: https://github.com/example/repo/pull/123"}' \
  "$JIRA_BASE_URL/rest/api/2/issue/$ISSUE_KEY/comment"
```

For `POST`, capture status code and response body so Jira permission or validation errors can be shown to the user. Never print token values.

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

## Autonomous Validators

Before autonomous Jira mutation, Release Marshal's executor must call the matching validator:

```bash
python3 <jira-scribe-skill-dir>/scripts/check_jira_text.py --text "<Spanish text>"
python3 <jira-scribe-skill-dir>/scripts/check_jira_issue_mutation.py --mutation-class jira_create --fixture <live-state-json>
python3 <jira-scribe-skill-dir>/scripts/check_jira_binding.py --mutation-class jira_backlink --fixture <live-state-json>
python3 <jira-scribe-skill-dir>/scripts/check_jira_transition.py --mutation-class jira_transition_done --fixture <live-state-json>
```

Autonomous completion to `Hecho` requires an exact ledger-bound Jira key, a one-to-one PR remote link, GitHub evidence that the linked PR is merged, and an exact transition ID when multiple done-like transitions exist. Existing `Hecho` status is a no-op success only when the issue is bound to the merged PR.

## HTTP Error Handling

- Use `curl -sS -f` for reads where any error should stop the flow.
- For `POST`, capture and inspect status/body on failure.
- If `401` or `403` appears, report authentication/authorization failure without printing tokens.
- If `400` appears with required fields, show Jira's message and ask for missing fields.
- Never guess custom field IDs.
