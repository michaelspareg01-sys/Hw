# Task report: Pack A, Year 11 Ch 6 Trigonometry (6G–6K)

Status: DONE_WITH_CONCERNS (past-paper shortfall under house rule 8; two doubtful book items left out; one book typo in a worked example printed correctly).

## What was built (`workspace/build/y11ch6/`)
Outputs: `output/Year_11_Ext1_Ch6_Trigonometry_6G-6K_Lesson_and_Homework.pdf` (70 pp) and `..._Homework_Answers.pdf` (10 pp), force-added.
pack.json parts: cover, r6g, l6h, r6ij, l6k / a_6g, a_6h, a_6ij, a_6k. Header "YEAR 11 MATHEMATICS EXTENSION 1".

- **cover.html**: TOC with past-paper notes; text explains the revision sections and the lesson order.
- **r6g.html, Revision 6G (homework only)**: book Boxes 20–25 and the Elimination paragraph, verbatim (r6g.html:5-29). Homework (r6g.html:31-69): Easy = Foundation Q2–Q10 (Q1 calculator check left out); Medium = Development Q11, Q12, Q13, Q15; Hard = Enrichment Q16 (a–j), Q17, Q18. Past-paper set (r6g.html:72-84): PP 1 SGS 2021 Q13(d)(i) (1), PP 2 NSB 2022 Q12(c) (3) = 4 marks, 5 min. Answers a_6g.html (book answers + full PP solutions).
- **l6h.html, Lesson 6H (full teaching)**: Concept 1 domain and boundary angles (Boxes 26, 27, Ex 16 with sin graph); Concept 2 quadrants-and-related-angle method (Box 28, Note, Ex 17 with quadrant diagrams); Concept 3 reciprocal functions (Box 29, Ex 18); Concept 4 compound angles (Box 30, Ex 19, Ex 20); Concept 5 more than one function (Ex 21 + a "Steps the book skips" tip on why dividing by cos x is safe). Each concept has a tutor demo and a your-turn (new values, none repeats a homework item). Exercise 6H Q1–Q11 transcribed in full (l6h.html:155-183) in the book's bands. Timed practice note (no past papers).
- **r6ij.html, Revision 6I–6J (homework only)**: naming convention + Boxes 31–40 verbatim, with the book's sentences on the area/angle and cos θ sign (r6ij.html:5-39). Homework: Easy = 6I Q1 a,c,e; Q3 b,d,f; Q4; Q5; Q6; 6J Q1 b,d,f; Q2 a,c,e; Q3; Q4a. Medium = 6I Q7, Q9, Q12, Q13 a,c, Q14 a,c, Q15 a,d, Q17; 6J Q5 a,c, Q6, Q8, Q9, Q10, Q12, Q13, Q15. Hard = 6I Q18, Q20, Q21; 6J Q16, Q17. 6I Q20's stem drops "We saw in the previous question that" because Q19 is not included (the fact is stated instead). Timed practice note.
- **l6k.html, Lesson 6K (full teaching) + review**: Concept 1 Box 41 and the congruence-tests text, tutor demo / your turn (AAS, SAS, SSS), and a pack worked example on the ambiguous ASS case (the book has no example here); Concept 2 two-step problems with demo / your turn (two boats) and Example 31 (figure + "Steps the book skips" tip on the bearing). Exercise 6K Q1–Q21 in full (l6k.html:74-120). Timed practice note. Chapter 6 review Q16–Q35 (the 6G–6K part; Q1–Q15 cover 6A–6F) at l6k.html:126-end.
- **Figures**: `figs.py` (ch10 Fig header + `tri`, `quad`, label auto-nudging) → 93 SVGs; svg_overlap 0 problems; every label ≥ 8.25 pt in the PDF.

## Sources
- Book `workspace/sources/CSM6_EXT1Y11_book.pdf`: 6G PDF 286–291, 6H 292–297, 6I 298–306, 6J 307–313, 6K 314–319, review 320–325; answers PDF 890–892 (rendered in halves at zoom 2). All pages rendered and read.
- Past papers (catalogue `docs/pp_candidates_y11ch6.md`, record `docs/pp_selected_y11ch6.md`):
  - Sydney Grammar School, 2021, "Trial Examination, Form VI Mathematics Extension 1", Q13(d)(i), 1 mark, `2021/3U SGS.pdf` question p7, no school solution (solved independently).
  - North Sydney Boys High School, 2022, "HSC Course Assessment Task 3-Trial Examination, Mathematics Extension 1", Q12(c), 3 marks, `2022/North Sydney Boys 2022 3U Trials & Solutions.pdf` question p6, solution p14 (tan θ = 40/9).
