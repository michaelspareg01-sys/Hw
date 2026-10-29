# Task 1 report: Y11 Ch 13 pack scaffold, cover, revision

Commit 45d5cc5 "Y11Ch13: scaffold, cover, revision" on branch ch10-pack (not pushed). Only workspace/build/y11ch13/ and workspace/checks/y11ch13_rev.py were staged.

## Built
- workspace/build/y11ch13/pack.json: footers "Year 11 Chapter 13 Discrete Probability Distributions | Lesson and Homework" / "... | Homework Answers"; answers heading "Chapter 13 Discrete Distributions - Homework Answers" (one line); parts lists cover, revision, l13a..l13d and a_rev, a_13a..a_13d.
- cover.html: title "Year 11 Chapter 13 / Discrete Probability Distributions"; rows Revision "Probability and data" (note "Year 11 · Ch 12, statistics"), Lessons 13A The language of probability distributions, 13B Expected value, 13C Variance and standard deviation, 13D Sampling, each with `Past papers: @@M13A@@`..`@@M13D@@` (to be filled later; they print literally for now), Review "Chapter 13 review exercise".
- revision.html (2 full pages, PDF pages 2-3): two summary boxes. Box 1 "Probability (Chapter 12)": P(E)=|E|/|S| on a uniform sample space, impossible/certain/sum to 1, complement and the word "not", addition rule and mutually exclusive, product rule, with and without replacement, tree diagrams, relative frequency (book wording from 12A box 4/5/6, 12D box 13/14, 12E box 16, 12F box 17, 12A Example 4). Box 2 "Mean, standard deviation and sigma notation (Advanced statistics)": mean as sum over n (13B wording), frequency table, f_r, weighted mean, deviation, variance, sigma^2 = sum x^2 f_r - xbar^2 (the 13D form), calculator key sigma_n (13D extension box), sigma notation and the two rules the 13C proof uses (sums split, constants come out). Warm-up of 5 questions: Q1 card (court card, not a court card, heart or king), Q2 three coin tosses, Q3 two marbles with and without replacement, Q4 spinner frequency table (relative frequency, mean, SD = 0.96), Q5 sigma notation (write 3+6+9+12 as a sum; sum(3x+1)p(x) given sum p = 1 and sum xp = 2).
- a_rev.html: full answers for the 5 questions.
- figs.py (header copied from Y11 Ch 15: Fig, Graph imports, save), svg/.gitkeep, placeholders l13a..l13d.html and a_13a..a_13d.html each `<!-- filled by Task N -->` (N = 2..5 for A..D).
- workspace/checks/y11ch13_rev.py: reads givens from revision.html and printed values from a_rev.html (each template matches exactly once, loose braces so \dfrac3{13} and \dfrac{3}{13} both read). Recomputes by enumeration with fractions.Fraction (52-card deck, 8 coin sequences, 25 and 20 ordered marble draws, the Q4 table read from the HTML, exact mean/variance by two routes, SD checked as 0.96^2 = 0.9216 exactly, several distributions for Q5b).

## Sources
Y11 book PDF 642-645 (13A), 652-653 (13B), 661-662 (13C) rendered and read; also 664, 670-676 (13C proof, 13D sample mean/s, sigma_n note), 646-651 (13A exercise, to see what it assumes: tree diagrams with and without replacement, tally, relative frequency) and Ch 12 pages 583-589, 607-609, 615-617, 623, 631-632 for the wording of the probability boxes.

## Decisions and omissions
- Two full pages was achievable only by trimming: the summary has no worked four-coin table (13A shows it), and the original Q3c (exactly one red without replacement) and Q5a (evaluate sum k^2, which the box already shows) were dropped; work boxes are 13-28 mm (short answers). Page 3 is full to about 15 mm below the last work box.
- No card-suit glyphs; the card question says "heart", "king" in words. Q1 stem carries the court-card definition (12 jacks, queens, kings).
- Ch 13's frequency/SD notation: used sigma^2 = sum(x - xbar)^2 f_r = sum x^2 f_r - xbar^2 (population SD, calculator sigma_n) as the 13D extension box says; no n-1 form taught.
- Past papers: none in this task. The @@M13x@@ placeholders stay literal until the controller fills them.

## Verification
- `python3 workspace/checks/y11ch13_rev.py`: 97 printed values checked, 0 failures, exit 0. Mutation tests (printed 2.72->2.73, 3/10->4/10, 0.96->0.97, =7->=8, "4 kings"->"5 kings") each FAIL loudly with exit 1; altering the given f row aborts with an assertion (exit 1).
- Build: `cd workspace/build && python3 build.py y11ch13 all && mv lesson.pdf answers.pdf y11ch13/`.
- qa.py: lesson.pdf 3 pages, 0 problems; answers.pdf 1 page, 0 problems.
- MathJax error-string scan (7 strings) over both PDFs: 0.
- Pages inspected: lesson pages 1-3, answers page 1. No clipped maths; the "@@" text on the cover is the intended placeholder.

## Concerns
- Q3 now has only two parts (a, b); the revision page is deliberately tight, so later tasks adding nothing to it need no change. Cover note for the revision row follows the brief exactly.
