# Deterministic Review Coordination

Load this reference after root captures a worker diff and `execution-lanes.md`
classifies the unit as `high` or `critical`. Use it to partition broad review,
maintain canonical findings, and target validation without asking several
reviewers to rediscover the same defects.

Do not use this machinery for `low` assurance or for a `medium` unit's single
focused reviewer. If a medium finding is disputed or exposes a high-risk
boundary, reclassify the unit before entering coordinated review. Multiple code
surfaces, directories, or available reviewer personas do not earn a council.

Coordinated review is earned by named high-risk boundaries. Before admitting an
assignment, record the unique question, evidence source, and readiness outcome
it can change. Omit assignments that duplicate another reviewer's confidence
contribution.

## Authority Boundaries

- Root owns the review plan and findings registry. Reviewers and validators
  return immutable JSON candidates; they never edit shared state.
- Scripts enforce shape, coverage, hashes, identity separation, severity
  budgets, and lifecycle transitions. Reviewers make semantic judgments.
- Partition primary review by changed code surface. Cross-cutting security and
  public-contract assignments may overlap only when declared explicitly.
- Canonical finding IDs come from the registry, never from reviewer prose.
- Exact fingerprints cover the complete normalized finding payload and
  deduplicate deterministically across review surfaces. Possible semantic
  duplicates require root judgment; do not merge them by fuzzy text matching.

## 1. Compile The Review Plan

Build a JSON input from the root-observed contract hash, diff digest, changed
paths, reviewer capacity, assurance tier, and admitted risk surfaces. Every
changed path must belong to exactly one non-cross-cutting primary surface. Each
assignment names its bounded risk checklist.

```bash
rtk python3 <seneschal-skill-dir>/scripts/plan_review_wave.py \
  --input <review-plan-input.json> \
  > <review-plan.json>
```

Review-plan schema version 2 includes `assurance_tier: high | critical`. Low
and medium units must bypass this compiler. The output binds the tier into
`review_plan_hash`, always sets `validation_wave_required: true`, and sets
`approval_required: true` only for critical assurance. Critical plans require
at least two distinct review assignments so a single reviewer cannot satisfy
the council gate.

The compiler fails on uncovered paths, overlapping primary ownership, unknown
roles, unsafe paths, or malformed inputs. `coverage_complete: false` means the
capacity-limited assignments remain queued as complete executable assignment
objects; run them serially before treating review coverage as complete. Never
drop them to fit the current slot count.

The compiler accepts only `high` or `critical`. Both require independent
validation; `critical` also sets `approval_required`. Reviewer count does not
control either gate. These fields select bounded validation and approval after
findings are ingested; they do not authorize another open-ended review wave.

## 2. Validate Reviewer Terminals

Give each reviewer only its assignment, contract, observed diff, existing
registry snapshot when one exists, and relevant verification evidence. Require
an exact JSON terminal with:

```json
{
  "contract_hash": "sha256:...",
  "diff_digest": "sha256:...",
  "review_plan_hash": "sha256:...",
  "reviewer_id": "reviewer-backend",
  "surface_id": "backend",
  "risk_boundaries_checked": ["input-validation", "response-contract"],
  "findings": [],
  "finding_feedback": [],
  "suppressed_speculative_count": 0,
  "stop_reason": "coverage-complete"
}
```

Validate it before ingestion:

```bash
rtk python3 <seneschal-skill-dir>/scripts/validate_review_terminal.py \
  --plan <review-plan.json> \
  --input <review-terminal.json>
```

The validator verifies the plan hash and resolves both admitted and queued
assignments by `surface_id`. `finding_feedback` lets a reviewer return evidence
against an existing canonical ID with action `corroborate` or `challenge`.
Root applies accepted feedback through the digest-guarded registry command; the
reviewer still cannot mutate shared state.

The Reviewer or Security Sentinel runs this validation before returning and
returns the exact accepted JSON. A missing `principle`, evidence collection, or
other required field is corrected in that same session. Root reruns the
validator before ingestion and never repairs the terminal on the reviewer's
behalf.

Load `role-recoverability.md` and use `render_role_envelope.py` so the reviewer
receives absolute invocation locators and an executable final validator rather
than the placeholders above. Recovery remains conditional and non-certifying;
it does not create a heartbeat protocol or weaken `coverage-complete`.

P0 and P1 findings are never capped. A reviewer may return at most three
actionable P2 findings, each with concrete evidence, impact, and a bounded
recommendation. P3 is not part of the direct Seneschal reviewer vocabulary.
Speculative preferences do not become findings. The reviewer cannot stop on a
finding budget before every assigned risk boundary is checked.

