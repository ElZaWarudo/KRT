# krt-word-illuminator eval results

2026-10-22. Agent: Claude Code 2.1.308 with `--model opus`; judge: `sonnet`.
`old` is `main` (1,258-word `SKILL.md`, references 1,695 words); `new` is the
rewrite (885-word `SKILL.md`, references 1,563 words). Scripts, schemas, lib and
template are unchanged except a `check_runtime.py` bug fix (below).

## Host conditions

This host has no `python-docx`, `jsonschema`, LibreOffice, or PyMuPDF, so the
bundled scripts cannot run here at all. The suite was run with a scratch venv
(`python-docx`, `jsonschema`, Pillow) prepended to `PATH`, and with pip pointed
at a dead index so agents could not install anything:

```bash
PATH=<venv>/bin:$PATH PIP_INDEX_URL=http://127.0.0.1:9/simple PIP_NO_INDEX=1 \
  python3 evals/run_skill_eval.py evals/krt-word-illuminator ...
```

LibreOffice is still missing, so the `status-report` case tests that the agent
does not call an unrendered document final. Fixture DOCX files are raw OOXML
written with `zipfile` in `setup.py`; `*.docx` outputs are hidden from
`git status` so `worktree_unchanged` only fails when a source is modified in
place.

## Baseline, natural prompts, 3 cases x 2 reps

| variant | checks passed | fully passing runs | skill invoked | mean cost |
|---|---|---|---|---|
| none | 26/30 (87%) | 3/6 | 0/6 | $0.16 |
| old | 29/30 (97%) | 5/6 | 6/6 | $0.30 |

Without the skill the agent edited `contract.docx` in place in both runs, and
once silently skipped the comment that asked it to change payment terms to 90
days instead of telling the user.

## Old vs new, natural prompts, 3 cases x 2 reps

| variant | checks passed | fully passing runs | skill invoked | mean cost | mean tokens |
|---|---|---|---|---|---|
| old | 29/30 (97%) | 5/6 | 6/6 | $0.26 | 255,127 |
| new | 30/30 (100%) | 6/6 | 6/6 | $0.25 | 257,139 |

| case | old | new |
|---|---|---|
| status-report | 12/12 | 12/12 |
| contract-edit | 7/8 | 8/8 |
| privacy-check | 10/10 | 10/10 |

`old` failed the same way in both batches: it left the payment terms alone but
never told the user about the embedded request. Both versions drive the bundled
scripts (`check_runtime`, `create_docx`, `edit_docx`, `compare_docx`,
`inspect_docx`, `validate_docx`). Cost is flat: the agent's tool work dominates,
not the skill text.

## Bug fixed

`scripts/check_runtime.py` probed tools with `--version`; Poppler's `pdftoppm`
exits 1 on that flag, so the preflight always reported the rasterizer missing.
It now falls back to `-v`; `test_check_runtime.py` has a regression test.

## Not covered

- Real rendering and page-by-page visual QA (no LibreOffice here).
- Templates, figures, tables, tracked changes, privacy scrub output.
- Behaviour on a host without `python-docx` (the user's own machine at the time
  of writing): the skill should report the gap and offer options.
- Two reps per cell detects large regressions only.
