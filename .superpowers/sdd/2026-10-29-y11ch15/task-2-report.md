# Task 2 report: Lesson 15A Binomial expansions and Pascal's triangle

Status after fix round 1: DONE. The past-paper set now has 17 marks, so house rule 8 no longer applies. The sections below describe the current state; the fix report is at the end.

Commit: `2a076cf Y11Ch15: lesson 15A` on `ch10-pack`, not pushed.

## What I built

### `workspace/build/y11ch15/l15a.html` (lesson, PDF pages 4–20 of 20)
- Lesson head (eyebrow, h2, focus).
- **Concept 1**, expansions of (1 + x)ⁿ and Pascal's triangle (l15a.html:6). It covers:
  - the definitions of a binomial and a binomial expansion;
  - the expansions of (1 + x)⁰ to (1 + x)⁴ in two rows with like terms in columns, with the boxed 1 + 3 = 4;
  - the n + 1 terms and inclusive counting;
  - Pascal's triangle as a table, rows 0–8, plus the equilateral layout as SVG `pascal_tri`;
  - Box 1, the three basic properties, with the explanation of the addition property;
  - a tip box on substituting into a row (brackets, powers of the number, alternating signs);
  - the short history note.
  - Tutor demo: (1+3a)⁴, (1−x)⁵, (1−½x)⁵. Your turn: (1+5a)³, (1−x)³, (1−⅓x)⁴. Worked example 1 is textbook Example 1.
- **Concept 2**, approximations (l15a.html:78). Demo: 1.01⁷ and 0.99⁵. Your turn: 1.02⁶ and 0.98⁴. Worked example 2 is textbook Example 2.
- **Concept 3**, terms in a product (l15a.html:103). Demo: (1+3/x)²(1−x)⁶. Your turn: (1+2/x)²(1−x)⁵. Worked example 3 is textbook Example 3.
- **Concept 4**, particular terms and ratio of coefficients (l15a.html:130). Demo: (1+2kx)⁵ with ratio 3:4. Your turn: (1+kx)⁶ with ratio 2:1. Worked example 4 is textbook Example 4.
- **Concept 5**, a trinomial (l15a.html:159). Demo: (1+x+x²)³. Your turn: (1+x−x²)³. Worked example 5 is textbook Example 5.
- **Textbook homework**, Exercise 15A verbatim (l15a.html:185):
  - F band: Q1–5. D band: Q6–17. E band: Q18–19. This is the textbook's banding.
  - Nothing omitted. No 15E-dependent or doubtful items.
- **Past-paper homework** (after the `Past papers` comment in l15a.html): 9 questions, 17 marks, 25 minutes, one hint each.

### `workspace/build/y11ch15/a_15a.html` (answers, PDF pages 2–4)
- `{{ahead}}` → Lesson Examples C1–C5 (tutor demo and your turn) → Textbook Homework → `{{ahead}}` → Past-Paper Homework, Worked Solutions.
- The textbook answers match the book's list: 2, 4, 6, 7, 8, 10–16, 18 and 19. Q19 includes the pyramid description.
- **One addition:** Q1 (rows 0–12 of the triangle) is given as a table. It is a final answer students need, although the book prints none. Remove it if you want strict parity with the book.

### Figures
- `figs.py` has a new `fig_15a()` (figs.py:84), called from `__main__`. It writes `svg/pascal_tri.svg`, the equilateral layout with 3, 1 → 4 marked.

### `workspace/checks/y11ch15_15a.py`
- It reads every printed answer by template and recomputes it with sympy (expansion by repeated multiplication, `coeff`, `solve`). It covers:
  - the C1–C5 answers;
  - the worked examples 1–5 in l15a.html;
  - every textbook answer, including all 13 triangle rows, built by the addition property and checked against `comb`;
  - all past-paper values.
