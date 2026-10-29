# Ch17 Task 1 report: scaffold, cover, normal review, standard normal table

Status: DONE_WITH_CONCERNS (the concerns are minor and listed at the end)
Commit: `2965ab9 Ch17: scaffold, cover, normal review` on `ch10-pack` (not pushed). It stages only my files.

## What I built
All files are under `workspace/build/ch17/`.
- `pack.json`: the lesson parts are cover, revision and l17a–l17d. The answer parts are a_rev and a_17a–a_17d. The footers and the answers heading are exactly as the spec gives them.
- `cover.html`:
  - The title is "Year 12 Chapter 17 / Binomial Distributions", split over two balanced lines.
  - The rows are: Revision "The normal distribution", note "Year 12 Advanced · Ch 16"; 17A Binomial probability; 17B Binomial distributions; 17C Normal approximations to a binomial; 17D Sample proportions (titles from the textbook section heads on PDF 802/811/823/835); Review.
  - Each lesson note reads `Past papers: @@M17A@@` … `@@M17D@@`, ready for Task 6 to fill.
  - The intro line adds one sentence: "The standard normal table is on the last page of the Revision section."
- `revision.html` (8 PDF pages, lesson pages 2–9):
  - Box "The standard normal distribution (16D)" (l.6): φ(z), the features in Box 7, Φ(z), how to read the table, P(Z = a) = 0, and the symmetry rules. Figures `phi_pdf` and `phi_area`.
  - Textbook Example 10 (l.21), with full working and five shaded-curve SVGs (`ex10a`, `ex10b1`–`ex10b4`).
  - Box "The empirical rule, and reading the table in reverse (16D)" (l.42): Box 8 with the three 68/95/99.7 curves (`emp1`–`emp3`), reverse lookup and interpolation, quartiles rounded to 2 d.p., and the IQR criterion. It includes a CDF graph (`Phi_cdf`) with the 0.75 and 0.9 lines.
  - Textbook Example 13 (l.54), in full, including its Note.
  - Box "General normal distributions and z-scores (16E)" (l.67): Boxes 9 and 10, X ~ N(μ, σ²), standardising, and the empirical rule for X. Figure `gen_normal`.
  - Textbook Example 15 (l.79).
  - Box "Applications of the normal distribution (16F)" (l.94), followed by Textbook Example 17 (l.100).
  - Warm-up (l.114), starting on a new page. Six questions, each labelled with its exercise:
    - Q1: Exercise 16D Q9, parts a, b, c, g, i, j, relabelled a–f.
    - Q2: Exercise 16D Q12, parts b, d, e, h, k.
    - Q3: Exercise 16D Q14, parts a, c, d, e.
    - Q4: Exercise 16E Q6, parts a, c, d, f.
    - Q5: Exercise 16F Q2, all parts, with "(use the empirical rule)" as the exercise directs.
    - Q6: Exercise 16F Q7, all parts.
  - The standard normal table page (l.~135; table at l.146). It is the **last page of the Revision section**. Later lessons cite it by name as "the standard normal table at the end of the Revision section", not by page number.
    - Layout: z from 0.0 to 3.9 in rows, columns "+.00" to "+.09" under the heading "second decimal place", as in the textbook (PDF 829–830).
    - Values: 400 values from `math.erf`, to 4 d.p.
    - Intro text: the textbook's own intro and its Φ(1.627) interpolation example, plus a shaded graph. A one-line note covers negative z and z ≥ 4.
    - The table's CSS is inline in `revision.html`. Shared `pack.css` is untouched.
