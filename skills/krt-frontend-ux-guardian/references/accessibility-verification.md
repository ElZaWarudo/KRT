# Accessibility Verification

Use this reference when building or changing interactive UI. Prefer semantic HTML and existing accessible components before ARIA or custom behavior.

## Structure

- Use landmarks, headings, lists, tables, forms, buttons, and links according to their meaning.
- Keep DOM reading order aligned with visual reading order.
- Do not use a `div` as a button when a native `button` works.
- Links navigate; buttons perform actions.
- Tables need clear headers, captions or surrounding context, and understandable row/column relationships.

## Keyboard And Focus

- Every interactive element must be reachable and usable by keyboard.
- Focus order must follow the workflow.
- Focus must be visible against the actual background.
- Modals and drawers should move focus inside when opened and restore focus when closed.
- Escape should close dismissible overlays unless the local pattern says otherwise.
- Menus, tabs, accordions, comboboxes, and dialogs should follow established component behavior already present in the repo.

## Names And Labels

- Accessible names should match or include visible labels.
- Icon-only buttons need names and tooltips where helpful.
- Inputs need visible labels.
- Error messages must be programmatically associated with the relevant field when the framework supports it.
- Status changes should be announced when they are important and not otherwise visible to assistive tech.

## Color, Contrast, And Meaning

- Do not rely on color alone for state, priority, category, or risk.
- Pair color with text, icon shape, pattern, position, or status label.
- Text, icons, focus rings, disabled states, borders, and charts must remain legible in supported themes.
- Check both light and dark themes when the app supports them.

## Target Size And Motion

- Hit targets should be at least 24x24 CSS px; prefer 44x44 or 48x48 for touch-heavy UI.
- Keep enough spacing between adjacent controls to avoid accidental activation.
- Provide non-drag alternatives for important drag interactions.
- Respect reduced-motion patterns already present in the app.
- Avoid motion that blocks task completion, hides information, or creates layout instability.

## Forms And Errors

- Keep user-entered data after validation errors.
- Put field errors near fields and summarize long-form errors at the top.
- Identify what failed, why it matters, and how to fix it.
- Do not require users to memorize instructions from another part of the screen.

## Minimum Manual Pass

Before delivery, keyboard through the affected surface:

1. Tab to every control.
2. Activate primary and secondary actions.
3. Open and close overlays.
4. Trigger at least one validation or error state where feasible.
5. Confirm focus remains visible and logical.
