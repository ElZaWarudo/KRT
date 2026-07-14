# Browser Interaction Audit

Use this reference to gather evidence from an executable frontend and verify interaction refinements.

## Contents

1. Prepare
2. Observe
3. Stress
4. Inspect
5. Verify
6. Evidence standard

## 1. Prepare

1. Identify the primary route and user job.
2. Start the normal local frontend and required mocks, fixtures, or backend services.
3. Choose one high-frequency workflow and one consequential or async workflow.
4. Record existing motion tokens, component primitives, supported themes, and product preferences.
5. Use realistic content volume. Include long labels or dense data when they affect transitions.

Do not begin by stepping frame-by-frame. First experience the product as a user at normal speed.

## 2. Observe

For each material action, record:

- Input method.
- Immediate acknowledgement.
- Pending behavior.
- Visible result and completion signal.
- Error and recovery path.
- Focus, selection, scroll, and spatial continuity.
- Duration or latency only when measurement helps explain the experience.

Exercise:

- Primary navigation or mode switch.
- Main call to action.
- Form or data mutation.
- Menu, dialog, popover, drawer, or disclosure.
- Insert, remove, sort, filter, or reorder when present.
- Empty, loading, success, and failure states relevant to the workflow.

## 3. Stress

Repeat the same actions under conditions that expose fragile polish:

- Rapid double activation.
- Open then immediately close or reverse.
- Navigate away during pending work.
- Slow or failed network request.
- Large data set or repeated list operation.
- Narrow viewport and touch-sized controls.
- Keyboard-only operation.
- `prefers-reduced-motion: reduce`.
- Background and return when pending work can outlive the view.

Look for duplicate submissions, stuck disabled state, lost focus, stale toasts, orphaned overlays, queued animations, snapping, layout shift, and false success.

## 4. Inspect

Use browser tooling proportionally to the risk:

- Performance recording for slow clicks, taps, keys, reflow, or frame drops.
- Network throttling or request blocking for async truth and recovery.
- Rendering or layout-shift overlays for unstable geometry.
- Accessibility tree and keyboard pass for focus and announcements.
- Computed styles or animation inspection for duration, easing, and reduced-motion overrides.
- Mobile emulation for touch, viewport, fixed regions, and disclosure behavior.

For responsiveness, distinguish:

1. Input delay before handlers begin.
2. Handler or framework work.
3. Rendering and presentation delay.
4. Network or background work after the first feedback.

The first visual acknowledgement should not wait for step 4.

## 5. Verify

Minimum matrix for a material interaction change:

| Dimension | Minimum check |
|---|---|
| Pointer | Hover where relevant, press, rapid repeat, reversal |
| Keyboard | Focus-visible, activation, Escape or cancel, focus restoration |
| Touch/narrow | Target size, no hover dependency, stable viewport, no clipped motion |
| Motion preference | Full and reduced choreography preserve the same state meaning |
| Async | Fast success plus one slow, failed, stale, or offline path |
| Continuity | Selection, scroll, focus, identity, and return path survive |
| Performance | Immediate next-paint feedback; no obvious long task, shift, or dropped-frame regression |

Also check supported light, dark, and high-contrast modes when the changed feedback uses color, borders, shadows, or opacity.

## 6. Evidence Standard

A finding must connect a concrete observation to a user effect and an acceptance check.

Strong:

> Saving disables the whole editor for 1.8 seconds and provides no local status. Users can mistake the click for a miss or lose comparison context. Keep the editor readable, show `Saving…` beside the changed field in the next paint, disable only conflicting actions, and verify success and failed retry under throttling.

Weak:

> The save interaction needs more juice.

Prefer short recordings or before/after observations for temporal problems. Screenshots alone rarely prove interaction feel. If browser execution is unavailable, label code-derived findings and unverified assumptions explicitly.
