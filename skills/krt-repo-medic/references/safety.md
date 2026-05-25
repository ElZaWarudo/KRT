# Safety Model

`krt-repo-medic` diagnoses repository health and prescribes maintenance. It should produce evidence-backed findings, not surprise rewrites.

## Guardrails

- Do not run expensive tests, destructive commands, formatters, or broad cleanup unless the user asks.
- Do not report a missing dependency, command, or doc without checking likely local alternatives.
- Do not recommend broad rewrites when a small documented fix would restore health.
- Keep findings concrete: evidence, impact, confidence, and recommended next step.
- Separate diagnosis from implementation unless the user explicitly asks to fix the findings.
