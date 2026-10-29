# Task 5 report: Lesson 13D Sampling, and the Chapter 13 review

Commit 1d6f082 "Y11Ch13: lesson 13D" on branch ch10-pack (not pushed). Staged by explicit path only: l13d.html, a_13d.html, figs.py, 4 new SVGs, workspace/checks/y11ch13_13d.py, docs/pp_selected_y11ch13.md. I did not edit l13c.html or a_13c.html (the 13C fix commit 2a23c32 by another agent landed while I worked), and touched nothing in ch17 or other chapters.

## Status: DONE_WITH_CONCERNS
The lesson and review are complete. The past-paper mini exam has **1 mark** (1 item): a house rule 8 shortfall. After a full sweep this is the only school-paper item that needs just 13D ideas (see "Past papers").

## What I built
**workspace/build/y11ch13/l13d.html** (lesson PDF pages 64–87; review 88–92; the lesson PDF is now 92 pages)
- Lesson head (l.2–4). A small `<style>` at l.1 for the wide tables (`table.tw`) and the random-number table (`table.rn`).
- **Concept 1: sampling a theoretical probability distribution** (l.6).
  - Boxes: "Sampling" (the two opening paragraphs); "Sampling of a theoretical probability distribution" (the rounded four-coin table, the graph `c13b_coins`, "We concluded that E(X) = 2 and Var(X) = 5 − 2² = 1"); "Rounding errors and simulations" (the rounding paragraph and "Can we confirm…"); **Box 9 Sample distribution** (l.25); "Sample statistics and theoretical statistics" (x̄ seldom equals μ).
  - Tutor demo: three coins, theory, then 100 simulations (f = 14, 35, 39, 12): x̄ = 1.49, s² ≑ 0.77, s ≑ 0.88 against μ = 1.5, σ ≑ 0.87. Your turn: two coins, 50 simulations (11, 27, 12): x̄ = 1.02, s ≑ 0.68 against μ = 1, σ ≑ 0.71.
  - Worked example (from the text): the authors' 100 simulations of four coins, with the full sample table, the new graph `c13d_sample`, all the book's bullet explanations and s² ≑ 1.14, s ≑ 1.07.
- **Concept 2: populations, census and survey** (l.75). Box "Populations: census and survey" (all five paragraphs), **Box 10** (l.83). Tutor demo: 50 of 800 students, brothers and sisters (x̄ = 1.64, s ≑ 1.18, census or survey, why x̄ ≠ μ). Your turn: internet survey of 40 visitors, pets (x̄ = 1.375, s ≑ 1.13, not random). **Worked example 8** = textbook Example 8, exoplanets (l.98), with the full table, statistics and solution.
- **Concept 3: sampling when there are no exact probabilities** (l.118). Box with the book's paragraph. Tutor demo: goals in 40 matches (x̄ = 1.8, s ≑ 1.25, two questions before predicting). Your turn: eggs in 25 nests (x̄ = 3.88, s ≑ 1.11, are these exact probabilities?). Worked example (from the text): the 1903 mice litters (all six rows as fractions of 121, x̄ ≑ 4.59, s² ≑ 3.0689, s ≑ 1.75, and all the discussion bullets). Box "Predicting the future" then Worked example (from the text): rainy April days 1913–2012 (two-part table, x̄ = 12.64, s² ≑ 20.89, s ≑ 4.57, the 2013–2017 results and all the questions). This example is allowed to break across pages (it is longer than a page).
- **Concept 4: a correction factor for the sample variance** (l.185). Box **"Extension: a correction factor for the sample variance"** (labelled as the book labels it), with the σn / σn−1 calculator note. Tutor demo: 40 matches, s² = 1.56 → 1.6, sd ≑ 1.26. Your turn: n = 16, s² = 3.75 → 4, sd = 2. Worked example (from the text): rainy days, 20.89 × 100/99 ≑ 21.10, s ≑ 4.59.
- **Textbook homework, Exercise 13D** (l.209): the boxes "Approaching the following exercise" and "Using a spreadsheet" (the book prints them just before the exercise), the exercise's three introductory paragraphs, then **all 14 questions** transcribed in full. Bands as the book: Foundation 1–5 (l.232), Development 6–13 (l.273), Enrichment 14 (l.318). Every table is an HTML table (Q1 a and b, the Q2 theory table with all four rows, the Q4(c)(iii) table beside its text, the Benford table). Q14 has the number-line diagram as SVG `c13d_tank`. Work boxes are small for the investigation questions.
- **A table of random numbers** (l.332): the cautions box, then the whole table (72 rows, 1000 five-digit groups, 14 per row) at l.338. It fills about 1.5 pages.
- **Past-paper homework** (l.340): 1 item, 1 mark, "Suggested time: 5 minutes". The note reads: "This is the only school-paper item that needs just this lesson's ideas. For more timed practice, do Questions 1, 4(c)(iii) and 7(a) above in 25 minutes." These are the three exercise items that can be done by hand from given data.
- **Chapter 13 Review** (l.355) as a new `.lesson` with the eyebrow "Chapter 13 Review", as in Y11 Ch 14 / Ch 15: all 12 questions, in-scope (Q12(b) is a simulation, kept as in the exercise).

