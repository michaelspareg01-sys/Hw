# Final whole-pack review: Y11 Ext 1 Ch 14 Combinatorics (14A–14F + review)

Reviewed at commit 7f0360b. The output PDFs are byte-identical to `workspace/build/y11ch14/lesson.pdf` and `answers.pdf` (126 pp and 38 pp).

**Verdict: Needs fixes.** There are 0 Critical and 2 Important issues. Both Important issues are small layout fixes in the answers PDF, where wrapped inline fractions collide. Everything else passes. The maths in every answer I sampled is correct.

### Spec Compliance
- ✅ **Structure.** The pack runs cover → revision + warm-up → 14A–14F → review (at the end of `l14f.html`), as the spec requires.
  - 14G and 14H are absent. The only "circle" items are selections of points: 14E C5, WE20, Ex 14E Q18.
  - The review omits Q15–Q17, as recorded.
- ✅ **Names.** Output file names, the pack.json footers and the answers heading match the spec. The heading fits on one line.
- ✅ **Cover rows (check 1).** Every cover row matches its lesson's `.pp-intro` line and the sum of the item marks. The times follow the 1.5 × marks rule, rounded to 5 min:

  | Lesson | Marks | Minutes | 1.5 × marks |
  |---|---|---|---|
  | 14A | 9 | 15 | 13.5 |
  | 14B | 13 | 20 | 19.5 |
  | 14C | 12 | 20 | 18 |
  | 14D | 16 | 25 | 24 |
  | 14E | 20 | 30 | 30 |
  | 14F | 15 | 25 | 22.5 |

  The sub-marks of multi-part items add up to their header marks: 14B PP8, 14C PP8, 14D PP7, 14E PP5/8/9, 14F PP6/7.
- ✅ **Lesson/answer pairing (check 2).** All 52 past-paper items in the lesson have a worked solution in the answers PDF. The PP numbers, order and source labels are character-identical in both files (6+8+8+12+11+7).
- ✅ **No reuse (check 3).**
  - No question appears twice in the pack. Ascham 2023 Q12(e)(i)/(ii)/(iii) are separate independent parts across 14A/14C/14B.
  - Every item was cross-checked against every other line of `docs/PAST_PAPERS_USED.md` (Ch 10, 11, 12, 13, 15) and against `pp_selected_ch10.md`, `_y11ch13.md` (working copy) and `_y11ch15.md`. There are no collisions. Same-paper neighbours are always different questions or parts, for example NSG20 Q13(c) vs Ch 10's Q13(d), and SGHS23 Q11(e) vs Q11(c)/Q11(d).
- ✅ **Ch 14 record (check 4).** The Ch 14 paragraph in PAST_PAPERS_USED.md lists exactly the 52 items in `pp_selected_y11ch14.md`, with matching subpart notation. SydTech and SGGHS were added to the key.
- ✅ **Numbering and cross-references (check 5).**
  - Boxes 1–13 and Worked examples 1–23 are consecutive and match the textbook.
  - Concept counts per lesson (3/4/3/3/5/3) match the C1… entries in the answers.
  - Every "Lesson 14x", "Box n", "Concept n" and "Question 18 of Exercise 14D" reference points to the right place.
  - Textbook answer numbers follow the lesson order. 14A Q11 is a show-that and is correctly omitted. 14E Q6 and 14B Q22b are omitted by ruling.
  - Answer sections follow the lesson order, with one exception: the review answers come before the 14F past-paper solutions (Minor 1).
- ✅ **Consistency (check 6).**
  - Band macros are the same in all lessons; textbook bands checked on the rendered pages.
  - Labels follow the cover word order, including NBHS and STHS, and "(i)(ii)" is used pack-wide.
  - Each PP item has exactly one hint.
  - Hints mostly give a starting idea (Minor 2).
- ⚠️ **Accepted gaps.** The accepted layout gaps (revision p2, 14A p9, 14E p84/p86) were seen and not re-raised.

### Strengths
- **Answers are correct.** Every one of about 150 answers I re-solved by hand or brute force is correct, and every one matches the textbook answer pages.
- **Figures match their questions:**
  - 14D PP10 (5×3 grid) and PP11 (5×3 and 4×2 grids joined at a corner, which gives 840). PP11 was compared with the St Aloysius original.
  - 14E PP7 (9 points, 4 collinear).
  - 14E PP11 (tiles: overlaps at columns 1 and 4). Compared with the Abbotsleigh 2024 original.
  - 14E Q25 (4 wide × 6 high, five crosses on the anti-diagonal through C).
  - The 14D concept grids (4×2 and 3×3).
- **Quiet fix of a key misprint.** The textbook key labels the 14A Q10 answer as "11". The pack numbers it correctly as 10, with nothing printed about the change.

### Issues

#### Critical
None.

#### Important
1. **Answers PDF p33: 14F Ex Q5, part j collides with part a.** `a_14f.html:35`. The row wraps, and the numerator "64" of j, \(\tfrac{64}{425}\), sits on the denominator "22 100" of part a, \(\tfrac{1}{22\,100}\). PyMuPDF glyph boxes show a vertical gap of 0.1–0.3 pt, so the two visibly touch. Fix: put a `<br>` before the j span, or start a second line at part f.
2. **Answers PDF p1: warm-up Q3 collision.** `a_rev.html:4`. The "30" in \(P=\tfrac{4}{30}\) on one line overlaps the "12 + 8" in \(P=\tfrac{12+8}{30}\) on the next. The gap is −0.4 pt, so the glyphs actually overlap. Q2 on the same page is tight between "13" and "26+4−2" but does not collide. Fix: a `<br>` before part **b** of Q3, or show the part-b fraction as a display.

