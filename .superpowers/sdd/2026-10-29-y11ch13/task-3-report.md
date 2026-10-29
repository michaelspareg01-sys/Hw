# Task 3 report: Lesson 13B Expected value

Commit af4460c "Y11Ch13: lesson 13B" on branch ch10-pack (not pushed). I staged files by explicit path only: l13b.html, a_13b.html, figs.py, 9 new svg files, workspace/checks/y11ch13_13b.py and docs/pp_selected_y11ch13.md. I did not touch anything in y11ch14 or ch17. The uncommitted y11ch14 changes belong to other agents.

## Status: DONE_WITH_CONCERNS
The lesson is complete but has **no past-paper mini exam (0 marks)**. No school-paper item fits the spec's 13B ruling (see "Past papers" below). House rule 8 asks for a minimum of one question, but every candidate breaks rule 7 (methods taught so far) or the spec's "no binomial formula" condition. **The controller needs to rule** on whether to accept 0 marks or name an item. The options are listed below.

## What I built
**workspace/build/y11ch13/l13b.html** (lesson PDF pages 27–44)
- Lesson head (l.1–3).
- **Concept 1: the notation p(x) and the centre of a distribution** (l.5).
  - Box: the notation p(x), with the four-coin table in both notations.
  - Box: "Where is the centre of the distribution?" (the two explanations, "values must be numeric from now on").
  - Tutor demo (l.18): the sum of two dice, using a p(x) table, a graph and the centre by symmetry.
  - Your turn: the sum of two tetrahedral dice.
  - Worked example from the text (l.30): the four coins, "where is the centre?", with the textbook's quoted explanations (long-run average, symmetry) and graph c13b_coins.
- **Concept 2: expected value, the weighted mean** (l.47).
  - Boxes:
    - Expected value: the ordinary mean and the 1/n form.
    - The weighted mean: the derivation giving E(X) = 2.
    - The formula for expected value (Σ).
    - Setting out the calculation in rows with a Sum column ("summing the middle row is only a check", plus the pointer to Q3).
    - The alternative setting out in columns (transposed table).
    - Expectation as a measure of central tendency (μ).
  - Box 6, Expected value of a discrete probability distribution.
  - The textbook's closing remark on unsymmetric data, in a small box titled "Unsymmetric distributions".
  - Tutor demo (l.98): the pickpocket (16 friends, set out in rows, E = $65).
  - Your turn: the thief (10 friends, set out in columns, E = $21).
  - Worked example 3 = textbook Example 3 (l.104): the robbery, with its table, $140 and graph c13b_rob.
- **Concept 3: expected value of a uniform distribution** (l.113).
  - Box with the textbook's two bullet points.
  - Tutor demo (l.120): an octahedral die (E = 4½).
  - Your turn: a dodecahedral die (E = 6½). Both ask whether μ is a face value.
  - Worked example 4 = textbook Example 4 (l.126): the die, with table, μ = 3½, graph c13b_die and the "a little unsettling" discussion.
- **Textbook homework, Exercise 13B** (l.140): all 14 questions, transcribed in full.
  - Bands: Foundation 1–4 (l.143), Development 5–10 (l.177), Enrichment 11–14 (l.203).
  - Every table is an HTML table: Q1 a–c, the Q2 column table, the Q3 theory, tally and frequency tables, Q4 a–b (x_i, p_i), the Q6 three tables, the Q10 tally and theory tables, and the Q13 infinite table.
- No past-paper section (see below).

**workspace/build/y11ch13/a_13b.html** (answers PDF pages 8–11)
- Order: ahead → Lesson Examples C1–C3 (tables, sums, graphs a13b_sum, a13b_tsum, a13b_pick, a13b_thief, a13b_oct, a13b_dodec) → Textbook Homework.
- The homework answers cover every item with a final answer in the book: 1, 2, 4–9, 10(d)(f), 11, 12, 13(b)(c) and 14.
- Q3 is omitted because it is a simulation and the book gives no answer.
- Q12(c) has a short added working line: E(X) = 54k/216 = k/4 = 1, so k = 4 and OOO pays 11k = $44. The book's sentence follows it.
- There is no second "ahead" and no PP section, because there are no past-paper questions.

