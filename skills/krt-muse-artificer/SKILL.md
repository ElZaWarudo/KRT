---
name: krt-muse-artificer
description: Run Muse Code (model muse-spark-1.3-contributor) headlessly as a bounded implementation worker on one ready unit in an existing Git worktree. Use when the user or krt-swarm-seneschal asks to hand a fast or settled standard implementation unit to Muse. The caller keeps worktree, review, verification, and release ownership. Not for diagnosis, architecture, or risky decisions.
---

# KRT Muse Artificer

Hand one ready implementation unit to Muse Code and bring back a validated
report. The caller (usually `krt-swarm-seneschal`, sometimes the user directly)
chooses the unit, creates the worktree, and judges the result.

## Good assignments

Muse is the preferred worker for **fast** units: a confirmed edit path, exact
owned files, closed decisions, and named checks (a bug fix with a known cause, a
mechanical change, a targeted test, a bounded UI tweak). Consider it for
**standard** units where only local implementation choices remain: focused
feature work, a contained refactor, tests for specified behavior.

Don't send ambiguous diagnosis, architecture, auth, data, security, migrations,
public contracts, concurrency, or production decisions; those need a deeper
worker and a human decision. If Muse or its model is unavailable, the caller
picks another worker before dispatch. Never swap models silently.

## Running it

Write the assignment as a short text file **outside** the worktree: outcome,
owned paths, acceptance criteria, the exact focused checks, and the stop
condition. Then:

```bash
rtk python3 <skill-dir>/scripts/run_muse_implementer.py \
  --assignment <abs-path>/assignment.md \
  --workspace <abs-path-to-existing-worktree> \
  --terminal-path <abs-private-dir>/terminal.json \
  --log-path <abs-private-dir>/muse.jsonl \
  [--max-model-steps 50] [--timeout-seconds 1800]
```

The runner refuses paths inside the worktree or reused output paths, checks
that the installed `muse exec` exposes the needed headless flags, runs Muse with
approvals off and web tools disabled under a step and time budget, and validates
the terminal report (`status`, `summary`, `changed_files`, `checks`,
`blockers`). Keep the JSONL log private: it can contain prompt and tool content.

## What the result means

The terminal report, exit code, and Muse's prose are claims. Before accepting
the unit, the caller inspects the actual diff, reruns the focused checks, and
applies whatever review the risk calls for. Preserve the worktree and log when a
run fails so it can be diagnosed.

Muse and this skill never stage, commit, push, open PRs, touch Jira, or clean up
worktrees.
