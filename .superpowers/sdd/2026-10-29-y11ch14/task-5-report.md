# Task 5 report: Lesson 14D Ordered selections with identical elements

Status: DONE_WITH_CONCERNS (concerns are at the end: one source label, one textbook typo kept verbatim)
Commit: d9f914d "Y11Ch14: lesson 14D" on ch10-pack (not pushed)

## What I built

### `workspace/build/y11ch14/l14d.html`
- Lesson head (l.1–3). I kept the textbook's two opening sentences and added one sentence on overcounting.
- **Concept 1: counting with identical elements** (l.5). Concept box with the PRESSES derivation (7!, overcounting by 2! and 3!, so 7!/(2!×3!) = 420), **Box 10** (l.13), and the r_i = 1 note.
  - Tutor demo: 4 mugs and 5 cups, then a chipped mug plus 2 replaced cups, then PEPPER.
  - Your turn: 2 vases and 4 jars (same changes), then TOOTH.
  - **Worked example 12** (l.30), copied from the textbook.
- **Concept 2: words with only two different letters** (l.41). Box 11 (l.46).
  - I dropped the textbook's forward note "After the next section, we will be able to use the concise symbol nCr …" and the clause "and will be vital in the next section", because of the no-forward-references rule.
  - I added a box, "An application: paths on a grid" (l.49), with a figure `grid32`. It shows the 3 by 2 grid, the path RDRRD and 5!/(3!2!) = 10. The textbook teaching pages have no grid paths, but the spec's topic map puts grid paths in 14D and two past papers need them. This box applies Box 11 to grids.
  - Tutor demo: 5 women and 3 men, a queue of 8, and a 4 by 2 grid (`grid42`).
  - Your turn: 4 women and 2 men, a queue of 6, and a 3 by 3 grid (`grid33`).
  - **Worked example 13** (l.75), with the table of ten 2s.
- **Concept 3: using cases** (l.86). The text is verbatim except that "As mentioned in the previous section" became "As mentioned in Lesson 14C".
  - Tutor demo: six-letter words from ADDRESS (1260). Your turn: five-letter words from LETTER (180).
  - **Worked example 14** (l.97): PRESSES, six-letter words, cases 180 + 120 + 120 = 420.
- **Textbook homework** (l.114): Exercise 14D, all 19 questions, verbatim, banded as in the book: Foundation 1–5 (l.117), Development 6–15 (l.128), Enrichment 16–19 (l.149). Every part is on its own line, including the sub-parts 8a i–iv, 16c i–v and 19b i–iv. No question is omitted.
- **Past-paper homework** (l.163): 12 items, 16 marks, 25 minutes. There is a `.pp-intro` line and a note that PP 8 and PP 9 are probability items and PP 10 and PP 11 are grid paths. Each item has one hint, which gives a starting idea only.

### `workspace/build/y11ch14/a_14d.html`
- `{{ahead}}` heading, then **Lesson Examples** C1–C3 (l.3–27), one part per line.
- **Textbook Homework** 1–19 (l.28–55). Final answers only; 19e and 19f are explanations, so they have no answer. Every value matches the book's answers on PDF 940.
- `{{ahead}}`, then **Past-Paper Homework – Worked Solutions** (l.56 on). Full working; each MC item explains the choice and the common wrong option.

### `workspace/build/y11ch14/figs.py`
- `grid()` (l.117) and `fig_14d()` (l.140) draw `grid32`, `grid42`, `grid33`, `nbhs22` (the NBHS 2022 5 by 3 grid), `stalo24` (the St Aloysius 2024 grids, 5 by 3 and 4 by 2, joined at a corner) and `stalo24c` (the same grids with the meeting point C labelled, for the solution).
- The earlier SVGs regenerate unchanged.

### `workspace/checks/y11ch14_14d.py`
- 239 checks, all reading printed values from the HTML. It exits 1 on any failure.
- Distinct arrangements are counted by brute force with a next-permutation generator over the multiset, checked against `set(permutations)`. This covers every word in the lesson, Q1 (including EQUILATERAL, 4,989,600 arrangements, about 3 s) and TRANSITION.
- Grid paths are counted on the grid read back from the built SVGs (segments, dots, labels). So the figure, the question and the printed answer are tied together. The drawn path in `grid32` is also read back as RDRRD.
- Q10 and Q17 use a split method, which is first checked against full enumeration on smaller cases.
- Every '='-piece of every printed chain is checked, and each term of the case sums is checked against its own case count.
- It also checks the PP structure: marks, time, numbering, labels identical in both files, one hint each, part marks, and MC letters.
- A mutation test (a changed answer, and a grid edge deleted from the SVG) gives MISMATCH as expected.

