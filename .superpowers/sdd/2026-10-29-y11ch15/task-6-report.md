# Task 6 report: assemble, record, final QA, deliver (Y11 Ch 15)

Commit: `049fef0 Y11Ch15: assemble, record, final QA` on `ch10-pack` (not pushed). Staged by explicit path: `workspace/build/y11ch15/{cover,l15a,l15b,l15c,l15d}.html`, `docs/PAST_PAPERS_USED.md`. Nothing in `workspace/build/y11ch14/` was touched.

## Brief items

| Item | What I did |
|---|---|
| Fill `@@M15X@@` from each `.pp-intro` | cover.html:8-11 now reads `Past papers: 17 marks · 25 min` (15A), `16 marks · 25 min` (15B), `18 marks · 25 min` (15C), `16 marks · 25 min` (15D). Confirmed against the `.pp-intro` lines (l15a:226, l15b:151, l15c:178, l15d:184) and against the sum of the PP marks: 15A 1+1+1+1+3+2+3+2+3 = 17; 15B 1+1+1+2+2+2+2+2+3 = 16; 15C 1+1+2+3+2+3+3+3 = 18; 15D 2+2+2+2+2+3+3 = 16. The times are 1.5 × marks rounded to 5 min (25.5, 24, 27, 24 → 25). Same format as the Ch 10 cover. |
| PAST_PAPERS_USED paragraph | Appended after the Ch 10 paragraph in the file's style. New abbreviations Moriah and PLC added to Key. "Next:" line unchanged (diff below). |
| Build, checks, qa, MathJax | All pass (outputs below). |
| Contact sheets of every page | 80 lesson pages and 19 answer pages viewed at zoom 0.62, with zooms where needed (list below). |
| Copy to output | Done with the spec names (below). |
| Controller: 15A Q3 work box | Enlarged 46 → 64 mm. Q4 and Q5 on the same page rebalanced so nothing reflows (details below). |
| Controller: hint softenings | 15D PP2, PP6 and PP7 softened. While re-checking every hint against house rule 4 I also softened 15B PP6 and 15C PP6, which pointed at near-identical worked examples (same reason as 15D PP2/PP6). |
| Controller: 15D review Q7 box | Enlarged 35 → 55 mm (page 78 had 36 mm slack, now 17 mm). Answers p17 is mostly empty, as you said is acceptable. |
| Controller: MathJax scan | Run on both PDFs: 0 hits. |

## Changes (file:line, old → new)

Layout:
- `l15a.html:189` (Ex 15A Q3) `{{work:46}}` → `{{work:64}}` (rendered box about 57 mm, room for the two column expansions side by side or stacked).
- `l15a.html:191` (Ex 15A Q4) `{{work:62}}` → `{{work:56}}` (8 one-line term answers; still about 50 mm rendered).
- `l15a.html:192` (Ex 15A Q5) `{{work:50}}` → `{{work:40}}` (two one-line expansions and two sums).
  Page 14 had only 4 mm slack. Without the Q4/Q5 trims, Q5 would move to p15 and push every page of the 15A homework down (each of p15-p19 has only 3-13 mm slack), adding a page. Page 14 now has 2.5 mm slack, nothing reflows, and the page count stays 80.
- `l15d.html:239` (Chapter review Q7) `{{work:35}}` → `{{work:55}}`.
- `l15d.html:165` (Ex 15D Q9 b(i), second bullet) `\(1,2,\dots,k-1\).` → `<span style="white-space:nowrap">\(1,2,\dots,k-1\).</span>`. Defect found on p69: the full stop wrapped onto a line of its own. It now stays with its maths, using the nowrap pattern from Ch 10 (l10a.html:81).

