# Evidence, Measurement, and Reporting Protocol

## 1. Task Dossier

Create one dossier per materially different task and user profile. Reuse stable application-atlas IDs when available.

```text
case_id: CL-CASE-<sequence>
task: <goal-oriented task>
success_signal: <observable completion>
user_profile:
  role: <ROLE-* or description>
  domain_expertise: <novice|intermediate|expert|mixed|unknown>
  product_familiarity: <new|occasional|frequent|unknown>
context:
  frequency: <frequent|occasional|rare|unknown>
  time_pressure: <none|moderate|high|unknown>
  interruption_risk: <low|medium|high|unknown>
  platform_input: <platform, viewport, keyboard/touch/assistive tech>
  consequence: <delay, error, abandonment, false confidence, harm>
necessary_complexity: <what must remain cognitively demanding and why>
flow: [<FLOW-* or ordered steps>]
information_dependencies: [<what must be found, remembered, or compared>]
decisions: [<choice and required evidence>]
states_and_recovery: [<pending, success, failure, interruption, retry>]
baseline_candidate: <version or variant>
sources_and_gaps: [<declared, observed, code, inferred, unverified>]
```

Do not combine profiles when expertise, abilities, or context plausibly reverse the effect of a design choice.

## 2. Evidence and Claim Basis

Keep the Product Polish Council evidence labels for interoperability:

- `observed`: reproduced at runtime, in a recording, or through equivalent direct evidence;
- `code`: demonstrated by code, configuration, or tests but not reproduced;
- `declared`: authoritative product or user intent;
- `inferred`: a reasoned hypothesis awaiting confirmation;
- `unverified`: an applicable condition without sufficient evidence.

Separately label how the cognitive-load claim was established:

- `heuristic`: model-based prediction from interface evidence;
- `observed-behavior`: direct task behavior without a controlled quantitative comparison;
- `behavioral-measure`: task success, critical errors, time, backtracks, help, retries, or another defined measure;
- `self-report`: a post-task mental-effort item, NASA-TLX, or another named subjective method;
- `instrumented`: eye tracking, pupil response, dual-task, EEG, or physiological measurement interpreted by an appropriate protocol;
- `mixed`: converging evidence from at least two of the above.

Never relabel heuristic evidence as observed or measured. A metric can correlate with workload without proving that a particular interface feature caused it.

## 3. Dimension Verdicts

Return a verdict and confidence for each dimension:

- **controlled**: no material avoidable burden was found in the examined task and profile;
- **friction**: avoidable burden is present, but completion remains reliable;
- **impairing**: evidence shows degraded speed, accuracy, comprehension, confidence, or recovery;
- **overload**: target users cannot complete the task reliably or avoid material harm under an in-scope condition;
- **NA**: not applicable or not verifiable in the available scope.

Use `overload` only with direct behavioral evidence; a heuristic pass may report a severe *risk* but not an overload verdict.

Confidence:

- `high`: converging direct evidence across the material task conditions and target profiles;
- `medium`: direct but partial evidence, or a strong behavioral pattern with limited triangulation;
- `low`: heuristic, code-only, isolated, or substantially incomplete evidence.

Do not calculate a global average. Show the six-verdict profile and identify the weakest material burden by consequence, frequency, and evidence.

## 4. Finding Severity

Use Council-compatible priorities so combined backlogs can be merged:

- **P0 - Serious harm or impossible task:** direct evidence of inability to complete a critical task, prevent serious error, or recover from a high-consequence action.
- **P1 - Reliability or trust failure:** frequent or critical errors, abandonment, false confidence, repeated work, or loss of context in an important task.
- **P2 - Systemic cognitive friction:** material memory, search, integration, decision, uncertainty, or recovery cost that slows or degrades work without making it unreliable.
- **P3 - Local refinement:** bounded burden with limited task impact.

Inference alone cannot support P0 or P1. Within a priority, sort by task centrality, frequency, affected profiles, consequence, and reversibility. Estimate effort only after defining a correction.

## 5. Assessor Return Contract

Return structured YAML or Markdown with these fields:

```text
assessor: <NN - name>
dimension: <memory|search|integration|decision|uncertainty|recovery>
verdict: <controlled|friction|impairing|overload|NA>
confidence: <high|medium|low>
claim_basis: <heuristic|observed-behavior|behavioral-measure|self-report|instrumented|mixed>
coverage:
  cases: [CL-CASE-...]
  flows: [FLOW-...]
  surfaces: [SURF-...]
  conditions: [<profile and context>]
  gaps: [<unverified item>]

findings:
- id: CL-<M|S|I|D|U|R>-<sequence>
  severity: <P0|P1|P2|P3>
  title: <specific interface-imposed burden>
  evidence_type: <observed|code|declared|inferred|unverified>
  claim_basis: <canonical basis>
  evidence: <exact behavior, location, condition, source, and metric if any>
  necessary_complexity: <necessary|partly-avoidable|avoidable|unknown with reason>
  user_effect: <effect on completion, accuracy, time, comprehension, confidence, or recovery>
  correction: <smallest concrete product, code, or content change>
  verify: <observable acceptance check and comparison when required>
  affected: [CL-CASE-..., FLOW-..., SURF-..., ROLE-..., platform]
  frequency: <frequent|occasional|rare|unknown>
  effort: <S|M|L|unknown>

keep:
- <working behavior or useful complexity to preserve>

unknowns:
- <missing evidence and exact next probe>

cross_refs:
- <other Court or Council dimension and brief evidence>
```

