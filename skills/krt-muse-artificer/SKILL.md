---
name: krt-muse-artificer
description: Run Muse Code as a bounded implementation worker for a Seneschal executable worker contract. Use when a ready fast or standard unit explicitly selects Muse; Seneschal retains worktree, review, verification, and release ownership.
---

# KRT Muse Artificer

Execute one ready Seneschal Implementer contract with Muse Code model
`muse-spark-1.3-contributor`. This skill owns the Muse invocation and its
terminal artifact. Seneschal owns unit selection, contract materialization,
worktree creation, root observation, review, verification, and reconciliation.

## Admission

- Require an existing hashed `worker-contract-v1` with profile
  `muse_contributor` and lane `fast` or `standard`.
- Require an existing Seneschal-created Git worktree and fresh contract,
  terminal, and JSONL paths outside that worktree.
- Read Seneschal's `references/executable-worker-contracts.md` when invoking
  this skill from a Seneschal wave. Do not create a parallel contract format.
- Run from an environment with both the Seneschal skill and Muse CLI installed.
  Check the installed CLI flags through the runner; an unavailable model is a
  dispatch blocker, not a reason to silently change models.

## Invocation

```bash
rtk python3 <muse-artificer-skill-dir>/scripts/run_muse_implementer.py \
  --seneschal-skill-dir <absolute-seneschal-skill-dir> \
  --contract <absolute-worker-contract.json> \
  --workspace <absolute-existing-worker-worktree> \
  --terminal-path <absolute-private-artifact-dir>/terminal.json \
  --log-path <absolute-private-artifact-dir>/muse.jsonl
```

The runner checks the Seneschal contract, renders its worker envelope, supplies
the terminal schema, invokes `muse exec` with a finite step and elapsed budget,
and validates the terminal artifact. Keep the JSONL private because it can
contain prompt and tool content. Preserve failed worktrees and logs for root
diagnosis.

Return the runner result and terminal path to Seneschal. The terminal, process
exit, and Muse prose are worker claims. Seneschal must independently capture
the diff, command outcomes, and any required certificates before accepting the
unit. This skill never stages, commits, pushes, opens PRs, mutates Jira, or
cleans up worker worktrees.
