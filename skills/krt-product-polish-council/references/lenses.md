# Polish Lenses

Twelve lenses for walking a flow. Use them as a checklist, not as twelve
reports: a finding gets one primary lens and cross-references the rest. Each
lens names what to inspect and the judgment that keeps it honest.

| # | Lens | Inspect | Don't |
|---|---|---|---|
| 01 | Scope and focus | the promise, entry points, onboarding, action hierarchy, competing primary actions, dead ends, internal architecture leaking into the UI | penalize a small scope or a deliberate constraint |
| 02 | Behavioural consistency | save, close, back, edit, delete, select, confirm across surfaces; terminology; action placement; state kept on return | flag differences justified by risk, platform, or context |
| 03 | Status and feedback | acknowledgement, pending, disabled, duplicate-submit guard, progress, success, failure, sync, optimism and rollback; signal beside the affected object; assistive-tech announcements | rank decorative animation above silence or false state |
| 04 | Non-ideal states | empty (initial and filtered), excess data, slowness, offline, server error, permission, expired session, long text, invalid files, abandoned flows, narrow viewports | demand states that don't apply; mark untestable ones as gaps |
| 05 | User protection | undo, autosave, drafts, contextual validation, safe defaults, kept input, friction proportional to risk; reversible vs destructive vs irreversible | run real destructive, financial, or public actions; train users with routine confirmations |
| 06 | Interface hierarchy | dominant action, grouping, alignment, spacing, type scale, contrast, density, controls that don't look interactive, screens designed in isolation | impose a new visual taste on an identity that works |
| 07 | Content and language | labels, buttons, errors, empty states, confirmations, terminology, synonyms for one concept, database names, generic verbs ("Continue", "Accept") | invent policies, guarantees, or outcomes in proposed copy |
| 08 | Perceived performance | first acknowledgement, prioritized loading, kept prior content, skeletons, local vs global blocking, layout shift, full reloads, flicker | recommend animation to hide slowness |
| 09 | Platform conventions | web: URLs, deep links, reload, back/forward, new tabs, keyboard; mobile: back, touch targets, field keyboards, safe areas, interruptions; desktop: shortcuts, context menus, multiselect, drag and drop, files | evaluate undeclared platforms |
| 10 | Built-in accessibility | contrast, visible focus, order, names, semantics, keyboard-only primary flow, targets, colour alternatives, zoom and reflow, reduced motion, status announcements | stop at automated checks; claim untested assistive tech |
| 11 | Context continuity | scroll, filters, search, sort, selection, tabs, focus, drafts after detail-return, edit-return, back/forward, reload, failure | require sensitive data to persist when clearing it is a declared choice |
| 12 | Completeness and seams | dead buttons, broken links, placeholder text, fake data, mismatched icons, console errors, half-finished features, seams between modules | turn preferences into defects |

Walk each important flow through its lifecycle: before (entry, preconditions),
during (input, pending), after (outcome, where the user lands), failure and
recovery, and real conditions (slow network, long content, interruption,
phone).

Ratings, when a profile helps the reader: **0** broken or absent, **1** fragile
(happy path only), **2** solid with specific gaps, **3** polished across the
examined conditions, **NA** not applicable or not verifiable (not zero). Give
confidence with each. Never average them; name the lowest material one.
