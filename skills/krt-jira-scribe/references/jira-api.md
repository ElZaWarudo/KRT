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

Jira Scribe still consumes only environment variables and must not read token files directly in ad hoc shell snippets, but it must not treat machine-global or ad-hoc shell exports as sufficient context. The active checkout's `.krt/env/jira-scribe.env` is the required source of Jira configuration.

If the shell is not preloaded with `direnv`, prefer the bundled loader:

```bash
python3 <jira-scribe-skill-dir>/scripts/run_with_jira_env.py --root <consumer-project-root> -- <command ...>
```

Use that helper for Jira verification, `curl`, and any bundled Jira scripts that need runtime variables.

When Jira seems unavailable, prefer the bundled readiness check before concluding that configuration is missing:

```bash
python3 <jira-scribe-skill-dir>/scripts/check_jira_env.py --root <consumer-project-root> --strict
```

The checker reports:

- which required Jira variables are present;
- whether `.krt/env/jira-scribe.env` exists;
- whether that secret file is actually ignored by Git; and
- whether the likely problem is "env file exists but was not loaded", "env file is present but incomplete", "variables appeared without the required project file", or "Jira is not configured yet".

By default, the checker loads non-empty Jira values from `.krt/env/jira-scribe.env` into its own process before evaluating readiness. Use `--no-auto-load` only when diagnosing whether the parent shell already loaded the env file. It does not print token values. Treat the result as not ready unless both the file exists and the required runtime variables are present after that load.

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

Avoid filtered environment searches for this check. Command wrappers such as `rtk` may summarize or filter `env` output and can make Jira variables look missing. Prefer the direct presence check above, or check individual non-secret values with `printenv JIRA_HOST` and `printenv JIRA_PROJECT_KEY`. Never print `JIRA_API_TOKEN`. Even when those checks pass, do not consider Jira configured unless `.krt/env/jira-scribe.env` exists for the active checkout.

## Credential Verification

**Do not rely on `/rest/api/2/myself` alone.** Some Jira Server/Data Center instances return 401 on `/myself` with Bearer tokens even when the same token works correctly for search, project list, and issue creation. Always use the two-endpoint strategy below.

### Two-Endpoint Strategy

1. **Primary: `/rest/api/2/project`** — lists all projects visible to the token. A 200 with a non-empty JSON array confirms the token works and has project access. This is the most reliable single check.

```bash
python3 <jira-scribe-skill-dir>/scripts/run_with_jira_env.py --root <consumer-project-root> -- \
  curl -sS -H "Authorization: Bearer $JIRA_API_TOKEN" \
  "$JIRA_BASE_URL/rest/api/2/project"
```

2. **Secondary: `/rest/api/2/myself`** — returns the authenticated user. If it succeeds, the token is definitely valid. But **a 401 here does NOT prove the token is broken**; it only means this specific endpoint rejected it. Cross-check with the primary endpoint before concluding.

```bash
python3 <jira-scribe-skill-dir>/scripts/run_with_jira_env.py --root <consumer-project-root> -- \
  curl -sS -H "Authorization: Bearer $JIRA_API_TOKEN" \
  "$JIRA_BASE_URL/rest/api/2/myself"
```

### Decision Table

| `/rest/api/2/project` | `/rest/api/2/myself` | Verdict |
|---|---|---|
| 200 + projects | 200 | Token valid. Proceed. |
| 200 + projects | 401 | Token valid. `/myself` is broken on this instance — ignore it. |
| 401/403 | 200 | Token valid but lacks project browse permission. Check project key. |
| 401/403 | 401/403 | Token invalid or expired. Report auth failure. |

### Verify Specific Project Access

After confirming the token works, verify the target project exists and its issue types are available:

```bash
python3 <jira-scribe-skill-dir>/scripts/run_with_jira_env.py --root <consumer-project-root> -- \
  curl -sS -H "Authorization: Bearer $JIRA_API_TOKEN" \
  "$JIRA_BASE_URL/rest/api/2/project/$JIRA_PROJECT_KEY"
```

### Auth Presence Sanity Check

After any search that returns `total: 0`, verify the request actually carried auth. The fastest check: if the response includes your user's display name or email from a known-authenticated field, auth was present. If in doubt, re-run the same search through `run_with_jira_env.py` explicitly — an anonymous search returns different (often empty) results than an authenticated one, and confusing the two is a common debugging trap.

Never interpret `total: 0` from a search as "project doesn't exist" or "no access" without first confirming auth was applied to that specific request. When a search returns zero results, immediately check: was `run_with_jira_env.py` used? Does the response body contain authenticated-user fields? If uncertain, re-run with the wrapper and compare.

## Search

### JQL Syntax Rules

JQL keywords (`AND`, `OR`, `NOT`, `ORDER BY`, `EMPTY`, `NULL`, `IS`, `WAS`, `CHANGED`, `IN`, `NOT IN`) are **always** in English regardless of Jira locale. Field names and operators use the Jira system language. Values must match the Jira instance's locale for status names, issue type names, etc.

**Common pitfalls that cause misleading errors:**

1. **`project = KEY` not `project=KEY`** — always include a space around operators. `project=PDP` may parse but can produce confusing errors on some Jira versions.
2. **Quote multi-word values** — `status = "In Progress"`, not `status = In Progress`. Single quotes also work: `status = 'In Progress'`.
3. **Status names are localized** — on a Spanish Jira instance, use `"En Progreso"` not `"In Progress"`. Always fetch actual status names from the API before writing JQL.
4. **`IN` operator needs parentheses** — `status IN ("Open", "En Progreso")` not `status in (Open, "En Progreso")`. Values inside `IN` must be quoted strings.
5. **Case-insensitive field names, case-sensitive values** — `PROJECT = PDP` works, but `project = pdp` does not if the project key is uppercase.
6. **JQL parse errors vs. "not found" errors are different** — if Jira says a project or field "does not exist", check JQL syntax first before concluding the project is missing. A malformed query can make Jira misinterpret a project key as something else.

**Debugging JQL errors:** When Jira returns an error about a project or field not existing, the first step is to simplify the JQL to the bare minimum (`project = "PDP"`) and re-run. If the simplified query works, the problem was JQL syntax, not project access.

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

## PR Backlinks And Optional Comments

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

Only add a Spanish comment with the PR URL when the user explicitly asked for it:

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
- **401 on `/rest/api/2/myself` is NOT definitive.** Cross-check with `/rest/api/2/project` or a project-key search before declaring the token broken. See Credential Verification section.
- If `401` or `403` appears on `/rest/api/2/project` or `/rest/api/2/search`, the token is likely invalid or lacks permissions. Report authentication/authorization failure without printing tokens.
- If `400` appears with required fields, show Jira's message and ask for missing fields.
- Never guess custom field IDs.

### Anti-Patterns That Caused Past Incidents

1. **Confirmation bias in auth debugging.** Forming the hypothesis "token is broken" from a single 401 on `/myself`, then interpreting every subsequent error (JQL parse failures, anonymous search results) as confirmation of that hypothesis, instead of doing the obvious test: `project = "PDP"` with the token via `run_with_jira_env.py`.
2. **Confusing JQL parse errors with access errors.** When Jira says a value "does not exist", it may mean the JQL syntax made Jira misinterpret a project key. Always simplify to the minimal query before concluding the project or token is bad.
3. **Mixing authenticated and anonymous requests.** Running some `curl` calls through `run_with_jira_env.py` and others without it produces incomparable results. An anonymous search returning `total: 0` looks identical to an authenticated search returning `total: 0` but means something completely different. Always use the wrapper for every Jira API call, or at minimum verify auth presence before interpreting results.