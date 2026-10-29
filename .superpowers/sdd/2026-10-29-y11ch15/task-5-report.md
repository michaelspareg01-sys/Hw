# Task 5 report: Lesson 15D Identities in Pascal's triangle, and the Chapter 15 review

Status: DONE_WITH_CONCERNS (see Concerns). Commit `06f4cde` "Y11Ch15: lesson 15D" on `ch10-pack` (not pushed).

## What I built
`workspace/build/y11ch15/l15d.html` (replaces the placeholder)
- Lesson head (l.1-3).
- Concept 1, patterns and three methods of proof (l.5-58): the textbook's interpretation text, the n\r table for rows 0-10, the "Methods of proof" box (combinatorics, substitution into (x+y)^n and (1+x)^n, the addition property), and a "sum of a row" box with the n = 5 example. Tutor demo / Your turn: substitute x = 3 (x = 4) to get the 4^n (5^n) identity, check it on a row, and explain 8C3 = 8C5 (9C2 = 9C7) by counting. Worked example: the textbook's own three proofs that the row sum is 2^n (combinatorics with the 2 x 2 x ... x 2 table, substitution, addition property). 15D has no numbered Examples or boxes, so this in-text example is the only textbook example.
- Concept 2, differentiating then substituting (l.60-94): the "further approaches" bullet, and the derivative of each term. Tutor demo n = 5 and Your turn n = 3 (x = 1 and x = -1, checked on the row). Worked example (my own, since the textbook has none): differentiate, put x = 2, get the n 3^(n-1) identity, check n = 3.
- Concept 3, the formula for nCr and equating coefficients (l.96-124): both remaining "further approaches". Tutor demo: r nCr = n (n-1)C(r-1), and the x^2 coefficient in (1+x)^2(1+x)^n. Your turn: (n-r) nCr = n (n-1)Cr, and the x^3 coefficient. Worked example (my own): nC(r+1)/nCr = (n-r)/(r+1), and mC2 + mC1 nC1 + nC2 = (m+n)C2 (checked for m = 3, n = 4).
- Textbook homework (l.126-179): Exercise 15D Q1-14 verbatim, bands F 1-3 (l.129), D 4-10 with the band's intro sentence (l.142), E 11-14 (l.170). Q12(d) is left out (see Omitted).
- Past-paper mini exam (l.181-221): 7 items, 16 marks, 25 min.
- Chapter 15 review (l.223 onward): a new `.lesson` block after the PP section, as in the Ch 10 model. Questions 1-13, all in scope, with parts on separate lines.

`workspace/build/y11ch15/a_15d.html` (replaces the placeholder)
- `{{ahead:Lesson 15D | ...}}`, then Lesson Examples C1-C3 (l.2), then Textbook Homework (l.10). It answers Q1, 4, 5, 6, 7, 8, 9, 10 and 12, the items the textbook answers (Q12 has a-c only). Q2, Q3, Q11, Q13 and Q14 are show-that items with no textbook answer.
- Then `<div class="ans-sec">{{ahead:Chapter 15 Review | Chapter review exercise}}</div>` (l.40, the Ch 10 form) with review answers 1-13.
- Then `{{ahead:Lesson 15D | ...}}` and the PP worked solutions (l.58-59 onward).
- The review answers come before the PP solutions, as in Ch 10's `a_10b.html`.

`workspace/checks/y11ch15_15d.py`: 285 checks, all OK. More below.

`docs/pp_selected_y11ch15.md`: a `## 15D` section with all 7 items and the items not taken.

