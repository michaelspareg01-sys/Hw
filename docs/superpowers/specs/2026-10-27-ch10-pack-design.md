# Spec: Year 12 Ext 1 pack "Chapter 10 Related Rates and Projectile Motion" (9E + 10A + 10B)

Brainstorm outcome. The owner's requirements were fixed in advance by `docs/HANDOVER_PROMPT.md` (owner-confirmed rules) and `docs/READFIRST-Y12.md` (house rules, overridden by the handover where they differ). This spec records those rules for this pack plus the design decisions already taken in the draft.

## Deliverables
Two PDFs, built with `workspace/build/build.py workspace/build/ch10 all` (run from `workspace/build/`; outputs land in the current directory as `lesson.pdf` and `answers.pdf`):
- `Year_12_Ext1_Ch10_Related_Rates_and_Projectile_Motion_Lesson_and_Homework.pdf`
- `Year_12_Ext1_Ch10_Related_Rates_and_Projectile_Motion_Homework_Answers.pdf`
No tutor-notes PDF.

## Scope and structure (fixed)
- Cover → Revision (short review of Advanced 9A–9C motion + warm-up) → Lesson 9E Related rates → Lesson 10A Projectile motion: the time equations → Lesson 10B Projectile motion: the equation of path → Chapter 10 review exercise (plus Ch 9 review Q18 ladder, related rates).
- Each lesson: Concepts (from the textbook teaching part, no omissions) → Tutor demo → Your turn → Worked example(s) to keep; Textbook homework banded Foundation / Development / Enrichment (from the textbook exercise, verbatim); Past-paper homework mini exam.
- Fragment files: `cover.html`, `revision.html`, `l09e.html`, `l10a.html`, `l10b.html` (lesson); `a_rev_9e.html`, `a_10a.html`, `a_10b.html` (answers). Figures: `workspace/build/ch10/figs.py` → `svg/*.svg`, inserted with `{{svg:name}}`.
- Placeholders still to fill: `@@PP9E@@`, `@@PP10A@@`, `@@PP10B@@` (lesson past-paper sets), `@@PPA9E@@`, `@@PPA10A@@`, `@@PPA10B@@` (answers), `@@M9E@@`, `@@M10A@@`, `@@M10B@@` (cover: "NN marks · NN min").

## Sources
- Textbook: `workspace/zip/Math Textbook CMS6 Ext1 Y12.pdf` (PDF page ≈ printed + 26). 9E = PDF 491–494; 10A = 506–513; 10B = 514–518; Ch 10 review = 519–520; Ch 9 review Q18 = 504. Textbook answers: 9E = PDF 919; 10A = 921 (right column); 10B = 921–922; Ch 10 review = 922; Ch 9 review = 920–921. Year 11 16A (related rates teaching) = `workspace/sources/CSM6_EXT1Y11_book.pdf` PDF 770–772.
- Past papers: `workspace/pp/Ext 1/<YEAR>/` 2020–2024. Candidate catalogue (pre-screened, page numbers, flags): `docs/pp_candidates_ch10.md`.
- Tools: `workspace/tools/render.py pdf page out.png [zoom] [y0frac y1frac]`, `renderclip.py`, `qa.py file.pdf` (flags raw LaTeX), `sheet.py file.pdf prefix [zoom] [first last]` (2-up contact sheets). Run Python on source PDFs with `python3 -I`.

## Global constraints (binding)
1. Past papers: **real school trial papers only** from `pp/Ext 1/2020`–`2024`. Never NEAP, PEM, TEC/Total Education, Bored of Studies, CSSA, Independent.
2. Never reuse a question listed in `docs/PAST_PAPERS_USED.md`, and never use the same question twice within this pack. Repeating a school is fine.
3. Each lesson's past-paper set is about a 30-minute mini exam, **15–22 marks**, good varied questions, accessible → demanding. Keep original marks.
4. Source label on every past-paper question in BOTH PDFs, format: `School name, year, paper title as printed, Qnumber(subpart)` (e.g. `Sydney Boys High School, 2020, Year 12 Term 3 Trial HSC, Mathematics Extension 1, Q13(a)`). Lesson: one brief hint under each question (a starting idea, not the answer). Answers: full worked solutions.
5. Fidelity: retain original wording, values, units, conditions, subpart dependencies and marks. Retyping is fine. Recreate needed diagrams accurately as SVG in `figs.py`. Do not extract a later part that depends on an omitted earlier part unless the earlier part is included or its result is supplied.
6. **Doubtful items:** if a textbook or past-paper item looks wrong, do NOT claim it is wrong and do NOT "correct" it. Quietly choose a different question instead.
7. Every answer solved independently and checked numerically (a Python check script committed under `workspace/checks/`). Compare with the school's own solution when the file has one; if they disagree, investigate; never copy an apparent error.
8. Methods must be within the taught Ext 1 course (no resisted motion / air resistance; no methods beyond 9E, 10A, 10B and their Advanced prerequisites).
9. HTML structure must copy the existing house patterns exactly: past-paper blocks as in `workspace/build/ch13/l13a.html` (`.pp`, `.pp-src` with `.pn` and `.mk`, `.pp-q`, `.pp-sub` with `.mk`, `.mc`, `.hint`, `{{work:NN}}`, and a `.pp-intro` line with time and marks), answer blocks as in `workspace/build/ch13/a_ab.html` (`{{ahead:Lesson … }}`, `.ans-sec`, `.ppa` with `.pp-src`).
10. Maths in MathJax `\( \)` / `\[ \]`. Vectors written `\tv{i}` (tilde underneath). Final PDFs must pass `qa.py` with 0 problems and every page must be visually checked: no overflow, no clipped equations, no orphaned headings.
11. Writing style for any new prose: plain, short sentences; avoid em dashes unless absolutely necessary.

## Decisions already taken (draft, commit 2a6a483)
- Chapter title "Chapter 10 Related Rates and Projectile Motion"; 9E is taught as a full lesson (Y11 16A review) with 3 concepts: chain rule for rates, eliminating a variable with geometry, rates of angles (plus the solids formula box from Y11 16A).
- Textbook homework includes Exercise 9E Q1–13 (Q14 reflection proof omitted as off-topic), all of 10A Q1–18, all of 10B Q1–12, Ch 10 review Q1–9 + Ch 9 review Q18.
- Answers list only items with a stated final answer (house style); "show that" items are omitted unless the textbook gives a result.
