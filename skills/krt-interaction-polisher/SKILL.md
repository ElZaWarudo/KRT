---
name: krt-interaction-polisher
description: "Audit and refine how a frontend responds over time: input acknowledgement, pending and success states, async truth, optimistic updates, transitions, motion, reduced motion, focus continuity, and perceived performance. Use when an implemented app feels dead, janky, abrupt, sluggish, jarring, or unpolished; when clicks seem ignored or double-submit; when asked to add juice, microinteractions, animation, or confetti; or when making loading, saving, deleting, dialogs, menus, or drag-and-drop feel instant and trustworthy. For visual composition and critique use krt-interface-warden."
---

# Interaction Polisher

Make interactions feel immediate, causal, and trustworthy, the way a mature
product does. Polish here means useful feedback around real state changes, not
decoration. Own the temporal layer: acknowledgement, sequencing, continuity,
perceived latency, state transitions, and motion. Preserve the product's task
model, visual language, accessibility, and data guarantees.

A request to review, assess, or critique authorizes an audit only. Change code
when the user asks for fixes or implementation.

## The response ladder

Judge every consequential interaction as one ladder:

`intent -> acknowledgement -> progress when needed -> outcome -> recovery when needed`

Most "feels dead" or "janky" complaints are a broken rung, not missing
animation. Look for these first, in roughly this order, because they cost trust
and data while easing problems only cost elegance:

- **Acknowledgement** arrives in the next paint, on the control the user
  touched. It never waits for the network or for a decorative transition.
- **Async truth.** Pending, success, failure, retry, and undo states say what
  the system actually guarantees, and say it near the affected object. A toast
  alone is a weak outcome signal; a disappearing one is weaker.
- **Duplicate and rapid input** (double-click, open-then-close, navigate away
  while pending) leaves no duplicate requests, stuck states, or stale overlays.
- **Failure keeps the user's work.** Errors sit by their cause, keep the input,
  and offer the next step.
- **Continuity.** Focus, selection, scroll position, and object identity
  survive dialogs, inserts, removals, and returns.

Then tune choreography and tactility.

## Judgment calls that are easy to get wrong

- **Optimistic UI** fits only when success is likely, the local result is
  unambiguous, and failure can be rolled back visibly. Deleting, paying,
  changing permissions, or publishing should look pending until the server
  confirms, unless there is a real undo or compensating path. Code that already
  removes items before the server answers, with no failure handling, is a
  finding in itself.
- **Reduced motion is a different choreography, not a blank stylesheet.**
  Replace travel, zoom, and bounce with instant state, short opacity, outline,
  or text, and keep every pending, success, and error signal.
- **Serious and high-frequency workflows want productive motion:** short,
  quiet, explicit properties. Bounce, overshoot, scaling every button, long
  entrance cascades, `transition: all`, confetti, and sound are wrong by default
  in finance, healthcare, admin, and other routine work. If the user asks for a
  celebration anyway, keep it rare, brief, non-blocking, and off under reduced
  motion, and say why.
- **Animation never hides latency** or a missing state model. An instant state
  change is often the most polished answer.
- **No new animation dependency** when CSS, the Web Animations API, or the
  repo's existing utilities can do it. Reuse the product's components and
  motion tokens.
- **Business state never commits from an animation callback** or a timer that
  simulates completion.

## Evidence and verification

Inspect the real code and, when an executable surface exists, run the primary
workflow in a browser at normal speed before slowing it down. Stress it:
rapid repeat, reversal, slow and failed requests, keyboard only, narrow
viewport, and `prefers-reduced-motion: reduce`. When no browser is available,
say which findings come from code and which behavior is unverified.

A finding connects a concrete observation to a user effect, an
implementation-ready refinement, and an observable check. "Saving disables the
editor for 1.8 s with no local status; show `Saving…` beside the field in the
next paint and verify success and failed retry under throttling" is useful;
"needs more juice" is not.

Severity: **P0** input appears ignored, state is lost or false, or motion
blocks operation; **P1** unclear causality, pending state, completion, or focus
causes repeated actions or mistakes; **P2** works but feels abrupt, sluggish,
or inconsistent; **P3** a restrained delight opportunity. Don't let P3 work
crowd out P0–P2.

For audits, return the verdict, the observed workflow, prioritized findings,
behaviors to keep, and what you could not verify. In fix mode, add what changed,
which findings were deferred, and how each change was verified (pointer,
keyboard, reduced motion, one slow or failing async path).

## References

- `references/interaction-craft.md`: timing ranges, async and optimistic
  patterns, continuity patterns, controls, delight budget, reduced motion,
  runtime performance, and a failure-to-replacement table. Read it for any
  material audit or implementation.
- `references/browser-audit.md`: the stress list and minimum verification
  matrix for executable frontends.

## Neighbours

Treat the app's functional and accessibility behaviour as fixed. Preserve `krt-interface-warden` composition, tokens, and surface
metaphor, and use its critique as visual context without reopening composition
questions unrelated to interaction feel. All of them are optional; work alone
when they are absent.