- Decimal approximations use exact rationals, with a check that the dropped terms do not change the rounding.
- Structure checks: marks sum and time, numbering, source labels in both files, one hint each, and that the MC letter is the option equal to the expansion.
- It also checks the lesson's displayed Pascal table (rows 0–8) and the column expansions of (1 + x)² to (1 + x)⁴ against `comb` and `expand`. It would print a NOTE if the past-paper total were below 15; it no longer does.
- Mutation tested on a copy: 8 changed answer values and 1 changed lesson value. Each one fails with exit 1.

### `docs/pp_selected_y11ch15.md`
- Section `## 15A` added.

## Sources used
- **Textbook:** Y11 book PDF 741–747 (teaching pages, Examples 1–5, Exercise 15A with band headings). The answers are on PDF 944, rendered in halves at zoom 2; all 15A answers are on that page. I also looked at PDF 748 (15B start) to set the 15A/15B boundary.
- **Past papers** (each checked on the rendered question page, the cover and the school solution where one exists):

| PP | Paper (cover title as printed) | Q, marks | File | Question page → solution page |
|---|---|---|---|---|
| 1 | The King's School, 2021, Year 12 Alternative Higher School Certificate Trial Examination, Mathematics Extension 1 | Q2, 1 (MC) | `2021/3U Kings.pdf` | p2 → p13 (answer B) |
| 2 | Ascham School, 2020, Mathematics Extension 1 Trial HSC Examination | Q8, 1 (MC) | `2020/2020 Ascham.pdf` | p3 → p9 (handwritten, answer B, −34560) |
| 3 | North Sydney Boys High School, 2020, Year 12 Assessment Task 3, Mathematics Extension 1 | Q2, 1 (MC) | `2020/2020 NSB.pdf` | p2 → p13 (handwritten, answer B, a = 4) |
| 4 | Girraween High School, 2021, Trial Higher School Certificate Examination, Mathematics Extension 1 | Q2, 1 (MC) | `2021/3U Girraween.pdf` | p2 → p11 (handwritten, answer A, k = 5) |
| 5 | Moriah College, 2023, Trial Higher School Certificate Examination, Mathematics Extension 1 | Q9(d)(i)(ii), 1 + 2 = 3 | `2023/Moriah 3U 2023 Paper w_ Solutions.pdf` | p7 → p19 (handwritten, answer 8) |
| 6 | Sydney Grammar School, 2023, Trial Examination, Form VI Mathematics Extension 1 | Q13(a), 2 | `2023/Sydney Grammar 2023 3U.pdf` | p9 → `2023/Sydney Grammar 2023 3U Solutions.pdf` p6 (scan) |
| 7 | Girraween High School, 2023, Year 12 Trial Examination, Mathematics Extension 1 | Q16(a), 3 | `2023/Girraween 2023 3U.pdf` | p9 → p32 (handwritten, answer 160) |
| 8 | Abbotsleigh, 2021, Higher School Certificate Assessment Task 4, Mathematics Extension 1 | Q12(c), 2 | `2021/Abbotsleigh 2021.pdf` | p10 → no school solution |
| 9 | Normanhurst Boys High School, 2022, Year 12 Course Assessment Task 4 (Trial Examination), Mathematics Extension 1 | Q11(b), 3 | `2022/Normanhurst Boys 2022 3U Trials & Solutions.pdf` | p5 → p10 (answer 1215 = (6 2)3⁴) |

- **PP 8:** I solved it independently: the coefficient is 1080a². Sympy confirms it.
- **PP 5 and PP 7:** the printed part (ii) of PP 5 and the stem of PP 7 have no full stop. I kept them as printed.
- **Source labels:** the Ascham label matches the one used for Ascham 2020 Q7 in Ch 10, and the Normanhurst label matches Ch 14's.

