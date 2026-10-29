# Task 2 report: Lesson 13A The language of probability distributions

Commit 091f2cc "Y11Ch13: lesson 13A" on branch ch10-pack (not pushed). Staged by explicit path only: l13a.html, a_13a.html, figs.py, 8 new svg files, workspace/checks/y11ch13_13a.py, docs/pp_selected_y11ch13.md. Nothing in y11ch14/y11ch15 was touched (their uncommitted files belong to other agents).

## What I built
**workspace/build/y11ch13/l13a.html** (lesson PDF pages 4-24)
- Lesson head (l.2-3).
- Concept 1, discrete probability distributions and random variables (l.6): the box on what a distribution is (sample space {0,...,4}, not uniform; values, numeric, discrete, listed), Box 1, where the probabilities come from (uniform space, other calculation, empirical), random/deterministic experiments, random variable X, the notation P(X = 3), the x / P(X = x) table and the graph convention. Tutor demo (l.23) two dice, number of sixes; Your turn die thrown twice, number of results less than 3; Worked example from the text (l.35): the four coins, with both textbook tables, P(X = 3), P(X > 2), P(X odd), P(X prime), and the graph (SVG c13a_coins).
- Concept 2, categorical data (l.60): the categorical box, Box 2, the "word of warning" (categorical is not discrete in this course). Tutor demo sports houses (counts table), Your turn jelly beans; Worked example from the text (l.83): the 2016 world population by continent table, the distribution and P(Europe or North America) = 0.177.
- Concept 3, uniform distributions and deterministic experiments (l.106): uniform box, Box 3, the deterministic-experiment distribution with its table and graph (c13a_det). Tutor demo five cards 2-10, Your turn tetrahedral die 1, 3, 5, 7; Worked example 1 = textbook Example 1 (l.126) with graph c13a_die.
- Concept 4, what is a list? (l.138): the list box (whole numbers, countably infinite, integers, Cantor), Box 4. Tutor demo throwing a die until a six (general term), Your turn spinner until red; Worked example 2 = textbook Example 2 (Wulf, l.162).
- Concept 5, continuous distributions (l.173): continuous box (intervals, probability of one value is zero, P(55 <= X <= 60), integration in Year 12), Box 5. Tutor demo / Your turn: classify numeric/categorical, discrete/continuous (including "recorded to 0.01 s" = discrete); Worked example from the text (l.197): the speed camera.
- Textbook homework, Exercise 13A (l.208): all 16 questions verbatim, bands F 1-7 (l.209), D 8-13 (l.237), E 14-16 (l.262). All distribution tables are HTML tables (Q2, Q6, Q7, Q9, Q11, Q13 tally tables, Q15).
- Past-paper mini exam (l.274): 1 question, 1 mark, 5 minutes, one hint. It follows Q16 on the same page (no page break) because it is so short; heading kept with its block.

**workspace/build/y11ch13/a_13a.html** (answers PDF pages 2-8): ahead, Lesson Examples C1-C5 (tables, sums, graphs a13a_sixes, a13a_less3, a13a_cards, a13a_tetra), Textbook Homework 1-16 (every item has an answer in the book, including the Q8(a)(i) tree diagram as SVG a13a_q8tree), ahead, Past-Paper Worked Solutions.

**workspace/build/y11ch13/figs.py**: helpers `dist_graph` (dot graph of a distribution, values across, probabilities up, fraction ticks), `bartext` (italic letters with an overline for complements) and `tree2` (two-stage tree with branch, outcome and path probabilities); `build_13a()` writes the 8 SVGs.

