# Task 4 report: Lesson 13C Variance and standard deviation

Commit 13aeccc "Y11Ch13: lesson 13C" on branch ch10-pack (not pushed). I staged files by explicit path only: l13c.html, a_13c.html, workspace/checks/y11ch13_13c.py and docs/pp_selected_y11ch13.md. I did not edit l13b.html, a_13b.html or figs.py, and I touched nothing in ch17 or other chapters.

## Status: DONE_WITH_CONCERNS
The lesson is complete. The past-paper mini exam has **3 marks** (3 items). This is a house rule 8 shortfall: after a full sweep, no other clean school-paper item fits 13C (see "Past papers").

## What I built
**workspace/build/y11ch13/l13c.html** (lesson PDF pages 45–63)
- Lesson head (l.1–3).
- **Concept 1: the variance, first formula** (l.5).
  - Box "Measures of spread": the textbook's opening paragraph.
  - Box "The variance: first formula": the four-coin table and graph, with μ = 2 from Lesson 13B.
  - Box "Deviations from the mean": the deviation, the two reasons for squaring, and Var(X) = Σ(x − μ)²p(x).
  - Box "Setting out the calculation of variance": the 5-row table with the side notes (a check), (the mean μ) and (the variance).
  - Box "Using columns instead of rows": the transposed table, "Take your pick".
  - Box "The variance as an expected value": Var(X) = E((X − μ)²), with the Year 12 remark.
  - Tutor demo (l.49): an octahedral die, by the definition (μ = 4½, Var = 5¼). Your turn: a tetrahedral die (μ = 2½, Var = 1¼).
  - Worked example 5 = textbook Example 5 (l.55): the die, with the full table, 70/24 = 2 11/12.
- **Concept 2: the variance, alternative formula** (l.66).
  - Box "The variance: alternative formula": the turgid-fractions text, Σx²p(x) − μ² and E(X²) − μ².
  - Box "The four coins again, using the alternative formula": the x²p(x) table and the 5 − 2² = 1 working.
  - Box 7 (l.82).
  - **Extension: proof of the alternative formula** (l.91), labelled as the textbook labels it, with all six lines and their side notes.
  - Tutor demo (l.101): a die with faces 1, 2, 2, 3, 3, 3 (μ = 2⅓, Var = 5/9). Your turn: faces 1, 1, 2, 2, 2, 4 (μ = 2, Var = 1).
  - Worked example 6 = textbook Example 6 (l.107).
- **Concept 3: standard deviation** (l.118).
  - Box "Standard deviation": units, σ = √Var(X), the remark on the term, and proportionality.
  - Box 8 (l.126).
  - Tutor demo (l.133): the 13B pickpocket, finding the mean and standard deviation (μ = $65, σ ≑ $74.58). Your turn: the 13B thief (μ = $21, σ ≑ $19.21).
  - Worked example 7 = textbook Example 7 (l.139): the 13B robbery, Var = 25 360, σ ≑ $159.25.
- **Textbook homework, Exercise 13C** (l.152): all 14 questions, transcribed in full.
  - Bands: Foundation 1–3 (l.155), Development 4–11 (l.191), Enrichment 12–14 (l.225), as the book bands them.
  - Every table is an HTML table: Q1, Q2 (with blank cells), Q3 a–d (c and d in columns), Q4 i–iv (iii and iv in columns), Q5, Q6 J and L, and both Q10 tables.
  - The paired column tables (Q3c/d, Q4 iii/iv) sit side by side, as in the book. All question text parts are on separate lines.
- **Past-paper homework** (l.239): 3 items, 3 marks, 5 minutes (1.5 × 3 = 4.5, rounded to 5).
  - A one-line note: "These are the only school-paper items that need just this lesson's ideas. For more timed practice, do Questions 6 and 11 above in 15 minutes."
  - Each item has one hint (a starting idea).
- **Figure:** the four-coin graph reuses the existing `{{svg:c13b_coins}}`, which is the same graph in the same p(x) notation, with ticks 0–4. figs.py is unchanged.

**workspace/build/y11ch13/a_13c.html** (answers PDF pages 12–16)
- Order: ahead → Lesson Examples C1–C3 (l.2–46) → Textbook Homework (l.47) → ahead → Past-Paper Worked Solutions (l.128).
- The homework answers cover all 14 questions. Each answer has its book result, plus a short working line where useful:
  - Q3 parts and Q6 show E(X²).
  - Q8 shows the z fractions.
  - Q12 shows the working for b and c, and a comparison for d. The book has no answer for 12(d). Mine checks n = 3 against Q7 and n = 6 against Worked examples 5 and 6.
  - Q13 and Q14 give the book's proofs.
