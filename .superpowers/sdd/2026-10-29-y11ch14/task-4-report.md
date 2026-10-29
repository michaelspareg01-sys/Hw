# Task 4 report: Lesson 14C Ordered selections and grouping

Status: DONE_WITH_CONCERNS (one small concern, see the end). Commit `fbb43b1` "Y11Ch14: lesson 14C" on `ch10-pack`. Not pushed.

## What I built
`workspace/build/y11ch14/l14c.html` (replaces the placeholder):
- Lesson head (l.1-3): the three new principles. The only lesson reference is back to Lesson 14B. No forward references.
- Concept 1, grouping (l.6-31): the textbook's compound-ordering text, a new figure `{{svg:groups9}}` showing the five groups of Example 9, Box 8. Tutor demo: (a) a queue of 5 boys and 3 girls with a couple and a pair of girls, (b) CAMPING with the vowels together. Your turn: (a) 3 boys and 3 girls, (b) TRAIN. Worked example 9 is the textbook example with its box table (l.24-31).
- Concept 2, the complementary situation (l.33-53): the textbook text, plus a note on using it for members that must be "apart". Tutor demo: (a) A–F with the vowels separated, (b) nine people with two not next to each other. Your turn: (a) A–E, (b) six people. Worked example 10 is the textbook example (l.46-53).
- Concept 3, using cases (l.55-85): the textbook text, Box 9, and the set form \(|A\cup B|=|A|+|B|-|A\cap B|\). The textbook cites "Section 12C, Box 12", so I point to the addition rule on the revision page instead. Tutor demo: (a) the Example 11 type with no overlap (odd > 600 or multiples of 5 < 300), (b) the same with an overlap (odd > 300 or multiples of 5 < 600), (c) digits 2, 3, 5, 7 used at most once, at least 500. The Your turn is parallel. Worked example 11 is the textbook example, parts a and b (l.76-85).
- Textbook homework (l.86-134): Exercise 14C Q1–22 verbatim, banded F 1–7, D 8–21, E 22. Every question is included and every part is on its own line (`.parts one`). Nothing was omitted: no part of 14C is in 14G or 14H, and nothing in it is doubtful. One spelling fix is in the teaching prose only: the textbook's "orerings" is printed as "orderings".
- Past-paper homework (l.135-196): 10 questions, 15 marks, 25 minutes (1.5 × 15 = 22.5, rounded half up).

`workspace/build/y11ch14/a_14c.html`: ahead line; Lesson Examples C1–C3; Textbook Homework 1–22, all matching the textbook answers on PDF 939–940 (22b is an "explain why" and has no answer); a second ahead line; the past-paper worked solutions. MC solutions explain the choice and the tempting wrong options.

`figs.py`: I added `fig_14c()` (the `groups9` box diagram) and a call to it in `__main__`. The existing figures are unchanged, and their SVGs rebuilt byte-identical.

## Sources
- Textbook: Y11 book PDF 702–705, which hold the 14C teaching (Box 8, Example 9, the complement principle, Example 10, Box 9, Example 11) and Exercise 14C. I also rendered PDF 706 to confirm where Q22 ends. Answers are on PDF 939 (bottom right) and 940 (top left), rendered in halves at zoom 2.
- Past papers. Each was verified on the rendered question page and cover, and against the school solution or key where one exists. All were also brute-forced.

