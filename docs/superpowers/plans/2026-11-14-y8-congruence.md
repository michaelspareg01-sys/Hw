# Year 8 Congruence: implementation plan

> Read these first:
> - `docs/superpowers/templates/implementer.md`
> - the spec: `docs/superpowers/specs/2026-11-14-y8-congruence-design.md`
> - the house rules: `docs/superpowers/specs/house-rules.md`
>
> Style model: `workspace/build/y10circ/` and its checks.

### Task 0: Catalogue past-paper congruence questions
Look at every page of every paper in:
- `workspace/pp/Y9/` (21 papers, 2020–2025);
- `workspace/pp/Y10/` (40 papers).

Some of these papers are scanned, so view or OCR them; don't rely on the text layer.

Write `docs/pp_candidates_y8cong.md` with one row per question part. Each row gives:
- file;
- question page and solution page;
- school and year;
- the cover title as printed;
- the question number and marks;
- what the part asks;
- a lesson tag: L1 (congruent figures), L2 (tests, statements) or L3 (proofs and quadrilateral properties);
- flags: doubtful, wrong solution, needs similarity or untaught methods, already used in any `pp_selected_*.md`.

Put the per-lesson counts and marks at the top.

Commit `Y8 congruence: past-paper catalogue`.

### Task S: Scaffold, cover and revision page
Commit `Y8 congruence: scaffold, cover, revision`.

### Lessons L1, L2, L3
Follow the same lesson standard as the Year 10 packs.

Commit each lesson as `Y8 congruence: lesson Ln`.

### Assemble
1. Fill in the cover.
2. Append a line to `docs/PAST_PAPERS_USED.md`.
3. Build, then run every check.
4. Look at every page.
5. Copy the PDFs to `output/` and `git add -f` them.

Commit `Y8 congruence: assemble, record, final QA`. A final whole-pack review follows.
