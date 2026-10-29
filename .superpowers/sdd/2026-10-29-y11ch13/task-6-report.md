# Task 6 report: Y11 Ch 13 Discrete Probability Distributions, assemble, record, final QA, deliver

Status: DONE_WITH_CONCERNS (minor layout only; see Concerns)
Commit: 593fb8d `Y11Ch13: assemble, record, final QA` on `ch10-pack`. Not pushed. 12 files, all mine, staged by explicit path.

## What was done

### Cover (`workspace/build/y11ch13/cover.html:8-11`)
Each `@@M13X@@` is filled. The wording is copied from each lesson's `.pp-intro` line, in the Ch 14 cover style:
- 13A: "Past papers: 6 marks · 10 min" (l13a.html:275)
- 13B: "Past papers: none · timed practice" (13B has no pp-intro; controller wording)
- 13C: "Past papers: 3 marks · 5 min" (l13c.html:242)
- 13D: "Past papers: 1 mark · 5 min" (l13d.html:343)

`grep -n '@@'` over cover, revision, l13*.html and a_*.html prints nothing (rc=1). The generated lesson.html is gitignored and is rebuilt each time.

### Controller text fix
- **13B timed-practice note** (`l13b.html:224`) now reads "do Questions 8, 9, 11 (after Question 2) and 12 above in 25 minutes." I checked that Q11 does refer to Q2: it says "The backers of the game in Question 2…".
- The y11ch13_13b.py check at line 125 matched the old phrase. I updated it to the new phrase, so it still checks the note. It now reports 141 OK.

### Record (`docs/PAST_PAPERS_USED.md`)
- **New paragraph**, placed after the Ch 10 paragraph and before the Y11 Ch 14 paragraph: "Y11 Ch 13 Discrete Probability Distributions (13A–13D) built 29 Oct. Past papers used: BHHS23 Q11c(i)/Q13c(ii), BHHS20 Q12a(i)(iii)(iv), Manly20 Q11a(iii), JRAHS20 Q1, HAHS23 Q8, BBHS24 Q2 (13B none: timed practice from the textbook)." All 8 items in `docs/pp_selected_y11ch13.md` are listed.
- **Key line:** added "Manly = Northern Beaches Secondary College Manly Selective Campus", the only new school.
- **"Next:"** not touched. It sits in the older Y12 "Ch 13 delivered 26 Oct" line, which I did not change.
- **Reuse check** (house rule 2), done again just before committing. I re-read `pp_selected_ch10/ch17/y11ch14/y11ch15.md` and PAST_PAPERS_USED.md, including the Ch 17 17C commits made during this task (c5556f1, ccbab56). There is no collision. Every match is a different part of the same question:
  - BHHS23 Q11(c)(ii) and Q13(c)(i) are in Ch 17.
  - BHHS20 Q12(a)(ii) is left free.
  - Manly20 Q11(a)(i)(ii) and Q2 are in Ch 17.
  - JRAHS20 Q6 and Q12(b) are in Ch 17.
  - HAHS23 Q13(c)(i) is in Ch 17.

### Glyph-collision scan
- I used the Ch 14 Task 8 tool (copied to scratch `bin/collide.py`) on both PDFs.
- I viewed every hit at zoom 2–3. Two were real near-collisions, where fraction rows were about to meet. Both are fixed:
  - **Lesson p89, Chapter 13 review Q5** (`l13d.html:372`). The two "\(\tfrac29\)" fractions on consecutive lines were 0.41 pt apart. The stem is now wrapped in `<span style="line-height:1.75">`. I tried 2.2 first, but the stem looked double-spaced.
  - **Answers p15, Ex 13C Q12** (`a_13c.html:91-94`). The "2" of \(\dfrac{n+1}{2}\) in part b almost touched the line of part c (1.0 pt). The answer is now wrapped in `<span style="line-height:2.3">`.
- On the final build neither hit remains. The other hits are false positives or not touching, at 1.05–1.6 pt:
  - lesson p33, the stacked axis fractions in the WE3 SVG;
  - box borders and hats: lesson p34/46/48/51/57/64/75/78/87;
  - answers p5, the tree-diagram labels;
  - answers p1 (warm-up Q1/Q4, 1.2–1.6 pt), p7, p16 and p21 (the \(\hat p\) hats).

