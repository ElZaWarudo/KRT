# Safety Model

`krt-release-marshal` owns the shipping handoff: commits, rebase, Jira, push, PR, reviewers, and Jira follow-up. Merge remains a separate protected action.

## Guardrails

- Never create a PR from `main`, `master`, or `develop`.
- Ask before every push, PR creation/update, PR comment, reviewer request, Jira mutation, or merge unless an accepted plan or active autonomous ledger covers the exact action. For a push, the plan must contain the exact push command and still match remote, branch/refspec, and mode (`-u`, normal, or `--force-with-lease`).
- Do not merge a PR without visible merge eligibility on GitHub, no blocking change requests, mergeable state, required checks satisfied or explicitly handled, and merge authorization for the resolved PR.
- Human reviewer approval is still required on normal/protected bases. It may be skipped only when the base branch is clearly experimental (`experimental/*`, `experiment/*`, `spike/*`, `sandbox/*`, `prototype/*`, or `playground/*`) and GitHub branch protection/rulesets show that approving reviews are not required there.
- Generic approvals such as `dale` are valid only as direct answers to a pending merge prompt for the resolved PR.
- Never include secrets, credentials, env dumps, internal verification logs, or Compound Master planning IDs in PR text.
- Write Release Marshal's GitHub-visible PR prose in English by default. Standalone PR comments are always in English; do not publish a non-English PR comment.
- Use `--force-with-lease`, never plain `--force`.
