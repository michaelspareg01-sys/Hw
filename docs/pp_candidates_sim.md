# Simultaneous equations (Y9/Y10, linear): past-paper candidates

Source folders: `workspace/pp/Y9/` (21 papers) and `workspace/pp/Y10/` (40 papers), 2254 pages in all. Spec: `docs/superpowers/specs/2026-11-16-simultaneous-design.md`.

**Method.** The question section of all 61 files (1176 pages, covers and formula sheets included) was rendered with PyMuPDF and read visually in 12-up contact sheets (4 × 3). Every candidate page, and every candidate's solution page, was then re-rendered at reading size and read. As a second net, the text layer of all 2254 pages, and a tesseract OCR of the 780 pages with no text layer, were searched for: simultan, intersect, meet, concurrent, pair of equations, elimination, substitution, satisfy, two linear equations on one page, and word-problem phrasing (tickets, ages, years ago, twice, three times, total of $, altogether). Every hit was resolved. Solution sections were read wherever they belong to a listed or "related" item; the other solution pages were covered by the text and OCR search only. Page numbers are 1-based PDF page indices, not printed page numbers. Every answer below was re-solved independently (sympy, all 47 pairs agree with the printed answers or keys).

**Lesson tags** (spec "Lessons").
- L1 = the graphical method and substitution: a solution as the point of intersection, reading or choosing a graph, checking a solution, items that say "substitution" or have one equation already in the form y = ... or x = ....
- L2 = elimination, or "any method" algebra on a given pair, including pairs hidden inside index or surd equations.
- L3 = word problems: define two pronumerals, form two equations, solve, answer in words.

**Flags.**
- DOUBTFUL: the question itself is unsound (reason given).
- WRONG SOLUTION: the printed solution is wrong. None found.
- SOLUTION SLIP: a typo in the printed working, but the printed answer is right.
- NO SOLUTIONS: the file has no solution for the item (solved independently here).
- DEPENDS ON: the part needs an earlier part (the needed result is named, so a stem can supply it).
- EXCLUDED: Sydney Boys 2025 (either year). No Sydney Boys 2025 row qualified; see "Related".
- ALREADY USED: the item is in a `docs/pp_selected_*.md` file. None of the 51 rows is (all 11 selection files checked on 16 Nov). Note: `pp_selected_y10trig.md` uses "Sydney Grammar School, 2020, Q6(c)(i)–(ii)" from the **Year 10** (Form IV) paper; sim-17/18 are Q6(c)(i)–(ii) of the **Year 9** (Form III) paper, a different question, so labels must carry the cover title.
- Other notes: MARKS NOT PRINTED (Sydney Grammar 2022 prints only question totals; marks inferred from the solution ticks), NEEDS INDEX LAWS / HIDDEN PAIR (the linear pair appears only after index or surd work), ACT SCHOOL (Canberra Grammar; earlier packs set it aside as non-NSW).

## Totals

| Tag | Rows | Marks | Rows without DOUBTFUL / WRONG / EXCLUDED / USED | Marks | Of those, with a school solution |
|---|---|---|---|---|---|
| L1 | 12 | 21 | 12 | 21 | 12 rows, 21 marks |
| L2 | 28 | 63 | 27 | 60 | 24 rows, 53 marks |
| L3 | 11 | 27 | 11 | 27 | 11 rows, 27 marks |
| **All** | **51** | **111** | **50** | **108** | **47 rows, 101 marks** |

- DOUBTFUL: 1 (sim-05, Normanhurst Boys 2025 Q11(c), 3 marks, L2).
- WRONG SOLUTION: 0. SOLUTION SLIP: 3 (sim-01, sim-08, sim-12; answers right).
- NO SOLUTIONS: 3 rows, 7 marks, all L2 (sim-36 James Ruse 2024, sim-46 Scots 2020, sim-47 Scots 2021).
- DEPENDS ON another part: 5 rows (sim-04, sim-12, sim-13, sim-22, sim-33); each needs only an equation or pair that can be put in the stem.
- MARKS NOT PRINTED: 5 rows (sim-19 to sim-23, Sydney Grammar 2022: 2 + 3 + 1 + 2 + 2 inferred) and 2 rows whose marks appear only on the solutions (sim-17, sim-18: "[2]" each).
- HIDDEN PAIR (index or surd work first): sim-05 (doubtful), sim-16, sim-23, sim-36.
- ACT SCHOOL: sim-33 (3 marks, L1).
- Each tag reaches the 15–22 mark mini-exam range with clean, solved items (L1 21, L2 53, L3 27).

## Sydney Boys 2025 covers
- **Year 10** (`Y10/Sydney Boys 2025 ...pdf`, p1, image only): the cover's "PUBLISHER'S NOTES" say "This is a recreation of the Sydney Boys High School 2025 Year 10 Stage 5 Yearly. This is not the official document." No linear simultaneous item; its related items are listed below as EXCLUDED.
- **Year 9** (`Y9/Sydney Boys 2025 ...pdf`): excluded as the brief directs. No linear simultaneous item; one related item is listed below as EXCLUDED.

## Files and scan status

"Scanned" means no text layer: those pages were read visually, and OCR was used only as a search aid. Fully scanned files: Y9 Baulkham Hills 2020, Y9 Sydney Tech 2023, Y10 Girraween 2020, Y10 Girraween 2022, Y10 North Sydney Boys 2021, Y10 North Sydney Boys 2022, Y10 Sydney Tech 2020; Y10 Baulkham Hills 2020 is scanned except p30; the Y10 Sydney Boys 2025 question pages (p1–27) are scanned. No file was unreadable.

