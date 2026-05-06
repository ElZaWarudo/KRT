# Impact Estimation

Estimate likely change impact before coding. The estimate guides context gathering, validation, and whether specialized skills are needed.

## Impact Levels

- **none** - No expected effect on this surface.
- **low** - Narrow or indirect effect; simple validation is likely enough.
- **medium** - Meaningful behavior, contract, or coordination risk.
- **high** - Cross-cutting, public, persistent, operational, or hard-to-rollback impact.
- **unknown** - Not enough context inspected; include a verification item.

## Surfaces

| Surface | Look For |
|---------|----------|
| Backend | Services, models, jobs, CLI commands, domain logic |
| Frontend | Pages, components, hooks, state, routing, accessibility |
| API contract | Routes, schemas, serializers, exported types, CLI flags |
| Data model | Migrations, persistence, indexes, backfills, schemas |
| Tests | Existing coverage, fixtures, integration paths, brittle areas |
| Docs | User docs, contributor docs, ADRs, plans, examples |
| Deployment | Config, environment variables, CI/CD, containers, runtime |
| External contracts | Third-party APIs, webhooks, plugins, MCP tools, downstream consumers |

## Risk Signals

Upgrade impact when the task touches:

- Authentication, authorization, permissions, secrets, or user data.
- Data migrations, backfills, persistent state, or destructive operations.
- Public APIs, command-line contracts, exported types, or shared schemas.
- Shell commands, filesystem writes outside the target area, generated artifacts, or tool execution with broad side effects.
- External services, retries, rate limits, webhooks, or network failures.
- Infrastructure, deployment, environment configuration, credentials, or privileged operations.
- Work that may be destructive, affect external systems, or be hard to recover with git.
- Multiple interfaces that should stay behaviorally aligned.
- Stale or contradictory documentation.
- Sparse tests in the affected area.

## Harness Guidance

- For **medium** or **high** impact, include explicit test and review guidance.
- For **unknown** impact, state what must be inspected to classify it.
- Do not overstate certainty. A low-confidence estimate is better than a confident guess.
- If impact is high but the user requested quick mode, note the mismatch and upgrade the harness depth unless the user explicitly narrows scope.
- When risk comes from actions rather than code shape, state the action boundary: what the next agent may do directly after summarizing intended changes, what requires human approval because it is destructive, external, or not git-recoverable, and what should only be planned.
