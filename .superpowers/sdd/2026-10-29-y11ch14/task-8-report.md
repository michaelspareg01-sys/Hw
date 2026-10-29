# Task 8 report: Y11 Ch 14 Combinatorics, assemble, record, final QA, deliver

Status: DONE_WITH_CONCERNS (layout trade-offs only; see Concerns)
Commit: 7f0360b `Y11Ch14: assemble, record, final QA` on `ch10-pack` (not pushed). 18 files, only my own, staged by explicit path.

## What was done

### Cover (`workspace/build/y11ch14/cover.html:8-13`)
Each `@@M14X@@` is now filled from its lesson's `.pp-intro` line: 14A 9 marks · 15 min, 14B 13 · 20, 14C 12 · 20, 14D 16 · 25, 14E 20 · 30, 14F 15 · 25. Running `grep -n '@@' workspace/build/y11ch14/*.html` prints nothing (rc=1).

### Required text fixes from the controller
- **BBHS 2023 Q12(c) sentence** (`a_14c.html:73`): now reads "so each count of selections of all four batteries (including the total) is 4 times the unordered count, and the 4 cancels." y11ch14_14c.py re-run: 205 OK.
- **Ex 14D Q19(c)** (`l14d.html:161`): "part B" is now "part **b**". I used bold `<b>b</b>` to match "part **f**" in part g of the same question. The TB19 template in y11ch14_14d.py is updated to match.
- **Hints softened** so each gives a starting idea, not a step:
  - 14B PP5 (Girraween 2020 Q14(c)): "think about how many digits such a number could have."
  - 14D PP6 (BHHS 2020 Q8): "think of the Es as one item."
  - 14D PP11 (St Aloysius 2024 Q8): "where do the two grids meet?" I checked this against the figure: two grids joined at C.
  - 14F PP6 (NBHS 2022 Q11(c)): "each committee of seven is equally likely to be chosen."
  - 14F PP7 (Girraween 2023 Q11(c)): "think about where the four friends can end up." It no longer states 40C20 or any step of the answer.
- **14F PP6(i)** (`a_14f.html:109`): the full stop is removed from the display (`=77\,520\]`). The y11ch14_14f.py template on line 1191 is updated to match. No 14F check reads hint text; the scripts only count hints (one per item).

### Labels (both PDFs; lesson and answers labels stay identical)
- **NBHS, all 7 labels in 14A, 14B, 14D and 14E**: now in the cover word order "Normanhurst Boys High School, YYYY, Mathematics Extension 1, Year 12 Course Assessment Task 4 (Trial Examination), Q…", the same as 14F. I rendered the covers of NBHS 2020, 2021, 2022 and 2023: all four print "MATHEMATICS EXTENSION 1" and then "YYYY Year 12 Course Assessment Task 4 (Trial Examination)".
- **STHS**: both covers print "Extension 1 Mathematics" and then "TRIAL HSC". 14E PP6 (2021) is now "…, Extension 1 Mathematics, Trial HSC, Q11(e)". I gave 14D PP3 (STHS 2023) the same fix under the same cover-order ruling; the brief named only STHS 2021.
- **Subpart style**: "(i)(ii)" is added to every label whose subparts are all used, matching 14E PP9 and 14F PP6/PP7. Affected: 14B PP8 (NSG 2020 Q13(c)), 14C PP8 (BBHS 2023 Q12(c)), 14D PP7 (SGGHS 2020 Q11(c)), 14E PP5 (SBHS 2020 Q12(d)) and 14E PP8 (SGHS 2023 Q11(e)). Items that use only one part already name it (for example Moriah 2023 Q10(b)(ii)).
- **Check scripts**: the label regexes in y11ch14_14d.py:739 and y11ch14_14e.py:1040 required "Extension&nbsp;1( Mathematics)?,&nbsp;Q", which rejected the corrected order. They now use the 14F form: labels match in both files, contain "Extension&nbsp;1", and end ",&nbsp;Q<digit>".

### Deferred layout minors (layout only, all by `{{work:NN}}` sizing or one page break)
- **Revision**: ♦ and ♥ are now red (`color:var(--rose)`, `revision.html:10`). p4 was about 40% empty; warm-up Q3/Q4/Q5 working is now 48/56/60 and the page ends at 278 mm. **p2 still has about a 40 mm gap.** The next summary box (multi-stage, 76 mm) cannot fit there, and closing the gap would mean splitting a box.
- **14A p9**: left as is (77 mm free). The C3 tutor demo is 86 mm. Moving it up would need its working cut to about 24 mm, and the gap would simply move to p10.
- **14B**:
  - p21: tutor demo and Your turn working 34→48 and 30→44; the page is now full.
  - p22: the C2 tutor demo working went 30→26 so the demo moves up onto p22 (now full).
  - p23: C2 Your turn working 28→68 (page ends 255 mm).
  - p27: C4 tutor demo working 46→94 (ends 234 mm).
  - p28: Your turn working 40→82 (ends 266 mm).
  - p38: PP8 working 80→170 (ends about 238 mm).
