# Task 6 report: Lesson 14E Counting unordered selections

Status: DONE_WITH_CONCERNS (the concerns are listed at the end: Ex 14E Q6 left out as doubtful, two textbook typos fixed silently, three past-paper wording slips kept as printed)

Commit: c39ea6f "Y11Ch14: lesson 14E" on ch10-pack (not pushed).

## What I built
`workspace/build/y11ch14/l14e.html` (replaces the placeholder)
- Lesson head (l.2). Five concepts, each with a Tutor demo, a Your turn and the textbook worked examples:
  - Concept 1, counting the subsets of a set (l.6): the list of all 32 subsets of {A, B, C, D, E}; the Y/N code and 2^5; 3-member subsets as words with 3 Ys and 2 Ns; the general formulae; the nCr and binomial notation; Box 12; the notes on the last bullet, on P and C and on calculators; the proof from ordered selections (nPr ÷ rPr). Worked examples 15 (l.64) and 16 (l.77).
  - Concept 2, the canonical correspondence nCr = nC(n−r) (l.85): afternoon tea, the table of the 10 complementary pairs, Box 13, the 'invisible enemies' note. Worked example 17 (l.116).
  - Concept 3, using nCr in counting problems (l.124), with the 'at least / at most / not / excluding' warning in a warn box. Worked example 18 (l.144).
  - Concept 4, subsets with conditions (l.161). Worked example 19 (l.177).
  - Concept 5, the harder question about points on a circle (l.192). Worked example 20 (l.212), with the circle figure.
- Textbook homework, Exercise 14E (l.238): Q1–5 and Q7–30 verbatim, banded as in the book: Foundation 1–7, Development 8–25, Enrichment 26–30. Q6 is left out (see below). Every part is on its own line, including the sub-parts 3a, 10a, 16a, 18c, 25a, 28c and 30a. Q25 has its grid figure.
- Past-paper homework (l.318): 11 questions, 20 marks, 30 minutes.

