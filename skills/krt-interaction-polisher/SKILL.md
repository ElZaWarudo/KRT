---
name: krt-interaction-polisher
description: Audit and refine the temporal, tactile, and perceived-performance quality of frontend interactions. Use when an implemented app feels dead, abrupt, sluggish, fragile, or insufficiently polished; when reviewing buttons, forms, menus, overlays, navigation, drag-and-drop, asynchronous mutations, loading and success states, animation, microinteractions, keyboard feedback, or reduced-motion behavior; or when a serious product needs implementation-ready interaction critique or focused fixes without a visual redesign.
---

# krt-interaction-polisher

Give frontend interactions the immediacy, continuity, and restraint of a mature product. Treat “juice” as useful feedback layered around state change, not as decorative animation.

Own interaction feel: acknowledgement, temporal sequencing, spatial continuity, perceived latency, state transitions, and motion behavior. Preserve the product's task model, visual language, accessibility, and data guarantees.

## Choose The Mode

- **Audit**: inspect the rendered interface and return an evidence-based interaction brief. Do not change code.
- **Audit and fix**: complete the brief, implement the highest-value refinements, and verify them in the browser.
- **Build guidance**: define the interaction contract and patterns for a feature that is not implemented yet.

Infer the mode from the request. A request to review, assess, or critique does not authorize implementation.

## Operating Workflow

1. Inspect the existing product before judging it: framework, components, tokens, motion utilities, state management, async behavior, accessibility conventions, supported inputs, and nearby interactions.
2. Run the actual primary workflow in a browser when an executable surface is available. Observe the interface at normal speed before slowing recordings or inspecting code.
3. Write a compact interaction contract for each material moment: user intent, immediate acknowledgement, pending state, completion signal, failure and recovery, continuity or focus requirement, and reduced-motion equivalent.
4. Inventory high-value moments: frequent actions, primary navigation, stateful controls, async mutations, object creation/removal/reordering, overlays, drag/drop, empty-to-populated transitions, and meaningful milestones.
5. Audit in this order:
   - **Response**: does click, tap, or key input receive visible acknowledgement in the next paint?
   - **Causality**: is it obvious what changed because of the action?
   - **Continuity**: do focus, position, identity, and surrounding context survive the transition?
   - **Async truth**: are pending, success, failure, retry, undo, and stale or offline states honest and local?
   - **Choreography**: is motion brief, coherent, interruptible, and proportional to distance and importance?
   - **Tactility**: do controls and manipulable objects communicate hover, focus, press, selection, pickup, drop, and disabled state without noise?
   - **Resilience**: does the interaction remain understandable with keyboard, touch, reduced motion, slow network, repeated input, and rapid reversal?
   - **Cost**: does the refinement avoid input delay, layout instability, frame drops, animation debt, and unnecessary dependencies?
6. Prioritize frequent and consequential interactions before rare delight. Fix missing feedback and broken continuity before tuning easing or adding flourish.
7. In fix mode, reuse the product's components and tokens. Centralize repeated durations and easings only when the repo already has or clearly needs a motion vocabulary. Do not add an animation library for effects CSS or existing primitives can express safely.
8. Verify the changed workflow in a browser at desktop and narrow widths, with keyboard and reduced motion. Exercise at least one pending or failure path for async changes when feasible.
9. Report evidence, changes, and checks. Name any state, preference, device behavior, or performance measurement that could not be verified.

## Response Ladder

Model every consequential interaction as:

`intent -> acknowledgement -> progress when needed -> outcome -> recovery when needed`

The first acknowledgement must not wait for the server or for a decorative transition. It may be a pressed state, selection mark, local status, stable placeholder, optimistic state, or immediate opening motion. Choose optimism only when success is likely, rollback is safe, and the user can understand or reverse failure.

Read `references/interaction-craft.md` for every material audit or implementation. It contains feedback layers, timing guidance, async patterns, continuity patterns, and anti-patterns.

Read `references/motion-accessibility-performance.md` whenever motion, latency, animation code, reduced-motion behavior, or performance feel is in scope.

Read `references/browser-audit.md` before delivering an audit or interaction change against an executable frontend.

## Severity Model

- **P0 — interaction blocker**: input appears ignored, state is lost or false, recovery is unavailable, or motion prevents operation.
- **P1 — trust or orientation failure**: causality, pending state, completion, focus, or spatial continuity is unclear enough to create repeated actions or mistakes.
- **P2 — quality gap**: the workflow works but feels abrupt, sluggish, inconsistent, or insufficiently tactile.
- **P3 — restrained delight opportunity**: a low-risk refinement could reward a meaningful moment without slowing repeated work.

Do not let P3 work distract from P0-P2 findings.

## Output Contract

For audit work, return:

```text
Verdict: <one sentence about interaction feel>
Primary workflow: <observed path>
Evidence: <browser/code/state evidence and constraints>

Interaction contract:
- <moment>: <intent -> acknowledgement -> progress -> outcome -> recovery>

Findings:
- [P1] <title>
  Evidence: <specific observed behavior>
  User effect: <trust, speed, orientation, or control impact>
  Refinement: <implementation-ready change>
  Verify: <observable acceptance check>

Keep:
- <successful behavior that should not be disturbed>

Verification matrix:
- <mouse/touch/keyboard/reduced motion/network/state checks>

Handoff: <audit complete|implementation ready|blocked by named evidence>
```

In fix mode, append the files or components changed, patterns reused, findings accepted or deferred, and verification evidence.

## Collaboration Boundaries

Operate independently. When companion artifacts exist:

- Treat `krt-frontend-ux-guardian` functional and accessibility constraints as immutable.
- Preserve `krt-interface-warden` composition, tokens, and surface metaphor unless interaction evidence requires a change.
- Use `krt-interface-inquisitor` findings as visual context; do not reopen composition questions that are unrelated to interaction feel.
- Hand back a temporal interaction brief that any frontend implementation workflow can consume.

The roles remain distinct: Guardian owns task completion, Inquisitor owns visual diagnosis, Warden owns visual composition, and Polisher owns how the interface responds over time.

## Non-Negotiables

- Do not use animation to disguise latency, unclear information architecture, or a missing state model.
- Do not delay input acknowledgement until an animation or network request completes.
- Do not animate every state change, every item on first render, or every hoverable element.
- Do not use bounce, overshoot, confetti, sound, haptics, or large-scale motion by default in serious or high-frequency workflows.
- Do not make destructive, financial, permission, or externally visible actions appear complete before the system can guarantee or safely reverse them.
- Do not remove state information under reduced motion; replace spatial motion with immediate state, opacity, color, outline, or concise status feedback.
- Do not rely on hover, motion, sound, haptics, or color as the only signal.
- Do not break focus order, screen-reader announcements, touch targets, scroll position, selection, or back-navigation expectations for polish.
- Do not ship motion that causes layout shift, blocks the main thread, queues behind repeated input, or becomes incorrect when interrupted or reversed.
- Do not introduce a new dependency without a repo-specific need that native CSS, Web Animations, or existing utilities cannot meet.