**workspace/build/y11ch13/figs.py**
- `dist_graph` gained `lift` (tick labels for close values, drawn above the axis to the right of the tick, as the book does for 50 in Example 3) and `xlo`. The defaults are unchanged, and the 13A figures are byte-identical (git shows no change to them).
- New `build_13b()` writes the 9 SVGs, with y-axis label p(x).

**Money formatting.** qa.py flags every literal "$" in the PDF text. So each dollar sign is written as `<span style="white-space:nowrap">\(\$\)560</span>`: the dollar sign is set in math and the digits stay in the text font, and the amount cannot wrap. "$x" and "$k" are `\(\$x\)`.

## Source pages used
- Y11 book PDF 652–660, each rendered at zoom 1.6 and read: the 13B teaching pages 652–656 (Examples 3 and 4) and all of Exercise 13B on pages 656–660, with the FOUNDATION / DEVELOPMENT / ENRICHMENT headings. PDF 661 confirmed that 13C starts there.
- Answers: PDF 935 (both halves) and 936 (both halves), rendered at zoom 2.
- Past papers rendered for the decision: Hurlstone 2023 p3 (Q8), James Ruse 2020 p3 (Q6), King's 2021 p9 (Q12(c)).

## Past papers: why there are none (house rule 8, spec thin-pool ruling)
The spec allows 13B to take 17x rows "only where the part asked needs just E(X) … of a given distribution (no binomial formula)". I checked every candidate:
- **Ch 13 rows.**
  - A6, Hurlstone 2023 Q8 (MC): "A Bernoulli variable X has E(X) = 5Var(X)" needs Var(X), which is 13C. It is the natural 13C item, so I left it free.
  - A5, JR 2020 Q1: the variance of a Bernoulli variable, which is 13C.
  - A7 and A3: JRAHS mock, excluded.
  - A1 and A2: 13A rows. A1(ii) needs the binomial formula; A1(iii) is Var(X) (C18, for 13C).
  - A4, STHS 2021 Q14(a)(i): binomial standard form with mean and variance.
- **17B rows that ask for a mean.**
  - C2, JR 2020 Q6: the pmf ¹⁵Cₖ(0.29)ᵏ(0.71)¹⁵⁻ᵏ is "given", but finding the mean needs np, or a 16-term sum using nCk. nCk is Ch 14, which comes after Ch 13.
  - C6, King's 2021 Q12(c)(i): "Let X be the binomial random variable…", E(X) = np.
  - C11(ii), BHHS 2023: the mean and variance of 30 rolls.
  - C14, STHS 2023 Q12(a): binomial.
  - C16, Abbotsleigh 2024 Q1: 12 Bernoulli trials, mean and variance.
  - C1, C3, C5, C8, C9, C12, C17: all np/npq.
  - C15(ii), Moriah: Var(X).
  - Every one of these needs the binomial mean formula.
- **17A, 17C and 17D.** These are binomial probabilities, normal approximations or p-hat. E(p-hat) = p is 17D theory.
- **My own sweep.** I ran a keyword search ("expect", "E(X)", "mean", "average", "weighted", "payout", "prize", "win") over every text-layer school paper 2020–2024. I skipped the commercial papers and the excluded files (JRAHS mock, Western, Fort Street 2023, NSB 2024). Every hit is binomial, p-hat, normal, or not probability at all. There are no expected-winnings or general-table E(X) items. The cataloguer checked the scanned papers by eye and found "No school paper has a general (non-binomial) discrete distribution table, E(X) from a table".
- **13A-method leftovers.** BBHS 2023 Q13(b)(ii) and Moriah 2023 Q12(a)(i) do not test 13B. The 13A review already judged them near-duplicates of 13A items.
- **Options for the controller**, if a 13B item is wanted anyway (each needs a ruling):
  - (a) King's 2021 Q12(c)(i), 1 mark. The hint would explain "binomial" as in 13A PP 2. It still needs np, which is not taught.
  - (b) JR 2020 Q6, MC, 1 mark, answer 4.35. It needs nCk and np.
  - (c) Hurlstone 2023 Q8, 1 mark, if Var can be moved forward. It cannot until 13C.
  - My recommendation: accept 0 marks for 13B and keep A6 for 13C.
