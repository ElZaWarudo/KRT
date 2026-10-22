# Safety Model

`krt-rebase-smith` rewrites branch history and may update a remote branch.

- Rebase only a feature branch whose identity is clear; never `main`,
  `master` or `develop`.
- Never rebase over uncommitted work, and never stash, commit or discard it
  without the user's choice.
- Remote updates use `--force-with-lease`, never plain `--force`, and run only
  after the user approved that exact command.
- Avoid `git reset --hard`, branch deletion and other destructive commands
  unless the user explicitly asks.
- Don't resolve conflicts silently, and don't merge branches or PRs.
