# Deterministic Validation

Load when using bundled scripts or interpreting their output.

Scripts provide mechanical evidence. They do not replace agent judgment about task meaning, risk, or whether a harness is useful.

## Scripts

```text
scripts/find_agent_init.py
scripts/find_harness.py
scripts/check_harness.py
scripts/check_evidence.py
scripts/promote_evidence.py
scripts/publication_safety.py
```

Expected JSON shape:

```json
{
  "allowed": true,
  "errors": [],
  "warnings": [],
  "summary": {},
  "paths": []
}
```

## Failure Handling

- If a script reports errors, do not claim the mechanical property passed.
- If a script cannot run, label the result as fallback/manual and lower confidence where appropriate.
- Warnings can be accepted when the harness explains why the heuristic is safe.
- Errors in `check_harness.py` must be fixed before marking a harness `ready`.
- Errors in `check_evidence.py` block promotion.
- Sidecar warnings require exact, non-empty entries in `warning_decisions`.
- `promote_evidence.py` refuses path escape and implicit overwrite, copies only staged Markdown atomically, and rescans the destination.

## Validation Targets

`check_harness.py` should catch:

- Missing or malformed frontmatter.
- Missing required sections.
- Invalid `status`, `scope`, or `confidence`.
- Absolute local filesystem paths.
- `krt-harness-wise` self-reference in the harness body.
- Broad read instructions such as reading an entire large directory without a boundary.
- Publication-safety findings through the detector shared with evidence promotion.
