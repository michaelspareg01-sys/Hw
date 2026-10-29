# Task 3 report: Lesson 15B Further binomial expansions

Status: DONE_WITH_CONCERNS. The concerns are minor and listed at the end. The past-paper set has 16 marks and runs 25 minutes.

Commit: `f6bb8b3 Y11Ch15: lesson 15B` on `ch10-pack`, not pushed.

## What I built

### `workspace/build/y11ch15/l15b.html` (lesson PDF pages 24–39 of 39)
- The lesson head has the eyebrow, h2 and focus line. The focus line covers the textbook's opening sentence: the symmetries are more obvious.
- **Concept 1, expansions of (x + y)ⁿ** (l15b.html:5). It covers:
  - the language box (monomial, binomial, trinomials in several variables);
  - the expansions of (x + y)² to (x + y)⁴ in two rows, with like terms in columns and the boxed 1 + 3 = 4 (`alignedat`, the same layout as 15A);
  - the "First" and "Secondly" notes and the "more generally" note;
  - Box 2 and the word "homogeneous of degree n";
  - a tip box, "Using the general expansion": brackets, the falling and rising powers, alternating signs.
  - Tutor demo: (3 − 2x)⁴ and (2x + ½a)⁵. Your turn: (2 − 5x)³ and (3x + ⅓a)⁴. Worked example 6 (l15b.html:42) is textbook Example 6, with full working.
- **Concept 2, particular terms with negative powers** (l15b.html:55). Tutor demo: (x + 3x⁻²)⁶, the constant term and the term in x⁻³. Your turn: (x + 2x⁻¹)⁴, the constant term and the term in x⁻². Worked example 7 (l15b.html:72) is textbook Example 7.
- **Concept 3, a term in a product** (l15b.html:89). Tutor demo: (3 − 2x)⁶ and then (4 + x)(3 − 2x)⁶. Your turn: (2 − x)⁵ and then (3 + x)(2 − x)⁵. Worked example 8 (l15b.html:101) is textbook Example 8.
- **Textbook homework** (l15b.html:110) is Exercise 15B, Q1–16, copied word for word.
  - The bands follow the textbook: Foundation Q1–4, Development Q5–13, Enrichment Q14–16.
  - Every question's parts are on separate lines (`.parts one`). The Q11 sub-parts are padded lines, so the stacked fractions do not touch.
  - Nothing is omitted. No question depends on 15E.
- **Past-paper homework** (l15b.html:148): 9 questions, 16 marks, 25 minutes, one hint per question.
  - Each hint is a starting idea or a pointer to a worked example, never a step.
- I searched for forward references (15C, 15D, 15E, "binomial theorem", "general term", "later"). There are none.

### `workspace/build/y11ch15/a_15b.html` (answers PDF pages 6–9)
- The order is `{{ahead}}`, then Lesson Examples C1–C3, then Textbook Homework, then `{{ahead}}`, then Past-Paper Homework – Worked Solutions.
- **Textbook answers.** They match the book's list on PDF 944–945: 1–7, 8(b)(c), 9 (7/2), 10, 11, 12, 14, 15 and 16.
  - The book prints no answer for 5(b), 8(a) and 13, which are "prove" and "show" items, so they are left out.
  - The Q16 answer gives the book's text and a recreated Sierpinski figure.
- **Past-paper solutions.** Each uses only the 15B method: a row of Pascal's triangle applied to (x + y)ⁿ.
  - For negative powers, the power of x steps by a fixed amount from term to term, as in Example 7.
  - For products, the expansion is taken only as far as needed, as in Example 8.
  - No nCr notation and no general term are used. Each MC solution explains the choice.

### Figures
- `figs.py` has a new `fig_15b()` (figs.py:107). It writes `svg/sierpinski.svg`, the first three stages of the gasket. `__main__` now calls it. `fig_15a` is unchanged, and `pascal_tri.svg` regenerates byte-identical.

### `workspace/checks/y11ch15_15b.py`
- It has 161 checks. Each one reads a printed value by template. A template must match exactly once, and a missing match is a loud failure.
- Each value is compared with an independent sympy computation, using expansion by repeated multiplication, `coeff`, `solve` and `limit`.
- **Lesson.** It checks:
  - the three column expansions: each row against x(x+y)ⁿ⁻¹, y(x+y)ⁿ⁻¹ and (x+y)ⁿ; the number of terms; that every term has degree n; and the boxed 1 + 3 = 4;
  - the tip-box example;
  - every line of worked examples 6–8;
  - the results printed inside textbook questions: Q3(a)–(d) as stated, Q5(b), Q8(a) = 20608, the Q9 identity and the Q13 ratio 10:3;
  - the demo and your-turn questions;
  - the MC options.
