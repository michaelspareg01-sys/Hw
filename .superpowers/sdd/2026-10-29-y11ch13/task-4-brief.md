### Task 4: Lesson 13C Variance and standard deviation — PDF 661–669.

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


## Controller notes
- Already used in Ch 13: see docs/pp_selected_y11ch13.md (13A: BHHS 2023 Q11(c)(i), BHHS 2020 Q12(a)(i)(iv), BHHS 2023 Q13(c)(ii), Manly 2020 Q11(a)(iii); 13B: none).
- Ch 17 is being built in parallel from the same catalogue. Re-read docs/pp_selected_ch17.md (if present) and every other pp_selected file before choosing and again before committing. Ch 17 lessons must keep 15+ clean marks each.
- Hints are a starting idea only, never the first step.
- Reports go in the gitignored SDD folder (not committed).
- Hurlstone 2023 Q8 (catalogue A6: Bernoulli X, E(X) = 5Var(X)) was kept free for 13C. James Ruse 2020 Q1 (A5, Bernoulli variance) is also a 13C candidate. A3/A7 are in the excluded "3U JRAHS.pdf" mock. Under the spec, 17x rows only where the part needs just E(X)/Var(X) of a given distribution (no binomial formula). If too few, apply rule 8 and say why (13B was ruled 0 marks with a factual note; follow that pattern only if nothing at all fits).
