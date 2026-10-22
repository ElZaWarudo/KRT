# krt-harness-wise eval results

2026-10-22. Agent: Claude Code with `--model opus`; judge: `sonnet`. `old` is
`main` (771-word `SKILL.md`, 2,377 words in 9 references, 6 scripts); `new`
is the rewrite (about 720 words, 3 references, 4 scripts). Natural prompts, 4
cases × 2 reps; both versions triggered in every run.

## Baseline: does the skill earn its place?

| variant | checks passed | skill invoked | mean cost |
|---|---|---|---|
| none | 29/42 (69%) | 0/8 | $0.19 |
| old | 41/42 (98%) | 8/8 | $0.29 |

| case | none | old |
|---|---|---|
| natural-handoff | 8/12 | 12/12 |
| sensitive-brief | 10/10 | 10/10 |
| promote-staged | 0/8 | 7/8 |
| billing-diagnose | 11/12 | 12/12 |

Without the skill, the agent wrote handoffs outside `docs/harnesses/` with
code snippets in them. Asked to promote a staged summary, it copied the file
to the wrong place with the budget still in it, and in one run it started
implementing (`invoicer/export.py`). Publication sanitizing of an inline client
brief was fine without the skill.

## Detector bugs found and fixed

The `promote-staged` fixture exposed two gaps in `publication_safety.py`, both
fixed in the rewrite with tests:

- Currency amounts written with a trailing symbol (`48.000 €`) never matched,
  because `\b` after `€` needs a following word character.
- Prefixed secret names (`BILLING_API_KEY=…`, `STRIPE_WEBHOOK_SECRET=…`) were
  missed because `_` blocks `\b`. Stripe/Slack-style key values (`sk_live_`,
  `whsec_`, `xox?-`) are now detected too.

## Rewrite

| variant | checks passed | skill invoked | mean cost | mean tokens |
|---|---|---|---|---|
| old | 40/42 (95%) | 8/8 | $0.30 | 248,543 |
| new | 41/42 (98%) | 8/8 | $0.26 | 213,123 |

| case | old | new |
|---|---|---|
| natural-handoff | 12/12 | 12/12 |
| sensitive-brief | 10/10 | 9/10 |
| promote-staged | 6/8 | 8/8 |
| billing-diagnose | 12/12 | 12/12 |

Old caught the budget amount by reading the file, but reported that the
checker passed. With the fixed detector, the new version gets the warning from
the script and redacts it before promoting. The new version's miss: it
treated "cancelled invoices excluded" as unconfirmed, because the requirements
doc lists it as open while the kickoff states it firmly. That is a defensible
reading of conflicting sources.

## Not covered

- `--overwrite` approval flow and concurrent promotion (unit tests cover the
  script side).
- Patching an existing harness in place.
- Converted evidence with embedded prompt injection.
