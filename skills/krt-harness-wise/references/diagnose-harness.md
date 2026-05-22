# Diagnose Harness

Load when a harness path is provided, pasted, or discovered as a likely match.

## Diagnosis Contract

Review the existing harness before generating a replacement. Classify the verdict:

- `Ready to use`: no blocking gaps.
- `Patch recommended`: salvageable with focused edits.
- `Regenerate recommended`: misleading, stale, or structurally incomplete.
- `Blocked`: objective or target is too ambiguous to judge safely.

## Finding Labels

| Label | Meaning |
|---|---|
| `Missing` | Required harness structure or evidence is absent. |
| `Revise` | Present but unclear, stale, or too weak. |
| `Overloaded` | Too much broad context or directory-level reading. |
| `Risk` | Guidance may cause unsafe or mis-scoped implementation. |
| `Stale/Verify` | Depends on unverified docs or assumptions. |
| `Keep` | Useful as written. |

Severity:

- `P1`: likely to mislead implementation or miss a blocking scope issue.
- `P2`: usable but missing meaningful context, validation, or guardrails.
- `P3`: clarity or compactness improvement.

## Improvement Rules

- Patch when the objective is clear and the existing harness has a usable core.
- Regenerate when patching would be longer than rebuilding, or when source-of-truth/context guidance is mostly wrong.
- Preserve still-valid frontmatter and evidence when patching.
- Keep diagnosis findings out of the harness body unless the harness status is `review`.
- Run `check_harness.py` before and after a patch when possible.

## Output Shape

Lead with findings:

```markdown
# Existing Harness Review

## Verdict
[Ready to use | Patch recommended | Regenerate recommended | Blocked]

## Findings
| Severity | Label | Section | Issue | Recommendation |
|---|---|---|---|---|

## Recommended Action
[Patch/regenerate/use as-is]
```

If the harness was patched, also report path, status, validation result, and remaining deferred verification.
