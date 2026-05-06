# Harness Structure Research

Use this reference when defining or revising the saved harness structure. It records the external basis for the structure so the standard is auditable and can evolve.

## Source Principles

The harness structure is grounded in these official documentation principles:

- OpenAI recommends putting instructions before context, separating instructions from input context, being specific about context and desired outcome, and articulating the desired output format. Source: https://help.openai.com/en/articles/6654000-best-practices-for-prompt-engineering-with-openai-api
- Anthropic recommends structuring complex prompts so instructions, context, examples, and inputs are separated unambiguously, using consistent descriptive section names, and including context or motivation behind instructions. Source: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices
- GitHub Copilot documentation says repository instructions should be short, self-contained, and relevant, and suggests including project overview, folder structure, coding standards, tools, libraries, and frameworks. It also notes practical limits for instruction file consumption in code review. Source: https://docs.github.com/en/copilot/concepts/prompting/response-customization
- VS Code Copilot documentation describes persistent markdown instruction files as a way to keep agent behavior aligned with project requirements and distinguishes always-on project instructions from file/task-specific instructions. Source: https://code.visualstudio.com/docs/copilot/customization/custom-instructions
- Google Gemini prompting guidance emphasizes role/persona, task, relevant context, and explicit output format, plus iteration when results need refinement. Source: https://support.google.com/docs/answer/15013615

## Derived Harness Requirements

Map the source principles into harness sections as follows:

| External principle | Harness requirement |
|--------------------|---------------------|
| Clear task and outcome | `Objective`, `Task Type`, `Execution Plan` |
| Relevant context, not raw dumps | `Source Of Truth Ranking`, `Context Plan` |
| Explicit structure and desired output | Standard markdown headings and `Agent-Ready Instructions` |
| Project-specific rules | `Project Rules Detected`, `Guardrails`, `Skills` |
| Separation of context, instructions, and inputs | Distinct sections for context, risks, assumptions, plan, and final agent instructions |
| Concise persistent instructions | Required minimum sections plus optional sections only when relevant |
| Reviewability and staleness detection | YAML frontmatter with `status`, `scope`, `confidence`, `created`, and `updated` |
| Iterative refinement | `Blocking Questions`, `Assumptions And Deferred Verification`, harness review mode |

## Why This Adds Value

A harness adds value when it reduces the next agent's uncertainty or token cost without hiding risk. Evaluate value with these questions:

- Does it prevent repeated repo discovery by preserving high-signal context?
- Does it bound what to read first and what to ignore?
- Does it expose uncertainty instead of letting an agent infer false certainty?
- Does it carry project rules and guardrails into the implementation turn?
- Does it make validation and review expectations explicit?
- Can another agent resume from it without needing the original chat?

If most answers are "no", keep the harness response-only and compact. If several are "yes", propose a saved harness file.

## Structure Guardrails

- Do not add sections merely because they look complete. Every section must affect execution, review, or risk control.
- Do not treat external prompt guidance as a fixed schema. The schema is local and should adapt to observed agent behavior.
- Keep saved harnesses shorter than broad repository instructions. A harness is task-specific, while `AGENTS.md` or Copilot instructions are project-wide.
- Prefer concrete paths, symbols, tests, commands, and docs over generic advice.
- Keep the final `Agent-Ready Instructions` as the executable handoff; earlier sections justify and constrain it.
