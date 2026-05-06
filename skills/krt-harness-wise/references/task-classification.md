# Task Classification

Classify the task before gathering deep context. Use the classification to decide what to read first and which risks to surface.

## Task Types

- **feature** - Adds new user-facing or agent-facing behavior. Prioritize architecture patterns, contracts, models, tests, and nearby examples.
- **bugfix** - Corrects broken behavior. Prioritize reproduction details, stack traces, failing tests, nearby code, recent changes, and regression coverage.
- **refactor** - Changes structure without intended behavior change. Prioritize boundaries, public interfaces, tests, compatibility, and blast radius.
- **migration** - Moves frameworks, data, dependencies, runtime, or architecture. Prioritize compatibility, rollout, configuration, and rollback risks.
- **integration** - Connects to an external service, API, plugin, MCP, or data source. Prioritize contracts, auth, retries, error handling, and test doubles.
- **architecture** - Changes system structure or boundaries. Prioritize current patterns, coupling, ownership, and alternatives.
- **optimization** - Improves speed, token use, memory, cost, or throughput. Prioritize baselines, hot paths, measurement, and regression tests.
- **testing** - Adds or improves test coverage. Prioritize behavior contracts, fixtures, brittle tests, and missing edge cases.
- **documentation** - Creates or updates docs. Prioritize source-of-truth ranking and docs freshness.
- **review** - Evaluates existing code, plan, docs, harness, or PR. Prioritize explicit criteria, findings, evidence, and severity.
- **security** - Touches auth, authorization, secrets, public input, privacy, permissions, compliance, or trust boundaries. Prioritize threat surfaces and specialized review.

## Impact Shape

- **local** - One component or narrow file cluster; few callers; low contract risk.
- **cross-cutting** - Multiple layers, interfaces, packages, apps, commands, or docs.
- **architectural** - Changes boundaries, responsibilities, extension points, execution model, or long-term direction.

## Classification Rules

- If several types apply, choose a primary type and list secondary concerns.
- If security, migration, external integration, or public contract surfaces apply, mention them even when not primary.
- If the task is vague, classify the likely shape but mark confidence low.
- If the classification would change what gets built, ask one product/scope question before finalizing.

## Context Priority By Type

| Type | Read First | Common Guardrail |
|------|------------|------------------|
| feature | Existing similar features, contracts, tests | Reuse existing patterns before adding new abstractions |
| bugfix | Failing test, stack trace, target code, regression tests | Reproduce or characterize before changing behavior |
| refactor | Public interfaces, tests, callers | Preserve behavior and contracts |
| migration | Config, dependency files, compatibility docs | Plan rollback and staged validation |
| integration | API/client boundaries, auth, retries, failure handling | Treat external contracts as unstable unless verified |
| architecture | Boundaries, dependency graph, ADRs, examples | Do not introduce a new pattern without explaining why |
| testing | Existing test style and fixtures | Test behavior, not implementation trivia |
| documentation | Code/tests/source docs | Do not let old docs override current code |
| review | Review target and criteria | Findings first, evidence-backed |
