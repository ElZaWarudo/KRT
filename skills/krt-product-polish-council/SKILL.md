---
name: krt-product-polish-council
description: Evidence-based product polish and cognitive-load audits of web, mobile, and desktop apps. Walks real end-to-end flows through twelve polish lenses (focus, consistency, feedback, non-ideal states, protection, hierarchy, copy, perceived performance, platform, accessibility, continuity, seams) and six workload factors (memory, search, integration, decision, uncertainty, recovery), then returns a prioritized, verifiable backlog. Use when asked to polish an app, make it feel finished or professional, assess product maturity, find rough edges, review a flow that users find confusing, exhausting, or mentally taxing, audit cognitive load or mental effort, check a workload or "reduced cognitive load" claim, or verify that a round of changes raised quality. For interaction feel and motion use krt-interaction-polisher; for visual composition use krt-interface-warden.
---

# Product Polish Council

Judge the application as a system of behaviour, not a set of screens.
Perceived quality is close to multiplicative across consistency, reliability,
clarity, responsiveness, and care: one very weak dimension limits the whole, so
the job is to find the weakest links and rank them honestly, not to produce a
long list of nits.

A review request authorizes an audit, not code changes. Implement only when
asked, and never exercise destructive, financial, public, or production actions
without authority and safe data.

## How to run it

One strong pass with the checklists below is the default. Read the code, run
the app when you can, and walk the important flows end to end: entry,
input, pending, outcome, failure and recovery, and real conditions (slow
network, long content, interruptions, phone). Subagents are worth their cost
only for a large app where flows or platforms can be explored in parallel;
split them by flow or surface, not by lens, and keep synthesis yourself.

Use `references/lenses.md` as the checklist of twelve polish lenses and
`references/cognitive-load.md` whenever workload, mental effort, a confusing
multi-step flow, or a "reduced cognitive load" claim is in scope. A finding gets
one primary lens and, where it applies, one primary workload factor; mention
others as cross-references rather than duplicating the finding.

## Intent before judgment

Read the README, briefs, and product docs first. Judge against declared intent:
who the user is, the primary job, the success signal, deliberate constraints,
and unacceptable outcomes. If the docs answer the material questions, proceed.
If a point is genuinely unknown and would change the ranking, state an explicit
assumption, finish the audit, and list the open questions at the end. Stop to
ask first only when you can't identify the user or the primary job at all.
Don't rank a mismatch against unconfirmed intent as a top-priority defect.

Respect declared constraints. Fields, steps, or friction that policy requires
stay; reduce the work around them instead.

## Evidence

Label every finding by how you know it: `observed` (reproduced at runtime),
`code` (seen in code or tests, not reproduced), `declared` (authoritative
intent), `inferred`, or `unverified`. Code shows that something exists, not
that it is reachable or understandable; screenshots don't prove time, state, or
recovery. An inference alone never supports P0 or P1. Areas you couldn't
reach are gaps, not failures.

For workload claims, also give the claim basis (heuristic, observed behaviour,
behavioural measure, self-report, instrumented). An inspection predicts risk;
it never shows that load was measured, "overloaded", or reduced by some
percentage. When someone wants to claim a reduction, say what comparison would
support it and offer wording that describes the concrete changes instead.

## Prioritize causes, not symptoms

- **P0** primary flow impossible, work lost or corrupted, misleading state with
  serious consequences, or an irreversible action without protection.
- **P1** high likelihood of error, repetition, disorientation, or inability to
  recover in an important flow.
- **P2** systemic friction: inconsistency, slowness, ambiguity.
- **P3** a real but limited seam or refinement.

Operability, lost work, trust, and recovery come before ornament. Merge
findings by shared cause and fix, not by matching words; one broken convention
across three surfaces matters more than three cosmetic tickets. Within a
severity, sort by frequency, flow centrality, roles affected, and
reversibility; don't lower severity because the fix is expensive. Prefer a
clarity, feedback, or recovery fix over a new feature. Never average ratings or
sum workload factors into a score.

Every accepted finding has evidence with a location, the user effect, the
smallest concrete correction, and an observable way to verify it.

## Report

Lead with a short verdict naming the weakest link and its consequence. Then
scope and evidence (what was run versus read, platforms, gaps), the prioritized
findings grouped Now (P0/P1 and systemic causes) / Next / Later, a short Keep
list of behaviour fixes must not break, and verification gaps with the next
probe. Add a lens rating profile or a workload table only when it helps the
reader. For a workload-focused question, frame it by task, profile, and
context, and separate necessary complexity from avoidable burden.

## Atlas and regression rounds

For products audited repeatedly, keep a factual application atlas
(`docs/product/application-atlas.md` by default) and check its freshness with
`scripts/check_atlas_freshness.py` before trusting it; see
`references/application-atlas.md`. Create or update one when the user wants
durable coverage or a regression round, not for every audit.

After remediation, reproduce each finding's verification, re-check the lenses
and factors it touched, take a quick pass over the modified flow for
cross-cutting regressions, and mark each finding resolved, partially resolved,
not reproduced, or open with new evidence. Don't upgrade a rating or claim
basis from a change that wasn't behaviourally verified when runtime
verification is available.

## Handoffs

When implementing accepted findings, reuse the app's components and
conventions. For deeper work, `krt-interface-warden` covers visual composition
and critique, and
`krt-interaction-polisher` temporal feedback and motion. They are optional; do
the work inline when they are absent.
