# krt-delivery-navigator eval results

2026-10-22. Agent: Claude Code with `--model opus`; judge: `sonnet`. `old` is
`main` (719-word `SKILL.md` plus 1,430 words of references); `new` is the
rewrite (about 760 words plus `roadmap-artifacts.md` and `safety.md`). The
rewrite also absorbs the roadmap/readiness-report use case from the deleted
`krt-roadmap-cartographer`. Natural prompts; both versions triggered in every
run.

## Baseline: does the skill earn its place?

The first 2-rep run was close (none 33/38, old 37/38), so plan-from-packet and
rough-idea got 3 more reps. Combined:

| variant | checks passed | skill invoked | mean cost |
|---|---|---|---|
| none | 60/77 (78%) | 0/11 | $0.13 |
| old | 72/77 (94%) | 11/11 | $0.19 |

| case (5 reps, fleet-roadmap 2) | none | old |
|---|---|---|
| plan-from-packet | 29/40 | 39/40 |
| rough-idea | 19/25 | 21/25 |
| fleet-roadmap | 12/12 | 12/12 |

Without the skill, the plan from a signed-off packet quietly settled the open
question (per-clinic hours) by building it in. It also left named risks
without mitigations, pushed performance and security checks into a final
hardening phase, and presented week counts as commitments. A generic
roadmap from docs was already fine without the skill.

## Rewrite

| variant | checks passed | skill invoked | mean cost | mean tokens |
|---|---|---|---|---|
| old | 38/38 (100%) | 6/6 | $0.19 | 93,988 |
| new | 38/38 (100%) | 6/6 | $0.18 | 102,639 |

Roadmap artifact for Compound Master (`fleet-roadmap-file`, new only, since
the old skill had no artifact convention): 13/14. Both runs wrote
`docs/roadmaps/YYYY-MM-DD-NNN-…-roadmap.md` with `RDM-###` items and returned
the `artifact_kind`/`artifact_path` closeout. The one miss was a borderline
"each item names its source doc" call.

## Not covered

- Readiness-report path (`docs/orchestration/...`) when docs are too thin.
- Plans that exceed team capacity, or deadline-versus-scope trade-offs.
- Routing against `krt-requirements-weaver` on fuzzy "plan this" prompts.
