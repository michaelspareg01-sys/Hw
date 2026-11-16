# Spec: Year 9/10 Simultaneous Equations pack (linear only)

## Owner request (16 Nov)
The owner asked to "make lesson for simultaneous equations" and then chose:
- **Level:** Year 9/10, linear equations only.
- **Format:** full lesson style, like the Year 10 and Year 8 packs.

Standing owner preferences:
- use real sources and do not guess;
- give a spread of difficulty: easy, medium, hard, then past-paper level;
- hard questions and extra material are welcome;
- avoid em dashes.

## Sources
1. **Year 11 Advanced book**, `workspace/zip/Cambridge Maths Advanced 2019.pdf`. PDF page = printed page + 14; confirm on the page.
   - **Section 1G, "Solving simultaneous equations" (PDF ~38–40).** Use the substitution and elimination text, its examples and Exercise 1G.
     - Only the linear items: Q1–Q4, Q6 word problems, and any other linear items.
     - Leave out the non-linear items, such as Q5 (y = x² etc.).
   - **Section 3C, "Using simultaneous equations" with graphs (PDF ~83).** Use it for the graphical method.
   - The answers are at the back of the book.
2. **Six scanned worksheets** in `/tmp/claude-0/-home-user-Hw/33fce1a1-283b-5e23-bc89-9ac277c110f5/scratchpad/y8zip/PDF attachments/`, named "Solving Simultaneous Equations and Problem solving involving Simultaneous (1)…(6).pdf".
   - Copy them to `workspace/sources/sim/` first.
   - They are image scans, so read them visually.
   - Use their questions as homework items, labelled e.g. "Worksheet 3 Q4". The worksheets came from the owner's materials email.
   - Any handwritten answers on them are not trusted: solve every item independently.
3. **Past papers:** Year 9 and Year 10 school yearly exams in `workspace/pp/Y9/` (21 papers) and `workspace/pp/Y10/` (40 papers). The owner has confirmed Year 9 and Year 10 papers are fine.
   - Usable items: linear simultaneous equations only, by graphs, substitution, elimination or word problems.
   - Excluded: Sydney Boys 2025 (both years, a publisher recreation), DOUBTFUL items, and items whose printed solution is wrong. Those items may be used only with our own correct solution, if the question itself is sound, under the C1 ruling.
   - Never reuse an item already listed in any `docs/pp_selected_*.md`.
   - Catalogue: `docs/pp_candidates_sim.md`. Selection record: `docs/pp_selected_sim.md`.

## Pack
- **Build dir:** `workspace/build/sim/`, modelled on `workspace/build/y8cong/`.
- **pack.json:** `"header": "YEAR 9–10 MATHEMATICS"`.
- **Outputs:** `output/Year_9_10_Simultaneous_Equations_{Lesson_and_Homework,Homework_Answers}.pdf`.
- **Revision page.** Summary boxes on:
  - solving one linear equation;
  - substitution into an expression;
  - gradient–intercept form, and plotting a line from a table.

  Then a 5–6 question warm-up.
- **Lessons:**
  - **L1 The graphical method and substitution.** Covers what a solution of a pair of equations means (the point of intersection), checking a solution, solving graphically, and the substitution method.
  - **L2 The elimination method.** Covers adding or subtracting equations, multiplying one or both equations first, and choosing a method.
  - **L3 Problem solving.** Covers forming two equations from a word problem, defining the pronumerals, solving, and answering in words. The chapter review comes at the end.
- **Per lesson:**
  - Concepts, every one taught from the sources. Book text goes in book boxes, verbatim. Pack explanations go in titled tips.
  - For each concept, a Tutor demo, a Your turn and the worked examples to keep, with every line of working shown.
  - Homework in Easy, Medium and Hard bands. Book items follow the book's own bands (Foundation, Development, Challenge). Worksheet items are placed by difficulty and labelled.
  - A past-paper mini exam of 15–22 marks, timed at 1.5 × marks. A shortfall is allowed under house rule 8, with a timed-practice note.
- **Rules carried over from the Year 10 and Year 8 reviews:**
  - hints are neutral starting questions;
  - no tip leaks a homework answer or method;
  - no homework item repeats a worked example;
  - figure labels are at least 8 pt;
  - no clipped or overlapping labels (run `svg_overlap.py`);
  - body text measures exactly 11.3 pt in both PDFs.
- **Answers:** lesson examples first, then homework by band, then full worked past-paper solutions. Each solution ends with a check by substituting into both equations.
- **Checks:** `workspace/checks/sim_*.py` reads every printed answer and re-solves each pair independently with sympy. For word problems, it checks the printed equations against the stated story numbers. For graph questions, it checks the plotted lines and the intersection from the SVG coordinates. Each script exits 1 on any failure.
