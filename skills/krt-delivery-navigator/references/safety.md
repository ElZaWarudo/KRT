# Safety Model

`krt-delivery-navigator` turns validated requirements into delivery plans. Its output should make work executable without silently expanding scope or pretending uncertainty is resolved.

## Guardrails

- Build from `krt-requirements-weaver` output when it exists.
- Do not silently widen scope during planning.
- Do not present speculative dates as commitments.
- Do not convert a backlog into a random task list; every item should trace back to validated need, risk, or dependency.
- Mark open assumptions and validation needs instead of treating them as implementation facts.
