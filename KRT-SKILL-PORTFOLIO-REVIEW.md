# Consolidated KRT Skill Portfolio Review

Review status: 2026-07-27

Branch reviewed: `feat/skill-portfolio-corrections`

Integrated base: `origin/main` (`6da13b4`)

Starting HEAD: `001a4f9`; the corrections described here remain uncommitted in
the working tree for user review.

## Executive Result

The portfolio now consists of 27 KRT skills with correct canonical identities,
autocomplete metadata, and structural validation. Twenty are classified as
`safety_critical` and load a local security contract indexed from
`docs/safety.md`.

The review was not limited to rewriting prompts. It checked contracts between
skills, authority boundaries, external effects, interruption recovery,
deterministic scripts, tests, and whether each `SKILL.md` promise matches what
its tools execute.

Verifiable results:

- All 27 skills pass `quick_validate.py`.
- Nineteen test files containing 219 `test_*` methods finish without failures.
- The Skill Arbiter corpus contains 12 structurally valid cases in six
  categories; this check does not mean they were executed against models or
  establish a pass rate.
- The catalog recognizes 27 skills and 20 critical skills.
- `git diff --check` finds no whitespace errors in the tracked diff; new files
  were also checked explicitly.
- Real Word rendering remains pending on this host because LibreOffice,
  `pdftoppm`, and PyMuPDF are not installed. The preflight detects this and
  correctly blocks a false declaration of a final document.

## Review Criteria

The evaluation used these dimensions:

1. Activation: concrete description, negative boundaries, and unambiguous routing.
2. Progressive disclosure: operational `SKILL.md` with reusable detail in
   `references/`, `scripts/`, `schemas/`, or `assets/`.
3. Authority: read before mutation, explicit approvals, and no implied
   permission to push, merge, mutate Jira, deploy, or delete.
4. Determinism: validators and scripts for testable contracts, without
   delegating critical invariants to model judgment.
5. Restart and state: versioned artifacts, schemas, and reconciliation when an
   operation can be interrupted.
6. Security: redacted secrets, untrusted inputs, bounded paths and outputs,
   and local contracts for critical skills.
7. Evaluability: positive, negative, routing, permission, fallback, restart,
   and observable-outcome cases.
8. Simplicity: duplication removed, references loaded only when needed, and a
   clear separation between orchestrators and specialists.

## Current Research Basis

Decisions were compared with current skill-design, security, and evaluation
documentation:

