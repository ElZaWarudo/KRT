# krt-interaction-polisher eval results

2026-10-22. Agent: Claude Code with `--model opus`; judge: `sonnet`. `old` is
`main` (1,122-word `SKILL.md` plus 3,167 words in three references); `new` is
the rewrite (about 850 words plus two references, about 1,460 words; the
motion/accessibility/performance reference was folded into
`interaction-craft.md`).

Fixture: the claims app from `evals/krt-product-polish-council/setup.py`
(no submit acknowledgement or double-submit guard, toast-only success,
form-wiping error, instant delete with no failure handling, `transition: all`
with overshoot easing, no reduced-motion rule, no dialog focus handling).
Natural prompts, 3 cases × 2 reps.

| variant | checks passed | skill invoked | mean cost | mean tokens |
|---|---|---|---|---|
| none | 38/42 (90%) | 0/6 | $0.27 | 167,478 |
| old | 41/42 (98%) | 6/6 | $0.41 | 298,188 |
| new | 41/42 (98%) | 6/6 | $0.35 | 237,637 |

| case | none | old | new |
|---|---|---|---|
| feels-dead-audit | 15/18 | 17/18 | 17/18 |
| polish-with-confetti | 16/16 | 16/16 | 16/16 |
| instant-delete | 7/8 | 8/8 | 8/8 |

The skill's margin over no skill is small. What it adds is narrow domain
judgment: without it, the agent twice treated reduced motion as "turn
animation off" without keeping state feedback, once kept the toast as the main
success signal, and once ignored focus after removing a row. Both versions
missed the reduced-motion point once. The model already handles optimistic
deletes, double-submit guards and confetti restraint without the skill.

## Not covered

- Browser verification (no browser in the sandbox), drag and drop, route
  transitions, runtime performance profiling.
- Build-guidance mode for an unimplemented feature.
- Two reps per cell detects large regressions only.
