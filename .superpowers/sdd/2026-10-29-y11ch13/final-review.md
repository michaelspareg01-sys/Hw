# Final whole-pack review: Y11 Ext 1 Chapter 13 Discrete Probability Distributions

**Verdict: Approved. 0 Critical, 0 Important, 6 Minor (polish only).**

Reviewed: `output/Year_12_Ext1_Y11_Ch13_Discrete_Probability_Distributions_Lesson_and_Homework.pdf` (92 pp) and `..._Homework_Answers.pdf` (21 pp). Both are byte-identical to `workspace/build/y11ch13/lesson.pdf` and `answers.pdf` (checked with cmp). Source fragments at HEAD 593fb8d. `docs/` has no uncommitted changes (checked with git status), so the Ch 17 record I checked is the committed one (last commit ccbab56, 17C).

## Spec Compliance
- ✅ Structure: cover → Revision (Ch 12 probability, frequency tables, mean/SD, sigma notation, plus a 5-question warm-up) → 13A–13D → Chapter 13 review at the end of `l13d.html`. The textbook extension boxes are included and labelled as the book labels them: "Extension: proof of the alternative formula" (lesson p49) and "Extension: a correction factor for the sample variance" (p74). The 13D random-number tables are on p85–87.
- ✅ Footers, cover title (two balanced lines) and the one-line answers heading ("Chapter 13 Discrete Distributions - Homework Answers") match the spec and `pack.json`.
- ✅ **Cover rows** (`cover.html:8-11`) match each lesson:
  - 13A: 6 marks, 10 min (`l13a.html:275`; 1.5 × 6 = 9, rounds to 10).
  - 13B: "none · timed practice" (`l13b.html:223-224`, heading "timed practice").
  - 13C: 3 marks, 5 min (`l13c.html:242`; 4.5 rounds to 5).
  - 13D: 1 mark, 5 min (`l13d.html:343`; 1.5, given the 5-minute minimum).
- ✅ **Past papers.** There are 8 items in the lesson PDF and 8 worked solutions in the answers PDF. The `pp-src` labels are character-identical in the two (compared from the HTML): 13A PP1–4 (`a_13a.html:85-101`), 13C PP1–3 (`a_13c.html:130-147`), 13D PP1 (`a_13d.html:104`). 13B has no past-paper item, by ruling, and no answers heading for one. The lesson sends students to Ex 13B Q8, 9, 11 and 12, which all have answers.
- ✅ **No reuse.**
  - I checked each item against every line of `PAST_PAPERS_USED.md` outside the Y11 Ch 13 paragraph (the Y12 Ch 11, 12, 13 and 10 lines, and the Y11 Ch 14 and 15 lines) and against `pp_selected_ch10`, `_ch17`, `_y11ch14` and `_y11ch15.md`.
  - The only matches are different questions, or other parts of the same question:
    - BHHS23 Q1, Q7, Q12a/b/c, Q14b/c, Q11(c)(ii) and Q13(c)(i) are used elsewhere;
    - BHHS20 Q8 is in Ch 14;
    - Manly20 Q2 is in Ch 17;
    - JRAHS20 Q3, Q6, Q11(b), Q12(b) and Q13a/b/c are used elsewhere;
    - HAHS23 Q9, Q10, Q12(d) and Q13(c)(i) are used elsewhere;
    - BBHS24 Q6 and Q12(d) are used elsewhere.
  - Inside the pack, BHHS20 Q12(a)(i)(iv) is in 13A and Q12(a)(iii) in 13C. These are different subparts, and the 13C stem supplies a and b (house rule 2). BHHS23 Q11(c)(i) and Q13(c)(ii) are different questions.
  - No commercial or excluded papers are used.
