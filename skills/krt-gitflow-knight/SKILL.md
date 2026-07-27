---
name: krt-gitflow-knight
description: >
  Gitflow-based commit workflow: ensure work happens on a properly named feature
  branch (propose/confirm branch name if missing or off-convention), split
  pending changes into atomic commits with clear messages, present a commit plan
  for user authorization, then stage and create the commits. Use when the user
  asks to hacer commits / commit changes, wants to follow gitflow, or wants help
  preparing commits before pushing/opening a PR. Never add any LLM co-author
  lines to commit messages. Runtime aliases may expose this as krt:gitflow-knight.
---

# Gitflow Knight

## Overview

Create clean, user-approved commits following a gitflow-style process: correct branch first, then plan commits, then execute them.

## Workflow

### 0) Operating rules (non-negotiable)

- Never add "Co-authored-by" lines (or any LLM attribution) to commit messages.
- Use one commit-plan acceptance gate when acting standalone. If this skill is running inside an already accepted `krt-release-marshal` workflow, do not add extra approval gates for local/reversible steps unless required information is missing or the action becomes destructive/external.
- Prefer non-interactive commands. Avoid `git add -p` unless the user explicitly wants an interactive hunk workflow.
- Use the host runtime's command wrapper only when the current repo requires one. The command examples below use plain `git` for portability.
- Do not run tests, linters, or formatters unless the user explicitly asks.
- Before branch, staging, or commit decisions, load `references/safety.md`.
- Before planning commits, run `scripts/ensure_krt_env_ignore.py --check-only` from the repository root. This reports whether `.krt/env/.gitignore` would change without creating directories or writing files, and still blocks if `.krt/env/jira-scribe.env` is already tracked.
- Build commit plans from a deterministic, sorted changed-path list.
- The only allowed way for Gitflow Knight to create a commit is `scripts/create_approved_commit.py --root <repo-root> --message "<approved message>" --path <approved-path>...`. Do not run `git add` or `git commit` directly from this skill. After the commit-plan gate, the script applies the normal (writing) KRT env ignore guard, validates commit-message shape, requires a clean index unless `--reset-index-approved` was explicitly authorized in the visible plan, stages exactly the approved paths, verifies the staged path set, and blocks staged env-secret paths or secret-like environment assignments. `.env.example` and `*.env.example` files are allowed when they contain placeholders rather than real secret values.
- When committing a CI fix, record whether the affected CI job's repo-specific equivalent command has passed locally. If it has not, mark the commit as locally unverified for release handoff; do not participate in a push/update-PR flow unless the user explicitly overrides the verification gap.

### 1) Preflight (do not change anything yet)

- Run `<gitflow-knight-skill-dir>/scripts/ensure_krt_env_ignore.py --root <repo-root> --check-only`.
  - If it reports `would_change: true`, include `.krt/env/.gitignore` in the commit plan as a deterministic local-env guardrail change.
  - If it reports any `block_reasons`, stop before staging or committing.
- Determine current branch: `git branch --show-current`
- Inspect working tree and staging:
  - `git status --porcelain=v1 -b`
  - `git diff --name-only`
  - `git diff --cached --name-only`
- If there are no changes (staged or unstaged), stop and tell the user there is nothing to commit.
- If `git branch --show-current` returns empty, treat it as detached HEAD and ask before creating a branch.

### 2) Enforce gitflow branch hygiene

Goal: all subsequent steps happen on a correctly named feature branch.

- Identify protected/base branches:
  - Treat `main`, `master`, and `develop` as protected (do not commit directly on them).
  - Determine base branch:
    - If `develop` exists locally or on origin, prefer `develop`.
    - Else fall back to `main` (or `master` if that is the default branch).
- Validate current branch name against a simple convention:
  - Allowed types: `feat/`, `fix/`, `docs/`, `chore/`, `refactor/`, `test/`, `perf/`, `build/`, `ci/`
  - Slug: `kebab-case` (letters/digits and hyphens)
  - Example: `feat/tire-family-schema-registry`
  - Treat orchestration/planning identifiers such as `RDM-001`, `U1`, `RU1`, `frt-004`, package numbers, and date-sequence traceability slugs as off-convention unless the user or repo convention explicitly requires them. Prefer semantic capability names such as `feat/public-dpp-integrity-verification`.
  - Derive the slug from the feature, user-visible behavior, or functional surface being changed. Prefer names like `feat/drive-sync-renewal` or `fix/mcp-search-language-filter`, not abstract delivery labels like `feat/ru1-drive-sync`, `feat/work-package-3`, or `feat/foundation-phase`.

Use `develop`/`main` as branch hygiene and PR-target context. Do not change the commit base unless the working tree is clean and the intended base is clear from the user request or enclosing workflow plan.

If the current branch is protected, detached, empty, or off-convention:

1. Propose a branch name based on the user request (or ask the user to provide one).
   - Prefer `<type>/<capability-slug>`, where `capability-slug` names what the code does, not which planning artifact requested it.
   - Strip work-package numbering, review-unit markers, planning prefixes, Jira parent/task fan-out markers, and date-sequence traceability fragments unless the repo explicitly requires them.
2. Include the exact branch name in the commit plan acceptance gate. If running under an already accepted `krt-release-marshal` plan and the branch name is clear, proceed without a separate branch-name gate.
3. After the relevant plan gate, switch to it safely:
   - If there are uncommitted changes, create from current HEAD: `git switch -c <branch>`
   - If the working tree is clean and the base is clear, create from base: `git switch -c <branch> <base>`
   - Or switch: `git switch <branch>`