### Page-straddle slivers (found during the page sweep)
- **Answers p2, p8, p12 and p18** each had a faint speck near the foot of the page. It is a copy of the numerator of an inline \(\tfrac{}{}\) on the first line of the next page. Chrome paints that line on both pages, and poppler and MuPDF show the copy at the foot of the earlier page.
- Each affected block is the first block on the next page: a "Tutor demo" C-entry (a_13a C3, a_13b C2, a_13c C3, a_13d C4). Each now has `style="padding-top:1.2mm"`. All four specks are gone and the page count is unchanged.
- The y11ch13_13d.py block regex required a bare `<div class="a">`. It now accepts an optional style attribute, exactly like the 13a/13b/13c scripts already did (`y11ch13_13d.py:346`).

### Layout (work-box sizing only)
Every page of both PDFs was viewed on 2x2 contact sheets at zoom 0.6, before and after the changes. The changed pages were also viewed at zoom 0.75–3. I measured content bottoms with PyMuPDF and enlarged boxes only where the next block could not move up and the change was easy:

| Page | Box | Change | Page now ends |
|---|---|---|---|
| lesson p17 | Ex 13A Q7 | 78→138 | 256 mm |
| lesson p25 | 13A PP2 | 40→64 | 265 mm, with PP3 |
| lesson p25 | 13A PP3 | 28→52 | 265 mm, with PP2 |
| lesson p26 | 13A PP4 (alone before Lesson 13B) | 70→170 | 240 mm |
| lesson p61 | Ex 13C Q13 (a two-part proof) | 100→170 | 249 mm |
| lesson p63 | 13C PP2 | 28→48 | 253 mm, with PP3 (accepted page, easy) |
| lesson p63 | 13C PP3 | 24→64 | 253 mm, with PP2 |
| lesson p79 | Ex 13D Q4 | 30→110 | 246 mm |
| lesson p89 | Review Q5 | 36→90 | box bottom about 259 mm (seen on render) |
| lesson p90 | Review Q6 | 30→120 | 248 mm |

Page counts are unchanged at 92 and 21.

Pages left as they are:
- The accepted pages 13B p36, 13C p45/p53 and 13D p74/p83/p84. In 13D the exercise boxes are 12 mm on purpose, because those questions are activities.
- Pages ending at 196–214 mm: p11, p19, p30, p34, p48, p54, p81, p92. The next block on each does not fit, and each is about 25% blank.

## Verification (final build)
- **Build:** the flock command as given: `cd /home/user/Hw/workspace/build && flock …/scratchpad/build.lock sh -c 'python3 build.py y11ch13 all && mv lesson.pdf answers.pdf y11ch13/'`
- **Check scripts:** all rc=0.

| Script | Result |
|---|---|
| y11ch13_rev.py | 97 printed values checked, 0 failures |
| y11ch13_13a.py | 192 checks, all OK |
| y11ch13_13b.py | 141 checks, all OK |
| y11ch13_13c.py | 173 checks, all OK |
| y11ch13_13d.py | 165 checks, 0 failed |

- **qa.py:** lesson.pdf 92 pages, 0 problems; answers.pdf 21 pages, 0 problems.
- **MathJax scan** on both PDFs (PyMuPDF get_text for Double subscripts / Double superscripts / Undefined control sequence / Missing / Extra } / Misplaced / Math input error): lesson 0, answers 0.
- **Placeholders:** no `@@` left.

## Delivered
- `/home/user/Hw/output/Year_12_Ext1_Y11_Ch13_Discrete_Probability_Distributions_Lesson_and_Homework.pdf`: 92 pages
- `/home/user/Hw/output/Year_12_Ext1_Y11_Ch13_Discrete_Probability_Distributions_Homework_Answers.pdf`: 21 pages

Both are byte-identical to the build (checked with cmp). PDFs are gitignored.

## Files changed
- docs/PAST_PAPERS_USED.md
- workspace/build/y11ch13/: cover.html, l13a.html, l13b.html, l13c.html, l13d.html, a_13a.html, a_13b.html, a_13c.html, a_13d.html
- workspace/checks/: y11ch13_13b.py (note phrase), y11ch13_13d.py (block regex)

## Concerns
1. **Two faint slivers remain in the lesson PDF.** They are the same Chrome page-straddle effect, at the foot of p67 (before the p68 display) and p90 (before review Q7's \(\text{E}(X^2)-\mu^2\)). They render as very light grey specks: minimum pixel 235 and 219 of 255 at 150 dpi. The Ch 10 and Ch 14 PDFs have one or two of the same. I left them because fixing a question block would mean changing the `class="q"` regex in the 13D check.
2. **Some boxes are now generous for their marks:** 13A PP4 is 170 mm (2 marks) and 13C PP3 is 64 mm (1 mark). They fill the last page before the next lesson, as in Ch 14. Shrink them if blank space is preferred.
3. **About 25% blank remains** on p11, p19, p30, p34, p81 and p92, and the accepted pages are unchanged.