- I read docs/PAST_PAPERS_USED.md and all docs/pp_selected_*.md files (ch10, y11ch13, y11ch14, y11ch15) before deciding and again before committing. There is no pp_selected_ch17.md yet. The record is in docs/pp_selected_y11ch13.md (section 13B). Ch 17 marks taken by 13B: none.
- Cover placeholder `@@M13B@@` is left for Task 6. It should read "none" (or as the controller rules).

## Fidelity notes, fixes and omissions
- Nothing omitted from the exercise. I found no doubtful exercise items: all data are consistent, and the book's answers agree with my own for every item.
- **Textbook cross-reference slips, corrected with no remark:**
  - Q6 "the notation … from Section 11A" is printed as "from Lesson 13A".
  - Q13 "In Example 2 in Section 11A" is printed as "In Worked example 2 of Lesson 13A" (Wulf is Example 2 of 13A).
- **Pack wording:**
  - "The first experiment in the previous section" is printed as "…in Lesson 13A".
  - "Example 3" is printed as "Worked example 3" in the prose that refers to it.
  - The textbook text "This section introduces…" and "In the theory for this section" (Q3) are kept as printed.
- **Textbook figure (PDF 652):** the four-coin graph has the same slip as on PDF 643. The dots are at 0–4, but the tick labels read 1–5 (tick 0 unlabelled, a spurious 5). My SVG c13b_coins labels the ticks 0–4. The Example 3 and Example 4 graphs are correct in the book.
- **Typographic:**
  - Em dashes in the book's prose became colons or full stops. For example, "add them up and divide by n", "it is easier to add up a column…", "the pronumeral μ. The Greek letter 'mu' stands for 'mean'", "The probabilities must add to 1. Summing the middle row is only a check", and the Q8/Q9 "(This is an example of a binomial distribution, a multi-stage experiment…)".
  - The book's "the rows becomes columns" is printed as "the rows become columns".
- The three demos and three your-turns are new value-changed variants. The worked examples are the textbook's: the four-coin centre discussion, Example 3 and Example 4.
- The "Unsymmetric distributions" box title is mine. It holds the textbook's closing paragraph after Box 6.

## Verification
- `python3 workspace/checks/y11ch13_13b.py`: **140 checks, all OK**, exit 0.
  - It reads every printed table cell by cell: x, p(x) and xp(x) rows, or the transposed columns, with the Sum entries. Each xp(x) cell must equal x·p(x), Sum p must be 1, and Sum xp must equal E(X).
  - It reads every inline value by template, and each template must match exactly once.
  - Every distribution is enumerated:
    - the coins (3 and 4), and two dice (sum and difference);
    - two tetrahedral dice;
    - 52×51 ordered card pairs (hearts);
    - the friends' cash, parsed from the printed statements (counts and amounts, with the friend total checked);
    - Fiona's 12 boxes, parsed from the statement;
    - the weighted die as 15 equally likely tickets (3:2);
    - the slot machine as 6³ rolls on an O,S,S,A,A,A reel;
    - the uniform dice.
  - The E(aX + b) answers are computed from the printed Q7 expressions, with E(X) = 5 read from the statement.
  - The Q6 tables are checked to be X, 2X and X + 1.
  - Q12's k is solved with sympy from the enumerated probabilities.
  - The Q13 and Q14 infinite sums use sympy summation (2 and ∞), and the first six terms of each printed series (1)–(4) are checked.
  - The figures are checked by re-running figs.build_13b() with dist_graph recorded.
  - Structure: 3 concepts, 3 demos, 3 your-turns, worked examples (text, 3, 4), Box 6, answer blocks, bands F 1–4 / D 5–10 / E 11–14, and no stray past-paper block.
- **Mutation tests** (via Y11CH13_SRC copies). Each of these gives MISMATCH and exit 1:
  - an xp(x) cell in Example 3 (28 → 29);
  - the pickpocket statement ("three have $120" → "two");
  - A9 19/34 → 18/34;
  - A12 profit 43 → 44;
  - A7e 0 → 1;
  - WE4 μ = 3½ → 3⅓;
  - the probabilities in figs.py (reversed);
  - a Q1c data cell (0.1 → 0.15);
  - A10 35/18 → 35/17;
  - C2 probability 1/16 → 1/15;
  - Example 3's $560 → $580.
