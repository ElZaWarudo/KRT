# Safety Model

`krt-deploy-summoner` inspects and prepares deployment work. Its default posture is read-only first, plan before action.

## Guardrails

- Classify every action as read-only, local-only, remote mutation, or destructive/rollback before running it.
- Require explicit approval before remote cluster, production host, namespace, Helm release, or workload mutation.
- Never switch Kubernetes context silently.
- Never delete resources, roll back releases, or run cleanup as a side effect.
- Never print kubeconfigs, registry credentials, tokens, secrets, or full environment dumps.
- Prefer `helm template`, `helm lint`, `helm diff`, `kubectl diff`, and dry-runs before mutation.
