# Spec: Year 10 Trigonometry (part 2) and Circle Geometry packs

## Owner request (11–12 Nov)
The owner wants Year 10 packs on the two topics from their schedule:
- **Topic 12, Trigonometry (part 2), MA5-TRG-P-02.** Lessons 3A, 4B and 5A.
- **Topic 13, Circle Geometry, MA5-CIR-P-01.** Lessons 6B, 7A and 8B.

The owner's instructions:
- "Since we have limited textbook questions you may source more from pastpapers."
- "You may pick hard y11 level questions too, just make sure there is a difficulty variety: easy, medium, hard, pastpaper lvl."
- Use real sources and do not guess.

**Binding rules.** Everything in `docs/superpowers/specs/house-rules.md` applies, except where this spec changes it. The rulings in `.superpowers/sdd/2026-11-07-integration/progress.md` also bind, and they are listed under "Rules carried over" below.

## Syllabus scope
The scope comes from the official NSW Mathematics K–10 (2022), Stage 5.

**MA5-TRG-P-02, Trigonometry D (Path):** "establishes and applies the properties of trigonometric functions and finds solutions to trigonometric equations". It covers:
- the unit-circle definitions of sin, cos and tan, and tan = sin/cos;
- graphs of sin, cos and tan for 0°–360° and for angles of any size, including negative angles;
- for obtuse angles: sin A = sin(180° − A), cos A = −cos(180° − A), tan A = −tan(180° − A);
- m = tan θ, where θ is the angle of inclination;
- exact ratios for 30°, 45° and 60°;
- complementary angles: sin A = cos(90° − A), cos A = sin(90° − A);
- finding the possible angle(s) from a given ratio;
- the sine rule and area rule, including the ambiguous case.

**Prerequisite, from Topic 11 = MA5-TRG-P-01, Trigonometry C:** 3D problems, and the sine, cosine and area rules in 2D, including bearings. Questions may use these as known.

**MA5-CIR-P-01, Circle geometry (Path):** "applies deductive reasoning to prove circle theorems and solve related problems". It covers:
- terminology;
- chord and angle properties, with their proofs;
- tangent ⟂ radius;
- tangent and secant properties, with their proofs;
- finding unknown angles and lengths.

**Out of scope:**
- radians;
- cosec, sec and cot;
- compound angles such as 2x in trig equations, except in the Hard band;
- Pythagorean identities beyond tan = sin/cos;
- equations of circles.

## Sources, all already downloaded
1. **Year 11 Advanced book:** `workspace/zip/Cambridge Maths Advanced 2019.pdf`. PDF page = printed page + 14; confirm this on the page.
   - Ch 5 Trigonometry: 5A right-angled (PDF from about p152), 5D general angles (182), 5E quadrant, sign and related angle, with graphs (186), 5F given one ratio find another (192), 5H trig equations (200), 5I sine rule and area formula, including the ambiguous case (206).
   - 6B gradients and the angle of inclination (238–245).
   - The answers are at the back. Exercise bands are Foundation / Development / Challenge.
2. **AMSI TIMES module "Circle Geometry"** (Years 9–10, Module 26, CC BY-NC-ND): `workspace/sources/y10/AMSI_TIMES_Circle_Geometry.pdf`.
   - Radii and chords (p5), angles in a semicircle (9), angles at the centre and circumference (11), cyclic quadrilaterals (14), tangents (16–21), alternate segment (22), similarity and circles: intersecting chords, secants, tangent–secant (24–27).
   - 28 exercises, with answers on p37–44.
   - It holds the theorem statements and proofs.
3. **Maths Pathway worksheets**, all with answers, in `workspace/sources/y10/`:
   - `MP_the_unit_circle.pdf`
   - `MP_using_symmetry_on_the_unit_circle.pdf`
   - `MP_graphs_of_trigonometric_functions.pdf`
   - `MP_solving_trigonometric_equations.pdf`
   - `MP_arcs_and_angles_in_circles.pdf`
   - `MP_chords_secants_and_tangents.pdf`
   - `MP_intersecting_chords_and_secants.pdf`
4. **Past papers:** Year 10 yearly exams, 2020–2025, in `workspace/pp/Y10/` (40 files). The catalogue is `docs/pp_candidates_y10_A.md` + `_B.md`.
   - NSG 2022 appears in both; treat the two copies as one.
   - **Exclude:**
     - Sydney Boys 2025, a publisher's recreation;
     - every row marked DOUBTFUL;
     - every row whose note says the printed solution is wrong.
   - Scots 2020, Scots 2021 and James Ruse 2024 have no solutions. They may be used, solved independently, and checked with extra care.

