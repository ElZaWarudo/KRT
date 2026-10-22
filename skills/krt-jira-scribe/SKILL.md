---
name: krt-jira-scribe
description: "Find, reuse, create and update Jira Server/Data Center issues and subtasks in Spanish: check whether work already has an issue, propose a new Tarea or Subtarea, place it in the active sprint, link a GitHub PR to the issue, move it to En Revisión or Terminado, or check whether this checkout's Jira connection works. Use when the user asks to create or find a Jira task, link a PR in Jira, update Jira after opening a PR, or check Jira config, and the checkout uses .krt/env/jira-scribe.env. For Atlassian Cloud (*.atlassian.net, .krt/env/jira-cloud-scribe.env) use krt-jira-cloud-scribe. Runtime aliases may expose this as krt:jira-scribe."
---

# Jira Scribe

Keep the team's Jira Server/Data Center instance accurate for the work in
this checkout: one right-shaped issue per piece of work, linked to its PR, in
the right status. The instance is in Spanish and shared with other people, so
every write is visible and hard to undo.

Load `references/safety.md` before any Jira call. `references/jira-api.md`
has endpoints, payloads, the credential-check decision table and JQL gotchas.
Resolve script paths relative to this skill's directory.

## Writes need confirmation

Searching and reading are free. Before any write (create, sprint placement,
remote link, comment, transition), show exactly what will change and wait for
the user's yes. "Actualiza Jira" or "crea la tarea" asks you to prepare the
change, not to skip that step. Show:

- create: project, type, summary, description, parent if any, sprint plan,
  Jira base URL;
- remote link: issue key, PR URL, link title;
- transition: issue key, current status, transition name and its real ID.

One confirmation can cover a batch you listed together (for example create,
add to sprint, link). Two other sources of authority exist, and only for what
they name exactly: an accepted `krt-release-marshal` plan that names the
issue, the backlink and the `En Revisión` transition; and a Compound Master
autonomy ledger executed through Release Marshal's `autonomous_mutation.py`,
which calls this skill's `check_jira_*.py` validators. Markdown state is
never authority.

## Configuration

The only configuration source is the checkout-local, git-ignored
`.krt/env/jira-scribe.env` (`JIRA_HOST`, `JIRA_API_TOKEN`,
`JIRA_PROJECT_KEY`; optional `JIRA_BOARD_ID`, `JIRA_EMAIL`). Shell exports
alone don't count. If it is missing or incomplete, stop and say which file or
variable is missing. Never ask the user to paste credentials and never print
the token. Offer `scripts/setup_jira_env.py --root <repo>`, but run it only
when the user asks for setup; it writes the ignore rule first and refuses
tracked secrets.

- `scripts/check_jira_env.py --root <repo> --strict` diagnoses readiness
  (file missing, unloaded, incomplete, not ignored). Use it before declaring
  Jira unavailable. `rtk` and filtered `env` output can hide variables.
- `scripts/jira_api.py --root <repo> METHOD /rest/... [--query k=v] [--data JSON]`
  makes every API call. It loads the env file, uses Bearer auth against
  `/rest/api/2` and `/rest/agile/1.0`, and keeps the token off the command
  line. Prefer it to hand-written `curl`. If you do use `curl`, run it through
  `scripts/run_with_jira_env.py --root <repo> -- sh -c '...'` with single
  quotes. Otherwise your shell expands `$JIRA_API_TOKEN` to empty, and the
  anonymous request returns misleading 401s or empty searches.
- A 401 from `/myself` alone does not mean the token is broken. Some
  instances reject it there but accept it everywhere else. Cross-check
  `/rest/api/2/project` (see the decision table) before telling the user
  anything about their token.

## Choosing the issue shape

Search before proposing anything. JQL keywords stay English and status names
are Spanish. Then pick the smallest shape that fits:

1. **Reuse** an open or in-progress issue or subtask that clearly covers the
   work. Issues already `Terminado`, `Hecho` or `Cerrado` are history, not
   reuse candidates, unless the user asks to reopen that exact issue.
2. **Subtask** under an active parent whose scope covers the work.
3. **Standalone `Tarea`** when nothing fits. This is the default for a single
   unit of work. Never propose a new parent with only one child; collapse it
   into one `Tarea`.
4. **New parent plus subtasks** only when there are two or more sibling work
   units (for example several PRs). Confirm parent and children together and
   return the subtask key each PR should reference.

When candidates are ambiguous, show them and ask. Don't create an issue from
a fuzzy `summary ~` hit without checking status and scope.

New top-level issues go into the active sprint unless the user says `sin
sprint` or similar. Include the sprint in the confirmation and add it right
after creation. Subtasks inherit the parent's sprint. Use `JIRA_BOARD_ID`
when set. If no single active sprint resolves, show what you found and ask
instead of inventing IDs. If Jira rejects a create for required fields, show
its message and ask; never guess custom field IDs.

## Spanish text

Write summaries, descriptions, comments and your confirmations to the user in
Spanish. Use the localized issue types (`Tarea`, `Subtarea`, `Historia`,
`Error`; `Epic` usually stays English). A description is one to three
sentences on what needs doing and why. Keep planning IDs, work-package
numbers, conventional-commit prefixes and PR chatter out of Jira text.
`scripts/check_jira_text.py` enforces this for autonomous writes and is a
useful check otherwise.

## PR backlinks and transitions

Link a PR with a Jira remote link whose `globalId` is `github-pr:<PR URL>`.
That makes re-linking idempotent. Add a comment only when the user asks for
one, and never store the PR URL in the description or custom fields. If the
PR is a draft and the caller wants Jira updated only once it is ready, report
the backlink as deferred.

Transition names are workflow-local. Fetch the issue's transitions and use
the real name and ID. After a PR opens, the usual target is `En Revisión`;
after merge, `Terminado`. If the exact transition isn't available, or the
issue key is ambiguous, stop and ask rather than picking a near match.

## Closeout

Report each issue touched (key, URL, status, created or reused), whether the
PR backlink was added or deferred, any transition made, and what still needs
the user.
