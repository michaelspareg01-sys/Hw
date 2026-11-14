# Spec: Year 7 revision practice pack (every Task 4A/4B topic except angles and length/area)

## Owner request (14 Nov)
The owner asked for "revision material for every topic except angle relationships", covering the topics in the two 2023 Year 7 tasks:
- 2023 Year 7 Mathematics Task 4A: angle relationships, linear relationships, probability.
- 2023 Year 7 Mathematics Task 4B: operations with numbers, computation with integers, indices, fractions, decimals and percentages, algebraic techniques, equations, length and area.

The owner's choices:
- **Practice questions only**, in the same style as `workspace/build/y7y8prac/`.
- **Skip length and area.** It is already in the Year 7–8 pack.
- **Past papers guide only.** In the owner's words: the past papers "only serve as guidance for topic and question type to include (but not limited to). Should probably use textbook as main question source, or you may make up your own question if you wish".
- **Weighting** (earlier owner preference): more hard questions than easy ones. Extra beyond 2 hours is welcome, because the tutor picks from it.

## Sources
- **Main source:** ICE-EM Mathematics 7, 3rd ed, `workspace/zip/Y7.pdf` (PDF page = printed page + 14; confirm on the page). Chapter starts, printed:

  | Ch | Title | Starts |
  |---|---|---|
  | 1 | Whole numbers | 1 |
  | 2 | Factors, multiples, primes and divisibility | 38 |
  | 3 | An introduction to algebra | 69 |
  | 4 | Fractions – part 1 | 96 |
  | 5 | Fractions – part 2 | 125 |
  | 7 | Algebra with fractions | 187 |
  | 8 | Decimals | 201 |
  | 10 | Review and problem-solving | 275 |
  | 11 | Integers | 299 |
  | 12 | Algebra and the Cartesian plane | 322 |
  | 14 | Negative fractions and decimals | 372 |
  | 15 | Percentages and ratios | 386 |
  | 16 | Solving equations | 405 |
  | 17 | Probability | 428 |
  | 22 | Review and problem-solving | 533 |

  Answers are at the back.
- **Guides:** the two tasks.
  - Task 4A: `/tmp/claude-0/-home-user-Hw/33fce1a1-283b-5e23-bc89-9ac277c110f5/scratchpad/y8zip/Additional Year 7 Assessments/2023-Yr7-Task4A.pdf`
  - Task 4B: `/tmp/claude-0/-home-user-Hw/33fce1a1-283b-5e23-bc89-9ac277c110f5/scratchpad/y8zip/Additional Year 7 Assessments/2023-7-Task4B.pdf`
  - Copy both into `workspace/sources/y7/` first.
  - Read every question in them, and make sure each question type they test is covered in the matching section.
  - Do NOT copy task questions into the pack.

## Pack
- **Build dir:** `workspace/build/y7rev/`, styled exactly like `workspace/build/y7y8prac/`: cover, q_*.html, a_*.html, figs.py, the "header" field in pack.json.
- **Outputs:** `output/Year_7_Revision_Practice_Questions.pdf` and `output/Year_7_Revision_Practice_Answers.pdf`.
- **Sections**, in this order. Map each one to the right ICE-EM sections by reading the chapter contents.

  | Section | Topic | Likely ICE-EM chapters |
  |---|---|---|
  | A | Operations with numbers | Ch 1–2 |
  | B | Computation with integers | Ch 11 |
  | C | Indices | Find where ICE-EM 7 teaches powers, square roots and index notation |
  | D | Fractions, decimals and percentages | Ch 4, 5, 8, 14, 15 |
  | E | Algebraic techniques | Ch 3, 7 |
  | F | Equations | Ch 16 |
  | G | Linear relationships | Ch 12 |
  | H | Probability | Ch 17 |
  | I | Mixed challenge | From the Ch 10 and Ch 22 review and problem-solving items on these topics |

- **Per section:**
  - a timing line;
  - 8–14 questions, easy to hard, with about one-third warm-up and two-thirds harder: later exercise parts, multi-step, reasoning, and the Review/Challenge exercises;
  - every distinct skill, and every question type in the tasks, covered at least once.
- **Size:** target about 3–4 hours in total. The cover shows minutes per section, says the pack holds more than one lesson, and marks a suggested 2-hour core set (★) that leans hard.
- **Wording:**
  - Textbook questions are verbatim, with a source label such as `Y7 ICE-EM Ex 11C Q4`.
  - Our own questions are allowed, especially to match a task question type the book lacks. Label them "Pack question", keep them clearly in Year 7 scope, and verify their answers with extra care.
- **What the pack leaves out:**
  - no teaching boxes, worked examples or hints, as in the Y7–8 pack;
  - no question already in the Y7–8 pack (check `workspace/build/y7y8prac/q_*.html`).
- **Answers PDF:**
  - a final answer for every part;
  - short working (1–3 lines) for multi-step items;
  - matches the book's answers, except that a book key slip gets our correct answer printed silently;
  - doubtful questions are skipped quietly.
- **Check:** `workspace/checks/y7rev.py` reads every printed answer from the HTML and recomputes it independently. Use `fractions` for exact arithmetic, enumerate sample spaces for probability, and solve equations with sympy. It must exit 1 on any failure.
- **Build and QA:**
  - build with flock;
  - qa.py reports 0/0;
  - the MathJax scan finds 0;
  - some span measures exactly 11.3 pt in both PDFs;
  - svg_overlap.py reports 0;
  - look at every page.
- **Style:** plain short sentences, no em dashes.
