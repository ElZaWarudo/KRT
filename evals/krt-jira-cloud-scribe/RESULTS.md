# krt-jira-cloud-scribe eval results

2026-10-22. Agent: Claude Code with `--model opus`; judge: `sonnet`. Both Jira
skills were installed. `old` is `main` (1,393-word `SKILL.md`, 798-word
`jira-cloud-api.md`). `new` is the rewrite (1,016 and 550 words) plus
`scripts/jira_api.py`.

The fixture is shared with `evals/krt-jira-scribe` (`setup.py` imports its
builder). The fake Jira runs in Cloud mode: Basic auth (email plus token)
only, v3 paths, `/search/jql`, and `.krt/env/jira-cloud-scribe.env`. In
`unconfigured-server-file`, only the Server/Data Center env file exists, and
the Cloud skill must not borrow it.

## Natural prompts, 3 cases × 2 reps

| variant | checks passed | skill invoked | mean cost | mean tokens |
|---|---|---|---|---|
| none | 23/42 (55%) | 0/6 | $0.11 | 78,290 |
| old | 40/42 (95%) | 6/6 | $0.24 | 213,536 |
| new | 42/42 (100%) | 6/6 | $0.18 | 150,864 |

`new` ran in a separate pass against the same fixtures.

| case | none | old | new | old → new cost |
|---|---|---|---|---|
| unconfigured-server-file | 9/14 | 14/14 | 14/14 | $0.16 → $0.17 |
| propose-create | 8/14 | 12/14 | 14/14 | $0.30 → $0.20 |
| pr-review | 6/14 | 14/14 | 14/14 | $0.27 → $0.16 |

In propose-create, `old` missed twice. One run offered to attach the work to
the closed KRT-10. The other did not resolve the active sprint by name. Without
the skill, the agent suggested fixing `jira-scribe.env` for Cloud and asked
for credentials.

## Not covered

- Executing writes.
- ADF payload correctness, because no write reaches the server.
- Create-metadata custom fields.
- Real Atlassian `/search/jql` pagination.
