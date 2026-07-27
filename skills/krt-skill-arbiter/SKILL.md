---
name: krt-skill-arbiter
description: Evaluate a KRT skill portfolio with deterministic corpus checks, supervisor-captured pass/fail/inconclusive scoring, and structural portfolio validation. Use when adding or changing skills, auditing routing and negative triggers, testing fallback/permission/restart/outcome behavior, or checking portfolio metadata and safety wiring. It does not execute models or grade its own behavior.
---

# KRT Skill Arbiter

Measure skill behavior without turning the evaluator into another opaque agent.

## Load References

- Load `references/safety.md` before handling prompts, outputs, traces, or tool logs.
- Load `references/evaluation-contract.md` before preparing or scoring a run.

## Workflow

1. Run `scripts/check_corpus.py` against `references/cases.json` and `references/expectations.json`.
2. Give each routing case to the evaluated runtime without its expected skill. Give capability cases with their declared target skill.
3. Keep expected behavior hidden until the runtime response is complete.
4. Have a supervisor record exactly one `pass`, `fail`, or `inconclusive` result per observed case. Preserve evidence outside the status field.
5. Run `scripts/score_run.py <results.json>` to aggregate the captured judgments. Do not convert inconclusive results into passes or failures.
6. Run `scripts/check_portfolio.py --repo-root <repo>` after adding or modifying skills.

Use the bundled scripts only as deterministic validators and aggregators. They do not invoke models, execute case content, or decide whether a response is correct.

## Output

Report:

- corpus version and coverage;
- pass, fail, and inconclusive counts;
- conclusive pass rate;
- failures grouped by evaluation category;
- portfolio contract errors;
- evaluator limitations and evidence location.

Do not claim improvement from one run alone. Compare like-for-like corpus versions and record runtime/model context outside the scored artifact.