- **Answers.** It checks:
  - all of C1–C3, including each side of every "=" chain;
  - every textbook answer;
  - every past-paper line and value, including the listed power sequences, the MC letter (the one option equal to the computed value) and 8a = 5b.
- **Pascal rows.** Every "Row n is …" printed in either file is compared with `math.comb`: 4 in the lesson and 9 in the answers.
- **Structure.** It checks:
  - the marks sum, which must be 15–22;
  - time = 1.5 × marks, rounded to 5 minutes;
  - the numbering;
  - identical source labels in both files;
  - one hint each;
  - the set of answer blocks, and that Q1–16 are present.
- **Mutation test.** I ran 20 mutations on a scratch copy, through `Y11CH15_SRC`:
  - answers: C1, C2, Q1(d), Q6(c), Q10(b), Q14(b), PP7, PP8, the PP1 letter, a row-12 entry and the PP5 power list;
  - lesson: two column-expansion rows, WE6, WE7(b), WE8, a PP1 option, the Q8(a) statement, the intro marks and a WE7 coefficient.
- Every mutation failed with exit 1.

### `docs/pp_selected_y11ch15.md`
- I added a `## 15B` section. It has the method, the 9 items with file, question page and solution page, the rows not taken, and the rows left free for 15C.

## Source pages used
- **Textbook** (Y11 book): PDF 748–749 (teaching, Box 2, Examples 6–8) and PDF 750–751 (Exercise 15B with band headings), rendered at zoom 1.6 and 2.2.
- **Answers:** PDF 944 (right column, 15B Q1–2) and PDF 945 (Q3–16), rendered in quarters at zoom 2.4. I checked every answer with sympy, and all agree with the book.
- **Past papers.** I checked each question page, the cover title and the school solution where one exists, on the rendered page. All paths are under `workspace/pp/Ext 1/`.

| PP | Label (school, year, title as printed on the cover, Q) | Marks | File | Question → solution |
|---|---|---|---|---|
| 1 | Sydney Grammar School, 2021, Trial Examination, Form VI Mathematics Extension 1, Q2 (MC) | 1 | `2021/3U SGS.pdf` | p2 → none (37500, C) |
| 2 | Hurlstone Agricultural High School, 2021, Higher School Certificate Assessment Task 4, Mathematics Extension 1, Q2 (MC) | 1 | `2021/3U HAHS.pdf` | p2 → none (30, B) |
| 3 | Hurlstone Agricultural High School, 2023, Higher School Certificate Trial Examination, Mathematics Extension 1, Q9 (MC) | 1 | `2023/Hurlstone 2023 3U.pdf` | p4 → p19 (B, 40) |
| 4 | Sydney Girls High School, 2023, Trial Higher School Certificate Examination, Mathematics Extension 1, Q11(c) | 2 | `2023/SGHS 2023 3U.pdf` | p8 → p23 (60) |
| 5 | Knox Grammar School, 2023, Higher School Certificate Trial Examination, Mathematics Extension 1, Q11(a) | 2 | `2023/Knox 2023 3U.pdf` | p8 → p17 (960) |
| 6 | Ascham School, 2023, Year 12 Trial Examination, Mathematics Extension 1, Q12(b) | 2 | `2023/Ascham 2023 3U.pdf` | p8 → p19 (2403) |
| 7 | Pymble Ladies' College, 2023, Mathematics Extension 1 HSC Trial Examination Term 3, Q13(a) | 2 | `2023/PLC 2023 3U.pdf` | p10 → none (9120) |
| 8 | St Aloysius' College, 2024, Trial Higher School Certificate Examination, Mathematics Extension 1, Q14(c) | 2 | `2024/St Aloysius_ College 2024.pdf` | p11 → none (a/b = 5/8) |
| 9 | James Ruse Agricultural High School, 2023, Year 12 Trial HSC Examination, Mathematics Extension 1, Q15(b) | 3 | `2023/Ruse 2023 3U.pdf` | p9 → p24 (a = ±3) |

- **Labels.** The labels for HAHS 2021 and 2023, SGHS 2023, Knox 2023 and Ascham 2023 match the ones already used in Ch 10 and Ch 14. The covers I checked were SGS 2021, HAHS 2021, Knox 2023, PLC 2023, St Aloysius' 2024 and James Ruse 2023.
- **Items without a school solution.** PP 1, 2, 7 and 8 have none. I solved each one independently and checked it with sympy.

