# Motion, Accessibility, And Performance

Use this reference whenever interaction polish adds or evaluates motion, perceived latency, reduced-motion behavior, or animation implementation.

## Contents

1. Motion decision
2. Choreography
3. Easing and duration
4. Reduced motion
5. Input and assistive technology
6. Runtime performance
7. Implementation review

## 1. Motion Decision

Before animating, name the job:

- Confirm an input.
- Explain an object's origin or destination.
- Preserve identity through reorganization.
- Direct attention to a consequential change.
- Communicate progress or mode.
- Reward a rare meaningful milestone.

If no job applies, prefer an instant state change.

Use **productive motion** for routine work: subtle, fast, and out of the way. Use **expressive motion** only for occasional moments that deserve attention. Serious product polish usually comes from consistent productive motion, not more expressive motion.

## 2. Choreography

- Animate the causal object first. Supporting elements may follow only when sequence clarifies hierarchy.
- Keep one dominant motion event at a time.
- Preserve reading and focus order even when visual elements move.
- Avoid long entrance cascades; they delay scanning and become punishing on repeated visits.
- Keep entry, exit, and reversal coherent. A reopened panel should reverse from its current visual state, not jump or wait for stale motion.
- Make motion interruptible. New intent supersedes old choreography.
- Separate animation state from business truth; an `animationend` event must not be the only way important state commits.

## 3. Easing And Duration

- Use standard in-out easing for elements visible throughout reorganization.
- Use deceleration for entrances and acceleration for exits when it supports physical intuition.
- Avoid linear easing for spatial UI movement; reserve it for continuous progress or time-based visualization.
- Avoid bounce, elastic overshoot, and abrupt stops by default.
- Scale duration with distance and viewport coverage, not component category alone.
- Keep motion tokens few and semantic, such as `fast`, `standard`, and `spatial`; do not create a duration for every component.
- Never use `transition: all`; list the intended properties.

## 4. Reduced Motion

Treat `prefers-reduced-motion: reduce` as a different choreography, not a blank stylesheet.

- Remove large translation, zoom, parallax, perspective, spinning, and repeated pulsing.
- Replace spatial travel with immediate state, a short opacity change, outline, color, or text/status update.
- Preserve origin and destination through static placement, labels, focus, selection, and hierarchy.
- Stop non-essential auto-animation and ambient loops.
- Keep essential progress understandable without movement.
- Test the actual workflow with the system or browser preference enabled.
- If a product has its own motion setting, respect the stricter of product and system preference.

Opacity can still be uncomfortable when large regions flash or pulse. Reduced motion means reduced sensory disruption, not merely zero transforms.

## 5. Input And Assistive Technology

- Provide equivalent response for click, tap, Enter, Space, and relevant shortcuts.
- Do not depend on hover for essential feedback; touch has no hover and keyboard uses focus.
- Keep focus-visible distinct from hover and selection.
- Restore focus after dialogs, menus, drawers, and destructive removal.
- Announce meaningful async status and errors through established live-region patterns, but avoid announcing every animation frame or transient decoration.
- Do not let motion reorder the DOM solely to match a visual effect.
- Provide non-drag alternatives for important rearrangement.
- Do not make sound or haptics the only feedback. Use them only on platforms with established conventions and user control.

## 6. Runtime Performance

Interaction polish fails when it increases latency.

- Measure or inspect the full interaction: input delay, handler work, rendering, and next paint.
- Keep event handlers small; defer unrelated work and break up long main-thread tasks.
- Prefer CSS transitions or Web Animations for simple visual interpolation. Use `requestAnimationFrame` for coordinated frame-by-frame work rather than timers.
- Prefer `transform` and `opacity` when they express the design. Do not force compositor tricks when layout genuinely must change.
- Avoid animating width, height, top, left, heavy filters, and large shadows on repeated or large-scale interactions unless profiling shows acceptable cost.
- Use `will-change` sparingly and remove it when no longer useful; excessive layers consume memory.
- Reserve geometry before async content arrives to prevent layout shift.
- Test realistic record counts, slow network, and rapid repeated input.
- Ensure event listeners, observers, and animation objects are cleaned up on unmount or route change.

Field performance is stronger evidence than one fast development machine. When field data exists, use it to identify slow interactions; otherwise reproduce representative high-frequency and worst-case actions in the lab.

## 7. Implementation Review

Check for:

- Broad `transition: all` rules.
- Duplicate hardcoded durations and easings.
- State committed only from animation callbacks.
- Timers used to simulate business completion.
- Animations that queue on repeated input.
- Exit animations that leave invisible focusable DOM.
- Mount/unmount races during route or overlay transitions.
- Loading indicators that appear too late or flash too briefly.
- Optimistic state without rollback.
- Missing `prefers-reduced-motion` behavior.
- Motion tokens that conflict with the existing design system.
- Layout-shifting skeletons or success messages.
- Large animated regions or expensive filters on low-power devices.

Reject any refinement whose visual benefit is smaller than its input-delay, accessibility, maintenance, or correctness cost.
