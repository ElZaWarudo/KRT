# Source Literature

CI Questor's workflow is grounded in current public CI/CD troubleshooting guidance and flaky-failure research:

- GitHub Actions troubleshooting (`https://docs.github.com/en/actions/how-tos/troubleshoot-workflows`): inspect workflow logs, debug logging, triggers, filters, skipped workflows, job conditions, runner issues, and metrics.
- GitLab CI/CD debugging (`https://docs.gitlab.com/ci/debugging/`): validate config, inspect variables, pin dependencies/images, use artifacts, analyze `rules` and `workflow: rules`, and reproduce job commands locally.
- CircleCI rerun failed tests (`https://circleci.com/docs/guides/test/rerun-failed-tests/`): use uploaded test results, JUnit metadata, and targeted reruns for transient test failures.
- Understanding and Detecting Flaky Builds in GitHub Actions (`https://arxiv.org/abs/2602.02307`): flaky builds undermine CI trust; common flaky categories include tests, network issues, and dependency resolution.
- 230,439 Test Failures Later (`https://arxiv.org/abs/2401.15788`): reruns and failure de-duplication are useful signals but can misclassify true failures as flaky.

## Practical Translation

- Treat logs, annotations, artifacts, and rerun history as evidence with different confidence levels.
- Diagnose trigger/config failures separately from execution failures.
- Pinpoint the first actionable error before summarizing cause.
- Separate deterministic failures from flaky/transient failures using same-commit reruns, history, and failure signatures.
- Recommend the smallest next action that increases confidence or restores the pipeline without masking real defects.
