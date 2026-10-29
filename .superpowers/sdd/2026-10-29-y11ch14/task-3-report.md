# Task 3 report: Lesson 14B Counting ordered selections

Status: DONE_WITH_CONCERNS. The past-paper mini exam has 13 marks, below 15 (house rule 8). Textbook Q22b was left out as a doubtful item (house rule 6).
Commit: `73254ac Y11Ch14: lesson 14B` on `ch10-pack`. Not pushed.

## What I built
`workspace/build/y11ch14/l14b.html` (replaces the placeholder). It follows the 14A structure.
- Lesson head (l14b.html:2-3).
- **Concept 1, the multiplication principle and box diagrams** (l14b.html:6). It covers the "ordered or unordered / with or without repetition" intro, Stefan's outfits (72 and 50 112), Box 3 (l14b.html:18) and box diagrams, with the outfit table. A note says a "word" is any string of letters, there are 5 vowels and 21 consonants, and y is a consonant (this is the textbook note after Example 3). Then a Tutor demo, a Your turn, and Worked example 3 (l14b.html:35) with the textbook's box table.
- **Concept 2, ordered selections with repetition** (l14b.html:44). It has the n-boxes table, Box 4 (l14b.html:49) and a short "at least one: count the complement" box for Example 4b. Then a Tutor demo, a Your turn and Worked example 4 (l14b.html:62).
- **Concept 3, permutations without repetition** (l14b.html:72). It covers factorials appearing, the with/without replacement note, the general case with the derivation of nPr = n!/(n−r)!, Box 5 (l14b.html:81), 5P3 = 60, the calculator nPr button, permutations of a set, and Box 6 (l14b.html:91, with its 14A cross-reference). Then a Tutor demo (14 members choose 3 officers; 6- and 7-digit numbers from 1–7; 10 vs 20 people in a queue; 6P4 by hand), a Your turn, and Worked examples 5, 6 and 7 (l14b.html:107, 114, 123). Example 6 sits in a `.split` with short aligned lines only.
- **Concept 4, deal with the restrictions first** (l14b.html:132). It has the general counting principle text, Box 7 (l14b.html:135), and a separate "restrictions on digits" box: the first digit is not 0 and the last digit sets parity. Then a Tutor demo (a variant of Example 8 with 10 people, plus odd numbers and numbers using 0), a Your turn, and Worked example 8 (l14b.html:151) with the box table.
- The decorative silhouettes in Example 8 were not drawn, and no figure was needed. All box diagrams are HTML `table.t` tables like the textbook's, so `figs.py` and `svg/` are unchanged.
- **Textbook homework** (l14b.html:165): Exercise 14B Q1–25 verbatim. Foundation is Q1–12, Development Q13–24, Enrichment Q25, as banded in the book. Q22b is omitted (see below).
- **Past-paper homework** (l14b.html:210): 8 questions, 13 marks, 20 minutes. Each has one hint that gives a starting idea, never a step. Two are MC.

`workspace/build/y11ch14/a_14b.html` (replaces the placeholder) has `{{ahead:Lesson 14B | Counting ordered selections}}`, then Lesson Examples C1–C4 (a_14b.html:3-10), then Textbook Homework (a_14b.html:13). Every question has an answer, except that 24c is a proof and has none. Then the ahead line again and the Past-Paper Homework worked solutions (a_14b.html:44 onward). The MC solutions explain the choice and the main wrong option.

`workspace/checks/y11ch14_14b.py` is new (218 checks).

## Sources used
- Textbook: `workspace/sources/CSM6_EXT1Y11_book.pdf`, PDF 694–701 (printed 670–677), all rendered and read. That is the teaching pages with Boxes 3–7 and Examples 3–8, plus Exercise 14B with its F/D/E bands.
- Answers: PDF 939. The Exercise 14B block is the lower-left column and the top of the right column, rendered in halves at zoom 2 (plus a zoom 2.5 strip for Q25). I solved all answers independently, and they agree with the book.

Past papers. Each was verified on the rendered question page and cover, and against the school solution where one exists:

| PP | Label (as printed) | Q, marks | File | Question p | Solution p |
|---|---|---|---|---|---|
| 1 | Normanhurst Boys High School, 2023, Year 12 Course Assessment Task 4 (Trial Examination), Mathematics Extension 1 | Q3, 1 (MC, B = 18) | `2023/Normanhurst 2023 3U.pdf` | 2 | 12 (key) |
| 2 | Moriah College, 2023, Trial Higher School Certificate Examination, Mathematics Extension 1 | Q10(b)(ii), 1 (20 160) | `2023/Moriah 3U 2023 Paper w_ Solutions.pdf` | 9 | 20 |
| 3 | Gosford High School, 2023, Trial HSC examination, Mathematics Extension 1 | Q5, 1 (MC, C = 72) | `2023/Gosford 2023 3U.pdf` | 3 | 15 (key) |
| 4 | Hurlstone Agricultural High School, 2021, Higher School Certificate Assessment Task 4, Mathematics Extension 1 | Q11(b), 1 (1/56) | `2021/3U HAHS.pdf` | 7 | none (solved independently, brute-forced) |
| 5 | Girraween High School, 2020, Trial Higher School Certificate Examination, Mathematics Extension 1 | Q14(c), 2 (168) | `2020/2020 Girraween.pdf` | 9 | 21 (handwritten) |
| 6 | Ascham School, 2023, Year 12 Trial Examination, Mathematics Extension 1 | Q12(e)(iii), 1 (2520) | `2023/Ascham 2023 3U.pdf` | 8 | 20 |
| 7 | Killara High School, 2024, Year 12 Examination, Mathematics Extension 1 HSC Trial Examination | Q12(d), 3 (proof) | `2024/Killara 2024 3U Trials & Solutions.pdf` | 9 | 21 |
| 8 | North Sydney Girls High School, 2020, HSC Trial Examination, Mathematics Extension 1 | Q13(c)(i)(ii), 1+2 (216, 432) | `2020/2020 NSG.pdf` | 9 | 22 (handwritten) |

