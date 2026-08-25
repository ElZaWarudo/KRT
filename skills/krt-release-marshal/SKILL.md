---
name: krt-release-marshal
description: "Orchestrate the full delivery flow for the current project repository: direct krt-gitflow-knight for clean commits, krt-rebase-smith for clean branch history, resolve Jira Cloud or Server/Data Center explicitly, then open a GitHub pull request with bidirectional Jira/PR links. Use when the user asks to create/open a PR, prepare a pull request, ship current work, publish branch changes for review, or run the full gitflow + rebase + Jira + PR workflow. Runtime aliases may expose this as krt:release-marshal."
---

# Release Marshal

Orchestrate the normal KRT delivery flow: commit -> rebase -> Jira -> push/PR -> reviewers -> Jira PR backlink -> Jira review transition. Do not introduce a separate "commit-task-PR" mode. Opening a PR is a handoff for human review; merging is a separate protected action unless an active autonomy ledger delegates the exact merge mutation to the deterministic executor.

The marshal directs component skills instead of duplicating them:

- `krt-gitflow-knight` (`krt:gitflow-knight`) owns branch hygiene, staging, and commit planning.
- `krt-rebase-smith` (`krt:rebase-smith`) owns clean branch history and safe rebase decisions.
- `krt-jira-cloud-scribe` owns Jira Cloud issue/subtask lookup, creation proposals, sprint handling, PR backlinks, and transitions.
- `krt-jira-scribe` (`krt:jira-scribe`) owns the same workflow for Jira Server/Data Center. Keep both provider skills public and separate.
- `gh` owns GitHub remote state, push/PR operations, PR comments, and reviewer requests after release-plan confirmation. Prefer `gh` before GitHub plugins/connectors; use connector/plugin APIs only as fallback when `gh` is unavailable, unauthenticated, or lacks required data.
- The bundled autonomous mutation executor owns ledger-bound autonomous PR, branch, reviewer, Jira, and merge side effects after deterministic validators pass.

Load `references/github-pr-flow.md` for exact `git`/`gh` commands, PR body details, base resolution, remote branch checks, and reviewer lookup.
Load `references/autonomous-mutation-executor.md` and `references/autonomous-validator-registry.md` only for autonomous handoffs that include `autonomous-ledger:<path>`.

Use bundled scripts for mechanical guardrails when preparing a PR:

- Resolve `<release-marshal-skill-dir>` to the directory containing this `SKILL.md`; in installed runtimes this may be `/home/teb/.agents/skills/krt-release-marshal`, not `skills/krt-release-marshal` inside the target repo.
- `<release-marshal-skill-dir>/scripts/check_pr_scope.py --base <base>...HEAD` to summarize human/generated/orchestration-doc lines, including untracked files by default, and surface split warnings.
- Use `--fail-on-blocking` when you need the script to fail for split/oversized-approval conditions while allowing advisory warnings.
- `<release-marshal-skill-dir>/scripts/check_stack_choreography.py ...` to validate stacked-PR merge choreography, especially when a parent PR may merge by squash and a child PR must be refreshed before continuing.
- `<release-marshal-skill-dir>/scripts/format_pr_body.py --file <draft-body-file>` to normalize noisy generated PR copy into the strict public body shape before validation.
- `<release-marshal-skill-dir>/scripts/check_pr_body.py --file <tmp-body-file>` before PR creation or update.
- `<release-marshal-skill-dir>/scripts/resolve_jira_provider.py --root <repo-root> [--provider <auto|cloud|server-datacenter|none>] [--jira-url <url>]` before selecting a Jira skill.
- Commit work is delegated to `krt-gitflow-knight`, which must run its deterministic `.krt/env/jira-scribe.env` ignore guard before planning and before each local commit.
- Jira readiness belongs to the selected provider skill's checkout-local env contract. Treat Jira as ready only when the resolver selected one provider, that provider's checker reports `ok: true`, and any supplied Jira URL matches the configured origin, effective port, base path, and project.

## Mandatory Rules

