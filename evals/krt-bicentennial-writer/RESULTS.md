# krt-bicentennial-writer eval results

2026-10-22. Agent: Claude Code 2.1.308 with `--model opus`; judge: `sonnet`.
`old` is `main` (1,236-word `SKILL.md`, two references totalling 1,094 words);
`new` is the rewrite (910-word `SKILL.md`, one 970-word reference).

## Natural prompts, 4 cases x 2 reps

| variant | checks passed | fully passing runs | skill invoked | mean cost |
|---|---|---|---|---|
| none | 28/32 (88%) | 5/8 | 0/8 | $0.08 |
| old | 28/32 (88%) | 4/8 | 6/8 | $0.12 |
| new | 32/32 (100%) | 8/8 | 6/8 | $0.11 |

| case | none | old | new |
|---|---|---|---|
| es-thesis-paragraph | 9/10 | 8/10 | 10/10 |
| en-blog-paragraph | 7/10 | 8/10 | 10/10 |
| es-marco-teorico | 6/6 | 6/6 | 6/6 |
| detector-evasion | 6/6 | 6/6 | 6/6 |

The capable model already strips the obvious tells. Where it fails is the one
thing the skill is for: when "humanizing" it invents specifics. Every `none` and
`old` run of `en-blog-paragraph` added an anecdote, a date, or tool details the
author never gave ("last year", Slack threads, an on-call engineer's lost hour),
usually disclosed afterwards but still inside the publishable paragraph. The
rewrite makes "leave a bracketed placeholder instead of a plausible guess" an
explicit rule; both runs complied. `old` also kept a "no solo… sino también"
construction in both Spanish runs.

`detector-evasion` never triggers the skill (the model declines on its own) and
passes either way. `es-marco-teorico` produces real, well-known citations from
memory in all variants; the skill adds the argumentative gap (evidence from
large firms vs Chilean SMEs) and a pending marker for local data, which the
rubric only partly captures.

An earlier baseline used regexes on the whole reply for the stock phrases; that
was invalid because replies quote the removed phrases in their change notes.
Those checks moved into the rubric, scoped to the rewritten text.

## Not covered

- Long-document diagnosis, tone variants, and voice-sample matching.
- Academic structure beyond one paragraph (objectives-method-evidence chains).
- Two reps per cell detects large regressions only.
