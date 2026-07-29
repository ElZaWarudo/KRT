# Autonomous Team Flow

Use this reference for `overnight-team-flow`, `autonomous-team-flow`, or any user instruction equivalent to "do not ask confirmation".

## Goal

Convert an ambitious delivery request into an unattended run:

```text
autonomy mandate -> documentation packet -> approved gate -> Jira/queue seed -> safe waves -> reconciliation -> release handoff -> morning packet
```

The core rule is no runtime interruption after the required gates pass: decisions can be encoded, deferred, or skipped. The documentary planning gate is still mandatory unless already approved or explicitly bypassed by the user's current instruction.

## Autonomy Mandate

Before external or irreversible mutations, resolve an autonomy ledger under:

```text
docs/orchestration/autonomy-ledgers/
```

Use the canonical Compound Master autonomy ledger JSON v1. Read
`../../krt-compound-master/references/autonomy-ledger-schema.md` and validate the
ledger with `../../krt-compound-master/scripts/check_autonomy_ledger.py` as resolved
from the shared skills directory. Swarm must not create a YAML authorization
contract or redefine allowed mutations, deny rules, scope, expiry, lifecycle,
or audit semantics.

The canonical JSON ledger replaces per-action human confirmation only after
required gates pass. It does not remove quality gates and does not authorize
bypassing documentation approval. If no active JSON v1 ledger exists, continue
local reversible work only and record external mutations as manual-required.
On resume, re-read and validate that JSON, compare its contract hash and audit
head, then replace the queue state's non-authoritative resume snapshot.

## Task Definition

First unattended work is documentary planning:

- Load `references/documentary-planning.md`.
- Create or revise the documentation packet.
- Persist `documentation_gate` in `docs/swarm/queue-state.yaml`.
- Mark documentation `in_review`.
- Stop with the review packet when no prior approval exists.

After approval, make work executable:

- Dispatch Planner workers for broad epics, roadmap sections, or Jira parent issues before Implementer workers run.
- Parse roadmap/backlog into the smallest useful work packages.
- Create or update Jira issue map.
- Identify acceptance criteria and verification for every unit.
- Detect dependencies before dispatch.
- Detect overlapping surfaces before dispatch.
- Pre-classify high-risk areas: auth, data, public contracts, migrations, central models, lockfiles, DIAN, accounting, payroll, security.
- Write unclear decisions to the blocker ledger instead of asking immediately.

If task definition is weak, do not improvise a broad platform. Create the documentation packet, propose what could be seeded, leave blocked units explicit, and stop for review unless approval already exists.

## No-Interruption Rules

During autonomous execution after the documentation gate is approved:

- Do not ask user confirmation.
- Do not stop because one unit is blocked.
- Do not stop because one external mutation class is not ledger-covered.
- Do not stop because one worker needs product/legal/accounting/security input.
- Record blockers, defer affected units, and continue independent work.
- Normalize nested Compound decision requests into the blocker ledger; never let a child ask the user during the run.
- Dispatch fixers for bounded verification or review failures when surfaces remain isolated.
- Dispatch Integrator workers before release handoff when two or more units may interact through dependencies, stack order, contracts, migrations, lockfiles, or shared generated artifacts.
- Split broad or scope-creeping work instead of forcing one large PR.

Before documentation approval, no-interruption means "produce the review packet and stop", not "continue into Jira or implementation".

Stop only when no independent ready work remains and every remaining path would violate ledger deny rules or the documentary planning gate.

## External Mutations

Seneschal still does not directly own release side effects:

- Jira mutations go through the selected Jira provider skill.
- Commits, pushes, PRs, reviewer requests, Jira PR backlinks, transitions, and merge flow go through `krt-release-marshal`.

In autonomous flow, pass the canonical JSON ledger path, expected contract hash, latest audit event, and `jira_provider` to downstream skills. Instruct them to use autonomous executors/validators where available. If a downstream skill cannot execute a covered mutation autonomously, record a blocker or handoff gap and continue other approved work.

Merge PRs only when the ledger explicitly allows merge and platform-visible merge eligibility is satisfied.

A user's "no confirmations" preference authorizes unattended work after required gates; it does not authorize bypassing documentation approval, branch protection, failing checks, missing credentials, or unsafe production compliance.

## Morning Packet

End an unattended run with:

```text
Autonomous run: <run id>
Documentation status: <draft|in_review|approved|changes_requested>
Source backlog: <paths/Jira filters>
Completed locally:
- <unit>
Release-ready:
- <unit> -> <release handoff/PR if created>
Needs fix:
- <unit>: <reason>
Blocked/deferred:
- <blocker id>: <decision needed>
Jira seed/drain:
- created/reused/updated/skipped counts
Verification:
- <command/result>
Review gates:
- <result>
Autonomy ledger:
- <path>
Queue state:
- docs/swarm/queue-state.yaml
Blocker ledger:
- docs/swarm/blockers.yaml
Next best action:
- <single highest-leverage unblock>
```
