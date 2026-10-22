# krt-repo-medic eval results

2026-10-22. Agent: Claude Code 2.1.308 with `--model opus`; judge: `sonnet`.
`old` is `main` (693-word `SKILL.md` plus 963 words of references, including a
skill-portfolio audit profile); `new` is the rewrite (482-word `SKILL.md`, 405
words of references), scoped to repository health only. Skill-portfolio audits
now belong to `krt-skill-arbiter`.

Fixture: a small Python service with planted drift (README `make test` with no
test target, CI on Python 3.9 vs `requires-python >=3.11`, docs naming an env
var the code no longer reads, CONTRIBUTING pointing to a moved script, and a
destructive `tools/reset_db.py`).

## Natural prompts, 3 cases x 2 reps

| variant | checks passed | fully passing runs | skill invoked | mean cost |
|---|---|---|---|---|
| none | 39/42 (93%) | 3/6 | 0/6 | $0.16 |
| old | 41/42 (98%) | 5/6 | 6/6 | $0.19 |
| new | 41/42 (98%) | 5/6 | 6/6 | $0.20 |

| case | none | old | new |
|---|---|---|---|
| health-check | 16/16 | 16/16 | 16/16 |
| es-onboarding | 13/14 | 13/14 | 13/14 |
| fix-boundary | 10/12 | 12/12 | 12/12 |

`none` and `new` ran in separate batches from `old` on the same fixture.

Without any skill the agent already finds every planted problem, leaves the
tree untouched, and avoids the destructive script. The skill's measurable
contribution is report shape: every finding carries file evidence and a
concrete fix (`none` missed this in both `fix-boundary` runs). The remaining
failure in all variants is a judge call on whether a prioritized list of six or
seven findings is "short".

This is close to the brief's REMOVE threshold: the skill holds no user-specific
convention or script, and the gap over no skill is formatting. It was kept and
slimmed because the coordinator asked for a repository-health-only version; the
evidence supports either keeping it as a light routing target or removing it.

## Not covered

- Large or multi-service repositories, git-history churn analysis, repeated
  audits with stable finding IDs.
- Two reps per cell detects large regressions only.
