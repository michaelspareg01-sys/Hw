### Task 1: Pack scaffold, cover and revision
**Files:** create `workspace/build/y11ch13/{pack.json,cover.html,revision.html,a_rev.html,figs.py}`, `svg/`, placeholders `l13a.html`…`l13d.html`, `a_13a.html`…`a_13d.html` (each only `<!-- filled by Task N -->`); `workspace/checks/y11ch13_rev.py`.
- [ ] pack.json, cover (rows: Revision "Probability and data" note "Year 11 · Ch 12, statistics"; Lessons 13A–13D with textbook titles and `Past papers: @@M13A@@`…`@@M13D@@`; Review), revision boxes per spec + 5-question warm-up, a_rev answers, rev check reading the HTML.
- [ ] Build; qa 0/0; MathJax scan; look at pages. Commit `Y11Ch13: scaffold, cover, revision` (stage only these files).

### Lesson task standard (Tasks 2–5)
For section S with textbook PDF pages P (answers ≈ 933–938):
- [ ] Render and read every teaching page of S (boxes, examples, extension boxes, notes) and the whole exercise with band headings.
- [ ] `l<S>.html` (replace placeholder) in the house lesson structure: concepts covering every box/method/warning (tables of distributions as HTML tables; graphs as SVG); per concept Tutor demo, Your turn, Worked example(s) copying the textbook examples; Textbook homework verbatim with F/D/E bands (omit only doubtful items, reporting them; long random-number tables may be reproduced as tables or, if huge, as an SVG/table faithfully); Past-paper homework per the spec's rulings.
- [ ] `a_<S>.html` (replace placeholder): ahead → Lesson Examples → Textbook Homework → ahead → Past-Paper Worked Solutions.
- [ ] `workspace/checks/y11ch13_<s>.py` reading every printed result from the HTML and recomputing with `fractions.Fraction` (exact sums, E(X), Var(X)), simulation-free; exit 1 on any failure.
- [ ] Build; qa 0/0; MathJax scan; look at every page added. Commit `Y11Ch13: lesson <S>` (stage only your files).

