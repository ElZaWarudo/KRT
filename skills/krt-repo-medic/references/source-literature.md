# Source Literature

Repo Medic's model is grounded in current public engineering guidance:

- DORA delivery metrics (`https://dora.dev/guides/dora-metrics/`): use throughput and instability signals to guide continuous improvement, while avoiding metric gaming and one-metric thinking.
- Google Engineering Practices (`https://google.github.io/eng-practices/`): prefer small, self-contained changes; keep related tests with behavior; split large work before review where possible.
- GitHub pull request documentation (`https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/reviewing-changes-in-pull-requests/about-pull-request-reviews`): PR reviews support quality and knowledge sharing through comments, suggestions, approvals, requested changes, and resolved threads.

## Practical Translation

- Measure delivery health as a system, not as individual blame.
- Treat repository health as maintainability plus delivery safety.
- Prefer small, reversible prescriptions over broad cleanup campaigns.
- Preserve context for future maintainers: stale or missing docs are delivery risk, not cosmetic debt.
- Review friction is a symptom; diagnose whether it comes from unclear ownership, large changes, weak tests, or missing rationale.
