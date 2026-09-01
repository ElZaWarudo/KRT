# Evidence, Rating, and Reporting Protocol

## Contents

1. Evidence labels
2. Dimension ratings
3. Finding severity
4. Evaluator return contract
5. Cognitive-load overlay and referral gate
6. Synthesis rules
7. Final report format
8. Regression after remediation

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
  cognitive_load:
    factors: [<M|S|I|D|U|R>] # use [] when none applies
    profile: <ROLE-* or target user profile>
    rationale: <task-, profile-, and evidence-specific effect, or why none is material>
    claim_basis: <heuristic|observed-behavior|behavioral-measure|self-report|instrumented|mixed>
    profile_sensitivity: <none|possible-reversal|confirmed-reversal|unknown>
    court_referral: <no|candidate>

keep:
- <successful behavior that should survive fixes>

unknowns:
- <missing evidence and exact next probe>

cross_refs:
- <dimension and evidence for another evaluator/lead>
```

Allow `findings: []`. Do not invent debt to fill the contract. Every returned finding must include `cognitive_load`; an empty factor list is valid, an absent block is not.

## 5. Cognitive-Load Overlay and Referral Gate

The overlay makes every Council evaluator inspect cognitive burden without turning the twelve roles into twelve copies of the full Court.

After all independent passes, normalize their outputs into a temporary JSON bundle. Include all evaluator IDs even when their finding list is empty:

```json
{
  "context": {
    "cognitive_load_requested": false,
    "workload_comparison_required": false
  },
  "evaluators": [
    {"evaluator": "01 - Scope and focus", "findings": []},
    {"evaluator": "02 - Behavioral consistency", "findings": []}
  ]
}
```

The abbreviated example shows the shape; the real bundle must contain exactly evaluators `01` through `12` and each finding's complete return-contract fields. Store it in a temporary or repository-approved audit-evidence location, not in the application atlas.

Run:

```bash
rtk python3 <skill-path>/scripts/check_cognitive_overlay.py <bundle.json>
```

The checker validates all twelve evaluator IDs and every overlay, aggregates structured `FLOW x profile x factor` signals, and returns `court_required`, `triggers`, and `signals`. It does not judge whether a factor is semantically correct; the Lead remains responsible for evidence quality.

Validate each finding before accepting it:

1. `factors` exists and contains only `M`, `S`, `I`, `D`, `U`, or `R`; `[]` is allowed.
2. `profile` names a stable `ROLE-*` or a specific target profile; materially different profiles are separate rather than `all users`.
3. `rationale` names the affected task, cites the finding's evidence, or states why no material factor applies.
4. `claim_basis` uses the Court vocabulary and does not overstate the evidence.
5. `profile_sensitivity` records whether novice, expert, ability, frequency, or context could reverse the effect.
6. `court_referral` is a recommendation only; the Lead applies the gate below.

If the checker reports any missing or malformed block, request exactly one contract-only repair from each implicated evaluator and rerun it once. If the bundle remains invalid, reject the implicated findings, record their flow and dimension as coverage gaps, rebuild the bundle with all twelve evaluator IDs, and require a valid checker result before synthesis.

The checker sets `court_required: true` before final Council synthesis when any gate condition is true:

- the user explicitly requested cognitive-load, mental-effort, overload, or workload analysis;
- an accepted P0 or P1 finding has at least one cognitive-load factor;
- two or more independent Council evaluators flag the same `FLOW-* x user profile x factor` tuple;
- any accepted finding reports `possible-reversal` or `confirmed-reversal`;
- the audit must claim or verify that a baseline and candidate differ in cognitive workload.

Pass the Court only the triggering tuples, target profile and context, fresh atlas, and factual evidence packet. Withhold Council titles, severities, corrections, and conclusions until the Court's independent assessor passes finish. The Court returns `CL-*` findings and claim strength; the Council Lead then merges causes and prioritizes the unified backlog.

If the Court is unavailable, complete the Council audit, preserve the overlay tags as heuristic signals, and report the triggered tuples as an explicit verification gap. Do not manufacture Court verdicts inline.

## 6. Synthesis Rules

1. Validate that every finding has evidence, an effect, a correction, verification, and a complete cognitive-load overlay.
2. Apply the Court referral gate before final synthesis.
3. Reject or downgrade claims whose evidence does not support the severity or cognitive claim basis.
4. Assign one primary Council dimension and, when applicable, one primary Court factor per cause; keep the rest as cross-references.
5. Merge findings when they share a cause, flow, and correction criterion. Keep different causes separate even when they appear on the same screen.
6. Detect systemic patterns: one broken convention across three surfaces matters more than three isolated cosmetic tickets.
7. Identify the weakest link by severity, centrality, and rating, not by average.
8. Build a backlog:
   - `Now`: P0/P1 and systemic causes that block trust or recovery;
   - `Next`: frequent or cross-cutting P2 findings;
   - `Later`: P3 findings and bounded refinements.
9. Keep a `Keep` list so remediation does not destroy patterns that already work.
10. Separate confirmed debt, Council heuristic signals, Court findings, and verification gaps.

Council overlay tags never become a numeric score or a Court verdict by aggregation. When the Court runs, preserve its stronger or weaker claim basis even if it disagrees with the Council signal.

## 7. Final Report Format

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

## Cognitive-load overlay
| Flow / profile | M | S | I | D | U | R | Court status |

<State whether entries are Council heuristic signals or Court findings. Record the referral gate result.>

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

## 8. Regression After Remediation

1. Update the atlas if a mapped element changed.
2. Run the freshness preflight.
3. Reproduce every `verify` criterion for remediated findings.
4. Rerun the affected primary dimensions and cross-references; require a fresh cognitive-load block on every finding.
5. Reapply the referral gate and rerun affected Court assessors when it fires or existing `CL-*` findings are in scope.
6. Make a smoke pass with all twelve evaluators over the modified flow.
7. Mark each finding `resolved`, `partially-resolved`, `not-reproduced`, or `open` with new evidence.
8. Do not raise a dimension's rating or cognitive claim basis from a code change that was not behaviorally verified when runtime verification is available.
