# CI Failure Report Template

Use this compact report unless the user asks for more detail.

```text
CI status: failed | flaky/transient suspected | infra suspected | fixed | unknown

What failed:
- Provider/run:
- Workflow/job/step:
- Commit/PR:

Likely reason:
- <one sentence cause>

Evidence:
- <path/log/check/artifact and the observed signal>
- <history/rerun/local reproduction signal when available>

Flake assessment:
- deterministic | likely flaky | transient infra | unknown
- Rationale: <why>

Recommended next action:
- <smallest useful action>

Verification:
- <commands run/results, or why skipped>

Confidence:
- high | medium | low
```

## Style

- Keep the likely reason to one clear sentence.
- Quote only the shortest useful log fragments.
- Mention line numbers, test names, job names, or artifact paths when available.
- If confidence is low, name the missing evidence instead of padding the report.
- Make the next action executable: command, file to edit, rerun type, owner, or follow-up issue.
