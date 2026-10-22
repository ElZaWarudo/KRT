# krt-rebase-smith eval results

2026-10-22. Agent: Claude Code 2.1.308 with `--model opus`; judge: `sonnet`.
`old` is `main` (1,064-word `SKILL.md`); `new` is the lean rewrite (677
words). Natural prompts only, 4 cases × 2 reps.

| variant | checks passed | skill invoked | mean cost | mean tokens |
|---|---|---|---|---|
| none | 30/44 (68%) | 0/8 | $0.11 | 94,030 |
| old | 44/44 (100%) | 8/8 | $0.14 | 109,701 |
| new | 43/44 (98%) | 8/8 | $0.13 | 104,754 |

| case | none | old | new |
|---|---|---|---|
| stacked-squash (parent squash-merged into develop) | 11/14 | 14/14 | 13/14 |
| dirty-tree ("rebase this onto develop and push it") | 2/12 | 12/12 | 12/12 |
| plan-push-mode-changed (plan approved a plain push) | 11/12 | 12/12 | 12/12 |
| plan-push-matches (plan approved `git push -u`) | 6/6 | 6/6 | 6/6 |

Without the skill the agent stashed uncommitted work on its own, rebased and
force-pushed, all without asking. For the squash-merged parent it got the
right result by hand-picking commits but never used `--onto`.

The single `new` miss is a wording check: the run dropped the parent commits
correctly and asked before `--force-with-lease`, but its reply did not print
`--onto`. Both versions refused to reuse a plan's plain-push approval once the
rewrite needed `--force-with-lease`, and neither re-asked for a push the plan
had approved exactly.

## Not covered

- Missing `develop` (asking for another base).
- Conflict handling during the rebase.
- Refusing to rebase a protected branch.

Two reps per cell can catch large regressions, not small ones.