- **14E**:
  - A `page-break` before Concept 4 (`l14e.html:162`) removes the stray rounded-box sliver at the foot of p82. Concept 4 starts on p83 as before.
  - C5 tutor demo working 26→68 and Your turn 120→68: balanced, and both now sit together on p85.
  - **Trade-off:** p84 now ends after the C5 concept box (191 mm, about 90 mm free), and Worked example 20 stays alone on p86 (173 mm block). WE20 cannot share a page unless a block of 85 mm or less joins it, which means a demo with about 26 mm of working (the original complaint). I chose the controller's balanced sizes.
- **Other half-empty pages found in the full sweep, and fixed**:
  - 14D: p61 Ex Q3 working 24→56; p62 Ex Q6 26→78; p70 PP5 30→68; p74 PP12 (alone before Lesson 14E) 60→130.
  - 14E: p91 Ex Q17 30→54; p96 Ex Q29 (was alone, 50% blank) 70→196; p101 PP8 50→82; p103 PP11 (alone before Lesson 14F) 56→170.

### Record (`docs/PAST_PAPERS_USED.md`)
- Added the paragraph "Y11 Ch 14 Combinatorics (14A–14F) built 29 Oct. Past papers used: …", listing all 52 items from `docs/pp_selected_y11ch14.md`. It sits after the Ch 10 paragraph and before the Ch 15 one.
- Key line gains "SydTech = Sydney Technical, SGGHS = St George Girls". SydTech is the abbreviation the Ch 13 line already uses.
- "Next:" line not touched.

### Reuse check (house rule 2)
Before committing I re-read `pp_selected_ch10.md`, `_y11ch13.md` and `_y11ch15.md`, plus PAST_PAPERS_USED.md. No collision: every match is a different question or part of the same paper (for example BHHS 2020 Q12(a) in Ch 13 vs our Q8; NBHS 2021 Q11(d) in Ch 15 vs our Q3/Q11(e)(i)).

## Verification (final build)
- Build command as given: `cd /home/user/Hw/workspace/build && flock …/scratchpad/build.lock sh -c 'python3 build.py y11ch14 all && mv lesson.pdf answers.pdf y11ch14/'`
- Check scripts, all rc=0:

| Script | Result |
|---|---|
| y11ch14_rev.py | 57 values, 0 failures |
| y11ch14_14a.py | 180 OK |
| y11ch14_14b.py | 218 OK |
| y11ch14_14c.py | 205 OK |
| y11ch14_14d.py | 239 OK |
| y11ch14_14e.py | 298 OK |
| y11ch14_14f.py | 376 OK |

- qa.py: lesson.pdf 126 pages, 0 problems; answers.pdf 38 pages, 0 problems.
- MathJax scan (PyMuPDF get_text for Double subscripts / Double superscripts / Undefined control sequence / Missing / Extra } / Misplaced / Math input error): lesson 0, answers 0.
- Pages inspected: every page of both PDFs on 2x2 contact sheets at zoom 0.6 (same rendering as sheet.py, 4-up). Close renders of p27 and of the 14E pages 81–86, plus a final sheet of the last-changed pages (70, 74, 91, 96, 101, 103). Every changed page was measured with PyMuPDF rectangles. No clipped maths, no overlaps, no stranded headings. Page counts are unchanged at 126 and 38.

## Delivered
- `/home/user/Hw/output/Year_12_Ext1_Y11_Ch14_Combinatorics_Lesson_and_Homework.pdf`: 126 pages
- `/home/user/Hw/output/Year_12_Ext1_Y11_Ch14_Combinatorics_Homework_Answers.pdf`: 38 pages

PDFs are gitignored, as for earlier chapters.

## Files changed
- docs/PAST_PAPERS_USED.md
- workspace/build/y11ch14/: cover.html, revision.html, l14a–l14f.html, a_14a–a_14f.html
- workspace/checks/: y11ch14_14d.py, y11ch14_14e.py, y11ch14_14f.py

## Concerns
1. Two layout gaps remain by necessity:
   - revision p2, about 40 mm (the next box is 76 mm);
   - 14A p9, about 77 mm (the next demo is 86 mm).
