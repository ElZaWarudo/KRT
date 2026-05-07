# CI Investigation Playbook

Use this playbook to diagnose CI failures without turning logs into a swamp.

## Evidence Order

1. Run metadata: provider, workflow, job, step, commit, branch, PR/MR, event, actor, timestamp.
2. Check summary and annotations: these often point to file, test, or command faster than raw logs.
3. First actionable error: search above final `exit code`, `Process completed`, or generic failure footer.
4. Job configuration: trigger, condition/rules, matrix, permissions, services, cache, artifacts, timeout.
5. Test reports and artifacts: JUnit/XML, screenshots, traces, coverage reports, build output.
6. History: previous passing run, reruns on same SHA, recent dependency/image/action updates, repeated signatures.

## Failure Signatures

| Signal | Likely class | Checks |
|---|---|---|
| Compile/type/lint error points to changed file | Code regression | Compare diff, run local command, check generated files |
| Test assertion fails consistently | Code or test issue | Identify test intent, fixture setup, changed behavior |
| Same SHA passes after rerun | Possible flake | Check known flaky history and whether external/resource symptoms exist |
| Timeout, connection reset, DNS, 5xx registry/API | Infra or external service | Check provider/service status, retry history, network dependency |
| Missing variable/permission denied/token scope | Secret/environment | Check variable presence and scopes without printing secret values |
| Workflow did not trigger or wrong jobs ran | CI configuration | Check event, branch/path filters, rules, skip annotations, merge conflicts |
| Image/action/plugin started failing without code change | Dependency/toolchain drift | Check pinned versions, release notes, lockfiles, cached layers |
| OOM, disk full, browser crash, worker lost | Runner/resource | Check resource limits, parallelism, test shard, artifact volume |

## Provider-Specific Hints

### GitHub Actions

- Use check annotations and workflow logs before downloading full archives.
- For unexpected skips/triggers, inspect `on:`, branch/path filters, skip annotations, merge conflicts, and default-branch-only events.
- For unclear conditions, download log archives and inspect expression evaluation in job system logs when available.
- Enable debug logging or tool-specific verbose flags only after the normal logs lack enough detail.

### GitLab CI

- Validate `.gitlab-ci.yml` syntax with CI Lint when configuration is suspect.
- For missing or wrong jobs, inspect `rules`, `only/except`, `workflow: rules`, pipeline source variables, and duplicate branch/MR pipelines.
- Verify expected variables are present in the job without exposing sensitive values.
- Reproduce job scripts locally in the configured container image when the command boundary is clear.

### CircleCI

- Use test results and artifacts, not only terminal logs.
- For transient test failures, prefer rerunning failed tests when JUnit results and `circleci tests run` support it.
- Check that JUnit output includes `file` or `classname` when rerun/partition behavior looks wrong.
- Use SSH rerun or full rerun only when targeted rerun cannot answer the question.

## Flake Assessment

Classify as:

- **Likely deterministic:** same command fails repeatedly on same SHA or locally; error maps to changed code/config.
- **Likely flaky/transient:** same SHA has pass/fail behavior; symptom is timing, resource, network, dependency resolution, external service, or known flaky signature.
- **Unknown:** only one failed run and no history/artifacts; recommend evidence-gathering before claiming root cause.

Reruns are evidence, not a cure. If a rerun passes, still record the failure signature and propose ownership when the same class repeats.

## Investigation Commands

Use commands appropriate to the repo and provider. Examples:

```bash
gh run view <run-id> --log-failed
gh run view <run-id> --json conclusion,event,headSha,jobs,status,workflowName
gh run download <run-id>
glab ci view
circleci workflow view <workflow-id>
```

Local reproduction should mirror the failing job command as closely as practical: same package manager, lockfile, runtime version, env shape, and test selector.