| Folder | File | Pages | Scan status | Rows |
|---|---|---|---|---|
| Y9 | Baulkham Hills 2020 | 8 | FULLY SCANNED (8 pp); NO SOLUTIONS | 0 |
| Y9 | Hornsby Girls 2021 | 10 | 1 of 10 pp scanned (p10); NO SOLUTIONS | 0 |
| Y9 | Kings 2022 | 42 | text | 0 |
| Y9 | Normanhurst Boys 2020 | 22 | text | 2 (sim-01 to sim-02) |
| Y9 | Normanhurst Boys 2025 | 38 | text | 3 (sim-03 to sim-05) |
| Y9 | North Sydney Boys 2020 | 40 | 20 of 40 pp scanned (p21-40) | 1 (sim-06) |
| Y9 | Penrith 2022 | 28 | 14 of 28 pp scanned (p15-28) | 0 |
| Y9 | St George Girls 2024 | 22 | text | 2 (sim-07 to sim-08) |
| Y9 | Sydney Boys 2020 | 47 | 8 of 47 pp scanned (p35-38, 44-47) | 3 (sim-09 to sim-11) |
| Y9 | Sydney Boys 2022 | 74 | 7 of 74 pp scanned (p12, 67, 70-74) | 1 (sim-12) |
| Y9 | Sydney Boys 2023 | 56 | text | 2 (sim-13 to sim-14) |
| Y9 | Sydney Boys 2024 | 57 | text | 2 (sim-15 to sim-16) |
| Y9 | Sydney Boys 2025 | 49 | text | 0 |
| Y9 | Sydney Grammar 2020 | 26 | 1 of 26 pp scanned (p12) | 2 (sim-17 to sim-18) |
| Y9 | Sydney Grammar 2022 | 32 | 7 of 32 pp scanned (p12, 18, 23, 26-29) | 5 (sim-19 to sim-23) |
| Y9 | Sydney Grammar 2023 | 30 | 21 of 30 pp scanned (p10-30) | 2 (sim-24 to sim-25) |
| Y9 | Sydney Grammar 2024 | 17 | 2 of 17 pp scanned (p11-12) | 3 (sim-26 to sim-28) |
| Y9 | Sydney Grammar 2025 | 30 | 19 of 30 pp scanned (p11-12, 14-30) | 4 (sim-29 to sim-32) |
| Y9 | Sydney Tech 2023 | 17 | FULLY SCANNED (17 pp) | 0 |
| Y9 | Sydney Tech 2024 | 21 | 8 of 21 pp scanned (p14-21) | 0 |
| Y9 | Sydney Tech 2025 | 29 | 13 of 29 pp scanned (p17-29) | 0 |
| Y10 | Baulkham Hills 2020 | 33 | 32 of 33 pp scanned (p1-29, 31-33) | 0 |
| Y10 | Canberra Grammar 2024 | 47 | 24 of 47 pp scanned (p23-24, 26-47) | 1 (sim-33) |
| Y10 | Fort St 2020 | 35 | 18 of 35 pp scanned (p18-35) | 0 |
| Y10 | Fort St 2021 | 39 | 20 of 39 pp scanned (p20-39) | 0 |
| Y10 | Fort St 2022 | 31 | 16 of 31 pp scanned (p16-31) | 0 |
| Y10 | Fort St 2023 | 38 | 3 of 38 pp scanned (p20, 31, 38) | 0 |
| Y10 | Girraween 2020 | 27 | FULLY SCANNED (27 pp) | 1 (sim-34) |
| Y10 | Girraween 2022 | 48 | FULLY SCANNED (48 pp) | 0 |
| Y10 | Girraween 2023 | 63 | 32 of 63 pp scanned (p32-63) | 1 (sim-35) |
| Y10 | Hornsby Girls 2021 | 42 | 23 of 42 pp scanned (p2, 21-42) | 0 |
| Y10 | James Ruse 2024 | 24 | text; NO SOLUTIONS | 1 (sim-36) |
| Y10 | Manly 2023 | 29 | text | 0 |
| Y10 | Merewether 2022 | 26 | text | 0 |
| Y10 | Merewether 2023 | 28 | 14 of 28 pp scanned (p15-28) | 0 |
| Y10 | NBCS 2021 | 24 | 5 of 24 pp scanned (p17-21) | 1 (sim-37) |
| Y10 | NBCS 2022 | 39 | 19 of 39 pp scanned (p21-39) | 1 (sim-38) |
| Y10 | NBCS 2023 | 38 | 19 of 38 pp scanned (p20-38) | 1 (sim-39) |
| Y10 | North Sydney Boys 2020 | 48 | 25 of 48 pp scanned (p1, 25-48) | 0 |
| Y10 | North Sydney Boys 2021 | 21 | FULLY SCANNED (21 pp) | 0 |
| Y10 | North Sydney Boys 2022 | 43 | FULLY SCANNED (43 pp) | 0 |
| Y10 | North Sydney Girls 2022 | 26 | 14 of 26 pp scanned (p13-26) | 0 |
| Y10 | North Sydney Girls 2023 | 28 | 6 of 28 pp scanned (p15, 20-22, 25, 28) | 0 |
| Y10 | North Sydney Girls 2024 | 28 | 16 of 28 pp scanned (p13-28) | 0 |
| Y10 | North Sydney Girls 2025 | 19 | 7 of 19 pp scanned (p13-19) | 0 |
| Y10 | Penrith 2024 | 32 | 2 of 32 pp scanned (p2, 18) | 0 |
| Y10 | Pymble 2021 | 24 | 8 of 24 pp scanned (p17-24) | 4 (sim-40 to sim-43) |
| Y10 | Pymble 2023 | 52 | 28 of 52 pp scanned (p2, 4, 27-52) | 2 (sim-44 to sim-45) |
| Y10 | Scots 2020 | 16 | text; NO SOLUTIONS | 1 (sim-46) |
| Y10 | Scots 2021 | 17 | text; NO SOLUTIONS | 1 (sim-47) |
| Y10 | Scots 2022 | 55 | 26 of 55 pp scanned (p30-55) | 1 (sim-48) |
| Y10 | Scots 2023 | 46 | 22 of 46 pp scanned (p25-46) | 0 |
| Y10 | Scots 2024 | 46 | 22 of 46 pp scanned (p25-46) | 1 (sim-49) |
| Y10 | Sydney Boys 2020 | 57 | 11 of 57 pp scanned (p25-27, 31-35, 42-44) | 0 |
| Y10 | Sydney Boys 2021 | 61 | 6 of 61 pp scanned (p41-44, 56-57) | 0 |
| Y10 | Sydney Boys 2022 | 65 | 6 of 65 pp scanned (p38, 44, 50, 55, 60, 64) | 0 |
| Y10 | Sydney Boys 2023 | 74 | 3 of 74 pp scanned (p40-42) | 1 (sim-50) |
| Y10 | Sydney Boys 2024 | 65 | text | 0 |
| Y10 | Sydney Boys 2025 | 74 | 27 of 74 pp scanned (p1-27) | 0 |
| Y10 | Sydney Grammar 2020 | 33 | 23 of 33 pp scanned (p11-33) | 0 |
| Y10 | Sydney Tech 2020 | 18 | FULLY SCANNED (18 pp) | 1 (sim-51) |