- `a_rev.html`: worked answers for the six warm-up questions. They use the "Chapter revision | Warm-up" heading, and each question is labelled with its exercise.
- `figs.py`: the header is copied from the model (Fig/Graph). `fig_rev()` writes the 12 SVGs into `svg/`. Later tasks add their own functions.
- Placeholders: `l17a`–`l17d.html` and `a_17a`–`a_17d.html` each contain only `<!-- filled by Task N -->` (N = 2–5).
- `workspace/checks/ch17_rev.py` has three parts:
  - **Table.** All 400 printed values are checked against erf to 4 d.p. They are also checked against the textbook's 400 printed values, which are embedded in the script. I transcribed them from PDF 829–830 by text extraction and spot-checked them against the rendered pages: rows 0.0, 1.6, 2.4, 2.9, 3.4, 3.9 in full, plus others. The script also checks the header and the row order.
  - **Box and example values.** It checks the values printed in the boxes and in Examples 10, 13, 15 and 17, using table lookups and interpolation, plus bisection for Q₃ = 0.67449.
  - **Warm-up.** The givens are parsed from `revision.html`. Answers are recomputed by table lookup, with z to 2 d.p. and Φ to 4 d.p., or by the empirical rule. Every number printed in `a_rev.html` is compared with these, and each final answer is also compared with the textbook's printed answer.
  - Each template must match exactly once, and the script exits with status 1 on any failure.

## Sources used (rendered and read)
- 16D: PDF 768–779. 16E: PDF 780–788. 16F: PDF 789–791.
- Answers: PDF 956–958, rendered in halves at zoom 2.
- Standard normal table: PDF 829–830, rendered at zoom 2.2.
- 17A–17D title pages: PDF 802, 811, 823, 835 (text only, for the cover titles).

## Omitted or adjusted, and why
- **Example 11 (16D) is not used. It looks doubtful.** Part b ii asks for P(−2.9 ≤ Z ≤ 0.6), but the printed solution works out P(−1.7 ≤ Z ≤ 0.6) = 0.6811. Example 10 covers the same symmetry methods. I did not mention this in the pack.
- **Example 12 (16D) is not used. It looks doubtful.** In part b, 840 scores are above b, so 160 are below. That puts 680 (68%) between −b and b, so b ≈ −1, but the book prints b ≑ −2.
- **Warm-up parts I avoided:**
  - 16D Q12c, because the book's answer carries an "inaccuracy" note.
  - 16E Q4f, because the book's answer 0.1475 does not match the empirical rule value of 0.135.
  - 16F Q10a, because the book prints 12% where z = −1.22 gives 11%.
  - 16F Q8, because its answer is muddled.
- **Example 10 cross-references fixed.** The textbook's working says "from part a", "by part b" and "by part c" where it means b i, b ii and b iii. I wrote "from part i", "by part ii" and "by part iii". This changes the references only, not the maths. Example 10 b's working is also laid out in running lines rather than the book's columns, to save space. Every step is kept.
- **Graph-lookup lines kept.** Example 13 says "This agrees with the horizontal line … on the graph of Φ(z)". I kept these lines and added a small Φ(z) graph so that they make sense.
- **"Supplied table" wording kept.** Warm-up Q6 (16F Q7) keeps the textbook's "Read the supplied standard normal distribution table". The supplied table is the pack's table on page 9.
- **Rounding choices in my answers.** The Q6c(i) answer explains 1.65 using the two-decimal table (Φ(1.64) = 0.9495, Φ(1.65) = 0.9505, so z ≈ 1.645). It also notes that interpolating between Φ(1.6) and Φ(1.7) gives about 1.65, which is the book's own hint. For Q6b and c(ii) I printed 186 and 197 cm, as the book does, from 185.6 and 197.375.

## Verification
- `python3 workspace/checks/ch17_rev.py`: 261 checks passed, 0 failures, exit 0.
- Mutation tests used the `CH17_SRC` env var on copies in scratch. Each of these changes made the script exit 1 with the right FAIL line:
  - a table value changed;
  - a printed answer changed;
  - a given changed;
  - a printed height changed;
  - an example value changed.
- Build: `flock … python3 build.py ch17 all && mv lesson.pdf answers.pdf ch17/` succeeded.
- `qa.py`: `ch17/lesson.pdf 9 pages, 0 problems`; `ch17/answers.pdf 2 pages, 0 problems`.
- MathJax error scan (PyMuPDF get_text for the seven error strings): clean on both PDFs.
- Pages inspected:
  - Every lesson page (1–9) and both answer pages, at zoom 1.0–1.25, over several layout rounds.
  - An early build had one display line too wide, which made Chrome shrink the whole PDF. I split it over two lines.
  - Example 10 is allowed to break across pages. The break falls after part a, and the "b" label stays with its graphs.
  - The warm-up starts on a new page so its heading is not stranded.
  - The table fits on one page.
  - Final state: no clipping and no overflow. Page 4 (Example 13 alone) and page 6 are each about one-third empty, because the next box or example cannot fit there.

