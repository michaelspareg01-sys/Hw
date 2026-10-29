### Task 1: Pack scaffold, cover and revision

**Files:** create `workspace/build/y11ch14/{pack.json,cover.html,revision.html,a_rev.html,figs.py}`, `svg/`; create `workspace/checks/y11ch14_rev.py`.

- [ ] `pack.json`: lesson parts `cover.html, revision.html, l14a.html … l14f.html`; answers parts `a_rev.html, a_14a.html … a_14f.html`; outputs `lesson.pdf` and `answers.pdf`; titles, footers and heading per the spec. Create minimal placeholder files `l14a.html`…`l14f.html` and `a_14a.html`…`a_14f.html`, each containing only an HTML comment `<!-- filled by Task N -->`, so the pack builds.
- [ ] `cover.html`: copy the Ch 10 cover structure. Title "Year 11 Chapter 14 Combinatorics". Rows: Revision (Probability basics, "Advanced · Year 11"), Lessons 14A–14F with their textbook section titles and notes `Past papers: @@M14A@@` … `@@M14F@@`, then Review. The intro paragraph is the house text.
- [ ] `revision.html`: summary boxes for the spec's revision topics (read the textbook's own wording where 14A–14F assume them: render 14A PDF 689–690 and 14F 720–721 to see what is assumed), plus a warm-up of 5 questions. `a_rev.html`: warm-up answers. `y11ch14_rev.py` checks them from the HTML.
- [ ] `figs.py`: copy the Ch 10 header (imports, `save`, `Fig` class), with no figures yet.
- [ ] Build; qa.py 0/0; MathJax scan; look at the cover, revision and answer page.
- [ ] Commit: `Y11Ch14: scaffold, cover, revision`.

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