- Load `references/safety.md` before beginning the workflow.
- Use the host runtime's command wrapper only when the current repo requires one.
- Use `gh` for GitHub PR operations before GitHub plugins/connectors.
- Never create a PR from protected branches: `main`, `master`, or `develop`.
- Never merge PRs or branches without user approval for that exact merge action, even after a release plan was accepted, unless an active autonomous ledger authorizes the exact mutation and the executor passes all merge validators. The approval text may identify the PR by number (`mergea la PR #96 ahora`), by an unambiguous current PR context already resolved by the workflow (`mergea la PR`), or by a generic approval (`dale`, `ok`, `sí`) only when it is the user's direct answer to an explicit pending merge prompt for that resolved PR. Generic approval to accept a release plan, create/update a PR, request reviewers, or continue non-merge work is not merge approval.
- Never merge a PR unless GitHub shows either:
  - human reviewer approval for the PR, or
  - that the PR targets an experimental base branch such as `experimental/*`, `experiment/*`, `spike/*`, `sandbox/*`, `prototype/*`, or `playground/*` and that branch protection/rulesets do not require approving reviews there.
  Internal code review, Compound Master review, CI evidence, author approval, or the agent's own judgment cannot substitute for GitHub-visible merge eligibility.
- Prefer `develop` as PR base when it exists; otherwise use the repository default branch unless the user or enclosing workflow provided a base.
- Never include LLM attribution in PR title/body or commit messages.
- Write GitHub-visible PR titles, body bullets, and reviewer-facing messages in English by default. Write every standalone PR comment authored by Release Marshal in English; do not publish a non-English PR comment. Keep user-facing plans in the user's language and Jira summaries/descriptions in Spanish. An explicit user instruction, repository convention, or required template may specify another language for titles, bodies, or reviewer messages, but not for Release Marshal PR comments. Translate supplied prose while preserving code identifiers, product names, issue keys, URLs, and quoted text that must remain exact.
- Never include Compound Master planning IDs or package numbers in PR titles, PR body bullets, branch names, or commit messages unless the user or repo convention explicitly requires them.
- Prefer branch names that describe the capability or functional behavior being shipped. Treat work-package IDs, review-unit markers, package numbers, and delivery-phase labels as branch-hygiene debt unless the user or repo convention explicitly requires them.
- Never put both parent and child Jira references in commit messages. If repo convention requires a Jira reference or link in a commit, use only the immediately relevant issue: usually the subtask/work-package issue; use the parent only when no child issue exists.
- Jira issue and subtask summaries/descriptions created or proposed by Release Marshal must be in Spanish. Translate English branch names, commit summaries, PR titles, or upstream suggested Jira text into concise Spanish before passing them to the selected Jira provider skill.
- Never include secrets, tokens, credentials, or internal environment dumps in the PR body.
- Treat verification results from upstream workflows as readiness evidence only. Do not include test commands, test output, or verification summaries in the PR body unless the user, repo template, or project convention explicitly requires it.
- Do not run tests, linters, or formatters unless the user explicitly asks; use verification results supplied by the user or upstream workflow.
- Before pushing or updating a PR with a CI-fix commit, require evidence that the repo-specific command equivalent to the affected CI job passed locally, or present the missing validation clearly and ask for explicit override before the remote mutation.
- Do not ask for Jira credentials or assume a provider. Resolve provider from explicit `jira-provider`, Jira URL, or exactly one ready provider. Use that skill's checkout-local env contract (`jira-cloud-scribe.env` or `jira-scribe.env`). If Jira is required and provider resolution/readiness fails, block and ask whether to continue without Jira. If Jira is optional, show the exact no-Jira diagnosis in the release plan and continue after approval.
- For stacked PRs, treat squash merge as a special choreography case. If PR1 will merge by squash and PR2 is stacked on PR1's branch, PR2 must be rebased or retargeted onto the final base before continuing merge work, and parent branch deletion must wait until that refresh is complete.
- Use `--force-with-lease`, never plain `--force`, when a rewritten branch must be pushed.
- Require the exact push command in the visible approval for every push, including first publication with `git push -u`. Reuse an accepted Release Marshal approval only when remote, branch/refspec, and push mode match exactly; otherwise ask again.
- In autonomous mode, route PR/branch/reviewer/Jira/merge side effects through `scripts/autonomous_mutation.py`; direct `gh`, Jira, or push commands are validation-only/manual-required unless the runtime enforcement boundary is confirmed.
- Prefer strict PR bodies: one factual change bullet per line, blank line, then the immediately relevant Jira URL. Do not include stack context, retargeting plans, base-branch notes, reviewer instructions, verification, or any operational commentary unless the repo template explicitly requires it.
- Prefer reviewable PRs and logical commits over package-sized PRs when the pending work has clear boundaries. A work package may produce several review-unit PRs; a single PR should represent one focused review unit unless a broad unit was explicitly approved.
- Use one or two commits only when the change truly has one or two coherent concerns. Do not compress broad feature work into "implementation" plus "docs" when the diff spans persistence, services, API contracts, generated surfaces, tests, and configuration.