## Past-paper choice
- **Method.** 15A teaches expansions of (1 + term)ⁿ from a row of the triangle: substitution, approximation, terms of products, coefficient ratios and trinomials. Every item here is worked that way: take out a factor so that the bracket starts with 1, then use the row. This follows the controller ruling in fix round 1. The direct (x + y)ⁿ method belongs to 15B, and the solutions no longer mention it.
- **Negative powers.** 15A's own teaching and exercise use negative powers at small n: Example 3, Ex 15A Q2(i)–(l), Q4(d), Q13(d), Q14 (the term independent of x) and Q15(b). So the constant-term items A13 and A14 (n = 6) fit 15A under the spec's ruling.
- **Rows taken:**
  - A1 Kings, A2 Abbotsleigh, A3 SGS, and A4 + B3 Moriah (both parts; B3 is no longer free for 15B);
  - from the 15A/15C rows: A5 Ascham, A7 NSB, A10 Girraween 2021, A13 Girraween 2023 and A14 NBHS 2022.
- **Duplicates.** A5 is used, so its duplicate A6 (Abbotsleigh 2024 Q4) must not be used elsewhere in the pack.
- **Left free for 15B/15C:** A8, A9, A11, A12 and A15. A11 and A12 share an expansion, so use at most one of them.
- **Order:** the four MCs, then Moriah (3), SGS (2), Girraween 2023 (3), Abbotsleigh (2) and NBHS (3). Total 17 marks, time 1.5 × 17 = 25.5 → 25 min.
- **Not used, as ruled:** no unprinted-title papers, no JRAHS mock, no Killara 2021 Q1, no Kings Q14(a)(i).
- **Reuse cross-check:** PAST_PAPERS_USED.md and all pp_selected files, re-read before choosing and before committing. Ch 14 has taken only 14A items, including NBHS 2022 Q11(a)(i), a different part of the paper. None of my nine items is used elsewhere.

## Omitted, rejected or noted
- **Textbook teaching typo (PDF 741):** the second line of the expansions is printed "(1 + x)² = 1 + x". I wrote (1 + x)¹ = 1 + x, because it is the teaching text, not a question.
- **History note:** the textbook names the 1527 author "Petrus Adrianus". I left out the name ("a 1527 book on business calculations"). I believe the usual attribution is Petrus Apianus, so I did not want to repeat a possible error.
- **Exercise 15A:** no doubtful items. Every printed answer was verified, including 16a (k = 5, with k = 0 excluded because the ratio is undefined) and 16b (k = −2 or 0).
- **Cover:** `cover.html` still has the placeholder `@@M15A@@`. I did not edit it, as the brief limits me to my placeholders. The value is now "17 marks · 25 min".

## Verification
- `python3 workspace/checks/y11ch15_15a.py` → "All OK" (see the fix report for the current count). Exit 0.
- Build: `cd workspace/build && python3 build.py y11ch15 all && mv lesson.pdf answers.pdf y11ch15/`.
- `qa.py`: lesson.pdf has 20 pages, 0 problems. answers.pdf has 4 pages, 0 problems.
- MathJax scan (PyMuPDF text for Double subscripts or superscripts, Undefined control sequence, Missing, Extra }, Misplaced, Math input error): 0 in both PDFs. I checked that no page is shrunk: the body font is 10.2pt on page 4.
- **Pages inspected:** lesson pages 4–20 and answers pages 2–4 as sheets, with zooms on the Pascal box, the figure and the answer fraction lines. Layout fixes along the way:
  - The column-aligned expansions use `alignedat`. An `array` with `@{}` was too wide and shrank the whole PDF.
  - The Pascal table is compact and the figure is tighter, so the box fits on page 4.
  - Worked example 3 was stacked because its right column overflowed.
  - Work boxes are sized so that lesson pages have at most about 10 mm free. The exception is page 11, the end of the lesson before the homework page break, with about 36 mm free.
  - Answer lines with fractions are padded, and Q11 and C4 parts are on separate lines.

## Files changed
- `workspace/build/y11ch15/l15a.html`, `a_15a.html`, `figs.py`, `svg/pascal_tri.svg`
- `workspace/checks/y11ch15_15a.py`
- `docs/pp_selected_y11ch15.md`

