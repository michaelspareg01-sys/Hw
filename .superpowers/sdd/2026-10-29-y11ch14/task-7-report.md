# Task 7 report: Lesson 14F Using counting in probability, and the Chapter 14 review

Status: DONE_WITH_CONCERNS (concerns at the end: the PP label order for NBHS now differs from the earlier lessons; Kings 2021 Q8 says "identical marbles"; one answer typo fixed silently)

Commit: 68b0d30 "Y11Ch14: lesson 14F" on ch10-pack (not pushed).

## What I built
`workspace/build/y11ch14/l14f.html` (replaces the placeholder)
- Lesson head (l.1–3). Three concepts, each with a Tutor demo, a Your turn and the textbook worked example:
  - Concept 1, counting the sample space and the event space (l.5): the two questions (ordered or unordered? repetition?), "unordered is usually easier", and a short warn box that the sample space and the event space must be counted the same way. Tutor demo: four cards, one heart and three spades, any order / in the order ♥♠♠♠. Your turn: two cards, one red and one black, any order / red then black. Worked example 21 (l.25) verbatim, with the Note.
  - Concept 2, problems requiring a variety of methods (l.42): the textbook sentence plus three bullets taken from the Example 22 solution (first digit not zero, distinct means without replacement, increasing order is counted by nCr). Tutor demo: four-digit numbers (at least 7000, odd digits, distinct, increasing). Your turn: three-digit numbers. Worked example 22 (l.65), with the box-diagram table.
  - Concept 3, the harder question (l.90): the three methods Example 23 uses (complement, addition theorem, cases with strings that begin with zero). Tutor demo: four-digit numbers (at least one 3; at least one 3 and one 6; exactly two 7s; at least two 7s). Your turn: three-digit numbers (5; 5 and 6; exactly two 2s; at least two 2s). Worked example 23 (l.113), with both tables.
- Textbook homework, Exercise 14F (l.141): all of Q1–27 verbatim, banded as in the book: Foundation 1–9, Development 10–25, Enrichment 26–27. Every part is on its own line. Nothing is omitted.
- Past-paper homework (l.201): 7 questions, 15 marks, 25 minutes.
- Chapter 14 review (l.245), in the Ch 10 review block structure: Q1–14. "(see Box 2 in Section 14A)" is printed as "(see Box 2 in Lesson 14A)"; Box 2 of l14a.html is "Calculating by unrolling factorials".

