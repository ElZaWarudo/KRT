# Skill evals

Behavioral evals that run real headless Claude Code sessions, comparing a
skill against an older version of itself and against no skill at all. They
answer the question `krt-skill-arbiter` can't: does this skill make the agent
do better, and at what cost?

```bash
python3 evals/run_skill_eval.py evals/krt-release-marshal \
  --variant none=none --variant old=main --variant new=worktree --reps 2
```

- A variant is `name=none`, `name=worktree`, or `name=<git-ref>`.
- Each run gets a fresh fixture (`setup.py <case> <dir>`) with a local bare
  `origin`. A fake `gh` (`evals/bin/gh`) answers reads from `gh-state.json` and
  logs every call. Only the variant's skills are installed, as project skills;
  `--setting-sources project` keeps user-level skills out.
- Scoring has two parts. Deterministic checks look at git refs, the working
  tree, `gh` mutations and regexes on the reply. A judge model checks the
  rubric items against the final reply.
- The summary reports pass rate, how often the skill was invoked, and mean
  cost, tokens and time per variant. Per-run transcripts land in `--out`.

A suite is a directory with `cases.json` and an optional `setup.py`. Without
`setup.py`, each run gets an empty repo with one commit.

- `cases.json` has `skill`, `skills` (everything to install; a skill missing
  at a variant's version is skipped, so merged skills can be listed), optional
  `allowed_tools` (extra tools for this suite), and `cases`.
- Each case has `id`, `prompt`, `checks`, `rubric`, and optional
  `judge_files: true`, which shows the judge the diff and any new files.
- Check types: `no_gh_mutation`, `origin_unchanged`, `worktree_unchanged`,
  `refs_unchanged`, `text_matches`, `text_not_matches`, and `file_matches`
  (`{glob: regex}`).
- `--invoke` forces the skill to load, so you can compare bodies. Leave it off
  to test whether the description triggers the skill.

Write cases from real runs that went wrong. Drop any check that passes
without the skill, because it isn't measuring the skill.