These are the only two collisions my glyph-stacking scan found across all 164 pages. The scan flagged glyphs from stacked lines that overlap horizontally with less than 1.6 pt vertical gap. The only other hit was lesson p9, inside an aligned display, and it is not a collision.

#### Minor
1. **Answer order.** The order in `a_14f.html` is 14F Lesson Examples → Textbook Homework → Chapter 14 Review → 14F Past-Paper solutions. The lesson PDF and the house rule ("…per lesson…; then the review answers") put the review after the 14F past papers. The Ch 15 pack does the same, so this is a consistent precedent, but the order differs from the lesson. A related detail: `a_14f.html:64` wraps the `{{ahead}}` heading inside an `ans-sec` div. It renders correctly (p34).
2. **Hint style.**
   - 14A PP2's hint ("put P in the first place and S in the last place. How many letters are left…") is the whole 1-mark solution.
   - 14A PP1 and PP3 also state the method rather than a starting idea.
   - The hints from 14B to 14F are uniformly short starting ideas.
3. **Unnumbered example.** 14A Concept 1 has one unnumbered "Worked example: From the text: keep for homework" (the queue and \(y^{(5)}\) example from the teaching text). Every other example is "Worked example n: Keep for homework". This is accurate, because the item is not a numbered textbook example, but it is the one style outlier.
4. **Notation.** 14B PP7 (Killara 2024) uses italic \({}^nP_r\). The rest of the pack uses roman \(\mathrm{P}\) and \(\mathrm{C}\). This is probably faithful to the paper; harmless.

### Checks run
1. **Check scripts.** `workspace/checks/y11ch14_{rev,14a,14b,14c,14d,14e,14f}.py` all exit 0: 57 / 180 / 218 / 205 / 239 / 298 / 376 OK. Each reads `a_*.html` and `l*.html` templates and recomputes independently. 14f also covers the review answers.
2. **QA.** `qa.py`: lesson 126 pages, 0 problems; answers 38 pages, 0 problems.
3. **MathJax and raw-text scan.**
   - MathJax error strings (Double subscripts / Double superscripts / Undefined control sequence / Missing / Extra } / Misplaced / Math input error): 0 in both PDFs.
   - Raw TeX, `{{` and `@@` scan: 0 hits. The one "undefined" match is the intended "(ratio undefined)" in 14E Q29, which matches the textbook.
4. **Cover vs pp-intro vs item marks.** Parsed for all six lessons, plus the 1.5× rule.
5. **Lesson/answer PP pairing.** Scripted comparison of PP numbers and labels; all identical.
6. **Reuse sweep.** Manual comparison against every line of PAST_PAPERS_USED.md and all four pp_selected files. Item-by-item reconciliation of the Ch 14 paragraph with pp_selected_y11ch14.md (52 = 52).
7. **Cross-references.** Grep of every Box / Concept / Worked example / Lesson / Question reference. Concept counts vs C-entries. Textbook question numbers vs answer numbers, per lesson and for the review.
8. **Hint audit.** All 52 hints listed. Exactly one hint per PP block.
9. **Answer sample.** About 150 values in total, covering every lesson, the warm-up and the review:
   - Textbook answer pages PDF 938–943 rendered in halves at zoom 2. Every Exercise 14A–14F and review answer printed in the pack was compared with them. All match, apart from the key's own "11" label for 14A Q10.
   - Re-solved by brute force with `itertools`/`math.comb`:
     - Ex 14B Q21, Q25
     - Ex 14C Q17, Q21
     - Ex 14D Q16, Q18
     - Ex 14E Q7, Q12, Q15, Q18–Q21, Q23, Q26, Q27
     - Ex 14F Q20b, Q24a, Q25
     - 29 past-paper answers: 14A PP5; 14B PP1/3/4/5/8; 14C PP4/5/6/7/8; 14D PP7/8/9/12; 14E PP2/3/6/8/9/10/11; 14F PP1–PP7.
   - By hand: Ex 14A Q10, Q13, Q14; Ex 14C Q11, Q14, Q15, Q16, Q22; Ex 14D Q1i, Q10, Q17; Ex 14E Q29; Ex 14F Q5–Q19, Q21–Q27; review Q1–Q14; all lesson-example answers in 14C C3, 14D C1–C3, 14E C1–C5 and 14F C1–C3. All correct.
10. **Contact sheets.** Every page of both PDFs on 2×2 sheets at zoom 0.62 (42 sheets). Zoomed renders of answers p1, p2, p32, p33 and p34, and of lesson p9, p73, p93, p94 and p103.
11. **Glyph-collision scan.** Scripted PyMuPDF scan of vertically stacked glyph boxes on all 164 pages.
12. **Source figures.** The St Aloysius 2024 Q8 and Abbotsleigh 2024 Q12(c) original pages were rendered and compared with the recreated figures and wording.

### Assessment
**Task quality:** Needs fixes

**Reasoning:** The pack is complete, correct, consistent and properly recorded. The only blockers are two wrapped-fraction collisions in the answers PDF (p1 warm-up Q3 and p33 14F Q5j). Each needs a one-line `<br>`, a rebuild and a re-check of those two pages.
