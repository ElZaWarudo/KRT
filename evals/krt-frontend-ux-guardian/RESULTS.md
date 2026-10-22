# krt-frontend-ux-guardian eval results

2026-10-22. Agent: Claude Code with `--model opus`; judge: `sonnet`. Natural
prompts, 2 reps per cell, `--budget 2`. `old` is `main`.

| variant | checks passed | skill invoked | mean cost |
|---|---|---|---|
| none | 42/42 (100%) | 0/6 | $0.15 |
| old | 40/42 (95%) | 6/6 | $0.21 |

| case | none | old |
|---|---|---|
| fix-signup (labels, button, error association, focus, data kept on error) | 16/16 | 16/16 |
| add-delete (confirm/undo, named buttons, focus after removal, empty state, owner guard) | 14/14 | 12/14 |
| review-checkout (loading/double submit, wiped input, color-only status, fixed width) | 12/12 | 12/12 |

The two `old` failures came from a broken `file_matches` check: the buttons
were created in JavaScript, so the `<button` regex missed them. The work met
every rubric item. That check has since been removed. Corrected, the result
is a tie, and the skill cost about 40% more.

Verdict: REMOVE candidate. The skill restates general accessibility and
usability practice that the model already applies unprompted, and it carries
no user convention, script, or domain knowledge. It was not rewritten. The
only edit removed its coordination protocol with the deleted
`krt-interface-inquisitor`.

## Not covered

- Browser verification behaviour (no browser in the sandbox).
- Large existing codebases with their own component conventions.