## Catalogue

Cover titles are given as printed. "same" repeats the cell above.

| ID | File | Q page | Sol page | School | Year | Cover title as printed | Q, marks | What the part asks | Tag | Flags and notes |
|---|---|---|---|---|---|---|---|---|---|---|
| sim-01 | `Y9/Normanhurst Boys 2020 Year 9 Maths Yearly & Solutions.pdf` | 11 | 21 | Normanhurst Boys High School | Y9 2020 | STAGE 5.1-5.3 MATHEMATICS, 2020 Year 9 Yearly Examination | Q7(a), 3 | Solve 2x - 3y = -8, 5x + 4y = 3 "by using an appropriate method". Answer x = -1, y = 2. | L2 | SOLUTION SLIP: the typed solution writes "2x - 6 = 8" for 2x - 6 = -8; the answer is right. |
| sim-02 | same | 11 | 21 | same | same | same | Q7(b), 4 | A test has 20 questions worth 2 or 3 marks, 52 marks in total. Set up a pair of simultaneous equations and find the number of each type. Answer 8 two-mark, 12 three-mark. | L3 | Clean. Typed solution. |
| sim-03 | `Y9/Normanhurst Boys 2025 Year 9 Maths Yearly & Solutions.pdf` | 14 | 34 | Normanhurst Boys High School | Y9 2025 | MATHEMATICS, 2025 Year 9 Assessment Task 4 (Yearly Examination) | Q10(e)i, 1 | Drinks $2 each, wedges $3 a serve; 100 items sold for $242. Construct a pair of simultaneous equations. | L3 | Clean. Handwritten solution: d + w = 100, 2d + 3w = 242. |
| sim-04 | same | 14 | 34 | same | same | same | Q10(e)ii, 2 | Solve the pair from (i): how many drinks and serves of wedges. Answer 58 drinks, 42 wedges. | L3 | DEPENDS ON (i) (the pair is not printed). Clean; substitution in the solution. |
| sim-05 | same | 17 | 37 | Normanhurst Boys High School | Y9 2025 | MATHEMATICS, 2025 Year 9 Assessment Task 4 (Yearly Examination) | Q11(c), 3 (printed "3+0") | Solve for x and y: 1/6^x = 18^(2y - 6). School answer x = 0, y = 3, from -x = 2y - 6 and -x = 4y - 12 (powers of 2 and of 3). | L2 | DOUBTFUL: one equation in two unknowns with no condition that x and y are integers or rational; over the reals there are infinitely many solutions (any y with x = -(2y - 6) ln 18 / ln 6). NEEDS INDEX LAWS. Handwritten solution. |
| sim-06 | `Y9/North Sydney Boys 2020 Year 9 Maths Yearly & Solutions.pdf` | 12 | 32 | North Sydney Boys High School | Y9 2020 | MATHEMATICS, 2020 YEAR 9 YEARLY EXAMINATION | Q6(d), 3 | Solve 3x + 2y = 20, 4x - 5y = -27. Answer x = 2, y = 7. | L2 | Clean. Q6 is headed "Linear Equations, Inequations and Simultaneous Equations". Solution scanned (elimination). |
| sim-07 | `Y9/St George Girls 2024 Year 9 Maths Yearly & Solutions.pdf` | 4 | 15 | St George Girls High School | Y9 2024 | Year 9 Assessment Task 3, October 2024, Mathematics | Section A Q3, 3 | Solve 2x + 5y = 7, 3x + 2y = -6 "using the elimination method". Answer x = -4, y = 3. | L2 | Clean. Marker note: students who did not use elimination lost 1 mark. |
| sim-08 | same | 6 | 17 | same | same | same | Section A Q7, 3 | Adjacent sides of a parallelogram are in the ratio 3 : 2 and the perimeter is 150 cm. Form a pair of simultaneous equations and solve for the side lengths. Answer 45 cm and 30 cm. | L3 | SOLUTION SLIP: the solution says "sub (1) in (2)" where it substitutes (2) into (1); the working and answer are right. Marker note: solving without simultaneous methods earned 1 mark in total. |
| sim-09 | `Y9/Sydney Boys 2020 Year 9 Maths Yearly & Solutions.pdf` | 11 | 35 | Sydney Boys High School | Y9 2020 | YEAR 9 TERM 4 YEARLY ASSESSMENT TASK, Mathematics Stage 5.3 | Part C Q1, 2 | Solve y = 4x + 3 and y = 17 - 3x simultaneously. Answer x = 2, y = 11. | L1 | Clean (equate the two expressions for y). Solution page scanned; marker note: students who found only x lost 1 mark. |
| sim-10 | same | 15 | 39 | same | same | same | Part D Q1, 2 | Six years ago Lydia was three times as old as Keiko; in three years Lydia will be twice as old as Keiko. Find their present ages. Answer Lydia 33, Keiko 15. | L3 | Clean. Scanned solution (L - 6 = 3(K - 6), L + 3 = 2(K + 3)). |
| sim-11 | same | 22 | 46 | same | same | same | Part E Q5, 3 | A jar holds red and yellow candies. Add 30 red: one-third are red. Then add 30 yellow: three-tenths are red. What fraction of the original candies were red? Answer 1/4 (60 red, 180 yellow). | L3 | Clean, hard. The two equations come from fractions and clear to 2r - y = -60, 7r - 3y = -120. Scanned solution. |
| sim-12 | `Y9/Sydney Boys 2022 Year 9 Maths Yearly & Solutions.pdf` | 14 | 53 | Sydney Boys High School | Y9 2022 | YEAR 9 STAGE 5.3 TERM 4 YEARLY EXAMINATION, Mathematics | Q18(e), 2 | "Hence, if T is the intersection of l and CB, find the coordinates of T", with l: x + 2y - 5 = 0 (stem) and CB: 2x - y - 4 = 0 (given in (c)). Answer T(13/5, 6/5). | L2 | DEPENDS ON OTHER PARTS: both equations are printed (stem and the show-that in (c)), so it can stand alone with a short stem. SOLUTION SLIP: "In (2): 13/5 + 2y - 5 = 0" substitutes into (1); the answer is right. Marker: about 30% got it right. |
| sim-13 | `Y9/Sydney Boys 2023 Year 9 Maths Yearly & Solutions.pdf` | 12 | 42 | Sydney Boys High School | Y9 2023 | YEAR 9 STAGE 5.3 TERM 4 YEARLY EXAMINATION, Mathematics | Q19(b), 2 | L has gradient 3 through A(-6, 4); K: x - 7y + 14 = 0 meets the y-axis at B and L at C. Find B and C. Answer B(0, 2), C(-7, 1). | L1 | DEPENDS ON (a) (L: y = 3x + 22 is found in (a)); supply it in the stem to use alone. Clean. Substitution in the typed solution. A blank grid is printed with the question. |
| sim-14 | same | 24 | 51 | same | same | same | Q28, 3 | Solve x + 2y + 4 = 0, 3x - y - 3 = 0. Answer x = 2/7, y = -15/7. | L2 | Clean. Fractional answers. Typed solution shows both elimination and substitution, with marking criteria. |
| sim-15 | `Y9/Sydney Boys 2024 Year 9 Maths Yearly & Solutions.pdf` | 9 | 39 | Sydney Boys High School | Y9 2024 | YEAR 9 STAGE 5 TERM 4 YEARLY EXAMINATION, Mathematics | Q15, 2 | Find a and b with 7a + b = 5, 5a - b = 19. Answer a = 2, b = -9. | L2 | Clean. Handwritten solution (add the equations). Marker: elimination is clearly the better approach here. |
| sim-16 | same | 20 | 47 | same | same | same | Q25, 2 | a and b are rational and a + 2b + sqrt(3a - b) = 2 + 2 sqrt5. Find a and b. Answer a = 6, b = -2 (from a + 2b = 2, 3a - b = 20). | L2 | HIDDEN PAIR: needs surds (equate rational and irrational parts, 2 sqrt5 = sqrt20) before the linear pair appears. Clean typed solution. Marker: not done well; students could not identify the simultaneous equations. Hard. |
| sim-17 | `Y9/Sydney Grammar 2020 Year 9 Maths Yearly & Solutions.pdf` | 8 | 19 | Sydney Grammar School | Y9 2020 | 2020 Annual Examination, Form III Mathematics | Q6(c)(i), 2 | Solve 3x - 2y = 7, y = x - 2. Answer x = 3, y = 1. | L1 | MARKS NOT PRINTED on the question page ("[2]" on the typed solution). Clean; substitution. |
| sim-18 | same | 8 | 20 | same | same | same | Q6(c)(ii), 2 | Solve 4x + 3y = 5, 7x - 4y = -19. Answer x = -1, y = 3. | L2 | MARKS NOT PRINTED on the question page ("[2]" on the solution). Clean; elimination. |
| sim-19 | `Y9/Sydney Grammar 2022 Year 9 Maths Yearly & Solutions.pdf` | 5 | 16 | Sydney Grammar School | Y9 2022 | 2022 Annual Examination, Form III Mathematics | Q3(h), 2 (inferred) | Solve simultaneously 3x - y = 6, y = x + 2. Answer x = 4, y = 6. | L1 | MARKS NOT PRINTED (the paper prints only "QUESTION THREE (13 marks)"; the handwritten solution has 2 ticks). Clean; substitution. |
| sim-20 | same | 6 | 17 | same | same | same | Q4(b), 3 (inferred) | Solve simultaneously "by the method of elimination" 3x + 5y = 8, x - 2y = -1. Answer x = 1, y = 1. | L2 | MARKS NOT PRINTED (3 ticks on the handwritten solution). Clean. |
| sim-21 | same | 7 | 19 | same | same | same | Q5(b)(i), 1 (inferred) | A hot chocolate costs $2 more than a bubble tea; three hot chocolates and five bubble teas cost $70. With x and y the prices, write two equations. | L3 | MARKS NOT PRINTED (1 tick). Clean: x - y = 2, 3x + 5y = 70. |
| sim-22 | same | 7 | 19 | same | same | same | Q5(b)(ii), 2 (inferred) | Solve the equations to find the cost of each drink. Answer hot chocolate $10, bubble tea $8. | L3 | MARKS NOT PRINTED (2 ticks). DEPENDS ON (i). Clean; the solution says the worded answer is required. |
| sim-23 | same | 10 | 27 | same | same | same | Q8(b), 2 (inferred) | a = 2^p and b = 2^q (p, q integers), ab = 32 and 2a^2 b = 32. Find p and q. Answer p = -1, q = 6 (from p + q = 5, 2p + q = 4). | L2 | NEEDS INDEX LAWS before the linear pair appears. MARKS NOT PRINTED (2 ticks). Clean. Hard. |
| sim-24 | `Y9/Sydney Grammar 2023 Year 9 Maths Yearly & Solutions.pdf` | 4 | 11 | Sydney Grammar School | Y9 2023 | 2023 Annual Examination, Form III Mathematics | Q3(f), 2 | Solve simultaneously "using the elimination method" a + b = 21, a - b = 5. Answer a = 13, b = 8. | L2 | Clean. Easy. Solution scanned (handwritten, two-column page). |
| sim-25 | same | 5 | 11 | same | same | same | Q4(c), 2 | Solve simultaneously "using the substitution method" x + 6y = 7, 3x + 2y = 13. Answer x = 4, y = 1/2. | L1 | Clean. Solution scanned. |
| sim-26 | `Y9/Sydney Grammar 2024 Year 9 Maths Yearly & Solutions.pdf` | 4 | 14 | Sydney Grammar School | Y9 2024 | 2024 Annual Examination, Form III Mathematics | Q3(a), 2 | Solve "using the substitution method" x = 2y + 3, x + y = 12. Answer x = 9, y = 3. | L1 | Clean. Handwritten tablet solution. |
| sim-27 | same | 5 | 14 | same | same | same | Q4(c), 2 | Solve "using the elimination method" 4x - 3y = 4, 3x + 3y = 10. Answer x = 2, y = 4/3. | L2 | Clean. Handwritten tablet solution. |
| sim-28 | same | 6 | 15 | same | same | same | Q5(e), 3 | Three lines 3x + 4y = 14, 3x - 2y = -16, 2x - 3y = -19. Determine whether they are concurrent. Answer yes, all pass through (-2, 5). | L2 | Clean. Two variables only: solve two of the equations, then check the point in the third (also fits L1 "checking a solution"). |
| sim-29 | `Y9/Sydney Grammar 2025 Year 9 Maths Yearly & Solutions.pdf` | 5 | 19 | Sydney Grammar School | Y9 2025 | 2025 Annual Examination, Form III Mathematics | Q3(d), 2 | Solve simultaneously "using the substitution method" y = 2x - 3, 2x + y = 12. Answer x = 15/4, y = 9/2. | L1 | Clean. Solution scanned (handwritten tablet). |
| sim-30 | same | 8 | 20 | same | same | same | Q5(a), 2 | Solve simultaneously "using the elimination method" 3x - 2y = 7, 4x - 5y = 15. Answer x = 5/7, y = -17/7. | L2 | Clean. Fractional answers. Solution scanned. |
| sim-31 | same | 9 | 23 | same | same | same | Q6(e), 2 | Parallel box plots of French and Geography marks. Twice as many boys scored above 70 in Geography as in French; 5 more boys scored below 80 in French than in Geography. How many boys sat Geography? Answer 80 (French 60). | L3 | Clean, hard. Needs quartile reading (75% of Geography above 70, 50% of French above 70, 75% of French and 50% of Geography below 80) to form x = (3/4)y and (3/4)x = (1/2)y + 5. Box plot must be recreated. |
| sim-32 | same | 10 | 24 | same | same | same | Q7(c), 4 | Train speed x km/h, journey time t h. 1 km/h faster cuts 24 minutes; 6 km/h faster cuts 2 hours. Form a pair of simultaneous equations and find the distance. Answer x = 24, t = 10, distance 240 km. | L3 | Clean, hard. The equations xt = (x + 1)(t - 0.4) = (x + 6)(t - 2) become linear after expanding (xt cancels): t - 0.4x = 0.4, 6t - 2x = 12. Solution p24-25. |
| sim-33 | `Y10/Canberra Grammar 2024 Year 10 Maths Yearly & Solutions.pdf` | 8 | 33 | Canberra Grammar School | Y10 2024 | 2024 Advanced Mathematics Year 10 Final Exam | Section 1 Q3(b), 3 | Line L: 3x + 2y = -2. "Use simultaneous equations" to find where L meets AB (y = 5x - 27, shown in (a)). Answer (4, -7). | L1 | DEPENDS ON (a), but the line AB is printed in (a) ("Show that ... y = 5x - 27"), so a short stem makes it stand alone. ACT SCHOOL (earlier packs set Canberra Grammar aside as non-NSW). Clean; substitution in the scanned solution. |
| sim-34 | `Y10/Girraween 2020 Year 10 Maths Yearly & Solutions.pdf` | 5 | 18 (MC key) | Girraween High School | Y10 2020 | "Year 10 Term 4 (Yearly Examination) 2020" (p1); p3 "GIRRAWEEN HIGH SCHOOL, YEAR 10 YEARLY EXAMINATION, MATHEMATICS, 2020" | Part A Q11 (MC), 1 | Sketch of the lines x - y = -7 and x + y = 1 meeting at P (not to scale). Which are the coordinates of P? Options (-4, 3), (-3, -4), (-3, 4), (-2, 3). Key C (-3, 4). | L1 | Clean (key confirmed by solving). Scanned paper; key only. |
| sim-35 | `Y10/Girraween 2023 Year 10 Maths Yearly & Solutions.pdf` | 7 | 36 (MC key) | Girraween High School | Y10 2023 | Girraween High School 2023 Year 10 Mathematics Yearly Exam | Multiple Choice Q8, 1 | David drew a correct diagram that gave the solution to y = 2x - 5 and y = x + 6. Which diagram did he draw? (four sketches of two lines). Key D. | L1 | Clean. Key D matches: both gradients positive, intercepts -5 and 6, steeper line starting lower, meeting at (11, 17) in the first quadrant. Key only. Diagrams must be recreated. |
| sim-36 | `Y10/James Ruse 2024 Year 10 Maths Yearly.pdf` | 6 | none | James Ruse Agricultural High School | Y10 2024 | SEMESTER 2 EXAMINATION, YEAR 10 2024, MATHEMATICS (school name in the crest) | Q11(b)ii, 3 | Solve 4^(x + y) = 64, 7^(2x - y) = 49 sqrt7. Answer x = 11/6, y = 7/6 (from x + y = 3, 2x - y = 5/2). | L2 | NO SOLUTIONS in the file (solved independently). NEEDS INDEX LAWS before the linear pair appears. |
| sim-37 | `Y10/NBCS 2021 Year 10 Maths Yearly & Solutions.pdf` | 14 | 22 | Northern Beaches Christian School (NBCS) | Y10 2021 | MATHEMATICS 2021 Year 10 5.3 - Yearly Examination | Q30(a), 2 | Solve simultaneously 7x + 2y = 34, 5x - 2y = 14. Answer x = 4, y = 3. | L2 | Clean. Easy (add the equations). Scanned marked solution. |
| sim-38 | `Y10/NBCS 2022 Year 10 Maths Yearly & Solutions.pdf` | 11 | 31 | Northern Beaches Christian School (NBCS) | Y10 2022 | Mathematics 2022 Year 10 5.3/Year 9 Accelerated Yearly Examination | Section II Q24(b), 2 | If 2p + q = 6 and 3p - 2q = 2, what is the value of p + q? Answer 4 (p = 2, q = 2). | L2 | Clean. Scanned marked solution (substitution). |
| sim-39 | `Y10/NBCS 2023 Year 10 Maths Yearly & Solutions.pdf` | 10 | 29 | Northern Beaches Christian School (NBCS) | Y10 2023 | Mathematics 2023 Year 10 5.3/Year 9 Accelerated Yearly Examination | Section II Q21(c), 2 | Given c - a = 12 and c + 2a = 15, find the value of c + a. Answer 14 (a = 1, c = 13). | L2 | Clean. Scanned solution (subtract the equations). |
| sim-40 | `Y10/Pymble 2021 Year 10 Maths Yearly & Solutions.pdf` | 5 | 18 | Pymble Ladies' College | Y10 2021 | Year 10 Mathematics, 5.3 Pathway, YEARLY ASSESSMENT, Term 4, 2021 | Q12 (MC), 1 | A worked solution of 3x + y = 20, 5x - 2y = 26 is shown in four lines. In which line does the first mistake occur? Key D (Line 4: "30 + y = 20", where 3 x 6 = 18). | L2 | Clean. Error-spotting item. The printed working is an image (needs recreating). Annotated scan as solution. |
| sim-41 | same | 8 | 20 | same | same | same | Q21 (MC), 1 | Solution of 5x + 7y - 3 = 0 and y = 7 - 4x? Key B (x = 2, y = -1). | L1 | Clean. Substitution, or check each option (fits "checking a solution"). |
| sim-42 | same | 8 | 20 | same | same | same | Q23 (MC), 1 | Lines y = 5x - 7 and y = -5x - 7. Which sentence is NOT true? Key D ("the lines have the same gradient"). | L1 | Clean. Intersection at the shared y-intercept (0, -7). |
| sim-43 | same | 14 | 23 | same | same | same | Q39 (MC), 1 | Solving 5x - 3y = 8 and 2x + y = 4 by elimination: the first line after eliminating y? Key D (11x = 20). | L2 | Clean. |
| sim-44 | `Y10/Pymble 2023 Year 10 Maths Yearly & Solutions.pdf` | 5 | 31 | Pymble Ladies' College | Y10 2023 | Year 10 Mathematics, 5.3 Pathway, YEARLY EXAMINATION, 2023 | Section I Q3 (MC), 1 | Solution set of 3x - y = 18, 4x + y = 10? Key C (4, -6). | L2 | Clean. Annotated scan as solution. |
| sim-45 | same | 16 | 42 | same | same | same | Section II Q22, 2 | Solve 5x - y = 1.5, 2x - y = -2.1. Answer x = 1.2, y = 4.5. | L2 | Clean. Decimal coefficients. Scanned marked solution. |
| sim-46 | `Y10/Scots 2020 Year 10 Maths Yearly.pdf` | 2 | none | The Scots College | Y10 2020 | Year 10 5.3 Mathematics, Thursday 5th November 2020, Yearly Examination | Q4 (MC), 1 | If 3x + y = 9 and 4x - y = 19, the value of y is: 4, -3, 7, 5. Answer B (-3; x = 4). | L2 | NO SOLUTIONS in the file (solved independently). |
| sim-47 | `Y10/Scots 2021 Year 10 Maths Yearly.pdf` | 5 | none | The Scots College | Y10 2021 | 2021 Year 10 Mathematics 5.3 Assessment Task 4 | Q11, 3 | Solve this pair of equations simultaneously: 3x - y = 2, 2x - 3y = 20. Answer x = -2, y = -8. | L2 | NO SOLUTIONS in the file (solved independently). |
| sim-48 | `Y10/Scots 2022 Year 10 Maths Yearly & Solutions.pdf` | 12 | 41 | The Scots College | Y10 2022 | 2022 Year 10 Assessment Task 4, Mathematics 5.3 | Q17, 3 | Solve 4x + 2y = 10 and 5x + 3y = 12 simultaneously. Answer x = 3, y = -1. | L2 | Clean. Both equations must be multiplied. Scanned solution shows two elimination routes. |
| sim-49 | `Y10/Scots 2024 Year 10 Maths Yearly & Solutions.pdf` | 7 | 31 | The Scots College | Y10 2024 | 2024 Year 10 Assessment Task 4, Mathematics 5.3 | Q9, 3 | Solve 5x - 3y = 18, 2x + 4y = 54. Answer x = 9, y = 9. | L2 | Clean. Both equations must be multiplied. Scanned marked solution. |
| sim-50 | `Y10/Sydney Boys 2023 Year 10 Maths Yearly & Solutions.pdf` | 28 | 66 | Sydney Boys High School | Y10 2023 | YEAR 10 STAGE 5.3 TERM 4 YEARLY ASSESSMENT, Mathematics | Part E Q3, 3 | The ratio of the ages of Lynne and her father Jeff is 3 : 7. Twelve years later it is 5 : 9. Find their initial ages. Answer 18 and 42. | L3 | Clean. The school solution uses one pronumeral (3x and 7x); the two-equation route is 7L = 3J, 9(L + 12) = 5(J + 12). Handwritten solution. |
| sim-51 | `Y10/Sydney Tech 2020 Year 10 Maths Yearly & Solutions.pdf` | 4 | 13 | Sydney Technical High School | Y10 2020 | Year 10 Mathematics, Assessment 4, October 2020 | Section 2 Q6(c), 2 | Solve the simultaneous equations x + y = 3, 2x + 3y - 10 = 0. Answer x = -1, y = 4. | L2 | Clean. Fully scanned file; handwritten solution shows elimination and substitution. |