- ✅ **Ch 13 record.** The `PAST_PAPERS_USED.md` line 6 lists exactly the 8 items in `pp_selected_y11ch13.md`: BHHS23 Q11c(i)/Q13c(ii), BHHS20 Q12a(i)(iii)(iv), Manly20 Q11a(iii), JRAHS20 Q1, HAHS23 Q8, BBHS24 Q2. Nothing is added and nothing is missing. "Manly" is in the key line.
- ✅ **Numbering and cross-references.**
  - Lesson letters 13A–13D are the same in the cover, the lesson heads and the answer headings.
  - Concepts are 1–5 / 1–3 / 1–3 / 1–4, and the answers have C1–C5 / C1–C3 / C1–C3 / C1–C4 to match.
  - The book box numbers run 1–10 across the chapter.
  - Worked examples are numbered 1–8 across the chapter (13A WE1–2, 13B WE3–4, 13C WE5–7, 13D WE8); unnumbered "From the text" examples follow the Ch 14 precedent.
  - Each cross-reference was checked against its target:
    - "Lesson 13A" (`l13b.html:8`, Ex 13B Q6);
    - "Worked example 3" (`l13b.html:96,137`);
    - "Worked example 2 of Lesson 13A" (`l13b.html:209`, Wulf);
    - "In Lesson 13B" (`l13c.html:13`);
    - "Worked example 5" (`l13c.html:69`);
    - "Worked example 7 below" (`l13c.html:123`);
    - "Worked example 3 of Lesson 13B" (`l13c.html:140`);
    - "Questions 13 and 14" (`l13c.html:125`);
    - "Worked example 8" (`l13d.html:82`);
    - "Question 10 of Exercise 13B" (`l13d.html:265`, difference of two dice);
    - "Question 12 of Exercise 13C" (`l13d.html:270`, uniform);
    - "Question 3 of Exercise 13B" (`l13b.html:69`);
    - answers 13C Q12(d): "Question 7" and "Worked examples 5 and 6".
  - Answer headings follow lesson order: Warm-up → 13A (Examples, Textbook, PP) → 13B (Examples, Textbook) → 13C (…, PP) → 13D (…, PP) → Chapter 13 Review last, matching the lesson PDF.
- ✅ **Consistency.**
  - Labels: every one reads "School, year, cover title, Mathematics Extension 1, Q…".
  - Hints: one per item, each a starting idea (all 8 read).
  - Bands: F/D/E in all four exercises; the review is unbanded, as in the book.
  - Money: always `\(\$\)` (no bare $ in any fragment), and 5-digit numbers take a thin space (24 500, 44 960).
  - "Var", "E" and p(x) notation is the same throughout.
  - Small style differences are listed under Minor.

## Strengths
- Answers are very clean. In about 75 independently re-solved answers I found no error. The silent fixes of book-key slips are all correct:
  - 13A Q8(d) "Snake Gully";
  - 13C Q2(a) xp(x) row 0.3, **1**, 0.3, 0.4;
  - 13D Q1(a) p(2) = **6/27** (the book prints 8/27).
- Past-paper fidelity spot-checked again against the source pages:
  - HAHS 2023 Q8 matches word for word, including the printed "5Var(X)".
  - BBHS 2024 Q2 matches its wording, options and A./B. style.
- Figures match their tables: the WE3 robbery graph, the answers' C2 pickpocket and thief graphs, and the Ex 13D Q1 graphs (8/27, 12/27, 6/27, 1/27).

## Issues

### Critical
None.

### Important
None.

### Minor
1. **"Section" wording left after the Lesson conversion.**
   - In `l13a.html:68` (lesson p7, "A word of warning"), "the calculations in the next two sections" means Lessons 13B and 13C.
   - Generic "this section" also appears in `l13b.html:16`, `l13b.html:162` (Ex 13B Q3, "In the theory for this section"), `l13c.html:123` ("at the start of this section") and `l13d.html:10`.
   - Fix: "next two lessons" / "this lesson". The meaning is clear as it stands.
2. **Apostrophe style.** `l13d.html` uses curly ’ (22 times); `l13a–c` and the answers use straight ' (about 20 times). It shows side by side in the past-paper notes: 13C "this lesson's ideas" (p62) against 13D "this lesson’s ideas" (p87). Fix: pick one style.
3. **MC answer style.**
   - 13C answers write "Answer (D)." / "Answer (B)." (`a_13c.html`).
   - 13D writes "Answer B." (`a_13d.html`).
   - Each follows its paper's printed option style, (A) for JRAHS/HAHS and A. for BBHS, so this is defensible. Note only.
