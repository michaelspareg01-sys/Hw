# Int1 assembly: Integration basics (4J–5I + Chapter 5 review). Assemble, record, final QA, deliver

Status: DONE_WITH_CONCERNS. The concerns are minor; see the end of this report.

## Delivered
- `output/Year_12_Ext1_Integration_Part1_Basics_Lesson_and_Homework.pdf`: 264 pages. Page 1 reads "Year 12 Integration Part 1 / Integration Basics / Lesson and Homework Pack". It was 268 pages before the layout fixes below.
- `output/Year_12_Ext1_Integration_Part1_Basics_Homework_Answers.pdf`: 99 pages. Page 1 reads "Integration Part 1 Integration Basics - Homework Answers". It was 100 pages.
- Both PDFs come from the final flock build in `workspace/build/int1/`. Both are added with `git add -f`.

## Controller additions
- **Cover** (`cover.html`): every `@@M..@@` is filled and grep finds no `@@` left.
  - With past papers: 5A, 5B, 5F and 5H read "1 mark · 5 min", 5C reads "3 marks · 5 min" and 5I reads "2 marks · 5 min".
  - With no past papers: 4J, 5D, 5E and 5G read "timed practice".
  - The Review row still reads "Mixed practice".
  - Format: I first used "N marks · 5 min · timed practice". On the cover, the 5C note and its title then wrapped onto two lines. So I used the controller's own format, "NN mark(s) · NN min". This also matches Part 2 (6I reads "2 marks · 5 min" and has its own timed-practice note). The 5A reviewer's suggestion, "1 mark · timed practice", is therefore not used word for word.
- **PAST_PAPERS_USED.md**:
  - I re-read the file right before editing. Parts 2 and 3 had already added their lines.
  - I appended: "Integration Part 1 (4J–5I) built 8 Nov. Past papers used: JRAHS23 Q4, NSB22 Q10, SydTech21 Q6, Abb23 Q10, EBHS24 Q12c(ii), NBHS22 Q10, SGS23 Q3, Ascham20 Q5, SBHS20 Q10 (4J, 5D, 5E and 5G none: timed practice from the textbook)."
  - I added "EBHS = Epping Boys" to the Key. "Next:" is unchanged.
  - Cross-check: none of these 9 items appears in the file or in any other `pp_selected_*.md`.

## Deferred minors
- **l5a.html:56 and :104**:
  - The semicircle/quadrant paragraph is now the tip box "Semicircles and quadrants" (l5a.html:58).
  - The grey/hatched parenthetical is now the tip box "Reading the pictures" (l5a.html:107).
- **Tip-box sweep (lesson files)**:
  - I extracted every concept, warn, take and formula box (117) and read them all.
  - I checked the suspect ones against the textbook text (PDF 202–206 rendered for 4J, 213–217 for 5A, and text search for 5B–5I).
  - **4J** was built before this rule existed, so it held a lot of pack prose. It now keeps the book's sentences only:
    - The "(Lessons 5A–5I of this pack)" aside is removed from the book sentence.
    - The derivative-of-a-constant lines are now the tip "Why the constant term makes no difference" (l4j.html:14).
    - The two proof notes are now the tip "Reading the proof" (l4j.html:24).
    - The "(see the worked example below)" pointer is removed.
    - The initial-condition box is restored to the book's lines, "7 = 4 + C. Thus C = 3 …". The pack-added line "7 = 2² + C" is dropped from the box; the worked example still shows it.
    - The check of ⅓x³+x+7 is now the tip "Checking a primitive" (l4j.html:73).
    - "A rule for finding primitives" and "Linear extension" now hold the book's text only. The divide-by-(n+1) derivations are now tips titled "Why the rule works" (l4j.html:110 and :176).
    - The pack-written boxes "Sums, multiples and constants", "Rewrite with indices first", "Watch the coefficient of x" (warn) and "Two primitives, two constants" are now tips.
  - **5A**: the pack summary "The calculation has four steps A–D" is now the tip "The four steps" (l5a.html:145).
  - **5B–5I**: the remaining box texts are the book's own. I confirmed the suspect phrases by text search: 5G Notes, 5H "Equal subintervals" and "Readers may like", 5I "Two notations", "Writing the integrand as a product" and "Adding the constant". Some cross-references were adapted ("Section 4J" became "Lesson 4J"); these had already been accepted in the reviews.
  - Per the ruling, answer files were not swept.
