# Deployment Rubric

Use this rubric for Docker, Compose, Helm, and Kubernetes deployment work.

## Risk Levels

| Level | Meaning | Examples |
|---|---|---|
| Read-only | Safe inspection | `kubectl get`, `kubectl describe`, `helm status`, `docker compose config` |
| Local mutation | Affects local machine only | build image, start local compose stack |
| Remote mutation | Changes shared environment | `helm upgrade`, `kubectl apply`, rollout restart |
| Destructive | Deletes, rolls back, replaces, or may cause downtime/data loss | `kubectl delete`, `helm uninstall`, rollback, DB migration job |

Remote mutation and destructive actions require explicit approval with target and rollback path.

## Review Areas

- **Images:** repository, tag immutability, pull policy, build args, provenance, registry access.
- **Configuration:** env vars, ConfigMaps, Secret references, value overrides, environment drift.
- **Probes:** readiness, liveness, startup, healthchecks, grace periods, false-positive risk.
- **Resources:** requests, limits, storage, ephemeral disk, HPA compatibility.
- **Networking:** Services, ports, Ingress, DNS, NetworkPolicy, TLS.
- **Security:** service account, RBAC, capabilities, privileged mode, secret exposure.
- **Rollout:** strategy, max surge/unavailable, progress deadline, hooks, migrations, jobs.
- **Observability:** logs, events, metrics, labels/annotations, traceability.
- **Rollback:** Helm revision, Kubernetes rollout history, image rollback, data compatibility.
- **Smoke tests:** endpoint, job, CLI, health, synthetic check, or manual verification.

## Common Failure Classes

| Symptom | Likely class | First checks |
|---|---|---|
| CrashLoopBackOff | app/config/probe/runtime | previous logs, env refs, command/args, probes |
| ImagePullBackOff | image/registry/auth/tag | image name/tag, pull secrets, registry access |
| Pending pod | scheduling/resources/storage | events, node selectors, taints, PVCs, quota |
| Ready false | readiness/dependency | describe pod, readiness probe, service dependency |
| Helm upgrade failed | template/hook/resource conflict | helm status/history, rendered manifests, events |
| Service unreachable | network/service/ingress | endpoints, selectors, ports, ingress, DNS |
| Rollout stalled | probes/resources/new version | rollout status, progress deadline, new pod events |

## Report Shape

```text
Deployment status: ready | risky | blocked | diagnosing

Target:
- <platform/context/namespace/release/workload>

Evidence:
- <manifest/log/event/status finding>

Risk:
- <what could break and why>

Recommended action:
- <read-only check, patch, deploy, rollback, or smoke test>

Approval required:
- <exact mutating commands, if any>
```
