### Task 1: Pack scaffold, cover, Ch 16 normal review, standard normal table
**Files:** create `workspace/build/ch17/{pack.json,cover.html,revision.html,a_rev.html,figs.py}`, `svg/`, placeholders `l17a.html`…`l17d.html`, `a_17a.html`…`a_17d.html` (each only `<!-- filled by Task N -->`); `workspace/checks/ch17_rev.py`.
- [ ] pack.json, cover (rows: Revision "The normal distribution" note "Year 12 Advanced · Ch 16"; Lessons 17A–17D with textbook titles and `Past papers: @@M17A@@`…`@@M17D@@`; Review), revision per the spec (boxes + one textbook example each, normal-curve SVGs, 6-question warm-up, full standard normal table page), a_rev answers, rev check reading the HTML (warm-up answers recomputed with `math.erf`; table values vs erf and vs ≥ 20 textbook values).
- [ ] Build; qa 0/0; MathJax scan; look at pages. Commit `Ch17: scaffold, cover, normal review` (stage only these files).

### Lesson task standard (Tasks 2–5)
For section S with textbook PDF pages P (answers 959–964):
- [ ] Render and read every teaching page of S (boxes, examples, notes) and the whole exercise with band headings.
- [ ] `l<S>.html` (replace placeholder) in the house lesson structure: concepts covering every box/method/warning; per concept Tutor demo, Your turn, Worked example(s) copying the textbook examples; Textbook homework verbatim with F/D/E bands (omissions per the spec's spreadsheet ruling or doubtful items, reported); Past-paper homework 15–22 marks per house rules and the spec's rulings.
- [ ] `a_<S>.html` (replace placeholder): ahead → Lesson Examples → Textbook Homework → ahead → Past-Paper Worked Solutions.
- [ ] Append chosen questions to `docs/pp_selected_ch17.md` under `## S` (re-read ALL `docs/pp_selected_*.md` and `docs/PAST_PAPERS_USED.md` first and before committing).
- [ ] `workspace/checks/ch17_<s>.py` reading every printed result from the HTML and recomputing (`math.comb`, `fractions.Fraction` for exact binomial probabilities, `math.erf` for Φ; table-lookup rounding as the textbook does, e.g. z to 2 d.p.); exit 1 on any failure.
- [ ] Build; qa 0/0; MathJax scan; look at every page added. Commit `Ch17: lesson <S>` (stage only your files).

