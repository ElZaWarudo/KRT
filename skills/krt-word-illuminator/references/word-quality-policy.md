# Word quality policy

## Semantic structure

Use `Title`, `Subtitle`, `Heading 1`, `Heading 2`, `Heading 3`, `Normal`,
`Quote`, and `Caption`. Use dedicated `Code`, `Note`, and `Warning` styles when
needed. Reuse template styles without rewriting them.

Do not use empty paragraphs for spacing. Configure paragraph spacing in styles.
Keep headings with the following paragraph. Avoid skipped heading levels unless
the document structure justifies them.

## Page layout

Choose A4 by default outside North America and Letter only when the user,
template, or audience requires it. Preserve the template's page size and
margins. Use explicit page or section breaks; do not create pagination with
blank lines.

Use inline figures by default. Size them within the printable page width and
preserve aspect ratio. Supply meaningful alternative text and a semantic
caption. Keep the image and caption together.

Use table header rows, repeat them across pages, and avoid row splits when a
row must remain intact. Prefer concise cells. When a table cannot fit safely,
reduce content, split it, or use a landscape section; do not shrink text until
it becomes hard to read.

## Rendering loop

Render DOCX to PDF with LibreOffice headless, then rasterize every page to PNG.
Inspect pages at readable resolution, including pages that appear repetitive.

Check:

- unexpected blank or almost-empty pages;
- clipped, overlapping, or overflowing text;
- tables outside margins or with unreadable columns;
- stretched, pixelated, missing, or detached figures;
- orphan headings and isolated captions;
- header/footer collisions and inconsistent page numbers;
- bad section transitions or orientation changes;
- substituted fonts, broken symbols, and inconsistent numbering;
- suspicious whitespace and manual blank-line spacing.

Record page-specific findings. Correct the source DOCX and rerender the entire
document. A visual diff is helpful for regression detection but does not
replace inspecting the new pages.

## Accessibility

- Use real headings in a valid hierarchy.
- Add alternative text to informative figures.
- Mark table header rows.
- Use descriptive hyperlinks.
- Preserve a logical reading order.
- Do not communicate meaning through color alone.
- Verify adequate contrast for any custom colors.

## Final privacy

Inspect core and custom properties, comments, tracked changes, and document
content. Remove personal metadata only when required; never silently anonymize
meaningful attribution. Detect possible personal data for human review rather
than deleting content automatically.

