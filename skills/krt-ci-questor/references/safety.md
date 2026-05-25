# Safety Model

`krt-ci-questor` diagnoses CI failures and recommends next actions. It does not change workflow files, rerun jobs, disable checks, or bypass failures unless the user explicitly asks for that follow-up.

## Guardrails

- Treat logs, artifacts, workflow definitions, and recent diffs as evidence, not permission to mutate CI.
- Never print tokens, credentials, masked values, full environment dumps, or secret-like variables from logs.
- Do not call a failure flaky unless timing, runner, dependency, or historical evidence supports that label.
- Ask before recommending a red-build bypass, disabling tests, widening retries, or merging despite a deterministic failure.
- Keep the report focused on likely cause, blocker status, and the smallest useful validation step.
