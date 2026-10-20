Paste this into a prompt (or another skill) together with `assets/template.html` and
`scripts/assemble_report.py` when the agent cannot load the `krt-before-after-herald` skill.

---

When you change anything visible, give me a before/after HTML report as evidence:

1. Before changing code, capture every affected screen in light and dark, at 1440px and 390px wide,
   into `shots/before/<key>-<theme>-<desktop|mobile>.webp`. Use the same data, account and wait time
   you will use afterwards. Desktop images resized to 1200px wide, WebP quality about 68.
2. Make the change, then capture the same screens the same way into `shots/after/`. Fix any horizontal
   overflow, error overlay or page error before going on.
3. Write `report.json` following the template's contract: title, one-sentence intro, meta (date, screen
   count, exact code reference, data used), "What changed" bullets as `<b>Claim.</b> one sentence`,
   "Verification" checks marked ok / note / fail with the command and its real result, a footer saying
   exactly what "before" is, and one short note per screen.
4. Build it with `python3 assemble_report.py report.json shots before-after.html`. It must not report
   missing images.
5. Open it and check: toggles, Previous/Next and arrow keys work without reloading or jumping; it reads
   well in both report themes and at phone width.
6. Give me the file path. Whenever the code changes again, recapture "after" and rebuild before telling
   me the work is done.