Findings use `Observation`, `Impact`, `Recommendation`, evidence, and one
principle: correctness, security, contract, testing, KISS, YAGNI, knowledge
DRY, scope, or an ISO/IEC 25010 maintainability dimension. Metrics may support
an observation but never determine severity or readiness by threshold alone.

## 3. Maintain The Root-Owned Registry

Initialize one registry for the contract and observed diff. Keep it outside
mutable worker worktrees.

```bash
rtk python3 <seneschal-skill-dir>/scripts/finding_registry.py init \
  --registry <root-owned-findings.json> \
  --registry-id <run-and-wave-id> \
  --contract-hash <contract-hash> \
  --diff-digest <diff-digest>
```

Ingest each validated terminal's findings with the current trusted registry
digest:

```bash
rtk python3 <seneschal-skill-dir>/scripts/finding_registry.py ingest \
  --registry <root-owned-findings.json> \
  --input <finding-submission.json> \
  --expected-registry-digest <trusted-current-digest>
```

Before ingestion, persist the exact validated terminal once with
`persist_role_terminal.py` and record its path and digest in the invocation.

The registry assigns `F-<HASH>` IDs from the contract hash, diff digest, and
complete normalized finding. Repeated exact findings add reporters, review
plans, and surfaces to the same entry. A disagreement in severity, principle,
observation, impact, recommendation, or evidence remains a separate candidate
for root reconciliation. A stale expected digest fails instead of overwriting
another root transition.

Use `feedback`, `validate`, and `resolve` subcommands with exact event JSON and
the current expected digest. Feedback names a canonical `finding_id`, actor,
`corroborate | challenge` action, rationale, and evidence; it preserves the
original finding. Validators must differ from every reporter. Only confirmed
or revised findings may become fixed or explicitly deferred.

## 4. Run Targeted Validation

When `validation_wave_required` is true, validators receive canonical finding
IDs and the evidence necessary to decide them. They do not repeat open-ended
review. Each verdict is exactly `confirmed`, `revised`, or `rejected` and is
applied through `finding_registry.py validate`.

After applying a validator batch, evaluate it:

```bash
rtk python3 <seneschal-skill-dir>/scripts/evaluate_finding_validation.py \
  --registry <root-owned-findings.json> \
  --input <validator-batch.json>
```

Targeted validators may surface a new P0 or P1 encountered while reproducing a
finding; suppressing a newly observed critical defect would be unsafe. They may
not expand the batch with a new P2. Route new P0/P1 candidates through a fresh
root ingestion and validation decision.

Give each validator a finite deadline sized to its supplied IDs and evidence.
Once every supplied ID has one verdict, it returns immediately. Interrupt a
validator that repeats open-ended review, explores unrelated surfaces, or
exceeds the deadline; if the remaining batch is a small deterministic check,
root completes it directly and records root as the validator actor.

When all planned reviewers return no findings, independent validation still
checks the plan's named high-risk invariants or claims. An empty batch may close
the findings registry, but it is only a deterministic receipt and does not
count as confidence gained or satisfy the substantive validation assignment.

## 5. Fix And Reconcile

- Send only confirmed or revised canonical IDs to a Fixer.
- Send one shared-cause defect cluster per Fixer with exact owned paths and
  exact focused commands; state `additional_review: forbidden`.
- Require the Fixer to map every assigned ID to changed paths and focused
  verification in the canonical return shape. Reject a narrative status report
  or a mapping with missing IDs before reconciliation.
- Validate the return with `scripts/validate_fixer_terminal.py` against the
  closed Fixer assignment before inspecting resolution evidence. Root then
  captures command exit codes independently; the mapping does not certify its
  own verification result.
- Apply `resolve` with the new root-observed diff digest and evidence.
- A rejected finding needs no fix. A deferred finding remains visible in the
  release handoff and follows the configured review threshold.
- Do not issue a passing Reviewer certificate while an at-or-above-threshold
  confirmed or revised finding remains unresolved.
- Bind the final Reviewer or Security Sentinel certificate to the latest
  contract hash and root-observed diff digest through `evaluate_worker_run.py`.

## Efficiency Evidence

Record assurance tier, reviewer count, unique review question count, candidate
count, unique finding count, exact-duplicate rate, validation verdict counts,
new validator P0/P1 count, readiness decisions changed, review duration by
surface, and time from observed diff to accepted review. Treat duplicated
questions, empty validation, and speculative findings as zero confidence gain.
Do not reward finding volume or claim improvement from lower review time alone;
escaped defects, validation reversals, and fix rounds must not worsen.
