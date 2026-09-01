# Cognitive Load Model for Interface Work

## Purpose and Boundary

Use this model to locate avoidable mental work in a software task. It is an operational synthesis of cognitive load theory, human factors, HCI, visual perception, information foraging, and multimedia learning. It is not a diagnostic instrument and its six factors are not psychometric subscales.

For a defined task and user profile, use this approximation:

```text
perceived task burden ~= necessary task complexity
                      + memory
                      + search
                      + integration
                      + decision
                      + uncertainty
                      + recovery
```

The Court judges the interface-imposed and avoidable portion. Necessary comparison, reflection, verification, or learning may deserve effort. A correction is successful only when it reduces waste without reducing comprehension, control, or decision quality.

## Six Factors

### M - Memory

**Question:** What must the user keep active in working memory because the interface does not keep it available?

Inspect identifiers, prior values, instructions, selected objects, cross-screen dependencies, multi-step forms, return paths, interruptions, duplicate entry, and comparison tasks.

Evidence cues include omission or substitution errors, repeated reopening, note taking that compensates for the interface, forgotten selections, loss after interruption, and requests to repeat instructions.

Typical corrections externalize relevant context, preserve prior values, favor recognition over recall, show progress and selections, support resume, and group related information into meaningful chunks.

Do not turn working-memory research into a rule that a screen may contain only four items. Chunk capacity depends on expertise, rehearsal, representation, and task conditions.

### S - Search

**Question:** How much effort is required to locate the next relevant object, fact, or action?

Inspect visual clutter, competing emphasis, scanning distance, weak grouping, ambiguous navigation, poor information scent, inconsistent locations, long unstructured sets, and target visibility at realistic scale.

Evidence cues include long time to first relevant action, wrong openings, repeated scanning, excessive cursor or focus travel, fixation patterns when valid eye tracking exists, and verbalized uncertainty about where to look.

Typical corrections strengthen hierarchy, semantic labels, grouping, ordering, filtering, target contrast, and consistent placement. Remove or defer elements only when they are irrelevant to the current decision.

Do not equate density with clutter. A dense expert tool can reduce search when its structure, landmarks, and positions are stable.

### I - Integration

**Question:** What related information must the user mentally join because the interface separates it in space, time, representation, or terminology?

Inspect detached errors, distant legends, cross-tab comparisons, references that require identifier matching, before/after states on separate views, values without units, and asynchronous evidence that must be reconciled manually.

Evidence cues include repeated view switching, transcription, cross-referencing, legend lookup, mismatched items, and errors that occur when two sources must be coordinated.

Typical corrections use spatial or temporal contiguity, direct labeling, aligned comparison, shared units, local explanation, persistent summaries, and side-by-side evidence.

Do not merge independent sources merely because they are related. Integration helps when the sources must be understood together; it can create redundancy when either source is already sufficient.

### D - Decision

**Question:** How much avoidable uncertainty must the user resolve to select an action or option?

Inspect competing primary actions, indistinguishable alternatives, hidden tradeoffs, ambiguous defaults, unclear consequences, option ordering, category quality, and whether the user can compare on decision-relevant attributes.

Evidence cues include hesitation, option toggling, repeated comparison, default abandonment, inconsistent choices, help requests, and errors between semantically similar actions.

Typical corrections clarify discriminating attributes and consequences, provide safe and explainable defaults, recommend when the product has grounds to do so, group alternatives semantically, and expose comparison tools.

Do not apply a mechanical choice limit. Thirty well-ordered countries can be easier than six ambiguous categories. Reduce uncertainty, not merely option count.

### U - Uncertainty

**Question:** What must the user infer about system state, causality, progress, outcome, or the next step?

Inspect pending and saved states, disabled controls, asynchronous work, destructive consequences, partial success, synchronization, stale data, navigation outcomes, permission boundaries, and system language.

Evidence cues include duplicate submission, repeated refresh, defensive reopening, status questions, premature exit, waiting without knowing whether work continues, and false confidence in incomplete results.

Typical corrections provide immediate acknowledgment, local and honest status, progress when meaningful, explicit success and partial-success signals, previews, consequence language, and a clear next action.

Keep this distinct from Search: Search concerns locating a signal; Uncertainty concerns interpreting what is true even when the signal is visible.

