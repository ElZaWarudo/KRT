# Frontend Verification

Use this reference before final delivery when the task changed visual behavior, routes, layout, interactions, or frontend state.

## Browser Setup

- Start the project dev server when the app requires one.
- If the requested route depends on backend data, use the repo's normal local stack, mocks, fixtures, or seeded data.
- Give the user the URL only after the page is running.
- If the page can be opened as static HTML, no dev server is required.

## Viewports

Check at least:

- Desktop width.
- Mobile/narrow width.
- Any obvious breakpoint affected by the change.

For dense tools, also check a data-heavy state when feasible.

## Visual Checks

- Primary surface appears without blank or broken regions.
- Content is not hidden behind fixed headers, sidebars, drawers, or bottom bars.
- Text fits inside buttons, chips, tabs, cards, table cells, and nav items.
- Long words, long names, localized text, and dynamic values do not break layout.
- Images and media reserve space and render at useful crop/framing.
- Tables, grids, boards, and controls keep stable dimensions.

## Interaction Checks

- Primary action works or reaches the expected next state.
- Secondary actions are discoverable and do not compete with the primary task.
- Loading and saving states are visible.
- Errors are recoverable.
- Overlays can be opened, used, and closed.
- Keyboard focus is visible and logical.

## Theme And Preference Checks

When the repo supports them:

- Check light and dark mode.
- Check reduced motion behavior for new animation.
- Check high-contrast or forced-color patterns if the app already supports them.

## Performance Feel

- Avoid blank initial surfaces when a meaningful shell or skeleton is possible.
- Avoid layout shift during loading.
- Avoid expensive animation or rendering on repeated interaction.
- Keep interaction response immediate under realistic item counts.
- Do not add large assets or dependencies for decorative effect.

## Final Report

In the final answer, state:

- Dev server or static file used, if any.
- Viewports checked.
- Interaction states checked.
- Accessibility checks run manually or automatically.
- Checks not run and why.
