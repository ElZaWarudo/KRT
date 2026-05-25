# Safety Model

`krt-rebase-smith` rewrites local branch history to keep PRs clean. Rebasing is powerful, so branch identity and push implications must be explicit.

## Guardrails

- Never guess the branch to rebase; use the current branch or an enclosing accepted plan.
- Refuse to rebase protected branches directly: `main`, `master`, or `develop`.
- Require a clean working tree before rebasing.
- Verify whether `develop` exists before choosing it as base.
- Use `--force-with-lease`, never plain `--force`, when rewritten history must be pushed.
- Show the exact force-with-lease command and ask before any remote rewrite.
- Do not resolve conflicts silently or merge PRs as part of this skill.