## Past-paper choice
- **Rows taken:**
  - 15B rows B1, B4 and B5;
  - the rows left free by 15A: A8, A9, A15 and A12 (not A11, which has the same expansion; A11 is now barred);
  - to reach 15 marks, two 15C rows that fit 15B's Pascal method: C21 (n = 10) and C22 (n = 8). Both are neg-power rows, and 15C keeps about 18 of them plus every positive-power row (C1–C5, B2, B6).
- **Not taken:**
  - B2: its part (i), the coefficient of xᵏ, is nCr work. Splitting off (ii) would need nCr in the stem.
  - B6: its options are in nCr form for a general n.
  - B3: already used in 15A.
  - B7: not a binomial expansion.
  - A6: barred.
- **Order:** three MCs (1 mark each), then four 2-mark items building up to products with unknowns, then the 3-mark "find a". The total is 16 marks, so 1.5 × 16 = 24, which rounds to 25 minutes.
- **Reuse cross-check.** I re-read `PAST_PAPERS_USED.md` and every `pp_selected_*.md` (ch10, y11ch14, y11ch15) before choosing and again before committing. None of the nine items appears in them. The Ascham 2023 Q12(e) parts in Ch 14, PLC 2023 Q14(a) in Ch 13 and HAHS 2023 Q12(d) in Ch 14 are different questions.
- **Controller rulings.** No paper with an unprinted title, no JRAHS 2021 mock, and neither of the two flagged items is used.

## Omitted, doubtful or noted
- **Exercise 15B Q10.** The textbook prints "correct to to five decimal places" in both parts, a doubled word. I printed "correct to five decimal places". The maths is unchanged and no claim of error is printed, but the controller may prefer the literal text.
- **HAHS 2021 Q2.** Option D is printed "D 60" without the full stop. I showed it as "D." to match the other options.
- **St Aloysius' Q14(c).** "provided neither a or b are zero" is kept exactly as printed.
- **James Ruse solution.** The school solution writes "5013" for 5103 in one line but reaches a⁶ = 729. This affects the school's solution only, not our material.
- No doubtful textbook items were found. Every book answer for 15B is correct, including Q12, where a = 0 is excluded because the ratio is undefined.

## Verification
- `python3 workspace/checks/y11ch15_15b.py` → All OK, 161 checks, exit 0. `python3 workspace/checks/y11ch15_15a.py` → All OK, still.
- Build: `cd workspace/build && python3 build.py y11ch15 all && mv lesson.pdf answers.pdf y11ch15/`. lesson.pdf has 39 pages and answers.pdf has 9.
- `qa.py`: 0 problems on lesson.pdf and 0 on answers.pdf.
- MathJax scan (PyMuPDF text): 0 hits in both PDFs.
- **Pages inspected:**
  - lesson pages 24–39, as sheets at zoom 0.95, with zooms on the column expansions (p24), Q11 (p34) and the PP pages;
  - answers pages 6–9, with zooms on PP 1–7.
- **Layout fixes along the way:**
  - The Q11 stacked fractions overlapped, so each sub-part is now a padded line.
  - Answer paragraphs with inline \dfrac have extra line height.
  - The work boxes were resized so that every lesson page has at most 15 mm free above the frame (measured). Page 24 has about 15 mm, because the tip box does not fit there.
  - PP 3 was moved onto the intro page.
- The answers page 7 ends after Q16 with white space, because the PP worked solutions start on a new `{{ahead}}` page. 15A has the same pattern.

## Files changed
- `workspace/build/y11ch15/l15b.html` and `a_15b.html`, which replace the placeholders
- `workspace/build/y11ch15/figs.py` (adds `fig_15b`) and the new `svg/sierpinski.svg`
- `workspace/checks/y11ch15_15b.py` (new)
- `docs/pp_selected_y11ch15.md` (adds `## 15B`)

Scratch work is in `/tmp/claude-0/-home-user-Hw/33fce1a1-283b-5e23-bc89-9ac277c110f5/scratchpad/work/y11ch15-t3/`.

## Concerns
1. The Q10 doubled word was changed silently, as described above.
2. Two 15C rows (C21 and C22) were used to reach 15 marks. The only clean rows tagged for 15B or left free gave 11 marks.
3. `cover.html` still has the controller's `@@M15B@@` placeholder. I did not edit it. The value is "16 marks · 25 min".
