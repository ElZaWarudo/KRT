---
name: krt-deploy-summoner
description: Prepare, inspect, and diagnose deployments across Docker, Docker Compose, Helm, and Kubernetes. Use when a user asks to review deployment manifests, Helm charts or values, Dockerfiles, compose files, Kubernetes resources, rollouts, pods, logs, probes, resources, namespaces, image tags, deployment readiness, rollback plans, smoke tests, CrashLoopBackOff, ImagePullBackOff, failed Helm upgrades, or safe kubectl/helm/docker diagnostic commands. Runtime aliases may expose this as krt:deploy-summoner.
---

# Deploy Summoner

Deploy Summoner helps invoke and inspect the runtime stack without turning every diagnosis into a risky cluster mutation.

Default posture: **read-only first, plan before action**. It may execute local or remote mutating deployment commands only when the user explicitly approves the target, command, namespace/context, and rollback path.

## Load References

- Load `references/deployment-rubric.md` before reviewing manifests, preparing deployment plans, or diagnosing runtime failures.
- Load `references/source-literature.md` when explaining the deployment model or when the user asks what the workflow is based on.

## Workflow

### Step 1 - Establish Target And Safety Boundary

Identify:

- platform: Docker, Docker Compose, Helm, Kubernetes, or mixed;
- target: local, staging, production, cluster/context, namespace, release, workload, service, image/tag;
- task: inspect, plan, deploy, rollback, diagnose, smoke test, or write commands;
- mutation level: read-only, local-only, remote mutation, destructive/rollback.

For remote mutation, require explicit approval before running commands such as `helm upgrade`, `helm rollback`, `kubectl apply`, `kubectl delete`, `kubectl rollout restart`, `docker compose up -d`, or image promotion.

### Step 2 - Inspect Configuration

Use repo-local sources first:

- Dockerfiles, compose files, `.env.example`, build scripts, image tags, healthchecks.
- Helm `Chart.yaml`, `values.yaml`, environment values, templates, hooks, CRDs, helpers.
- Kubernetes manifests for Deployments, StatefulSets, DaemonSets, Jobs, Services, Ingress, ConfigMaps, Secrets references, ServiceAccounts, RBAC, HPA, NetworkPolicy.
- CI/CD deploy scripts and release notes when they define deployment behavior.

Check for common readiness risks:

- unpinned or surprising image tags;
- missing readiness/liveness/startup probes;
- missing resource requests/limits where project policy expects them;
- secret/env/config references without corresponding documented source;
- namespace/context ambiguity;
- unsafe rollout settings, hooks, or migrations;
- values drift between environments;
- missing rollback and smoke-test commands.

### Step 3 - Diagnose Runtime Evidence

For live issues, gather read-only evidence before proposing fixes:

- `kubectl get/describe`, events, pod status, previous logs, init containers, rollout status/history;
- Helm release status/history/values/manifests;
- Docker/Compose ps, logs, config, health status, image IDs;
- service endpoints, ingress status, config/secret references, resource pressure signals.

Prefer the first actionable failure over the last noisy line. Classify the issue as image/build, config/env/secret, probe, resource, scheduling, networking, migration/job, chart/template, rollout, dependency, or unknown.

### Step 4 - Plan Deploy Or Rollback

Return a plan before mutation:

```text
Deployment status: ready | risky | blocked | diagnosing

Target:
- Platform/context/namespace/release:

Findings:
- [severity] [area] issue
  Evidence:
  Impact:
  Action:

Plan:
1. Read-only verification:
2. Mutating command(s), if approved:
3. Smoke checks:
4. Rollback:

Approval needed:
- <exact commands and target>
```

Use Helm dry-runs/templates and Kubernetes diff/server-side validation when available before mutating. For Docker Compose, render/validate config before starting or recreating services.

### Step 5 - Execute Only Approved Actions

When approved:

- restate the exact target and command;
- run one coherent action batch;
- capture rollout/status/log evidence;
- run smoke checks;
- record rollback command or confirm rollback is not applicable.

If the action fails, stop and report the first actionable failure with evidence. Do not keep applying speculative fixes.

## Guardrails

- Never mutate a remote cluster, production host, namespace, Helm release, or Docker runtime without explicit approval.
- Never print secrets, full env dumps, kubeconfigs, tokens, registry credentials, or decoded Secret values.
- Never switch Kubernetes context silently.
- Never delete resources or roll back a release as "cleanup" without approval.
- Prefer `helm template`, `helm lint`, `helm diff` when installed, `kubectl diff`, `kubectl describe`, and read-only logs before mutation.
- Treat production as dangerous even when the command looks routine.
- Make rollback and smoke checks part of the plan, not an afterthought.
