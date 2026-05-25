# Safety Model

`krt-gitflow-knight` prepares local commits. It should keep branch hygiene and commit history clean without surprising the user or touching remote state.

## Guardrails

- Do not commit directly on protected branches unless the user explicitly asks for that exact branch.
- Do not add LLM attribution or co-author trailers.
- Do not stage unrelated files by default; stage the planned paths for each commit.
- Treat pre-staged changes as a separate planning fact instead of mixing them silently with new staging.
- Ask before partial staging, branch rename with remote implications, or destructive commands.
- Never run `git restore --staged .`, `git reset --hard`, or broad cleanup as an unapproved shortcut.
