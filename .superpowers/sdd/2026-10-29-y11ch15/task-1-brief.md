### Task 1: Pack scaffold, cover and revision
**Files:** create `workspace/build/y11ch15/{pack.json,cover.html,revision.html,a_rev.html,figs.py}`, `svg/`, placeholders `l15a.html`…`l15d.html` and `a_15a.html`…`a_15d.html` (each only `<!-- filled by Task N -->`); create `workspace/checks/y11ch15_rev.py`.
- [ ] pack.json, cover (rows: Revision "Counting and index laws" note "Year 11 · Ch 14, indices"; Lessons 15A–15D with textbook titles and `Past papers: @@M15A@@`…`@@M15D@@`; Review), revision summary boxes per spec + 5-question warm-up, a_rev answers, rev check script reading the HTML.
- [ ] Build; qa 0/0; MathJax scan; look at the pages. Commit `Y11Ch15: scaffold, cover, revision` (stage only these files).

### Lesson task standard (applies to Tasks 2–5)
For section S with textbook PDF pages P (answers in 944–947):
- [ ] Render and read every teaching page of S and the whole exercise with its band headings.
- [ ] Write `l<S>.html` (replacing its placeholder) in the Ch 10 lesson structure: concepts covering every box/method/warning; per concept Tutor demo (value-changed variant of a textbook example), Your turn (parallel, no harder), Worked example(s) copying the textbook examples with full working; Textbook homework = the exercise verbatim with F/D/E bands (omit only 15E-dependent or doubtful items, report them); Past-paper homework.
- [ ] Past papers: choose from `docs/pp_candidates_y11ch15.md` rows tagged S (others if fitting what has been taught), honouring the catalogue flags and the spec's negative-power ruling; not in `docs/PAST_PAPERS_USED.md` or any `docs/pp_selected_*.md`; 15–22 marks per house rules 1–8; verify on the rendered page and school solution; append to `docs/pp_selected_y11ch15.md` under `## S`.
- [ ] Write `a_<S>.html` (replacing its placeholder): `{{ahead:Lesson S | Title}}` → Lesson Examples → Textbook Homework (final answers, matching textbook answers) → `{{ahead:...}}` → Past-Paper Homework – Worked Solutions.
- [ ] `workspace/checks/y11ch15_<s>.py` reading every printed numeric/algebraic answer from the HTML and recomputing (use sympy `expand`/`binomial`/`series` for expansions and coefficients; brute-force sums for identities). Exit 1 on any failure.
- [ ] Build; qa 0/0; MathJax scan; look at every page added; fix layout. Commit `Y11Ch15: lesson <S>` (stage only your files).

