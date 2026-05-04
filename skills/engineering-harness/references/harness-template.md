# Coding Harness Template

Use this structure for new harnesses. Omit sections that are truly irrelevant in quick mode, but keep the output grounded, compact, and explicit about uncertainty.

```markdown
# Coding Harness

## Objective
[One or two sentences interpreting what the user wants changed, reviewed, or investigated.]

## Task Type
- Type: [feature | bugfix | refactor | migration | integration | architecture | optimization | testing | documentation | review | security]
- Mode: [quick | deep | bugfix | feature | refactor | skill-audit | harness-review | docs-trim]
- Impact shape: [local | cross-cutting | architectural]
- Confidence: [high | medium | low | unknown] - [why]

## Source Of Truth Ranking
1. [Current code paths or "current code, not yet inspected"]
2. [Tests or "tests, not yet found"]
3. [Recent ADRs/specs/docs]
4. [README or older docs]
5. [Comments or inferred behavior]

## Context Plan

**Read First**
- `[path]` - [why this is high priority]

**Summarize**
- `[path]` - [task-specific summary goal]

**Inspect If Needed**
- `[path]` - [condition that would make it relevant]

**Ignore For Now**
- `[path]` - [why it is out of scope]

## Documentation Classification

| Document | Label | Reason | Confidence |
|----------|-------|--------|------------|
| `[path]` | KEEP/SUMMARIZE/IGNORE/STALE/ASK/VERIFY | [reason] | high/medium/low/unknown |

## Project Rules Detected
- [Technology, entry point, config, or test command]
- [Observed layer, naming, error, testing, or dependency pattern]

## Skills

**Recommended**
- `$skill-name` - [required | optional | review-only] - [why]

**Missing Or Desirable**
- `[skill idea]` - [why the current task would benefit]

**Unverified**
- `$possible-skill` - [why availability needs checking]

## Guardrails
- Do not [architecture or scope violation].
- Reuse [existing pattern] before introducing new abstractions.
- Do not add dependencies unless [justification threshold].

## Change Impact Estimate
| Surface | Impact | Notes |
|---------|--------|-------|
| Backend | none/low/medium/high/unknown | [notes] |
| Frontend | none/low/medium/high/unknown | [notes] |
| API contract | none/low/medium/high/unknown | [notes] |
| Data model | none/low/medium/high/unknown | [notes] |
| Tests | none/low/medium/high/unknown | [notes] |
| Docs | none/low/medium/high/unknown | [notes] |
| Deployment | none/low/medium/high/unknown | [notes] |

## Risks
- [Risk] - [mitigation or verification]

## Blocking Questions
- [Only product/scope questions that must be answered before a useful harness exists]

## Assumptions And Deferred Verification
- [Technical unknown] - verify by [inspection/research/test during planning or implementation]

## Execution Plan
1. [Read/verify key context]
2. [Confirm contract or behavior]
3. [Implement or review target area]
4. [Add/update tests or justify no tests]
5. [Run validation]

## Agent-Ready Instructions
[A compact instruction block that a coding agent can follow without re-reading this entire analysis.]
```

## Quality Check

Before returning the harness, verify:

- The objective is concrete enough to guide the next step.
- Product/scope ambiguity is blocked rather than guessed.
- Technical uncertainty is labeled as an assumption or deferred verification.
- Context sections explain why each file or doc matters.
- Guardrails are derived from observed patterns or clearly marked assumptions.
- The harness does not ask the next agent to read broad directories without a reason.

If an existing harness was supplied, use `harness-review.md` before filling this template from scratch.