## Sources used
- Textbook (Y11 book, PDF = printed + 24): 15D teaching PDF 758-759, Exercise 15D PDF 760-763 (p763's lower half is a garbled letter block, not content), Chapter review PDF 767-768. Answers: 15D on PDF 946, review on PDF 947, rendered in halves at zoom 2.
- Past papers, in lesson order. All are 2 or 3 marks, and paths are under `workspace/pp/Ext 1/`. I checked each one on the rendered page.

| PP | School, year, title as printed, Q | Marks | File | Question page | Solution |
|---|---|---|---|---|---|
| 1 | North Sydney Boys High School, 2020, Year 12 Assessment Task 3, Mathematics Extension 1, Q14(a) | 2 | `2020/2020 NSB.pdf` | p11 | p24 (handwritten, x = 1) |
| 2 | Sydney Boys High School, 2020, Year 12 Term 3 Trial HSC, Mathematics Extension 1, Q14(c)(i) | 2 | `2020/2020 SBHS 2.pdf` | p11 | p37 |
| 3 | Killara High School, 2021, Year 12 Mathematics Extension 1 Trial Examination, Q13(e) | 2 | `2021/3U Killara.pdf` | p12 | p31 (2^99) |
| 4 | Blacktown Boys' High School, 2024, HSC Trial Examination, Mathematics Extension 1, Q12(d) | 2 | `2024/Blacktown Boys 2024.pdf` | p5, right half | p11, left half (p = 2025, q = 102 or 1923) |
| 5 | Pymble Ladies' College, 2023, Mathematics Extension 1 HSC Trial Examination Term 3, Q14(b) | 2 | `2023/PLC 2023 3U.pdf` | p12 | none; solved independently and enumerated |
| 6 | Kinross Wolaroi School, 2023, Year 12 Mathematics Extension 1 Trial HSC Examination, Q14(d) | 3 | `2023/2023 Kinross-Wolaroi Ext 1.pdf` | p11 | none; solved independently |
| 7 | North Sydney Boys High School, 2023, Year 12, Assessment task 3, Term 2, Mathematics Extension 1, Q14(c) | 3 | `2023/NSB 2023 3U.pdf` | p9 | p40-41 (handwritten, (n+1)^n/n!) |

- Every label keeps `Extension&nbsp;1,&nbsp;Q...` together, or `...Term&nbsp;3,&nbsp;Q` for PLC.
- I took the cover titles from the rendered covers. The NSB 2023 cover has only a crest, but the page header prints "North Sydney Boys High School".
- I checked every item against `docs/PAST_PAPERS_USED.md` and every `docs/pp_selected_*.md`, three times: before choosing, after writing, and just before committing. I also checked the in-progress Ch 14 file `l14e.html`, which uses none of these items.
- I claimed the items in the working tree early, since Ch 14 reads the same directory.
- NSB 2020 Q14(a) is Ch 14 catalogue row E12. Ch 14 had not taken it, so it is now recorded as used by 15D.

## Omitted or rejected, and why
- **Exercise 15D Q12(d), omitted as doubtful (house rule 6).** As printed, "(2nC0)^2 + (2nC1)^2 + ... + (2nC2n)^2 = 2nCn" is false: at n = 1 it gives 1 + 4 + 1 = 6, not 2C1 = 2. The intended identity is the one in Q11, (nC0)^2 + ... = 2nCn, and the textbook answer is muddled the same way. Q12(a)-(c) are kept. Nothing in student material says why (d) is missing.
- **Chapter review: no question omitted.** All 13 are within 15A-15D. None needs 15E. Q10 (14C8, 14C7) uses only the 15C theorem.
- **Past papers not taken:**
  - D3, STHS 2023 Q13(e): same method as D2, so a near-duplicate.
  - D4, NBHS 2023 Q11(d): written in sigma notation, which this pack does not teach.
  - D5, Hornsby 2023 Q11(e): (ii) needs induction (brief), and (i) is Ch 14 row E26, left for Ch 14.
  - D9, Kings 2021 Q14(a): (i) has the misprint (controller ruling), and (ii) is Ch 14 row E11.
  - Killara 2021 Q7 (Ch 14 row E6): left for Ch 14.
  - D10(ii), SBHS 2020 Q14(c)(ii), 3 marks: **doubtful**. The school solution ends with "(n+2)2^(n-2)". Its own previous line, 2^(n-1)(2n+2-n), equals (n+2)2^(n-1). For n = 1 (letters a, b, c, choose 1) there are 3 ways, and (n+2)2^(n-2) gives 1.5. Following the Ch 14 precedent (JRAHS 2020 Q14(c)), I did not use it. Only (i) is used.

## Small typographic fixes (please confirm; same kind as the "to to" ruling)
- Ex 15D Q12(a): "occuring" printed as "occurring".
- Ex 15D Development intro: "an r-member subsets" printed as "an r-member subset".
- Review Q6: the textbook says "Check your answers against Pascal's triangle you developed in Exercise 16A", which is a wrong cross-reference. It is printed as "Check your answers against Pascal's triangle.", matching l15c Q1.
- PP7 (NSB 2023): the first bracket is printed "(a_o + a_1)" with a letter o. It is shown as a_0.

## Textbook answer slips: own correct answers printed with no remark (15C Q18 precedent)
- Review Q4(b): the book writes "1 + 7 x 0.2 + ...". Printed: "1 + 7 x 0.02 + 21 x 0.0004 + ... = 1 + 0.14 + 0.0084 + ...; first decimal place 1".
- Ex 15D Q9(b)(i): the book's "This makes 353-member subsets" (a typesetting slip) is printed as "This makes 35 subsets with 3 members".
- Ex 15D Q7(a): the book gives no answer. I give both sides for each of the five sequences.
- Ex 15D Q7(c): I add the simplified fractions r/(n+1), (r+2)/(n+1) and (r+1)/(n+1).
- Ex 15D Q12(c)(iii): the book gives no answer. I give 5C2 x 5C2 = 100.
- Review Q1: I print the rows. Review Q13(c): I give the two row-5 checks, 80 and 160.

## Verification
- `python3 workspace/checks/y11ch15_15d.py`: 285 OK, "All OK", exit 0. It reads the printed values from both HTML files and checks them against independent computation:
  - the Pascal table, against subset counts;
  - every printed identity (lesson, exercise, review, PP), by brute force over n, r and m;
  - subset lists, against itertools;
  - the committee table (PP5), by enumeration;
  - the PP4 large binomials, with exact integers;
  - the PP7 product, from the actual coefficients;
  - the review expansions, by repeated multiplication;
  - structure: marks 16 (15-22), 25 min, numbering, labels in both files, one hint each, bands, review numbering, answer blocks.
- Mutation tests in my scratch copy (Y11CH15_SRC): I changed one printed value at a time in 15 places. Every change made the script exit 1, with one mismatch each. The values changed were review Q10, PP4 q, the A9 total, a table cell, the R4 decimal, AC1 256, an A7 fraction, the PP7 result, an A6 set, the PP5 table, a C3 identity, AC2 80, and PP marks.
- The other checks still pass: y11ch15_15a, 15b, 15c and rev all OK (rev: 85 values, 0 failures).
- Build `python3 build.py y11ch15 all`: lesson 80 pages, answers 19 pages.
- `qa.py`: 0 problems on both PDFs.
- MathJax and leftover-tag scan (the listed error strings plus "<p>"): 0 on both PDFs. I fixed one `\\(` row-separator bug found this way.
- Pages inspected:
  - lesson pp. 58-80, all of them, after the final layout;
  - answers pp. 14-19.
- I resized the work boxes so that each page has two questions where they fit, with no stranded headings and no clipped maths.

## Concerns
1. Exercise 15D Q2a(ii), a(iii) and b(iii) are printed for general n without "n >= 1" or "n >= 2". At n = 1, b(iii) gives 1 = 0. Q8 states "for n >= 1" for (2), but Q2 does not. I judged this the textbook's usual implied condition and kept the questions verbatim. They have no printed answer. Please rule if you think this is doubtful under house rule 6.
2. The worked examples for Concepts 2 and 3 are my own, because 15D has no numbered examples. Each uses a different identity from any exercise or PP item.
3. Answers PDF p.17 holds only review answers 11-13. The past-paper section's `{{ahead}}` forces a new page after it.