Hints (lesson only; question wording, maths and labels unchanged):
- `l15d.html:193` PP2 (SBHS 2020 Q14(c)(i)): "compare the Concept 2 worked example." → "where could the number in front of each \({}^nC_r\) on the right come from?"
- `l15d.html:213` PP6 (KWS 2023 Q14(d)): "compare the Concept 3 worked example, part b." → "write \((1+x)^3(1+x)^6\) as a single power of \((1+x)\)."
- `l15d.html:220` PP7 (NSB 2023 Q14(c)): "what does the given identity \((1+x)^{n+1}=(1+x)^n(1+x)\) say about each bracket \(a_{k-1}+a_k\)?" (this gave the key step) → "start by writing each \(a_k\) and each \(b_k\) as a binomial coefficient."
- `l15b.html:178` PP6 (Ascham 2023 Q12(b), \((2+x^2)(3-2x)^5\)): "compare Worked example 8." (WE8 is \((5+x)(2-3x)^7\), near-identical) → "which products of terms give \(x^2\)?" (same wording as the 15A PP5 and 15B PP8 hints).
- `l15c.html:206` PP6 (NSB 2020 Q11(b), \((x^2-1/x^2)^{10}\)): "compare the Concept 3 worked example." (that example reduces to \((x^2-x^{-2})^{20}\), essentially the same question) → "write \(\dfrac{1}{x^2}\) as a power of \(x\)." (matches the 15C PP2 hint style).

Hints re-checked and kept: the "take out a factor so that the bracket starts with 1" hints (15A); "compare Worked example 4" (15A PP4: WE4 is a ratio question, PP4 is equal coefficients); "compare Worked example 3"/"7"/"8"/"9(c)"/"9(d)", "Concept 3 tutor demo", "Exercise 15C Question 14" (each points to a method and the target is a different problem or an unsolved exercise); 15D PP1 "start from the binomial expansion", PP3 "which terms cancel", PP4 "rows are reversible", PP5 "sort the committees by the number of males". All of these are starting ideas. PP4 and PP5 name the property or case split to start from, but no step of the working. They are borderline but within rule 4, so I left them.

## Verification outputs (final build)

Build: `cd workspace/build && python3 build.py y11ch15 all && mv lesson.pdf answers.pdf y11ch15/` → wrote lesson.pdf, answers.pdf. The PDF titles and footers were checked as Chapter 15, so the moved files were mine and not Ch 14's.

Checks (each run after the final edit, exit codes from the scripts themselves):
```
y11ch15_rev.py  exit=0  85 printed values checked, 0 failures
y11ch15_15a.py  exit=0  All OK   (158 OK lines)
y11ch15_15b.py  exit=0  All OK   (161 OK lines)
y11ch15_15c.py  exit=0  All OK   (170 OK lines)
y11ch15_15d.py  exit=0  All OK   (285 OK lines)
```
Two lines contain the string "fail", and neither is a failure: `85 printed values checked, 0 failures` and `OK Q12d as printed fails at n = 1 (so it is left out)`.

qa:
```
y11ch15/lesson.pdf 80 pages, 0 problems
y11ch15/answers.pdf 19 pages, 0 problems
```
MathJax error-string scan (PyMuPDF get_text; "Double subscripts", "Double superscripts", "Undefined control sequence", "Missing", "Extra }", "Misplaced", "Math input error"):
```
y11ch15/lesson.pdf: 80 pages, MathJax error hits = 0
y11ch15/answers.pdf: 19 pages, MathJax error hits = 0
```
Extra scan for stray punctuation (a punctuation-only text line with no text or vector maths just to its left): lesson 0 after the fix (p69 was the only hit before it). Answers 1 hit, p15 Q7(c), a false positive: the comma sits between two displayed fractions on the same line. Checked at zoom 1.8.

`@@`: `grep -rn --include='*.html' --include='*.json' --include='*.py' '@@' workspace/build/y11ch15/` prints nothing (exit 1). The PDF text of both PDFs has 0 occurrences. A bare `grep -rn '@@'` only reports "binary file matches" for the two PDFs (compressed stream bytes, not text).

## Pages inspected