## Approval Policy

The workflow has one initial plan acceptance gate. After the user accepts that plan, proceed through local/reversible phases without asking again: branch creation/switching, staging, local commits, local rebase on unpushed branches, reading repo/GitHub/Jira state, and preparing PR text.

The release plan is a user-visible contract, not internal reasoning. Emit it in the assistant's visible response before changing local state or invoking component skills that mutate state. Do not leave the plan only in analysis/thought. If the runtime has separate reasoning and final-response channels, the plan must appear in the final/user-visible message.

Ask before destructive, irreversible, external, or notification-causing work unless that exact action was explicitly included in the accepted plan:

- PR or branch merge.
- Jira issue/subtask creation or updates.
- Jira transition.
- Any push, including `git push -u` and `--force-with-lease`; the accepted plan must show the exact push command.
- PR creation or update.
- Reviewer requests.
- PR comments or other reviewer-facing PR messages.
- Remote branch rewrites.

One explicit release-plan approval may cover reviewer requests, an exact PR comment, automatic post-PR Jira PR backlinking, and automatic post-PR Jira transition to `En Revisión` if the plan names the behavior and fallback. For a PR comment, the plan must name the target PR and show the exact English text to publish. For Jira PR backlinking, the plan must name the issue and PR link behavior. For Jira transition, the plan must name the issue and target status. For reviewer requests, the plan may name explicit reviewers or authorize automatic lookup and request of a clear inferred human reviewer.

Merge approval cannot be bundled into the release-plan approval. If the user asks to merge, first inspect the PR's review, branch-protection, and check state, then ask for merge authorization only after the visible gate is satisfied: human reviewer approval on normal/protected bases, or GitHub-visible review-optional status on an experimental base. The response may be a generic approval when the prompt names the PR and the pending merge action. If approvals, protection state, or checks are missing, report the missing gate and stop without merging.

Autonomous approval can be bundled only by an active ledger, not by prose in a release plan. The executor must validate ledger scope, payload hash, live state, current-head human approval, branch protection/rulesets, required green checks, audit write, and enforcement boundary before mutation. Missing data blocks.

## Inputs

Use context already provided by the user or previous skills:

- Desired workflow scope: full flow or PR-only.
- Review unit scope from Compound Master, when provided.
- Jira parent issue key, subtask key, or issue URL.
- `jira-provider:cloud|server-datacenter|none` from an enclosing workflow when known; persist it as `jira_provider` in release handoffs and autonomous Jira mutations.
- Jira policy from an enclosing workflow: `required`, `optional`, or `skip`; default to `optional` when the enclosing workflow provided Jira-ready handoff text but no explicit policy.
- Suggested Jira summary/description from an enclosing workflow. Treat these as semantic input, not final text; normalize them into Spanish before Jira creation proposals.
- Target/base branch.
- PR title/body preference.
- Optional PR comment intent or draft. Treat it as semantic input, normalize it to concise English by default, and preserve exact technical identifiers.
- Draft vs ready preference.
- Explicit reviewers, or "sin reviewers" / "no reviewers".
- Verification results as internal readiness context only.
- For CI fixes, affected workflow/job context plus the local CI-equivalent command result, or the exact reason that validation could not be run.
- Suggested commit grouping from an enclosing workflow, when provided.
- Autonomous ledger path, allowed mutation classes, latest audit hash, and executor mode from Compound Master, when provided.

If the user asks simply to create a PR and there are uncommitted changes, propose the full flow. Treat missing Jira context as optional by default: run provider resolution when there is enough signal, otherwise state that Jira will be omitted unless the user requires it. Never infer a default Jira provider.

## Workflow

### 1. Preflight And Phase Plan

Load `references/github-pr-flow.md` for commands. Inspect branch, working tree, remotes, and repository default branch.

When Jira may be relevant, run `python3 <release-marshal-skill-dir>/scripts/resolve_jira_provider.py --root <repo-root>` plus `--provider` or `--jira-url` when supplied. Resolution order is explicit provider, URL, then exactly one ready provider. If both are ready, neither is ready, or explicit input conflicts with the URL, report ambiguity/unresolved state; never choose a default. Preserve the resolved `jira_provider` in the plan and all handoffs.

