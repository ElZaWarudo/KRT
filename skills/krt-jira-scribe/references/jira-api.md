# Jira Server/Data Center API

Every call below goes through `scripts/jira_api.py --root <repo> METHOD PATH`,
which adds `Authorization: Bearer $JIRA_API_TOKEN` from
`.krt/env/jira-scribe.env`. Platform API: `/rest/api/2`. Boards and sprints:
`/rest/agile/1.0`.

## Credential check

Call `GET /rest/api/2/project` first, then `GET /rest/api/2/myself`, then
`GET /rest/api/2/project/$JIRA_PROJECT_KEY` for issue types.

| `/project` | `/myself` | Verdict |
|---|---|---|
| 200 + projects | 200 | Token valid. |
| 200 + projects | 401 | Token valid; `/myself` is broken on this instance. Ignore it. |
| 401/403 | 200 | Token valid but cannot browse projects. Check the project key and permissions. |
| 401/403 | 401/403 | Token invalid or expired. Report it without printing the token. |

If `check_jira_env.py` says `ok: true`, a later failure is not missing
configuration. Diagnose the real cause instead of asking for credentials:
auth scheme, expired token, wrong host, network, or permission.

Past incidents came from three traps:

- treating one `/myself` 401 as proof the token is broken;
- reading JQL parse errors as access errors;
- comparing anonymous and authenticated results, because a search returning
  `total: 0` looks the same either way.

## Search and read

```bash
jira_api.py GET /rest/api/2/search --query 'jql=project = PDP AND summary ~ "exportación" ORDER BY updated DESC' --query maxResults=10
jira_api.py GET /rest/api/2/issue/PDP-42
jira_api.py GET /rest/api/2/search --query 'jql=parent = "PDP-32"'
```

JQL gotchas:

- Keywords (`AND`, `OR`, `IN`, `ORDER BY`, `EMPTY`) are English.
- Status and type values are localized and case-sensitive:
  `status = "En Progreso"`, `status IN ("Por Hacer", "En Progreso")`.
- Quote multi-word values and put spaces around operators.
- If Jira says a project or field "does not exist", first re-run the bare
  query `project = "PDP"`. A malformed query can make Jira misread the key.

## Create

```json
POST /rest/api/2/issue
{"fields": {
  "project": {"key": "PDP"},
  "issuetype": {"name": "Tarea"},
  "summary": "Exportar pedidos a CSV",
  "description": "Permitir descargar el listado de pedidos en CSV para que contabilidad lo procese sin copiarlo a mano."
}}
```

For a subtask, use `"issuetype": {"name": "Subtarea"}` plus
`"parent": {"key": "PDP-32"}`. On 400, show `errors` / `errorMessages` and
ask about the missing fields.

## Active sprint

```bash
jira_api.py GET /rest/agile/1.0/board --query projectKeyOrId=PDP     # skip if JIRA_BOARD_ID is set
jira_api.py GET /rest/agile/1.0/board/<boardId>/sprint --query state=active
jira_api.py POST /rest/agile/1.0/sprint/<sprintId>/issue --data '{"issues":["PDP-123"]}'
```

Use the board only when exactly one candidate exists, and the sprint only
when exactly one is active. Otherwise ask.

## PR remote link

```json
POST /rest/api/2/issue/PDP-42/remotelink
{"globalId": "github-pr:https://github.com/acme/orders/pull/42",
 "object": {"url": "https://github.com/acme/orders/pull/42", "title": "GitHub PR #42",
            "icon": {"url16x16": "https://github.githubassets.com/favicons/favicon.png", "title": "GitHub"}}}
```

The same `globalId` updates the existing link instead of duplicating it.
`GET .../remotelink` shows the current links. A comment, only on request,
goes to `POST /rest/api/2/issue/PDP-42/comment` as `{"body": "PR lista para
revisión: <url>"}`.

## Transitions

```bash
jira_api.py GET /rest/api/2/issue/PDP-42/transitions
jira_api.py POST /rest/api/2/issue/PDP-42/transitions --data '{"transition":{"id":"31"}}'
```

## Autonomous validators

Release Marshal's executor runs these before an autonomous Jira write. They
read live-state JSON and print allow/block decisions:

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

`references/autonomous-jira-fixtures.md` maps each fixture to its expected
outcome.