### R - Recovery

**Question:** How much reasoning and reconstruction are required to avoid, diagnose, and recover from an error?

Inspect validation, constraints, undo, drafts, preserved input, error placement, diagnosis, retry, conflict handling, irreversible actions, alternate paths, and return after failure.

Evidence cues include repeated failed attempts, data re-entry, abandonment, support dependence, recovery time, accidental destructive action, and inability to tell what was preserved.

Typical corrections prevent invalid actions, validate at the useful moment, place actionable messages beside causes, preserve work, support undo or safe retry, and explain what happened, what remains, and what to do next.

Keep this distinct from Uncertainty: Uncertainty asks whether the user understands state; Recovery asks whether the user can restore progress after something goes wrong.

## Cross-Cutting Modifiers

Record these before judging any factor:

- **Expertise:** guidance that helps a novice can become redundant interference for an expert. Evaluate materially different profiles separately.
- **Frequency:** repeated tasks make small burdens compound and make stable spatial memory or shortcuts more valuable.
- **Time pressure and interruption:** hidden context and ambiguous state become more costly when attention is divided.
- **Consequence:** deliberate friction can be justified for irreversible or high-stakes action, but it must support accurate review rather than ritual confirmation.
- **Accessibility and fatigue:** motor, sensory, language, attention, and fatigue conditions can change the burden. The Court records these effects but does not replace an accessibility audit.
- **Learning goal:** deeper explanations can increase effort while improving understanding. Judge the intended outcome, not effort alone.

## Anti-Rules

- Four chunks is a research-informed warning about constrained working memory, not a UI item cap.
- Fewer choices are not automatically easier; semantic structure and uncertainty matter more than raw count.
- Progressive disclosure is not a universal workload reducer. It can add navigation and integration cost or hide information needed for a mental model.
- Removing redundancy helps only when the removed source is genuinely unnecessary for the target user and task.
- A heuristic tally predicts risk; it does not measure cognition.
- A single physiological or interaction metric does not establish cause.

## Compact Source Basis

The operational guidance above synthesizes these sources; runtime use should rely on this reference rather than re-browsing them:

- Hollender, Hofmann, Deneke, and Schmitz (2010), [Integrating cognitive load theory and concepts of human-computer interaction](https://doi.org/10.1016/j.chb.2010.05.031): connects CLT and HCI and distinguishes useful from software-imposed load.
- Cowan (2001), [The magical number 4 in short-term memory](https://doi.org/10.1017/S0140525X01003922): supports a conditional three-to-five chunk capacity estimate and explicitly describes its boundary conditions.
- Kahn, Tan, and Beaton (1990), [Reduction of Cognitive Workload through Information Chunking](https://doi.org/10.1177/154193129003401919): finds spatial grouping can aid chunk formation and reduce subjective workload, with task-dependent error effects.
- Rosenholtz, Li, and Nakano (2007), [Measuring visual clutter](https://doi.org/10.1167/7.2.17): relates excess or disorganized visual information to search and recognition difficulty and evaluates image-based clutter measures.
- Blackmon (2012), [Information scent determines attention allocation and link selection](https://doi.org/10.1080/0144929X.2011.599041): shows that semantic similarity between a goal and available labels strongly shapes navigation attention and success.
- Kalyuga and Renkl (2010), [Expertise reversal effect and its instructional implications](https://doi.org/10.1007/s11251-009-9102-0): shows that support beneficial to novices can become redundant or harmful as expertise increases.
- Anik and Bunt (2026), [Designing Effective Training Dataset Explanations](https://doi.org/10.1145/3742413.3789087): provides a bounded counterexample in which progressive disclosure did not significantly reduce reported cognitive load, while complete information supported perceived learning and preference.
- Darejeh, Marcus, Mohammadi, and Sweller (2026), [Cognitive Load Measurement Methods for Usability Testing](https://doi.org/10.1177/00187208261427867): reviews 87 interface studies and distinguishes subjective, behavioral, eye-tracking, dual-task, EEG, and physiological approaches.
- NASA, [Task Load Index](https://www.nasa.gov/human-systems-integration-division/nasa-task-load-index-tlx/): authoritative instructions and materials for the six-subscale subjective workload instrument.