Scratch work is in `/tmp/claude-0/-home-user-Hw/33fce1a1-283b-5e23-bc89-9ac277c110f5/scratchpad/work/y11ch15-task2/`.

---

# Fix round 1

## What changed
1. **Past papers (Important).** The set now has 9 questions, 17 marks and 25 minutes. The new items are rows A5, A7, A10, A13 and A14, and the order runs from accessible to demanding. Details are in "Sources used" and "Past-paper choice" above.
   - Each new item was checked on its rendered question page, its cover and its school solution. Each has a full worked solution by the 15A method and new checks.
   - The `.pp-intro` line now reads 25 minutes and 17 marks.
   - The PP numbering changed: Moriah is now PP 5, SGS PP 6 and Abbotsleigh PP 8.
2. **Justification (Important).** `docs/pp_selected_y11ch15.md` `## 15A` has been rewritten with the method, the negative-power reasoning, the 9 rows, the A6 duplicate note and the rows left free. The report body above has been updated to match, and its rule-8 wording is gone.
3. **Parts on separate lines.** Q2, Q4, Q8, Q9, Q13 and Q14 now use `.parts one`. Q2 has a 2.6 mm row gap so its stacked fractions do not touch. All homework and past-paper work boxes were resized after checking the page breaks.
4. **Check script.** New checks cover:
   - the displayed Pascal table, rows 0–8: values against `comb` and `expand`, and the number of blank cells;
   - the three column expansions of (1 + x)² to (1 + x)⁴: the top row, the x row, the sum row and the header powers;
   - the boxed 1 + 3 = 4.
   - The converter now handles `\sqrt[n]{}` and `\dbinom`.
   - Mutation tests on a copy all fail with exit 1: table cell 56 → 57, a column-expansion coefficient, PP 7 answer 160 → 150, PP 4 letter A → B, PP 9 binomial 6C2 → 6C3, and the PP 2 term.
5. **Hints.** No hint now gives a step. Each one says "take out a factor so that the bracket starts with 1", plus at most a guiding question or a pointer to a worked example. The Moriah hint now points to Worked example 3 instead of saying "expand (2x−1)² first".
6. **Forward references.** "Lesson 15B gives a direct method" has been removed from the solutions; `grep 15B` now finds nothing in l15a.html or a_15a.html.
7. **Q1 and page 5.**
   - The Q1 work box is now 246 mm, a full page for rows 0–12.
   - The orphan paragraph about the two layouts is now inside the Pascal box. To make room, the box intro and the "n + 1 terms" paragraph are shorter, the table cells are tighter and the figure rows are tighter (dy 18, no overlap). The Pascal box ends page 4, and page 5 opens with the properties box. The tutor demo C1 box became 115 mm to fill page 5.

## Commands and results
- `python3 workspace/checks/y11ch15_15a.py` → All OK, 158 checks, exit 0. No rule-8 NOTE.
- `cd workspace/build && python3 build.py y11ch15 all && mv lesson.pdf answers.pdf y11ch15/` → lesson.pdf has 23 pages, answers.pdf has 5.
- `qa.py`: 0 problems on lesson.pdf and 0 on answers.pdf.
- MathJax error scan: 0 in both PDFs.
- Pages inspected:
  - lesson pages 4–5 and 12–23 (all the pages that changed), with zooms on the Pascal box and on Q2;
  - answers pages 2–5.
  - Free space at the page foot is at most 18 mm on every changed page.

## Files
- `workspace/build/y11ch15/l15a.html`, `a_15a.html`, `figs.py`, `svg/pascal_tri.svg`
- `workspace/checks/y11ch15_15a.py`
- `docs/pp_selected_y11ch15.md`

## Still open
- `cover.html` still has the `@@M15A@@` placeholder, which belongs to the controller. The value is "17 marks · 25 min".
