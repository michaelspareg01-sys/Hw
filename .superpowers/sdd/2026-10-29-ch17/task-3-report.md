# Task 3 report: Lesson 17B Binomial distributions

Status: DONE_WITH_CONCERNS (minor; see Concerns)

## What I built
`workspace/build/ch17/l17b.html` (placeholder replaced), in the house lesson layout copied from 17A.
- Lesson head (l17b.html:6-8). The focus line is the textbook's opening paragraph plus one summary sentence. A small `<style>` block at the top (l.1-5) sets the font size and padding for wide tables (`table.t.t17b`) and the figure widths (`.wide17b`, `.big17b`).
- Concept 1, notation and the Bernoulli distribution (l.12). It has the notation box, Box 2, and the Bernoulli mean and variance statement. Then a tutor demo (writing B(n, p); a Bernoulli Y ~ B(1, 0.35) by ΣyP and Σy²P − μ²) and a your-turn (Y ~ B(1, 0.8)). The worked example is the textbook's Bernoulli proof, tagged "Worked example / From the text" (l.38), as 17A did with its die example.
- Concept 2, mean and variance of B(n, p) (l.47). It has the text, the lemma with both proofs, the proofs that the mean is np and the variance is npq, Box 3 and the notation note. Then a tutor demo (n = 25, p = 0.2), a your-turn (n = 18, p = 1/3), and Worked example 6 (l.107).
- Concept 3, conditions on the mean and standard deviation (l.126). This holds Example 7. Its short concept box is pack-written (the textbook has no text between Box 3 and Example 7), and so is a tip box "Finding n and p from μ and σ²" (q = σ²/μ). The PP items need that method. The tutor demo (n = 400, p = 0.1) and the your-turn (n = 225, p = 0.2) are parallel to Example 7, and each has a part d on the tip. Worked example 7 is at l.149.
- Concept 4, skewed and non-skewed distributions (l.170). It has the text with the three dot graphs (20 coins; 20 dice with success 'six' and 'not six'), Box 4 and Worked example 8 (l.206). The tutor demo (100 trials, p = 1/2 and 1/5) and the your-turn (48 trials, p = 1/2 and 1/4) ask for the ratio of the SDs, the shapes, and the reversed variable Z.
- Concept 5, simulating and graphing (l.217). It keeps the textbook's spreadsheet note and adds one sentence saying the simulation results are given, so the rest can be done with a calculator (spec ruling). The tutor demo (8 coins) and the your-turn (8 dice, success '5 or 6') each come with pack-made 100-run frequency tables. Worked examples 9 (l.242) and 10 (l.260) have the book's tables and the four histograms with polygons.
- Textbook homework, Exercise 17B (l.279), verbatim, with the book's numbers and bands:
  - Foundation: Q1-6
  - Development: Q8-11
  - Enrichment: Q14 (the stem and part d only) and Q15
  - The omissions are listed below.
- Past-paper homework (l.320): 10 questions, 21 marks, 30 minutes, ordered from accessible to demanding, with 4 MC items and one starting-idea hint per question.

`workspace/build/ch17/a_17b.html` (placeholder replaced), in this order:
- the ahead heading
- Lesson Examples C1-C5 (l.11)
- Textbook Homework (l.71)
- the ahead heading again
- Past-Paper Worked Solutions PP 1-10 (l.123)

A small style block (l.1-8) sizes the paired histograms and two answer figures.

Figures: `workspace/build/ch17/figs_17b.py` (new; it imports Fig/save from figs.py, as figs_17a.py does). Run it with `python3 workspace/build/ch17/figs_17b.py`. It writes 14 SVGs:
- lesson: c17b_coin20, c17b_die20, c17b_die20r (dot graphs), c17b_ex9a/b and c17b_ex10a/b (histograms with polygons), c17b_q6 (Q6 polygon on a grid);
- answers: a17b_d_th/sim and a17b_y_th/sim (C5 histograms), a17b_q6e (p = 0.75), a17b_q11 (σ² against p).

Record: `docs/pp_selected_ch17.md`, new section `## 17B`.

## Sources
Textbook (Y12 CMS6 Ext 1): 17B teaching on PDF 811-818, Exercise 17B on PDF 818-822, answers on PDF 960 (right column) to 961. I rendered and read every page, and zoomed in on the lemma, Box 4 and Example 7c.

