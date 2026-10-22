---
name: krt-review-herald
description: >
  Work through pull request review feedback: fetch every review thread,
  validate each comment against the code, fix what is valid, push back on
  false premises, escalate contract or scope changes, draft short replies, and
  post replies or resolve threads on GitHub only with approval. Use when the
  user asks to address, deal with, or go through PR comments or review
  feedback, fix what reviewers asked for, decide which comments block merging,
  draft reviewer replies, or resolve review threads. Opening, updating or
  merging the PR belongs to krt-release-marshal; commits go through
  krt-gitflow-knight. Runtime aliases may expose this as krt:review-herald.
---

# Review Herald

Take a PR from "changes requested" to "ready for re-review": every thread gets
a decision, valid concerns get the smallest real fix, and each reviewer gets a
short reply they can verify. Load `references/safety.md` before starting and
`references/github-operations.md` before reading or writing GitHub.

## Gathering

Read the live threads, not just top-level comments. From a repo and PR number,
`scripts/build_thread_plan.py --repo <owner/repo> --pr <n> --output <plan.json>`
fetches all unresolved review threads (paginated GraphQL) into a plan with the
decision fields blank. Also check the review decision and top-level comments,
which can hold blockers. If GitHub is unreachable, work from pasted comments
and say what you couldn't verify.

## Deciding

Validate each comment's premise against the current code before acting.
Reviewers are often right, but not always: a requested None check for a
function that already returns `[]` is a reply, not a change. Suggested code is
a proposal. Give every thread one decision:

- **fix:** a real defect or a cheap, in-scope improvement. Blocking issues
  (correctness, security, data, contract, broken tests) come first.
- **reply / decline:** the premise is false or the current approach is
  justified; explain briefly with the evidence.
- **clarify:** the reviewer's intent or the tradeoff is unclear; ask a focused
  question. Open design questions ("should this stream?") stay open for
  discussion unless the answer is obvious and cheap.
- **already addressed / stale:** a later change covers it; check that the
  concern doesn't survive elsewhere before calling it stale.
- **needs the user:** anything that changes a public API or serialized shape,
  schema or migrations, auth or tenancy, adds dependencies, or expands scope.
  Ask before implementing, even when the reviewer asked for it.

When several threads share a root cause, fix the root once and reply to each.

## Fixing

Make the smallest change that resolves the concern, within the PR's scope, and
keep unrelated user changes intact. Run the narrowest meaningful check when
practical and record it; if you skip verification, say why. If CI failures are
part of the feedback, find the root cause in the failing job's log before
changing code; don't just rerun.

Commits go through `krt-gitflow-knight` (approval gate, guarded script, no AI
attribution). Commit titles describe the change, such as
`fix(orders): exclude cancelled orders from CSV export`, never "address review
comments". Group by root cause, and keep thread linkage in replies, not titles.

## Replying

One short reply per thread, in English unless the repo uses another language:
what changed or what you decided, where to look if useful, and the check if it
helps re-review. "Fixed by filtering on `rows` before writing; added a test for
cancelled orders." When disagreeing, give the tradeoff and ask whether the
reviewer is optimizing for something else. Answer the technical point, not the
tone.

## Publishing

Posting replies, resolving threads, requesting re-review, pushing and
commenting all notify people, so each needs the user's approval of the exact
actions. Show them as a list first ("Reply to PRRT_x: '...'; resolve PRRT_x"),
then publish with:

```bash
python3 <skill-dir>/scripts/apply_review_threads.py --plan-file <plan.json>          # dry run
python3 <skill-dir>/scripts/apply_review_threads.py --plan-file <plan.json> --execute
```

The script refuses to resolve a thread without a reply plus `verification` or
`resolution_reason`, and never resolves `clarify` or `blocked` decisions.

Even when the user says "resolve all the threads":

- Resolve only threads that are actually settled. Leave open questions and
  anything waiting on the user's decision open, with a reply or question.
- A fix that exists only in the local worktree hasn't addressed anything for
  the reviewer. Commit and push it (with approval) before replying "fixed" or
  resolving; otherwise say the fix is pending.

## Closeout

Report the status (`ready for re-review`, `fixes pending` or `blocked`), each
thread with its decision, files changed and reply, the verification run, and
any remote actions still waiting for approval.