- `y11ch13_13a.py` gives 192 checks, all OK, so the figs.py change did not affect 13A. `y11ch13_rev.py` gives 97 checks with 0 failures.
- Build: `cd workspace/build && flock …/scratchpad/build.lock sh -c 'python3 build.py y11ch13 all && mv lesson.pdf answers.pdf y11ch13/'`.
- qa.py: lesson.pdf has 44 pages and 0 problems; answers.pdf has 11 pages and 0 problems.
- MathJax error-string scan (7 strings) over both PDFs: 0.
- **Pages inspected** (contact sheets, plus zooms of the Example 3 graph and the answer graphs): lesson 27–44 and answers 8–11.
  - Concept headings are kept with their first box.
  - There are no clipped tables or overflowing displays.
  - In the Example 3 graph, the y labels 1/20–5/20 are clear and the "50" label sits clear of the dot at 40.
  - I resized the work boxes to cut white space: Q5 75 mm, Q6 70, Q13 100, Q14 120, and C3 demo/YT 62.
  - The emptiest pages are p27 (Concept 1, about 75% full, because the demo box does not fit under the boxes) and p36 (Worked example 4, about 45%, then the page break before the homework).

## Files changed
- workspace/build/y11ch13/l13b.html, a_13b.html, figs.py
- workspace/build/y11ch13/svg/c13b_coins.svg, c13b_rob.svg, c13b_die.svg, a13b_sum.svg, a13b_tsum.svg, a13b_pick.svg, a13b_thief.svg, a13b_oct.svg, a13b_dodec.svg
- workspace/checks/y11ch13_13b.py
- docs/pp_selected_y11ch13.md (13B section)

## Concerns
1. **0 past-paper marks for 13B.** No clean item exists under the spec's ruling. This needs a controller ruling; the options and my recommendation are above.
2. Money is shown as a math-mode "$" followed by text digits, because qa.py rejects a literal "$". It reads correctly. The dollar glyph comes from the MathJax font.
3. No remaining textbook-answer slips were found. The Section 11A cross-references and the four-coin graph labels are handled as described above.

---
# Follow-up: 13B past-paper note (controller ruling: accept 0 marks)

Commit "Y11Ch13: 13B past-paper note" (not pushed). Files: l13b.html, workspace/checks/y11ch13_13b.py, docs/pp_selected_y11ch13.md, this report.

1. **Lesson.** The end of l13b.html now has a `<!-- ============ Past papers ============ -->` block with the heading `{{sec:amber:clock:Past-paper homework:timed practice}}` and one plain note: "The school trial papers used for this pack (2020–2024) have no question on expected value that can be done without the Year 12 binomial results. For timed practice, do Questions 8, 9, 11 and 12 above in 25 minutes."
   - I changed the suggested "Questions 8–11" because Q10 is the [Simulation experiment]: it needs 36 dice throws and cannot be done as timed practice.
   - Q8 (three coins), Q9 (two cards), Q11 (weighted die) and Q12 (slot machine) are all E(X) calculations. They are roughly 4 + 6 + 6 + 9 minutes, so 25 minutes.
2. **Answers.** I left the past-paper heading out of a_13b.html. With no questions, an "ahead" plus a "Past-Paper Homework – Worked Solutions" heading would be an empty section, and the 13A structure has nothing to put under it. Answers 8–9, 11 and 12 are already in the Textbook Homework answers.
3. **Record.** docs/pp_selected_y11ch13.md, under 13B, now reads "none (controller ruling: no in-scope item)".
4. **Check script.** It now confirms the following:
   - the note block is present;
   - Questions 8, 9, 11 and 12 exist and none of them is a simulation;
   - there is no pp-intro or pp block in the lesson, and no PP section in the answers;
   - the homework parsing stops at the past-paper marker.
   Result: 141 checks, all OK. The 13A check still passes all 192 checks.
5. **Build and QA.**
   - Built with flock. qa.py: lesson.pdf has 44 pages and 0 problems; answers.pdf has 11 pages and 0 problems.
   - MathJax scan: 0 errors in both files.
   - Last page (p44) inspected: the heading and note sit under Q14's work box, together, with no overflow.
