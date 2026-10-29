### Task 2: Lesson 14A Factorial notation
Section 14A, PDF 689–693. Apply the Lesson task standard. Past papers for factorial algebra are scarce. Per house rule 8, you may use fewer marks, or take early 14B-style items that need only factorials and the multiplication principle.


### Lesson task standard (applies to Tasks 2–7)

For section S (14A … 14F) with textbook PDF pages P and answer pages from 938–942:
- [ ] Render and read every teaching page of S (boxes, examples, notes, warnings) and the whole exercise, with its band headings.
- [ ] Write `l<S>.html` (replacing the placeholder) in the Ch 10 lesson structure. Concepts cover every box, method and warning in the teaching part. Each concept gets a Tutor demo (a value-changed variant of a textbook example), a Your turn (parallel, no harder) and Worked example(s) copying the textbook examples with full working. Then the Textbook homework: the exercise verbatim with its F/D/E bands, every question. Note any omission and its reason in the report: off-scope 14G/14H content, or a doubtful item under house rule 6. Then the Past-paper homework.
- [ ] Past papers: choose from `docs/pp_candidates_y11ch14.md` rows tagged S (others if they fit what has been taught so far). Do not reuse anything in `docs/PAST_PAPERS_USED.md`, `docs/pp_selected_ch10.md` or `docs/pp_selected_y11ch14.md`. Total 15–22 marks under house rules 1–8. Verify each on the rendered page and against its school solution. Append the choices to `docs/pp_selected_y11ch14.md` under `## S`.
- [ ] Write `a_<S>.html` (replacing the placeholder): `{{ahead:Lesson S | Title}}` → Lesson Examples (C1, C2, …) → Textbook Homework (final answers, matching the textbook answers; all solved independently) → `{{ahead:Lesson S | Title}}` → Past-Paper Homework – Worked Solutions.
- [ ] Figures: add accurate SVGs to `figs.py` (tree diagrams, grids, arrangements) where the textbook or a paper has a diagram that the question needs.
- [ ] Write `workspace/checks/y11ch14_<s>.py` (for example `y11ch14_14b.py`). It reads every printed numeric answer from `a_<S>.html` and the worked examples, and recomputes each independently. Brute-force enumeration with itertools is preferred for counts. It must exit 1 on any failure.
- [ ] Build; qa.py 0/0; MathJax scan; look at every page added in both PDFs; fix layout.
- [ ] Commit: `Y11Ch14: lesson <S>`.


## Controller rulings (binding)
- Do not use papers that do not print their school name/title: Western 2020 ("Western Mathematics"), Fort Street 2023, NSB 2024.
- Do not use these doubtful items: James Ruse 2020 Q14(c), Sydney Tech Sample 1 Q8, Sydney Tech Sample 2 Q14(c)(ii), Fort Street 2023 Q3(d)(ii).
- Cross-check ALL docs/pp_selected_*.md (Ch 15 is being built in parallel and may take nCr-identity items such as NSB 2020 Q14(a)).
