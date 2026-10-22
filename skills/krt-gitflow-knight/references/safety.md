# Safety Model

`krt-gitflow-knight` changes local branches, the index and history. It never
touches remote state.

- Commit only through `scripts/create_approved_commit.py`, and only what the
  accepted plan lists. Its `block_reasons` are stops, not obstacles to route
  around.
- Don't clear the index, run `git restore --staged .`, `git reset --hard`,
  `git clean` or similar broad cleanup without explicit approval. Pre-existing
  staged or untracked work may be someone else's.
- Ask before hunk-level staging, renaming a pushed branch, or committing on a
  protected branch the user explicitly named.
- Real secrets (`.env`, `.krt/env/*.env`, token or password assignments) never
  enter a commit, even when the user says "all files".
