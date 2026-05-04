# Harness Wise

Harness Wise is a portable skill package for building coding harnesses before a coding agent starts changing files with the confidence of a junior developer after one successful grep.

The short version: it helps an agent pause, inspect the repo intelligently, choose relevant context, identify useful skills, flag stale docs, estimate risk, and produce a compact operational brief before implementation begins.

It is not an app framework. It is not a scanner that pretends to understand your architecture because it saw a folder named `services`. It is a disciplined pre-work harness for agents that would otherwise improvise with a straight face.

## Why This Exists

Modern coding agents are useful, but they can be weirdly eager. Given a feature request, they may:

- Read too much.
- Read too little.
- Trust old docs over current code.
- Invent a pattern because the existing one was three directories away.
- Recommend no specialized skills because nobody asked loudly enough.
- Add tests only after the smoke clears.

Harness Wise exists to make that less normal.

The goal is simple: before coding, build the right harness. A harness tells the next agent what matters, what does not, what is known, what is assumed, what skills may help, and where the risks are hiding.

## What It Provides

The canonical skill lives at:

```text
skills/engineering-harness/
```

It includes:

- `SKILL.md`: the main workflow and trigger description.
- `agents/openai.yaml`: UI metadata for compatible agent runtimes.
- `references/harness-template.md`: the Coding Harness output contract.
- `references/task-classification.md`: feature, bugfix, refactor, migration, review, security, and related task typing.
- `references/modes.md`: quick, deep, bugfix, feature, refactor, skill-audit, harness-review, and docs-trim behavior.
- `references/context-curation.md`: anti-context-bloat rules.
- `references/document-classification.md`: KEEP, SUMMARIZE, IGNORE, STALE, and ASK/VERIFY labels.
- `references/confidence-rubric.md`: high, medium, low, and unknown confidence labels.
- `references/skill-selection.md`: available, missing, review-only, and unverified skill recommendations.
- `references/harness-review.md`: review mode for an existing harness.
- `references/validation-scenarios.md`: prompts for forward-testing changes to the skill.

## How It Works

Harness Wise uses progressive disclosure:

```text
task -> classify -> scan lightly -> curate context -> extract patterns
     -> recommend skills -> estimate impact -> ask only blocking questions
     -> emit harness or review existing harness
```

The main skill file stays small. Detailed rubrics live in `references/` and are loaded only when relevant. This is intentional. A context-saving skill that starts by dumping every rule into context has already lost the plot.

## Modes

- `quick`: small local task, compact harness.
- `deep`: cross-cutting, risky, or architecture-heavy task.
- `bugfix`: prioritize reproduction, nearby code, and regression tests.
- `feature`: prioritize existing patterns, contracts, docs, and tests.
- `refactor`: preserve behavior and public interfaces.
- `skill-audit`: check whether the available skill set is enough.
- `harness-review`: review an existing harness before coding.
- `docs-trim`: classify and summarize docs without making the context window carry furniture.

## Existing Harness Review

If you already have a harness, Harness Wise can review it instead of generating a duplicate.

It checks for:

- Objective and task interpretation.
- Source-of-truth ranking.
- Context plan.
- Documentation freshness.
- Project rules and guardrails.
- Skill recommendations and gaps.
- Risk and impact estimates.
- Blocking questions vs technical assumptions.
- Agent-ready instructions.

The review labels are deliberately plain:

- `Keep`
- `Revise`
- `Missing`
- `Overloaded`
- `Risk`
- `Stale/Verify`

No mystical rubric. Just enough structure to stop a bad harness from becoming a bad implementation with nicer formatting.

## Installation

The canonical source remains:

```text
skills/engineering-harness/
```

Use the Agent Skills installer and let its TUI do the awkward small talk:

```bash
npx -y skills add ElZaWarudo/harness-wise --skill engineering-harness
```

Or skip the guessing and point it at a specific agent:

```bash
npx -y skills add ElZaWarudo/harness-wise --skill engineering-harness -a codex
npx -y skills add ElZaWarudo/harness-wise --skill engineering-harness -a claude
npx -y skills add ElZaWarudo/harness-wise --skill engineering-harness -a cursor
npx -y skills add ElZaWarudo/harness-wise --skill engineering-harness -a windsurf
npx -y skills add ElZaWarudo/harness-wise --skill engineering-harness -a cline
npx -y skills add ElZaWarudo/harness-wise --skill engineering-harness -a continue
npx -y skills add ElZaWarudo/harness-wise --skill engineering-harness -a opencode
npx -y skills add ElZaWarudo/harness-wise --skill engineering-harness -a qwen-code
```

For agents that prefer repo instructions over skill packages, add a short
pointer to `skills/engineering-harness/` in the rule file they read. Do not paste
the entire skill into three different places unless you enjoy maintaining
documentation with a shovel.

## Using It

Point a compatible agent at the skill:

```text
Use $engineering-harness before implementing CSV export for invoices.
```

Or review an existing harness:

```text
Use $engineering-harness to review this harness before coding:

# Coding Harness
Objective: Add invoice CSV export.
Context: Read the entire repo and all docs.
Plan: Implement it.
```

That second example should get flagged. "Read the entire repo and all docs" is not a context strategy. It is a cry for help wearing a bullet point.

## Project Layout

```text
skills/
  engineering-harness/
    SKILL.md
    agents/
      openai.yaml
    references/
      confidence-rubric.md
      context-curation.md
      document-classification.md
      harness-review.md
      harness-template.md
      impact-estimation.md
      modes.md
      skill-selection.md
      task-classification.md
      validation-scenarios.md
```

## Validation

Validate it with whichever validator your target agent runtime uses for skill packages.

The package itself is intentionally stored under `skills/`, so agent-specific adapters can be added without making one tool the landlord.

## Design Notes

Harness Wise is intentionally conservative:

- It does not code.
- It does not pretend old docs are truth when current code disagrees.
- It does not recommend every skill just because the names sound impressive.
- It does not block on technical unknowns that can be verified later.
- It does block when product or scope ambiguity would make the harness misleading.

That may be less magical, but it is much less likely to send an agent into your codebase armed with vibes and a diff.

## Status

Early and useful. The skill package is portable, structured, and validated, and installation is intentionally just the standard `skills` command instead of a bespoke wrapper pretending to be infrastructure.

Future work probably belongs around:

- stronger forward-test automation,
- example harness outputs,
- and whatever unpleasant edge case appears the moment this meets a real repo with three old architectures stacked in a trench coat.