When the release may produce stacked PRs, use `python3 <release-marshal-skill-dir>/scripts/check_stack_choreography.py ...` to validate the plan before remote mutations. At minimum, use it to verify that any squash-merge parent PR has an explicit downstream refresh plan, and rerun it after parent merge before continuing child merge work or deleting the parent branch.

Run a PR scope guardrail before building the plan:

- Prefer running `<release-marshal-skill-dir>/scripts/check_pr_scope.py --base <base>...HEAD` after base resolution.
- Compare changed files against any provided review-unit scope. If the diff includes unrelated review units, stop and ask whether to split or proceed with an explicit mixed-scope override.
- Treat these `check_pr_scope.py` results as soft blockers before PR creation: lines printed as `BLOCKING:`, generated/mechanical files dominating functional review, or ~1,000+ human-authored changed lines. Mixed orchestration/planning docs are a warning to assess relevance and noise, never a blocking reason by themselves, and not a reason to silently exclude related documentation from the branch or PR.
- Do not respond to documentation warnings by moving related docs into stash, another worktree, a side branch, or an otherwise unshipped local state. Either keep the docs in the current PR/branch, or show an explicit user-approved split plan that names where those docs will ship.
- Treat >900 human-authored changed lines as an advisory warning that must be visible in the plan.
- If a soft blocker appears, do not bury it as a normal warning. The plan must include an explicit `Size/scope decision:` line with exactly one of: `split before PR` or `approve large PR because <rationale>`.
- The accepted release plan only authorizes an oversized/mixed PR when that `Size/scope decision` line names the rationale and the remote mutations covered by approval include the oversized override.
- If the user or enclosing workflow already approved a broad review unit, carry that rationale into the release plan and `Size/scope decision`, not the PR body.

Build and show a phase plan in the user's language. The visible message should read like an editorial release proposal, not a raw workflow dump. The English labels below are canonical examples; translate every visible label into the user's language except the machine-readable `Size/scope decision:` control line and its `split before PR` / `approve large PR because <rationale>` values, which must remain exact. For a single PR/release unit, prefer a compact structure such as:

```markdown
**Release plan**
- Objective:
- Current branch:
- Base branch:
- Scope:
- Commits:
- Jira:
- Scope guardrail:
- Size/scope decision: `<split before PR | approve large PR because rationale | not required>`
- Exact push: `<exact push command or none>`
- PR:
- Reviewers:
- Merge:
- Remote mutations covered by this approval:
- Items I will still ask about:

Do you approve this release plan?
```

Adapt the labels when another short shape is clearer, but keep the same idea: summarize the release decision, not the tool choreography. The push is the exception: show the exact push command so approval binds remote, branch/refspec, and first-push versus force-with-lease mode. Use exact branch names and concrete Jira/PR intent when known. Summarize checker/script outcomes in plain language instead of pasting raw diagnostics. In manual/guarded flow, make clear that merge is not part of this step and that the PR will wait for human review plus later merge authorization. In autonomous flow, summarize merge posture in one sentence instead of dumping validator details unless the user needs them. If a value is not known yet, say what local read-only step will resolve it inside the accepted plan.
When a PR comment is in scope, add the target PR and the exact English comment text to the visible plan. Approval covers only that target and text; present any later edit as a new external mutation.
When commit work is needed, the visible plan should include the proposed commit messages plus the main files or surfaces for each commit. Do not summarize commits as merely “needed” or “one or more commits”; show the intended grouping when it can be inferred safely.
When branch work is needed, the visible plan should include the proposed branch name. Prefer semantic branch names derived from the shipped capability, not from work-package labels, review-unit numbering, or planning traceability.
When the release plan spans two or more stacked or sibling PRs, do not compress them into one generic phase summary. Prefer this visible structure instead:

```markdown
Ready. <one-line readiness summary>

Local state:

- <branch or stack fact 1>
- <branch or stack fact 2>
- <validation status / warning>

Updated delivery plan:

PR1

- Branch:
- Base:
- Commit / Commits:
- Scope / Functional scope / Documentation scope:
- Title:
- Body / Validated body:

PR2

- Branch:
- Base:
- Commit / Commits:
- Scope / Functional scope / Documentation scope:
- Title:
- Body / Validated body:

Note about PR2:

- <stacking or retarget note when relevant>

Inferred reviewer:

- <reviewer or “none clearly identified”>

Jira:

- <runtime/mutation status>
- <what is still pending>

Exact next steps, if desired:

1. ...
2. ...
3. ...

To have me execute it, reply yes and name the concrete action.
```

