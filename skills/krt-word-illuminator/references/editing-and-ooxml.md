# Editing and OOXML

## Safe editing sequence

1. Inspect the input package and save its report.
2. Copy to a new output path.
3. Apply the smallest deterministic operation.
4. Inspect and compare before/after packages.
5. Render and inspect all pages.
6. Validate the requested final variant.

The basic editor supports exact paragraph replacement, insertion after a
uniquely named heading, section append, and selected core-property changes.
Abort zero-match and multi-match replacements unless the patch explicitly
allows all matches.

## Package preservation

A DOCX is a ZIP package of parts connected by relationships. Changes to
comments, fields, bookmarks, revisions, notes, numbering, and drawings may
require coordinated edits to:

- the owning document part;
- its `.rels` relationship part;
- `[Content_Types].xml`;
- referenced data parts; and
- identifiers shared across elements.

Never copy an isolated XML snippet without updating relationships and unique
IDs. Use namespace-aware XML. Preserve unknown parts and attributes. Work on a
copy, validate ZIP integrity, reopen through `python-docx` or LibreOffice, and
compare the package inventory.

## Revisions and comments

`python-docx` does not provide a complete revision model. Saving can expose only
the visible paragraph model and may not support edits inside revision wrappers.
Do not promise tracked-change authoring or acceptance through ordinary
paragraph replacement.

Comment removal is package-level cleanup: remove comment anchors and references,
the comments relationship, content-type override, and comments part. Validate
that no dangling relationship remains.

## Field behavior

The tools can insert TOC and page-number field instructions. LibreOffice or Word
may update them on open or conversion. Validate the rendered result; do not
assume an inserted field instruction has a current cached value.