`workspace/build/y11ch14/a_14e.html` (replaces the placeholder): the ahead line, then Lesson Examples C1–C5, then Textbook Homework (Q1–5, Q7–30, with the textbook's explanations for 3b, 10, 16a, 30b–f), then the ahead line again, then Past-Paper Homework – Worked Solutions PP 1–11.

Figures (`figs.py` `fig_14e`, l.160–235): `circle10` (Example 20), `grid25` (Ex 14E Q25: 4 squares wide, 6 high, crosses at the five points four moves from A, C the middle cross), `abb20pts` (Abbotsleigh 2020 Q13(a): nine points, four on the drawn line), `abb24tiles` (Abbotsleigh 2024 Q12(c): the example arrangement, top 1, 3, 4, 10 shaded, bottom 1, 4, 6, 7, 8, 9).

`workspace/checks/y11ch14_14e.py`: 298 checks, all OK.

## Sources
- Textbook: Y11 book PDF 711–719 (printed 687–695), all read rendered: teaching pp. 711–716, Exercise 14E pp. 716–719 (Foundation 1–7, Development 8–25, Enrichment 26–30). Answers PDF 940 (right column, from "Exercise 14E") and 941 (left column, to 30f).
- Past papers (all paths under `workspace/pp/Ext 1/`; every question checked on the rendered page, and against the school solution where there is one):

| PP | Label | Q, marks | File | Question p | Solution p |
|---|---|---|---|---|---|
| 1 | Sydney Boys High School, 2020, Year 12 Term 3 Trial HSC, Mathematics Extension 1 | Q6, 1 (MC) | `2020/2020 SBHS 2.pdf` | 4 | 13 (A, 4845) |
| 2 | Sydney Grammar School, 2020, Trial Examination, Form VI Mathematics Extension 1 | Q6, 1 (MC) | `2020/Sydney Grammar 2020 3U Trials & Solutions.pdf` | 3 | 10 (B, 100) |
| 3 | Moriah College, 2023, Trial Higher School Certificate Examination, Mathematics Extension 1 | Q3, 1 (MC) | `2023/Moriah 3U 2023 Paper w_ Solutions.pdf` | 3 | 15–16 (C, 33075) |
| 4 | Killara High School, 2024, Year 12 Examination, Mathematics Extension 1 HSC Trial Examination | Q6, 1 (MC) | `2024/Killara 2024 3U Trials & Solutions.pdf` | 4 | 15 (D) |
| 5 | Sydney Boys High School, 2020, … | Q12(d)(i)(ii), 2+1 | `2020/2020 SBHS 2.pdf` | 8 | 24 (7098, 156) |
| 6 | Sydney Technical High School, 2021, Trial HSC, Extension 1 Mathematics | Q11(e), 2 | `2021/3U Sydney Tech.pdf` | 6 | 13 (196) |
| 7 | Abbotsleigh, 2020, Higher School Certificate Assessment 4 Trial Examination, Mathematics Extension 1 | Q13(a), 2 | `2020/2020 Abbotsleigh (No Solutions).pdf` | 11 | none (80, solved independently) |
| 8 | Sydney Girls High School, 2023, Trial Higher School Certificate Examination, Mathematics Extension 1 | Q11(e)(i)(ii), 1+2 | `2023/SGHS 2023 3U.pdf` | 9 | 24 (2704156, 36764) |
| 9 | Normanhurst Boys High School, 2023, Year 12 Course Assessment Task 4 (Trial Examination), Mathematics Extension 1 | Q11(e)(i)(ii), 1+1 | `2023/Normanhurst 2023 3U.pdf` | 5 | 13 (462, 210) |
| 10 | Knox Grammar School, 2023, Higher School Certificate Trial Examination, Mathematics Extension 1 | Q12(d), 2 | `2023/Knox 2023 3U.pdf` | 9 | 18–19 (n = 11) |
| 11 | Abbotsleigh, 2024, Higher School Certificate Assessment 4 Trial Examination, Mathematics Extension 1 | Q12(c), 2 | `2024/Abbotsleigh 2024.pdf` | 10 | 23 (18900) |

Order runs from accessible to demanding: four 1-mark MCs, then committees, the collinear points, a cases question, equal groups, an nCr equation and the tiles. Each item needs only 14A–14E (PP 4 combines a 14B ordered choice with a 14E unordered one). All selections are recorded under `## 14E` in `docs/pp_selected_y11ch14.md`. I re-read `pp_selected_ch10.md`, `pp_selected_y11ch14.md`, `pp_selected_y11ch15.md` and `PAST_PAPERS_USED.md` before choosing and again just before committing. There is no overlap. Ch 15 has taken NSB 2020 Q14(a) (E12) and PLC 2023 Q14(b) (E25) for 15D, so I did not use them.

## Omitted or rejected, and why
- **Ex 14E Q6 is omitted: doubtful under house rule 6 (inconsistent data).** It says "three identical green balls and six identical blue balls". The book's answers (126, 45, 51, 75) treat the nine balls as distinct, for example 9C4 = 126. If the balls really are identical, the answers would be 4, 1, 2, 2. The numbering keeps the book's numbers, so it goes from 5 to 7. Please rule. The other option is to print it with the book's answers.
- Q24 (painted cubes, die in a box) is kept. It is in 14E and needs no 14G method: 6!/24 = 30, where 24 is the number of rotations (6 faces down × 4 turns). The check counts orbits under the 24 rotations.
- Not taken (past papers): E30 (Ascham 2024 Q14(e)) is Ex 14E Q22(b) with the same numbers, and E8 (SGS 2021 Q9) has the same structure. E7 (stem typo "a least") and E19 ("commitee"). E10 and E21 (majority committees, the same skill as PP 8). E13, E15, E20, E28 and E34 (plain products, the same skill as PP 5(i)). E24 (the same complement as PP 2). E16 (the same case split as PP 3). E14, kept with its (ii) for 14F. E5 (key only). E33 (wording slip). E17 and E18 (Fort Street 2023: controller ruling). Identity items: E6 (Killara 2021 Q7), E11 (Kings 2021 Q14(a)(ii)) and E26 (Hornsby 2023 Q11(e)(i)) were not needed. Ch 15 has left them free for Ch 14.
- No 14F probability rows were used.

## Textbook typos (reported, printed corrected with no remark)
1. Box 13 prints "Let n and r be whole numbers with o ≤ r ≤ n" (the letter o for zero). I printed 0 ≤ r ≤ n.
2. Example 19(c) prints "U = {2, 4, 6 12}" (a missing comma). I printed {2, 4, 6, 12}.
3. Answer slip: the book's answer to Q16(a)(ii) says "choose the two people to go in the same group as Laura", but there is no Laura in the question. I printed "… as one particular person". The number, 10, is unchanged.
All other textbook answers agree with brute force.

## Past-paper wording kept as printed (house rule 5; not mathematical, so not treated as doubtful)
- Killara 2024 Q6: "are chosen from class of n students".
- Knox 2023 Q12(d): "Find n the number dancers in the performing arts academy."
- Abbotsleigh 2024 Q12(c): "… in the bottom row, An example of one such arrangement is shown."
- STHS 2021: the paper's cover is "Extension 1 Mathematics TRIAL HSC August 2021". Its solution pages are headed "Mathematics Common Test Assessment 4 2019", but they solve this paper's Q11(d)–(g). Only the question is used, and the answer 196 was found independently.

## Verification
- `python3 workspace/checks/y11ch14_14e.py`: 298 checks, all OK, exit 0, about 15 s.
  - The script reads every printed value: the concept-box displays (the subsets table against itertools, 2^5, 5!/(3!2!), the general formulae, Box 12 and Box 13 at all n ≤ 8 to 10, 5P3, 3P3, 60 ÷ 6, nPr ÷ rPr), Worked examples 15–20 (every '=' piece, plus the prime factorisation), C1–C5, Textbook Q1–30 and PP 1–11.
  - The truths come from enumeration:
    - committees are built from labelled people;
    - Q15 deals all 2 598 960 hands;
    - triangle overlap is decided from coordinates on a circle;
    - Q24 counts orbits under the 24 rotations;
    - Q25 walks the grid read back from `grid25.svg`;
    - Q28 builds every doubles structure, 155 925 of them;
    - Q29 uses a DP, checked against full enumeration for n ≤ 4;
    - Q12 uses sequential choice, checked against enumeration on a smaller case;
    - PP 7 counts collinear triples on the points read from `abb20pts.svg`;
    - PP 8 lists all 2 704 156 teams;
    - PP 11 checks the SVG example and enumerates every shading.
  - Algebraic answers (nC4, nC2, WE15b, Q17d, Q23d, Q30a/e, PP 4's options and answer) are checked at many values.
  - The structure checks cover marks (20), time (30), numbering, matching labels, one hint each, part marks and each MC letter.
  - A mutation test changed four printed values (Q18c ii, a PP 3 factor, a Q29 ratio, a WE16 prime). All four were caught, with exit 1.
- The other Ch 14 checks still pass after the `figs.py` change: 14a 180, 14b 218, 14c 205, 14d 239, rev 57.
- Build: `python3 build.py y11ch14 all && mv lesson.pdf answers.pdf y11ch14/`. `qa.py`: lesson.pdf 103 pages, 0 problems; answers.pdf 30 pages, 0 problems. The MathJax error scan (and a scan for stray `{{`) is clean on both PDFs.
- Pages inspected: lesson pp. 75–103 (all of 14E) and answers pp. 23–30. I fixed:
  - a `{{sec}}` title containing maths, which broke the macro;
  - the subsets table wrapping;
  - pagination, so that every concept heading stays with its box and the following demo;
  - the size of the circle figure.
  Some pages have white space below a block that cannot be split (p. 84 below WE19 + C5 is tight; p. 86 has WE20 alone, about 40% blank).

## Files changed
`workspace/build/y11ch14/l14e.html`, `a_14e.html`, `figs.py`, `svg/circle10.svg`, `svg/grid25.svg`, `svg/abb20pts.svg`, `svg/abb24tiles.svg`, `workspace/checks/y11ch14_14e.py`, `docs/pp_selected_y11ch14.md`. I did not touch `workspace/build/y11ch15` (its `cover.html` shows as modified by another agent, and it is not staged).

## Concerns
1. Ex 14E Q6 is omitted as doubtful. Please rule.
2. Two textbook typos (Box 13 "o", Example 19c comma) and one answer slip (Q16a(ii) "Laura") were fixed silently, as instructed.
3. Three past-paper wording slips are kept as printed (Killara 2024 Q6, Knox 2023 Q12(d), Abbotsleigh 2024 Q12(c)).
4. Layout: p. 86 holds WE20 alone (about 40% blank), and the C5 tutor-demo work box is small (26 mm) so that the concept heading, box and demo share p. 84.