| PP | Label (school, year, title as printed, Q) | Marks | File | Question p → solution p |
|---|---|---|---|---|
| 1 | Abbotsleigh, 2020, Higher School Certificate Assessment 4 Trial Examination, Mathematics Extension 1, Q1 | 1 (MC) | `2020/2020 Abbotsleigh (No Solutions).pdf` | p3 → none (solved independently: 4320, C) |
| 2 | James Ruse Agricultural High School, 2020, Year 12 Trial HSC Examination, Mathematics Extension 1, Q3 | 1 (MC) | `2020/James Ruse 2020 3U Trials & Solutions.pdf` | p2 → p10 (key D) |
| 3 | Abbotsleigh, 2023, Higher School Certificate Assessment 4 Trial Examination, Mathematics Extension 1, Q9 | 1 (MC) | `2023/Abbotsleigh 2023 3U Trials & Solutions.pdf` | p7 → p18 (handwritten, C) |
| 4 | James Ruse Agricultural High School, 2023, Year 12 Trial HSC Examination, Mathematics Extension 1, Q10 | 1 (MC) | `2023/Ruse 2023 3U.pdf` | p5 → p13 (key D) |
| 5 | Caringbah High School, 2020, Higher School Certificate Trial Examination, Mathematics Extension 1, Q10 | 1 (MC) | `2020/2020 Caringbah.pdf` | p4 → p12 (key D) |
| 6 | North Sydney Girls High School, 2020, HSC Trial Examination, Mathematics Extension 1, Q11(d) | 2 | `2020/2020 NSG.pdf` | p6 → p16 |
| 7 | Pymble Ladies’ College, 2024, HSC Trial Examination Term 3, Mathematics Extension 1, Q11(b) | 2 | `2024/Pymble Ladies College 3U.pdf` | p5 → none (solved: 30 240) |
| 8 | Ascham School, 2023, Year 12 Trial Examination, Mathematics Extension 1, Q12(e)(ii) | 1 | `2023/Ascham 2023 3U.pdf` | p8 → p20 |
| 9 | Sydney Technical High School, 2021, Trial HSC, Extension 1 Mathematics, Q11(c) | 2 | `2021/3U Sydney Tech.pdf` | p6 → p12 (headed "Common Test Assessment 4 2019", but the working is for this question: 15/34) |
| 10 | Blacktown Boys’ High School, 2023, Year 12 Trial Examination, Mathematics Extension 1, Q12(c)(i)(ii) | 3 | `2023/Blacktown Boys 2023 3U.pdf` | p8 → p24 (uses nCr; I use ordered selections, with the same answers 7/66 and 91/330) |

All ten are recorded in `docs/pp_selected_y11ch14.md` under `## 14C`. I re-read all of `docs/pp_selected_*.md` (ch10, y11ch14, y11ch15) and `docs/PAST_PAPERS_USED.md` just before committing, and none of these items appears in them.

