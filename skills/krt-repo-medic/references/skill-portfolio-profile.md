# Skill Portfolio Profile

Use this profile to audit a repository of agent skills without turning the report into one finding per file.

## Per-Skill Matrix

Create one row per discovered skill:

| Field | Evidence |
|---|---|
| Skill ID | folder and frontmatter `name` |
| Purpose and trigger | frontmatter `description`; clear positive and negative routing boundary |
| Runtime metadata | canonical `display_name`; canonical ID in `default_prompt` |
| Core structure | concise workflow; directly linked references; deterministic scripts where justified |
| Safety | critical safety reference exists, is explicitly loaded, and appears in the central safety index |
| Verification | script tests, routing/negative-trigger cases, permission/restart/fallback/outcome coverage |
| Catalog | central catalog, examples, dependencies, and aliases agree |
| Overlap | nearest skills and the boundary that prevents collision |
| Status | healthy, watch, attention needed, or blocked |

Use `not applicable` with a reason instead of treating every optional resource as mandatory.

## Stable Finding Register

Deduplicate matrix symptoms by root cause. Assign IDs shaped as `KRT-<AREA>-<slug>`, for example `KRT-EVAL-missing-negative-triggers`. Keep the ID stable across audits while the root cause and remediation remain materially the same.

Each finding records:

- ID and lifecycle: `new`, `persistent`, `changed`, or `resolved`;
- severity and affected skill IDs;
- current repo-relative evidence;
- impact on routing, safety, maintainability, or outcomes;
- smallest useful prescription;
- confidence and verification.

Do not create one copy of a portfolio-wide finding for every affected skill. Do not carry a prior lifecycle state forward without rechecking current evidence.

## Snapshot Boundary

This profile reports current observable state. Do not introduce baseline/snapshot files, automated historical comparisons, or a new persistent registry unless the user explicitly requests that capability. A prior report may guide reinspection but is not current truth.
