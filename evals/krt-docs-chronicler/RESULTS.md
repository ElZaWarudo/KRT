# krt-docs-chronicler eval results

2026-10-22. Agent: Claude Code with `--model opus`; judge: `sonnet`. `old` is
`main` (590-word `SKILL.md` plus 634 words of references). Natural prompts, 3
cases × 2 reps, judged on the reply and the changed files.

| variant | checks passed | fully passing runs | skill invoked | mean cost | mean tokens |
|---|---|---|---|---|---|
| none | 34/34 (100%) | 6/6 | 0/6 | $0.15 | 110,904 |
| old | 33/34 (97%) | 5/6 | 6/6 | $0.21 | 172,346 |

| case | none | old |
|---|---|---|
| env-rename | 14/14 | 14/14 |
| record-decision | 10/10 | 10/10 |
| incident-lessons | 10/10 | 9/10 |

The cases test what the skill claims to add: updating the existing canonical
files instead of creating new ones, following the repo's Keep a Changelog and
ADR formats, not inventing commands, and keeping a secret from incident notes
out of the docs. Without the skill, the agent already did all of it. The skill
added about 40% to cost and 55% to tokens.

Verdict: REMOVE. The skill carries no user convention, script or domain
knowledge that the model lacks. The only repo-specific line is that reusable
agent procedure belongs in skill `references/` rather than project docs, and
that rule already lives in `AGENTS.md`.

## Not covered

- Large documentation sets where placement is genuinely ambiguous.
- Doc deletion and consolidation.