## Sources used
- Textbook pages: Y11 book, PDF 706–710 (14D teaching pages and the full exercise with its band headings). Answers: PDF 940, Exercise 14D block, rendered in halves at zoom 2.
- I solved every textbook answer independently by brute force, and all agree with the book. The book counts Y as a consonant in PROPORTIONALITY Q10, and that gives its printed answer.

### Past papers (all `workspace/pp/Ext 1/`)

| PP | Source label (as printed) | Q, marks | File, question p → solution p | School answer |
|---|---|---|---|---|
| 1 | Knox Grammar School, 2022, Higher School Certificate Trial Examination | Q7, 1 (MC) | `2022/Knox 2022 3U Trials & Solutions.pdf` p2 (right half) → p7 | B, 30240 |
| 2 | Sydney Boys High School, 2020, Year 12 Term 3 Trial HSC | Q11(a), 1 | `2020/2020 SBHS 2.pdf` p7 → p15 | 360 |
| 3 | Sydney Technical High School, 2023, Trial HSC, Extension 1 Mathematics | Q1, 1 (MC) | `2023/Sydney Technical 2023 3U.pdf` p3 → p19 | B, 6!/2! (handwritten) |
| 4 | Sydney Grammar School, 2022, Trial Examination, Form VI Mathematics Extension 1 | Q12(a), 1 | `2022/Sydney Grammar 2022 Extension 1 _ Solutions.pdf` p9 → p24 | 907200 |
| 5 | Sydney Grammar School, 2023, Trial Examination, Form VI Mathematics Extension 1 | Q11(c), 2 | `2023/Sydney Grammar 2023 3U.pdf` p7 → `2023/Sydney Grammar 2023 3U Solutions.pdf` p2 | 24 and 90 (scanned) |
| 6 | Baulkham Hills High School, 2020, Year 12 Trial Examination | Q8, 1 (MC) | `2020/2020 Bauklham Hills.pdf` p4 → p12 | D, 8!/2! |
| 7 | St George Girls High School, 2020, Trial HSC Examination | Q11(c)(i)(ii), 1+2 | `2020/2020 SGGHS.pdf` p7 → p19 | 50400 and 10080 (handwritten) |
| 8 | Normanhurst Boys High School, 2021, Year 12 Course Assessment Task 4 (Trial Examination) | Q3, 1 (MC) | `2021/3U NBHS.pdf` p3 → no solutions | solved independently and enumerated: 1/28, C |
| 9 | Ascham School, 2020, Trial HSC Examination | Q2, 1 (MC) | `2020/2020 Ascham.pdf` p2 → p8 | B, 1/360 (handwritten) |
| 10 | Normanhurst Boys High School, 2022, Year 12 Course Assessment Task 4 (Trial Examination) | Q11(e), 2 | `2022/Normanhurst Boys 2022 3U Trials & Solutions.pdf` p5 → p10 | 56 |
| 11 | St Aloysius' College, 2024, Trial Higher School Certificate Examination | Q8, 1 (MC) | `2024/St Aloysius_ College 2024.pdf` p5 → no solutions | solved independently, paths enumerated on the recreated figure: 840, B |
| 12 | Hurlstone Agricultural High School, 2023, Higher School Certificate Trial Examination | Q10, 1 (MC) | `2023/Hurlstone 2023 3U.pdf` p4 → p19 | C, 10!/(4!2!) |

- Every label ends "Mathematics Extension 1, Q…" except PP 3, whose cover reads "Extension 1 Mathematics". The labels keep "Extension&nbsp;1,&nbsp;Q" together.
- I checked every item on the rendered page and against the school solution, where one exists.
- I re-read all the `docs/pp_selected_*.md` files and `PAST_PAPERS_USED.md` before choosing and again before committing, including the new Ch 15 15C section. None of these questions is used elsewhere. Other questions from the same papers are used elsewhere, and the record notes this.
- The choices are appended under `## 14D` in `docs/pp_selected_y11ch14.md`.
- **Fit to the lesson:**
  - PP 8 and PP 9 are probability items, but both need the 14D count, which is the whole point of the item. The solutions also explain why the distinct words are equally likely.
  - PP 12 (row B8, which 14B left for 14E) is solved entirely by Box 10. Each player gets a label (1st–4th, F, F, O, O, O, O), so the count is 10!/(4!2!). It does not need nCr.