Use this multi-PR structure by default when the message needs to explain stacked branches, retargeting after a base PR merge, per-PR commit groupings, or a split between functional and docs scope. Keep each PR block editorial and concrete. Do not hide stacked-PR prerequisites in prose if they materially affect PR body wording, base branch choice, or reviewer understanding.
For stacked PRs, add one short choreography note when relevant:

- merge method expected for PR1;
- whether PR2 will be rebased or retargeted after PR1;
- whether parent branch deletion must wait.

If PR1 is expected to merge by squash and PR2 is stacked on PR1, this note is mandatory in the visible plan.

The plan must be in the final/user-visible response for the gate. Do not only summarize that a plan exists. Do not continue into commit, rebase, Jira creation/update, push, PR creation/update, reviewer request, Jira PR backlink, or Jira transition until the user accepts this visible plan.

If the plan includes `approve large PR because <rationale>`, the legacy `aprobar PR grande`, `mixed-scope override`, or any equivalent oversized/split override, that approval is only valid for the specific branch, base, Jira issue, and changed-line counts shown in the plan. If the diff grows materially before PR creation, rerun the scope guardrail and ask again.

Plan these phases:

- Commit phase: needed if there are staged/unstaged changes or branch hygiene issues.
- Rebase phase: recommended before PR unless the user explicitly skips.
- Jira phase: needed if the user wants a Jira link, the project requires it, or optional Jira context/configuration is available enough to create/reuse a task safely under the checkout-local `jira-scribe.env` contract; otherwise summarize the omission briefly, for example "omitida: Jira no listo en este checkout", rather than asking a separate question.
- PR phase: always included.
- PR scope guardrail: validate that the PR contains one focused review unit; separate docs/orchestration and generated artifacts only when they materially obscure review. Keep related documentation updates, including catch-up docs for nearby already-landed behavior, in the branch/PR by default unless the user explicitly wants a split.
- Never leave related documentation orphaned in stash/worktree/side-branch state.
- Reviewer phase: after PR creation, request explicit reviewers or infer one clear reviewer when the accepted plan includes automatic reviewer handling; otherwise ask or skip according to user preference.
- Merge phase: omitted from the normal release flow. A later merge requires a fresh PR-state inspection, visible human reviewer approval, passing required checks, no blocking change requests, and exact user authorization for that PR.
- Jira PR backlink phase: after a ready PR exists, add the PR URL back to the associated Jira task/subtask when Jira context exists and the accepted plan included that backlink; when the PR groups several review units, backlink every covered review-unit subtask; otherwise ask.
- Jira transition phase: after a ready PR exists, move the associated Jira task to `En Revisión` when Jira context exists and the accepted plan included that transition; when the PR groups several review units, transition every covered review-unit subtask; otherwise ask.

When commit work is needed, include proposed branch and commit grouping when practical. If grouping needs more inspection, make that the next local step inside the same acceptance gate rather than adding another branch/commit confirmation.

Commit grouping guidance for the phase plan:

- Inspect the changed file list before proposing grouping. If the enclosing workflow supplied grouping, validate it against the actual changed surfaces and refine it when it is too coarse.
- Prefer three to six logical commits for broad packages with natural seams.
- Natural commit boundaries include data/model/schema changes, domain/service or integration behavior, API/controller/generated contract surfaces, configuration/deployment surfaces, focused tests/fixtures, and docs/orchestration artifacts.
- For multi-surface feature work, explicitly consider separate commits for persistence, service/integration behavior, API/generated contract surfaces, config/deployment wiring, focused tests, and docs.
- Avoid broad catch-all messages such as `feat(epcis): add bridge foundation` when the files naturally split into narrower review units like model state, bridge service, API endpoint, tests, and docs.
- Keep tests with the behavior commit when splitting them out would leave an intermediate commit obviously broken or hard to review. Use a separate `test(...)` commit only when the test change is a coherent review unit and earlier commits remain sensible.
- Keep docs/orchestration state in a separate `docs(...)` commit when it does not need to be bundled with runtime behavior.
- If more than six commits seem necessary, call out that the package may be too broad or that some commits should be combined.

Ask the user to accept the visible phase plan before changing local state.

### 2. Commit Phase

