### Task 4: Lesson 17C Normal approximations to a binomial — PDF 823–834.

### Lesson task standard (Tasks 2–5)
For section S with textbook PDF pages P (answers 959–964):
- [ ] Render and read every teaching page of S (boxes, examples, notes) and the whole exercise with band headings.
- [ ] `l<S>.html` (replace placeholder) in the house lesson structure: concepts covering every box/method/warning; per concept Tutor demo, Your turn, Worked example(s) copying the textbook examples; Textbook homework verbatim with F/D/E bands (omissions per the spec's spreadsheet ruling or doubtful items, reported); Past-paper homework 15–22 marks per house rules and the spec's rulings.
- [ ] `a_<S>.html` (replace placeholder): ahead → Lesson Examples → Textbook Homework → ahead → Past-Paper Worked Solutions.
- [ ] Append chosen questions to `docs/pp_selected_ch17.md` under `## S` (re-read ALL `docs/pp_selected_*.md` and `docs/PAST_PAPERS_USED.md` first and before committing).
- [ ] `workspace/checks/ch17_<s>.py` reading every printed result from the HTML and recomputing (`math.comb`, `fractions.Fraction` for exact binomial probabilities, `math.erf` for Φ; table-lookup rounding as the textbook does, e.g. z to 2 d.p.); exit 1 on any failure.
- [ ] Build; qa 0/0; MathJax scan; look at every page added. Commit `Ch17: lesson <S>` (stage only your files).

## Controller notes
- Revision (Task 1, in review) holds the Ch 16 normal review and the standard normal table. Refer to it as "the standard normal table at the end of the Revision section", never by page number.
- Ch 13 (13B/13C/13D) is being built in parallel from the same catalogue. Re-read docs/pp_selected_y11ch13.md and every other docs/pp_selected_*.md before choosing and again before committing. Create docs/pp_selected_ch17.md if absent (same format as docs/pp_selected_y11ch15.md).
- Catalogue A1 (BHHS 2020 Q12(a)): parts (i) and (iv) are used by 13A. Parts (ii) and (iii) need p = 0.3 from (i); if used, supply "p = 0.3" in the stem (rule 2).
- Hints are a starting idea only, never the first step.
- Spreadsheet/experiment-only exercise parts: omit per the spec and list them in the report.
- 17C specifics: teach the continuity correction exactly as 17C does (spec ruling). Past-paper solutions follow the school solution's method when the question is silent, stating in one plain line which method is used; never call either method wrong. Honour the catalogue CC column. D5 (BBHS 2022 Q12(e)) and D11 (Caringbah 2021 Q14(a)) are doubtful: do not use. Kings 2021 Q12(c)(iii) (D4) needs μ = 8000 and σ = 40 supplied in its stem if used.
- Figures go in a new workspace/build/ch17/figs_17c.py (same pattern as figs_17a.py/figs_17b.py).
- 17B is in review; do not edit l17b.html/a_17b.html. 13D (Ch 13) may take up to two 17D rows; it does not use 17C rows.
