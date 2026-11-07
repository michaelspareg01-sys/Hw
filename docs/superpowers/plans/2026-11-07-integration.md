# Integration (three parts) Implementation Plan

> Read `docs/superpowers/templates/implementer.md` first. Spec: `docs/superpowers/specs/2026-11-07-integration-design.md`; house rules: `docs/superpowers/specs/house-rules.md`. Style model: finished `workspace/build/ch17/` and checks `workspace/checks/ch17_*.py`.

### Task 0: Past-paper catalogue for integration
Sweep every school Ext 1 trial paper 2020–2024 in `workspace/pp/Ext 1/` (not NEAP/PEM/TEC/CSSA/Independent/BoS; excluded: "3U JRAHS.pdf" 2021 mock, Western 2020, Fort Street 2023, NSB 2024) for integration items (primitives, definite/indefinite integrals, areas, trapezoidal rule, reverse chain rule, exp/log/trig integrals, inverse trig derivatives and integrals, sin²/cos² integrals, substitution, volumes). Exclude differential equations (Ch 13) and probability density functions. Write `docs/pp_candidates_integration.md`: one row per (sub)part with file, question and solution pages, title as printed, Q and marks, what it asks, the earliest lesson tag that has all its methods, and flags: doubtful (with reason), ALREADY USED (in `docs/PAST_PAPERS_USED.md` or any `docs/pp_selected_*.md`), needs results from other parts. Per-lesson counts and marks at the top. Commit `Integration: past-paper catalogue`.

### Task 1/2/3: Scaffold, cover and revision for Part 1 / Part 2 / Part 3
Files: `workspace/build/intN/{pack.json,cover.html,revision.html,a_rev.html,figs.py}`, `svg/`, placeholders `l<sec>.html`/`a_<sec>.html` per lesson (`<!-- filled by Task … -->`); `workspace/checks/intN_rev.py`. Cover rows list each lesson with textbook title and `Past papers: @@MX@@`. Revision boxes per the spec + 5–6 question warm-up and answers. Build; qa 0/0; MathJax 0; look at pages. Commit `IntN: scaffold, cover, revision`.

### Lesson task standard (each lesson)
- [ ] Render and read every teaching page of the section and the whole exercise with band headings, and the answer pages.
- [ ] `l<sec>.html` (replace placeholder): concepts covering every box, derivation, method and warning, with no skipped lines; per concept Tutor demo (value-changed textbook example, full working), Your turn, Worked example(s) copying the textbook examples with every line; Textbook homework verbatim with F/D/E bands (omit only doubtful or later-method items, reported); Past-paper homework per spec and house rules (15–22 marks, or a reported shortfall with a timed-practice note).
- [ ] `a_<sec>.html`: ahead → Lesson Examples → Textbook Homework → ahead → Past-Paper Worked Solutions (full working).
- [ ] Append to `docs/pp_selected_intN.md` (re-read ALL pp_selected files and PAST_PAPERS_USED first and again before committing).
- [ ] `workspace/checks/intN_<sec>.py` reading every printed result from the HTML and recomputing with sympy (`integrate`, `diff`, exact values; numeric checks for trapezoidal estimates); exit 1 on failure.
- [ ] Build (flock); qa 0/0; MathJax 0; look at every page added. Commit `IntN: lesson <sec>`.

### Final tasks per part: Assemble, record, final QA, deliver
Fill `@@MX@@`; append the part's paragraph to `docs/PAST_PAPERS_USED.md` (do not change "Next:"); build; all checks; qa; MathJax; glyph-collision scan; look at EVERY page; copy to output with the spec names and `git add -f`. Commit `IntN: assemble, record, final QA`.
