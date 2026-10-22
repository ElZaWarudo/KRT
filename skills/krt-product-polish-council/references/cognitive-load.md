# Cognitive Load

How to locate avoidable mental work in a software task, and how strong a claim
the evidence supports. The six factors are an engineering decomposition, not a
validated psychometric scale: never sum them into a score.

## Unit of analysis

`task x user profile x context`, not the screen. Record before judging:

- task and success signal; necessary complexity the domain requires;
- profile: domain expertise, product familiarity, relevant abilities;
- frequency, time pressure, interruptions, device and input;
- consequence of delay, error, abandonment, or false confidence.

Split materially different profiles instead of writing "all users". Guidance
that helps a novice can become interference for an expert (expertise reversal).
Frequent tasks compound small burdens. Interruptions make hidden context and
ambiguous state costlier. Deliberate friction can be right for irreversible
actions if it focuses attention on the real consequence.

## Six factors

| Factor | Question | Typical evidence | Typical correction |
|---|---|---|---|
| **M** Memory | What must the user hold in mind because the interface doesn't keep it available? | retyping, reopening, notes, forgotten selections, loss after interruption | keep context visible, preserve prior values, recognition over recall, show selections and progress, resume |
| **S** Search | How hard is it to find the next relevant object, fact, or action? | slow first action, wrong openings, repeated scanning | hierarchy, information scent, grouping, ordering, stable placement |
| **I** Integration | What must the user mentally join because it is split across space, time, representation, or terminology? | view switching, transcription, legend lookup, mismatches | put related information together, direct labels, shared units, local explanation |
| **D** Decision | How much avoidable ambiguity must be resolved to choose an action? | hesitation, toggling, wrong one of two similar actions | name the discriminating consequence, safe defaults, semantic grouping |
| **U** Uncertainty | What must the user infer about state, progress, outcome, or next step? | duplicate submits, refreshing, premature exit, false confidence | immediate acknowledgement, honest local status, step position, explicit success and partial success |
| **R** Recovery | How much diagnosis and rework follow an error or interruption? | re-entry, repeated failures, abandonment, support calls | prevent, validate at the useful moment, message by the cause, keep work, undo, safe retry |

Search is about finding a signal; Uncertainty is about interpreting what is
true when the signal is visible. Uncertainty asks whether the user understands
state; Recovery asks whether they can restore progress. Assign one primary
factor per cause: a distant validation message is Integration, an error that
cannot restore input is Recovery, an invisible save outcome is Uncertainty.

## Anti-rules

- "Four chunks" or "7 ± 2" is not a UI item cap. Capacity depends on expertise,
  representation, and task.
- Fewer fields, choices, steps, or words are not automatically easier.
  Thirty well-ordered countries beat six ambiguous categories. Required fields
  stay; reduce the work around them.
- Progressive disclosure can add navigation and integration cost or hide what a
  mental model needs.
- Density is not clutter; a stable dense expert tool can reduce search.
- Don't hide information needed for an accurate model or a consequential
  decision.
- Task time, eye movement, pupil size, error rate, or a workload score alone is
  not cognitive load.

## Claim basis and measurement

Label how each cognitive-load claim was established:

- `heuristic`: predicted from inspecting the interface or code;
- `observed-behavior`: watched real task behaviour, no controlled comparison;
- `behavioral-measure`: defined success, critical errors, time, backtracks,
  retries, help requests;
- `self-report`: a named post-task instrument (SEQ, NASA-TLX, a mental-effort
  item);
- `instrumented`: eye tracking, pupillometry, dual-task, EEG, physiology, with
  proper protocol;
- `mixed`: converging evidence from two or more.

A heuristic pass can report a severe *risk* but not overload, and never a
measured or percentage reduction. Use the lightest method that answers the
decision: inspection to find candidates; observation and task metrics to show
where performance degrades; post-task self-report for perceived workload;
instruments only with the expertise and controls they require.

For a claim that a redesign reduced workload:

1. State a directional hypothesis tied to factors.
2. Hold task, success criteria, data difficulty, device, environment, and
   profile equivalent across baseline and redesign.
3. Counterbalance order or record learning and fatigue effects.
4. Collect completion, critical errors, and recovery before speed.
5. Rate immediately after each task, not at the end of the session.
6. Report sample, missing data, spread, and uncertainty; no invented thresholds.
7. Check whether novice, expert, accessibility, or high-pressure profiles
   respond differently.
8. Get the authority and consent needed to recruit or record people; minimise
   personal data.

Define the acceptance criterion before seeing the redesign's result. Never
invent participants, scores, norms, or statistical confidence.

## Source basis

Hollender et al. 2010 (CLT and HCI); Cowan 2001 (conditional 3–5 chunk
capacity); Rosenholtz et al. 2007 (visual clutter); Blackmon 2012 (information
scent); Kalyuga and Renkl 2010 (expertise reversal); Anik and Bunt 2026
(progressive disclosure counterexample); Darejeh et al. 2026 (review of load
measurement in usability testing); NASA-TLX manual.
