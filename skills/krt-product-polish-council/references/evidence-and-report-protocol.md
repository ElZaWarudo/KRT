# Evidence, Rating, and Reporting Protocol

## Contents

1. Evidence labels
2. Dimension ratings
3. Finding severity
4. Evaluator return contract
5. Synthesis rules
6. Final report format
7. Regression after remediation

## 1. Evidence Labels

- `observed`: reproduced directly at runtime, in a recording, or through an equivalent artifact.
- `code`: demonstrated by code, configuration, or a test, but not reproduced at runtime.
- `declared`: intent confirmed in the atlas by an authoritative source.
- `inferred`: a reasonable conclusion that has not yet been confirmed.
- `unverified`: a known condition or surface without sufficient evidence.

Prefer `observed` for behavior and `declared` for intent. Code alone does not prove that an interaction is reachable or understandable. An inference must never support a P0 or P1 by itself.

## 2. Dimension Ratings

Use a short scale and always include confidence:

- **0 — Broken or absent**: prevents completion or understanding of material flows, or exposes serious loss.
- **1 — Fragile**: works on the happy path but fails frequently, inconsistently, or in ways that are hard to recover from.
- **2 — Solid**: covers normal use and the main risks, with specific quality gaps remaining.
- **3 — Polished**: behaves predictably, tolerantly, and consistently across the examined flows and conditions.
- **NA — No evidence/not applicable**: the dimension or condition does not apply to the scope or could not be verified.

Confidence:

- `high`: direct evidence across all assigned material flows;
- `medium`: partial direct evidence plus consistent code or documentation;
- `low`: mostly inferences, isolated screenshots, or inaccessible areas.

Do not calculate a global average. Show the full profile and highlight the lowest material rating. `NA` is not zero.

## 3. Finding Severity

- **P0 — Blocker or serious harm**: primary flow is impossible; work is lost or corrupted; misleading state has serious consequences; the flow is completely inaccessible; or an irreversible action lacks sufficient protection.
- **P1 — Trust or recovery failure**: high likelihood of error, repetition, disorientation, abandonment, or inability to recover in an important flow.
- **P2 — Systemic friction**: inconsistency, perceived slowness, ambiguity, or quality debt that makes the task harder but does not prevent it.
- **P3 — Seam or refinement**: a real finish defect with limited impact; a polish opportunity after P0-P2.

Within a severity, sort by frequency, flow centrality, number of affected roles or platforms, and reversibility. Estimate effort as `S`, `M`, or `L` only after defining a correction; do not lower severity because the fix is expensive.

## 4. Evaluator Return Contract

Return structured YAML or Markdown with these fields:

```text
evaluator: <NN — name>
dimension: <canonical dimension>
rating: <0|1|2|3|NA>
confidence: <high|medium|low>
coverage:
  flows: [FLOW-...]
  surfaces: [SURF-...]
  platforms: [PLAT-...]
  gaps: [<unverified item>]

findings:
- id: POL-<NN>-<sequence>
  severity: <P0|P1|P2|P3>
  title: <specific failure>
  evidence_type: <observed|code|declared|inferred|unverified>
  evidence: <exact behavior, location, condition and source>
  user_effect: <confidence, completion, speed, recovery or error impact>
  correction: <smallest concrete product/code/content change>
  verify: <observable acceptance check>
  affected: [FLOW-..., SURF-..., ROLE-..., platform]
  frequency: <frequent|occasional|rare|unknown>
  effort: <S|M|L|unknown>

keep:
- <successful behavior that should survive fixes>

unknowns:
- <missing evidence and exact next probe>

cross_refs:
- <dimension and evidence for another evaluator/lead>
```

Allow `findings: []`. Do not invent debt to fill the contract.

## 5. Synthesis Rules

1. Validate that every finding has evidence, an effect, a correction, and verification.
2. Reject or downgrade claims whose evidence does not support the severity.
3. Assign one primary dimension per cause; keep secondary dimensions as cross-references.
4. Merge findings when they share a cause, flow, and correction criterion. Keep different causes separate even when they appear on the same screen.
5. Detect systemic patterns: one broken convention across three surfaces matters more than three isolated cosmetic tickets.
6. Identify the weakest link by severity, centrality, and rating, not by average.
7. Build a backlog:
   - `Now`: P0/P1 and systemic causes that block trust or recovery;
   - `Next`: frequent or cross-cutting P2 findings;
   - `Later`: P3 findings and bounded refinements.
8. Keep a `Keep` list so remediation does not destroy patterns that already work.
9. Separate confirmed debt from verification gaps.

## 6. Final Report Format

```text
# Product Polish Audit

## Verdict
<one paragraph: perceived maturity, weakest link and consequence>

## Scope and freshness
- Atlas: <path, status, fingerprint>
- Commit/environment:
- Flows, roles and platforms covered:
- Material gaps:

## Quality profile
| # | Dimension | Rating | Confidence | Strongest evidence | Main gap |

## Weakest links
1. <cause spanning findings/flows>
2. <cause>
3. <cause>

## Prioritized findings
### Now
- [P1] <finding with evidence, effect, correction and verify>
### Next
...
### Later
...

## Flow lifecycle matrix
| Flow | Before | During | After | Failure | Real conditions |

## Keep
- <working behavior to preserve>

## Verification gaps
- <unknown, why and exact next probe>

## Remediation slices
| Slice | Findings | Expected outcome | Effort | Acceptance checks |

## Handoff
<audit complete | implementation authorized | blocked by named evidence>
```

Maintain traceability from every slice to `POL-*`, `FLOW-*`, and `SURF-*` IDs. Avoid giant tables: when detail is extensive, keep the summary in the report and link to versioned evidence.

## 7. Regression After Remediation

1. Update the atlas if a mapped element changed.
2. Run the freshness preflight.
3. Reproduce every `verify` criterion for remediated findings.
4. Rerun the affected primary dimensions and cross-references.
5. Make a smoke pass with all twelve evaluators over the modified flow.
6. Mark each finding `resolved`, `partially-resolved`, `not-reproduced`, or `open` with new evidence.
7. Do not raise a dimension's rating based on a code change that was not behaviorally verified when runtime verification is available.
