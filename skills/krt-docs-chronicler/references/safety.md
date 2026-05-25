# Safety Model

`krt-docs-chronicler` keeps durable project knowledge current. It should reduce future confusion without creating new sprawl or inventing operational truth.

## Guardrails

- Update the nearest canonical document before creating a new one.
- Do not duplicate truth across multiple files unless one is a short index that links to the canonical source.
- Do not invent commands, environment variables, architecture, guarantees, owners, or production posture.
- Do not preserve stale docs for nostalgia; update, consolidate, archive, or delete when appropriate.
- Never copy secrets, tokens, full env dumps, or credential-bearing logs into documentation.
- Escalate dangerous operational steps into a runbook shape with preconditions, rollback, and verification.