All are appended to `docs/pp_selected_y11ch14.md` under `## 14B`. Before choosing and again before committing, I cross-checked `docs/PAST_PAPERS_USED.md`, `pp_selected_ch10.md`, `pp_selected_y11ch14.md` and `pp_selected_y11ch15.md`. There is no clash: Ch 10 used Killara 2024 Q13(e) and NSG 2020 Q13(d); Ch 15 used Moriah 2023 Q9(d); 14A used Ascham Q12(e)(i). Labels follow the 14A label style in this pack.

## Omitted or rejected, and why
- **Exercise 14B Q22b ("Repeat the two parts to this question if repetitions are allowed") is omitted: doubtful under house rule 6, a missing condition.** With repetition allowed, the digits 2, 3, 4, 5 form infinitely many integers. The book's answers (340 and 170) silently assume at most four digits. Q22a is kept with its i and ii, and the lone "a" label is kept to match the book. Please confirm this is acceptable. The other option is to include 22b, but its answer rests on an unstated condition.
- **Under 15 marks (house rule 8).** These 13 marks are the clean items that fit what 14B teaches. Rejected:
  - Hurlstone 2023 Q10 (row B8). It needs an unordered selection (10C6), so it is left for 14E.
  - Sydney Tech 2020 Sample 2 Q14(c)(i). It is from a sample paper, its stem is a sentence fragment ("A four letter employee password from the letters …"), and no solution is pinned. Part (ii) is banned by ruling.
  - NSB 2024 Q11(d). Banned by ruling: no school name.
  - CTHS 2020 Q1 and Ascham Q12(e)(i). Already used in 14A.
- PP 4 (HAHS 2021, row F5) is a probability item from the 14F list. It needs only 14B counting and P(E) = |E|/|S| from the revision page, which the intro line says. Using it leaves 14F's large pool almost untouched.
- PP 2 and PP 6 use the same symmetry idea (Exercise Q18d). I used both because the pool is short, and they have different contexts (people and letters). They are kept apart (PP 2 and PP 6).
- Two items are left free for other lessons: Ascham Q12(e)(ii) (vowels adjacent, 14C) and Moriah Q10(b)(i) (a circle: never used).
- No doubtful past-paper items were found among those used.

## Verification
- `python3 workspace/checks/y11ch14_14b.py` gives **218 checks, all OK** (exit 0), with a NOTE that 13 marks is below 15.
  - It reads every printed value with exactly-once templates. For each printed chain, such as `5\times5\times8\times3\times6!=432\,000`, every '='-separated piece must equal the count.
  - The counts are independent, almost all by itertools brute force over the actual letters, digits or people: all 8! orders for Example 8, the boat crew, NUMBER, CONSIDER, EPSILON, all 1–5 digit numbers for PP 1 and PP 5, all 4-digit numbers for NSG, and all 5-digit numbers for Q25.
  - Some cases are too large to enumerate. The 10^7 phone numbers use a DP over positions, self-tested against brute force. The licence plates multiply separately enumerated letter and digit parts. The 10-person queue enumerates the named people's places, checked against the full enumeration in the 8-person case.
  - It also checks: the nPr derivation and Box 5/6 formulas for 0 ≤ r ≤ n ≤ 7; that the Q24c identities as printed are true (catching any transcription slip); and every line of the Killara proof at 165 (n, r, k) triples. It re-reads key question data from l14b.html, so the truths match the printed questions. It checks the PP structure (marks sum, time, numbering, identical labels in both files, one hint each) and the MC letters.
- Mutation tests, using `Y11CH14_SRC` on a scratch copy, each exit 1 with exactly one mismatch: a wrong factor in a chain (C4a), a wrong TB answer (21c 95→96), a wrong total (PP8), a wrong MC letter (PP1), and a changed question digit (PP5).
- `python3 workspace/checks/y11ch14_14a.py` still gives 180 checks, all OK.
- Build: `python3 build.py y11ch14 all && mv lesson.pdf answers.pdf y11ch14/` produces a 38-page lesson and a 10-page answers PDF.
- `qa.py` reports 0 problems on lesson.pdf and 0 on answers.pdf.
- MathJax error scan (PyMuPDF text, all seven strings) found 0 in both PDFs.
- Pages inspected:
  - Lesson pp 20–38 (14B), as sheets, plus zoomed crops of the nPr derivation (p24), Example 6 split (p26) and the PP intro (p35).
  - Answers pp 6–10, plus zoomed crops of C1–C4 (p6) and the Killara proof (p10).
  - No clipped or overflowing maths, no stranded headings, and the tables are inside their boxes.
  - Work boxes were rebalanced: Q21–23 enlarged to fill p33, and PP 7 enlarged. The last page (p38) holds PP 8 alone, about half full.

## Files changed
- `workspace/build/y11ch14/l14b.html`, `workspace/build/y11ch14/a_14b.html` (placeholders replaced)
- `workspace/checks/y11ch14_14b.py` (new)
- `docs/pp_selected_y11ch14.md` (## 14B appended)
- `figs.py` and `svg/` are unchanged. Ch 15 files were not touched. The modified y11ch15 files in the working tree are another agent's and were not staged.

## Concerns
1. Q22b omitted as doubtful (above). Please rule.
2. The mini exam has 13 marks (house rule 8).
3. PP 4 borrows a 14F-tagged item (row F5). If the controller would rather keep it for 14F, PP 4 can be dropped (12 marks, time 20 → 20 min, unchanged).
