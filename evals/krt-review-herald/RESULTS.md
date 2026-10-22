# krt-review-herald eval results

2026-10-22. Agent: Claude Code 2.1.308 with `--model opus`; judge: `sonnet`.
`old` is `main` (1,062-word `SKILL.md` plus 2,347 words of references); `new`
is the lean rewrite (734 words plus 348). Both variants also install
`krt-gitflow-knight` (old or new). Natural prompts only, 3 cases × 2 reps.

The fixture is PR #18 with five unresolved threads: a real bug, a false premise
(a None check for a function that returns `[]`), a public-contract rename, a
nit, and an open design question.

| variant | checks passed | skill invoked | mean cost | mean tokens |
|---|---|---|---|---|
| none | 30/42 (71%) | 0/6 | $0.25 | 261,901 |
| old | 41/42 (98%) | 6/6 | $0.38 | 430,096 |
| new | 42/42 (100%) | 6/6 | $0.31 | 295,672 |

| case | none | old | new |
|---|---|---|---|
| address-comments ("deal with the review comments") | 12/16 | 16/16 | 16/16 |
| resolve-all ("fix ... and resolve all the threads") | 8/10 | 10/10 | 10/10 |
| fix-and-commit ("address ... and commit the fixes") | 10/16 | 15/16 | 16/16 |

Without the skill the agent renamed `total` to `amount` in the public CSV and
JSON on its own, pushed and tried to post replies without asking, wrote no
per-thread replies, and committed with a generic "address PR #18 review
feedback" message plus an AI co-author trailer. The old skill's one miss was a
direct `git commit` with a co-author trailer; the new body routes commits
through `krt-gitflow-knight`. With the new skill, "resolve all" left the rename
and streaming threads open and held every reply until the fix was pushed.

The fake `gh` labels `gh api graphql` mutations and `-f body=` REST replies as
reads, so `setup.py` documents a workaround: the cases match the raw call log
(`../gh-log.jsonl`) for mutation markers. It also git-excludes `__pycache__`,
because bytecode in the judged work product put a null byte in the judge prompt
and crashed the runner.

## Not covered

- Executing approved replies and resolutions (`apply_review_threads.py --execute`).
- Already resolved or outdated threads, and pagination.
- CI failures handed to `krt-ci-questor`.

The two scripts' unit tests cover plan generation and the resolve guardrails.
