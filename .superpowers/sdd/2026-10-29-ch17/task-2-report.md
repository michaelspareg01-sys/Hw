# Task 2 report: Lesson 17A Binomial probability

Status: DONE_WITH_CONCERNS (minor; see Concerns)

## What I built
`workspace/build/ch17/l17a.html` (placeholder replaced). The structure follows the house lesson layout and the Ch 13 13A model.
- Lesson head (l17a.html:1-3).
- Concept 1, Bernoulli trials and binomial experiments (l17a.html:5). It has the textbook text (Bernoulli trials, binomial experiments, n and p as the parameters, a Bernoulli trial as a one-stage binomial experiment). Then a tutor demo ("Bernoulli trial or not? Binomial or not?"), a your-turn, and Worked example 1 (Example 1).
- Concept 2, repeatedly attempting to throw a six (l17a.html:44). A summary box, a tutor demo (a spinner with p = 1/3 spun three times: tree, 3Cx, the expansion), a your-turn (a heart in three draws with replacement), and the textbook's teaching example "a die thrown four times" as "Worked example, from the text" (l17a.html:65). That example has the 16-leaf tree (SVG `c17a_tree`), the 4C2 = 6 orderings, the result table and the binomial expansion of (1/6 + 5/6)^4 and (x + y)^4.
- Concept 3, the general case (l17a.html:87). It has the derivation, Box 1 (l17a.html:95), and a box covering the x-for-r notation and complementary events and cases. Then a tutor demo (a die thrown 7 times, success = less than 3, denominator 3^7), a your-turn (5 cards with replacement, hearts, denominator 4^5), and Worked example 2 (Example 2).
- Concept 4, p = q = 1/2 (l17a.html:143). Tutor demo (20 tosses), your-turn (30 tosses), and Worked example 3 (Example 3) with its Note.
- Concept 5, experimental probabilities (l17a.html:168), with Worked example 4. I added a tip box "How many trials are needed?" (l17a.html:172). The spec topic map names "finding n" for 17A, and Ex 17A Q12 needs it, but the textbook's teaching part has no worked method for it. The box gives the complement and logarithm method, with the inequality reversing because ln q < 0. The tutor demo (2% cracked eggs, trays of 30) and the your-turn (5% seeds fail, packets of 40) each have a part c on finding n.
- Concept 6, each stage a compound event (l17a.html:200). Tutor demo (two machines making bolts), your-turn (two ovens), and Worked example 5 (Example 5).
- Textbook homework: Exercise 17A Q1-22, verbatim, banded as in the book: Foundation Q1-7, Development Q8-20, Enrichment Q21-22 (l17a.html:220). Nothing is omitted. There are no spreadsheet or physical-experiment parts in 17A.
- Past-paper homework (l17a.html:271): 10 questions, 21 marks, 30 minutes, ordered from accessible to demanding, with 3 MC items. There is one starting-idea hint per question.

`workspace/build/ch17/a_17a.html` (placeholder replaced), in this order:
- ahead heading
- Lesson Examples C1-C6 (l.2-58)
- Textbook Homework 1-22 (l.60); Q21c(ii) is a "show that" and is omitted
- ahead heading again
- Past-Paper Worked Solutions PP 1-10 (l.85)

