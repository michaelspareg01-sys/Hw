### Task 2: Lesson 13A The language of probability distributions — PDF 642–651.

### Lesson task standard (Tasks 2–5)
For section S with textbook PDF pages P (answers ≈ 933–938):
- [ ] Render and read every teaching page of S (boxes, examples, extension boxes, notes) and the whole exercise with band headings.
- [ ] `l<S>.html` (replace placeholder) in the house lesson structure: concepts covering every box/method/warning (tables of distributions as HTML tables; graphs as SVG); per concept Tutor demo, Your turn, Worked example(s) copying the textbook examples; Textbook homework verbatim with F/D/E bands (omit only doubtful items, reporting them; long random-number tables may be reproduced as tables or, if huge, as an SVG/table faithfully); Past-paper homework per the spec's rulings.
- [ ] `a_<S>.html` (replace placeholder): ahead → Lesson Examples → Textbook Homework → ahead → Past-Paper Worked Solutions.
- [ ] `workspace/checks/y11ch13_<s>.py` reading every printed result from the HTML and recomputing with `fractions.Fraction` (exact sums, E(X), Var(X)), simulation-free; exit 1 on any failure.
- [ ] Build; qa 0/0; MathJax scan; look at every page added. Commit `Y11Ch13: lesson <S>` (stage only your files).


## Controller rulings / lessons learned (binding)
- Reach 15–22 marks when eligible clean rows exist; sweep the catalogue before accepting a shortfall (rule 8) and explain in the report. Every item must genuinely test methods taught so far; no near-duplicates (also vs earlier lessons).
- Parts on separate lines; hints = starting idea only; no forward references; no long lines in .split columns; headings kept with their blocks; labels keep "Extension&nbsp;1,&nbsp;Q…" together.
- Copied worked example with a textbook typo: print the correct version with no remark and report it. Printed textbook answer with a slip: print your own correct answer with no remark. Typographic fixes (spelling, doubled words) are fine; report them.
- Cross-check ALL docs/pp_selected_*.md (Ch 14 and Ch 17 work in parallel/after).