4. **13A past-paper intro has no "more timed practice" pointer.** 13B, 13C and 13D each name textbook questions for extra timed practice; 13A (6 marks, 10 min, also a rule-8 shortfall) does not (`l13a.html:276`). Optional: add one line, e.g. Ex 13A Q8 and Q10 in 15 minutes.
5. **Known layout, unchanged.**
   - The WE3 graph's stacked y-axis fractions on lesson p33 (5/20 … 1/20) nearly touch (0.67 pt). They are legible at print size.
   - The faint page-straddle specks at the foot of lesson p67 and p90 (Task 6 Concern 1) are not visible on my renders at zoom 2.5.
   - Generous boxes (13A PP4, 170 mm) and the roughly 25%-blank pages are as listed in the Task 6 report.
6. **13D cover time.** 1 mark × 1.5 = 1.5 min is shown as 5 min. This is a sensible minimum and consistent with the lesson's pp-intro. Note only.

## Checks run
- `workspace/checks/y11ch13_rev.py`, `_13a.py`, `_13b.py`, `_13c.py`, `_13d.py`: all rc=0. Results: 97 values / 192 / 141 / 173 / 165 OK, 0 failures.
- `qa.py` on both output PDFs: 92 pages, 0 problems; 21 pages, 0 problems.
- MathJax error scan (PyMuPDF get_text for Double subscripts / Double superscripts / Undefined control sequence / Missing / Extra } / Misplaced / Math input error): lesson 0, answers 0.
- cmp of the output PDFs against the build PDFs: identical.
- **Glyph-collision scan** (the Ch 14 Task 8 method; `collide.py` copied to scratch):
  - Lesson hits: p33, p34, p46, p48, p51, p57, p64, p75, p78, p87.
  - Answers hits: p1, p5, p7, p16, p21.
  - These are the same hits the Task 6 report lists, and the two real near-collisions it fixed (lesson p89, answers p15) are gone.
  - I viewed p33, p64, answers p5, p7 and p21 at zoom 2.2–3. All are false positives (box borders, hats, tree labels, stacked axis fractions not touching).
- **Every page viewed** on 4-up contact sheets at zoom 0.6: 23 sheets for the lesson, 6 for the answers. Close renders: lesson p33, p64, p67 foot, p88, p89, p90 foot; answers p5, p7, p9, p19, p21.
  - No clipped maths, overlap, stranded heading, blank page, stray mark or mismatched figure found.
  - Box splits across pages (e.g. p67/p68) are clean.
- **Textbook answers** compared with the book key (PDF 933–938, text layer) for:
  - 13A: Q4, 8, 9, 10, 11, 12, 14, 15, 16;
  - 13B: Q1, 2, 4–12, 14;
  - 13C: Q1–12;
  - 13D: Q1, 2, 4(c), 7(a);
  - the review: Q1–8 and Q11–12.
- **Independently re-solved** (about 75):
  - warm-up Q1–5;
  - 13A: C1 (demo and your turn), Ex Q4(c), 9(a–e), 10(b, c), 11, 12(b), 14, 15(a, b), 16(a, b), 8(c), PP1–4;
  - 13B: C2 (both), Ex Q1(c), 2, 4, 5, 6, 7, 9, 10(d), 11, 12;
  - 13C: C1–C3 (both each), Ex Q1, 3(a–d), 4(i–iv), 6, 7, 8, 9, 10(a, c, d), 11, PP1–3;
  - 13D: C1–C4 (both each), Ex Q1(a, b), 2(a), 4(c)(iii), 7(a), WE8 exoplanets, rainy-days WE and correction, mice WE, PP1;
  - review Q2, 4, 5, 6, 7, 8, 11, 12(a).
  - All agree with the pack.
- Book chapter review (PDF 685–687) compared with the pack review: all 12 questions are present with the same values.
- Past-paper sources re-rendered: HAHS 2023 p3 (Q8) and BBHS 2024 p2 (Q2).
- Reuse greps over `PAST_PAPERS_USED.md` and all five `pp_selected_*.md` files, for every school and question in the pack.

## Assessment
**Pack quality:** Approved
**Reasoning:** Every past-paper item has an identically labelled worked solution, there is no reuse inside or outside the pack, the record matches the selection file, all checks pass, and about 75 re-solved answers are correct. What remains is wording and style polish that does not affect a student's use of the pack.
