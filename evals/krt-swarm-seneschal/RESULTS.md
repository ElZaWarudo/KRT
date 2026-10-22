# krt-swarm-seneschal eval results

2026-10-22. Agent: Claude Code with `--model opus`; judge: `sonnet`. `old` is
`main` (1,085-word `SKILL.md`, about 25,000 words of references, about 90
scripts and tests); `new` is the lean design taken from `krt-light-seneschal`
(about 1,050 words, a 175-word `references/safety.md`, three simplified Codex
worker profiles, no scripts).

Fixture: a tiny Python toolkit on `develop` with two independent bugs (slugify,
median) and failing tests, a README typo, and `docs/units.md` with four ready
units. Two of them (U1, U2) overlap on auth and migrations. Local bare origin and
fake `gh`. Suite-level `allowed_tools` adds `Edit`, `Agent`, `cd`, and `python`
so workers in sibling worktrees can run tests.

## Natural prompts, 3 cases × 2 reps (none: 1 rep)

| variant | checks passed | skill invoked | mean cost | mean tokens |
|---|---|---|---|---|
| none | 18/20 (90%) | 0/3 | $0.21 | 70,535 |
| old | 40/40 (100%) | 5/6 | $0.38 | 216,418 |
| new | 40/40 (100%) | 4/6 | $0.28 | 147,478 |

| case | none | old | new |
|---|---|---|---|
| two-unit-wave | 8/8 | 16/16 | 16/16 |
| single-task-gate | 6/6 | 12/12 | 12/12 |
| overlap-plan | 4/6 | 12/12 | 12/12 |

Both skill variants dispatched two workers on two-unit-wave and fixed the typo
directly on single-task-gate. The new version's misses on "skill invoked" are
single-task-gate runs, where not loading the skill is the right outcome.
Without a skill, the agent ran U1 and U2 concurrently and planned four
parallel workers. Both skill variants serialized U1/U2 and kept at most two
mutable workers. That is the skill's main measured value.

`new` matched `old` at about 26% lower cost and 32% fewer tokens.

An early run of the first rewrite left both fixes in sibling worktrees and never
ran the combined suite. The reconcile section now says to consolidate into one
candidate (normally the user's checkout) and see the suite pass there; the
measured runs above use that wording.

## Not covered

- Muse Code dispatch (`muse` is not installed here) and Codex Luna profiles.
- Nested Compound Master children and brokered decisions.
- Resume from a persisted run record; autonomous ledger runs.
- Worktree cleanup safety.
