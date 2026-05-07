# Source Literature

Deploy Summoner is grounded in current official deployment and runtime documentation:

- Kubernetes troubleshooting applications (`https://kubernetes.io/docs/tasks/debug/debug-application/`): inspect Pods, Services, StatefulSets, init containers, running containers, and termination reasons when diagnosing application issues.
- Kubernetes rolling updates and rollbacks (`https://kubernetes.io/docs/tasks/run-application/update-deployment-rolling/`): verify rollout progress, understand progress deadlines, and use rollout history/rollback deliberately.
- Kubernetes `kubectl debug` reference (`https://kubernetes.io/docs/reference/kubectl/generated/kubectl_debug/`): use debug sessions and ephemeral containers for deeper troubleshooting when standard inspection is insufficient.
- Helm chart best practices (`https://helm.sh/docs/chart_best_practices/`): structure charts, values, templates, dependencies, labels, RBAC, CRDs, and pod templates carefully.
- Helm values best practices (`https://docs.helm.sh/docs/chart_best_practices/values/`): keep values understandable, document `values.yaml`, and design values for users and template authors.
- Docker Compose production guidance (`https://docs.docker.com/compose/how-tos/production/`): adapt compose files for production, rebuild/recreate changed services deliberately, and use production-specific overrides.
- Docker Compose services reference (`https://docs.docker.com/reference/compose-file/services/`): healthchecks and service configuration affect runtime readiness and diagnosis.

## Practical Translation

- Inspect rendered configuration before mutating live runtime.
- Treat context, namespace, release, and image tag as safety-critical facts.
- Diagnose from events, status, logs, rendered manifests, and rollout history before guessing.
- Make rollback and smoke checks explicit before deployment.
- Keep secrets masked and never decode or print sensitive values by default.