## Not linear (not counted)

Pairs where one graph is a parabola, circle, hyperbola, exponential, cubic or other curve.

| File | Q page (sol page) | Q, marks | Pair |
|---|---|---|---|
| `Y9/Sydney Grammar 2023` | 9 | Q8(b)(i)–(iii), 2 + 2 + 1 | Prize-money story: show 2Pr = 700 and P(1 + r^2) = 17507, then solve simultaneously for r (non-linear) |
| `Y10/Fort St 2021` | 15 | Part D Q1, 4 | x^2 + y^2 = 5 and xy = -2 |
| `Y10/Fort St 2022` | 10 (25) | Section C Q4(a), 2; Q4(b), 2 | y = x^2 + 4x and 2x - y - 1 = 0; prove y = x - 4 and y = x^2 - x - 2 do not meet |
| `Y10/Fort St 2023` | 8 (30) | Part E Q3, 4 | xy = 6 and x - y = 5, find intersections and sketch |
| `Y10/Girraween 2020` | 10 | Q23(d), 3 | y = mx - 4 tangent to y = x^2 - 1 |
| `Y10/Girraween 2022` | 6; 17; 19 | Part A Q3 (MC), 1; Q23(b), 3; Q23(d)(i)(ii), 4 + 4 | y = 5^x and y = 1/5; y = 4x + k meets y = x^2 + 5 twice; x^2 + y^2 = 25 and y = 3x/4 |
| `Y10/Girraween 2023` | 5; 21 (53) | MC Q2, 1; Q2(d), 3 | y = x and a semicircle of radius 2; x^2 + y^2 = 5 and y = x + 1 |
| `Y10/Merewether 2022` | 7; 13 (26) | Part C Q2 (MC), 1; Part D Q9, 2 | y = x^2 - 5x + 2 and y = -x - 2 (how many points); y = 3/x and y = 2x + 1 |
| `Y10/Merewether 2023` | 9 (23) | Section IV Part B Q2, 2 | y = x^2 + x + 1 and y = 4x + 5 meet at x = -1 and one other x |
| `Y10/NBCS 2023` | 14 | Q27(a), 3; (b), 1 | y = x^2 + 4x + 2 and y = -x^2 - 2x - 2; line through their intersections |
| `Y10/North Sydney Boys 2021` | 3 | Q2(g), 3 | y = x^2 - 3x + 7 and 2x - y + 3 = 0 |
| `Y10/North Sydney Girls 2022` | 12 | Q20(b), 3 | (x - 5)^2 + (y + 1)^2 = 16 and y = x - 2 |
| `Y10/North Sydney Girls 2023` | 8 (22) | Q18(d), 3 | f(x) = 4/x and g(x) = x + 3 meet at A and B; find AB |
| `Y10/North Sydney Girls 2024` | 10 | Q19(c)(i), 3 | (x - 2)^2 + (y - 1)^2 = 25 and y = 4 - x |
| `Y10/North Sydney Girls 2025` | 8 | Q18(b)(i), 2; (ii), 2 | y = 2x + 15 and y = x^2; then x^2 ≥ 2x + 15 |
| `Y10/Pymble 2023` | 20 (46) | Q27, 3 | y = 4/(x + 1) and x - y - 2 = 0 |
| `Y10/Scots 2023` | 11 (35) | Q17, 3 | y = x^2 - 2x - 1 and 4x + 2y = 0 |
| `Y10/Sydney Boys 2020` | 15 | Part C Q32(b), 2 | f(x) = x^3 - x and its inverse relation |
| `Y10/Sydney Boys 2021` | 33; 26 | Part G (a)(i), 3; Part E (e)(iv), 2 | 2x^2 - y^2 = 17 and x + 2y = 1; f(x) = f^-1(x) |
| `Y10/Sydney Boys 2022` | 16 (49) | Part C Q5(b), 4 | y = 5(2^2x) - 6(2^x) and y = 5(2^x) - 2 |
| `Y10/Sydney Boys 2024` | 20 (54) | Part D Q1, 3 | y = x^2 + x + 1 and y = 5x - 3 |
| `Y10/Sydney Boys 2025` | 3; 17 (58) | Section A Q7 (MC), 1; Section C Q3(e), 2 | 8/x = 2x + 4; f and f^-1. EXCLUDED |
| `Y10/Sydney Grammar 2020` | 9; 10 | Q7(c), 3; Q8(b), 3; Q9(b), 3 | y = 3/(x + 3) and y = 2x + 5; x^2 - y^2 = 11 and log x - log y = 1; circle and parabola meeting in exactly two points |
| `Y10/Sydney Tech 2020` | 11 | Q9(c)(ii), 2 | y = 2x^2 - 1 and y = 6x + 2, algebraically |

