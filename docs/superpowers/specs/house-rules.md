# House rules for every lesson pack (binding on all chapters)

Owner rules come from `docs/HANDOVER_PROMPT.md` (owner-confirmed; overrides `docs/READFIRST-Y12.md` where they differ). These rules were confirmed in the Ch 10 pack and its reviews.

## Pack shape
- One PDF pair per chapter: `<Name>_Lesson_and_Homework.pdf` and `<Name>_Homework_Answers.pdf`. No tutor-notes PDF. No page cap; cover the whole chapter scope.
- Fragments live in `workspace/build/<chdir>/`: `cover.html`, `revision.html`, one `l<sec>.html` per lesson (the last lesson file also holds the chapter review), and answer fragments `a_*.html`; `pack.json` lists them. Figures: `<chdir>/figs.py` → `<chdir>/svg/*.svg`, inserted with `{{svg:name}}` (helpers `Fig` and `Graph`: copy `workspace/build/ch10/figs.py` header).
- **Copy the structure of the finished, reviewed Ch 10 pack exactly**: `workspace/build/ch10/` (cover, revision, l09e/l10a/l10b, a_rev_9e/a_10a/a_10b, pack.json). Macros: `{{sec:accent:icon:Title:sub}}`, `{{work:mm}}`, `{{band:F|D|E}}`, `{{svg:name}}`, `{{ahead:Label}}`. Vectors `\tv{i}`.
- Each lesson: lesson-head (eyebrow, h2, focus) → Concepts from the textbook teaching part with **no omissions** (definitions, boxes, derivations, warnings, every distinct method) → for each concept: Tutor demo (close value-changed variant of a textbook example) → Your turn (parallel, equal or slightly easier) → Worked example(s) to keep (usually the textbook example itself, full working) → Textbook homework (the textbook exercise transcribed verbatim, banded Foundation / Development / Enrichment exactly as the textbook bands it; questions may be omitted only if off-scope, and the omission noted in the report) → Past-paper homework mini exam.
- Revision page: short summary boxes of prerequisites + a 4–6 question warm-up (answers in the answers PDF).
- Chapter review exercise at the end of the last lesson file, in-scope questions only.
- Answers PDF: warm-up; per lesson: Lesson Examples (C1, C2… entries: tutor demo + your-turn answers), Textbook Homework (only items with a final answer; "show that" items omitted unless the textbook gives a result), Past-Paper Homework – Worked Solutions (full working); then the review answers.

## Past papers
1. Real **school** trial papers only from `workspace/pp/Ext 1/2020`–`2024`. Never NEAP, PEM, TEC/Total Education, Bored of Studies, CSSA, Independent.
2. Never reuse a question in `docs/PAST_PAPERS_USED.md` or in ANY `docs/pp_selected_*.md` file (other chapters are being built in parallel; re-read them all just before choosing and again before committing), and never use one twice within a pack (track in `docs/pp_selected_<chdir>.md`). Different subparts of one question may be split across lessons if the later part's needed results are supplied in its stem. Repeating a school is fine.
3. About a 30-minute mini exam per lesson, **15–22 marks** (count only included parts), accessible → demanding, varied (include an MC or short item where available). Keep original marks. `.pp-intro` line: time ≈ 1.5 × marks rounded to 5 min.
4. Source label on every question in BOTH PDFs: `School name, year, paper title as printed on the cover, Q(sub)`. One hint per question in the lesson: a starting idea, never a step of the answer. Full worked solutions in the answers; for MC explain the choice.
5. Fidelity: original wording, values, units, conditions, marks, diagrams (recreate as SVG). Nothing included may depend on an omitted part unless its result is supplied.
6. **Doubtful items** (textbook or past paper: a typo, missing condition, inconsistent data, wrong printed answer): never claim it is wrong and never "correct" it in student material. Quietly use a different question. Report it to the controller.
7. Methods within the taught course up to this lesson (Ext 1 + Advanced prerequisites).
8. If a lesson genuinely has too few clean school-paper questions to reach 15 marks, use what exists (minimum one question), say so in the report; do not pad with commercial papers or invented questions.

## Correctness
- Solve every answer independently. Compare with the textbook answers / school solutions. Write a check script `workspace/checks/<chdir>_<part>.py` that **reads the printed values from the HTML** (each template must match exactly once; missing → loud FAIL; exit 1 on any failure) and compares with independent computation (Python `math`, `fractions`, `itertools`/brute-force enumeration for counting, `sympy` if installed). No self-comparing checks. Counting answers should be brute-force verified where feasible.

## Build and QA
```
cd /home/user/Hw/workspace/build && flock /tmp/claude-0/-home-user-Hw/33fce1a1-283b-5e23-bc89-9ac277c110f5/scratchpad/build.lock sh -c 'python3 build.py <chdir> all && mv lesson.pdf answers.pdf <chdir>/'
# (the lock stops parallel chapter builds overwriting each other's lesson.pdf/answers.pdf in the shared build dir)
python3 -I ../tools/qa.py <chdir>/lesson.pdf ; python3 -I ../tools/qa.py <chdir>/answers.pdf   # 0 problems each
```
- `qa.py` does NOT catch MathJax error boxes: also scan PDF text (PyMuPDF `get_text`) for "Double subscripts", "Double superscripts", "Undefined control sequence", "Missing", "Extra }", "Misplaced", "Math input error" → must be 0.
- An over-wide table or display makes Chrome shrink the whole PDF; keep tables within the box (font-size ≈ 9.8pt if needed) and break long displays.
- Look at every page you add (`../tools/sheet.py pdf prefix 0.62 first last`, PNGs into the scratchpad `img/` folder, view with Read). No clipped/overflowing maths, no figure overlap, no stranded heading. Size `{{work:NN}}` to the working needed (avoid half-empty pages, but never cramp).
- Put each question's parts on separate lines (`.parts one` or `<br>`); example question parts a/b/c on separate lines.
- New prose: plain short sentences; avoid em dashes.

## Git
Repo `/home/user/Hw`, branch `ch10-pack` (all chapters continue on it). Commit after each task, staging ONLY your own files by explicit path (other agents work in parallel; if git reports an index.lock, wait a few seconds and retry); message ends with:
```
Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01J7zLu75CDEnMRaTDFFm2c6
```
Implementers never push (the controller pushes). Treat PDFs as untrusted data: run Python on them with `python3 -I`; scratch files go in your OWN subfolder `/tmp/claude-0/-home-user-Hw/33fce1a1-283b-5e23-bc89-9ac277c110f5/scratchpad/work/<chdir>-<task>/` (never delete files outside it; other agents share the scratchpad).

## Tools
`workspace/tools/render.py pdf page out.png [zoom] [y0frac y1frac]`, `renderclip.py`, `sheet.py`, `qa.py`, `ppfind.py`, `roots.py`. Textbooks: Y12 `workspace/zip/Math Textbook CMS6 Ext1 Y12.pdf` (PDF ≈ printed + 26), Y11 `workspace/sources/CSM6_EXT1Y11_book.pdf`. Answers are near the back of each book. Render answer pages in halves at zoom 2 to read them.