**workspace/build/y11ch13/a_13d.html** (answers PDF pages 17–21; the answers PDF is now 21 pages)
- ahead → Lesson Examples C1–C4 (l.2) → Textbook Homework (l.72) → ahead → Past-Paper Worked Solutions (l.102) → `<div class="ans-sec">{{ahead:Chapter 13 Review | Chapter review exercise}}</div>` (l.108), the ch10 / y11ch14 pattern.
- Homework answers: the items with a final answer in the book: 1 (both tables, graphs `a13d_q1a` and `a13d_q1b`, values, c), 2(a), 4(c)(iii) (completed table and values), 7(a) (with E(X²) = 17.901), 12(a), 14(a)(b). The other items are experiments or projects with no book answer.
- PP solution with the choice explained (D is "at least 12"; A and C use 1/6).
- Review answers 1–12 (12(a) only; 12(b) is a simulation).

**workspace/build/y11ch13/figs.py**: `dist_graph` gained `ysub=None` (a subscript after the y-axis label, for f_r); the defaults are unchanged, so every 13A/13B SVG is byte-identical (git shows no change to them). New `tank_line()` and `build_13d()` write c13d_sample, c13d_tank, a13d_q1a, a13d_q1b.

## Source pages used
- Y11 book PDF 670–684, each rendered at zoom 1.6 and read: teaching pages 670–677 (Example 8, Boxes 9 and 10, the extension, "Approaching the following exercise", "Using a spreadsheet"), Exercise 13D 677–682 with the FOUNDATION / DEVELOPMENT / ENRICHMENT headings, the random-number table 683–684. Review PDF 685–687.
- Answers: PDF 937 and 938, each rendered in halves at zoom 2.
- Past paper: Blacktown Boys' High School, 2024, cover "Blacktown Boys' High School 2024 HSC Trial Examination Mathematics Extension 1", Q2 (MC), 1 mark. File `2024/Blacktown Boys 2024.pdf`, question p2 left half (printed p3), solution p9 left half ("2024 Mathematics Extension 1 AT4 Trial Solutions", answer B). Cover, question and solution pages rendered and read. The label matches the Ch 17 / Y11 Ch 15 labels for this paper and is identical in both PDFs.

## Past papers: choice and sweep (house rule 8, spec thin-pool ruling)
- The spec allows 13D at most two 17D rows that need only 13D ideas (sample proportion or sample mean as a statistic, no normal approximation).
- **Taken: E18, BBHS 2024 Q2.** "At most 12 of 18 rolls show a 3" is the event p̂ ≤ 12/18 = 2/3. It needs only the idea that a sample proportion is a relative frequency f/n (13D Box 9). The stem defines p̂, so no Y12 notation is assumed. The hint: "a proportion of the rolls is a relative frequency, like f_r in this lesson."
- **Not taken (every other 17D row):** E1/E6/E14, E2, E3, E4/E12, E5, E8, E10, E11, E13, E15, E16, E17, E20 all need E(p̂) = p, Var(p̂) = pq/n or a normal approximation. E9 (Killara 2023 Q14(b)(i), "Find the sample proportion and sample standard deviation", 2 marks): the SD part needs pq/n, and the catalogue flags the wording as ambiguous. E19 doubtful, E7 excluded paper.
- **My own sweep**: a keyword search ("sample mean", "sample variance", "sample standard", "census", "survey", "frequency table", "relative frequenc", "simulat", "random number", "sample proportion", "sampl") over every text-layer school paper 2020–2024, skipping the commercial and excluded files. Every hit is a p̂ / normal item above, a binomial item, or the word "Sample" on an MC instruction or a sample paper. The catalogue records that the scanned papers were checked by eye and have no 13D item. Script and output: /tmp/claude-0/-home-user-Hw/33fce1a1-283b-5e23-bc89-9ac277c110f5/scratchpad/work/y11ch13-t5/scripts/sweep.py and sweep.out.
- **Ch 17 effect**: 17D loses 1 mark (E18) of about 47; Ch 17 keeps well over 15 clean 17D marks.
- **Records read**: docs/PAST_PAPERS_USED.md and every docs/pp_selected_*.md (ch10, ch17, y11ch13, y11ch14, y11ch15) before choosing and again just before committing (Ch 17 had committed 17B by then: BBHS 2024 Q2 is still free; BBHS 2024 Q6 (17A) and Q12(d) (Y11 Ch 15) are different questions). Recorded in docs/pp_selected_y11ch13.md, section 13D.
- **Time**: 1.5 × 1 = 1.5 rounds to 0 at 5-minute steps; I printed "5 minutes" (the smallest step). The cover placeholder `@@M13D@@` is left for Task 6 (it should read 1 mark).

