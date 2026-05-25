# Safety Model

`krt-state-archivist` compacts Compound Master state while preserving historical detail in archive files. It should reduce live-state noise without losing audit history.

## Guardrails

- Do not compact unrelated project documentation.
- Never overwrite a state file unless a full archive snapshot has been written first.
- Never treat compaction as permission to drop audit history.
- Do not delete detail that was not already archived.
- Do not compact when the active phase, blocker, or next action is unclear.
- Do not archive secrets or credentials into a new location if the state accidentally contains them; stop and ask how to redact.
