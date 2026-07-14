# Interaction Craft Reference

Use this reference to turn “make it juicy” into observable, restrained interaction quality. Apply patterns selectively according to frequency, consequence, platform, and product voice.

## Contents

1. Quality model
2. Feedback layers
3. Temporal budget
4. Async interaction patterns
5. Spatial continuity patterns
6. Control and manipulation patterns
7. Delight budget
8. Common failures and replacements
9. Source basis

## 1. Quality Model

A polished interaction has six properties:

1. **Immediate**: input receives acknowledgement in the next visual update.
2. **Causal**: the response is attached to the control or object that caused it.
3. **Continuous**: the user can track identity, position, focus, and context across change.
4. **Truthful**: pending and completed states reflect what the system actually guarantees.
5. **Interruptible**: rapid repeat, reversal, escape, navigation, or cancellation does not leave stale animation or state.
6. **Proportionate**: frequency and consequence determine intensity; common work stays fast and quiet.

Judge the whole response ladder, not animation in isolation:

`intent -> acknowledgement -> progress -> outcome -> recovery`

## 2. Feedback Layers

Add only the layers that improve recognition, orientation, confidence, or control.

| Layer | Purpose | Examples |
|---|---|---|
| State | Make the new truth legible | selected mark, checked value, changed label, local status |
| Tactile | Confirm contact and manipulability | pressed surface, focus ring, drag lift, insertion marker |
| Spatial | Explain origin, destination, or reorganization | anchored popover, expanding detail, FLIP-style reorder |
| Progress | Make work and waiting visible | inline pending label, skeleton, determinate progress, cancel |
| Outcome | Close the loop | saved state, row inserted, toast linked to an undo action |
| Emphasis | Direct attention once | brief highlight of changed content, milestone accent |
| Sensory | Reinforce rare important events | optional sound or haptic on suitable native platforms |

State feedback is mandatory when the truth changes. Other layers are conditional. More layers do not automatically mean more quality.

### Intensity by frequency

- **Continuous and repeated work**: near-instant, quiet, productive feedback.
- **Occasional navigation or mode change**: spatial continuity with moderate motion.
- **Rare meaningful milestone**: one expressive accent, only if it fits product voice.
- **Error or risk**: clear state and recovery; avoid playful or theatrical motion.

## 3. Temporal Budget

Use timing as a diagnostic range, not a universal token prescription. Existing product tokens win when coherent.

### Perceived response

- Aim for visual acknowledgement in the next paint and roughly within 100 ms of input.
- Treat field INP at or below 200 ms as the broad “good responsiveness” threshold, not permission to delay a pressed or selected state.
- Under roughly 1 second, keep the user's flow intact with local state change; avoid flashing loaders for work that completes almost immediately.
- Beyond roughly 1 second, expose that work continues near the affected object.
- Beyond roughly 10 seconds, prefer determinate or concrete progress, allow cancellation or backgrounding where feasible, and support reorientation on return.

### Motion ranges

- **80-160 ms**: press, hover, focus-adjacent styling, small toggles, compact feedback.
- **160-240 ms**: menus, tooltips, small disclosure, local insertion or removal.
- **240-360 ms**: drawers, panels, meaningful spatial reorganization.
- **300-500 ms**: rare expressive transitions or milestones, never routine task tax.

Shorten exits relative to entrances when the departing object no longer needs attention. Increase duration modestly with distance and size. Prefer immediate reversal from the current visual state rather than finishing an obsolete animation.

Do not animate solely because a range exists. An instant state change is often the most polished response.

## 4. Async Interaction Patterns

### Safe optimistic mutation

Use optimism when all are true:

- Success is common.
- The local result is unambiguous.
- Failure can be rolled back or reconciled safely.
- Duplicate input can be prevented or made idempotent.
- The user receives local pending and failure feedback.

Pattern:

1. Acknowledge input immediately.
2. Apply or stage the local result.
3. Mark it pending without blocking unrelated work.
4. Reconcile the server result.
5. On failure, restore or clearly mark the affected object and offer retry or undo.

Do not use optimistic completion for destructive, financial, permission-changing, legal, or externally visible actions unless the system has explicit transactional or compensating guarantees.

### Confirmed mutation

Keep the action local and responsive while awaiting confirmation:

- Press state appears immediately.
- Button or object shows a stable pending state without resizing.
- Duplicate submission is prevented without making the whole screen inert.
- Success appears at the changed object; a global toast is supplemental.
- Failure preserves user input and exposes recovery near its source.

### Loading without flicker

- Preserve stable geometry.
- Keep prior content visible when it remains valid; mark refresh rather than blanking it.
- Use a short loader delay for very fast operations only when it prevents flash without hiding real waiting.
- Use skeletons only when they represent predictable content structure. Do not pulse the entire page indefinitely.
- Announce meaningful async status to assistive technology without flooding live regions.