Three-variable systems: none found.

## Related items, not counted

Linear pairs that appear only as a step inside another topic, or items that look like simultaneous equations but are solved with one unknown. Listed so nobody needs to search for them again.

| File | Page (sol) | Q, marks | Why not counted |
|---|---|---|---|
| `Y10/Fort St 2020` | 4 (21) | Section A Q4, 3 | Monic quadratic through (-2, 18) and (1, 0): a linear pair in b and c inside a quadratics question |
| `Y10/Girraween 2020` | 12 | Q24(d), 4 | P(x) = x^3 + ax^2 + bx + 2 with factors x + 1 and x - 2: factor theorem gives a linear pair in a, b |
| `Y10/North Sydney Boys 2022` | 16 | Q20, 2 | Divisible by x - 3, remainder -8 on x - 1: factor/remainder theorem pair |
| `Y10/Sydney Boys 2021` | 30 | Part F (d), 3 | Factor x - 4, remainder 18 on x + 2: polynomial pair |
| `Y10/Sydney Boys 2022` | 29 (62) | Part F Q2, 3 | Remainder 216 on x - 2, factor x + 1: polynomial pair (marker: "2 correct equations to solve simultaneously") |
| `Y10/Sydney Boys 2023` | 30 | Part E Q5, 3 | Factor x + 1, remainder -18 on x - 2: polynomial pair |
| `Y10/Baulkham Hills 2020` | 10 | Q23(b), 1 | Where y = 5 meets 2x - y - 1 = 0: one substitution, part of a coordinate-geometry question |
| `Y10/Manly 2023` | 15 | Book 3 Q5(a), 2 | Two numbers with mean 7 and mode 4: x + y = 12 with x = 4 from the mode, not a pair |
| `Y10/NBCS 2022` | 12 | Q26(a)–(c), 1 + 1 + 2 | Taxi fare line compared with y = 2 + 2x at 8 km: no intersection asked |
| `Y9/Sydney Boys 2020` | 21 (45) | Part E Q3, 3 | Point on y = x - 9 equidistant from A(1, -4) and B(5, -2): one unknown after substitution (distance) |
| `Y9/Sydney Boys 2024` | 10 (40) | Q17, 3 | Toby's pay ($21.80, time-and-a-half, three times the hours): one unknown (x and 3x) |
| `Y9/Sydney Boys 2023` | 8 | Q16(b), 2 | Shade the region y - 2 ≤ 0 and 2x - y - 4 ≤ 0: inequalities |
| `Y9/Sydney Boys 2022` | 31–32 | Part 2 Q8(a)–(b) | Golden rectangle lines in terms of φ (comprehension paper); the intersection is given in the text |
| `Y9/Sydney Boys 2025` | 18 (40) | Section D Q2, 3 | Perpendicular distance without the formula (foot of a perpendicular). EXCLUDED |
| `Y10/Sydney Boys 2025` | 18 | Section D Q4, 3 | 2 sin(x + y) = √3, 3 tan(x - y) = √3: becomes x + y = 60°, x - y = 30° (trig). EXCLUDED |
