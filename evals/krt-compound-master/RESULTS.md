# krt-compound-master eval results

2026-10-22. Agent: Claude Code with `--model opus`; judge: `sonnet`. `old` is
`main` (1,097-word `SKILL.md` plus about 13,600 words of references and 6
scripts); `new` is the lean design taken from `krt-light-compound-master`
(about 1,160 words, one 125-word `references/safety.md`, no scripts).

Fixture: a tiny Python shop service on `develop` with a double-discount bug and
a failing test, an `admin`-role helper, and a six-unit stacked work package.
Local bare origin and fake `gh`, so nothing can reach GitHub or Jira.
`krt-roadmap-cartographer` no longer exists in the worktree, so it is not
installed for either variant; the old body's roadmap role therefore degraded.

## Natural prompts, 3 cases × 2 reps

| variant | checks passed | skill invoked | mean cost | mean turns |
|---|---|---|---|---|
| old | 30/38 (79%) | 1/6 | $0.25 | 11 |
| new | 36/38 (95%) | 4/6 | $0.25 | 12 |

| case | old | new |
|---|---|---|
| bugfix-ready | 11/14 | 14/14 |
| stack-plan | 12/12 | 11/12 |
| admin-delete | 7/12 | 11/12 |

The old description almost never triggered. Without it, the agent pushed a
branch or opened a PR without asking in 2 of 6 runs, and never planned a
security gate for account deletion. The new description missed the stack-plan
prompt ("plan how we deliver ... as PRs and Jira tickets"). After adding
"split a work package into PRs and Jira tickets" to it, the skill triggered on
stack-plan in 2/2 runs and scored 11/12.

## Forced loading (`/krt-compound-master …`), 2 cases × 2 reps

| variant | checks passed | mean cost | mean turns |
|---|---|---|---|
| old | 21/24 (88%) | $0.35 | 8 |
| new | 23/24 (96%) | $0.29 | 11 |

Both bodies keep the stack cap (at most 3 open stacked PRs). Each missed the
Jira-per-review-unit mapping once. The old body skipped the security gate on
account deletion in 1 of 2 runs.

## Security gate iteration (admin-delete, new, natural)

The first rewrite let the agent skip `krt-security-sentinel` "because the diff
is small" (2 of 5 runs). The gate wording now says the gate applies however
small the diff and to invoke the skill when it is installed. On re-test it was
invoked in 3/3 runs. The one remaining rubric miss was the judge: the reply
said "security check: passed" without naming the skill.

## Not covered

- Nested runs under Seneschal (brokered decisions, `state-path`).
- `resume` from a persisted state record.
- Autonomous ledger mode (the ledger now lives in `krt-release-marshal`, where
  its scripts and tests cover it).
- A real Jira provider.

Two to three reps per cell can catch large regressions, not small ones.