Figures: `workspace/build/ch17/figs_17a.py` writes `svg/c17a_tree.svg` (the lesson's 4-stage tree, with branch probabilities on stages 1-3 as in the book) and `svg/a17a_spin.svg`, `svg/a17a_heart.svg` (the 3-stage trees for the C2 answers). I kept these figures in a separate module because `figs.py` belongs to Task 1, which was being edited in parallel (it had uncommitted changes). `figs_17a.py` imports `Fig`/`save` from `figs.py` and does not change it. Run it with `python3 workspace/build/ch17/figs_17a.py`. The controller may fold it into figs.py later.

Record: `docs/pp_selected_ch17.md` (new, in the format of pp_selected_y11ch15.md), section `## 17A`.

## Sources
Textbook (Y12 CMS6 Ext 1). 17A teaching: PDF 802-807. Exercise 17A: PDF 807-810. Answers: PDF 959 (right column) to PDF 960 (left column). I rendered and read every page.

Past papers. Each entry gives the school, year, title as printed, Q, marks, file, question page and solution page.
1. Northern Beaches Secondary College Manly Selective Campus, 2020, Year 12 Trial Examination, Mathematics Extension 1, Q2 (1, MC). `2020/2020 Manly.pdf`, question p2, solution p13 (C).
2. Blacktown Boys' High School, 2024, HSC Trial Examination, Mathematics Extension 1, Q6 (1, MC). `2024/Blacktown Boys 2024.pdf`, question p3 (left half), solution p9 (D).
3. Ascham School, 2024, Year 12 Trial Examination, Mathematics Extension 1, Q11(c) (2). `2024/Ascham 2024 Extension 1 & Solutions.pdf`, question p6, solution p13 (625/3888).
4. Baulkham Hills High School, 2023, Higher School Certificate Trial Examination, Mathematics Extension 1, Q13(c)(i) (2). `2023/Baulkham Hills 2023 3U.pdf`, question p8, solution p18 (45/512). (ii) is in Y11 13A.
5. Blacktown Boys' High School, 2023, Year 12 Trial Examination, Mathematics Extension 1, Q13(b)(i)(ii) (1+1). `2023/Blacktown Boys 2023 3U.pdf`, question p10, solution p26 (0.0131, 0.7819).
6. Abbotsleigh, 2024, Higher School Certificate Assessment 4 Trial Examination, Mathematics Extension 1, Q11(d) (1+2). `2024/Abbotsleigh 2024.pdf`, question p9, solution p22 (0.24, 0.79).
7. Blacktown Boys' High School, 2020, HSC Trial Examination, Mathematics Extension 1, Q12(a) (1+2). `2020/2020 Blacktown Boys.pdf`, question p8, solution p15 (0.2273, 0.1130).
8. James Ruse Agricultural High School, 2020, Year 12 Trial HSC Examination, Mathematics Extension 1, Q11(b) (3). `2020/James Ruse 2020 3U Trials & Solutions.pdf`, question p5, solution p11 (0.0000922).
9. Knox Grammar School, 2022, Higher School Certificate Trial Examination, Mathematics Extension 1, Q13(c)(i)(ii) (1+2). `2022/Knox 2022 3U Trials & Solutions.pdf`, question p5 (right half), solution p13 (right half) to p14 (left half) (19/30, 0.93).
10. Killara High School, 2024, Year 12 Examination, Mathematics Extension 1 HSC Trial Examination, Q9 (1, MC). `2024/Killara 2024 3U Trials & Solutions.pdf`, question p6, solution p16 (B).

I re-read every `docs/pp_selected_*.md` file and `docs/PAST_PAPERS_USED.md` before choosing and again before committing. None of the ten is used anywhere else. The Ch 13 work in progress (13C) takes JR 2020 Q1, BHHS 2020 Q12(a)(iii) and HAHS 2023 Q8, so there is no overlap.

## Omitted, rejected, and silent fixes
- Textbook homework: nothing omitted.
- In the answers, only Q21c(ii) is left out (a "show that" with no printed result).
- Q15: the book asks for four decimal places but prints the exact values 0.03456 and 0.68256. I print "0.0346 (exactly 0.03456)" and "0.6826 (exactly 0.68256)".
- Silent fixes in the textbook's teaching part (copied worked material; house ruling: print the correct version and report):
  - In the four-dice table, the row for 4 sixes is printed in the book as 4C3 (1/6)^3 (5/6)^1. I print 4C4 (1/6)^4 (5/6)^0 (value 0.000 77 as in the book).
  - Example 3 asks for "four significant figures", but the book's answer is 0.0796 (3 s.f.). I print 0.07959.
- Silent answer fix: in the book's answers to Q8, the list of the six orderings sits under part b. I print it under part a, where it is asked for.
- Typographic fixes:
  - Q8 "A coins is tossed" becomes "A coin is tossed".
  - Q18a "will need to discarded" becomes "will need to be discarded".
  - Box 1 "A binomial random variable is the outcomes of" becomes "is the outcome of".
  - Em dashes in the textbook prose became colons, commas or questions.
  - Answer 7b ".91^9" becomes "0.91^9".
- Past-paper changes:
  - BBHS 2023 Q13(b): the stem line "You may use the information on page 15 to answer this question." is left out. It points to the z-table for (iii), which is not included. All other wording is kept.
  - Killara 2024 Q9: "Sunny" is capitalised as printed.
  - BBHS 2020: the school solution writes "X ~ B(15, 0.18)" but works with 0.08. This is a solution slip only; the question is clean and my solution is my own.
- Rejected 17A rows:
  - B1, B2 (Western, excluded paper), B6 (doubtful), B11 (JRAHS mock, excluded), B25 (sample paper, label clash).
  - A4/B10 (STHS 2021 Q14(a)): the stem has typos ("1 green numbers", "the ball land"), so it is doubtful.
  - B22 (BBHS 2024 Q12(c)): typo "ratio" for radio, so it is doubtful.
  - B14 (Killara 2023 Q12(f)): the same as textbook Example 4, and the file has no solutions.
  - B24 (St Aloysius 2024 Q6): the same as Exercise 17A Q5(b), and the file has no solutions.
- Left free for other lessons or Y11 Ch 13: B3(i)(ii), B7, B8, B9, B12, B17, B18, A1(ii).

## Verification
- `python3 workspace/checks/ch17_17a.py` reports **247 checks, 0 failed, ALL OK**. The script reads every printed value from l17a.html, a_17a.html and the three SVGs. Each template must match exactly once, or the check FAILs. It recomputes each value independently:
  - small experiments by enumeration (dice faces 6^4, 6^5, 6^6, 6^7; suits 4^5, 4^6; coins; Bernoulli sequences up to 2^14);
  - larger n by Fraction + math.comb, cross-checked against a convolution of n stages for every (n, p) used;
  - roundings half-up in d.p. or s.f., and truncated decimals by their leading digits;
  - "how many trials" answers by searching n;
  - Q21c(i) by enumerating 4-subsets of 1..20 for n = 4..20;
  - Q22a by sympy expand.
  It also checks the lesson data (n, p and percentages read from the demo and question text), the MC letters (only one option equals the value), and the past-paper structure: marks 21 in the range 15-22, time 30 = 1.5 x 21 rounded to 5, part marks, numbering, labels identical in both files, one hint each.
- Mutation test: copies with five planted errors (a tree leaf, a C3 fraction, a demo datum, Q9, a PP6 rounding) all FAIL.
- Build: `flock .../build.lock sh -c 'python3 build.py ch17 all && mv lesson.pdf answers.pdf ch17/'`. lesson.pdf has 32 pages (17A is pp 11-32) and answers.pdf has 7 pages (17A is pp 3-7).
- `qa.py`: lesson 0 problems, answers 0 problems. The first run flagged the "$" in Q11b; the dollar amounts are now typeset as \(\$10\,000\).
- MathJax error scan (all seven strings) on both PDFs: 0.
- I looked at every added page as contact sheets, and zoomed in on the trees and the C2 answers. While doing this I fixed:
  - the tree labels (inline a/b);
  - WE2 parts c and d, which were stranded (each part's label is now kept with its display);
  - the WE die and WE2 blocks, which may now break across pages, to avoid half-empty pages;
  - Q22, which was alone on an answers page (the Q8 fractions are now compact).

## Files changed
- workspace/build/ch17/l17a.html
- workspace/build/ch17/a_17a.html
- workspace/build/ch17/figs_17a.py (new)
- workspace/build/ch17/svg/c17a_tree.svg, svg/a17a_spin.svg, svg/a17a_heart.svg
- workspace/checks/ch17_17a.py (new)
- docs/pp_selected_ch17.md (new)

The commit is 09e3ce0 "Ch17: lesson 17A". I staged only these paths; nothing is pushed.

## Concerns
1. The Task 1 fix commit 5715881 ("Ch17: normal review polish") already contains an early draft of my `svg/c17a_tree.svg`, because that agent staged the whole svg folder. My commit replaces it with the final version. Nothing else of mine was in that commit.
2. The figures live in `figs_17a.py`, not in `figs.py`, to avoid editing Task 1's file while it was being changed. Merge them later if you prefer a single file.
3. The "How many trials are needed?" tip box (Concept 5) is pack-written. It was added for the spec's "finding n" topic and Ex 17A Q12. It is not a textbook box.
4. The textbook's teaching part has two slips that I fixed silently: the 4C4 row of the four-dice table, and Example 3, which asks for four significant figures but prints 0.0796. The Q8 answer placement was also fixed silently. Please confirm.

## Fix round (after approval: hint polish)
- PP 9 (Knox 2022 Q13(c)) hint is now "a probability tree may help. What is \(p\) for one tomato?" (l17a.html:324). It no longer says what 'twice as likely' gives, or what the complement of 'no more than eight' is.
- PP 10 (Killara 2024 Q9) hint is now "what is \(p\) for one day?" (l17a.html:329).
- PP 7 hint is unchanged. No other edits. The check script is unchanged (the hints are not read by it).
- Verification:
  - Rebuilt with flock.
  - qa.py: lesson 32 pages, 0 problems; answers 7 pages, 0 problems.
  - MathJax error scan: 0 on both PDFs.
  - `python3 workspace/checks/ch17_17a.py`: 247 checks, 0 failed, ALL OK.
  - I looked at the changed page (lesson p32, PP 9 and PP 10). The layout is unchanged.
- Commit: 7b9ced8 "Ch17: 17A hint polish". Only l17a.html was staged, and nothing is pushed.
