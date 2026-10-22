# krt-before-after-herald eval results

2026-10-22. Agent: Claude Code with `--model opus`; judge: `sonnet`. `old` is
`main` (807-word `SKILL.md`); `new` is a light trim (768 words): the file list
and report.json pointers folded together, template-maintenance rules condensed,
and two gotchas made explicit (report missing captures to the user when using
`--allow-missing`; checks nobody ran are `note`, never `ok`). Script, template
and references are unchanged.

Fixture: a settings page with ready-made tiny PNG captures for two screens ×
light/dark × desktop/mobile, one "after" capture deliberately missing, and
notes saying contrast was not checked. Natural prompts, 2 cases × 2 reps.

| variant | checks passed | skill invoked | mean cost |
|---|---|---|---|
| none | 13/26 (50%) | 0/4 | $0.23 |
| old | 26/26 (100%) | 4/4 | $0.28 |
| new | 26/26 (100%) | 4/4 | $0.32 |

Without the skill the agent linked images instead of embedding them, built a
static stacked page with no screen or variant switching, and twice wrote a
Markdown file instead of HTML for the Spanish prompt. The skill's template and
`assemble_report.py` are what make the difference. The cost gap between old
and new is within run-to-run noise (both read the same template and script).

## Not covered

- Live capture with `capture_screens.mjs` (no Node or Playwright in the eval
  sandbox), and the "freeze before first" ordering on a real code change.
- Browser check of the built report.