Past papers. Each entry gives the school, year, title as printed, Q, marks, file, question page and solution page.
1. Abbotsleigh, 2024, Higher School Certificate Assessment 4 Trial Examination, Mathematics Extension 1, Q1 (1, MC). `2024/Abbotsleigh 2024.pdf`, question p3, solution p18 (B).
2. James Ruse Agricultural High School, 2020, Year 12 Trial HSC Examination, Mathematics Extension 1, Q6 (1, MC). `2020/James Ruse 2020 3U Trials & Solutions.pdf`, question p3, solution p10 (key only, C).
3. Blacktown Boys' High School, 2023, Year 12 Trial Examination, Mathematics Extension 1, Q5 (1, MC). `2023/Blacktown Boys 2023 3U.pdf`, question p3, solution p16 (D, 0.36).
4. The King's School, 2021, Year 12 Alternative Higher School Certificate Trial Examination, Mathematics Extension 1, Q12(c)(i)(ii) (1+1). `2021/3U Kings.pdf`, question p9, solution p22 (8000; σ = 40). (iii) is left free for 17C.
5. Baulkham Hills High School, 2023, Higher School Certificate Trial Examination, Mathematics Extension 1, Q11(c)(ii) (2). `2023/Baulkham Hills 2023 3U.pdf`, question p6, solution p14 top (5, 25/6). The catalogue says p13, but p13 has only (i). (i) is used in 13A, so the stem supplies its result: "In an earlier part of the question, it was found that the probability of a sum of 7 is p = 1/6." This is the 13C wording.
6. Hurlstone Agricultural High School, 2023, Higher School Certificate Trial Examination, Mathematics Extension 1, Q13(c)(i) (1). `2023/Hurlstone 2023 3U.pdf`, question p9, solution p26 (positive skew since p < 0.5). The z-table extract printed below (ii) belongs to (ii), so it is not reproduced. (ii) (17D) is left free.
7. Knox Grammar School, 2022, Higher School Certificate Trial Examination, Mathematics Extension 1, Q6 (1, MC). `2022/Knox 2022 3U Trials & Solutions.pdf`, question p2 (right half), solution p7 (D, n = 16).
8. Blacktown Boys' High School, 2022, HSC Trial Examination, Mathematics Extension 1, Q13(d) (2). `2022/Blacktown Boys 3U Maths Paper _ Solutions 2022.pdf`, question p10, solution p22-23 (0.638).
9. Sydney Technical High School, 2023, Extension 1 Mathematics, Trial HSC, Q12(a) (2+1+1+2 = 6). `2023/Sydney Technical 2023 3U.pdf`, question p10, solution p22 (handwritten: p = 2/3, n = 18, a die showing more than 2, 0.000126...).
10. Moriah College, 2023, Trial Higher School Certificate Examination, Mathematics Extension 1, Q12(a) (1+3). `2023/Moriah 3U 2023 Paper w_ Solutions.pdf`, question p13, solution p24 (3/(8+k); k = 3).

Every label matches the label already used for that paper in other packs (17A, Ch 12, Y11 Ch 13/14/15). I re-read every `docs/pp_selected_*.md` file and `docs/PAST_PAPERS_USED.md` before choosing and again just before committing. I also checked the in-progress Y11 13D lesson, which uses BBHS 2024 Q2. None of my ten items is used anywhere else.

## Omitted, rejected, and silent fixes
Textbook homework omissions. The numbering keeps the book's numbers, as in Y11 14E.
- **Q7** (Technology, BINOM.DIST in Excel): omitted under the spec's spreadsheet ruling. It is all spreadsheet work.
- **Q12** (doubtful, house rule 6): a fair coin is tossed n times, and the question counts "columns entirely contained in the interval one standard deviation or less from the mean". The book's answers 4, 6, 8 only work if each column spans [k, k+1]. With columns centred on the labels, as in the book's own histograms (Examples 9 and 10), the answers are 3, 5 and 7. For example, for n = 16 the interval [6, 10] contains the columns at 7, 8 and 9 only. Please rule.
- **Q13**: omitted because it says "Continuing with Question 12 above" and depends on Q12's set-up. It also has a typo ("number of column").
- **Q14 a-c** (doubtful): part a prints "P(X > 1) = 1 − (1 − p)^n", where it should be P(X ≥ 1). The table in part c lists p = 0.5 twice (0.8 ... 0.1, 0.5). I kept the stem and part d, which stand alone, labelled d as in the book.

Answer blocks:
- Answers are given for 1-6, 8-11, 14d and 15.
- Q11c and Q15a(i)(ii) are "show that" items, so they are left out.
- Q15a(iii) gets μ = 1/p (the "hence calculate μ" result).

