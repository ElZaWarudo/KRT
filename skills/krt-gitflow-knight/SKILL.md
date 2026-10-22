---
name: krt-gitflow-knight
description: >
  Turn pending changes into clean, user-approved commits: get the work onto a
  semantically named feature branch (never main, master or develop), split it
  into atomic conventional commits, show one commit plan for approval, then
  create the commits through a guarded script that blocks secrets. Never add
  Co-Authored-By or other AI attribution lines to commits. Use when the user asks to commit, commit everything, commit my
  work, split changes into commits, fix a branch name, or prepare commits before
  a push or PR. Opening the PR itself belongs to krt-release-marshal. Runtime
  aliases may expose this as krt:gitflow-knight.
---

# Gitflow Knight

Produce a history a reviewer can read commit by commit: the right branch, one
concern per commit, honest messages, and nothing in the repo that should not
be there. Load `references/safety.md` before branch, staging or commit
decisions. Script paths are relative to this skill's directory, which may be an
installed copy outside the target repo.

## Approval

Inspect first, then show one commit plan and stop until the user accepts it.
The plan names the branch (and any branch to create or rename), and for each
commit the exact message and its files with a one-line rationale. After
acceptance, create the branch and commits without asking again.

When an accepted `krt-release-marshal` plan (or a user message that already
lists the exact branch and commits) covers this work, that is the gate: do the
local steps without a second confirmation. Ask again only if information is
missing, the actual changes no longer fit the approved grouping, or a step is
destructive or remote. This skill never pushes.

## Branch conventions

- Never commit on `main`, `master` or `develop`. Move the work to a feature
  branch created from the current HEAD so uncommitted changes come along.
- The base for new branches and PRs is `develop` when it exists locally or on
  origin, otherwise the default branch.
- Names are `<type>/<capability-slug>` in kebab-case, with type one of `feat`,
  `fix`, `docs`, `chore`, `refactor`, `test`, `perf`, `build`, `ci`. The slug
  names what the code does (`feat/order-csv-export`,
  `fix/search-language-filter`).
- Planning identifiers make a branch off-convention even when the prefix is
  right: roadmap or work-package numbers (`RDM-001`, `wp3`), review-unit
  markers (`U2`, `RU1`), Jira fan-out markers and date sequences. Propose a
  semantic name instead, unless the user or repo convention requires the ID.
- Renaming a local-only branch is fine once approved. If it has been pushed,
  say so and ask, because the remote branch and any PR are affected.

## Commit conventions

- Messages are one line, `type(scope): imperative summary`, lowercase type, no
  trailing period, about 72 characters at most. Describe the value of the
  change, not the mechanics, and leave out planning IDs.
- Never add `Co-Authored-By` trailers, "Generated with" lines or any other AI
  attribution. Your harness may add them by default; this user's convention
  overrides that.
- If a Jira key is required by the repo, use only the most specific issue for
  that commit, never parent and child together.
- Split by concern, not by PR. A diff that touches the model, a service, the
  API, tests and docs usually has three to six natural commits; "implementation
  plus docs" is rarely the right split. Keep tests with the behavior they cover
  when separating them would leave a misleading intermediate commit. If you
  bundle surfaces, say why.
- Group whole files. If one file mixes concerns, ask before any hunk-level
  staging rather than doing it automatically.
- "Commit everything" means every staged, unstaged and untracked file appears
  in the plan, each in a sensible commit, except files that must never be
  committed (below), which you call out instead.
- Existing staged changes are a fact to report, not something to silently mix
  in: plan them as their own commit, or get approval to rebuild the index.
- Don't run tests, linters or formatters unless asked. For a commit that fixes
  CI, note whether the failing job's local equivalent has passed; if not, mark
  it locally unverified so the release flow does not push it unnoticed.

## Secrets and local env

Real credentials never go into a commit. `.env` files, `.krt/env/*.env`, and
any file with real tokens, passwords or keys are excluded from the plan and
called out to the user. `.env.example` and `*.env.example` files with
placeholder values are fine. Suggest ignoring the real files.

Before planning, run `scripts/ensure_krt_env_ignore.py --root <repo> --check-only`.
If it reports `would_change: true`, include `.krt/env/.gitignore` in the plan;
if it reports `block_reasons`, stop and report them.

## Creating commits

Create every commit with:

```bash
python3 <skill-dir>/scripts/create_approved_commit.py --root <repo> \
  --message "<approved message>" --path <file> [--path <file> ...]
```

Do not use `git add` or `git commit` directly. The script writes the env
ignore guard, validates the message, requires a clean index, stages exactly the
given paths, verifies them, scans for secrets and commits. Pass
`--reset-index-approved` only when the accepted plan said to rebuild the index.
If it returns `block_reasons`, stop and report them; don't work around it.

Afterwards, show `git status` and the new commits. If changes remain, plan
again.