- OpenAI, [Build skills](https://learn.chatgpt.com/docs/build-skills) and
  [Agent approvals & security](https://learn.chatgpt.com/docs/agent-approvals-security).
- Agent Skills,
  [Specification](https://agentskills.io/specification),
  [Best practices for skill creators](https://agentskills.io/skill-creation/best-practices),
  and
  [Evaluating skill output quality](https://agentskills.io/skill-creation/evaluating-skills).
- Anthropic,
  [Agent Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview),
  [Skills for enterprise](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/enterprise),
  [Define success criteria and build evaluations](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests),
  and [Mitigate jailbreaks and prompt injections](https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/mitigate-jailbreaks).
- Agent Skills,
  [Adding skills support to your agent](https://agentskills.io/client-implementation/adding-skills-support),
  for collisions, reloads, deduplication, and preservation after compaction.
- Anthropic,
  [Permission policies](https://platform.claude.com/docs/en/managed-agents/permission-policies).
- OWASP,
  [LLM01:2025 Prompt Injection](https://genai.owasp.org/llmrisk/llm01-prompt-injection/).
- Microsoft,
  [Macros from the internet are blocked by default in Office](https://learn.microsoft.com/en-us/microsoft-365-apps/security/internet-macros-blocked).

The consensus supports concise metadata, operational `SKILL.md` files,
progressive loading, scripts for mechanical invariants, evaluations with
negative cases, separation between sandboxing and approvals, and treatment of
external content as data. It also motivated classifying Document Forge as
critical: converted text can contain prompt injection even when the technical
conversion is correct.

## Cross-Cutting Changes Applied

### Authority and External Effects

- Planning, local authorization, and remote mutations were separated.
- Rebase, push, merge, comments, Jira transitions, and deployments require
  visible, specific authority.
- Autonomous modes are bound to a versioned ledger and deterministic
  validators; an autonomy label does not expand permissions by itself.
- Jira Server/Data Center and Jira Cloud are resolved by provider and
  environment without printing tokens or mixing APIs.

### Evidence and Publication

- Document Forge keeps sources and sidecars private; it does not publish
  summaries directly.
- Harness Wise promotes evidence only after deterministic validation and
  secret screening.
- Staging, provenance, and rendering artifacts remain separate from versioned
  deliverables.

### Portfolio Governance

- `krt-skill-arbiter` was created with a unique KRT name that does not reuse
  “forge.”
- Its catalog checks identity, metadata, security wiring, and coverage of all
  27 `krt-*` folders.
- Its versioned corpus measures routing, negative triggers, permissions,
  restart behavior, fallback, and outcomes while keeping `pass`, `fail`, and
  `inconclusive` separate.

### Simplification

- Compound Master coordinates specialists without copying their procedures.
- Swarm Seneschal maintains document authority and a bounded queue without
  replacing Compound Master or Release Marshal gates.
- Jira, evidence, and mutation helpers reuse small contracts instead of
  parallel branches with different rules.

## Matrix of the 27 Skills

| Skill | Verdict | Review result |
|---|---|---|
| `krt-bicentennial-writer` | Fit | Retains progressively loaded editorial references and text-only scope with no external effects. |
| `krt-ci-questor` | Corrected | Explicitly loads security before querying logs or credentials or recommending bypasses. |
| `krt-compound-master` | Corrected | Authority, ledger, roles, review/security/CI gates, and handoff are aligned without duplicating specialists. |
| `krt-delivery-navigator` | Corrected | Preflight and security are mandatory before producing plans that may lead to execution. |
| `krt-deploy-summoner` | Corrected | Distinguishes inspection from mutation and loads the security contract before deployment operations. |
| `krt-docs-chronicler` | Corrected | Security and publication rules prevent secrets or private evidence from entering durable documentation. |
| `krt-document-forge` | Corrected | Conversion, staging, private provenance, and promotion are separate; documents and extracted text are untrusted evidence, and the skill is now safety-critical. |
| `krt-frontend-ux-guardian` | Fit | Functional scope, accessibility, responsiveness, and browser verification remain well bounded. |
| `krt-gitflow-knight` | Corrected | Branch/commit guards and safe updates to local ignore files reduce accidental credential commits. |
| `krt-harness-wise` | Corrected | Private evidence is validated and promoted through a deterministic gate with publication checks. |
| `krt-interaction-polisher` | Fit | Remains a temporal/tactile specialist, separate from visual design and the functional gate. |
| `krt-interface-inquisitor` | Corrected | Canonical metadata and visual-critique routing align with the formal ID. |
| `krt-interface-warden` | Corrected | Canonical metadata and boundaries against Guardian/Inquisitor prevent overlapping responsibilities. |
| `krt-jira-cloud-scribe` | Corrected | Environment preflight, token redaction, autonomy contract, and Cloud API v3 are explicit. |
| `krt-jira-scribe` | Corrected | Environment preflight, token redaction, and Server/Data Center routing prevent use of the wrong provider. |
| `krt-product-polish-council` | Corrected | Canonical metadata and optional specialists preserve a comprehensive audit without blocking on absences. |
| `krt-rebase-smith` | Corrected | Requires a clean tree, explicit branch/base, a plan gate, and separate authorization for push with lease. |
| `krt-release-marshal` | Corrected | Jira, commits, rebase, PR, reviewers, and merge have separate authority and validators; they do not inherit ambiguous permissions. |
| `krt-repo-medic` | Corrected | Health diagnosis connects to Skill Arbiter for reproducible checks without becoming another orchestrator. |
| `krt-requirements-weaver` | Corrected | Safety preflight and evidence keep clarification separate from planning or implementation. |
| `krt-review-herald` | Corrected | Triage, fix application, and remote replies distinguish reads, local changes, and GitHub mutations. |
| `krt-roadmap-cartographer` | Corrected | The context gate, provenance, and safety preflight limit output to one roadmap/readiness report. |
| `krt-security-sentinel` | Corrected | Agentic threat model, rubric, and evaluation connection cover inputs, secrets, permissions, and external effects. |
| `krt-skill-arbiter` | New | Adds a deterministic catalog, versioned corpus, supervisor-captured scoring, and security wiring. |
| `krt-state-archivist` | Corrected | Metadata and security preserve complete history without turning the archive into execution authority. |
| `krt-swarm-seneschal` | Corrected | Queue, blockers, reconciliation, and the authority contract prevent the swarm from skipping plans, gates, or release ownership. |
| `krt-word-illuminator` | Corrected | Added after integrating `origin/main`; provides OOXML security, hash-bound QA, strict privacy, and routing against Document Forge. |

## Specific Review of `krt-word-illuminator`

Word Illuminator was absent from the first pass because it arrived on
`origin/main` through a parallel line of history. After the rebase, the review
covered `SKILL.md`, metadata, references, schemas, template, libraries, and the
nine original scripts.

Corrections applied:

- Preflight before `python-docx`, `zipfile`, and LibreOffice.
- Configurable limits for ZIP member counts and sizes, per-member size, and
  compression ratio, plus physical and central-directory limits before
  `ZipFile`; encrypted, duplicate, and traversal entries are rejected.
- Macros, macro-enabled MIME types, ActiveX, OLE, embeddings, and recoverable
  external relationships are rejected by default, including encoded XML
  forms; passive hyperlinks remain data and are not opened.
- The rendering report is bound to the SHA-256 of the DOCX, PDF, and every PNG.
- Final validation requires exactly one image per page, complete coverage,
  `passed` status, current hashes, and zero open blockers.
- Paragraph editing is limited to plain text in a single run; paragraphs with
  formatting, hyperlinks, fields, drawings, or references abort instead of
  silently losing semantics.
- `--final --privacy` turns custom properties and possible PII into errors
  unless explicitly excepted; it inspects complete stories, alt text, notes,
  extended properties, and ZIP metadata. Reports show fields and counts, not
  authors or original values.
- Inspection and comparison redact content by default; `--include-content` is
  opt-in for protected working artifacts.
- Non-clobber outputs publish atomically and reject symlink components;
  embedded paths in requests or patches cannot escape approved roots.
- Every consumer opens the DOCX with `O_NOFOLLOW`, copies from that same
  descriptor into a private snapshot, verifies that it did not change during
  the copy, and consumes only the admitted version. Replacing the original
  path afterward does not alter what is inspected, edited, compared, scrubbed,
  validated, or rendered.
- Creation publishes the DOCX and sidecar as a recoverable transaction;
  rendering prepares the complete PDF, PNGs, and report in staging and
  preserves earlier evidence if an authorized overwrite fails. It replaces
  only directories carrying its valid marker/manifest and rejects unknown
  entries to avoid deleting unrelated artifacts.
- LibreOffice uses an ephemeral profile and a networkless namespace. An
  explicitly connected preview can be generated, but its report cannot pass
  final validation. Because editable JSON cannot authenticate its own
  provenance, the final gate requires explicit acknowledgment of the isolation
  claim and permits it only when the agent directly controlled execution and
  retained the evidence.
- Privacy scanning counts comments and revisions by namespace and local name,
  including alternate XML prefixes, and rejects sensitive parts renamed
  through relationship or content types.
- Scrubbing requires new rendering, inspection, and QA for that variant.
- `check_runtime.py` checks dependencies without installing them.
- The `references/safety.md` contract, `safety_critical` registration, and
  routing are unambiguous: Document Forge converts sources to Markdown; Word
  Illuminator produces DOCX deliverables.

## Validation Evidence

Primary commands:

```bash
rtk python3 skills/krt-word-illuminator/scripts/test_word_illuminator.py
rtk python3 skills/krt-word-illuminator/scripts/test_package_safety.py
rtk python3 skills/krt-word-illuminator/scripts/test_check_runtime.py
rtk python3 skills/krt-skill-arbiter/scripts/check_portfolio.py --repo-root .
rtk python3 skills/krt-skill-arbiter/scripts/check_corpus.py \
  skills/krt-skill-arbiter/references/cases.json \
  skills/krt-skill-arbiter/references/expectations.json \
  --skills-root skills
rtk git diff --check
```

Results:

| Check | Result |
|---|---|
| Python suites | 19 files, 219 test methods, no failures |
| Word Illuminator | 30 workflow + 13 package-safety + 2 runtime tests |
| Quick validation | 27/27 |
| Portfolio | 27 skills, 20 safety-critical |
| Corpus | 12 cases, six categories, valid structure; not executed against models |
| Real rendering runtime | Correctly blocked by missing tools |

## Residual Risk and Next Cycle

After correcting the two P1 findings and one P2 from the last adversarial
review, no known defects remain that justify blocking the portfolio. Explicit
limitations and improvements remain for the next cycle:

1. Periodically run the 12 Skill Arbiter cases with several models and
   versions, keeping supervisor-captured results separate and recording the
   model, runtime, host, tokens, time, and repetition.
2. Add an A/B baseline against the previous version or no skill to measure real
   improvement, not only absolute compliance.
3. Add CI with LibreOffice and a rasterizer to test real DOCX rendering in
   addition to the existing fast fixtures.
4. Run LibreOffice in a networkless sandbox with CPU, memory, process, and time
   limits defined by the runtime.
5. Add an aggregate metadata budget to the portfolio checker: some hosts limit
   the initial catalog to 2% of context or 8,000 characters.
6. Test trigger collisions and coexistence across repository, user, plugin,
   and system scopes, not only each skill in isolation.
7. Add runtime cases for updating a skill during a session, installing a
   plugin, changing permissions, and restart expectations.
8. Expand the corpus when a real incident reveals a new failure class; do not
   add cases merely to inflate coverage.
9. Review descriptions and negative triggers quarterly based on observed
   routing confusion, not cosmetic trend changes.
10. Run every evaluation in a clean session, holding corpus, model, and runtime
    constant when comparing versions.
11. Extend the portfolio checker with declared and observed indicators for code
    execution, network access, MCP, credentials, and filesystem scope.

## Conclusion

The portfolio no longer depends on persuasive instructions alone. Its critical
areas combine written contracts, authority boundaries, deterministic scripts,
negative fixtures, and portfolio checks. The most important improvement is not
an isolated skill, but the maintenance loop: diagnose, correct, evaluate, and
review again with evidence.