2. The 14E C5 rebalance leaves p84 about a third blank, and WE20 stays alone on p86. This is the cost of giving the C5 demo 68 mm instead of 26 mm.
3. Some working boxes are now generous for their marks: 14B PP8 170 mm (3 marks), 14D PP12 130 mm (1 mark), 14E PP11 170 mm (2 marks). They fill the last page before a new lesson; shrink them if blank space is preferred.
4. Done beyond the letter of the brief, under the same rulings:
   - STHS 2023 label order (14D PP3);
   - "(i)(ii)" added pack-wide, not only in 14E;
   - suit glyphs in 14F (♡♠♣) left in their textbook form, uncoloured.

---

# Fix round 1: final whole-pack review (`final-review.md`)

Commit: 0310834 `Y11Ch14: final review fixes` (6 files, my own, staged by explicit path; not pushed).

## Changes

### 1. Important: answers p33, 14F Ex Q5 (`a_14f.html:35`)
- Parts f–j now sit on a second row: `<span style="display:block;margin-top:2mm">`.
- The whole answer is wrapped in a line-height 2.6 span.
- At zoom 2.2 the two fraction rows are now clearly apart. Before, the "64" of j touched the "22 100" of a.

### 2. Important: answers p1, warm-up Q3 (`a_rev.html:4`)
- A `<br>` now comes before part **b**, and the answer is wrapped in a line-height 2.6 span. The "30" no longer meets the "12 + 8".
- I gave Q2 on the same page (`a_rev.html:3`, the "13" over "26 + 4 − 2", 1.0 pt gap) the same span, since it was the next-tightest pair.
- Both check templates still match: rev 57 values OK, 14f 376 OK.

### 3. 14A hints (`l14a.html:178,183,188`): now starting ideas only
- PP1: "does the order of the digits in a PIN matter?"
- PP2: "which places in the arrangement are already decided?"
- PP3: "how are \((n+1)!\) and \((n+2)!\) related?"
- PP4's "the same method as PP 3. Which factorial is the larger one?" still reads correctly.

### 4. 14B PP7 notation
`{}^{n}P_{r}` is now `{}^{n}\mathrm{P}_{r}` in the PP7 block of l14b.html (question and hint, 4 places) and of a_14b.html (solution, 8 places). The 14b check's evaluator already handles both forms: 218 OK.

### 5. Answer order (`a_14f.html`)
- The Chapter 14 Review block moved, unchanged, to the end of the file. The order is now: 14F Lesson Examples → Textbook Homework → ahead line + Past-Paper solutions → Chapter 14 Review. This matches the lesson PDF.
- The move was clean: one cut and paste.
- In y11ch14_14f.py I updated the section split:
  - `A = TB..HEAD`;
  - `RA` = everything after `RVSEC`;
  - `ppsec` = `PPSEC..RVSEC`;
  - the heading-order assertion is now TB < PP < Review.

### 6. Unnumbered "From the text" worked example in 14A
Left as is, as instructed.

## Verification
- Rebuilt with the flock command.
- Check scripts all rc=0:

| Script | Result |
|---|---|
| y11ch14_rev.py | 57 values, 0 failures |
| y11ch14_14a.py | 180 OK |
| y11ch14_14b.py | 218 OK |
| y11ch14_14c.py | 205 OK |
| y11ch14_14d.py | 239 OK |
| y11ch14_14e.py | 298 OK |
| y11ch14_14f.py | 376 OK |

- qa.py: 0 problems in each PDF.
- MathJax scan: 0 and 0.
- No `@@` placeholders. Page counts unchanged: 126 and 38.
- **Glyph-collision scan** (new tool: scratch `bin/collide.py`).
  - It takes text-char bboxes plus the small filled vector glyph paths (MathJax draws math as `fs` paths). It flags pairs that overlap in x and are stacked with a vertical gap between −0.8 and 1.6 pt.
  - Validation on the previous (pre-fix) output PDFs: it caught answers p1 (−0.35 pt) and p33 (0.12–0.28 pt).
  - On the new build neither hit remains.
  - Remaining hits (all present in both builds; I viewed each at zoom 3) are false positives:
    - answers p34: 14F Ex Q22(f) "32 487" over "4^5 ways", 1.3 pt, not touching;
    - answers p35: "^{14}C_3" prescript over text;
    - lesson p7: box border;
    - lesson p86: WE20 figure labels A10/A1;
    - lesson p104: box borders.
- Pages viewed:
  - answers p1, p33 (zoom 2.2), p29–38 (review now on p37–38 after the 14F past-paper solutions), p10 (PP7 upright P);
  - lesson p18 (14A PP1–3 hints), p37 (14B PP7 hint).
- Re-copied both PDFs to `/home/user/Hw/output/` (byte-identical to the build: 126 and 38 pages).

## Concerns
None new.