If there are staged/unstaged changes or the current branch is protected/off-convention, load and follow `krt-gitflow-knight`. Pass along any suggested commit grouping from the accepted release plan. Let it use the accepted release plan or commit plan as the single local gate. Return here after commits complete.

### 3. Rebase Phase

Unless the user explicitly skips history cleanup, load and follow `krt-rebase-smith`. Resolve target/base from current context when unambiguous. Use `rebase --onto` when the branch was derived from another feature branch whose commits should be dropped. The accepted plan may satisfy Rebase Smith's push gate only when it included the exact push command that remains unchanged.

### 4. Jira Phase

If Jira context was provided, keep its URL and `jira_provider`, but do not treat it as execution-ready until the provider resolver selects one provider and that provider's checkout-local readiness check passes.

If `jira-policy:skip`, omit Jira lookup, creation, backlinking, and transition.

Resolve Jira with `scripts/resolve_jira_provider.py`. Use `krt-jira-cloud-scribe` only for `jira_provider=cloud` and `krt-jira-scribe` only for `jira_provider=server-datacenter`. Run API commands through the selected provider's `run_with_jira_env.py`. If resolution or readiness reports `ok: false`, treat the exact result as a diagnosis, not permission to guess or switch providers. With `jira-policy:optional`, surface it and continue without Jira after plan approval. With `jira-policy:required`, stop and ask whether to continue without Jira. For PRs that look like a review unit inside a larger delivery sequence, prefer finding or creating a parent task plus subtasks only when there are two or more likely child tasks. Never propose a single parent task with a single child subtask; use one standalone `Tarea` for that case and attach PR backlink/transition to it. Before proposing creation, derive Spanish Jira text:

- Summary: concise Spanish action phrase, no branch prefixes, no Conventional Commit type, no Jira key, no Compound Master IDs, and no package/date numbers.
- Description: 1-3 concise Spanish sentences explaining what must be done and why.
- If an enclosing workflow supplied English suggested Jira text, translate it to Spanish while preserving the intended scope.
- If the work domain contains unavoidable English product/API names, keep those terms but write the surrounding title and description in Spanish.

Pass the Spanish summary, description, and `jira_provider` explicitly to the selected Jira provider skill. When looking for an existing Jira task/subtask to associate with commits, branch work, or PRs, prefer only issues in open or in-progress statuses; treat done/closed-like matches as historical context, not default reuse candidates. Create or reuse Jira issues only after confirmation. Capture the immediately relevant Jira URL for the PR body: the subtask when a real multi-child parent exists, otherwise the standalone task.

If provider resolution or the selected readiness checker reports any `ok: false` diagnosis, stop the Jira phase and ask whether to continue PR creation without Jira links only when `jira-policy:required`. With `jira-policy:optional`, record the exact diagnosis, omit Jira links/backlinks/transitions in the plan, and continue after the normal release-plan approval.

### 5. PR Preparation

Load `references/github-pr-flow.md` for base selection, remote branch state, PR content gathering, and body construction.

Build PR body text deterministically:

1. Draft only change lines, plus the immediately relevant Jira URL when present.
2. Run `<release-marshal-skill-dir>/scripts/format_pr_body.py --file <draft-body-file>` and write the output to the body file used by `gh`.
3. Run `<release-marshal-skill-dir>/scripts/check_pr_body.py --file <tmp-body-file>`.
4. If the formatter cannot find change lines or the checker fails, fix the draft body before asking for PR approval. Do not fall back to `Summary`, `Verification`, stacked-context, reviewer, retargeting, or test-command sections.

Before push or PR creation/update, show a concise user-facing PR proposal in the user's language. The English labels below are canonical examples; translate every visible label into the user's language. Prefer a shape such as:

```markdown
**PR proposal**
- Current branch:
- Base branch:
- Proposed commits:
- Title:
- Status:
- Scope:
- Key files or surfaces:
- Exact push:
- Jira:
- Reviewers:
```

Then show:

```markdown
**PR body**
- ...
```

