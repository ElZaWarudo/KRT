# Safety Model

`krt-harness-wise` creates or improves coding harness artifacts. It prepares context for implementation but does not implement the change itself.

## Guardrails

- Do not edit application code, tests, migrations, generated clients, or deployment manifests as part of harness creation.
- Do not imply that writing a harness authorizes commit, push, Jira, PR, merge, or release work.
- Build harnesses from existing docs, initialization files, and narrowly relevant source context.
- Mark missing evidence and open assumptions instead of converting them into instructions.
- Keep the harness compact enough for a future agent to use without rereading the whole repo.