- Pool search: text layer of every school paper plus OCR (tesseract) of all 534 scanned pages; every hit read. Nothing else fits 6G–6K without later methods (radians, compound/double angles, t-formulae, auxiliary angle) or Year 12 vectors/forces/projectiles. Details and rejected items are in the catalogue.

## Omitted / doubtful (please note)
- **Ex 6G Q14** (doubtful): the stem says "Prove that each expression is independent of θ by simplifying it" but the parts are x/y pairs whose answers are eliminations. Left out; Q15 used.
- **Ex 6I Q22** (doubtful): part (a) "Show that tan∠BT₁T₂ = cot 36°/cot 25°" does not hold for the angle at T₁ between T₁B and T₁T₂ (3D computation gives 0.848 vs 0.642; it holds for ∠LT₁T₂). Quietly left out; not mentioned in student material.
- **Example 17(a)** prints "x = −15° or −30°"; the book's own diagram shows −150°. The worked example in the lesson prints −150° (the check confirms −150°, −30°). Flagging for the controller since house rule 6 discourages silent correction.
- Revision sets are selections (as the spec allows): 6G Q1 (calculator check); 6I Q1 b,d,f, Q2, Q3 a,c,e, Q8, Q10, Q11, Q13b, Q14b, Q15 b,c, Q16, Q19; 6J Q1 a,c,e, Q2 b,d,f, Q4b, Q5b, Q7, Q11, Q14 left out to keep the sets a manageable length.
- NSB 2022 Q12(c) is also row F11 in the Ch 17 catalogue; I recorded it in pp_selected_y11ch6.md ("Ch 17 must not take it"). pp_selected_y11ch17.md did not contain it when last checked.

## Verification
- Checks (all read printed values from the HTML/SVG; equations brute-force scanned over the printed domain at 0.005° steps with bisection and touching-zero search; domain read from the printed stem and compared):
  - `python3 workspace/checks/y11ch6_6g.py` → 79 OK, 0 FAIL (simplifications, every identity side, eliminations, PP 2 by brute force).
  - `y11ch6_6h.py` → 454 OK, 0 FAIL (84 equations: demos, your turns, Examples 16–21, Exercise 6H).
  - `y11ch6_6ij.py` → 188 OK, 0 FAIL (all printed answers recomputed; figure labels checked against the data).
  - `y11ch6_6k.py` → 144 OK, 0 FAIL (lesson examples, Exercise 6K, review Q16–Q35 incl. 15 equations).
  - Mutation tests on 6G and 6H (changed answers, domain, Example 17) fail as expected.
- Build through flock: OK. `qa.py`: lesson 70 pages 0 problems; answers 10 pages 0 problems.
- PyMuPDF scan: 0 MathJax error strings, 0 "{{", 0 "@@", 0 em dashes; body text 11.3 pt on every page of both PDFs (no shrink; overflowing displays were split). Smallest figure label 8.25 pt.
- svg_overlap on all 93 SVGs: 0 problems.
- Looked at every lesson page (1–70) and answers page (1–10) on 2-up sheets at 0.62; figures also checked in a gallery at 2x.

## Commits (branch ch10-pack, not pushed)
382fc9c catalogue · e5b5db1 scaffold + 6G · 7cf58d0 6H · bec3092 6I–6J · 8fc5244 6K + review · 5d231de assembly (cover, PAST_PAPERS_USED line, outputs) · plus this report.

## Concerns
- Past-paper shortfall: 4 marks total (6G only); 6H, 6I–6J and 6K have timed practice from the textbook instead (rule 8, as in Y11 Ch 13 13B).
- Figures are schematic (not to scale), like the book's; a few dense ones (review Q29a, Q35) are readable but crowded.
- Revision sections have no warm-up page of their own; the 6G summary acts as the revision page.