- **Hints**: I re-read all 9 past-paper hints (5A, 5B, 5C×3, 5F, 5H, 5I×2). Each is a starting question that names no rule, technique, step or value. The 4J Q15 hint is the textbook's own. No change was needed.
- **Clipped-label sweep**: `svg_overlap.py` reports 0 frame clips in all 187 int1 SVGs (there were 36 before). The "6E Q1 grid" item is a Part 2 figure, so it does not apply here.
- **svg_overlap.py**: it now reports 0 problems on all 187 int1 SVGs (there were 204 before). Details are in the next section.
- **l5g.html:265**: the timed-practice note again reads "each integration question in the catalogue for these papers" (as in l5e).
- **q5g_3b**: "y = x²" and "y = (x − 3)²" now have arrow leaders, as in the book. There is a new `leader()` helper in `figs_5g.py`. The frame is widened to 245 px so that the right-hand label fits.
- **a_5i.html**:
  - The "Textbook Homework" heading is kept with Q1 (a_5i.html:43), so it is no longer stranded at a page foot.
  - The stray "." after Q3 b ii is removed (it wrapped onto a line of its own).
  - In Q17c, ", so" is joined to the f(−x) chain, which now sits on one full-width line. The sketch column is enlarged from 2fr to 1fr 1fr.
  - Q17 may now break between its parts (a_5i.html:124), which removes a half-empty page.
- **5I Q8b alignment** (lesson p24 of the solo build): I inspected it at zoom 1.3. Its layout matches Q7 and Q9, so no change was made.

## Figure work (svg_overlap: 204 → 0)
- **New helper `workspace/build/int1/figfit.py`.** It is hooked into `figs.save`, `figs_4j.save_raw` and `figs_5d.combine`:
  - `fit()` grows the frame, moving the drawing right and down, only when the tool's label box would be clipped. A figure with no clipped label is returned unchanged.
  - `flatten()` and `shift()` put composite figures into true coordinates, so the tool checks them panel by panel. These are `a4j_q8` (it used translated `<g>` groups) and the `figs_5d.combine` pairs (they used nested `<svg>`).
  - `separate()` changes draw order only. It moves a tick or guide line that sits between two labels, and is not a fraction bar, so that the tool no longer reads "label, line, label" as one stacked fraction. This was the source of false "4/−4"-type problems. The page looks the same.
  - `untangle()` nudges a flagged single label by at most 8 px, to the nearest place where the figure has fewer problems. Stacked fractions are never moved.
  - `masked()` puts a white background behind a label. I used it only for the graph-paper unit labels (q5a_13, q5a_14) and for A(1, 2) over the curve families (a4j_q8).
- **Fixes in the figure code:**
  - 5D C1 sketches: the negative x ticks are above the axis, and −3/2 is right of the axis.
  - 5D Q8: π/2 is below the axis and 2π is beside its dashed line.
  - 5D Example 13: the B leaders start clear of the labels.
  - 5C Example 7: C is moved. Example 12: ±2 are inside the region.
  - 5C solutions (cos⁻¹): π and π/2 sit at the ends of their dashed guides.
  - 4J family: the 2 label is moved.
  - 5B: y = x⁻⁴ is one text element with a tspan exponent, so the index stays with its base.
  - Revision shapes: the circle is drawn as a path. The tool treats every `<circle>` as a dot, so the r label inside it was flagged.
  - 5A Q5d: there is room above 12 for the axis label.
- **Inspection**: I looked at every changed SVG at 1.5× (78 figures; 9 contact sheets, plus re-renders after each fix). The figure scripts regenerate identically: running all 10 `figs*.py` and diffing against the saved SVGs gives no difference.
- `a5h_q5` and `c5h_e32` changed in draw order only, through `separate()`. I verified this: their sorted element lists are identical.

