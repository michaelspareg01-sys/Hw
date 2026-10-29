### Task 5: Lesson 17D Sample proportions, and the Chapter 17 review — PDF 835–846 and review 847–849. Append the review (in-scope questions) to `l17d.html` and its answers to `a_17d.html` under `{{ahead:Chapter 17 Review | Chapter review exercise}}`.

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
- 17D specifics: Ch 13 lesson 13D used BBHS 2024 Q2 (row E18). E19 (BBHS 2024 Q11(e)) is doubtful: do not use. Most school solutions use no continuity correction for p-hat; follow the school method when the question is silent and say so in one plain line.
- Past-paper stems: keep every method instruction verbatim; only a page/location reference to a table becomes a bracketed pointer "[the standard normal table at the end of the Revision section]". Reproduce a paper's own table extract if its form differs and the question needs it. Results from omitted earlier parts must be supplied in the stem (rule 2).
- Figures go in a new workspace/build/ch17/figs_17d.py.
- After 17D, append the Chapter 17 review (PDF 847–849, in-scope questions; spreadsheet/experiment-only parts omitted per the spec) to l17d.html and its answers to a_17d.html under {{ahead:Chapter 17 Review | Chapter review exercise}}, checked in ch17_17d.py.
- 17C is in a fix round; do not edit l17c.html/a_17c.html.
