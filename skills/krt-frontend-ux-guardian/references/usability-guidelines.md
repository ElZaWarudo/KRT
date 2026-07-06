# Usability Guidelines

Use this reference to make frontend workflows easier to learn, complete, repeat, and recover from. These rules synthesize established usability heuristics into checks an implementation agent can apply without external research.

## System Status

- Every consequential action needs visible feedback: loading, saving, saved, failed, queued, offline, blocked, or complete.
- Feedback should appear near the action or affected object when possible.
- Long operations need progress, estimated state, or a clear waiting affordance.
- Optimistic UI must still expose failure and recovery.
- Do not leave users wondering whether a click, submit, upload, save, or delete worked.

## User Language And Mental Model

- Use domain terms users recognize, not implementation names, API fields, or database labels.
- Order information in the sequence users need it to decide or act.
- Map controls to outcomes: labels should describe what will happen.
- Avoid icons that require interpretation unless the product already uses them consistently.
- Help text should clarify a decision, not explain a confusing layout.

## Control And Recovery

- Provide cancel, back, undo, redo, edit, retry, or save-draft when the workflow can be interrupted or mistaken.
- Risky actions need confirmation proportional to the damage.
- Do not trap users in modals, dead-end empty states, failed submissions, or irreversible flows.
- Preserve entered data through validation errors, navigation mistakes, and retry flows where feasible.
- Let users recover at the point of failure instead of restarting the whole process.

## Consistency And Standards

- Reuse product conventions for navigation, forms, tables, filters, destructive actions, status, and empty states.
- Use platform-standard controls when they solve the job.
- Do not use different words for the same action or state.
- Do not make similar components behave differently unless the workflow clearly demands it.
- Keep keyboard, pointer, and touch interactions aligned.

## Error Prevention

- Remove unnecessary inputs and choices.
- Use constraints, defaults, masks, autocomplete, validation, and confirmation to prevent common errors.
- Check high-cost errors before submit or commit.
- Warn before destructive, expensive, irreversible, or permission-changing actions.
- Prefer prevention over an excellent error message.

## Recognition Over Recall

- Keep field labels, selected filters, current step, previous choices, and required context visible.
- Show available actions instead of requiring users to remember commands.
- Keep examples close to the input they explain.
- For multi-step flows, show where the user is and what remains.
- Do not require users to copy information from one part of the interface to another when the system can carry it forward.

## Efficiency For Repeated Work

- Optimize for both first-time and repeated users.
- Provide bulk actions, saved filters, keyboard shortcuts, recent items, templates, duplication, and sensible defaults when the workflow is repetitive.
- Keep frequent actions closer and rarer actions available but quieter.
- Avoid forced confirmations for low-risk repeated actions.
- Make dense operational screens scannable instead of spacious by default.

## Minimalism For Function

- Remove content, controls, and decoration that do not support the current task.
- Progressive disclosure is useful when advanced options distract from the primary path.
- Do not hide required context behind disclosure.
- Use visual hierarchy to reveal priority, not to decorate.
- Every section should answer: decide, act, inspect, compare, recover, or navigate.

## Error Messages

- Put errors close to their source and provide an error summary for long forms.
- Use redundant indicators: text plus border/icon/position, not color alone.
- Delay validation until it helps; do not flag errors while users are merely exploring a field.
- Use plain language, precise cause, and concrete recovery.
- Avoid blame, jokes, obscure codes, and generic messages like "Something went wrong".
- Preserve user input and reduce correction effort with suggested fixes when possible.

## Forms And Question Flow

- Ask only for information needed to complete the service or workflow.
- Know why every question exists, who needs to answer it, and how it will be verified or used.
- Put eligibility, routing, or branching questions early when they save user time.
- Prefer one decision or question per step for unfamiliar or high-stakes flows.
- Merge steps only when the workflow is internal, repeated, low-risk, or clearly faster in one screen.
- Keep question wording, labels, and page titles consistent so users can build rhythm.

## Trust And Continuity

- Be reliable, consistent, and honest about system state.
- Show what data is being changed, saved, submitted, shared, or deleted.
- Explain privacy, permissions, or irreversible consequences when they affect the decision.
- Reduce the impact of server, validation, upload, and network failure.
- Verify that the workflow still works with realistic data and likely interruptions.
