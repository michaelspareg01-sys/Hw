# Task 1 report: pack scaffold, cover and revision

Status: DONE. Commit `ea82a81` "Y11Ch14: scaffold, cover, revision" on branch `ch10-pack` (not pushed).

## What was built (all under `workspace/build/y11ch14/`)
- `pack.json`: lesson parts `cover, revision, l14a..l14f`; answers parts `a_rev, a_14a..a_14f`; outputs `lesson.pdf`/`answers.pdf`. Footer "Year 11 Chapter 14 Combinatorics | Lesson and Homework" (lesson) and "... | Homework Answers" (answers); answers heading "Chapter 14 Combinatorics - Homework Answers" (fits one line on the rendered page).
- `l14a.html`..`l14f.html` (comments "filled by Task 2..7") and `a_14a.html`..`a_14f.html` (same task numbers): placeholders, so the pack builds.
- `cover.html`: Ch 10 structure; h1 "Year 11 Chapter 14 / Combinatorics"; rows Revision (Probability basics, "Advanced · Year 11"), 14A-14F with textbook titles and notes `Past papers: @@M14A@@ ... @@M14F@@` (left for Task 8 to fill), Review. House intro paragraph with the vector/g sentences removed.
- `revision.html`: lesson-head "Probability basics" plus four summary boxes (sample space/equally likely/P(E)=|E|/|S| with pack-of-cards facts; complements and "at least one"; sets, and/or, addition rule, mutually exclusive; multi-stage product rule, without replacement, multiplication principle as the lead-in to Ch 14), then a 5-question warm-up (die with "even or multiple of 3"; cards a-d; class soccer/tennis Venn; four coin tosses; bag draw without replacement).
- `a_rev.html`: warm-up answers with working, in the a_rev_9e style.
- `figs.py`: Ch 10 header (imports, `save`, `Fig` class) with an empty `__main__`; `svg/.gitkeep` so the folder is tracked.
- `workspace/checks/y11ch14_rev.py`: reads every printed value in `a_rev.html` (templates must match exactly once; missing -> FAIL; exit 1 on failure) and the givens of Q3 and Q5 from `revision.html`; recomputes by brute force (itertools product/permutations over a 52-card deck, coin sequences, ordered disc draws, explicit sets).

## Source pages used
- Y11 book (PDF = printed + 24): PDF 689-690 (14A start: queue/product intro, n! definition, Example 1) and 720-721 (14F: sample space and event space counting, Examples 21-22) to see what 14A-14F assume. Probability prerequisites from this book's Chapter 12: PDF 583-585 (12A: equally likely outcomes, basic formula, sample/event space, |E|/|S|, complement box), 599-601 (12C: and/or/not as sets), 607-610 (12D: mutually exclusive, addition rule, complement with and/or), 614, 616-617 (12E: product rule, independence, without replacement, listing outcomes).
- 14F assumes: P(E)=|E|/|S|, uniform sample space, ordered vs unordered sample space, "at least", product rule for digits, and the 52-card pack. All appear in the revision boxes.

## Omitted or rejected
- No past-paper content (not part of this task). Nothing doubtful found.
- Tree diagrams, Venn diagrams and sample-space graphs were not drawn in the revision (no figures were required, and the Q3 Venn is solved with counts).
- `@@M14A@@`..`@@M14F@@` remain on the cover on purpose; `build.py` does not expand them and Task 8 fills them.

## Verification
- `python3 workspace/checks/y11ch14_rev.py`: 57 printed values checked, 0 failures, exit 0. Mutation test (a copy of `a_rev.html` with 15/28 changed to 14/28, via `Y11CH14_SRC`): FAIL reported, exit 1.
- Build: `cd workspace/build && python3 build.py y11ch14 all && mv lesson.pdf answers.pdf y11ch14/` succeeded.
- `qa.py`: lesson.pdf 4 pages, 0 problems; answers.pdf 1 page, 0 problems.
- MathJax error-string scan of both PDFs (PyMuPDF text): 0 hits.
- Pages inspected: lesson pp 1-4 (cover, revision summary page, product-rule box + warm-up Q1-2, warm-up Q3-5) and answers p 1. One layout fix made after the first look: the addition rule moved to a display so it no longer wraps awkwardly. Page 4 is about 40 percent full (warm-up Q3-5); acceptable.

## Files changed
`workspace/build/y11ch14/*` (pack.json, cover, revision, a_rev, l14a-f and a_14a-f placeholders, figs.py, svg/.gitkeep) and `workspace/checks/y11ch14_rev.py`. Build outputs (pdf, lesson.html, answers.html) are git-ignored. `docs/` untouched.

## Concerns
- None blocking. The house-rules Git section names the old "Claude Opus 5.5" attribution; the commit uses the attribution lines given for this session ("Claude Sonnet 5.5").