**workspace/checks/y11ch13_13a.py**: 162 checks. It reads every printed table cell by cell and every inline value by template (each must match exactly once), converts the LaTeX to exact Fractions and compares with independent computation: every distribution is ENUMERATED with itertools (coins, dice, the 52-card deck, balls, tiles, marbles, coins scooped, the sentence's words, the digits of 1.41421356237, the two bags, ticket lists, the word Parramatta, 1..1000 digit counts); "until the first success" distributions are enumerated over all sequences of each length (n = 1..8 for the general terms); Q9/Q15 are solved with sympy from the printed tables and every root is tested against 0 <= P <= 1; Q6 validity and Q7 probabilities are computed from the printed tables; the continents per cents are recomputed from the printed populations; the figures are checked by re-running figs.build_13a() with the plotting calls recorded. It also checks structure (5 demos, 5 your-turns, Worked examples 1, 2 + 3 from the text, answer blocks 1-16 + C1-C5, bands), and the past-paper block (marks = intro total, time, numbering, labels identical in both files, one hint), plus the consistency of the BHHS table data (four trials with p = 0.3, by enumeration). Simulation-free. Exit 1 on any failure.

## Sources used
- Y11 book PDF 642-651 (13A teaching pages 642-646 and the whole Exercise 13A 646-651 with the FOUNDATION / DEVELOPMENT / ENRICHMENT headings), rendered at zoom 1.6 and read.
- Answers PDF 933 (both halves), 934 (both halves), 935 top half, rendered at zoom 2.
- Past paper: Baulkham Hills High School 2020 (`workspace/pp/Ext 1/2020/2020 Bauklham Hills.pdf`; no cover in the file, title from the marking guidelines header "Year 12 Trial Examination 2020 Mathematics Extension 1", as already used in the Ch 14 pack), Q12(a)(iv), 1 mark, question page p7, solution page p14 (left half): P(X >= 3) = 0.0756 + 0.0081 = 0.0837. Label printed: "Baulkham Hills High School, 2020, Year 12 Trial Examination, Mathematics Extension 1, Q12(a)(iv)" (Extension&nbsp;1,&nbsp;Q12(a)(iv) kept on one line).
- Also rendered for the decision: Manly 2020 p2 (Q2) and p13 (key), Sydney Tech 2021 p9 (Q14(a)).

## Past papers: the shortfall (house rule 8), sweep and reasons
The mini exam has **1 mark** (BHHS 2020 Q12(a)(iv)). The catalogue's 13A rows:
- **A1 BHHS 2020 Q12(a)** (5 marks): only (iv) uses 13A methods (adding table entries, as in Exercise 13A Q7). (i) "use the known entries to calculate p" and (ii) "find a and b" need the meaning of X ~ Bin(4, p), which is not taught in Year 11 (Ch 17); (iii) Var(X) is 13C/17B. The stem is printed as on the paper (it mentions Bin(4, p)); the hint says the table is all that is needed. (i)-(iii) stay free; (iii) is catalogue row C18 and could go to 13C with a and b supplied, or to Ch 17.
- **A2 Manly 2020 Q2** (MC, "Which one of the following describes a Bernoulli random variable?"): rejected under house rule 7. The word "Bernoulli" does not occur anywhere in the Year 11 book (text search of the whole PDF), so a 13A student cannot answer it. It is a good 17A item; I left it free for Ch 17.
- **A3 JRAHS 2021 mock**: excluded by the spec.
- **A4 STHS 2021 Q14(a)(i)**: "Write the distribution of Y in standard form, and give its mean and variance" means Y ~ Bin(5, 18/37) with np and npq: binomial (17A/17B), not 13A. (Also flagged for typos.)
- My own sweep: a keyword search ("random variable", "distribution", "Bernoulli", "discrete", "uniform", "P(X =") over every text-layer school paper 2020-2024 (commercial files skipped). Every hit is a binomial, sample-proportion, normal or continuous-pdf item (17x rows or out of scope). The scanned papers were checked by eye by the cataloguer ("No school paper has a general (non-binomial) discrete distribution table"). The only near-13A item is BHHS 2023 Q11(c)(i) (two dice, p = P(sum of 7), 1 mark), but it is part of 17x row C11 (and 14F row F16), so the 13A ruling ("13A gets no 17x rows") excludes it. If the controller wants a second mark, that is the candidate.
- Time: 1.5 x 1 = 1.5, which rounds to 0; I printed 5 minutes (the check accepts max(5, rounded)).
- Checked against docs/PAST_PAPERS_USED.md and ALL docs/pp_selected_*.md (ch10, y11ch13, y11ch14, y11ch15; no Ch 17 file yet) just before committing: BHHS 2020 Q12 is not used anywhere (Ch 14 uses BHHS 2020 Q8, a different question). Recorded in docs/pp_selected_y11ch13.md.

## Fidelity notes, fixes and omissions
- Nothing omitted from the exercise; no doubtful exercise items found (all data consistent; Q4c's number has 12 digits; the zoo counts add to 20; Q15(b) really has two valid roots, as the book says).
- Printed textbook answer slips, replaced by my own correct answers with no remark: **8(c)** the book's table for the number of girls is reversed (it gives P(X = 0) = 8/125 ... P(X = 3) = 27/125); printed P(X = 0) = 27/125, 54/125, 36/125, P(X = 3) = 8/125. **8(d)** the book's answer says "Snake Ridge"; printed "Snake Gully". **13** the book labels the answers to (d), (e), (f) as a, b, c; printed as d, e, f.
- Small wording changes in answers: 4(c) "digits recorded from the first 12 digits of sqrt 2" printed as "the digit chosen from the 12 digits of 1.41421356237"; 4(d) the book's "(Note that the answer is the same if the sets are amalgamated. Why?)" printed as a short explanation (equal bag sizes).
- Textbook figure (PDF 643): in the book's graph of the four-coin distribution the dots are in the right places. The slip is only in the axis labelling: tick 0 is unlabelled and there is a spurious tick labelled 5. My SVG labels the ticks 0-4 with no tick 5. (Corrected in the fix round; the earlier wording 'tick labels shifted by one' was wrong.)
- Typographic: em dashes in the textbook prose became commas or full stops (for example Q11's "[This is an example of a multinomial distribution, a multi-stage experiment ...]" and Box 1 "listed, meaning that ..."); the four-coins table's reference to "Example 18 of Section 12E" is replaced by the working in the worked example.
- Demos and your-turns are new value-changed variants; worked examples are the textbook's (Examples 1, 2 and the three prose examples: four coins, continents, speed camera).

## Verification
- `python3 workspace/checks/y11ch13_13a.py`: 162 checks, all OK, exit 0. Mutation tests (via Y11CH13_SRC copies): 9/169 -> 10/169, 0.0837 -> 0.0838, 13/18 -> 13/19, Q9c 1/27 -> 1/26, Q15b 7/6 -> 6/7, Q6e No -> Yes, Q7 table 0.25 -> 0.35, jelly beans 5 -> 6 black, Q8c table back to the book's reversed order, and a figure value in figs.py: each gives MISMATCH and exit 1.
- `python3 workspace/checks/y11ch13_rev.py`: 97 values, 0 failures (unchanged).
- Build: `cd workspace/build && flock .../scratchpad/build.lock sh -c 'python3 build.py y11ch13 all && mv lesson.pdf answers.pdf y11ch13/'`.
- qa.py: lesson.pdf 24 pages, 0 problems; answers.pdf 8 pages, 0 problems.
- MathJax error-string scan (7 strings) over both PDFs: 0.
- Pages inspected (contact sheets and zooms): lesson 4-24, answers 2-8. Concept headings are kept with their first box; no clipped maths or overflowing tables; graphs and the tree checked at zoom (labels clear of lines). Work boxes sized to the page; the emptiest homework pages are p17 (Q7, 0.66 full, last Foundation question) and p19 (Q9, 0.71).

## Concerns
- The 1-mark mini exam (house rule 8 shortfall, explained above). Possible extra mark: BHHS 2023 Q11(c)(i), if the controller relaxes the 17x ruling for it.
- The PP stem shows the untaught notation X ~ Bin(4, p) (kept verbatim for fidelity; the hint tells students they only need the table).

---
# Top-up round (controller ruling: parts of 17x rows answerable with 13A methods only)

Commit a59199a "Y11Ch13: lesson 13A past-paper top-up" (not pushed). Files: l13a.html, a_13a.html, workspace/checks/y11ch13_13a.py, docs/pp_selected_y11ch13.md.

## New mini exam (6 marks, 10 minutes)
I re-read all docs/pp_selected_*.md (ch10, y11ch13, y11ch14, y11ch15) and PAST_PAPERS_USED.md before choosing and again before committing. None of these parts is used anywhere.
| PP | Source label as printed | Marks | Question page / solution page | Answer |
|---|---|---|---|---|
| 1 | Baulkham Hills High School, 2023, Higher School Certificate Trial Examination, Mathematics Extension 1, Q11(c)(i) | 1 | `2023/Baulkham Hills 2023 3U.pdf` p6 / p13 | p = 1/6 (school: 6 of 36) |
| 2 | Baulkham Hills High School, 2020, Year 12 Trial Examination, Mathematics Extension 1, Q12(a)(i)(iv) | 1 + 1 | `2020/2020 Bauklham Hills.pdf` p7 / p14 | p = 0.3 (school: P(X = 4) = p^4 = 0.0081); P(X >= 3) = 0.0837 |
| 3 | Baulkham Hills High School, 2023, Higher School Certificate Trial Examination, Mathematics Extension 1, Q13(c)(ii) | 1 | `2023/Baulkham Hills 2023 3U.pdf` p8 / p18 | 1023/1024 (school: 1 - P(all correct)) |
| 4 | Northern Beaches Secondary College Manly Selective Campus, 2020, Year 12 Trial Examination, Mathematics Extension 1, Q11(a)(iii) | 2 | `2020/2020 Manly.pdf` p6 / p14 | n = 6 (school: (2/3)^n < 0.1, n > 5.67) |
- Wording and notation are as printed. Each stem keeps the shared lead-in of the question (dice; the Bin(4, p) table; Jerry's five-question test; the archer, "eight shots" included). No earlier part's result is needed by any part taken.
- PP 2 hint explains the untaught notation: "X ~ Bin(4, p) means that X is the number of successes in 4 independent trials, each with probability p of success. For (i), which value of X needs every trial to succeed? For (iv), the table is all you need." So (i) uses only the product rule (Ch 12, as in Exercise 13A Q8), not the binomial formula. A1(ii) (a = 4pq^3) still needs the binomial formula and (iii) is Var(X), so neither is used.
- PP 3 and PP 4 are "at least one" probabilities of a count over independent identical stages (complement and product rule, Exercise 13A Q8 style); PP 4 also uses logarithms (Advanced Year 11). Neither needs nCk, E(X), Var(X) or a normal distribution.
- Worked solutions in a_13a.html give full working; PP 2 also checks the table entry 0.2401 = 0.7^4.

## Sweep of 17x rows (why nothing else is taken)
- 17A: every other part needs nCk p^k q^(n-k) (B4, B5, B7-B10, B12, B13(ii), B14, B16(i), B17-B22, B24; B23 needs the binomial formula after p = 0.8). B16(ii) BBHS 2023 Q13(b)(ii) (1 - 0.97^50) is a near-duplicate of PP 3, so not taken. B13(i) Knox 2022 (total probability, "show 19/30") has no distribution or random variable, so it is a Ch 12 skill. B1, B2 (Western), B11 (JRAHS mock), B6 (doubtful), B25 (sample paper, label clash) are excluded.
- 17B: every other part needs E(X) or Var(X). The exception is C15(i) Moriah 2023 Q12(a)(i) (P(first marble blue) = 3/(8 + k)), a single-stage probability with no distribution that has the same skill as PP 1, so I did not take it. C14 STHS 2023 Q12(a) parts need Bin meaning or the binomial formula.
- 17C and 17D: all normal or sample-proportion work. E18 BBHS 2024 Q2 needs p-hat.
- If the controller wants up to 2 more marks, the borderline items are B16(ii) (1) and C15(i) (1), both rejected above as near-duplicates.

## Ch 17 marks taken and remaining (clean marks, excluding Western, JRAHS mock, sample papers and doubtful rows)
- 17A: about 43 clean marks before; taken 3 (B3(iii) 2, B15(ii) 1); about 40 remain. A1(i) (1 mark, a 13A row with binomial content) is also used. A4 (2) and A2 (1) remain free.
- 17B: about 32 before; taken 2 (C11(i), C18 = A1(iv)); about 30 remain, before any 13B/13C use of E/Var rows.
- 17C: about 24, none taken. 17D: about 47, none taken (13D may take up to two).
Every Ch 17 lesson keeps well over 15 clean marks.

## Verification
- `python3 workspace/checks/y11ch13_13a.py`: 192 checks, all OK. The new PP checks:
  - PP 1: the 36 dice outcomes enumerated, and the printed six pairs, 6/36 = 1/6 and 5/6.
  - PP 2: p found by search over k/1000 with p^4 = 0.0081; the table entries reproduced by enumerating four trials; 0.7^4 = 0.2401; the sum 0.0837.
  - PP 3: all 4^5 answer sheets enumerated.
  - PP 4: shot sequences enumerated for n = 1..11, giving least n = 6, with 32/243 and 64/729 and their 3 d.p. decimals and ln 0.1 / ln(2/3) = 5.678...
  - Structure: marks 1 + 2 + 1 + 2 = 6 = intro; 10 minutes; part marks add to each question's total; labels identical in both files; one hint each.
- Mutation tests: each gave exit 1. The mutations were 6 shots -> 5, 1023/1024 -> 1022/1024, p = 0.3 -> 0.4, 1/6 -> 1/5, the intro 6 marks -> 7, and the table entry 0.0081 -> 0.0082.
- `y11ch13_rev.py` 97 OK.
- Build with the flock command. qa.py: lesson.pdf 26 pages, 0 problems; answers.pdf 9 pages, 0 problems. MathJax scan 0 on both.
- Pages inspected: lesson 24-26 (mini exam: heading, intro and PP 1 kept together after Q16; PP 2-3 on p25; PP 4 on p26 with a larger work box) and answers 8-9. The source labels keep "Extension 1, Q…" together.

## Concerns
- 6 marks is still below 15. This is house rule 8, and every clean 13A-method part found is included.
- PP 2 keeps the untaught notation Bin(4, p) in the stem. The hint explains it.

---
# Fix round (review findings)

Commit f4321bf "Y11Ch13: 13A review fixes" (not pushed). Files: l13a.html, figs.py, svg/a13a_q8tree.svg.

1. REQUIRED, PP 2 hint (BHHS 2020 Q12(a)): the Bin(4, p) sentence and "For (iv), the table is all you need" are kept. The (i) question now reads "For (i), which entry of the table is easiest to link to p?" It no longer names X = 4.
2. PP 4 hint (Manly 2020 Q11(a)(iii)) now reads "think about the complementary event to ‘at least one bullseye’."
3. PP 2 table: `table-layout:fixed` with a colgroup that gives the five value columns 17 mm each, so every value cell has the same width (checked on lesson p25).
4. Tree a13a_q8tree: each branch probability is now placed 19 px from the midpoint of its branch, along the branch's normal, on the outer side. This is the new helper `_off` in figs.py. Checked at zoom 2.5 on answers p5: no label touches a line.
5. Report: the note on the textbook's four-coin graph is corrected. On PDF 643 the dots are in the right places; the only slip is that tick 0 is unlabelled and there is a spurious tick 5. The pack's graph is unchanged.

The check script does not test hint wording (it checks only that there is one hint per question), so it needed no change.
Verification: y11ch13_13a.py runs 192 checks, all OK. qa gives 0 problems on lesson.pdf (26 pages) and answers.pdf (9 pages). The MathJax scan finds 0 errors. I looked at lesson p25 and p26 and answers p5.
