---
name: krt-skill-arbiter
description: Evaluate KRT skills behaviourally and structurally. Runs real headless agent sessions through evals/run_skill_eval.py to compare no skill, the old version, and a new version on pass rate, triggering, cost, and tokens, and checks portfolio identity, metadata, and safety wiring with check_portfolio.py. Use when adding, rewriting, trimming, or retiring a skill; when asked whether a skill helps, whether its description triggers, or whether a rewrite regressed; to write eval cases from a real failure; or to validate skill metadata before commit. Runtime aliases may expose this as krt:skill-arbiter.
---

# KRT Skill Arbiter

Decide with evidence whether a skill makes the agent do better, and at what cost. A skill earns its place only if the agent does measurably worse without it, or if it carries something the model can't know (the user's conventions, a deterministic script, domain judgment, authority limits). Everything else is context the model pays for on every run.

Read `references/safety.md` before running evals: they spend money and execute an agent against fixtures. Read `references/writing-evals.md` when writing or debugging a suite; `evals/README.md` documents the harness itself, and `evals/krt-release-marshal/` is the worked example.

## Structural check

Run after any skill is added, renamed, or edited:

```bash
python3 skills/krt-skill-arbiter/scripts/check_portfolio.py --repo-root .
```

It enforces that every `skills/krt-*` folder has an entry in `references/portfolio.json` and vice versa; that frontmatter `name` equals the folder and a description exists; that `agents/openai.yaml` has `display_name` equal to the skill ID and a `default_prompt` starting with `Use <skill-id>`; and that a skill marked `safety_critical` has `references/safety.md`, mentions it in `SKILL.md`, and has a row in `docs/safety.md`, while a non-critical skill has neither. It doesn't judge behaviour.

## Behavioural evals

A suite lives in `evals/<skill>/`: `cases.json`, plus `setup.py` when the case needs a fixture.

**Write cases from real failures.** Start from a run that went wrong, or from the specific thing the skill claims to add: a convention, a gotcha, an approval gate, a judgment call. Three or four sharp cases beat a broad corpus. Generic competence (finding an obvious bug, writing a plausible plan) is not what a skill is for, so don't test it.

**Baseline first.** Run with no skill and with the current version before changing anything:

```bash
python3 evals/run_skill_eval.py evals/<skill> \
  --variant none=none --variant old=main --reps 2 --jobs 3 --budget 2 --out <scratch>/<skill>-baseline
```

Then drop every check, and every case, that passes without the skill. It isn't measuring the skill, and it inflates pass rates for every variant.

**Separate triggering from the body.** The `skill invoked` column shows whether the description made the agent load the skill. Natural prompts (phrased the way the user actually talks, without naming the skill) test the description. `--invoke` prefixes `/<skill>` to force loading and isolates the body. If a variant didn't trigger, rerun it with `--invoke` before judging its body; otherwise a description problem looks like a content problem. In the release-marshal pilot the description, not the body, decided most of the gap.

**The REMOVE rule.** If no-skill roughly equals the old skill on every case, including with `--invoke`, and the skill carries no user-specific convention, script, or domain knowledge the model lacks, recommend removal with the evidence. Don't rewrite a skill that has nothing to keep.

**Compare old and new.** After a rewrite:

```bash
python3 evals/run_skill_eval.py evals/<skill> --variant old=main --variant new=worktree --reps 2 --jobs 3 --budget 2
```

Read pass rate together with mean cost, tokens, and time. A rewrite that holds the score at lower cost is a win; one that gains a point at double the tokens may not be. If the new version regresses, fix the skill and re-measure, but change the skill to address the cause, not to echo the case wording; prompts and rubric phrases copied into a skill contaminate future evidence.

Two reps per cell detect large regressions, not small ones. Say so in the results rather than claiming a few points of improvement.

## Reporting

Record results in `evals/<skill>/RESULTS.md`: date, agent and judge models, what `old` and `new` are, tables for natural and forced runs (variant, checks passed, skill invoked, mean cost, mean tokens), the notable failures with the judge's reasons, and what the suite doesn't cover. Keep the transcripts in scratch, not in the repo.