- The PP solutions are full working. Each MC answer explains why the other options are wrong.

## Source pages used
- **Y11 book**, PDF 661–669, each rendered at zoom 1.6 and read:
  - teaching pages 661–665: Examples 5–7, Boxes 7 and 8, and the extension proof;
  - Exercise 13C, pages 666–669, with the FOUNDATION / DEVELOPMENT / ENRICHMENT headings;
  - PDF 670, which confirms that 13D starts there.
- **Answers**: PDF 936 (right column, both halves) and 937 (both halves), rendered at zoom 2.
- **Past papers**:
  - PP 1: James Ruse Agricultural High School, 2020, cover "2020 YEAR 12 Trial HSC Examination, Mathematics Extension 1". Q1 (MC), 1 mark. File `2020/James Ruse 2020 3U Trials & Solutions.pdf`, question p2, answer key p10 (D).
  - PP 2: Baulkham Hills High School, 2020, "Year 12 Trial Examination 2020, Mathematics Extension 1". The file has no cover, so the title comes from the marking-guidelines header, as in 13A. Q12(a)(iii), 1 mark. File `2020/2020 Bauklham Hills.pdf`, question p7, solution p14 (0.84, by npq).
  - PP 3: Hurlstone Agricultural High School, 2023, cover "Higher School Certificate Trial Examination, Mathematics Extension 1". Q8 (MC), 1 mark. File `2023/Hurlstone 2023 3U.pdf`, question p3, solution p19 (B, 4/5).
  - All three covers and question pages were rendered and read. Each label is identical in both PDFs, and the 13A and Ch 14 labels for these schools were followed.

## Past papers: choice and sweep (house rule 8, spec thin-pool ruling)
- **A5, JR 2020 Q1** and **A6, Hurlstone 2023 Q8** were kept free for 13C (controller note). Both are solved as a two-value distribution with 13C methods.
  - "Bernoulli" is not in the Y11 book, so each hint defines it: X = 1 for success, 0 for failure. This follows the 13A Bin(4, p) hint pattern.
  - Order: PP 1 (direct variance) → PP 2 (variance from a table) → PP 3 (an equation in p).
- **C18, BHHS 2020 Q12(a)(iii)**, "Calculate Var(X)":
  - The stem supplies the results of part (ii), "a = 0.4116 and b = 0.2646" (house rule 2/5 pattern). The full table is then a given distribution, and Var(X) = E(X²) − μ² = 2.28 − 1.44 = 0.84. No binomial formula is needed.
  - This is the spec's allowed 17x case. 13A already used (i) and (iv) of the same Q12(a). (ii) is still free for Ch 17.
- **The rest of the catalogue**:
  - A7 and A3 are in the excluded JRAHS mock.
  - A4 (STHS 2021) is binomial standard form with typos (Ch 17 also treats it as doubtful).
  - The other 17B rows (C1, C3, C5, C6(ii), C8–C12, C14, C15(ii), C16, C17) all need Var = npq or np.
  - The 17D rows need Var(p̂), and the rest need the normal distribution.
- **My own sweep**:
  - I searched every text-layer school paper 2020–2024 for "variance", "standard deviation", "Var(" and "σ". I skipped NEAP, PEM, CSSA, Independent, TEC, the JRAHS mock, Western, Fort Street 2023 and NSB 2024.
  - Every hit is binomial, p̂, normal or the empirical rule, apart from the three items above. The script is at /tmp/claude-0/-home-user-Hw/33fce1a1-283b-5e23-bc89-9ac277c110f5/scratchpad/work/y11ch13-t4/sweep.py.
  - The scanned papers were checked by eye by the cataloguer, who found no general-distribution items.
- **Near-duplicates**: PP 1 and PP 3 are both Bernoulli. PP 1 is a direct numerical variance, while PP 3 sets up and solves E(X) = 5Var(X) for p. I judged them different enough. If the reviewer disagrees, dropping PP 1 leaves 2 marks.
- **Records read**: I read docs/PAST_PAPERS_USED.md and every docs/pp_selected_*.md (ch10, y11ch13, y11ch14, y11ch15 and the new ch17) before choosing and again before committing. None of the three items is used anywhere. Ch 17's 17A record lists "A1(ii) BHHS 2020 Q12(a)(ii)" as free. I took only (iii).
- **Record**: docs/pp_selected_y11ch13.md, section 13C. Ch 17 marks taken by 13C: 17B 1 (C18).
- The cover placeholder `@@M13C@@` is left for Task 6. It should read 3 marks.

