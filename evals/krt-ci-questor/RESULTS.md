# krt-ci-questor eval results

2026-10-22. Agent: Claude Code with `--model opus`; judge: `sonnet`. `old` is
`main` (984-word `SKILL.md` plus about 1,085 words of references). No rewrite
was measured. The verdict is **REMOVE**.

Fixture: a small Python billing repo. The PR branch renamed a status value
from `cancelled` to `canceled`. CI runs `unittest -f` (failfast), so the log
shows only the first broken test, and `tests/test_reports.py` is broken too
but hidden. The log ends with a misleading cache `ECONNRESET` error from
post-job cleanup. A suite-local `gh` wrapper (`gh_runs.py`, put on PATH
through the fixture's `.claude/settings.json` env) serves `gh run
list/view --log-failed` and logs `gh run rerun` as a mutation.

## Results, 3 cases × 2 reps

| variant | run | checks passed | skill invoked | mean cost |
|---|---|---|---|---|
| none | natural, fixed fixture | 34/34 (100%) | 0/6 | $0.13 |
| old | forced (`/krt-ci-questor …`) | 34/34 (100%) | 6/6 | $0.22 |
| old | natural, fix-and-verify only | 10/10 | 0/2 | $0.17 |

The first natural pass ran before two fixture fixes. With the same failures
in both variants, it scored none 21/24 and old 20/24 on why-failed plus
rerun-flaky:

- running the tests left `__pycache__` in the tree, which now has a
  `.gitignore`;
- one rerun-flaky rubric item required citing "attempt 2" and has since been
  loosened.

The old description triggered in 2 of 6 natural runs, so the forced run is
the fair comparison of bodies.

Without the skill, the agent did all of the following:

- found the deterministic cause;
- ignored the `ECONNRESET` noise;
- noticed that failfast hid `test_reports.py`;
- refused to rerun a "flaky" job and explained why;
- fixed both tests;
- verified with the full workflow command, without pushing.

The skill added cost and nothing measurable.

## Why REMOVE

The skill has no scripts. Its content is general CI triage that the current
model already does: read the first actionable error, separate flakes from
deterministic failures, keep secrets out, and choose the smallest next
action. The one user-specific rule, that a CI fix needs local parity with the
failing job before it is pushed, already lives in `krt-release-marshal`.

## Not covered

- GitLab, CircleCI or Jenkins.
- Infrastructure failures that really are flaky.
- Secret-bearing logs.

These are general skills too, and nothing suggests the model needs help
there.
