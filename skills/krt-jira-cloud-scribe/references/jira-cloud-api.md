# Jira Cloud API

Every call below goes through `scripts/jira_api.py --root <repo> METHOD PATH`,
which adds Basic auth (`JIRA_CLOUD_EMAIL:JIRA_CLOUD_API_TOKEN`) from
`.krt/env/jira-cloud-scribe.env`. Platform API: `/rest/api/3`. Boards and
sprints: `/rest/agile/1.0`.

Source basis: Atlassian's Basic auth for REST APIs, the REST API v3 groups
(issue search, issues, remote links), the Jira Software Cloud sprint API, and
the Atlassian Document Format structure on developer.atlassian.com.

## Credential check

- `GET /rest/api/3/myself` should return 200 with your `accountId`.
- `GET /rest/api/3/project/$JIRA_CLOUD_PROJECT_KEY` should return the project
  and its issue types.
- A 401 points to a wrong email/token pair, a revoked token, or the wrong site
  URL. A 403 points to missing project permission.

If `check_jira_env.py` says `ok: true`, a later failure is not missing
configuration. Report the cause; don't ask for credentials.

## Search and read

```bash
jira_api.py POST /rest/api/3/search/jql --data '{"jql": "project = KRT AND summary ~ \"exportación\" ORDER BY updated DESC", "maxResults": 10, "fields": ["summary","status","issuetype","parent","subtasks"]}'
jira_api.py GET /rest/api/3/issue/KRT-42 --query fields=summary,status,issuetype,parent,subtasks,description
```

`/rest/api/3/search/jql` returns only issue IDs unless you pass `fields`. It
pages with `nextPageToken` instead of `startAt`. If a tenant returns 404 for
it, fall back to `/rest/api/3/search`.

JQL gotchas:

- Keywords are English.
- Status and type values are the workflow's own, so Spanish here:
  `status = "En Progreso"`.
- Quote multi-word values.
- If Jira says a project "does not exist", re-run the bare query
  `project = "KRT"` before blaming access.

## Atlassian Document Format

`description` and comment `body` must be ADF documents:

```json
{"type": "doc", "version": 1, "content": [
  {"type": "paragraph", "content": [{"type": "text", "text": "Explicación breve de lo que hay que hacer y por qué."}]}
]}
```

When asking for confirmation, show the user the plain Spanish text, not the
JSON.

## Create

```json
POST /rest/api/3/issue
{"fields": {
  "project": {"key": "KRT"},
  "issuetype": {"name": "Tarea"},
  "summary": "Exportar pedidos a CSV",
  "description": {"type": "doc", "version": 1, "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Permitir descargar el listado de pedidos en CSV para que contabilidad lo procese sin copiarlo a mano."}]}]}
}}
```

For a subtask, add `"parent": {"key": "KRT-32"}` and use the project's
subtask type name. To see valid type names and required fields, call
`GET /rest/api/3/issue/createmeta/KRT/issuetypes` and then
`.../issuetypes/<id>`. On 400, show Jira's `errors` and ask.

## Active sprint

```bash
jira_api.py GET /rest/agile/1.0/board --query projectKeyOrId=KRT     # skip if JIRA_CLOUD_BOARD_ID is set
jira_api.py GET /rest/agile/1.0/board/<boardId>/sprint --query state=active
jira_api.py POST /rest/agile/1.0/sprint/<sprintId>/issue --data '{"issues":["KRT-123"]}'
```

Use the board only when exactly one candidate exists, and the sprint only
when exactly one is active. Otherwise ask.

## PR remote link

```json
POST /rest/api/3/issue/KRT-42/remotelink
{"globalId": "github-pr:https://github.com/acme/orders/pull/42",
 "object": {"url": "https://github.com/acme/orders/pull/42", "title": "GitHub PR #42",
            "icon": {"url16x16": "https://github.githubassets.com/favicons/favicon.png", "title": "GitHub"}}}
```

The same `globalId` updates the existing link instead of duplicating it. A
comment, only on request, goes to `POST /rest/api/3/issue/KRT-42/comment`
with an ADF `body`.

## Transitions

```bash
jira_api.py GET /rest/api/3/issue/KRT-42/transitions
jira_api.py POST /rest/api/3/issue/KRT-42/transitions --data '{"transition":{"id":"31"}}'
```

## Autonomous validators

These are the same validators as Server/Data Center. Release Marshal's
executor runs them before any autonomous write:

```bash
check_jira_text.py --text "<texto>"
check_jira_issue_mutation.py --mutation-class jira_create|jira_update --fixture <state.json>
check_jira_binding.py --mutation-class jira_backlink --fixture <state.json>
check_jira_transition.py --mutation-class jira_transition_review|jira_transition_done --fixture <state.json>
```

An autonomous move to done needs four things:

- a Jira key bound in the ledger;
- a one-to-one PR remote link;
- GitHub evidence that the PR merged;
- an exact transition ID when more than one done-like transition exists.
