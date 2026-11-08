# Task Int1 lesson 5H report: The trapezoidal rule

Status: DONE_WITH_CONCERNS. The concerns are:
- the past-paper shortfall, which the catalogue predicted (1 mark);
- the textbook items I omitted or corrected quietly (listed below).

## What I built
- `workspace/build/int1/l5h.html` (it replaces the placeholder).
  - **Lesson head** (l.1-3).
  - **Concept 1** (l.5-74): the trapezoidal rule, and subdividing the interval.
    - Box "Why approximate?" and box "The trapezoidal rule". The second box has the figure `c5h_one` and the width / average-of-parallel-sides derivation.
    - Box 18.
    - Tip "Where the formula comes from".
    - Box "Subdividing the interval".
    - Tip "How the pieces fit together".
    - Tutor demo: 12/x on [1,4] with 1 and then 3 subintervals. Your turn: 60/x on [2,5] with 1 and then 3 subintervals.
    - **Worked example 32**, with the figure `c5h_e32`.
    - Tip "Steps the book skips: Worked example 32", which adds the fractions over 120.
    - Box with the book's Note on equal subintervals.
  - **Concept 2** (l.76-125): concavity.
    - The book text and Box 19.
    - Tip "Recall: concavity (Year 11)".
    - Tutor demo: 50x − x⁴ on [1,3], which underestimates. Your turn: x³ + 1 on [1,3], which overestimates. Each has a part c that finds the exact value.
    - **Worked example 33**.
    - Tip with the table arithmetic, the sign of y'', and a check against the exact value 1775.2.
  - **Concept 3** (l.127-215): the formula for n subintervals.
    - Book text, the number-line figure `c5h_div`, the full derivation, Box 20 and the rearrangement.
    - Tip "The steps of the derivation, filled in".
    - Box "Using the formula".
    - Tutor demo: dam inflow in m³/s, converted to millions of m³ per hour. Answer 31.59, worked with both formulas.
    - Your turn: a tank, 1225 L, worked with both formulas.
    - **Worked example 34**, with the Peachtree Creek graph recreated as `c5h_creek`.
    - Tip covering the conversions, the doubled values and the units.
  - **Concept 4** (l.217-280): spreadsheets.
    - Book text, and tip "Reading the spreadsheet".
    - Tutor demo: ∫₀^0.5 φ with 10 subintervals, about 0.1914, an underestimate. Your turn: ∫₁² φ with 10 subintervals, about 0.1360, an overestimate. The fact φ'' = (x²−1)φ is given in the question.
    - **Worked example 35**, with all six steps.
    - Tip with the whole sheet (rows 2-4, L4 = 6.822861, L5 = 0.341143).
    - Box "More subintervals".
  - **Textbook homework** (l.282-): Exercise 5H, verbatim.
    - The Technology note, then F Q1-6, D Q8-14 and E Q15-17.
    - It includes the spreadsheet investigation, "Possible spreadsheet projects" and the web-graph investigation.
    - Figures recreated: Q11 lake, Q12 rock cutting, Q17 hydrograph.
  - **Past papers**: PP 1, then the timed-practice note.
- `workspace/build/int1/a_5h.html`
  - The ahead heading.
  - Lesson Examples C1-C4. Every chain has full working; C4 has the spreadsheet tables.
  - Textbook Homework Q1-6 and Q8-17, with working. Q4 and Q5 have diagrams (`a5h_q4a`, `a5h_q4b`, `a5h_q5`).
  - The ahead heading again, then the PP 1 worked solution.
- `workspace/build/int1/figs_5h.py`
  - It makes 11 SVGs: `c5h_*` (4), `q5h_*` (3), `p5h_sgs` and `a5h_*` (3).
  - The data of the two river graphs are module constants, which the check script reads.
- `workspace/checks/int1_5h.py`: 431 checks.
- `docs/pp_selected_int1.md`: a `## 5H` section added.

## Sources
- Textbook `workspace/zip/Math Textbook CMS6 Ext1 Y12.pdf`. I rendered and read each page; the figures and the derivation were read from zoomed clips.
  - Teaching pages: PDF 270-276 (printed 244-250).
  - Exercise 5H: PDF 276-279.
  - Answers: PDF 892 (bottom of the right column) and PDF 893 (left column, Q4-15d). The key has no answers for Q16-17.
- Past paper: **PP 1**, Sydney Grammar School 2023, "Trial Examination, Form VI Mathematics Extension 1".
  - Q3, 1 mark, MC.
  - File `2023/Sydney Grammar 2023 3U.pdf`, question p4. Solution in `2023/Sydney Grammar 2023 3U Solutions.pdf`, p1 (handwritten, A).
  - It is catalogue row 1.9-01, the only int1-L9 row.
  - The diagram is recreated as `p5h_sgs`.
  - Before choosing and again before committing, I re-read every pp_selected_*.md and PAST_PAPERS_USED.md, and grepped the built packs. SGS23 Q11(c), Q12(a), Q12(b) and Q13(a) are used elsewhere; Q3 is not used anywhere.