Silent fixes in the textbook's teaching part. These are copied worked material, so I followed the house ruling: print the correct version and report it.
- Lemma b is printed in the book as "x(x − 1) × nCx = n(n − 2) × n−2Cx−2". The proof directly below gives n(n − 1), and I print n(n − 1).
- The variance proof has a doubled "+ +" in the bracket. I print one.
- Example 7c ends "(roughly, greater than 9.99)". I print "greater than 0.99", which matches the root 0.9899.
- Example 8 prints "σ_X = 3" in the Y column. I print σ_Y = 3.
- Box 4 has two fixes:
  - "symmetric about x = ½" becomes "x = ½n", matching the first bullet and the coin example.
  - "the standard deviation gets closer to 0 or 1 as the skewness becomes more pronounced" becomes "the standard deviation gets smaller as p gets closer to 0 or 1, that is, as the skewness becomes more pronounced". This matches the text before Example 8 and Q11.
- The dice reflection line prints "P(7 heads) = ... = P(13 non-heads)" for a die. I print "P(7 sixes) ... P(13 non-sixes)".
- Example 9 prints "s ≐ 1.700". The data give 1.699 to 3 d.p. (population SD; the sample SD is 1.708). I print "s ≐ 1.70", which is 2 d.p. as in Example 10's "s ≐ 1.13". The check script confirms that 1.70 and 1.13 are the population SDs.
- "in Section 15E" becomes "in Section 15E (Year 11)". Em dashes in the textbook prose became colons.

Q2 table: the book's second row header reads "Number of ways can occur probability", which is two rows run together. I print two rows, "Number of ways can occur" and "Probability".

Book answers I did not copy. I solved every item myself and print my own result, without saying the book is wrong:
- 1d: the book says "number of heads", but the question asks for tails. I print tails, with p = 0.6.
- 2a: the book prints 0.23 for x = 4. I print exact fractions.
- 3a: the book prints 4/32 for x = 1, where the value is 5/32.
- 3c: the question asks for 3 d.p., and I print mean 1.154 and SD 0.942 (the book has 1.15 and 0.94).
- 9: the book says 74 is "2.6σ" above the mean, which comes from rounding σ to 4.3 first. I print 2.53σ, from σ ≐ 4.35. The conclusion (Team A) is unchanged.

Past-paper changes:
- BHHS 2023: the result of (i) is supplied in the stem. "Two fair six-sided dice ..." is kept as printed.
- Hurlstone: the z-table extract is not reproduced, because it is for (ii), which is not included.
- BBHS 2023 Q5: "variance of X is 144" is printed without "the", as in the paper.
- Notation as printed: "Bin(n, p)" (BBHS, Knox, STHS) and the binomial coefficient (15 choose k) (JR). The JR hint explains that (15 choose k) means 15Ck.

Rejected or left free 17B rows:
- C1 Caringbah 2020 Q11(e) and C9 BBHS 2022 Q11(c): the same skill as STHS 2023 Q12(a)(i)(ii) and BBHS 2023 Q5, so left free.
- C3: Sydney Tech 2020 sample paper, with sloppy wording.
- C4: Western 2020, an excluded paper.
- C5 Caringbah 2021 Q10: the same skill as Abbotsleigh 2024 Q1, so left free.
- C7: JRAHS 2021 mock, an excluded paper.
- C17 St Aloysius 2024 Q7: the file has no solutions.
- C18: used in 13C.
- A1(ii) BHHS 2020 Q12(a)(ii): still free (needs "p = 0.3" supplied).

## Verification
- `python3 workspace/checks/ch17_17b.py` reports **413 checks, 0 failed, ALL OK**. The script reads every printed value from l17b.html, a_17b.html and the 14 SVGs. Each template must match exactly once, or the check FAILs. It recomputes each value independently:
  - distributions of coins, dice and cards by enumeration (2^n, 6^n, a 52-card deck, two dice for the sum of 7);
  - larger n by Fraction + math.comb, cross-checked by convolution;
  - every mean and variance from ΣxP and Σx²P − μ² of the distribution itself;
  - the lemma for every n ≤ 14, and E(X(X − 1)) = n(n − 1)p² by enumeration;
  - the simulation statistics from the frequency tables printed in the lesson;
  - roundings half-up;
  - n and p found by search, the quadratic roots with sympy, and the smallest k (PP10) by exact search;
  - the geometric mean 1/p by partial sums;
  - SVG column and dot heights proportional to the probabilities and the relative frequencies, the Q6 polygons and their peaks, and the parabola vertex.
  It also checks the lesson structure (concept blocks, worked example tags, question numbers and bands, Q14 part d only) and the past-paper structure: 21 marks in the range 15-22, 30 min = 1.5 × 21 rounded to 5, part marks, numbering, labels identical in both files, one hint each, and the MC letter being the only option equal to the value.
