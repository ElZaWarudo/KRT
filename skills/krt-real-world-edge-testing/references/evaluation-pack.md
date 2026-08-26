# Behavioral Evaluation Pack

This skill carries a dedicated Skill Arbiter corpus under `references/evals/`. It supplements the portfolio baseline without changing or contaminating it.

Validate the hidden-expectation pair from the repository root:

```bash
python3 skills/krt-skill-arbiter/scripts/check_corpus.py \
  skills/krt-real-world-edge-testing/references/evals/cases.json \
  skills/krt-real-world-edge-testing/references/evals/expectations.json
```

Follow `krt-skill-arbiter`'s blind run protocol. Routing cases receive only the prompt; capability cases receive the named target skill. Keep expectations hidden until the runtime response and tool trace are captured.

Score supervisor-captured results against this pack by supplying both corpus paths:

```bash
python3 skills/krt-skill-arbiter/scripts/score_run.py \
  eval-results.json \
  skills/krt-real-world-edge-testing/references/evals/cases.json \
  skills/krt-real-world-edge-testing/references/evals/expectations.json
```

The corpus tests routing, negative triggers, degraded-environment fallback, production/shared-resource permissions, restart integrity, oracle strength, and honest partial completion. It does not constitute a completed RAG or transactional-system pilot; record those separately when suitable systems become available.
