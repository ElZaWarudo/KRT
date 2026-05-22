# Agent Initialization Context

Load when creating or diagnosing a harness.

Agent initialization context is the project-level instruction layer that should constrain later agents. It is not the whole repository.

## Sources To Detect

| Source | Purpose | Default action |
|---|---|---|
| `AGENTS.md` | Repository rules for agents | Read first |
| `CLAUDE.md` | Compatibility instruction file when retained | Summarize if present |
| `.codex/` | Codex project/runtime config | Summarize filenames and relevant config |
| `.agents/` | Runtime skill/config surface | Summarize filenames and relevant config |
| `skills/*/agents/openai.yaml` | Skill autocomplete/runtime metadata | Inspect when harness concerns skills |

Use `scripts/find_agent_init.py` when available. If a script cannot run, do a small manual scan and label it as fallback.

## Summary Requirements

The harness should include:

- Which initialization files were inspected.
- Rules that materially affect the task.
- Any missing initialization context that lowers confidence.
- Any conflict between user task and repository instructions.

Do not paste entire initialization files into the harness. Summarize the relevant operational constraints.