## Omitted, corrected or doubtful items
- **Ex 5H Q7 omitted (doubtful, house rule 6).** Its table prints x = 9, 10, 11, 12, **12**, 13, 14, 15, but parts b and c need x = 9 to 16.
- **Question label typos fixed silently.**
  - Q13 prints "a, a"; we print a, b.
  - Q15 prints "a, a, b, c"; we print a-d. The key's "15 d" confirms the intended letters.
  - Q16: "use a spreadsheet estimate" is printed as "use a spreadsheet to estimate".
- **Key slip, Q12.** The key gives 5900. The heights 5, 10, 13, 14, 11, 7, 3 at 50 m intervals give 25 × 118 = 2950 m², which is what we print. The key is exactly double; the check script records this.
- **Book slips, written correctly without comment** (they are slips in the teaching text and solution lines, as in the 5E precedent):
  - Box 18: "Approximating the curve from x = 1 to x = b" is printed as "from x = a to x = b".
  - Derivation: "b = x_{n+1}" is printed as x_n.
  - Derivation: the second integral's limits "∫_{x2}^{x1}" are printed as ∫_{x1}^{x2}.
  - Rearranged formula: "2(f(x1) + 2f(x2) + ⋯ + 2f(x_{n−1}))" is printed as 2(f(x1) + f(x2) + ⋯ + f(x_{n−1})).
  - Example 34, text against graph title: "4th December" is printed as "24th December", to agree with the graph title "Dec. 24, 2002".
  - Example 34: the integral's upper limit 20 is printed as 24, in both chains.
  - Example 34: the missing term 41.76 (that is, 2 × 20.88, the doubled value at t = 12) is restored in the first sum. The book's total of 223.2 is correct.
  - Example 34: the second-formula bracket "…+14.76+62.48+1.44+1.08" is printed as "…+14.76+6.48+2.88+2.16".
  - Example 35: "The correct approximation to three decimal places is 0.398" is printed as "The correct value to four decimal places is 0.3413". The integral is 0.34134; 0.398942 is φ(0).
  - Example 35, two small typos: "column D and row is labelled D3" gets "row 3", and "one standard deviations" becomes "deviation".
- **Recreated graphs.**
  - Example 34 and Q17 are drawn from data constants that pass through the book's table values. For Q17 these are my own readings of the book's graph.
  - The rotated axis labels of both books' graphs are set horizontally. The overlap tool cannot read rotated text, and the result is clearer.
  - In Q17 the date-time labels are set as "17:40" above "04/05", and the axis title reads "Fecha (día/mes, 2004)". The stem gives the full date-times.
- **Answers that are ours.**
  - The key gives nothing for Q16 and Q17. Q16 is computed, and Q17 uses readings from our graph, marked "yours may differ a little".
  - Q2, Q14 and Q15 have added working.
  - Q4 has diagrams.
- **Past papers.** This is a house rule 8 shortfall: 1 mark, 5 minutes. The note reads: "This is the only school-paper item that needs just this lesson's ideas. For more timed practice, do Questions 5, 9(c), 12, 13 and 14 above in 25 minutes."
  - SGS 2022 Q12(c)(ii) uses the trapezoidal rule, but it is tagged int3-L6, so I did not take it.
- **Cover placeholder `@@M5H@@`.** It is not my file. Suggested value: "1 mark · timed practice".

## Verification
- **`python3 workspace/checks/int1_5h.py`: 431 checks, 0 failures, ALL OK.** It checks the following:
  - Every trapezoidal estimate is recomputed by its own implementation of the rule, from the stem integrand and limits (Q8, Q9, Q13, Q16, demos) or from the printed tables (Q1-3, Q10, WE34, C3, Q17). It is compared to the printed rounding: the 2 or 3 significant figures and decimal places asked for.
  - Every member of every chain is checked. f(k) terms are substituted, and [F]ₐᵇ brackets are evaluated with sympy.
  - Exact integrals use sympy.integrate, and the concavity signs are checked on a grid.
  - Spreadsheet tables: every φ value to 6 dp, every doubled value, and the L4 and L5 values.
  - WE34: the table equals the drawn curve, R = flow × 3600/10⁶, and every term in the sums.
  - Q17: the readings equal the graph data, and the peak and heavy-rain times are right.
  - The figure labels for Q11 and Q12, read from the SVGs.
  - The book key, transcribed (the Q12 slip is recorded).
  - Q7 is absent, and the bands are F 1-6, D 8-14, E 15-17.
  - PP 1:
    - the label in both files, 1 mark, 5 minutes;
    - one hint, with a test that it is neutral;
    - only (A) equals the estimate, for a = 3, e and 10;
    - the questions named in the timed-practice note exist.