## Fidelity notes, fixes and omissions
- Nothing is omitted from the teaching pages or the exercise. I found no doubtful exercise items, and all data are consistent.
- **Printed textbook answer slip**: in the Q2(a) answer table (PDF 936), the xp(x) cell for x = 2 is printed as 0.1. It is 0.5 × 2 = 1, and the row's sum of 2 confirms this. I printed 1 with no remark.
- **Rounding shown**: the book gives Var(J) = 2.05 and σ = 1.45 / 1.06 with "=". I print Var(J) = 2.0475 ≑ 2.05 and σ ≑ 1.45 / 1.06.
- **Corrections made with no remark:**
  - The standard deviation text says "proven in the Enrichment section of Exercise 13C (Questions 12–14)". I print "(Questions 13 and 14)", because Q12 is the uniform distribution and the proportionality proofs are Q13–14.
  - Example 7 "Example 3 Section 13B" is printed as "Worked example 3 of Lesson 13B (the restaurant robbery)".
  - "Example 5" and "Example 7" in the prose are printed as "Worked example 5" and "Worked example 7".
  - "In the last section, the expected value…" is printed as "In Lesson 13B, the expected value…". "At the start of this section" is kept as printed, following 13B.
- **Typographic fixes:**
  - Q4(iv) table header "p(W = w)" is printed as P(W = w), like the other three.
  - Q12(a) "What is the probability of P(X = k)" is printed as "What is the probability P(X = k)".
  - Em dashes in the book's prose became colons or full stops. Examples: "its mean, was found", "Take your pick: use the layout…", the "Variance — first formula" headings, Q10(c), and the Q4b and Q10f answers.
- **Textbook figure (PDF 661)**: the four-coin graph has the same tick slip as on PDF 643 and 652 (labels 1–5 under dots at 0–4). The reused c13b_coins labels the ticks 0–4.
- **Layout**: box titles such as "Deviations from the mean", "Setting out the calculation of variance" and "The four coins again, using the alternative formula" are mine. They split the book's long passages so that headings stay with their boxes. The text inside is the book's.
- **Demos and your-turns**: all six are new value-changed variants. The C3 pair reuses the 13B cash statements, now asking for σ. The worked examples are the textbook's Examples 5–7.

## Verification
- `python3 workspace/checks/y11ch13_13c.py`: **173 checks, all OK**, exit 0.
  - **Tables**: every table is read cell by cell, skipping the side notes. Each p, xp, (x−μ)², (x−μ)²p, x² and x²p cell and each Sum is recomputed with Fraction. Var is computed by both formulas, which must agree. σ is checked to the printed number of decimals.
  - **Distributions**: these are enumerated from the printed statements:
    - the coins, and the dice face lists;
    - the octahedral and tetrahedral dice;
    - the friends' cash;
    - the Q7 spinner;
    - Worked example 7, whose data comes from the statement of 13B Worked example 3 in l13b.html, read only.
    - The question data comes from the printed question tables.
  - **Q8 and Q9**: the z-scores are parsed from the statements, and the verdict words are checked.
  - **Q10**: the outlier z-score of 3.2 is checked, and so is the correction moving 0.05 from 8 to 5.
  - **Q11**: k is solved with sympy.
  - **Q12**: checked with sympy summation, including the n = 3 and n = 6 comparisons.
  - **Q13 and Q14**: E(kX + a) = kE(X) + a and Var(kX + a) = k²Var(X) are verified on all 24 lesson distributions, and the key proof lines are checked.
  - **Past papers**:
    - PP 1: the Bernoulli table, the answer D and the explanations of the other options.
    - PP 2: p is recovered from P(X = 4) = p⁴, the table and the supplied a and b are checked against Bin(4, 0.3), Var = 0.84 is checked from the table and equals 4pq.
    - PP 3: sympy solves p = 5p(1 − p) with p ≠ 0, giving answer B, and the claims about options A, C and D are checked.
    - Labels are identical in both files, the total is 3 marks and 5 minutes, and each item has one hint.
  - **Structure**: 3 concepts, the named boxes, Boxes 7 and 8, the extension, 3 demos, 3 your-turns, WE5–7, answer blocks C1–C3 and 1–14, bands F 1–3 / D 4–11 / E 12–14, the figure data via figs.build_13b(), and no literal "$".
