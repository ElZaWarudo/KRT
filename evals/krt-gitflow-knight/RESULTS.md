# krt-gitflow-knight eval results

2026-10-22. Agent: Claude Code 2.1.308 with `--model opus`; judge: `sonnet`.
`old` is `main` (1,845-word `SKILL.md`); `new` is the lean rewrite (845
words). Natural prompts only, 4 cases × 2 reps.

| variant | checks passed | skill invoked | mean cost | mean tokens |
|---|---|---|---|---|
| none | 22/50 (44%) | 0/8 | $0.12 | 96,541 |
| old | 50/50 (100%) | 6/8 | $0.14 | 90,675 |
| new | 50/50 (100%) | 8/8 | $0.15 | 117,063 |

| case | none | old | new |
|---|---|---|---|
| on-develop ("commit these changes" on develop) | 3/16 | 16/16 | 16/16 |
| planning-id-branch (`feat/rdm-004-u2-wp3`) | 2/14 | 14/14 | 14/14 |
| secrets-in-tree ("commit everything" with real `.env` files) | 11/12 | 12/12 | 12/12 |
| approved-plan (exact commits pre-approved) | 6/8 | 8/8 | 8/8 |

Without the skill the agent committed straight onto `develop` and onto the
planning-ID branch, in one commit, without asking, and added a
`Co-Authored-By: Claude` trailer (the harness default). With either version it
proposed a semantic branch and an atomic split, stopped for approval, and left
the trailer out. Secret handling is mostly something the model already does.

The old skill missed two invocations but still passed, because its description
said "Never add any LLM co-author lines". The first draft of the new
description dropped that sentence; it was restored so that the convention holds
even when the body never loads. Costs are flat: the skill is small either way.

`setup.py` installs a `commit-msg` hook that appends every message to
`.git/commit-msgs.log`, so the suite can check all created commits for
attribution trailers.

## Not covered

- Pre-staged changes, `--reset-index-approved`, hunk-level splits.
- Renaming a branch that is already pushed.
- CI-fix verification notes.

`scripts/test_commit_guards.py` covers the script invariants. Two reps per
cell can catch large regressions, not small ones.