If the user wants to rename an existing local-only branch and the target name is clear, proceed. If the branch has already been pushed, ask first because the remote implications are external.

### 3) Build a commit plan

Goal: split pending work into atomic, reviewable commits with clear messages. Do not default to a single commit just because the pending work belongs to one PR or one Compound Master package.

- Collect changed files (staged + unstaged) and group them into commits using simple heuristics:
  - `docs/` -> `docs(<scope>): ...`
  - `test/`, `tests/`, `__tests__/` -> `test(<scope>): ...`
  - Build/CI files -> `ci(...)` / `build(...)` / `chore(...)`
  - Product code changes -> `feat(...)` / `fix(...)` / `refactor(...)` depending on intent
- Treat suggested commit grouping from an enclosing `krt-release-marshal` or Compound Master handoff as a starting point, not an override. Refine it when the actual changed files reveal clearer atomic boundaries.
- Sort changed paths lexicographically before grouping and keep that order stable in the visible plan. When staged changes exist, preserve their explicit "Commit 0" grouping unless the user approves rebuilding the plan.
- Prefer three to six commits for broad multi-surface packages when the changes have clear natural boundaries. One or two commits are correct only when the diff truly has one or two coherent concerns; do not use "implementation" and "docs" as the default split for a package that touches persistence, services, API contracts, tests, and deployment/config docs.
- Natural boundaries include:
  - data/model/schema/backfill changes;
  - domain/service enforcement changes;
  - API/controller/generated binding or public contract changes;
  - configuration/deployment surfaces that change runtime behavior;
  - focused tests/fixtures for a coherent behavior surface;
  - docs/orchestration artifacts.
- For multi-surface feature work, actively check whether separate commits are warranted for:
  - persistence/schema/model state;
  - domain service or integration behavior;
  - API/controller/generated client surfaces;
  - configuration/deployment wiring;
  - focused tests/fixtures;
  - docs/orchestration and delivery artifacts.
- Do not collapse distinct runtime surfaces into one broad `feat(...)` commit merely because they all belong to one work package or PR. A commit should be small enough that a reviewer can understand the intent and blast radius without mentally separating unrelated concerns.
- If a proposed grouping has fewer commits than the number of major changed surfaces, either split it further or explicitly explain why bundling preserves buildability/reviewability.
- Keep each commit internally coherent. Do not split tests away from behavior if that would leave an intermediate commit obviously broken, unbuildable, or misleading to review.
- If the user explicitly says to include all files or all changes, the plan must include every staged, unstaged, and untracked file. Do not exclude "unrelated" files by default; instead group them into separate atomic commits and call out their domain clearly.
- If staged changes exist before planning, pause and classify them:
  - Keep staged changes as "Commit 0".
  - Unstage and rebuild the whole plan.
  - Commit staged changes separately with a planned message.
- For CI-fix commits, include verification evidence in the plan when available: minimal diagnostic command, natural sub-suite, and affected CI job equivalent. If only a targeted selector was run and the test relies on global hooks, shared fixtures, or seeded state, call that out as diagnostic-only evidence.
- Do not mix pre-staged changes with newly staged files unless the commit plan explicitly includes that grouping.
- Prefer file-level grouping. If a single file mixes multiple concerns, propose either:
  - a small refactor to split changes first, or
  - an interactive/hunk-based staging approach (only with user approval).
- Default to whole-file commits. If atomicity requires splitting a file, stop and ask whether the user wants interactive/hunk staging. Do not attempt partial staging automatically.

Commit messages should use `type(scope): imperative summary`.

Rules:

- Use a lowercase type.
- Scope is optional but preferred when obvious.
- Avoid a trailing period.
- Keep the summary under ~72 characters when practical.
- Describe user-visible or maintenance value, not implementation mechanics.
- Do not include orchestration IDs such as `RDM-001`, `U1`, package numbers, or date sequences unless the user or repo convention explicitly requires them.
- Do not include both parent and child Jira references in commit messages. If repo convention requires a Jira reference or link in commits, include only the immediately relevant issue for the commit: usually the subtask/work-package issue; use the parent only when there is no more specific child issue.

Examples:

- `feat(auth): add token refresh flow`
- `fix(api): preserve pagination filters`
- `docs(readme): clarify local setup`

Present the plan to the user as the single local commit-plan gate:

- Commit 1: `<message>`
  - Files: `path/a`, `path/b`
  - Rationale: why these files form one logical change
- Commit 2: `<message>`
  - Files: `path/c`
  - Rationale: why this should be separate or why it remains bundled

Ask the user to approve the plan (and any exact commit messages) before staging or committing, unless an enclosing `krt-release-marshal` plan already approved the same branch and commit grouping.

### 4) Execute commits

For each commit in the accepted plan:

- Create the commit only through:
  - `<gitflow-knight-skill-dir>/scripts/create_approved_commit.py --root <repo-root> --message "<exact approved message>" --path <path-a> --path <path-b>`
- If the script reports any `block_reasons`, stop and report them. Do not bypass it with direct `git add` or `git commit`.
- The script owns staging, staged-path verification, env-secret leak checks, and the final `git commit`.

If there were already staged changes before this workflow started:

- Treat them explicitly as "Commit 0" in the plan, or ask the user if you should unstage and restage by plan.
- Never clear the index without user approval. If the accepted plan explicitly says to rebuild the index from approved paths, pass `--reset-index-approved` to `create_approved_commit.py`; otherwise let the script block with `index-not-clean`.

### 5) Post-commit checks

- Show what is left: `git status`
- Show recent commits for confidence only if useful or requested: `git log -n 5 --oneline`
- If there is still pending work, loop back to "Build a commit plan".