Allow `findings: []`. Stable IDs survive regression runs.

## 6. Measurement Ladder

Choose the least costly level that can support the intended decision.

### Level 0 - Heuristic Case

Use direct flow inspection, code, and the six-factor model to predict avoidable burden. This is suitable for finding hypotheses and remediation candidates. Report `claim_basis: heuristic`; do not claim that cognitive load was measured or reduced.

### Level 1 - Behavioral Evaluation

Observe representative users performing the defined task with realistic data. Predefine success, critical errors, recoverable errors, backtracks, retries, help requests, and time boundaries. Think-aloud can explain behavior but can also change workload; disclose its use.

Use a single participant or formative session to find concrete problems, not to estimate a population effect.

### Level 2 - Subjective Workload

Collect a named post-task measure immediately after each condition. NASA-TLX measures broad workload through mental, physical, and temporal demand, perceived performance, effort, and frustration; it does not map one-to-one to the Court's six UI factors. Follow its manual and report whether weighting or a raw variant was used.

A short mental-effort item may be proportionate for rapid formative comparison, but preserve its scale, wording, timing, and limitations.

### Level 3 - Controlled or Instrumented Evaluation

Use eye tracking, pupillometry, dual-task methods, EEG, or other physiological signals only with appropriate expertise, calibration, and control of confounds. Fixations can support a search diagnosis; pupil response can change with lighting or arousal; task time can reflect care or strategy. Triangulate rather than treating any one signal as load itself.

### Comparison Controls

For baseline-versus-candidate claims:

1. State a directional hypothesis tied to one or more Court factors.
2. Hold task goal, success criteria, data difficulty, device, environment, and user profile equivalent.
3. Counterbalance order or record learning and fatigue effects when the same people use both variants.
4. Collect completion, critical errors, and recovery outcomes before optimizing for speed.
5. Collect subjective ratings after each task, not as a vague end-of-session impression.
6. Report sample, missing data, spread, and uncertainty; do not invent universal pass thresholds.
7. Inspect whether novice, expert, accessibility, or high-pressure profiles respond differently.
8. Minimize captured personal data and obtain the authority and consent required for recording or research participation.

Pre-register the decision rule when a formal experiment will decide release or adoption. For ordinary formative work, define the acceptance criterion before seeing the candidate result.

## 7. Synthesis Rules

1. Reject any finding without evidence, effect, correction, and verification.
2. Downgrade severity or claim basis when the evidence is weaker than the wording.
3. Assign one primary factor per root cause and retain secondary effects as cross-references.
4. Merge causes, not similar phrases or co-located symptoms.
5. Separate necessary complexity from avoidable burden in every accepted finding.
6. Preserve successful context, guidance, and protective friction in a `Keep` list.
7. Build `Now`, `Next`, and `Later` slices from priority and systemic leverage, not cosmetic ease.
8. Separate confirmed burden, predicted risk, and measurement gaps.

## 8. Final Report Format

```text
# Cognitive Load Court Report

## Verdict
<task, target profile, weakest material burden, consequence, and evidence strength>

## Docket and evidence
- Case/task/profile/context:
- Baseline/candidate and environment:
- Atlas or task dossier:
- Evidence and measurement levels:
- Material gaps:

## Burden profile
| Factor | Verdict | Confidence | Claim basis | Strongest evidence | Main gap |

## Root causes
1. <cause spanning factors, surfaces, or steps>

## Prioritized findings
### Now
- [P1] <finding with evidence, effect, correction, and verification>
### Next
...
### Later
...

## Keep
- <useful behavior, information, guidance, or friction to preserve>

## Measurement status
<predicted only | observed | measured comparison, method and limitations>

## Verification gaps
- <unknown and exact next probe>

## Remediation slices
| Slice | CL findings | Expected outcome | Effort | Acceptance checks |

## Council cross-references
- <POL dimension or finding, when applicable>

## Handoff
<audit complete | measurement proposed | implementation authorized | blocked by named evidence>
```

Maintain traceability among `CL-*`, `FLOW-*`, `SURF-*`, and any `POL-*` IDs. Keep detailed raw observations outside the summary when they would overwhelm the decision.

## 9. Regression After Remediation

1. Update the shared atlas when mapped product behavior changed.
2. Reproduce each remediated finding's acceptance check under the original profile and condition.
3. Re-run the primary assessor and all explicit cross-references.
4. Smoke-test all six factors on the modified task.
5. Repeat the original measurement method for comparative claims; do not upgrade a measured baseline with a heuristic candidate result.
6. Mark each finding `resolved`, `partially-resolved`, `not-reproduced`, or `open` with new evidence.
7. Record regressions for other user profiles and any useful complexity lost by the correction.
