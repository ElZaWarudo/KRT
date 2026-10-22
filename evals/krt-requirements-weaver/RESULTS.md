# krt-requirements-weaver eval results

2026-10-22. Agent: Claude Code with `--model opus`; judge: `sonnet`. `old` is
`main` (854-word `SKILL.md` plus 2,242 words of references); `new` is the
rewrite (about 660 words, `references/safety.md` only). Natural prompts, 3
cases × 2 reps. Both versions triggered in every run.

## Baseline: does the skill earn its place?

| variant | checks passed | skill invoked | mean cost |
|---|---|---|---|
| none | 27/38 (71%) | 0/6 | $0.12 |
| old | 35/38 (92%) | 6/6 | $0.17 |

Without the skill, the agent went straight into solution design when the brief
named technologies (testnets, smart contracts, model choices for the
"blockchain + AI attendance" prompt), did not separate stated from assumed
facts, and stated invented standards (TLS 1.2, AES-256, GDPR) as if they were
requirements.

## Rewrite

| variant | checks passed | skill invoked | mean cost | mean tokens |
|---|---|---|---|---|
| old | 34/38 (89%) | 6/6 | $0.16 | 71,470 |
| new | 37/38 (97%) | 6/6 | $0.17 | 69,343 |

| case | old | new |
|---|---|---|
| client-notes | 11/14 | 14/14 |
| rewrite-vague | 12/12 | 11/12 |
| solution-biased | 11/12 | 12/12 |

The old skill's "ask one question at a time" made it defer acceptance criteria
to a later packet in every client-notes run. The rewrite asks for a draft
baseline with ranked questions in one pass, and acceptance criteria with marked
placeholders. Its one miss was an unflagged standard (HTTP 401, TLS 1.2) in a
rewritten security requirement.

## Not covered

- Multi-turn elicitation (the harness has no user to answer questions).
- Writing the packet to a file.
- Routing against `krt-delivery-navigator` on ambiguous "plan this" prompts.

Two reps per cell can catch large regressions, not small ones.
