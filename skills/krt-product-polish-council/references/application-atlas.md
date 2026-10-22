# Application Atlas

A versioned, factual map of what the application intends and exposes, kept at
`docs/product/application-atlas.md` unless the repo already has an equivalent.
It pays off for repeated audits and regression rounds on a product that keeps
changing; a one-off audit of a small app doesn't need one.

The atlas holds facts only: no severities, "bad" labels, or recommendations.
Record gaps between intent and observation neutrally; the audit decides later
whether they are findings. Never copy secrets or personal data into it.

## Freshness

The frontmatter carries:

```yaml
atlas_schema_version: 1
status: "draft"            # "validated" after the coverage check, "stale" when behind
verified_source_commit: "<full-sha>"
application_fingerprint: "sha256:<digest>"
tracked_paths: ["app", "src", "config"]
excluded_paths: ["docs/product/application-atlas.md", "docs/audits/"]
last_verified_at: "YYYY-MM-DD"
```

Check it before relying on it:

```bash
python3 <skill-dir>/scripts/check_atlas_freshness.py --atlas docs/product/application-atlas.md
```

Results: `fresh` (covered files match `HEAD`, no relevant uncommitted
changes), `stale`, `missing`, or `invalid`. After exploring a clean commit, get
the value to store with `--compute`. The commit is provenance; the fingerprint
of the covered tree is the proof. Don't require the commit to equal `HEAD`:
committing the atlas itself changes `HEAD`. A stale atlas is a lead, not
evidence, and an outdated atlas is not a product defect.

## Content

Keep IDs (`ROLE-01`, `SURF-03`, `FLOW-07`, `STATE-12`) stable across versions and
update by diff. Sections, as tables where they fit:

1. Intent (declared): promise, primary user, primary job, primary action,
   success signal, deliberate constraints, unacceptable outcomes, sources.
2. Platforms and environments, with inputs.
3. Actors and permissions.
4. Surfaces and navigation (entry, exits, return, route).
5. Flows: per flow, preconditions, before/during/after, failure and recovery,
   real conditions, data written, context that must survive.
6. State catalog per surface (empty, loading, success, validation, error,
   offline, permission, expired session, extreme content, volume).
7. Data and context lifecycle (drafts, filters, selection, scroll, history).
8. External and async boundaries.
9. Destructive and high-consequence actions, with a safe test path.
10. Content and scale envelopes.
11. Platform, input, and accessibility expectations.
12. Coverage ledger: `covered`, `partial`, `unverified`, `out-of-scope`.
13. Open intent questions and conflicts.
14. Change log.

Mark each fact `declared`, `observed`, `code`, `inferred`, or `unverified`.

## Coverage before a full audit

Before calling an audit comprehensive: intent is declared or marked as
hypothesis; every known platform and role has a disposition; every reachable
in-scope surface is mapped; primary and high-consequence flows have entry,
completion, data, states, and recovery; the ledger distinguishes covered from
unverified. Small apps: cover everything reachable. Large apps: inventory the
full breadth, go deep by risk, with at least one flow per role, platform,
interaction pattern, and critical integration. Otherwise narrow the claim.

## Maintenance

Update the atlas in the same change that alters routes, roles, a flow's entry
or outcome, persistence, integrations, supported platforms, limits, or intent.
Add a change-log line and recompute the fingerprint from a clean commit.
