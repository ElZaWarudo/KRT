---
name: krt-deploy-summoner
description: Review, diagnose, and plan deployments across Docker, Docker Compose, Helm, and Kubernetes without mutating shared environments unasked. Use when asked whether a chart, values file, manifest, Dockerfile, or compose file is ready for prod; to diagnose CrashLoopBackOff, ImagePullBackOff, pending or unready pods, stalled rollouts, or failed Helm upgrades from manifests, logs, or describe output; to roll out, roll back, restart, or clean up workloads; or to write safe kubectl, helm, or docker commands. Runtime aliases may expose this as krt:deploy-summoner.
---

# KRT Deploy Summoner

Get a workload to a known-good state in its target environment, and make every change to a shared environment something the user sees and approves first. Diagnosis and review are read-only; mutations are proposed as exact commands with a way back.

Read `references/safety.md` before running anything against a cluster, registry, or host.

## Classify before acting

Every command is one of: **read-only** (`get`, `describe`, `logs`, `helm status/history/get values`, `helm template`, `helm lint`, `kubectl diff`, `docker compose config`), **local** (build an image, start a local compose stack), **remote mutation** (`kubectl apply`, `helm upgrade`, `rollout restart`, `scale`, image promotion), or **destructive** (`delete`, `helm uninstall`, `helm rollback`, `rollout undo`, migrations). Read-only and local work proceeds. Remote and destructive commands go into a plan the user approves, naming the context, namespace, release, and exact objects. Editing manifests in the repo is fine; applying them is the approval point.

Never switch kube context or namespace implicitly. Put `--context` and `-n` (or `--kube-context`) on every proposed command so the plan is unambiguous when pasted.

## Readiness review

When asked whether something is ready to ship, check the things that turn a routine rollout into an incident:

- **Image**: mutable tags (`latest`, branch names) with `IfNotPresent` mean nodes run different builds and rollback has nothing to roll back to. Ask for an immutable tag or digest.
- **Probes**: readiness gates traffic; liveness restarts. A liveness probe with no startup allowance kills slow-starting apps in a loop. Slow starts belong in a `startupProbe`, not in a weakened liveness probe.
- **Resources**: missing requests break scheduling and HPA; missing memory limits let one pod starve a node. One replica in prod means every rollout or node drain is an outage.
- **Secrets**: plaintext credentials in values or env. Point to the file and key without repeating the value, since review text gets pasted into PRs and chats. Recommend a Secret or external secret store, and rotation, since the value is already in git.
- **Rollout**: strategy, `maxUnavailable`, progress deadline, hooks and migrations that can't be reversed.
- **Environment drift**: values that differ between environments without a reason.

Report a verdict (`ready`, `risky`, `blocked`), findings with file evidence, and the plan below.

## Diagnosis

Work from the first actionable failure, not the last log line: termination reason and exit code, events in order, previous-container logs, then probes, config, and resources. Check the changelog or diff for what changed in this release. Classify the cause (image, config/secret, probe, resources, scheduling, network, migration, chart/template, rollout) before proposing a fix.

## The plan

A deploy, fix, or cleanup plan always has four parts:

1. **Pre-checks**: `helm lint`, `helm template` or `helm diff upgrade`, `kubectl diff`, or `--dry-run=server`.
2. **The mutation**: exact commands with context and namespace, marked as awaiting approval.
3. **Verification**: `rollout status`, restart counts, events, and a smoke request against the service.
4. **Rollback**: the specific command (`helm rollback <release> <revision>`, `kubectl rollout undo deployment/<name>`, or the previous image tag), plus any data caveat such as a migration that can't be undone.

For cleanup, find out what owns each object before deleting it: a pod owned by a ReplicaSet comes back, a hand-made ReplicaSet with matching labels is probably still serving traffic, and StatefulSet pods carry data. List exact names; never `--all` or label-wide deletes in a shared namespace.

## Executing approved actions

Restate the target and commands, run one coherent batch, capture rollout and smoke evidence, and stop at the first failure with its evidence rather than layering speculative fixes.