`workspace/build/y11ch14/a_14f.html` (replaces the placeholder): `{{ahead:Lesson 14F | Using counting in probability}}` → Lesson Examples C1–C3 → Textbook Homework Q1–27 (Q22 with the book's explanations for a, b, f; Q25 without c, a graph; Q27 without a, a "show that") → `{{ahead:Chapter 14 Review | Chapter review exercise}}` with review answers Q1–14 → `{{ahead:Lesson 14F | …}}` → Past-Paper Homework – Worked Solutions PP 1–7.

No figures were needed (no diagram in 14F or in the chosen papers). `figs.py` is unchanged.

`workspace/checks/y11ch14_14f.py`: 376 checks, all OK.

## Sources
- Textbook (Y11 book, all rendered and read): teaching PDF 720–723 (printed 696–699: intro, "Counting the sample space and the event space", Example 21 and Note, "Problems requiring a variety of methods", Examples 22 and 23); Exercise 14F PDF 723–726 (Foundation 1–9, Development 10–25, Enrichment 26–27); Chapter 14 review PDF 738–739. Answers: Exercise 14F on PDF 941 (left column bottom, right column); Chapter 14 review on PDF 943 (right column), which is just past the 938–942 range in the brief.
- Past papers (paths under `workspace/pp/Ext 1/`; each checked on the rendered page, and against the school solution where there is one; labels in the cover's word order):

| PP | Label | Q, marks | File | Question p | Solution p |
|---|---|---|---|---|---|
| 1 | The King’s School, 2021, Year 12 Alternative Higher School Certificate Trial Examination, Mathematics Extension 1 | Q8, 1 (MC) | `2021/3U Kings.pdf` | 5 | 15 (B) |
| 2 | Killara High School, 2023, Year 12 Examination, Mathematics Extension 1 Trial | Q6, 1 (MC) | `2023/2023_Killara_High_School_-_X1_-_Trial_-_Questions.pdf` | 5 | none (4285/593775 ≈ 0.0072, B, solved independently) |
| 3 | Normanhurst Boys High School, 2020, Mathematics Extension 1, Year 12 Course Assessment Task 4 (Trial Examination) | Q11(f), 2 | `2020/2020 Normanhurst.pdf` | 5 | 13 (12/805) |
| 4 | Sydney Technical High School, 2021, Extension 1 Mathematics, Trial HSC | Q11(c), 2 | `2021/3U Sydney Tech.pdf` | 6 | 12 (handwritten, 15/34) |
| 5 | Hornsby Girls High School, 2022, Mathematics Extension 1, Year 12 Higher School Certificate Trial Examination Term 3 | Q12(c), 2 | `2022/Hornsby Girls 3U Maths Paper _ Solutions 2022.pdf` | 8 | 18 (20/51) |
| 6 | Normanhurst Boys High School, 2022, Mathematics Extension 1, Year 12 Course Assessment Task 4 (Trial Examination) | Q11(c)(i)(ii), 1+2 | `2022/Normanhurst Boys 2022 3U Trials & Solutions.pdf` | 5 | 10 (77520, 91/380) |
| 7 | Girraween High School, 2023, Year 12 Trial Examination, Mathematics Extension 1 | Q11(c)(i)(ii), 2+2 | `2023/Girraween 2023 3U.pdf` | 7 | 16 (handwritten, 2·36C16/40C20 and 2·4C3·36C17/40C20 ≈ 0.499) |

Order runs from two 1-mark MCs, through single-group and two-group committees and a complement, to the two-class question. Every item counts both the sample space and the event space with nCr, so each one genuinely needs 14F. STHS 2021 Q11(c) (F8): the 14F method is the natural one (two cards are an unordered hand, 1 − ³⁹C₂/⁵²C₂ = 15/34), and the school's ordered method is shown as a check. All choices are recorded under `## 14F` in `docs/pp_selected_y11ch14.md`. I read `PAST_PAPERS_USED.md` and every `pp_selected_*.md` (ch10, y11ch13, y11ch14, y11ch15) before choosing and again just before committing. I also grepped every build folder for these papers. There is no overlap.

## Omitted or rejected, and why
- Exercise 14F: nothing omitted.
- Chapter 14 review: **Q15, Q16 and Q17 omitted.** Q15 is a circle arrangement (14G). Q16 (peanuts and monkeys) and Q17 (1500 birthdays) are the pigeonhole principle (14H). Q1–14 are all within 14A–14F, and none is doubtful.
- Past papers not taken: F9 (BBHS 2022 Q6) and F15 (Epping 2024 Q11(a)) are "a from one group and b from the other" committee probabilities, the same skill as HGHS 2022 Q12(c), so they would be near-duplicates. F16 (BHHS 2023 Q11(c)(i), two dice, sum 7) needs no counting, and it is part (i) of a binomial question. F4, F17 and F18 are barred by the controller rulings. F1, F2, F5, F6 and F14 were already used in 14B–14D. That leaves 15 marks of clean, varied 14F items. The pool of about 25 marks shrinks to 15 once these are taken out.

## Textbook slips (reported; printed correct, no remark)
1. Review answer Q13 prints "when this person is a women". I printed "a woman". The answer 3/7 is unchanged.
2. Example 23 refers to "Example 22". I printed "Worked example 22", the pack's name for it. Example 23(d) prints "P(atleastthree 7s)" with no spaces, and I printed it spaced.
All Exercise 14F and review answers agree with brute force.

## Notes for the controller
- **Label order.** I followed the lesson-learned rule (labels in the cover's word order). For NBHS the cover reads "MATHEMATICS EXTENSION 1 / 20xx Year 12 Course Assessment Task 4 (Trial Examination)". So PP 3 and PP 6 read "…, Mathematics Extension 1, Year 12 Course Assessment Task 4 (Trial Examination), Q…". The NBHS labels in 14A, 14B, 14D and 14E use the other order. Task 8 may want to align them.
- **Kings 2021 Q8** says "5 identical blue marbles, 6 identical black marbles and 3 identical red marbles". This is not the Ex 14E Q6 problem: there the question asked for a count, which changes if the balls are identical. Here it asks for a probability, which does not change. The worked solution says that the marbles are still 14 different objects, so every unordered selection is equally likely, and the school's key (B) counts them that way. If you would rather not have the word "identical" in the pack, the spare 1-mark replacement is F9 (BBHS 2022 Q6). It is a near-duplicate of PP 5.
- Ex 14F Q19 ("The digits 1, 2, 3 and 4 are used to form numbers …") does not say "without repetition". The book's answers (3/8, …, 17/64) need each digit used at most once, which is the normal reading of "the digits … are used". I kept the question and checked it that way. Q27 needs a random draw, and "any two particular players" implies one. The check plays every draw position and every match result.

## Verification
- `python3 workspace/checks/y11ch14_14f.py`: 376 checks, all OK, exit 0, about 36 s.
  - It reads every printed value: Worked examples 21–23 (every line of working, including the box-diagram tables and the Note's 1/3), C1–C3 (every inline value), Exercise 14F Q1–27, review Q1–14 and PP 1–7 (every step, and each MC letter as the only option equal to the answer).
  - The truths come from enumeration:
    - cards are dealt from a labelled 52-card deck: every 3-card hand, every ordered deal of 3 and of 4, with-replacement triples, and all 2 598 960 poker hands;
    - numbers 100–99 999 and all digit strings are tested digit by digit;
    - people, letters and balls are labelled, then arranged or chosen with itertools (PROMISE, PRINTER, KETTLE, FOUNDER, REPORTER, 10! seatings);
    - exits and menus are assigned with itertools.product;
    - the lottery lists all 593 775 draws, and PP 3 lists all 5 200 300 teams.
  - Reduced methods, each checked on small cases first:
    - ENTERTAINMENT: E-position sets, checked against every arrangement of EEENTNA;
    - the birthday problem: sequential probability, checked on 5- and 7-day years;
    - PP 7: sequential class places, checked against every class A for 8, 10 and 12 students;
    - the 16- and 2^n-player tournaments: a recursion, checked against an 8-player brute force over every draw and every match result.
  - Decimals are compared with the exact value rounded as asked. The algebraic answers (Q24b, Q25b, Q27c, review Q2b and Q2c) are evaluated at several values.
  - Structure: 15 marks, 25 min, PP numbering, labels the same in both files, one hint each, part marks, bands F 1–9 / D 10–25 / E 26–27, and the review numbering and scope.
  - Mutation test: I changed seven printed values (a WE21 factor, a WE23 count, a C3 step, TB5i, TB15c, TB21b, a PP 2 factor). All seven were caught, with exit 1.
- Build (with the flock lock): `python3 build.py y11ch14 all && mv lesson.pdf answers.pdf y11ch14/`. The lesson PDF has 126 pages (14F is pp. 104–126) and the answers PDF has 38 (14F is pp. 31–38).
- `qa.py`: lesson.pdf 0 problems, answers.pdf 0 problems. MathJax error-string scan: 0 in both.
- Pages inspected: every 14F lesson page 104–126 and answers pages 30–38, from contact sheets plus zooms. Fixes made:
  - Long displays in WE22(d) and WE23(b) were clipped. I rewrote them as indented lines.
  - Pages were half-blank. Each concept now runs concept box, then demo, then Your turn on one page, with its worked example on the next page; WE23 fits on one page.
  - The work boxes were resized to fill the homework, PP and review pages.
  - The Q22 answer lines touched, so I spaced them.
  - The last lesson page (review Q13–14) is about 75% full.

## Files changed
- `workspace/build/y11ch14/l14f.html`, `workspace/build/y11ch14/a_14f.html` (placeholders replaced)
- `workspace/checks/y11ch14_14f.py` (new)
- `docs/pp_selected_y11ch14.md` (appended `## 14F` and the review note)