## Marks: 16 (inside 15–22)
I swept the whole catalogue. Every 14D row is used except the following:
- **D5** (Killara 2023 Q7, STATISTICS): the same question as SGGHS 2020 Q11(c)(i). The catalogue advises one STATISTICS item per pack.
- **D9** (Knox 2022 Q11(f)): the same wording and skill as D8.

Of the 14C/14D rows offered to me, I used C4 and C5 and left out:
- **C9** (NSG 2023 Q5): STATISTICS again, a near-duplicate.
- **C10** (Hornsby 2023 Q4): PROBABILITY, where the answer depends on Y being a consonant and the question does not say so. This is doubtful under house rule 6.

I also took F1, F6 and B8.

## Omitted or rejected
- Textbook: nothing omitted.
- Teaching text: the two forward references to nCr and "the next section" were dropped, as described above.

## Verification
- `python3 workspace/checks/y11ch14_14d.py`: 239 checks, all OK, exit 0.
- `python3 workspace/checks/y11ch14_14c.py`: 205 checks, all OK, so 14C is not disturbed.
- Build command: `cd workspace/build && python3 build.py y11ch14 all && mv lesson.pdf answers.pdf y11ch14/`.
- `qa.py`: lesson.pdf 74 pages, 0 problems; answers.pdf 22 pages, 0 problems.
- MathJax error scan (PyMuPDF text, the 7 strings): 0 in both PDFs.
- **Pages inspected:** lesson PDF pp. 56–74 (14D) and answers PDF pp. 16–22 (14D), as contact sheets plus a larger render of p22.
- **Layout fixes:**
  - The Concept 2 heading was stranded, so I restored a page break before Concept 2.
  - The Q19 work box was split across pages, so I shrank it to 70 mm.
  - Part c of the Concept 2 demos now has its grid figure beside the text.
  - Work boxes are sized so no box border splits across pages.
  - The Lesson Example answers have one part per line, with spacing so the fractions do not touch.
  - MC options with fractions have extra row gap.
- Some pages are not full: p56 bottom, p70 and the last PP page. This is because the boxes cannot be split, and no box is split.

## Files changed
- `workspace/build/y11ch14/l14d.html`
- `workspace/build/y11ch14/a_14d.html`
- `workspace/build/y11ch14/figs.py`
- `workspace/build/y11ch14/svg/{grid32,grid33,grid42,nbhs22,stalo24,stalo24c}.svg`
- `workspace/checks/y11ch14_14d.py`
- `docs/pp_selected_y11ch14.md`

## Concerns for the controller
1. **BHHS 2020 Q8 (PP 6) source.** The file has no cover page, and the question pages print no school name. I took the school and title from the marking-guidelines header: the crest reads "Baulkham Hills", and the heading reads "Year 12 Trial Examination 2020 Mathematics Extension 1". This paper is not on your list of papers without a printed name, and the dispatch offered row C4. If you rule it out, remove PP 6 and the total becomes 15 marks, still 25 minutes. The check script needs only the PP 6 block deleted; the structure checks adapt.
2. **Textbook typo kept verbatim.** Ex 14D Q19(c) prints "In doing part B, however, …", where part b is meant. I kept it as printed rather than "correcting" it. It does not affect the maths. Tell me if you would rather omit Q19.
3. **Grid paths.** I added the "An application: paths on a grid" box to Concept 2. It is not in the textbook's 14D teaching pages, but the spec's topic map assigns grid paths to 14D, and PP 10 and PP 11 need it.
4. **Q15(b) wording.** "minimum number of colours needed to guarantee at least 10 000 different patterns" only makes sense with the best split of the marbles among the colours. The book's answer, 4, matches that reading: 3 colours give at most 4200 patterns, and 4 colours give 25200. I kept the question verbatim and did not treat it as doubtful.
