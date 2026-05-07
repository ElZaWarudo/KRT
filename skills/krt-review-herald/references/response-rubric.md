# Review Response Rubric

Use this rubric to classify and answer PR feedback.

## Thread Status

| Status | Meaning | Default action |
|---|---|---|
| Blocking fix | Must change before merge | Fix or ask user if scope changes |
| Valid improvement | Improves quality without changing scope materially | Fix when reasonable |
| Clarification needed | Reviewer intent or tradeoff is unclear | Ask a focused question |
| Discuss/decline | Current approach may be right despite concern | Explain tradeoffs respectfully |
| Nit/advisory | Optional polish | Batch only if cheap |
| Already addressed | Later code/comment resolves it | Draft concise pointer |

## Reply Principles

- Answer the technical concern, not the tone.
- Prefer "Fixed by..." over "Done" when a change was made.
- Mention verification only when it helps re-review.
- Ask for clarification when the requested tradeoff is unclear.
- Keep durable rationale in code, docs, commit messages, or PR description when future readers need it.

## Fix Principles

- If code is confusing, clarify code before writing a long review reply.
- If a reviewer found a missing test, add the narrowest meaningful test unless the test would be brittle or impossible locally.
- If feedback is out of scope, say why and offer a follow-up only when it has real value.
- If multiple comments point to one root problem, fix the root and reply to each thread with the same concise rationale.

## Escalation

Ask the user before:

- changing public API or persistence semantics;
- broadening product scope;
- accepting migration/data risk;
- adding dependencies;
- rejecting a reviewer-requested blocker;
- pushing, requesting re-review, or resolving remote threads.
