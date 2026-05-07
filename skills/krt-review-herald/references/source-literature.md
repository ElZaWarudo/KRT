# Source Literature

Review Herald's workflow is grounded in public code review guidance:

- GitHub pull request reviews (`https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/reviewing-changes-in-pull-requests/about-pull-request-reviews`) support comments, suggestions, approvals, requested changes, and resolved conversation tracking.
- Google Engineering Practices (`https://google.github.io/eng-practices/`) emphasize small, self-contained changes, informative change descriptions, and collaborative handling of reviewer comments.
- The Value of Effective Pull Request Description (`https://arxiv.org/abs/2602.14611`) reinforces that purpose, rationale, and requested feedback help reviewers engage effectively.

## Practical Translation

- Triage feedback before coding so blockers, nits, and discussion points do not blur together.
- Keep responses short and factual; preserve durable rationale in code or PR descriptions when future readers need it.
- Treat review as collaboration toward codebase health, not as a debate to win.
- Ask clarifying questions when the reviewer may be optimizing for a different tradeoff.
- Prefer small, reviewable fixes and re-request review only when the response state is clear.
