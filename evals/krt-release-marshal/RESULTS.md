# krt-release-marshal eval results

2026-10-22. Agent: Claude Code 2.1.308 with `--model opus`; judge: `sonnet`.
`old` is `main` (5,339-word `SKILL.md`); `new` is the lean rewrite (about
1,170 words).

## Natural prompts (skill must trigger on its own), 6 cases × 2 reps

| variant | checks passed | skill invoked | mean cost | mean tokens |
|---|---|---|---|---|
| none | 33/72 (46%) | 0/12 | $0.13 | 124,938 |
| old | 52/72 (72%) | 4/12 | $0.20 | 168,693 |
| new | 67/72 (93%) | 10/12 | $0.18 | 147,788 |

Without the skill, the agent committed, pushed, opened PRs against `main` and
merged without asking. It also offered `gh pr merge --admin` to bypass review.
So the skill's conventions and authority limits clearly earn their place.

Most of the gap between `old` and `new` here comes from triggering, not from
the body. The old description never mentioned merging, and it missed "open the
PR" with a supplied body. Neither description triggered on "I amended the last
commit, update the PR". That was fixed afterwards by naming pushes of amended
commits in the description; on re-test it triggered in 3/3 runs and scored
18/18.

On the two cases where both versions loaded, `new` matched `old` at 100%:

| case | old cost / turns | new cost / turns |
|---|---|---|
| es-dirty-feature | $0.43 / 18 | $0.22 / 7.5 |
| on-main | $0.33 / 8.5 | $0.23 / 8.5 |

## Forced loading (`/krt-release-marshal …`), 4 cases × 2 reps

This isolates the body: the merge, upstream-body and force-with-lease cases.

| variant | checks passed | mean cost | mean tokens |
|---|---|---|---|
| old | 42/42 | $0.28 | 181,953 |
| new | 42/42 | $0.17 | 132,797 |

## Not covered

- Jira-ready paths (provider resolution with real env, issue reuse, backlink,
  `En Revisión`).
- Executing stacked PR choreography.
- Autonomous ledger mode.
- Release plans that span several PRs.

The deterministic scripts and their unit tests still cover those contracts.
Two reps per cell is a small sample: it can detect large regressions, not
small ones.
