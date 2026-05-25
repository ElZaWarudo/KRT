# Safety Model

`krt-compound-master` coordinates planning, review, execution, and release handoff. It may direct other skills, but it must not silently turn orchestration into shipping authority.

## Guardrails

- Do not implement before written and reviewed plan context exists.
- Do not invent product behavior, authorization rules, production posture, Jira topology, or data contracts.
- Do not let worker roles create PRs, request reviewers, transition Jira, push, or merge.
- Treat internal review, Security Sentinel output, and CI prevention evidence as readiness signals only.
- External mutations require the owning skill, an explicit user approval, or an active autonomous ledger plus deterministic validation for the exact mutation.
- Never pass merge authorization from a release plan into a merge action.
