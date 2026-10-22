# krt-jira-scribe eval results

2026-10-22. Agent: Claude Code with `--model opus`; judge: `sonnet`. Both Jira
skills were installed, so routing was part of the test. `old` is `main`
(2,291-word `SKILL.md`, 1,999-word `jira-api.md`). `new` is the rewrite (979
and 552 words) plus `scripts/jira_api.py`.

Fixture: a feature branch, plus a fake Jira Server/Data Center
(`fake_jira.py`, 127.0.0.1 only, Bearer auth, Spanish workflow) wired through
`.krt/env/jira-scribe.env`. It logs every request, and any write drops
`JIRA_MUTATION_DETECTED` into the repo, which fails `worktree_unchanged`. The
server exits after about 18 minutes, or sooner once the run directory is
deleted. The `unconfigured` case has no env file and no server.

## Natural prompts, 4 cases × 2 reps

| variant | checks passed | skill invoked | mean cost | mean tokens |
|---|---|---|---|---|
| none | 30/50 (60%) | 0/8 | $0.15 | 137,795 |
| old | 50/50 (100%) | 7/8 | $0.29 | 282,854 |
| new | 50/50 (100%) | 8/8 | $0.18 | 161,233 |

`new` ran in a separate pass against the same fixtures, and `old` was not
re-run.

| case | none | old | new | old → new cost |
|---|---|---|---|---|
| unconfigured | 7/12 | 12/12 | 12/12 | $0.22 → $0.15 |
| propose-create | 9/14 | 14/14 | 14/14 | $0.37 → $0.22 |
| pr-review | 6/14 | 14/14 | 14/14 | $0.29 → $0.16 |
| myself-401 | 8/10 | 10/10 | 10/10 | $0.27 → $0.18 |

Without the skill, the agent did the following:

- did not find `.krt/env/jira-scribe.env`, and asked for credentials or
  suggested an MCP server instead;
- wrote long descriptions with acceptance criteria;
- never planned the active sprint;
- proposed a comment instead of a remote link;
- in one run, posted the comment and ran the transition without asking.

So the conventions and the confirmation gate are what the skill adds.

## Not covered

- Parent-plus-subtasks creation for several PRs.
- Executing writes after confirmation.
- Draft-PR deferral.
- Release-marshal and autonomy-ledger authority.

The validators keep their unit tests in `scripts/test_jira_autonomy.py`, and
`scripts/test_jira_api.py` covers the new request helper.
