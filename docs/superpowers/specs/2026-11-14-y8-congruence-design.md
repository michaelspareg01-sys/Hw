# Spec: Year 8 Congruence pack

## Owner request (14 Nov)
"Let's do congruence, I feel like it builds on nicely from the angle relationships."

The pack follows on from the angle work, Y8 6A–6D, already in the Year 7–8 practice pack.

Standing owner preferences:
- use real sources;
- give a difficulty variety: easy, medium, hard, then past-paper level;
- hard questions are welcome, and so is extra material;
- avoid em dashes.

## Source
Cambridge Maths NSW Stage 4 Year 8 (2nd ed), Chapter 8 "Transformations and congruence": `workspace/sources/y8/chapter 8.pdf`. Its answers are in `workspace/sources/y8/answer.pdf`; find the Ch 8 block.

| Use | Sections |
|---|---|
| Revision page only | 8A Reflection, 8B Translation, 8C Rotation |
| Taught | 8D Congruent figures, 8E Congruent triangles, 8H Using congruent triangles to establish properties of quadrilaterals |
| Not taught | 8F–8G Similar figures and triangles (extension). Note this on the cover. |

The Chapter 8 review questions that are in scope go at the end of the last lesson.

## Pack (full lesson style, like the Year 10 packs)
**Build dir:** `workspace/build/y8cong/`. Model it on `workspace/build/y10circ/` (pack.json with `"header": "YEAR 8 MATHEMATICS"`, cover, revision, l*/a* files, figs.py and checks).

**Outputs:** `output/Year_8_Congruence_{Lesson_and_Homework,Homework_Answers}.pdf`

**Revision page.** Summary boxes on:
- angle facts from 6A–6D: angles at a point, vertically opposite, parallel lines, triangle and quadrilateral angle sums;
- transformations 8A–8C.

It ends with a 5–6 question warm-up.

**Lessons:**
- **L1 Congruent figures (8D):** congruence, corresponding vertices, sides and angles, and the notation.
- **L2 Congruent triangles (8E):** the SSS, SAS, AAS and RHS tests, writing a congruence statement, and why AAA and ASS do not prove congruence (if the book says so).
- **L3 Proving properties with congruent triangles (8H):** setting out a congruence proof, and proving properties of quadrilaterals. The Chapter 8 review (in-scope items) comes at the end.

**Each lesson:**
1. Concepts: every box, definition and example from the book's teaching part, with no omissions. Book text sits in book-styled boxes, verbatim. Pack additions sit in titled tips after the box.
2. Per concept: a Tutor demo (a value-changed book example), a Your turn, and the book's examples to keep, with every line of working.
3. Homework in labelled bands, verbatim, each item with its source label:

   | Band | Book band |
   |---|---|
   | Easy | Fluency |
   | Medium | Problem-solving |
   | Hard | Reasoning and Enrichment |

4. A past-paper level set from real school Year 9 and Year 10 yearly exams in `workspace/pp/Y9/` and `workspace/pp/Y10/`. Use congruence questions only: proofs, finding sides and angles via congruence, naming tests.
   - Search every paper, including the scanned ones (view or OCR them).
   - Excluded: Sydney Boys 2025 (both years), DOUBTFUL items, and items whose printed solution is wrong.
   - Label each item with the school name as printed. If the cover lacks it, use THSC Online's listing (Y10 ruling).
   - Aim for 15–22 marks per lesson. A shortfall is allowed under house rule 8, with a timed-practice note.
   - Record the items in `docs/pp_selected_y8cong.md`. Never reuse an item that appears in another `docs/pp_selected_*.md`.

**Rules carried over from the Year 10 reviews:**
- hints are neutral starting questions;
- no tip leaks a homework answer;
- no homework item repeats a worked example;
- bands follow the book's own bands;
- no clipped or overlapping labels (run svg_overlap.py);
- figures stay faithful to the source;
- circles are drawn round;
- body text measures exactly 11.3 pt in both PDFs.

**Answers:**
- Lesson examples first, then homework by band, then full worked past-paper solutions.
- Congruence proofs are set out in the book's style: statement, reason, test, conclusion.

**Check:** `workspace/checks/y8cong_*.py` reads every printed numeric answer and recomputes it from the given data, using coordinates where useful. For proofs, it checks that each named test matches the given equal parts (for example, SAS needs the included angle).