## The two packs

| Pack | Build dir | Lessons | Revision page |
|---|---|---|---|
| Trigonometry part 2 | `workspace/build/y10trig/` | **T1 Angles of any size:** the unit circle (Adv 5D), quadrants, ASTC, related angles, the obtuse relationships and the graphs of sin, cos and tan (5E), tan = sin/cos, and gradient m = tan θ (6B, inclination part only). **T2 Exact values and trig equations:** the exact ratios for 30°, 45° and 60°, and complementary angles (from 5A or wherever the book has them), given one ratio find another (5F), and finding the possible angles from a ratio, i.e. equations in degrees over 0°–360° (5H). **T3 The ambiguous case:** the sine rule ambiguous case, and the area rule giving two angles (5I). | Topic 11 summary: SOHCAHTOA, bearings, the sine rule, the cosine rule, the area rule. 5–6 warm-up questions |
| Circle geometry | `workspace/build/y10circ/` | **C1 Chords, radii and angles:** terminology, radii and chords (the perpendicular from the centre, equal chords), the angle in a semicircle. **C2 Angles at the centre and circumference:** angles on the same arc, and cyclic quadrilaterals, including the exterior angle. **C3 Tangents and secants:** tangent ⟂ radius, tangents from an external point, the alternate segment theorem, intersecting chords, secant–secant and tangent–secant. | Year 7–9 geometry: angle facts, isosceles triangles, congruence and similarity tests, and the structure of a geometric proof (reasons). 5–6 warm-up questions |

## Lesson structure (both packs)
1. **Concepts.** Every definition, theorem and proof from the teaching source for that lesson, with nothing omitted.
2. **For each concept:**
   - a **Tutor demo**: a value-changed source example, with full working;
   - **Your turn**;
   - **Worked example(s) to keep**: the source's own examples, keeping the source's lines and wording.
3. **Homework in four labelled bands**, chosen to give a real spread of difficulty:

   | Band | Trig pack | Circle pack |
   |---|---|---|
   | **Easy** | Year 11 book Foundation items in scope; Maths Pathway sheets | Maths Pathway sheets |
   | **Medium** | Year 11 book Development items; Maths Pathway sheets | Maths Pathway sheets; easier AMSI exercises |
   | **Hard** | Year 11 book Challenge items (hard Year 11 questions are allowed); hard past-paper parts | AMSI proof exercises; hard past-paper parts |

   - Items are transcribed verbatim, each with its source label (book and exercise and Q, Maths Pathway sheet and Q, or AMSI Exercise N).
   - Past-paper items used in a band carry the full past-paper label and a hint. Their full solutions go in the answers.
   - Aim for roughly 6–10 Easy, 8–12 Medium and 5–8 Hard items per lesson, scaled to what the lesson needs.
4. **Past-paper level:** a mini exam per lesson, 15–22 marks, timed at 1.5 × marks, under house rules 3–8.

**No reuse.** Never use a question twice within or between the two packs. Track them in `docs/pp_selected_y10trig.md` and `docs/pp_selected_y10circ.md`; re-read both before choosing and again before committing.

## Rules carried over from the integration reviews
- Textbook-styled boxes (concept, theorem, "From the text" example) hold only the source's own sentences and lines. Every added line, step or note goes straight after the box in a titled tip, such as "Steps the source skips: Example N". Our own examples are titled "Our own example: …". No step of working may be skipped.
- Hints are neutral starting questions: no value, step or technique.
- Pack explanation goes only in titled `box tip` boxes.
- Figures:
  - no clipped or overlapping labels; run `workspace/tools/svg_overlap.py`;
  - figures must be faithful to the source diagram.
- Body text must measure exactly 11.3 pt in both PDFs.
- Avoid em dashes in new text.
- Solo builds go in your own scratch copy; shared builds go only through the flock command.

## Deliverables
- `output/Year_10_Trigonometry_Part2_{Lesson_and_Homework,Homework_Answers}.pdf`
- `output/Year_10_Circle_Geometry_{Lesson_and_Homework,Homework_Answers}.pdf`

`pack.json` settings:
- `"header": "YEAR 10 MATHEMATICS"`;
- footers "Year 10 Trigonometry (part 2) | Lesson and Homework" / "| Homework Answers", and likewise for "Year 10 Circle Geometry".

Add each pack's paragraph to `docs/PAST_PAPERS_USED.md` at assembly.