- **Mutation tests**: 19 single edits in copies run through Y11CH13_SRC. **All 19 were detected** (exit 1, MISMATCH). The edits covered:
  - answer table cells, chains, σ roundings, k, the Q12 formula and the MC letter;
  - statement data: the pickpocket count, the dice faces, the Q1 table, the PP 2 b value, a Q9 mean and the Q8 μ;
  - the WE7 x²p cell, the WE5 result and the pp-intro time.
  - The script is at /tmp/claude-0/-home-user-Hw/33fce1a1-283b-5e23-bc89-9ac277c110f5/scratchpad/work/y11ch13-t4/mut.py.
- **Other checks**: y11ch13_13a.py gives 192 checks OK, y11ch13_13b.py gives 141 OK, and y11ch13_rev.py has 0 failures.
- **Build**: `cd workspace/build && flock …/scratchpad/build.lock sh -c 'python3 build.py y11ch13 all && mv lesson.pdf answers.pdf y11ch13/'`.
- **qa.py**: lesson.pdf has 63 pages and 0 problems; answers.pdf has 16 pages and 0 problems.
- **MathJax scan** (7 error strings, PyMuPDF get_text) over both PDFs: 0.
- **Pages inspected**: lesson 45–63 and answers 11–16 as contact sheets, with zooms of p45, p52 and answers p13 and p15.
  - There are no clipped tables or overflowing displays, and headings are kept with their boxes.
  - I resized the work boxes: Q3 110 mm, Q7 32, Q8 30, Q9 28, Q13 100, C2 demo and your turn 64, pickpocket demo 54, PP 16/28/24.
  - I also split two long boxes so that the concept headings stay with their first box.
  - The emptiest pages:
    - p45 is about 75% full: the "Deviations" box does not fit under the opening boxes.
    - p53 (Worked example 7) is about 45% full, followed by the page break before the homework, as in 13B.
    - p63 (PP 2 and PP 3) is about 70% full, at the end of the lesson.

## Files changed
- workspace/build/y11ch13/l13c.html, workspace/build/y11ch13/a_13c.html
- workspace/checks/y11ch13_13c.py (new)
- docs/pp_selected_y11ch13.md (13C section)

## Concerns
1. **3 past-paper marks** (house rule 8 shortfall). No other clean item exists (sweep above). The note points to Exercise 13C Q6 and Q11 for 15 more minutes of timed practice.
2. **PP 1 and PP 3 are both Bernoulli items** (direct variance versus solving for p). I kept both. Dropping PP 1 would leave 2 marks.
3. **PP 2 supplies the results of part (ii)** (a and b) in the stem, so that only the 13C table method is needed. The school's solution uses npq, and mine computes the same 0.84 from the table.
4. **Silent corrections**: one textbook answer slip (Q2(a) xp cell) and one cross-reference ("Questions 12–14" changed to "13 and 14"). Details are above.

---
# Fix round (review of 13C)

Commit "Y11Ch13: 13C hint fixes" (not pushed). The only file changed is workspace/build/y11ch13/l13c.html, past-paper hints at l.248, 256 and 261. I did not touch l13d.html, a_13d.html or the answers.

1. **REQUIRED, PP 3 hint** (Hurlstone 2023 Q8). The hint now gives only the definition: "a Bernoulli variable takes the value 1 with probability p and the value 0 otherwise, as in PP 1." I dropped "Write each side of the given equation in terms of p."
2. **PP 1 hint** (JRAHS 2020 Q1). It is now a pure definition: "a Bernoulli trial has two outcomes: success (the value 1) and failure (the value 0)."
   - My first wording ran to two lines. That pushed the whole past-paper block to a new page and left PP 3 alone on a page.
   - The final wording fits on one line, and the reviewed layout is back.
3. **PP 2 hint** (BHHS 2020 Q12(a)(iii)). It now reads: "think about what the table now gives you."
4. **C3 demo data**: left as it is, as ruled.

## Verification
- `python3 workspace/checks/y11ch13_13c.py`: 173 checks, all OK.
- Build with flock: lesson.pdf has 63 pages, answers.pdf has 16 pages.
- qa.py: 0 problems in each PDF. MathJax scan: 0 errors in both.
- Pages inspected: lesson 61–63.
  - p62: Q14, then the past-paper heading, intro and PP 1.
  - p63: PP 2 and PP 3.
  - The hints are on one line each, and nothing overflows.