- **Mutation tests** (INT1_SRC scratch copies). I made 14 single edits, for example:
  - the WE32b result;
  - a C1 chain line;
  - the Q9c stem;
  - A8d;
  - A12 changed to 5900;
  - a spreadsheet row-4 cell;
  - an A17b R value;
  - a WE34 R value;
  - the C4 L4 value;
  - the PP hint;
  - A13a;
  - a WE33 table value;
  - a Q17 reading;
  - the C1 demo stem.

  Each one gives exit 1 with the matching MISMATCH. The test exposed one gap (the stated L4 value), which I closed.
- **`workspace/tools/svg_overlap.py`** on all 11 of my SVGs: 0 problems. A Chrome getBBox clip check also reports none.
- **Solo build** (scratch pack.json with only l5h and a_5h):
  - lesson 27 pages, answers 9 pages;
  - qa.py 0 problems in each, MathJax scan 0;
  - body text **11.3 pt in both**;
  - overflow probe: 0 elements.
- **Full flock build** `python3 build.py int1 all`:
  - lesson.pdf 266 pages and answers.pdf 100 pages, qa.py 0 problems in each;
  - MathJax scan 0;
  - body text 11.3 pt in both.
- **Pages inspected**: every page of the solo lesson (1-27) and answers (1-9), as grids.
  - Fixed during this: over-wide chains and tables (split, or transposed spreadsheet tables), work-box sizes, a stranded "Possible spreadsheet projects" heading, Q17 overflow and a small Q5 answer figure.
  - Pages that are still partly blank because the next block cannot fit: lesson p.11 (before the C3 demo, about 45% blank), p.15 (before the C4 demo, about 40%) and p.26 (before the past-paper page).

## Files and commit
- Files:
  - workspace/build/int1/l5h.html
  - workspace/build/int1/a_5h.html
  - workspace/build/int1/figs_5h.py
  - workspace/build/int1/svg/{c5h_one,c5h_e32,c5h_div,c5h_creek,q5h_11,q5h_12,q5h_17,p5h_sgs,a5h_q4a,a5h_q4b,a5h_q5}.svg
  - workspace/checks/int1_5h.py
  - docs/pp_selected_int1.md
- Commit 4e095b5 `Int1: lesson 5H` on ch10-pack (not pushed). I staged only these paths.

## Concerns
1. The past-paper shortfall: 1 mark, the only int1-L9 row.
2. Q7 is omitted as doubtful, and the Q12 key slip is handled quietly.
3. Example 34 has several printing slips, which I corrected silently (listed above). The controller may want to note them.
4. The Q17 answers depend on graph readings. Ours come from our recreated graph and are labelled approximate.

## Fix round 1 (review: APPROVED, one fix)
- **Q17 graph data.** The reviewer measured the book's curve against its gridlines. In `figs_5h.py`, `Q17_FLOW` now has 7.6 at t = 30 (it was 7.4), 12.7 at t = 33 (it was 13.2) and 11.0 at t = 36 (it was 10.3). The peak (14.7 near t = 34) and the other points are unchanged.
- **Q17 answers recomputed** (`a_5h.html`):
  - b: the readings 3.3, 4.0, 7.6, 12.7, 11.0, 7.4 and 6.3 give R = 11.88, 14.4, 27.36, 45.72, 39.6, 26.64 and 22.68. Then 1.5 × (11.88 + 2(14.4 + 27.36 + 45.72 + 39.6 + 26.64) + 22.68) = 1.5 × 342 = 513, about 513 thousand m³.
  - c: 513 ÷ 143.64 ≑ 3.6, so about 3.6 times as much. Part a is unchanged.
- **Check constants** (`int1_5h.py`): 513 replaces 509, and 3.6 replaces 3.5. The readings are still compared with the drawn data.
- **Silent fixes added to the list above**: Box 18 "x = 1" printed as x = a, and the inserted 20.88 (as 41.76) in Example 34.
- **Commands and outputs:**
  - `python3 workspace/checks/int1_5h.py`: 431 checks, 0 failures, ALL OK.
  - `svg_overlap.py` on all 11 of my SVGs: 0 problems.
  - Solo build: lesson 27 pages, answers 9 pages, qa 0/0, MathJax 0, body text 11.3 pt in both, overflow probe 0.
  - Full flock build `python3 build.py int1 all`: lesson 266 pages, answers 100 pages, qa 0/0, MathJax 0, body text 11.3 pt in both.
  - Pages inspected: lesson p.25-26 (Q17) and answers p.8 (Q17 answers).
- Commit 7bf244d `Int1: 5H review fixes`; not pushed.
