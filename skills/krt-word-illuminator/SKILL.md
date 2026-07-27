---
name: krt-word-illuminator
description: Create, edit, inspect, render, compare, validate, and privacy-scrub professional Microsoft Word DOCX documents. Use for reports, proposals, letters, minutes, manuals, articles, and other .docx deliverables that require semantic Word styles, template preservation, grounded content, tables or figures, accessibility checks, metadata hygiene, and mandatory visual QA before final delivery.
---

# Word Illuminator

Produce professional Word documents through an evidence-grounded editorial
workflow. Keep content decisions in the agent and file manipulation in the
bundled deterministic tools.

## Non-negotiable rules

- Separate content, structure, layout, and quality control.
- Inspect every source before drafting. Never invent dates, figures, people,
  regulations, decisions, or results.
- Classify factual material as `user`, `source`, `inference`, or `pending`.
  Mark material without sufficient evidence as `[PENDING CONFIRMATION]`.
- Use semantic Word styles. Do not simulate headings with bold body text or
  blank paragraphs with manual spacing.
- Preserve templates and existing documents. Write to a new path unless the
  user explicitly authorizes replacement.
- Render every final DOCX to PDF and PNG, inspect every page, correct defects,
  and render again. A successfully saved DOCX is not a finished document.
- Do not claim unsupported advanced Word behavior. Read
  `references/capability-matrix.md` before promising comments, tracked changes,
  cross-references, content controls, or field updates.
- Deliver only the requested final variant. Keep reports and page renders in a
  working directory unless the user asks for them.

## Resolve the request

Capture the objective, document type, audience, language, approximate length,
sources, template or identity, mandatory sections, formality, citation needs,
tables, figures, privacy needs, and output path.

Use reasonable defaults for secondary details. Block only when the objective,
essential source material, or intended deliverable cannot be inferred safely.
Model a creation request with `schemas/document-request.schema.json`.

## Load references progressively

| Need | Read |
|---|---|
| Grounding, planning, and content states | `references/grounding-and-planning.md` |
| Styles, layout, tables, figures, and visual inspection | `references/word-quality-policy.md` |
| Supported and deferred operations | `references/capability-matrix.md` |
| Editing or OOXML-sensitive work | `references/editing-and-ooxml.md` |

Resolve `<skill-dir>` as the directory containing this `SKILL.md`; installed
runtimes may not use the repository path.

## Mandatory workflow

1. Inspect source files and the template or existing DOCX.
2. Extract facts, constraints, citations, unknowns, and required sections.
3. Draft a content plan before manipulating DOCX. For non-trivial work, keep a
   temporary request JSON conforming to the bundled schema.
4. Draft text separately from layout. Attach provenance and source IDs to
   factual blocks. Record every unverified claim.
5. Create or edit the DOCX with the bundled scripts.
6. Inspect and validate the generated file.
7. Render DOCX to PDF and all pages to PNG.
8. Inspect every rendered page with the runtime's image-viewing capability.
   Check clipping, overflow, whitespace, orphan headings, tables, figures,
   headers, footers, numbering, font substitution, and blank pages.
9. Record visual QA with `schemas/visual-qa.schema.json`. Correct findings and
   repeat steps 5–8 until all blocking findings are closed.
10. Run structural, accessibility, grounding, and privacy validation. Compare
    before/after versions for edits.
11. Scrub metadata or working comments when the requested final variant
    requires it.
12. Reopen, revalidate, and deliver the final requested file.

## Deterministic tools

All scripts emit JSON to stdout and use non-zero exits for failed checks.

```text
scripts/inspect_docx.py <file.docx>
scripts/create_docx.py request.json [--output file.docx]
scripts/edit_docx.py input.docx patch.json --output edited.docx
scripts/render_docx.py file.docx --output-dir qa/render
scripts/validate_docx.py file.docx [--request request.json]
scripts/compare_docx.py before.docx after.docx
scripts/privacy_scrub.py input.docx --output clean.docx
scripts/build_template.py [--output template.docx]
```

Use the repository command wrapper when required, for example:

```bash
rtk python3 <skill-dir>/scripts/inspect_docx.py input.docx
```

Creation produces a sidecar report by default. Preserve it through QA so the
final validation can account for source coverage and unverified claims.
Use `assets/templates/professional-report.docx` as the neutral A4 base when the
user has no template and a reusable template is preferable to default styles.

## Editing guardrails

- Inspect the input before editing.
- Express requested edits in `schemas/document-patch.schema.json`.
- Prefer exact, uniquely matched paragraph replacements and heading-relative
  insertions. Abort ambiguous replacements instead of guessing.
- Compare the original and edited files. Confirm no unrelated section, style,
  table, figure, header, footer, or metadata changed.
- Do not use the basic edit tool for tracked changes, comments, or arbitrary
  XML surgery. Follow `references/editing-and-ooxml.md`.

## Visual QA evidence

`render_docx.py` reports `visual_qa: pending_manual_inspection` by design.
Create a visual QA JSON containing the render-report path, rendered page count,
every inspected page number, findings, corrections, and final `passed` status.
Validation may accept this file through `--visual-qa`.

If LibreOffice or the PDF rasterizer is unavailable, report the missing tool
and stop short of calling the document final. Do not silently downgrade visual
QA.

## Definition of done

Declare completion only when:

- the DOCX opens and all requested sections are present;
- heading hierarchy and semantic styles are coherent;
- no accidental placeholders remain;
- tables, figures, headers, footers, and page numbers render correctly;
- all rendered pages were inspected and no blocking visual finding remains;
- the requested comments or tracked-change state is correct;
- no unsupported or invented assertion is presented as fact;
- accessibility and privacy checks meet the request;
- an edit changes only the requested scope; and
- the final variant was reopened and validated after cleanup.