## Layout fixes found by looking at every page
- **4J**: the tip boxes had added pages and left half-empty ones. To fix this:
  - "Primitives" is grouped with Box 15.
  - The work boxes are resized: concept 3 from 40 to 35, concept 6 from 52 to 42, concept 7 from 70 to 58.
  - 4J is now 21 pages (it was 23), and demo, your turn and worked example now sit together.
- **5A**: Worked example 1 may break between its parts (l5a.html:74). This removes a page that held only the Your turn box (old p40).
- **5G**: Exercise 5G Q1 is split into a–d and e–h, each with a 40 mm work box (l5g.html:186, class `q q-cont`). This removes a near-blank page that held only the "line by line" tip (old p203). `int1_5g.py` still passes: Q1 has 8 diagrams in order.
- **5H**: the first tutor demo and your turn have work boxes of 86 mm (they were 100 mm), so they share a page (old p217–218 each held one box and was about 50% blank).
- **Answers 5G**: the Q1–19 list spacing is 1.6 mm. This removes a 92%-blank page that held only Q19 (old p73).
- **Answers review**: Q9 may break between its lines. This removes a page that held only Q8 (old p98).
- **Remaining half-empty pages**: these are pages in 5B–5I that the lesson reviews approved. Nearly all of them are a demo or worked example that does not fit on the page before it, or a section end before a forced page break. I left them, because any change risks cramping the work boxes. The last answers page (99) holds review Q13–Q14 only.

## Verification (final flock build)
- Build command: `cd workspace/build && flock …/build.lock sh -c 'python3 build.py int1 all && mv lesson.pdf answers.pdf int1/'`. The scratch builds ran only in `…/scratchpad/work/int1-asm/b/`.
- Check scripts: `int1_4j` 1048 OK (it was 1052; the initial-condition box now holds one line fewer). `int1_5a`–`int1_5i` are ALL OK and `int1_rev` passes 355 checks. Every script has 0 failures.
- `qa.py`: lesson 264 pages, 0 problems; answers 99 pages, 0 problems.
- MathJax error scan (PyMuPDF text, the 7 house-rule strings): 0 in both PDFs.
- Font size: 11.3 pt spans are present in both PDFs (lesson 123,608 chars; answers 34,192), and so is box text at 9.8 pt. So neither PDF is shrunk.
- `svg_overlap.py workspace/build/int1/svg/*.svg`: 187 files, 0 problems.
- Pages inspected: every page of both PDFs, on 8-up contact sheets (34 lesson and 13 answer sheets). After the fixes I re-checked 4J, 5A, 5G, 5H, answers 5G, answers 5I and the review on fresh sheets. I zoomed in on the cover, lesson p14–15, p55–56, p183–184, p254 and answers p26–27, p45–46 and p85–94.

## Files changed
- Build files:
  - `workspace/build/int1/{cover,l4j,l5a,l5g,l5h,a_5g,a_5i}.html`
  - `figs.py`, `figs_4j.py`, `figs_5a.py`, `figs_5b.py`, `figs_5c.py`, `figs_5d.py`, `figs_5g.py`
  - new `figfit.py`
  - 78 SVGs
- `docs/PAST_PAPERS_USED.md` and the two output PDFs.
- I also committed two int1 report edits that were in the working tree but uncommitted (`task-int1-5g-report.md` gets its commit hash; `task-int1-5h-report.md` gets the fix-round-1 notes and a Box 18 slip). They came from the finished 5G and 5H agents and do not overlap with my work.

## Concerns
1. The cover notes use "N mark(s) · 5 min" rather than "1 mark · timed practice". The reason is the wrapping and Part 2 consistency described above. Each of these lessons still prints its own timed-practice note.
2. In 4J, the initial-condition concept box now matches the book ("7 = 4 + C"). The skipped line "7 = 2² + C" is shown in the worked example just below it.
3. `untangle()` moved some tick labels by up to 7 px (for example a, b, c, d in c5d_Ap, and 3 and 5 in p5c_st). I checked each one by eye: every label still sits beside its tick or line.
4. Some half-empty pages remain in lessons the reviews had approved (see the layout section above).

## Commit
- `Int1: assemble, record, final QA` on ch10-pack (not pushed). I staged only int1 files, `docs/PAST_PAPERS_USED.md` and the two output PDFs, each by explicit path.
