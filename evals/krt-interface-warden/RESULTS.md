# krt-interface-warden eval results

2026-10-22. Agent: Claude Code with `--model opus`; judge: `sonnet`. Natural
prompts (no `--invoke`), 2 reps per cell, `--budget 2`.

`krt-interface-inquisitor` was merged into this skill as its critique mode.
`old` is `main`: for the design cases it is main's warden (1,695 + 1,949
words); for the critique cases it is main's inquisitor **plus** warden
installed together (`legacy-critique/`, because the worktree no longer has
inquisitor and the harness cannot install a missing skill). `new` is the
merged skill (1,169 + 1,257 words, down from 6,708 across both skills).

| variant | checks passed | skill invoked | mean cost |
|---|---|---|---|
| none | 43/52 (83%) | 0/8 | $0.26 |
| old (warden on design cases; inquisitor+warden on critique cases) | 50/52 (96%) | 8/8 | $0.43 |
| new | 52/52 (100%) | 8/8 | $0.35 |

| case | none | old | new | old cost | new cost |
|---|---|---|---|---|---|
| redesign-returns | 12/12 | 12/12 | 12/12 | $0.55 | $0.34 |
| build-claim | 10/14 | 12/14 | 14/14 | $0.71 | $0.59 |
| critique-returns | 13/14 | 14/14 (inquisitor) | 14/14 | $0.25 | $0.22 |
| audit-invoices | 8/12 | 12/12 (inquisitor) | 12/12 | $0.21-0.26 | $0.23 |

Main's warden alone on the critique cases scored 24/26 (it missed the keep-the-
table rationale and the stat-card replacement on `audit-invoices`).

What the doctrine adds over no skill:

- `build-claim`: without the skill, every section became a bordered white
  panel on grey with nested boxes, and the decision did not dominate.
- `audit-invoices`: without the skill, the agent never said why the table
  should stay and did not propose a structure to replace the identical stat
  cards.

`redesign-returns` is saturated: once the prompt says "looks like every
other SaaS template", the base model already strips the cards. It stays as
a regression guard.

## Not covered

- Screenshot or browser-based critique (fixtures are static code only).
- Existing design systems or component libraries that the redesign must reuse.
- Critique-then-fix in one turn.
- Mobile rendering is judged from the CSS, not rendered.

Two reps per cell can detect large regressions, not small ones.
