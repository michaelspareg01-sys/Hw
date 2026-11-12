# Year 10 Trigonometry part 2 and Circle Geometry: implementation plan

> Read these first:
> - `docs/superpowers/templates/implementer.md`
> - the spec: `docs/superpowers/specs/2026-11-12-y10-trig-circles-design.md`
> - the house rules: `docs/superpowers/specs/house-rules.md`
>
> Style model: the finished `workspace/build/int1/` (see `l5e.html` and `l5i.html` for the tip conventions) and its checks, `workspace/checks/int1_*.py`.

### Task S-trig / S-circ: scaffold, cover and revision
Create these files:
- `workspace/build/<dir>/` with `pack.json` (Y10 header and footers, as the spec gives), `cover.html`, `revision.html`, `a_rev.html` and `figs.py`;
- the `svg/` folder;
- the placeholder files `l<lesson>.html` and `a_<lesson>.html`;
- `workspace/checks/<dir>_rev.py`.

Cover rows list each lesson with "Past papers: @@MX@@". Build the pack; qa must report 0 problems in both PDFs and MathJax 0; look at every page.

Commit `Y10 <pack>: scaffold, cover, revision`.

### Lesson task standard (T1, T2, T3, C1, C2, C3)
- [ ] Render and read every teaching page, example and exercise for the lesson in its sources, and their answers.
- [ ] Write `l<lesson>.html`:
  - concepts, each with its Tutor demo, Your turn and Worked example(s) to keep;
  - the four-band homework (Easy / Medium / Hard from the sources, plus past-paper items where they help the spread);
  - the past-paper mini exam, 15–22 marks, or a reported shortfall with a timed-practice note.
- [ ] Write `a_<lesson>.html` in this order: ahead → Lesson Examples → Homework answers by band (past-paper items get full worked solutions) → ahead → Past-Paper Worked Solutions.
- [ ] Record every past-paper item used in `docs/pp_selected_<dir>.md`. Re-read both y10 pp_selected files first, and again before committing.
- [ ] Write `workspace/checks/<dir>_<lesson>.py`. It reads every printed numeric result from the HTML and recomputes it with math or sympy (angles, lengths, areas, both ambiguous-case solutions, equation solution sets). For geometry, recompute lengths and angles from the given data. Exit 1 on any failure.
- [ ] Build (flock). Then:
  - qa reports 0 problems in both PDFs;
  - MathJax reports 0;
  - some span measures exactly 11.3 pt in each PDF;
  - `svg_overlap.py` reports 0;
  - look at every page added.

  Commit `Y10 <pack>: lesson <lesson>`.

### Final task per pack: assemble, record, final QA, deliver
1. Fill in `@@MX@@`.
2. Append the pack's paragraph to `docs/PAST_PAPERS_USED.md`.
3. Build and run every check.
4. Look at every page.
5. Copy the PDFs to `output/` under the spec's names and `git add -f` them.

Commit `Y10 <pack>: assemble, record, final QA`. A final whole-pack review follows.
