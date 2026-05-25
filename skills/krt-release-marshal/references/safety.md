# Safety Model

`krt-release-marshal` owns the shipping handoff: commits, rebase, Jira, push, PR, reviewers, and Jira follow-up. Merge remains a separate protected action.

## Guardrails

- Never create a PR from `main`, `master`, or `develop`.
- Ask before push, force-with-lease push, PR creation/update, reviewer request, Jira mutation, or merge unless an accepted plan or active autonomous ledger covers the exact mutation class.
- Do not merge a PR without visible human reviewer approval, no blocking change requests, mergeable state, required checks satisfied or explicitly handled, and merge authorization for the resolved PR.
- Generic approvals such as `dale` are valid only as direct answers to a pending merge prompt for the resolved PR.
- Never include secrets, credentials, env dumps, internal verification logs, or Compound Master planning IDs in PR text.
- Use `--force-with-lease`, never plain `--force`.
