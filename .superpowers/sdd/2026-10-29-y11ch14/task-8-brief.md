### Task 8: Assemble, record, final QA, deliver
**Files:** `cover.html`, `docs/PAST_PAPERS_USED.md`, any fragment needing a layout fix; `/home/user/Hw/output/`.
- [ ] Fill each `@@M14X@@` with "NN marks · NN min" from its lesson's `.pp-intro` line. Confirm that `grep -n '@@' workspace/build/y11ch14/*.html` prints nothing.
- [ ] Append a paragraph to `docs/PAST_PAPERS_USED.md` in the existing style: "Y11 Ch 14 Combinatorics (14A–14F) built <date>. Past papers used: …" listing every used question from `docs/pp_selected_y11ch14.md`, with new abbreviations added to the Key line. Do NOT change the "Next:" line (the controller owns it; the Ch 10 and Ch 15 paragraphs already exist, so add the Ch 14 paragraph in chapter order before the Ch 15 one).
- [ ] Build both PDFs. Run all `workspace/checks/y11ch14_*.py` (all must pass), qa.py (0/0) and the MathJax scan (0). Contact-sheet EVERY page of both PDFs and look at each one. Fix layout defects (layout only).
- [ ] Copy the PDFs to `/home/user/Hw/output/` with the spec names, and report the page counts.
- [ ] Commit: `Y11Ch14: assemble, record, final QA`.

## Controller additions
- qa.py misses MathJax errors: run the MathJax error-string scan on both PDFs.
- Deferred minors (layout/hint only): revision p2 quarter empty / p4 40% (Task 1); suit glyphs ♦♥ could be red (Task 1); 14A p9 quarter blank; 14B PP5 hint: replace with "think about how many digits such a number could have"; 14B lesson pages ~22, ~28 partly blank and ~38 half; plus any deferred items later tasks add to the ledger summary below.
- REQUIRED wording fix (a_14c.html, BBHS 2023 Q12(c) worked solution, the ordered-vs-unordered sentence): replace "every count below, and the total, is 4 times the unordered count" with wording that is true, e.g. "each count of selections of all four batteries (including the total) is 4 times the unordered count". Re-run y11ch14_14c.py after.
- Typo fix: Ex 14D Q19(c) "part B" → "part b" (l14d.html).
- Soften 14D hints: PP6 → e.g. "think of the Es as one item"; PP11 → e.g. "where do the two grids meet?".
- 14E layout: lesson ~p86 (Worked example 20 alone, ~40% blank); rebalance if possible.
- 14E layout: Concept 5 tutor-demo box ~26 mm → ~60–70 mm, Your turn ~120 mm → ~50 mm (pp ~84–85); stray rounded-box sliver at p82 bottom (keep Concept 4 heading with its block / page break).
- 14E labels: STHS 2021 label must follow the cover order ("Extension 1 Mathematics, Trial HSC, ..."); make subpart style consistent across PP labels (e.g. include "(i)(ii)" where all subparts are used, as PP9 does).
- Align ALL Normanhurst Boys (NBHS) past-paper labels in 14A, 14B, 14D, 14E to the cover word order used in 14F ("…, Mathematics Extension 1, Year 12 Course Assessment Task 4 …" — copy exactly what each cover prints), in both lesson and answers files; update any check-script label templates.

## Controller additions from the 14F review (apply in Task 8)
- 14F PP 7 hint (Girraween 2023 Q11(c)): it currently hands over the denominator. Replace with a starting idea only that fits the question as printed (it must not state 40C20 or any other step of the answer).
- 14F PP 6 hint (NBHS 2022 Q11(c)): soften to a starting idea that fits the question as printed (no step of the answer).
- 14F PP 6(i) worked solution: move the full stop out of the display maths.
- Update y11ch14_14f.py if it checks hint text.