## Files changed
- `workspace/build/ch17/`: pack.json, cover.html, revision.html, a_rev.html, figs.py, svg/*.svg (12 files plus .gitkeep), l17a–d.html and a_17a–d.html (placeholders).
- `workspace/checks/ch17_rev.py`.

## Concerns / notes for the controller
1. Examples 11 and 12 and the warm-up parts listed above look doubtful in the textbook. I avoided them quietly and the pack says nothing about them.
2. **Later lessons cite the table by name, not by page number:** "the standard normal table at the end of the Revision section". After the fix round the table is on lesson PDF page 10, and its page number moves whenever the Revision section changes length.
3. The two-decimal table differs from the textbook's one-decimal table in Ch 16. The examples copy the textbook's one-decimal interpolations (for example, Φ(1.2) and Φ(1.3) in Example 13). Every value they use is in the pack's table, so they still read correctly.

## Fix round 1 (review polish, 2026-10-29)
Commit: `5715881 Ch17: normal review polish`. It stages only my files and is not pushed.

1. **New worked example after Example 10.** It is titled "More symmetry: intervals that are not centred on 0" and is unlabelled; it does not refer to the book's Example 11.
   - a: P(−2.3 ≤ Z ≤ −0.6) = P(0.6 ≤ Z ≤ 2.3) = Φ(2.3) − Φ(0.6) ≑ 0.9893 − 0.7257 ≑ 0.2636. This is the both-negative case.
   - b: P(−1.4 ≤ Z ≤ 0.9) = Φ(0.9) − (1 − Φ(1.4)) ≑ 0.8159 + 0.9192 − 1 ≑ 0.7351. This is the straddling case with unequal ends.
   - Two new shaded-curve figures go with it: `sym_a` and `sym_b`.
   - `ch17_rev.py` reads the givens from the question line and checks every printed step. It also checks that each table result is within table rounding (±0.0001) of the direct erf value, which is 0.2635 for a and 0.7352 for b.
2. **Two-decimal-table lines.**
   - After Example 13: Φ(1.28) ≑ 0.8997 is the entry closest to 0.9, so z ≑ 1.28; Φ(0.67) ≑ 0.7486 is the entry closest to 0.75, so Q₃ ≑ 0.67.
   - After Example 15c: Φ(2.05) ≑ 0.9798 is the entry closest to 0.98, so z ≑ 2.05 and a ≑ 141, the same answer. The closest entry is 2.05, not the 2.06 found by interpolation.
   - The script finds each closest table entry itself, fails on a tie, and compares the result with the printed lines.
3. **Figures.**
   - emp1–emp3: dropped the peak label and moved the percentage labels off the y-axis to the upper right.
   - phi_area and phi_area_small: moved z to 1.6 and added a tick with an italic "z" marker on the axis. The Φ(z) label now sits inside the shaded area, clear of the curve. The small version drops the "1" tick label.
   - All φ curves: the 1/√(2π) ≈ 0.4 label is raised clear of the peak, and the y-range is extended to make room.
   - Phi_cdf: made the graph taller and removed the crowded "1" tick label. The dashed asymptote is now labelled "y = 1" at the left, and "y = Φ(z)" sits below the curve on the right.
4. **Report.** The note on citing the table is updated above.
5. **Other file in the directory.** `workspace/build/ch17/figs_17a.py` is untracked and was not created by me (presumably the Task 2 agent's). I did not touch it.

**Verification**
- `python3 workspace/checks/ch17_rev.py`: 304 checks passed, 0 failures, exit 0.
- New mutation tests each exited 1: the Sym a result changed, the Ex15 two-decimal z changed, and a Sym b given changed.
- Build with flock succeeded. `qa.py` reports lesson.pdf 10 pages, 0 problems, and answers.pdf 2 pages, 0 problems. The MathJax scan is clean on both PDFs.
- The Revision section is now 9 pages (lesson pages 2–10); the table is on page 10.
- Pages inspected: 2, 3, 4, 5, 6 and 10 at zoom 1.25, with the figure rows on pages 2, 4 and 10 at zoom 2.2–2.5. No overlaps, no clipping and no stranded headings.