- Mutation test: a copy with six planted errors (C2c rounding, Q5a, PP9, a C5 f_r, a your-turn frequency datum, an SVG column height) gives 10 FAILs. Every planted error is caught.
- Build: `cd workspace/build && flock .../build.lock sh -c 'python3 build.py ch17 all && mv lesson.pdf answers.pdf ch17/'`.
  - lesson.pdf has 56 pages; 17B is pp 33-56.
  - answers.pdf has 12 pages; 17B is pp 7-12.
- `qa.py`: lesson 0 problems, answers 0 problems.
- MathJax error scan (all seven strings) on both PDFs: 0.
- I looked at every 17B page as contact sheets, and zoomed in on the proofs page, the WE9 figures and answer page 7. While doing this I fixed:
  - the figures, which were too small (dot graphs now 118 mm wide, histograms 80 mm);
  - the C1 and C5 work boxes, which I enlarged to avoid half-empty pages;
  - the Q11 answer figure, where a clipped label was fixed and two answer figures were shrunk.
  Some half-empty pages remain: pp 46 and 47 each hold one simulation worked example (each is about 60% of a page and must not split), and the page before the forced homework page break.

## Files changed
- workspace/build/ch17/l17b.html
- workspace/build/ch17/a_17b.html
- workspace/build/ch17/figs_17b.py (new)
- workspace/build/ch17/svg/c17b_*.svg (8) and svg/a17b_*.svg (6), all new
- workspace/checks/ch17_17b.py (new)
- docs/pp_selected_ch17.md (## 17B appended)

The commit is 7be3206 "Ch17: lesson 17B". I staged only these paths; nothing is pushed.

## Concerns
1. Please rule on the doubtful textbook items: Q12 (column convention against the printed answers 4/6/8), Q13 (depends on Q12) and Q14a-c (typos P(X > 1) and the repeated 0.5).
2. These silent teaching-part fixes need confirming:
   - lemma b n(n − 2) → n(n − 1)
   - Example 7c 9.99 → 0.99
   - Example 8 σ_X → σ_Y
   - two Box 4 bullets
   - "heads" → "sixes" in the dice reflection
   - Example 9 s ≐ 1.700 → 1.70
3. Pack-written material: the Concept 3 box and the tip "Finding n and p from μ and σ²"; in the Concept 5 "Simulations" box, the sentence saying the simulation results are given and the three bullets (f_r = f / number of runs; x̄ and s from the frequency table as in Year 11 Ch 13; histogram columns 1 unit wide centred on x, with the polygon joining the midpoints of the column tops). The C5 demo and your-turn simulation frequencies are invented (consistent) data, as the spec allows for teaching simulations.
4. The figures live in figs_17b.py (the same pattern as figs_17a.py), so figs.py is untouched.

## Fix round 1 (polish after approval)
Changes (all in `workspace/build/ch17/l17b.html`):
- PP 3 hint is now "what do you know about n, p and q?". PP 8 hint is now "start with the mean and the standard deviation of X." It no longer points to Worked example 6c.
- The Example 6 part d paragraph has `break-inside:avoid`, so it no longer splits across pages; it now sits whole at the top of p39.
- The variance-proof box has `box-decoration-break:clone`, so its continuation on p37 has its own border and padding, and the first line no longer touches the edge.
- p45 blank space: Worked example 9 may now break between its parts (a, b and c are each kept together), and the your-turn work box went from 150 to 110 mm. Worked examples 9 and 10 now share pp 45-46. The lesson is one page shorter: 17B is now pp 33-55 of a 55-page lesson.pdf.
- Report: the Concept 5 "Simulations" box bullets are now listed with the other pack-written material (Concerns 3).

Commands and results:
- build: `flock .../build.lock sh -c 'python3 build.py ch17 all && mv lesson.pdf answers.pdf ch17/'`
- `qa.py`: lesson 0 problems (55 pages), answers 0 problems (12 pages)
- MathJax error scan on both PDFs: 0
- `python3 workspace/checks/ch17_17b.py`: 413 checks, 0 failed, ALL OK
- I looked at pp 36-47 as contact sheets, and zoomed in on the p36/p37 box break.

I did not touch any 17C file (figs_17c.py and the c17c/a17c SVGs belong to Task 4).