### Undo

Prefer undo over confirmation for frequent, reversible, low-consequence actions. Keep the affected result visible long enough to understand what changed. Do not make the undo window the sole recovery path for consequential loss.

## 5. Spatial Continuity Patterns

### Disclosure and overlays

- Anchor menus and popovers to their trigger.
- Move focus into modal interaction and restore it to the invoking control on close.
- Preserve the underlying scroll position.
- Use opacity or short transform only to explain appearance; never animate focus itself.
- Close promptly on Escape and reversal.

### Navigation and detail

- Preserve a selected row, tab, or source marker when opening detail.
- Keep shared identity visible through title, thumbnail, label, or position.
- Restore list position and selection when returning.
- Use route transitions only when they clarify hierarchy; do not make every page cross-fade.

### Insert, remove, and reorder

- Show where a new item arrived.
- Keep neighboring content traceable during reflow.
- For removal, confirm which object left before collapsing space, unless immediate disappearance is clearer.
- For sorting and filtering, preserve headers, controls, focus, and a stable anchor.
- Prefer transform-based reordering over animating layout properties when practical.

### Drag and drop

Provide pickup, valid-target, insertion, drop, and cancellation feedback. Keep a keyboard or command alternative for important operations. Do not let ornamental spring physics obscure the exact drop target.

## 6. Control And Manipulation Patterns

### Buttons and icon controls

- Distinguish rest, hover where available, focus-visible, pressed, disabled, pending, and success or failure when the action owns that result.
- Keep label and geometry stable while pending; replace content only when the accessible name remains clear.
- A pressed state may use color, border, shadow, or 1-2 px displacement. Do not scale every button by reflex.

### Selection controls

Update the selection mark immediately. If persistence is async, separate selected from saving rather than delaying the selection itself.

### Forms

- Acknowledge submit immediately and keep entered data.
- Place validation feedback by the field and focus or summarize appropriately.
- Avoid shaking fields; use clear text, outline, and focus placement.
- Show autosave state quietly and distinguish saving, saved, offline, conflict, and failed.

### Keyboard

Keyboard activation must receive the same state and outcome feedback as pointer input. Keep visible focus through DOM updates, overlays, sorting, insertion, and deletion. Shortcuts need discoverability and must not conflict with typing or platform conventions.

## 7. Delight Budget

Earn delight after correctness, speed, and recovery.

Use an expressive moment only when it:

- Marks a real achievement, completion, or identity-bearing transition.
- Happens rarely enough to remain meaningful.
- Does not delay the next action.
- Has a quiet reduced-motion equivalent.
- Fits the domain; healthcare, finance, security, and incident response demand extra restraint.

Prefer product-specific feedback over generic confetti. A precise changed-value highlight, completed sequence, satisfying snap, or concise milestone mark often feels more mature than spectacle.

## 8. Common Failures And Replacements

| Failure | Replace with |
|---|---|
| Dead click until server response | Immediate pressed/pending state attached to the action |
| Toast as the only completion signal | Changed local state plus optional toast for cross-page persistence |
| Spinner replaces the whole screen | Stable shell and contextual progress near affected content |
| Every item staggers on render | Animate only a causal insertion or meaningful first-use reveal |
| Universal `transition: all` | Explicit properties with purpose and bounded duration |
| Spring or bounce on routine controls | Productive easing and direct state change |
| Error shake | Clear message, visible focus, preserved input, recovery action |
| Disabled control with no explanation | Prevent invalid state earlier or explain the unmet requirement nearby |
| Optimistic deletion with silent failure | Pending removal, safe rollback, and explicit recovery |
| Reduced motion removes feedback | Replace displacement with immediate state, opacity, outline, or status |
| Long success animation blocks work | Immediate completion state; optional non-blocking accent |

## 9. Source Basis

This reference synthesizes durable guidance from:

- web.dev, **Interaction to Next Paint (INP)**: next-paint feedback and the 200 ms good-responsiveness threshold.
- Nielsen Norman Group, **Response Times: The 3 Important Limits**: direct-manipulation, flow, and attention thresholds around 0.1, 1, and 10 seconds.
- IBM Carbon, **Motion**: productive versus expressive motion, purposeful choreography, and restrained easing.
- W3C WCAG 2.2, **2.3.3 Animation from Interactions**: disable or replace non-essential interaction-triggered motion.
- MDN, **prefers-reduced-motion**: honor system preference and replace vestibular triggers such as large scaling or panning.
- MDN, **CSS and JavaScript animation performance**: use appropriate browser animation primitives and avoid layout-heavy animation when compositor-friendly properties suffice.
- Established interaction-design principles of visibility, feedback, mapping, constraints, error prevention, and recovery.

The operational guidance lives here so agents can apply it without browsing or copying a particular design system's visual style.
