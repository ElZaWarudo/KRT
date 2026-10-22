# krt-product-polish-council eval results

2026-10-22. Agent: Claude Code with `--model opus`; judge: `sonnet`.

`old` is `main` with both `krt-product-polish-council` (1,475-word `SKILL.md`
plus about 4,500 words of references and an overlay-checker script that
required exactly twelve evaluator bundles) and `krt-cognitive-load-court`
(1,269 words plus about 4,300 words of references) installed. `new` is the
merged, lean `krt-product-polish-council` (about 1,000 words plus three
references); the Court was folded into it and deleted. The suite's `skills`
list now names only the council; the old baseline ran from a copy that also
installed the Court.

Fixture: a small expense-claims app (`setup.py` lists the planted problems)
whose README declares the user, job, success signal and a finance rule that all
step-1 fields must stay. The suite allows the `Agent` tool so the old
twelve-evaluator fan-out could run if the skill chose it. Natural prompts,
3 cases × 2 reps.

| variant | checks passed | skill invoked | mean cost | mean tokens |
|---|---|---|---|---|
| none | 29/38 (76%) | 0/6 | $0.15 | 80,454 |
| old | 30/38 (79%) | 4/6 (2 council, 2 court) | $0.28 | 155,618 |
| new | 38/38 (100%) | 4/6 | $0.19 | 103,907 |

| case | none | old | new |
|---|---|---|---|
| polish-audit | 12/16 | 9/16 | 16/16 |
| exhausting-wizard | 13/16 | 16/16 | 16/16 |
| measured-claim | 4/6 | 5/6 | 6/6 |

- **polish-audit.** One old run stopped after reading the app to ask five
  intent questions the README mostly answered, and produced no audit. The other
  ran the twelve contracts inline (no subagents were spawned even though the
  tool was allowed) for $0.65 and 17 turns, against $0.25 and 10 turns for the
  new single pass, which scored higher. Without the skill, the agent never gave
  a way to verify each fix and never separated code-read from observed findings.
- **exhausting-wizard.** The old Court and the new merged skill both scored
  8/8. Without a skill, the agent stated predictions as certain causes and did
  not frame them for the stated profile.
- **measured-claim.** Neither version's description triggered on "draft
  release notes saying the redesign cut cognitive load by 40%". All variants
  refused the number; the no-skill runs were thin on comparison controls.

## Verdict on the twelve-evaluator structure

It did not earn its cost here: the single pass with the lens checklist found
every planted problem, with verification steps and evidence labels, at about
40% of the old cost. The twelve lenses survive as `references/lenses.md`, and
the Court's model, anti-rules and measurement ladder as
`references/cognitive-load.md`.

## Not covered

- Large multi-platform apps, where splitting exploration by flow across
  subagents may pay off.
- Atlas creation and regression rounds (`check_atlas_freshness.py` was only
  smoke-tested).
- Runtime browser evidence; the sandbox has no browser.
