# Spec: "Year 7–8 Angles and Measurement: Practice Pack" (one 2-hour lesson, practice questions only)

Owner request (30 Oct): a revision pack of **practice questions only** for a **2-hour lesson**, covering content equivalent to the student's Year 7 Ch 2 (angle relationships) and Ch 10 (measurement: length, perimeter, area), plus Year 8 6A–6D (angles, triangles, quadrilaterals) and 3D (area of special quadrilaterals). The student's own Year 7 book is not in our files; the owner said to use the equivalent chapters of the Year 7 book we have.

## Sources (real textbook questions only; never invented)
- Year 7: ICE-EM Mathematics 7, 3rd ed — `workspace/zip/Y7.pdf` (PDF page = printed + 14).
  - Ch 6 An introduction to geometry: 6A–6G (printed 144–182), Review exercise PDF 197–198, Challenge exercise PDF 199–200. Answers from PDF 576.
  - Ch 9 Measurement: 9A Units, 9B Other units, 9D Perimeter, 9E Area, 9F Areas by addition and subtraction, 9G Areas of triangles and parallelograms (printed 232–258; skip 9C unitary method, 9H volume, 9I time, 9J speed). Review exercise PDF 283–285 (length/perimeter/area items only), Challenge PDF 286+. Answers ≈ PDF 585–592 (find the Ch 9 block).
- Year 8: Cambridge Maths NSW Stage 4 Year 8, 2nd ed — `workspace/sources/y8/chapter 6.pdf` (6A pp 4–11, 6B 12–18, 6C 19–25, 6D 26–31), `chapter 3.pdf` (3D pp 21–24), answers `workspace/sources/y8/answer.pdf` (book pages 600–660).

## Pack shape
- Build dir `workspace/build/y7y8prac/`; outputs `Year_7_8_Angles_and_Measurement_Practice_Questions.pdf` and `Year_7_8_Angles_and_Measurement_Practice_Answers.pdf` → `/home/user/Hw/output/` (force-add both in git, `*.pdf` is ignored).
- Cover: title, one-line instructions, a timing table (section → suggested minutes, total 120 min).
- Part A Angles (≈ 60 min), Part B Measurement (≈ 50 min), Part C Mixed challenge (≈ 10 min). Topic order:
  - A1 Points, lines, angles and notation (Y7 6A–6B + Y8 6A); A2 Measuring and classifying angles (Y7 6C); A3 Angles at a point (Y7 6D); A4 Transversals and parallel lines (Y7 6E + Y8 6B); A5 Further parallel-line problems and proving lines parallel (Y7 6F–6G); A6 Triangles (Y8 6C); A7 Quadrilaterals (Y8 6D).
  - B1 Units and conversions (Y7 9A–9B); B2 Perimeter (Y7 9D); B3 Area of rectangles and composite shapes (Y7 9E–9F); B4 Triangles and parallelograms (Y7 9G); B5 Special quadrilaterals: rhombus, kite, trapezium (Y8 3D).
  - C: 4–6 questions from the two chapters' Review/Challenge exercises (angles and length/perimeter/area only).
- Per topic: a timing line ("about N min"), then 3–6 questions chosen from that section's exercise (and its review items), easy → harder, covering each distinct skill once. **No teaching boxes, no worked examples, no hints.** Total working time must fit 120 min for a typical Year 7/8 student (estimate each question; record estimates in the report).
- Every question verbatim (wording, values, units, diagrams recreated as SVG), with a small source label: `Y7 ICE-EM Ex 6D Q3` / `Y8 Cambridge Ex 6C Q5` / `Y7 Ch 9 Review Q4`. Parts on separate lines where long; short numeric parts may sit in a grid. Modest working space (`{{work:NN}}`), sized to the question.
- Avoid items needing a protractor, ruler, compasses, grid paper or a physical activity unless the diagram we draw makes the task doable on the page (e.g. "measure this angle" only if our SVG is drawn to exact scale; prefer to skip).
- Answers PDF: final answers for every part, with short working (1–3 lines) for multi-step items and reasons for angle facts ("co-interior angles are supplementary"). Match the textbook answers; where the book's key has a slip, print our own correct answer silently (house precedent). Doubtful questions: skip quietly (house rule 6).

## Correctness and QA (house rules apply)
- `workspace/checks/y7y8prac.py` reads every printed answer from the answers HTML and recomputes independently (angle sums, perimeters, areas, unit conversions); exit 1 on failure.
- Build with the flock command (`python3 build.py y7y8prac all`); qa.py 0/0; MathJax scan 0; look at every page; plain short sentences, no em dashes in new text.
