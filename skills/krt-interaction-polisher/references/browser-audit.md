# Browser Interaction Audit

Use when an executable frontend is available.

## Observe, then stress

Use the product at normal speed first, with realistic content volume. Cover one
high-frequency workflow and one consequential or async one: primary
navigation, main call to action, a data mutation, an overlay, and any insert,
remove, sort, or filter, plus their empty, loading, success, and failure
states.

Then repeat under conditions that expose fragile polish:

- rapid double activation, and open-then-immediately-close;
- navigating away during pending work, and returning after backgrounding;
- slow or failed requests (throttling or request blocking);
- large data sets or repeated list operations;
- narrow viewport and touch-sized targets;
- keyboard only;
- `prefers-reduced-motion: reduce`.

Watch for duplicate submissions, stuck disabled states, lost focus, stale
toasts, orphaned overlays, queued animations, snapping, layout shift, and false
success.

For slow interactions, split the time into input delay, handler work,
rendering, and network or background work. The first visual acknowledgement
must not wait for the last of these. Use a performance recording, layout-shift
overlay, accessibility tree, and computed animation styles as the risk
warrants.

## Minimum verification matrix for a change

| Dimension | Check |
|---|---|
| Pointer | hover where relevant, press, rapid repeat, reversal |
| Keyboard | focus-visible, activation, Escape or cancel, focus restoration |
| Touch / narrow | target size, no hover dependency, no clipped motion |
| Motion preference | full and reduced versions carry the same state meaning |
| Async | fast success plus one slow, failed, stale, or offline path |
| Continuity | selection, scroll, focus, and identity survive |
| Performance | next-paint feedback; no new long task, shift, or dropped frames |

Check light, dark, and high-contrast modes when feedback relies on colour,
borders, shadows, or opacity. Prefer short recordings or before/after
observations for temporal problems; screenshots rarely prove feel.
