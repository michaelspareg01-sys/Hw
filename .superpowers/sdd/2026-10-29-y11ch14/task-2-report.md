# Task 2 report: Lesson 14A Factorial notation

Status: DONE_WITH_CONCERNS. The concern is that the past-paper mini exam has 9 marks, below 15. House rule 8 allows this, and so does the brief.

Commit: `b47caab Y11Ch14: lesson 14A` on `ch10-pack`. Not pushed.

## What I built

### `workspace/build/y11ch14/l14a.html`
- Lesson head (l.1–3).
- **Concept 1: the definition of n factorial** (l.6)
  - Boxes: "Where factorials come from" (the queue of five, with the `queue5` box figure, and the fifth derivative of x⁵), **Box 1** (informal and recursive definitions, and why the recursive one is better), and "Why 0! = 1" (empty product and empty sum, the 0!–11! table, the calculator button, the domain is the whole numbers).
  - Tutor demo: a queue of 6; the 4th derivative of x⁴; 10! and 8! from 9!.
  - Your turn: 7 runners; the 3rd derivative of x³; 8! and 6! from 7!.
  - The textbook has no numbered example for this part. Its opening discussion (the queue of five and the 5th derivative) is the worked example, labelled "Worked example: From the text". Worked examples 1 and 2 then keep the textbook numbering.
- **Concept 2: unrolling factorials** (l.57)
  - Boxes: unrolling 8!, and **Box 2** (calculating by unrolling factorials).
  - Tutor demo: 9!/6!, (n+3)!/n!, n!/(n−4)!, 8!/(5!3!).
  - Your turn: 11!/8!, (n+4)!/(n+1)!, n!/(n−3)!, 9!/(6!3!).
  - Worked example 1 is textbook Example 1 (10!/7!, (n+2)!/(n−1)!, n!/(n−r)! with the "r factors" underbrace).
