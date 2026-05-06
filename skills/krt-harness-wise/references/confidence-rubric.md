# Confidence Rubric

Use confidence labels for material conclusions. Do not annotate every sentence; annotate conclusions that affect scope, architecture, skill choice, context selection, or validation.

## Labels

- **high** - Verified from current code/tests/config or multiple consistent sources.
- **medium** - Supported by one reliable source or strong repeated pattern, but not exhaustively verified.
- **low** - Plausible from limited evidence, naming, or partial inspection.
- **unknown** - Not inspected, unavailable, or contradictory.

## Source-Of-Truth Ranking

Default ranking:

1. Current code and configuration.
2. Current tests and fixtures.
3. Recent ADRs, plans, specs, or requirements docs.
4. README and contributor docs.
5. Older docs.
6. Comments and inferred behavior.

Adjust only when the repo clearly establishes another source of truth.

## Confidence Examples

- `Architecture detection: high` - multiple current modules follow the same pattern.
- `Documentation freshness: medium` - docs match current paths but no date is available.
- `Test coverage: low` - tests exist nearby but do not cover the target behavior.
- `Skill recommendation: unknown` - skill inventory is not visible in the current environment.

## Handling Contradictions

When sources disagree:

- Prefer current code/tests over docs.
- Mark the doc or claim as `ASK/VERIFY` or `STALE`.
- State the contradiction briefly.
- Do not resolve product intent from code alone if the user goal conflicts with current behavior; ask a product/scope question.

## Harness Requirement

Every final harness should include at least:

- Overall classification confidence.
- Confidence for architecture/pattern detection when guardrails depend on it.
- Confidence for docs freshness when docs influence the plan.
- Confidence or assumption label for skill recommendations when inventory is incomplete.