## Past-paper choice and the catalogue sweep (house rules 7 and 8)
The clean items tagged 14C-only are C1, C2, C3, C6, C7, C8 and C11, worth 9 marks. To reach 15 marks I swept the whole catalogue for items that the 14A–14C methods can solve:
- **Taken from other tags**: F2 (dice, cases), F8 (at least one heart, complement) and F14 (batteries, ordered selections and complement). They use only ordered counting, cases or complements, with P(E) = |E|/|S| and the complement rule from the revision page. This follows the 14B precedent of HAHS CONSIDER. Plenty is left for 14F: F3, F7, F9–F13, F15 and others.
- **Not taken, because they need identical elements (14D is not yet taught)**: C4 EXTENSION (the N repeats), C5 and C9 STATISTICS, and C10 PROBABILITY (the I's repeat; it also has the Y-as-consonant flag). D1 (SBHS chairs) could be forced through 14B boxes, but it is a natural 14D item and 14D is tight, so I left it.
- **Not taken, because they need nCr (14E)**: every E row, B8 Hurlstone Q10, E31, and F3/F7/F9–F13/F15.
- **Not taken, because of a controller ruling or doubt**: NSB 2024 (B4), Western 2020 (F17), Fort Street 2023, STHS Sample 1 Q8 (F18), James Ruse 2020 Q14(c) (F4). STHS 2020 Sample 2 Q14(c)(i) (B10) was left out because the sample-paper stem is a sentence fragment ("A four letter employee password from the letters …") and its part (ii) is banned. F16 (BHHS 2023, P(sum of 7)) was left out as a trivial Advanced item that sits inside a binomial question.
- **Extra sweep beyond the catalogue**: I scanned the text layer of every school paper from 2020 to 2024 for together, next to, adjacent, apart, separated, alternate, consecutive, immediately, arrange and queue. The only new hits were circle items (NBHS 2021 Q11(a)(ii), BHHS 2023 Q11(b), Killara 2024 Q11(c)), and these are out of scope. Script and output: `.../scratchpad/work/y11ch14-t4/scripts/scan.py`, `scan.txt`.
- **The 15th mark**: C7 (Ascham, EPSILON vowels adjacent, the number) and C8 (James Ruse 2023, the same count as an MC expression) are the same problem. The catalogue says "use one", but they are the only two clean 14C rows left, and without both the exam reaches only 14 marks. So I used both, kept them apart (PP 4 and PP 8), and the PP 8 hint says "compare with PP 4". If the reviewer prefers variety, dropping PP 8 gives 14 marks and 20 minutes, which rule 8 permits.

Hints give a starting idea only, for example "seat the boys first. Where can the girls then go?" and "count the complementary situation."

## Verification
- `python3 workspace/checks/y11ch14_14c.py` → **209 checks, all OK**, exit 0, about 2 s.
  - It reads every printed result in `a_14c.html`: C1–C3, TB 1–22, and every number in every PP working line, including each '=' piece of every chain and each term of a sum such as 350+120−30.
  - It also reads the results in the l14c concept boxes and Worked examples 9–11, and the figure labels.
  - Each value is compared with brute-force itertools enumeration of the actual people, letters, digits, dice, cards and batteries: 8!, 9! and 7^7 are enumerated in full.
  - Where full enumeration is too big, it uses a method that it first checks against full enumeration on a smaller case: the 13-book shelf (Q4) by subject patterns, and 10 people (Q16a) by the places of the named people. Q16b's formulas are checked for n = 3 to 8.
  - It also checks the structure: marks sum, time, numbering, labels identical in both files, one hint each, part marks, and each MC letter.
  - A mutation test changed four printed values (WE11 total, C1 a factor, D(7), PP7). All four were caught and the script exited 1.
- Build: `cd workspace/build && python3 build.py y11ch14 all && mv lesson.pdf answers.pdf y11ch14/`.
- `qa.py`: lesson.pdf has 56 pages and 0 problems; answers.pdf has 15 pages and 0 problems.
- MathJax error scan (PyMuPDF get_text, all 7 strings): 0 in both PDFs.
- Pages inspected:
  - Lesson PDF pp. 39–56 (all 14C pages), on contact sheets and with close-ups of the figure and PP 10. I measured each page's free space with a script and tuned the work boxes. Every homework and PP page now has 1–9 mm free. The lesson pages have at most 36 mm free; p43 has 34 mm because it is the last page before the homework page break.
  - Answers PDF pp. 11–15. Page 12 is half empty because the `{{ahead}}` heading starts the past-paper section on a new page, as in 14B.

## Files changed
`workspace/build/y11ch14/l14c.html`, `a_14c.html`, `figs.py`, `svg/groups9.svg` (new), `workspace/checks/y11ch14_14c.py` (new), `docs/pp_selected_y11ch14.md` (appended `## 14C`). Only these were staged, by explicit path. The PDFs are ignored by git (`*.pdf`).

## Concerns
- PP 4 and PP 8 are the same EPSILON count, as explained above.
- Three PP items are probability items: PP 5, PP 9 and PP 10, rows F2, F8 and F14. The 14F implementer should know these are taken.
- No doubtful textbook items were found in 14C. The textbook answers all agree with brute force.

---

# Fix round 1 (commit `7f854b4` "Y11Ch14: lesson 14C fix round 1")

## Changes
1. **Removed James Ruse 2023 Q10** (catalogue C8). This was the EPSILON expression MC. In my numbering it was PP 4, not PP 8: PP 8 was Ascham 2023 Q12(e)(ii). The ruling names the question as "James Ruse 2023 Q10" and calls it the near-duplicate. The catalogue also names C8 as the "use one, not both" partner. So I removed James Ruse 2023 Q10 and kept Ascham Q12(e)(ii). Keeping Ascham also adds a short-answer item after the MCs. If the controller meant the Ascham item instead, swap the two: the marks and time do not change.
2. **Removed STHS 2021 Q11(c)** (catalogue F8). Its line is deleted from `docs/pp_selected_y11ch14.md`, which leaves it free for 14F.
   - The new set has 8 questions, 12 marks and 20 minutes (1.5 × 12 = 18).
   - New order: PP 1 Abbotsleigh 2020 Q1, PP 2 JRAHS 2020 Q3, PP 3 Ascham 2023 Q12(e)(ii), PP 4 Abbotsleigh 2023 Q9, PP 5 Caringbah 2020 Q10, PP 6 NSG 2020 Q11(d), PP 7 PLC 2024 Q11(b), PP 8 BBHS 2023 Q12(c).
   - PPs are renumbered in both files. The .pp-intro line now reads 20 minutes and 12 marks.
   - The .small note now says the exam is a little shorter than usual. It also says PP 5 and PP 8 are the probability questions, which combine 14B/14C counting with P(E)=|E|/|S|. Both claims are true.
   - The Ascham solution no longer cross-refers to the removed item, and its hint is now "first pick out the vowels of EPSILON".
   - `pp_selected` records the rule 8 shortfall: the reviewer re-scanned every paper and found no other clean 14C item, and the remaining rows need 14D. It also lists both removed items as free.
3. **Hints**:
   - PP 5 (Caringbah) now reads "which of the scores 1 to 6 are perfect squares themselves?"
   - PP 8 (BBHS) now reads "start with part (i): what must be true of all four batteries that the teacher selects?"
   - Neither gives the case split or the modelling choice.
4. **BBHS solution**: I added a sentence explaining the equivalence. Each choice of an unordered pair for each remote matches exactly 2!×2! = 4 ordered selections, so every count and the total are 4 times the unordered ones, and the 4 cancels. The check script verifies this. It enumerates the unordered pairs and confirms they give the same 7/66 and 91/330, and it confirms the factor 4 = 7920/1980.
5. **Lesson p41 stray arc**: Concept 3 now begins with `<div class="page-break"></div>`, so its heading box never splits. The p41 bottom was checked at zoom 1.5 and is clean. The layout is otherwise unchanged.
6. **Source labels**: every PP label in both files now joins "Extension&nbsp;1,&nbsp;Q…", so the Q number never sits alone on a line. The labels are still identical in both files, and the check script confirms this.

## Work boxes
The PP section now fills 4 pages (lesson pp. 52–55); it was 5. The lesson PDF is now 55 pages. I retuned the PP 3, PP 4 and PP 8 boxes. Every PP page is filled except p52, which has about 45 mm free. PP 2 does not fit on p52 when the boxes grow by even 10 mm, so I kept p52 as it is.

## Check script
`y11ch14_14c.py` was updated:
- PP blocks are renumbered, and the checks for the two removed items are deleted.
- New checks: no trace of either removed item remains in either file; the intro note's claims are true; the Ascham block has no cross-reference; the BBHS unordered-model result matches.
- The marks check now expects 12. It prints a rule 8 NOTE, as the 14B script does. The time check is 20 min.

## Verification
- `python3 workspace/checks/y11ch14_14c.py` → 205 checks, all OK (exit 0).
- `y11ch14_14a.py` → 180 checks, all OK. `y11ch14_14b.py` → 218 checks, all OK.
- Build: `python3 build.py y11ch14 all && mv lesson.pdf answers.pdf y11ch14/`.
- qa.py: lesson.pdf has 55 pages and 0 problems; answers.pdf has 15 pages and 0 problems.
- MathJax scan: 0 in both PDFs.
- Pages inspected:
  - Lesson pp. 41–44 (the Concept 3 break and the bottom of p41, zoomed), and pp. 52–55 (all PP pages).
  - Answers pp. 13–15 (all PP solutions).

## Files
`workspace/build/y11ch14/l14c.html`, `a_14c.html`, `workspace/checks/y11ch14_14c.py`, `docs/pp_selected_y11ch14.md`. Only these were staged. The Ch 15 files that show as modified belong to another agent and are untouched.