## Fidelity notes, fixes and omissions
Nothing is omitted from the teaching pages, the exercise or the review. No doubtful exercise item was found that needed dropping.
- **Teaching-text slip, corrected with no remark:** PDF 670 prints "Var(X) = 5² − 2² = 1"; printed as "5 − 2² = 1" (E(X²) = 5 from the table).
- **Printed textbook answer slips, own answers with no remark:**
  - Ex 13D Q1(a) answer table (PDF 937) prints p(2) = 8/27; the question has 6/27, and the book's own xp(x) = 12/27 and x²p(x) = 24/27 cells need 6/27. Printed 6/27 (and the empty p(x) Sum cell as 1).
  - Review Q2 answer labels are printed "a Yes, a No, b No"; printed a Yes, b No, c No (with the sums 1.2 and 19/24 added).
  - Review Q5(b) prints "$27.22 × 52 = $1415.56", but 27.22 × 52 = 1415.44. Printed 52 × 245/9 ≑ 1415.56 (the book's value, from the exact mean).
- **Typographic or wording fixes in the exercise (no remark):**
  - Ex 13D intro "the subsequent questions all takes some time" → "all take".
  - "Using a spreadsheet": "it may generate or 0.865…" → "it may generate 0.865…" (stray "or").
  - Q14(c)(ii) "a random number from 1 and N" → "from 1 to N".
  - Q5 "There is also a list of 10 000 random numbers at the end of this exercise": the printed table has 1000 five-digit numbers (5000 digits), so "10 000" matches neither count. I printed "a list of random numbers" (count dropped). The controller may prefer the book's wording.
  - Review Q6 "Var(X) = (E(X − μ)²)" (misplaced bracket) → "Var(X) = E((X − μ)²)", as in 13C.
  - Em dashes in the book's prose became colons, commas or full stops (heading "Populations — census and survey" → "Populations: census and survey", Box 10 title, "Extension —" → "Extension:", "x̄ = 1.96 — placing a bar…" → two sentences, Q3(c), Q3(e), Q6, Q7, Q8 and others). Example 8's "x̄ = 1.37 planets" is printed with ≑ (1.3680 rounded).
- **Textbook figures (PDF 670):** both graphs (the four-coin p(x) graph and the sample f_r graph) have the same tick slip as on 643/652/661: dots at 0–4 under tick labels 1–5. My graphs label 0–4 (reused c13b_coins, new c13d_sample).
- **Pack wording (not the book's):**
  - Box titles "Rounding errors and simulations" and "Sample statistics and theoretical statistics"; the text inside is the book's.
  - Linking sentences: "Their results are in the worked example below." (replacing "Here are the results:"), "The first worked example below, about litters of mice, comes from the text.", "The worked example below, about rainy days in April, comes from the text.", "The worked example below uses it." (in the extension box), and "compared with the theoretical graph in the box above".
  - "as Example 8 shows" → "as Worked example 8 shows"; "the example above about rainy days" → "the worked example above about rainy days".
  - The four text examples (four-coin sample, mice, rainy days, correction) are posed as questions in my words; their solutions are the book's text and numbers.
  - "Approaching the following exercise" and "Using a spreadsheet" are teaching text; they sit at the start of the homework section because the book prints them immediately before Exercise 13D.
- **Demos and your-turns:** all eight are new value-changed variants. The C4 demo reuses the C3 demo's 40 matches (x̄ = 1.8, s² = 1.56).

## Verification
- `python3 workspace/checks/y11ch13_13d.py`: **165 checks, all OK**, exit 0.
  - Every table is read cell by cell. Theoretical tables are checked against enumerations (2, 3 and 4 coins by itertools.product; three dice for Q1; two dice, sum and |difference|, for Q2 and Q4(c)(iii)). Sample tables are recomputed from the printed frequencies: f_r = f/n, x f_r, x² f_r and the sums, exact, or to the book's 4 decimals for Example 8.
  - x̄, s² and s are recomputed exactly and compared with the printed roundings; the answer chains are parsed by template (each template must match once).
  - Concept 1 checks the 2-dp rounded probabilities, the unrecalculated rows, the book's "1.50 is not 2² × 0.38" remark and "Var = 5 − 2² = 1".
  - Rainy days: 100 years from 1913 to 2012; the two halves of the solution table join to the statement's frequencies; the correction 20.89 × 100/99 ≑ 21.10 also follows from the unrounded s².
  - Q5 μ and σ² of the uniform distributions on 0–9 and 1–8; Benford's percentages add to 100% and give μ = 3.441, σ ≑ 2.46; 2³⁶ ≑ 6.8719 × 10¹⁰; Q14's formula and its SVG (crosses at 3, 6, 9, dots at 1 and 11, m and N labels placed).
  - The random-number table is compared group by group with the text layer of PDF 683–684 (1000 groups, 72 rows).
  - PP: the event "at most 12 of 18" is compared with the event of each option; only B matches; D is "at least 12".
  - Review: sums of probabilities (Q2, Q3), E(X) rows (Q4), the meal prices and ratings parsed from the statement (Q5), E/Var/σ for Q6–Q8 (Q7 uses Q6's tables), the linear transforms (Q11), the uniform 5–9 (Q12).
  - Figures: figs.build_13d() re-run with dist_graph recorded; structure: 4 concepts, boxes, Boxes 9 and 10, the extension, 4 demos, 4 your-turns, the worked examples, answer blocks, bands, PP label (identical in both files), marks, time, one hint; no literal "$"; no em dash in the lesson prose.
- **Mutation tests**: 15 single edits in copies via Y11CH13_SRC, **all 15 detected** (exit 1): an Example 8 cell, a rainy-day statement frequency, a rainy-day x²f_r cell, a C1 s rounding, answer 1(a) p(2) back to 8/27, review 5(a) 27.22, a random-number group, the PP answer letter, "5^2 − 2^2", the mice s, review 11(c), a demo statement frequency, the Benford μ, the C4 corrected variance, and the c13d_sample data in figs.py. Script: /tmp/claude-0/-home-user-Hw/33fce1a1-283b-5e23-bc89-9ac277c110f5/scratchpad/work/y11ch13-t5/mut/mut.py.
- Other checks: y11ch13_rev 97 / 0 failures, y11ch13_13a 192 OK, y11ch13_13b 141 OK, y11ch13_13c 173 OK (figs.py change harmless).
- Build: `cd workspace/build && flock /tmp/claude-0/-home-user-Hw/33fce1a1-283b-5e23-bc89-9ac277c110f5/scratchpad/build.lock sh -c 'python3 build.py y11ch13 all && mv lesson.pdf answers.pdf y11ch13/'`.
- qa.py: lesson.pdf **92 pages, 0 problems**; answers.pdf **21 pages, 0 problems**.
- MathJax error-string scan (7 strings, PyMuPDF get_text) over both PDFs: **0**.
- Word-level diff of the lesson text against the book's text layer (PDF 670–687): the only differences are the layout, the intended fixes and the pack wording listed above.
- **Pages inspected** (contact sheets at zoom 0.8 plus zooms): lesson 64–92, answers 17–21.
  - At first every exercise question started a new page. The questions were just too tall at full work-box size, so I shrank the work boxes of the investigation questions (12–30 mm) and of some demos.
  - Box splits and order: the four-coin box was split so Concept 1 starts well; "Predicting the future" sits just before the rainy-days example, which may break across pages.
  - No clipped tables or overflowing displays; headings stay with their boxes. The emptiest pages: p74 (end of the rainy-days example, then the Concept 4 box, about 75% full; the demo does not fit under it), p75 (Concept 4 demo, your turn and worked example, about 70%, then the page break before the homework), p90 (review Q6 only, about 60%), answers p20 (Q12 and Q14 only, before the forced past-paper page).

## Files changed
- workspace/build/y11ch13/l13d.html, a_13d.html (placeholders replaced), figs.py
- workspace/build/y11ch13/svg/c13d_sample.svg, c13d_tank.svg, a13d_q1a.svg, a13d_q1b.svg (new)
- workspace/checks/y11ch13_13d.py (new)
- docs/pp_selected_y11ch13.md (13D section)

## Concerns
1. **1 past-paper mark** (house rule 8 shortfall). No other clean 13D-only item exists in the 2020–2024 school papers (sweep above). The note points to Exercise 13D Q1, Q4(c)(iii) and Q7(a) for 25 minutes of timed practice. Time printed as 5 minutes for the single 1-mark MC.
2. **Q5 "10 000 random numbers"** printed without the count (the table has 1000 numbers). The controller may prefer to keep the book's words.
3. **Silent corrections**: the Var(X) = 5 − 2² teaching slip, three answer-key slips (13D Q1(a) p(2), review Q2 labels, review Q5(b) arithmetic), Q14(c)(ii) "from 1 to N", review Q6 bracket, and the graph tick labels. Details are above.
4. The lesson is long (24 lesson pages + 5 review pages), mostly because Exercise 13D is a set of projects transcribed in full and the random-number table takes 1.5 pages.
