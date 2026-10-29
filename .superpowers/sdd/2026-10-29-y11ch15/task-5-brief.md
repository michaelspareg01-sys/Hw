### Task 5: Lesson 15D Identities in Pascal's triangle, and the Chapter 15 review
Section 15D, PDF 758–764, plus the Chapter 15 review PDF 767–768. Lesson task standard for 15D; then append the review to `l15d.html` (in-scope questions only; list omitted numbers in the report) and its answers to `a_15d.html` under `{{ahead:Chapter 15 Review | Chapter review exercise}}`, checked in `y11ch15_15d.py`.


### Lesson task standard (applies to Tasks 2–5)
For section S with textbook PDF pages P (answers in 944–947):
- [ ] Render and read every teaching page of S and the whole exercise with its band headings.
- [ ] Write `l<S>.html` (replacing its placeholder) in the Ch 10 lesson structure: concepts covering every box/method/warning; per concept Tutor demo (value-changed variant of a textbook example), Your turn (parallel, no harder), Worked example(s) copying the textbook examples with full working; Textbook homework = the exercise verbatim with F/D/E bands (omit only 15E-dependent or doubtful items, report them); Past-paper homework.
- [ ] Past papers: choose from `docs/pp_candidates_y11ch15.md` rows tagged S (others if fitting what has been taught), honouring the catalogue flags and the spec's negative-power ruling; not in `docs/PAST_PAPERS_USED.md` or any `docs/pp_selected_*.md`; 15–22 marks per house rules 1–8; verify on the rendered page and school solution; append to `docs/pp_selected_y11ch15.md` under `## S`.
- [ ] Write `a_<S>.html` (replacing its placeholder): `{{ahead:Lesson S | Title}}` → Lesson Examples → Textbook Homework (final answers, matching textbook answers) → `{{ahead:...}}` → Past-Paper Homework – Worked Solutions.
- [ ] `workspace/checks/y11ch15_<s>.py` reading every printed numeric/algebraic answer from the HTML and recomputing (use sympy `expand`/`binomial`/`series` for expansions and coefficients; brute-force sums for identities). Exit 1 on any failure.
- [ ] Build; qa 0/0; MathJax scan; look at every page added; fix layout. Commit `Y11Ch15: lesson <S>` (stage only your files).


## Controller rulings (binding)
- Do not use papers that do not print their school name/title (Western 2020, Fort Street 2023, NSB 2024), the JRAHS 2021 "Mock Trial" file, or catalogue-flagged doubtful items (Killara 2021 Q1; Kings 2021 Q14(a)(i) misprint).
- Cross-check ALL docs/pp_selected_*.md (Ch 14 is being built in parallel and may take nCr items).
