---
name: krt-before-after-herald
description: Build a single-file HTML report that compares UI screenshots before and after a change, with theme and viewport toggles, a screen picker, a summary of what changed and an honest verification list. Use when a visual or UX change needs evidence a reviewer can check quickly, when asked for a "before/after", "antes y después", visual comparison, screenshot report or UI change evidence. Runtime aliases may expose this as krt:before-after-herald.
---

# Before/After Herald

Produce one self-contained HTML file (images embedded) in which a reviewer picks a screen and sees
"Before" and "After" side by side, switching screenshot theme, viewport and the report's own theme.
The page is quiet on purpose: a header, two short lists, a sticky toolbar, and the two images.

Files in this skill (paths relative to this skill's directory):

- `assets/template.html`: the page. Don't edit it per report; everything varies through report.json.
- `assets/report.example.json` and `references/report-json.md`: the data contract and its field reference.
- `scripts/assemble_report.py`: validates report.json and the images, embeds them, writes the HTML.
- `scripts/capture_screens.mjs`: optional Playwright capture for both themes and viewports.
- `references/portable-prompt.md`: a paste-in prompt for agents that cannot load this skill.

## Workflow

1. **Freeze "before" first.** Capture the current state before changing code (or from the base commit
   in a separate worktree). Once code changes, the old state is gone.
2. **List the screens.** One entry per screen: `key` (file-name safe), `label`, optional `group`
   (becomes a group in the picker) and `note` (one or two sentences on what changed on that screen).
3. **Capture both sides** with identical data, URL, viewport and wait time, into
   `IMAGES_DIR/before/` and `IMAGES_DIR/after/`, named `<key>-<theme>-<viewport>.<ext>`. With the bundled script:
   ```bash
   node scripts/capture_screens.mjs routes.json shots/before   # before the change
   node scripts/capture_screens.mjs routes.json shots/after    # after the change
   ```
   It exits 1 on horizontal overflow, an error overlay or a page error; fix those before building.
4. **Shrink the images** (keeps a 30-screen report around 10 MB):
   ```bash
   for f in shots/*/*-desktop.png; do magick "$f" -resize 1200x -quality 68 "${f%.png}.webp"; done
   for f in shots/*/*-mobile.png;  do magick "$f" -quality 68 "${f%.png}.webp"; done
   rm shots/*/*.png
   ```
5. **Write report.json** from `assets/report.example.json` (fields in `references/report-json.md`).
   Fill `changes` and `checks` from evidence you actually gathered. Fields ending in `_html` and `meta`
   values are inserted as HTML, so escape anything copied from outside.
6. **Build:**
   ```bash
   python3 scripts/assemble_report.py report.json shots out/before-after.html
   ```
   It fails on any missing image. Recapture it if you can; otherwise build with `--allow-missing`
   (placeholder) and tell the user which captures are missing. It also warns about unreferenced
   images and files over 15 MB.
7. **Open and check it yourself** in a browser: each toggle, Previous/Next and the arrow keys, at desktop
   and phone width, in both report themes. Then give the user the path.
8. **Keep the report current.** When the code changes again, recapture "after", update notes and checks,
   and rebuild. A stale report is worse than none. Keep the build commands in a script next to the
   images so a rebuild is one command.

## Rules that make it easy to review

- **Same conditions on both sides.** Same data, tenant, account, viewport, wait and language; otherwise
  the diff shows noise. If something differs (a backend error present in both), say it in a check.
- **Every screen in every variant.** Light and dark, desktop (1440) and mobile (390). Missing combinations
  are the first thing a reviewer finds.
- **A note per screen.** What changed on this screen and why, in one or two sentences, in the reader's words.
  Reviewers read the note, then look for it in the images.
- **Verification is evidence, not adjectives.** Each check names the command or measurement and its result
  ("498 pass; 25 fail, the same 25 as before"). Use `note` for pre-existing failures, known exceptions and
  checks nobody ran, `fail` for anything unresolved. Never mark `ok` what was not run.
- **State exactly what "before" is.** A commit, a branch, or "the app at the start of this round".
- **One file.** Images embedded, no external scripts or fonts, so it opens offline and can be attached.
- **If you change the template**, keep its no-reload image swapping and held height (test Next at the
  bottom of a long screen), its colour tokens with a dark override, and 4.5:1 text contrast.

## Reusing it from another skill or prompt

From another skill, add a step such as: "Produce visual evidence with the `krt-before-after-herald` skill:
capture before, implement, capture after, write report.json, build, open and check it, and return the path."
For agents without this skill, paste `references/portable-prompt.md` and attach `assets/template.html` and `scripts/assemble_report.py`.
