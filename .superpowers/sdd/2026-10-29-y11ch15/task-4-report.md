# Task 4 report: Lesson 15C The binomial theorem

Status: DONE_WITH_CONCERNS (minor, listed at the end). The past-paper set has 18 marks and runs 25 minutes.

Commit: `874d074 Y11Ch15: lesson 15C` on `ch10-pack`, not pushed.

## Negative-power ruling: decision
- **Exercise 15C uses negative powers.** Q15 asks for the term independent of x in (x + 1/x)^40 (x − 1/x)^40, which is (x² − x⁻²)^40. The book's answer is ⁴⁰C₂₀ ≈ 1.378 × 10¹¹ (PDF 945).
- So negative-power rows are **in scope** for the 15C set, as the spec allows.
- **Where the step is taught.** Concept 3 (l15c.html:100) teaches it before the past papers. It has:
  - a concept note: write each term as a power of x, as in 15B; the power changes by a fixed step; count the steps r; the term is ⁿC_r (first)^(n−r) (second)^r; and A^n B^n = (AB)^n for products;
  - a tutor demo, (x³ − 2/x)¹², and a your-turn, (x + 2/x²)⁹;
  - a worked example built on Q15: (x + 1/x)²⁰ (x − 1/x)²⁰, answer ²⁰C₁₀ ≈ 1.848 × 10⁵ (l15c.html:118).
- **Why not Q15 itself.** I changed 40 to 20 so the homework Q15 stays a real exercise. The spec says "a worked example taken from that exercise question". If the controller wants Q15 word for word, the swap is one block.
- **Notation.** No T_{r+1} general-term notation and no sigma notation (15E) appear anywhere. The solutions use only Box 3 and the step-counting of 15B Example 7.
- **Neg-power items used:** 4 of 8 (C18, C8, C13, C15), 9 of the 18 marks. C13, (x² − 1/x²)¹⁰, is the direct analogue of Q15.

## What I built

### `workspace/build/y11ch15/l15c.html` (lesson PDF pages 40–57 of 57)
- **Lesson head.** It has the eyebrow, h2 and focus line.
- **Concept 1, the binomial theorem** (l15c.html:5). It covers:
  - the entries of Pascal's triangle are ⁿC_r, in both notations;
  - the proof by counting words: the 16 words of (x + y)⁴ in an array, the six xxyy words = 4!/(2!2!), and the general count;
  - Box 3;
  - a tip box with the product form of ⁿC_r, "do not mix the two notations", and the term with y^r in brackets.
  - Tutor demo: 13C9, x⁴y⁵ in (x + y)⁹, A⁴B⁴ in (3A − 2B)⁸ in primes, and a^(n−3)b³ in (a − 3b)^n. Your turn is parallel.
  - Worked example 9 (l15c.html:41) is textbook Example 9(a)–(d), with full working.
- **Concept 2, ⁿC₀, ⁿC₁, ⁿC₂** (l15c.html:61). It has the formulae, the symmetry consequences and Box 4.
  - Tutor demo: ⁿC₂ = 66 and the sum = 37. Your turn: 28 and 16. The revision warm-up's 45 is avoided.
  - Worked example 10 (l15c.html:83) is textbook Example 10.