The contact sheets (`sheet.py … 0.62`) of the final build cover all 80 lesson pages and all 19 answer pages. I viewed each one. Pages 1-22 were viewed from the final render. Pages 23-80 and A1-A19 were viewed from the build before the last edit. That edit (the p69 nowrap span) only changed p69, which I viewed again from the final render along with its sheet. Zoomed views: p14 at zoom 1 (Q3/Q4/Q5 boxes), p69 at zoom 1.6 (stranded full stop, before and after the fix), p73 and p75 at zoom 1.4 (new 15D hints), answers p15 at zoom 1.8 (scan hit).
- Defects fixed: p14 Q3 box too small (enlarged); p69 stranded full stop (fixed); p78 review Q7 box small (enlarged).
- No clipped or overflowing maths, figure overlaps or stranded headings found. Every PP source label and hint is present in the lesson, and every PP source label is present in the answers.
- Noted and left alone: p11 (15A Concept 5 Your-turn page) and p62/p64/p72 end with some white space, because the next block starts a new section or page-break. Answers p17 is mostly empty (accepted by the controller). p20 (Ex 15A Q19, Pascal pyramid) has one large box, which is appropriate.

## PAST_PAPERS_USED diff
```
 Ch 10 (9E + 10A + 10B, Related Rates and Projectile Motion) built 27 Oct. Past papers used: ...
+Y11 Ch 15 Binomial theorem (15A–15D) built 29 Oct. Past papers used: Kings21 Q2, Ascham20 Q8, NSB20 Q2/Q11b/Q14a, Girraween21 Q2, Moriah23 Q9d(i)(ii), SGS23 Q13a, Girraween23 Q16a, Abb21 Q12c, NBHS22 Q11b, SGS21 Q2, HAHS21 Q2, HAHS23 Q9, SGHS23 Q11c, Knox23 Q11a, Ascham23 Q12b, PLC23 Q13a/Q14b, StAlo24 Q14c, JRAHS23 Q15b, SGS20 Q2, SGS22 Q7, Abb23 Q11c, NSG23 Q12b(i)(ii), NSG20 Q11e, HGHS23 Q11d, NBHS21 Q11d, SBHS20 Q14c(i), Killara21 Q13e, BBHS24 Q12d, KWS23 Q14d, NSB23 Q14c.

-Key: ... Knox = Knox Grammar, SGHS = Sydney Girls.
+Key: ... Knox = Knox Grammar, SGHS = Sydney Girls, Moriah = Moriah College, PLC = Pymble Ladies' College.
```
All 33 selected items are listed (15A 9, 15B 9, 15C 8, 15D 7). Before committing I re-read `PAST_PAPERS_USED.md` and every `docs/pp_selected_*.md` (ch10, y11ch13, y11ch14). None of them uses the same school, year and question as this pack. PLC23 Q14a (Ch 13), Moriah23 Q3/Q10(b)(ii) (Ch 14), NSB20, SBHS20 Q11a/Q12c, NBHS22 Q11a(i) and NBHS21 Q11e(i) are all different questions.

## Output
- `/home/user/Hw/output/Year_12_Ext1_Y11_Ch15_Binomial_Theorem_Lesson_and_Homework.pdf`: 3,508,277 bytes, 80 pages, title "Year 12 Ext 1 Year 11 Chapter 15 The Binomial Theorem - Lesson and Homework"
- `/home/user/Hw/output/Year_12_Ext1_Y11_Ch15_Binomial_Theorem_Homework_Answers.pdf`: 2,209,376 bytes, 19 pages, title "... - Homework Answers"
Both are byte-identical (cmp) to `workspace/build/y11ch15/lesson.pdf` and `answers.pdf`. PDFs are gitignored, so they are not committed.

## Concerns
- I softened two hints beyond the three the brief named: 15B PP6 and 15C PP6. Both pointed at near-identical worked examples, the same reason the controller gave for 15D PP2 and PP6. Revert them if you prefer the brief's list only.
- To keep page 14 from reflowing, the 15A Q4 box is now 56 mm and the Q5 box 40 mm (were 62 and 50). They are adequate for the working, but less generous.
- 15D PP4 ("the rows of Pascal's triangle are reversible") and PP5 ("sort the committees by the number of males") name the property or case split to start from. I judged them to be starting ideas and kept them.
- `build.py` writes `lesson.pdf`/`answers.pdf` into the shared `workspace/build/` directory, so a parallel Ch 14 build could collide. I checked the title and footer of each moved PDF, and both were Chapter 15.
