# Task Int1 lesson 5G report: Areas of compound regions

Status: DONE_WITH_CONCERNS. The only concern is the expected past-paper shortfall: the catalogue has no int1-L8 row, so the section ends with a timed-practice note only (house rule 8). (Work resumed after a rate-limit stop; the figure rewrite, the svg_overlap pass, the builds, the check and the commit were all finished in this run.)

## What I built
- `workspace/build/int1/l5g.html` (replaces the placeholder; 267 lines)
  - Lesson head (l.1-3).
  - **Concept 1** (l.5-49), regions under a combination of curves.
    - Book boxes: "Compound regions" (the section's opening paragraph) and "Areas of regions under a combination of curves".
    - Tips: "Cutting the region into pieces", and "The primitive of (x-2)^2" (the 4J rule, with a check by differentiating).
    - Demo: y = x^2 and y = (x-4)^2. Your turn: y = x^2 and y = (x-6)^2. Each has parts a, b, c.
    - **Worked example 1** (l.29) is textbook Example 28, with the book's lines only and the figure.
    - Then the book's Note (symmetry), and the tip "Worked example 1, line by line": finding (1, 1) by solving, and both substitutions.
  - **Concept 2** (l.51-98), regions between curves.
    - Book text, **Box 17** "Area between curves", and the book's paragraph "The assumption f(x) <= g(x) is important".
    - Tip "Why subtraction works", with a three-panel figure (area under g − area under f = area between) and the integral identity from 5C.
    - Tip "Finding the limits and the top curve".
    - Demo: y = (x-3)^2 and y = x+3. Your turn: y = (x-1)^2 and y = x+1.
    - **Worked example 2** (l.81) is Example 29, with the book's lines only. The tip after it shows each substitution and 2⅔ + 1⅚ = 27/6 = 4½.
  - **Concept 3** (l.100-132), a region between curves that crosses the x-axis.
    - The book's Note (two paragraphs).
    - Tip "Why the formula still works": shift both curves by c, (g+c) − (f+c) = g − f, and no split at the x-intercepts is needed.
    - Demo: y = x^2-6x+3 and y = x-3 (the C2 demo shifted down 6). Your turn: y = x^2-2x-2 and y = x-2.
    - **Worked example 3** (l.118) is Example 30. The tip after it gives the integrand expansion and the step the book leaves out (2⅔ − (−1⅚) = 4½).
  - **Concept 4** (l.134-177), regions between curves that cross.
    - The book's paragraph, and the tip "One integral for each piece".
    - Demo: y = −x^2+2x−1 and y = x^2−8x+7, meeting at (1, 0) and (4, −9). Your turn: the same first curve with y = x^2−6x+5, meeting at (1, 0) and (3, −4). Both are diagram questions, like the example.
    - **Worked example 4** (l.158) is Example 31, with the book's lines and figure. The tip after it gives both integrand expansions (as aligned displays) and every substitution.
  - **Textbook homework** (l.179-260): Exercise 5G Q1-20 verbatim, with the technology note.
    - Bands as in the book: F 1-4, D 5-18, E 19-20.
    - The 16 diagrams of Q1-Q4 are recreated as SVG.
    - Q8 and Q11 parts are each on their own line.
  - **Past-paper section** (l.262-): "timed practice" heading and the note (wording as in l5e). It names Questions 8(b), 11(c), 13, 15 and 17, in 30 minutes. All of these exist.
- `workspace/build/int1/a_5g.html`:
  - ahead, then Lesson Examples C1-C4 with every line: the meeting point solved, the top curve tested at a value of x, the integrand expanded, the brackets and the arithmetic. C1-C3 also have sketches.
  - Then Textbook Homework, with final answers only (Q1-19).
  - There is no past-paper section, as in 4J, 5D and 5E.
- `workspace/build/int1/figs_5g.py` (new) produces 31 figures:
  - c5g_e28, c5g_e29, c5g_e30, c5g_e31 (the worked examples);
  - c5g_sub1-3 (the Box 17 tip);
  - c5g_d4, c5g_y4 (the C4 diagrams);
  - a5g_c1d … a5g_c3y (the answer sketches);
  - q5g_1a-h, q5g_2a-d, q5g_3a-b, q5g_4a-b (the exercise).
  - Label placement: labels go through a `place()` helper. It tries offsets around a point and keeps the first one at which `workspace/tools/svg_overlap.py` (`check_string`) reports no new problem. A few labels are set by hand, with leaders as in the textbook (Q1f, Q1g, Q3b, Q4a, and the left points of C2/C3).
  - `save()` runs the same tool and stops the script if anything is reported.
- `workspace/checks/int1_5g.py`: the check script, 409 checks.
- `docs/pp_selected_int1.md`: I added `## 5G` (none), placed between 5F and 5H.

## Sources
- Textbook `workspace/zip/Math Textbook CMS6 Ext1 Y12.pdf`. I rendered and read:
  - teaching pages PDF 263-266 (printed 237-240): Examples 28-31 and Box 17;
  - Exercise 5G, PDF 266-269 (printed 240-243);
  - the answers, PDF 892 (printed 866, right column).
  - I zoomed the Q1-Q4 diagrams to transcribe the labels, the shading and the leaders.
  - 5H starts on PDF 270.
- Past papers: none. The catalogue lists int1-L8 with 0 items. Before choosing and again before committing, I re-read every `docs/pp_selected_*.md` and `docs/PAST_PAPERS_USED.md`: nothing to choose or record.

## Omitted, slips and doubtful items
- Textbook questions: none omitted (Q1-20 all present).
- Answers omitted, because they are show-that, sketch or explain parts with no key answer: 5a, b; 6a, b; 7a, b; 9a, b; 10a, b; 12a, b; 13a; 14a, b; 15b; 18a; and Q20.
- Textbook-key slips. In each case our own correct version is printed silently:
  - the key labels the answers to Q5, Q6 and Q7 as "5a", "6a" and "7a", but they are the answers to the c parts; we print them as c;
  - the Q16a key has a stray "(" ("((0,0), …").
- Every key value matches sympy.
- Doubtful items: none. All of the diagram data in Q1-Q4 is consistent (checked by the script).

## Verification
- `python3 workspace/checks/int1_5g.py` gives **409 checks, 0 failures, ALL OK**. It does the following.
  - Every working chain has a data-k key and must be found exactly once.
    - Each member is evaluated with sympy: integrals exactly, and brackets as F(b) − F(a), with F' equal to the integrand before it.
    - Each member is compared with the area computed independently from the curves **read from the question stem** (under-both, between, or crossing pieces).
  - The rows that find the meeting points must have exactly the roots of f = g, and the printed points must be the meeting points.
  - Every chain in a tip box and in the answer notes is checked as an identity (34 chains).
  - Exercise:
    - Q1-Q4 are recomputed from the transcribed diagrams, and the script checks that the meeting points lie at the ends of each shaded interval.
    - Q5-Q19 are recomputed from equations read from the stems. Both printed integrals in 5c, 6c, 7c, 9c and 10c must equal the area.
    - The tangents (13, 14, 18) come from sympy.diff, Q17a from solve_univariate_inequality, and Q19 from solving for k.
    - Every value is compared with the transcribed key.
  - It also checks the structure, the bands, that there is no PP block, the timed note, and that every figure exists.
- Mutation tests (INT1_SRC scratch copies). Each of these single edits gives exit 1 with the matching MISMATCH:
  - a Q1e answer;
  - a Q11c stem;
  - a WE2 chain line;
  - a C2 bracket;
  - the WE4 primitive;
  - a C2 factorisation row;
  - the timed-note part;
  - a tip arithmetic line (y = 1² = 1). Catching this one needed a fix to the check, which now catches it.
- `python3 -I workspace/tools/svg_overlap.py build/int1/svg/{c5g,a5g,q5g}_*.svg` gives **31 files, 0 problems**. I also inspected every figure as a rendered sheet, and moved labels that were ambiguous although the tool passed them (Q1e, Q1h, Q2b, the C2/C3 answer sketches).
- Solo build (scratch pack of only l5g and a_5g):
  - lesson 25 pp and answers 7 pp;
  - qa.py gives 0 problems for each;
  - the MathJax error scan gives 0;
  - the body text measures **11.3 pt in both**;
  - the overflow probe (print media, 680 px) reports scrollWidth 665 = body width, with no overflowing element.
  - Overflows I fixed on the way:
    - a `\\(` row separator read as an inline-maths opener: now written `\\{}(`;
    - a long inline chain in the WE4 tip: now aligned displays.
- Full build with flock (`build.py int1 all`):
  - lesson 266 pp and answers 100 pp;
  - qa.py gives 0 problems for each;
  - MathJax 0;
  - 11.3 pt is the dominant size in both.
- Pages inspected: all 25 lesson pages and all 7 answer pages (contact sheets, with zooms of the Q1 diagrams and the answer sketches).
  - Work boxes are sized to fill pages.
  - Remaining part-empty pages:
    - p10 (WE3 tip and the Concept 4 boxes; the C4 demo does not fit below them);
    - the half page after Q20 / the timed note;
    - the last answers page (Q18-19).

## Files and commit
- Files:
  - workspace/build/int1/l5g.html, a_5g.html and figs_5g.py;
  - svg/c5g_*.svg (9), a5g_*.svg (6), q5g_*.svg (16);
  - workspace/checks/int1_5g.py;
  - docs/pp_selected_int1.md;
  - this report.
- Commit `Int1: lesson 5G` on ch10-pack (not pushed). Only my files were staged.

## Concerns
1. Past papers: none exist for int1-L8. The section has the timed-practice note only, as the brief expects.
2. Cover placeholder `@@M5G@@`: I did not edit it, because the cover is not my file. Suggested value: "timed practice".