Keep this proposal editorial and review-oriented, but always show the exact push command. Summarize PR body validation as a short confidence note such as “body validated” or “I adjusted the body to match the format,” not raw checker output, unless the checker is failing and the failure itself needs discussion. If Jira backlinking or transition will happen automatically after PR creation, mention that briefly in the proposal only when it affects the user's approval decision.
When there are multiple PRs in scope, emit one `PR1` / `PR2` / `PR3` block per branch instead of one merged proposal, and add a short `Local state:` section above them with the current stack/base relationships and any non-blocking validation warnings. Keep the block labels stable so users can approve “open both PRs” against a concrete structure.
If the current branch name includes planning/review-unit identifiers or otherwise reads like traceability instead of capability, treat that as branch hygiene debt. When the branch has not been pushed yet, propose a semantic rename in the visible plan. When it has already been pushed, call out the mismatch in the plan and ask before renaming.
For semantic renames, prefer the primary user-visible or architectural capability in the slug, for example `feat/drive-watch-renewal` over `feat/wp3-watch`, or `fix/release-plan-jira-backlink` over `fix/ru2-jira`.
Ask for approval before the next remote mutation.

### 6. Push And Create PR

After approval, push only if the exact push command still matches the accepted plan, then create the PR with `gh`. If remote, branch/refspec, or push mode changed, present the new exact command and obtain fresh approval. Use a temporary body file rather than passing long body text inline.

If an open PR already exists for the branch, stop and ask whether to view/update it instead of creating a duplicate.

### 6.5 Stacked PR Refresh Rule

When a parent PR in a stack merges by squash:

1. Rebase or retarget the child PR onto the final base before continuing merge work on the child.
2. Treat downstream approvals and checks as stale until GitHub shows them current after the refresh.
3. Do not delete the parent branch before the child refresh is complete.
4. Prefer proving this state with `scripts/check_stack_choreography.py` before presenting the next child-merge step.

### 7. Reviewer Phase

If the user explicitly requested no reviewers, skip.

If the accepted release plan already included the exact reviewer request behavior, do not ask again.

If the user provided reviewers and the accepted plan did not already approve reviewer requests, show them and ask before adding them because this notifies people.

If no reviewers were provided, infer candidates from recent merged PR approvals against the same base. Exclude bots, duplicates, and the author/current GitHub user. If no clear reviewers remain, say so and skip assignment. If the accepted plan included automatic inferred reviewer lookup/request, add the single clear reviewer without asking a second time; otherwise ask before adding inferred reviewers.

### 7.5 PR Comment Phase

Post a PR comment only when the user or an enclosing workflow explicitly requests one. Do not add a ceremonial status comment merely because the PR was created.

Draft the comment in concise English, even when the conversation and visible release plan are in Spanish. Preserve code identifiers, issue keys, URLs, product names, and exact quoted text. Translate any supplied non-English draft before presenting or posting it. Do not publish a non-English PR comment.

Show the target PR and exact comment text before posting. Do not ask again when the accepted release plan already approved that exact target and text. Load `references/github-pr-flow.md` for the body-file command. In autonomous mode, treat PR comments as manual-required unless the active validator registry and mutation executor explicitly support a PR-comment mutation class.

### 8. Closeout, Jira PR Backlink, And Review Transition

After PR creation, return PR number, URL, base branch, head branch, Jira link if included, draft/ready state, and the comment URL when a PR comment was posted.

If Jira context was included, the PR is ready for review, and the approved plan included Jira PR backlinking, use the resolved Jira provider skill to add the PR URL back to the associated Jira issue without asking again in manual/guarded flow. When the PR groups several review units, add the backlink to every covered review-unit subtask, not just one. In autonomous flow, call the mutation executor with `--jira-provider <jira_provider>` so it selects the matching provider validator. For a grouped PR whose subtasks should inherit completion from the parent, also remote-link the grouped PR to the shared parent so the parent is autonomously completable. Prefer a Jira remote link only. If the provider or issue key is ambiguous, the PR is still draft, or the approved plan did not include automatic backlinking, ask or report the deferred action instead of updating Jira silently.

If Jira context was included, the PR is ready for review, and the approved plan included review transition, use the resolved Jira provider skill to inspect real transitions and move the associated Jira issue to `En Revisión` without asking again in manual/guarded flow. When the PR groups several review units, transition every covered review-unit subtask. In autonomous flow, call the mutation executor with `--jira-provider <jira_provider>`. If `En Revisión` is unavailable, provider or issue key is ambiguous, the PR is still draft, or the approved plan did not include automatic transition, ask before transitioning.

## PR-Only Mode

If the user explicitly asks for PR-only mode:

- Do not run commit, rebase, or Jira phases.
- Still refuse protected branches.
- Still stop on uncommitted changes unless the user confirms they should be ignored.
- Still ask before push and PR creation.
