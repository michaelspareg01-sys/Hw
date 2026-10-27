# Handover prompt: Year 12 Maths Extension 1 lesson packs

Paste everything below the line into a new session, and attach or unzip `Y12_Ext1_Lesson_Packs_Handover.zip` first.

---

You are continuing a tutoring project. The aim is to build NSW Year 12 Mathematics Extension 1 lesson packs, **one chapter per PDF pair**:

- `Year_12_Ext1_ChXX_<Topic>_Lesson_and_Homework.pdf`
- `Year_12_Ext1_ChXX_<Topic>_Homework_Answers.pdf`

Three chapters are finished: Ch 11 Trig Equations, Ch 12 Further Calculus and Ch 13 Differential Equations (in `finished_pdfs/`). Ch 8 Vectors was made earlier by the owner. `sources/Year_12_Ext1_Ch8_Vectors_Homework_Answers.pdf` is the style sample they liked.

## Remaining order (do these next, in order, without asking for approval between chapters)
1. **9E + Ch 10 Rates and Projectile motion.** Open with a short review of Advanced 9A–9C (motion), then teach 9E (related rates, Ext 1), 10A and 10B. This is one PDF pair.
2. **Y11 Ext 1 Ch 14 Combinatorics** (14A–14F; skip 14G and 14H unless asked), taught at full Year 12 lesson depth. Source: `sources/CSM6_EXT1Y11_book.pdf`.
3. **Y11 Ext 1 Ch 15 Binomial theorem** (15A–15D; 15E is enrichment, so skip it).
4. **Y11 Ch 13 Discrete probability distributions** (13A–13D; keep 13D Sampling, as it sets up 17D).
5. **Y12 Ch 17 Binomial distributions** (17A–17D). Open with a short review of Advanced Ch 16 (normal distribution).

Y12 textbook: `Math Textbook CMS6 Ext1 Y12.pdf`, inside `sources/Tutoring_All_Source_Files.zip`. The PDF page number is roughly the printed page + 26. There is also a full text dump at `workspace/txt/y12.txt`, with pages split by form feeds.

## Owner's rules (all confirmed by the owner)
- **Scope:** Ext 1 topics only, plus short Advanced or Year 11 reviews where they are prerequisites. This overrides the "Advanced only" default in `READFIRST-Y12.md`. Otherwise follow READFIRST: tutor demo, then your turn, then a worked example for each concept, with textbook homework banded Foundation / Development / Enrichment.
- **Length:** one PDF per chapter, however many lessons that takes. There is no page cap; cover the whole chapter.
- **Past papers:**
  - Use real school trial papers only, from `sources/Ext 1-...zip` (2020–2024). Commercial papers (NEAP, PEM, TEC/Total Education, Bored of Studies, CSSA, Independent) are saved for later, so don't use them.
  - Repeating a school is fine. Aim for about a 30-minute mini exam per lesson (roughly 15–22 marks), and choose good questions.
  - Show the source (school, year, paper title, question number) in both PDFs, with a hint under each question in the lesson PDF and full worked solutions in the answers PDF.
  - Don't reuse questions already used. The list is in `PAST_PAPERS_USED.md`.
- **No tutor-notes PDF:** the owner said it isn't needed.
- **Doubtful items:** if a textbook or past-paper item looks wrong, **don't claim it's wrong and don't "correct" it**. Quietly use a different question instead.
- **Checking:** solve every answer yourself and check it numerically. Render the PDF pages and look at them before delivering.
- **Workflow:** keep going chapter after chapter. Send each chapter's PDFs to the user when done, and copy them to the owner's `Downloads\Y12 Ext1 Lesson Packs\`.

## Build kit (`workspace/`)
- `build/build.py <chapter_dir> [lesson|answers|all]` reads `<chapter_dir>/pack.json` (copy the format from `build/ch13/pack.json`). It assembles the HTML fragments and prints them to PDF with headless Chrome (`build/print.mjs`, which needs Node 18+ and Chrome at `C:/Program Files/Google/Chrome/Application/chrome.exe`; edit the path if yours differs).
- Fragments are HTML with MathJax `\( \)` and `\[ \]`. Macros: `{{sec:accent:icon:Title:sub}}`, `{{work:mm}}` (blank answer box), `{{band:F|D|E}}`, `{{svg:name}}` (inserts `<chapter>/svg/name.svg`), and `{{ahead:Label}}` (answers section heading). Copy the structure of `build/ch13/*.html` exactly: the cover, `revision.html`, one `lNNx.html` per lesson (the last also holds the chapter review), and `a_*.html` for the answers.
- `build/<ch>/figs.py` generates the SVG diagrams using `build/plots.py`. `Graph` has methods for curves, fills, slope fields, labels and dots.
- `tools/`:
  - `qa.py file.pdf` flags raw LaTeX.
  - `sheet.py file.pdf prefix` makes two-page contact sheets for visual checks.
  - `render.py` and `renderclip.py` render textbook or paper pages to PNG so you can read them.
  - `ppfind.py outdir tag "YEAR/paper.pdf" "search text"` finds and renders a past-paper page. It expects the trial papers unzipped to `workspace/pp/Ext 1/`.
  - `roots.py` is a numeric root finder for checking answers.
- Python 3.10+ with `pymupdf`, plus poppler (`pdftotext`). Run Python on the source PDFs with `-I`.

## First steps
1. Unzip `sources/Ext 1-...zip` into `workspace/pp/` (giving `workspace/pp/Ext 1/2020/...`). Unzip `sources/Tutoring_All_Source_Files.zip` into `workspace/zip/`.
2. Run a test build of `build/ch13` to check that the toolchain works.
3. Start the 9E + Ch 10 pack.
