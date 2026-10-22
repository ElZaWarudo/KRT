# Interaction Craft

Patterns for turning "make it feel better" into observable, restrained
interaction quality. Existing product tokens and conventions win when they are
coherent; these ranges are diagnostic, not prescriptions.

## Temporal budget

Perceived response:

- Visual acknowledgement in the next paint, roughly within 100 ms. Field INP at
  or under 200 ms is "good", but that is no licence to delay a pressed state.
- Under about 1 s, keep flow with a local state change; avoid flashing loaders.
- Over about 1 s, show that work continues near the affected object.
- Over about 10 s, show concrete progress, allow cancel or backgrounding, and
  support reorientation on return.

Motion ranges:

| Range | Use |
|---|---|
| 80–160 ms | press, hover, small toggles, compact feedback |
| 160–240 ms | menus, tooltips, small disclosure, local insert or remove |
| 240–360 ms | drawers, panels, meaningful spatial reorganization |
| 300–500 ms | rare expressive moments only, never routine task tax |

Exits are shorter than entrances. Duration grows modestly with distance. New
intent reverses from the current visual state instead of finishing an obsolete
animation. Use deceleration for entrances, acceleration for exits, standard
easing for elements that stay visible, linear only for continuous progress.
Keep motion tokens few and semantic (`fast`, `standard`, `spatial`).

## Feedback layers

State feedback is required whenever the truth changes. Add the others only when
they improve recognition, orientation, confidence, or control.

| Layer | Examples |
|---|---|
| State | selected mark, changed label, local status |
| Tactile | pressed surface, focus ring, drag lift, insertion marker |
| Spatial | anchored popover, expanding detail, FLIP-style reorder |
| Progress | inline pending label, skeleton, determinate progress, cancel |
| Outcome | saved state on the object, inserted row, toast with undo |
| Emphasis | one brief highlight of changed content |

Intensity follows frequency: repeated work stays near-instant and quiet;
occasional navigation gets moderate spatial continuity; rare milestones may get
one expressive accent if it fits the product voice; errors and risk get clear
state and recovery, never playful motion.

## Async patterns

**Safe optimistic mutation** needs all of: common success, unambiguous local
result, safe rollback or reconciliation, duplicate input prevented or
idempotent, local pending and failure feedback. Apply locally, mark pending
without blocking unrelated work, reconcile, and on failure restore or mark the
object and offer retry or undo. Not for destructive, financial, permission,
legal, or externally visible actions without transactional or compensating
guarantees.

**Confirmed mutation:** immediate press state; stable pending state without
resizing; duplicate submission blocked without making the whole screen inert;
success shown at the changed object (a toast is supplemental); failure keeps
input and puts recovery near its source.

**Loading without flicker:** reserve geometry; keep valid prior content visible
and mark it refreshing; delay a loader briefly only to avoid a flash; use
skeletons only for predictable structure; announce meaningful status to
assistive tech without flooding live regions.

**Undo** beats confirmation for frequent, reversible, low-consequence actions.
Keep the changed result visible long enough to understand. Don't make a short
undo window the only recovery for consequential loss.

## Continuity

- Overlays: anchor to the trigger, move focus in, restore it to the invoker on
  close, keep the underlying scroll, close promptly on Escape.
- Navigation: keep the source row or tab marked, keep shared identity visible,
  restore list position and selection on return; use route transitions only
  when they clarify hierarchy.
- Insert, remove, reorder: show where an item arrived; keep neighbours
  traceable; confirm which object left before collapsing space; keep headers,
  controls, focus and an anchor stable while sorting; prefer transforms over
  animating layout.
- Drag and drop: pickup, valid target, insertion, drop, and cancel feedback,
  plus a keyboard or command alternative for important moves.

## Controls

- Buttons distinguish rest, hover, focus-visible, pressed, disabled, pending,
  and their own success or failure. Keep label and geometry stable while
  pending. A press can be colour, border, shadow, or 1–2 px displacement; don't
  scale every button.
- Selection updates instantly; if persistence is async, show "saving"
  separately instead of delaying the mark.
- Forms acknowledge submit at once, keep data, place validation by the field,
  avoid shake, and distinguish saving, saved, offline, conflict, and failed.
- Keyboard activation gets the same feedback as pointer input; focus stays
  visible through DOM updates; shortcuts don't fight typing or the platform.
- Disabled controls explain the unmet requirement nearby, or the invalid state
  is prevented earlier.

## Delight budget

Earn delight after correctness, speed, and recovery. An expressive moment marks
a real achievement, happens rarely, doesn't delay the next action, has a quiet
reduced-motion equivalent, and fits the domain. A precise changed-value
highlight or a clean snap usually feels more mature than spectacle.

## Reduced motion and assistive tech

Under `prefers-reduced-motion: reduce`, remove large translation, zoom,
parallax, spinning, and pulsing; replace travel with instant state, short
opacity, outline, colour, or text; stop ambient loops; keep essential progress
understandable. Large flashing opacity is still disruptive. Respect the stricter
of the product's own motion setting and the system preference. Never rely on
hover, motion, sound, haptics, or colour as the only signal, and don't reorder
the DOM to match a visual effect.

## Runtime performance

Polish fails when it adds latency. Keep handlers small and break up long
tasks. Prefer CSS transitions or Web Animations; use `requestAnimationFrame`,
not timers, for frame work. Prefer `transform` and `opacity`; avoid animating
width, height, top, left, heavy filters, and large shadows on repeated or large
interactions. Use `will-change` sparingly. Reserve space for async content.
Clean up listeners, observers, and animations on unmount.

Implementation smells: `transition: all`; duplicated hard-coded durations;
state committed from `animationend`; timers simulating completion; animations
queueing on repeated input; exit animations leaving invisible focusable DOM;
loaders that appear too late or flash; optimistic state without rollback;
missing reduced-motion rules; layout-shifting skeletons or success messages.

## Failure → replacement

| Failure | Replace with |
|---|---|
| Dead click until server response | Immediate pressed/pending state on the action |
| Toast as the only completion signal | Changed local state, optional toast |
| Spinner replaces the whole screen | Stable shell, progress near affected content |
| Every item staggers on render | Animate only causal inserts or a first-use reveal |
| Spring or bounce on routine controls | Productive easing, direct state change |
| Error shake | Clear message, visible focus, kept input, recovery |
| Optimistic delete with silent failure | Pending removal, rollback, explicit recovery |
| Reduced motion removes feedback | Instant state, opacity, outline, or status |
| Long success animation blocks work | Immediate completion, optional non-blocking accent |

## Source basis

web.dev INP; Nielsen Norman Group response-time limits (0.1 / 1 / 10 s); IBM
Carbon productive vs expressive motion; WCAG 2.2 SC 2.3.3; MDN
`prefers-reduced-motion` and animation performance guidance.