- **Concept 3** is described above.
- **Textbook homework** (l15c.html:127) is Exercise 15C Q1–20, copied word for word.
  - The bands follow the book: Foundation Q1–10, Development Q11–17, Enrichment Q18–20.
  - Every part is on its own line.
  - Nothing is omitted. Q7 (Pascal's rule, given in the question) and Q20 (power series) are part of the 15C exercise and need nothing from 15E.
- **Past-paper homework** (l15c.html:175): 8 questions, 18 marks, 25 minutes (1.5 × 18 = 27, rounded to 25). There is one hint per question, each a pointer or a starting idea.
- **Forward references.** I searched for 15D, 15E, "general term", "later" and "Pascal's rule". There are none.

### `workspace/build/y11ch15/a_15c.html` (answers PDF pages 10–13)
- **Order.** `{{ahead}}`, then Lesson Examples C1–C3 (each part on its own line), then Textbook Homework, then `{{ahead}}`, then the Past-Paper worked solutions.
- **Textbook answers.** They match the book (PDF 945, right column) for 1–15, 17, 19 and 20(b)(c).
  - 6(a) is printed as "both are 56 / both are 35", because the book prints one value for each pair.
  - Left out: 7(a), 12(c), 16 and 20(a), which are verify/show items, and 18. The book's Q18 text has a slip ("r = 2, 3, …, r − 1", which should end at n − 1). By house rule 6, I neither reproduce nor correct it.
- **Past-paper solutions.** Every solution uses Box 3, with nCr from the formula, and the 15B step-counting for negative powers. Each MC solution explains the choice.

### `workspace/checks/y11ch15_15c.py`
- It has 167 checks. Each one reads a printed value by template, and a template must match exactly once.
- The LaTeX parser handles {}^nC_r, \dbinom and n!.
- **Independent computation:**
  - expansions by repeated multiplication;
  - nCr by itertools enumeration (n ≤ 18) or by an additive Pascal table;
  - expressions in n compared with expanded powers for n = 4..12;
  - equations in n solved by trying n = 0..60, row by row;
  - Q12(b), Q6, Q7, Q14 and PP7 found by brute-force search;
  - Q19 by enumerating polygons;
  - Q20 with sympy `series`;
  - the 4-significant-figure values with exact integers;
  - prime factorisations with `factorint`.
- **Lesson items checked:**
  - the 16 words (all of {x,y}⁴, grouped by the number of y's);
  - every row of WE9 and WE10;
  - the Concept 2 formulae against subset counts;
  - the Concept 3 note and its worked example;
  - the results printed inside Q7, Q12(c), Q16 and Q20(a);
  - the bands;
  - the MC options and letters, marks, time, labels and hints.
- **Mutation test.** I made 23 mutations on scratch copies, through `Y11CH15_SRC`, across both files. Every one failed with exit 1.

### `docs/pp_selected_y11ch15.md`
- I added a `## 15C` section. It has the method, the 8 items with file and pages, and the rows not taken.

## Source pages used
- **Textbook** (Y11 book): PDF 752–757 (teaching, Boxes 3–4, Examples 9–10, Exercise 15C with band headings), rendered at zoom 1.6. Answers: PDF 945 right column, rendered at zoom 2.6 in halves. I checked every answer independently, and all agree with the book.
- **Past papers.** All paths are under `workspace/pp/Ext 1/`. I read each question page and solution page on the rendered page. I checked the covers of SGS 2020, SGS 2022, Killara 2023 (not used) and NBHS 2021. The other labels match ones already used in this repo.

| PP | Label (as printed in both PDFs) | Marks | File | Question → solution |
|---|---|---|---|---|
| 1 | Sydney Grammar School, 2020, Trial Examination, Form VI Mathematics Extension 1, Q2 (MC) | 1 | `2020/Sydney Grammar 2020 3U Trials & Solutions.pdf` | p2 → p10 (D, −48384) |
| 2 | Sydney Grammar School, 2022, Trial Examination, Form VI Mathematics Extension 1, Q7 (MC) | 1 | `2022/Sydney Grammar 2022 Extension 1 _ Solutions.pdf` | p4 → p20 (D, 5376) |
| 3 | Abbotsleigh, 2023, Higher School Certificate Assessment 4 Trial Examination, Mathematics Extension 1, Q11(c) | 2 | `2023/Abbotsleigh 2023 3U Trials & Solutions.pdf` | p8 → p19 (p = 5) |
| 4 | North Sydney Girls High School, 2023, HSC Trial Examination, Mathematics Extension 1, Q12(b) (1 + 2) | 3 | `2023/North Sydney Girls 2023 3U Trials & Solutions.pdf` | p10 → p30 (6Ck 2^(6−k) 3^k; 2016) |
| 5 | North Sydney Girls High School, 2020, HSC Trial Examination, Mathematics Extension 1, Q11(e) | 2 | `2020/2020 NSG.pdf` | p6 → p17 (489888) |
| 6 | North Sydney Boys High School, 2020, Year 12 Assessment Task 3, Mathematics Extension 1, Q11(b) | 3 | `2020/2020 NSB.pdf` | p7 → p16 (−252) |
| 7 | Hornsby Girls High School, 2023, Year 12 Higher School Certificate Trial Examination, Mathematics Extension 1, Q11(d) | 3 | `2023/Hornsby 2023 3U.pdf` | p6 → p15 (n = 9) |
| 8 | Normanhurst Boys High School, 2021, Year 12 Course Assessment Task 4 (Trial Examination), Mathematics Extension 1, Q11(d) | 3 | `2021/3U NBHS.pdf` | p5 → none (solved independently, checked) |

## Past-paper choice
- **Order:** two MCs, then easy items building up to the harder ones: find p, x^k with a product, two constant terms, a ratio for n, and a proof.
- **Reuse cross-check.** I read `PAST_PAPERS_USED.md` and every `pp_selected_*.md` (ch10, y11ch14, y11ch15) before choosing and again before committing. I also grepped the y11ch14 and ch1x builds, including Ch 14's uncommitted 14D work. None of the eight items appears. Other parts of these papers are used elsewhere: Abb23 Q7/Q9, NSG20 Q11(d)/Q13, NBHS21 Q11(e)(i), SGS22 Q12(a)/Q13 and NSG23 Q1/Q3/Q13. Those are different questions.
- **Controller rulings followed:**
  - no unprinted-title paper: C24 (NSB 2024) and C17 (2021 NSB, no cover) are not used;
  - no JRAHS 2021 mock;
  - neither flagged item;
  - A6 and A11 are not used;
  - C12 (Sydney Tech "Sample 3", solutions mislabelled) is avoided.
- **Not taken:**
  - C2 and C3 are the same skill as C1, and C3's answer (−489888) has the same size as PP5's;
  - B6;
  - the remaining neg-power rows, which are left free.

## Omitted, doubtful or noted
- **Exercise 15C Q18 printed answer.** It has a slip (see above). The answer is left out. Q18 itself is fine.
- **NSB 2020 Q11(b)** reads "in the expansion (x² − 1/x²)¹⁰", without "of" and without a full stop. It is kept as printed.
- **Q20(c)** prints "parts b i and ii". I wrote "parts b(i) and (ii)" to match the pack's part style.
- No textbook question was omitted.

## Verification
- **Check scripts.** `python3 workspace/checks/y11ch15_15c.py` → All OK, 167 checks, about 4 s. 15a, 15b and rev → still All OK.
- **Build:** `cd workspace/build && python3 build.py y11ch15 all && mv lesson.pdf answers.pdf y11ch15/`. The lesson PDF has 57 pages and the answers PDF has 13.
- **`qa.py`:** 0 problems on lesson.pdf and 0 on answers.pdf.
- **MathJax scan:** 0 hits in both PDFs.
- **Pages inspected:** lesson pages 40–57 and answers pages 10–13, all at zoom 1.0.
- **Free space.** Measured with PyMuPDF, the free space below content on lesson pages 40–57 is 3–20 mm on every page.
- **Fixes made along the way:**
  - A `\\(` inside aligned rows was read as an inline-math opener by `escape_math`. It is now written `\\ (`.
  - Commas after inline maths are moved inside the maths, so no line starts with a comma.
  - C2 parts are put on separate lines.
  - A page-break before the Enrichment band avoids a lone Q19 page.
- **Known layout choices.**
  - Answers page 11 is short (Q15–Q20), because the PP solutions start on their own `{{ahead}}` page. 15A and 15B have the same pattern.
  - The 15C Concept 3 your-turn box is large (120 mm), to fill page 45.

## Files changed
- `workspace/build/y11ch15/l15c.html` and `a_15c.html`, which replace the placeholders
- `workspace/checks/y11ch15_15c.py` (new)
- `docs/pp_selected_y11ch15.md` (adds `## 15C`)

Scratch work is in `/tmp/claude-0/-home-user-Hw/33fce1a1-283b-5e23-bc89-9ac277c110f5/scratchpad/work/y11ch15-t4/`.

## Concerns
1. The Concept 3 worked example is Q15 with 40 changed to 20, not Q15 verbatim (see the ruling section).
2. The textbook's Q18 answer has a slip, so that answer is left out of the answers PDF.
3. `cover.html` still has the `@@M15C@@` placeholder, which the controller fills. The value is "18 marks · 25 min".
4. The Concept 3 your-turn work box is generous (120 mm), so that page 45 is not half blank.

## Fix round 1
- **Q18 answer added** (`a_15c.html`, between 17 and 19). It is the pack's own short proof, with no mention of the textbook's slip:
  - the second member of row n is ⁿC₁ = n;
  - take n prime and 2 ≤ r ≤ n − 1; then ⁿC_r × r!(n−r)! = n! = n × (n−1)!;
  - every factor of r! and (n−r)! is less than n, so the prime n has no common factor with r!(n−r)!; hence n divides ⁿC_r;
  - also ⁿC₁ = ⁿC_{n−1} = n, so only the 1s at the ends are excluded.
  - It uses the house answer style, an `.a` block with line-height 1.85 for the inline factorials.
- **Check script** (`y11ch15_15c.py`):
  - 18 is removed from the no-answer list; the expected answer blocks now include 18.
  - New template checks read the printed lines "ⁿC₁ = n", "ⁿC_r × r!(n−r)! = n! = n × (n−1)!" (each side, n = 2..11, and the identity for all r) and "ⁿC₁ = ⁿC_{n−1} = n".
  - A new brute-force check confirms that n divides ⁿC_r for 1 ≤ r ≤ n − 1, for primes n = 2, 3, 5, 7, 11, 13 (subset enumeration).
  - A mutation of the printed "= n" to "= n − 1" fails with exit 1.
- **NSB 2020 Q11(b)** wording is unchanged.
- **Verification:**
  - `y11ch15_15c.py` → All OK, 170 checks. 15b and 15a → All OK. rev → 85 printed values, 0 failures.
  - Rebuild: the lesson PDF has 57 pages and the answers PDF has 13.
  - qa.py: 0 / 0 problems. MathJax scan: 0 hits in both PDFs.
  - Answers page 11 (Q15–Q20, with the new Q18) was inspected at zoom 1.1. It is clean.
- **Files:** `workspace/build/y11ch15/a_15c.html` and `workspace/checks/y11ch15_15c.py`.