- **Concept 3: common denominators and common factors** (l.93)
  - The box covers the largest factorial as the common denominator (Example 2's method).
  - It also covers taking out a common factor. The teaching pages show no example of this, but Exercise 14A Q6 asks for it, and it is unrolling applied to a sum. I flagged this in the box and gave it parts c and d of the demo and the Your turn.
  - Tutor demo: 1/7! − 1/9!, 1/(n+1)! + 1/(n+2)!, 10! − 9!, (n+2)! − (n+1)!.
  - Your turn: 1/6! + 1/8!, 1/(n−1)! − 1/n!, 7! + 5!, n! + (n−1)!.
  - Worked example 2 is textbook Example 2.
- **Textbook homework, Exercise 14A** (l.127): all of Q1–Q14, verbatim, banded as the book bands them: Foundation Q1–6 (l.128), Development Q7–12 (l.142), Enrichment Q13–14 (l.162). Nothing is omitted. All of 14A is in scope, and I found no doubtful item.
  - One spelling fix: in Q1d, the book's "interchangable" is printed as "interchangeable".
- **Past-paper homework** (l.169): 6 questions, 9 marks, 15 minutes. One short note explains why it is shorter than usual. Each question has its source label and one hint.

### `workspace/build/y11ch14/a_14a.html`
- `{{ahead:Lesson 14A | Factorial notation}}`.
- Lesson Examples C1–C3 (l.2).
- Textbook Homework (l.10): every item that has a final answer, which is Q1–8, 9b, 10, 12, 13 and 14. Q11 is left out because it is "show that" only, as is Q9a. I include Q12d because the book prints the collapsing-sum form.
- `{{ahead:...}}` again (l.27), then Past-Paper Homework – Worked Solutions (l.28), with full working and the MC choice explained.
- I solved every textbook answer independently, and all match the book (PDF 938–939).
- Answer labels are kept with their maths by `white-space:nowrap` spans, which are layout only.

### Figures
`figs.py` l.84 `boxes()` and l.100 `fig_14a()` draw `svg/queue5.svg` (lesson Concept 1), `svg/pin4.svg` (PP 1 solution) and `svg/epsilon.svg` (PP 2 solution).

## Sources

**Textbook:** `CSM6_EXT1Y11_book.pdf`. I rendered and read teaching pages and the exercise at PDF 689–693, and the answers at PDF 938 (bottom right) and 939 (left), in halves at zoom 2.

**Past papers** (paths under `workspace/pp/Ext 1/`). Each was checked on the rendered page, along with its cover title:

| PP | Source label (both PDFs) | Marks | File | Question p | Solution p |
|---|---|---|---|---|---|
| 1 | Cherrybrook Technology High School, 2020, Year 12 AP4, Mathematics Extension 1, Q1 (MC) | 1 | `2020/2020 Cherrybrook Tech.pdf` | 3 | 14 (key D, ¹⁰P₄ = 5040) |
| 2 | Ascham School, 2023, Year 12 Trial Examination, Mathematics Extension 1, Q12(e)(i) | 1 | `2023/Ascham 2023 3U.pdf` | 8 | 20 (5! = 120) |
| 3 | Normanhurst Boys High School, 2022, Year 12 Course Assessment Task 4 (Trial Examination), Mathematics Extension 1, Q11(a)(i) | 1 | `2022/Normanhurst Boys 2022 3U Trials & Solutions.pdf` | 5 | 10 |
| 4 | Normanhurst Boys High School, 2021, Year 12 Course Assessment Task 4 (Trial Examination), Mathematics Extension 1, Q11(e)(i) | 1 | `2021/3U NBHS.pdf` | 5 | none in file (my own solution, checked symbolically and numerically) |
| 5 | Sydney Boys High School, 2020, Year 12 Term 3 Trial HSC, Mathematics Extension 1, Q12(c) | 2 | `2020/2020 SBHS 2.pdf` | 8 | 24 (n = 7) |
| 6 | Hurlstone Agricultural High School, 2023, Higher School Certificate Trial Examination, Mathematics Extension 1, Q12(d) | 3 | `2023/Hurlstone 2023 3U.pdf` | 8 | 24 |

All six are recorded under `## 14A` in `docs/pp_selected_y11ch14.md`. None is in `PAST_PAPERS_USED.md` or in any `pp_selected_*.md` (I re-checked just before committing, and also looked at the live `l15a.html` of the parallel Ch 15 task). None is on the controller's banned list.

## Omitted or rejected, and why
- **Killara 2024 Q12(d) (row A5, 3 marks):** it is written in ⁿPᵣ notation, which 14A does not teach. Adding a definition to the stem would change the question, so I left it for 14B and noted that in the selection record.
- **Induction parts NBHS 2021 Q11(e)(ii) and NBHS 2022 Q11(a)(ii):** induction is a Year 12 method, not 14A, as the catalogue says.
- **E6 Killara 2021 Q7 and E26 Hornsby 2023 Q11(e)(i):** both need ⁿCᵣ (14E).
- **Top-up and the 14B pool (concern for the controller):**
  - To reach 9 marks I took two "early 14B-style" items, as the brief allows. They need only the fill-the-places argument from the start of 14A:
    - CTHS 2020 Q1 (PIN, 10×9×8×7)
    - Ascham 2023 Q12(e)(i) (EPSILON starting with P and ending with S, 5!)
  - Ascham (ii) and (iii) stay free for 14C and 14B.
  - I did not take more (for example NBHS 2023 Q3 or Girraween 2020 Q14(c)), because the 14B pool is also thin. Without these two, 14B keeps B2, B3, B5, B6(iii), B7, B8, B9, A5 and the others.
  - If the controller would rather 14B had them, both can come out of 14A, leaving 7 marks.
- **PP 4 has no school solution in its file:** I included it because the pool is thin and the item is clean. My solution is verified by the check script.
- **Doubtful items:** none found in Exercise 14A or in the chosen papers.

## Verification
- **`python3 workspace/checks/y11ch14_14a.py`: 180 checks, all OK, exit 0.**
  - It reads every printed value in `a_14a.html`, and the worked examples, concept boxes and 0!–11! table in `l14a.html`.
  - It re-reads the printed questions for Q2, Q3, Q5, Q6, Q7, C2, C3 and the PP statements, so each answer is tied to the question as printed.
  - Independent sources of truth:
    - counts by `itertools` brute force (queues, PIN with option values for (B) and (C), EPSILON)
    - factorial expressions at n = 4..9 with exact `Fraction`s
    - derivatives with `sympy.diff`
    - prime powers by repeated division of 10! and 100!
    - partial sums and the limit
    - Stirling error, which gives 0.1388% for 60! and confirms the 2.73% and 0.83% in the question
    - every line of the PP 3, 4 and 6 identities
    - PP 5: each line is a nonzero multiple of (n−7)(n+10), and a brute-force search of 0..199 gives n = 7 only
  - Structure checks:
    - the marks sum to the intro (9)
    - the time is 15 = 1.5 × 9 rounded to 5
    - the PP numbering and labels match in both files
    - each PP has one hint
    - the MC letter is D
  - It prints a NOTE that 9 < 15 under house rule 8.
- **Mutation tests:** 11 one-value edits in copies, run through `Y11CH14_SRC`. Each made the script exit 1 with the right MISMATCH: a textbook number, an algebraic answer, a prime power, the MC letter, a PP6 working line, the PP5 answer, a question transcription, the intro marks, a source label, the Stirling percentage, and a worked-example result.
- **Build:** `python3 build.py y11ch14 all && mv lesson.pdf answers.pdf y11ch14/`.
  - qa.py: lesson.pdf 19 pages, 0 problems; answers.pdf 5 pages, 0 problems.
  - MathJax error-text scan: 0 in both.
- **Pages inspected** (contact sheets at 0.62, plus pages at 1.3):
  - lesson pp.5–19, all of 14A: concepts pp.5–10, homework pp.11–17, past papers pp.18–19
  - answers pp.2–5
  - I resized the work boxes to remove half-empty pages and spaced out the fraction rows. Page 9 still has about a quarter of the page blank, because the next demo block cannot be split.

## Files changed
- `workspace/build/y11ch14/l14a.html`, `a_14a.html`, `figs.py` (14A block only), `svg/queue5.svg`, `svg/pin4.svg`, `svg/epsilon.svg`
- `workspace/checks/y11ch14_14a.py`
- `docs/pp_selected_y11ch14.md`

## Other concerns
- Early on I ran `rm -f` on `l*.png` and `a*.png` in the shared scratchpad folder `img/`. That may have removed contact-sheet PNGs that another agent had left there. They are scratch images and can be regenerated with `sheet.py`. After that I used `img/t14a/` only.

## Fix round 1

### What changed (`workspace/build/y11ch14/l14a.html`)
1. **[Important] Clipped maths on lesson p.7.** In the "Worked example: From the text" block, the last aligned line is now split in two: `y^{(5)}&=5×4×3×2×1` and then `&=5!=120.` The block keeps its two columns and all of its content. The p.7 crop at zoom 2 shows nothing passing the box edge. The check template in `workspace/checks/y11ch14_14a.py` now matches the split line.
2. **[Minor] Hints that gave away a step (house rule 4).**
   - PP 6 now reads: "unroll each factorial down to the smallest one."
   - PP 5 had the same problem, so I changed it too. The old hint was "unroll (n+2)! until n! appears, then cancel n!". The new one is "unrolling turns this into an ordinary equation in n. Remember what values n is allowed to take."
3. **[Minor] Ex 14A Q13 layout.** The parts row now uses columns that size to their content (`grid-template-columns:auto auto auto; justify-content:space-between`). Each part span has `white-space:nowrap`, so the labels a, b and c each sit beside their expression. My first attempt fixed c but made a and b wrap, and this version fixes all three. The p.16 crop at zoom 2 confirms it.

### Verification
- `python3 workspace/checks/y11ch14_14a.py`: 180 checks, all OK, exit 0. The only other output is the usual house rule 8 NOTE.
- I rebuilt with `python3 build.py y11ch14 all && mv lesson.pdf answers.pdf y11ch14/`.
  - qa.py: lesson.pdf 19 pages, 0 problems; answers.pdf 5 pages, 0 problems.
  - MathJax error scan: 0 in both.
- I inspected crops of lesson p.7 (zoom 2), p.16 (zoom 2) and p.19 (zoom 1.3, the PP 5 and PP 6 hints). The page count is unchanged.
- Scratch images are in `scratchpad/work/y11ch14-t2/`. I deleted nothing.

### Files and commit
- Files: `workspace/build/y11ch14/l14a.html`, `workspace/checks/y11ch14_14a.py`.
- Commit: "Y11Ch14: lesson 14A fix round 1". I did not touch `workspace/build/y11ch15`.
