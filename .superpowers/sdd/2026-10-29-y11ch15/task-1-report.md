# Task 1 report: Y11 Ch 15 pack scaffold, cover and revision

Commit: e9bdc7c "Y11Ch15: scaffold, cover, revision" on branch ch10-pack (not pushed). Only the 15 files below were staged.

## Built
- `workspace/build/y11ch15/pack.json`: lesson parts cover, revision, l15a-l15d; answers parts a_rev, a_15a-a_15d. Footer "Year 11 Chapter 15 Binomial Theorem | Lesson and Homework" / "... | Homework Answers"; answers heading "Chapter 15 Binomial Theorem - Homework Answers" (fits one line in the render).
- `cover.html`: title "Year 11 Chapter 15 / The Binomial Theorem" (two balanced lines). Rows: Revision "Counting and index laws" (note "Year 11 · Ch 14, indices"); Lessons 15A "Binomial expansions and Pascal's triangle", 15B "Further binomial expansions", 15C "The binomial theorem", 15D "Identities in Pascal's triangle" (titles confirmed on book PDF 741, 749, 752, 758) each with `Past papers: @@M15A@@`...`@@M15D@@`; Review "Chapter 15 review exercise". Same closing paragraph as Ch 14.
- `revision.html` (2 pages, both full): summary boxes (a) factorials and nCr from Ch 14 (14A/14E: definition as number of r-member subsets, "n choose r", formula both forms, worked 8C5 = 56 from the book's Ex 15, symmetry nCr = nC(n-r), 2^n total, nCr as word count with the xxyy = 4!/(2!2!) = 6 link used in 15C), (b) index laws incl. negative and fractional indices, sign and (2x)^3 warnings, 3/x^2 = 3x^-2, (c) expanding brackets (binomial definition as in 15A, square identities, term-by-term with (1+x)^3 built one bracket at a time, coefficient and constant term). Warm-up of 5 questions (factorial/nCr values; nC1, nC2 in n and solve nC2 = 45; index-law simplification incl. (-2/x)^3 and 8^(-2/3); expansions incl. coefficient in a product; arrangements of AAABB as 5C2).
- `a_rev.html`: answers with working for all five questions, parts on separate lines.
- `figs.py` (copy of the Ch 14 header, no figures), `svg/.gitkeep`, placeholders `l15a-d.html` ("<!-- filled by Task 2..5 -->") and `a_15a-d.html`.
- `workspace/checks/y11ch15_rev.py`.

## Sources
Y11 book PDF 741-743 (15A: expansion of (1+x)^n, Pascal properties, Examples 1-3), 752-753 (15C: binomial theorem box 3, nCr formula, Example 9), and for Ch 14 wording PDF 712-714 (14E: box 12 "Counting the subsets of a set", Example 15, canonical correspondence). No past papers in this task.

## Layout decisions (from the Ch 14 review)
- No partly empty revision pages: revision is exactly 2 pages (summary page, then warm-up page filled to within a few mm of the footer by sizing `{{work:NN}}` 24/21/26/32/20). Ch 14 had 3 pages with a short last one.
- No card-suit glyphs anywhere (scanned the PDF text for the four suit characters: none). No card question used.
- Warm-up parts on separate lines (`.parts one`); answer parts separated with `<br>`, not run-on `&nbsp;`.

## Omitted / doubtful
Nothing omitted. The page assumes nothing from 15E. The Pascal addition property and the 2^n sum proof are left to 15A/15D; 2^n and nCr symmetry appear in revision only as the Ch 14 results they are (box 12, 14E).

## Verification
- `python3 workspace/checks/y11ch15_rev.py`: 85 printed values checked, 0 failures. It reads the answers from a_rev.html and the givens from revision.html (hence rebuilt expectations if the givens change); each template or regex must match exactly once; printed algebra chains (e.g. `(2x-3)^2 = 4x^2-12x+9`, `8^{-2/3} = 1/8^{2/3} = ... = 1/4`) are parsed with sympy and every link compared with an independent value; counting by itertools (permutations of AAABB = 10, 2-subsets of positions = 10), `math.comb`, brute force n with C(n,2) = 45.
- Mutation test: 8 deliberately wrong printed values (84->83, 8x^6->8x^5, 22->21, n=10->11, -1 -> 1, 10 arrangements -> 12, 4x^2-12x+9 -> 4x^2-6x+9, 1/4 -> 1/2) each gave exit 1.
- Build `python3 build.py y11ch15 all && mv lesson.pdf answers.pdf y11ch15/`: lesson.pdf 3 pages (cover + 2 revision), answers.pdf 1 page. `qa.py`: 0 problems on both.
- MathJax scan (PyMuPDF text for Double subscripts, Double superscripts, Undefined control sequence, Missing, Extra }, Misplaced, Math input error): 0 on both PDFs.
- Looked at every page (cover, revision summary, warm-up, answers); nothing clipped, no stranded heading, no half-empty page. PDFs and lesson.html/answers.html are git-ignored.

## Files changed
workspace/build/y11ch15/{pack.json, cover.html, revision.html, a_rev.html, figs.py, svg/.gitkeep, l15a-d.html, a_15a-d.html}; workspace/checks/y11ch15_rev.py.

## Concerns
- The cover's `@@M15A@@`...`@@M15D@@` markers are left for the lesson tasks to replace with mark totals (same as Ch 14). The Task 2-5 implementers must also fill them in cover.html, which is owned by Task 1; flag to the controller.
- Revision page 1 is tight: the third summary box just fits. Adding text to the summary boxes would push the Expanding brackets box onto a new page.
