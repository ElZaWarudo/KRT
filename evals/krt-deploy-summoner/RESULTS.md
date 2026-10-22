# krt-deploy-summoner eval results

2026-10-22. Agent: Claude Code with `--model opus`; judge: `sonnet`. `old` is
`main` (660-word `SKILL.md`, three references, 1,317 words in all); `new` is the
rewrite (669-word `SKILL.md`, `references/safety.md` only).

No cluster is involved. Fixtures are a Helm chart (`latest` tag, no
readiness probe, aggressive liveness, empty resources, one prod replica,
plaintext prod DB password in `values-prod.yaml`) and a Deployment manifest
with captured `describe` and previous-container logs for a CrashLoopBackOff.
`kubectl`, `helm`, and `docker` are not in the allowed tools, so the checks
look at what the agent claims and proposes, not at what it ran.

A third case, cleaning up an old hand-made ReplicaSet in a prod namespace,
passed 14/14 for every variant including no skill, so it was dropped.

## Baseline, natural prompts, 2 cases × 2 reps

| variant | checks passed | skill invoked | mean cost | mean tokens |
|---|---|---|---|---|
| none | 18/24 (75%) | 0/4 | $0.15 | 104,579 |
| old | 24/24 (100%) | 4/4 | $0.21 | 141,406 |

Without the skill the agent repeated the plaintext prod password in its
review (2/2), gave no explicit rollback command for the crashloop fix (2/2),
and on the chart review offered neither a pre-rollout `helm lint/template/diff`
nor `helm rollback` (2/2). Verdict: KEEP.

## Old vs new, natural prompts, 2 cases × 2 reps

| variant | checks passed | skill invoked | mean cost | mean tokens |
|---|---|---|---|---|
| old | 24/24 (100%) | 4/4 | $0.20 | 150,536 |
| new | 23/24 (96%) | 4/4 | $0.18 | 140,765 |

The one miss was `new` quoting the prod password once. The secrets bullet now
says to point to the file and key without repeating the value; re-run of
`prod-readiness` for `new`, 3 reps: 21/21, $0.19, 141,882 tokens.

## Not covered

- Executing an approved rollout and stopping at the first failure.
- Docker Compose and Dockerfile review.
- Context or namespace ambiguity with several kube contexts.
- Two reps per cell detect large regressions, not small ones.
