# Task reviewer instructions (read fully before starting)

You review one task of a NSW Year 12 Mathematics Extension 1 tutoring pack: first spec compliance, then quality. Your dispatch names the brief, the implementer's report, the diff file (base..head) and any extra focus. Binding rules: `docs/superpowers/specs/house-rules.md` and the chapter spec named in the brief.

## Method
- Read the diff file once (it is the change). Do not re-run git unless it is missing.
- Treat the report as unverified claims. Verify against the diff AND the sources.
- **Independent verification is the core of the review:**
  - Textbook fidelity: render the textbook pages (`python3 -I /home/user/Hw/workspace/tools/render.py <pdf> <page> <out.png> 1.3 [y0frac y1frac]`, images into `/tmp/claude-0/-home-user-Hw/33fce1a1-283b-5e23-bc89-9ac277c110f5/scratchpad/img/rev/`) and compare at least 8 transcribed homework questions word for word (favour number-heavy ones), the worked examples copied from the textbook, and the concept boxes (anything in the teaching part missing?).
  - Answers: compare at least 8 textbook-homework answers with the textbook answer pages, and re-solve at least 4 lesson-example answers (tutor demos / your turns) yourself.
  - Past papers: for EVERY past-paper question, render the question page and cover; compare wording, values, marks, diagram labels; check the label (school, year, cover title, Q); solve it yourself and compare with the worked solution and the school solution; confirm it is not in `docs/PAST_PAPERS_USED.md` or the pack's `docs/pp_selected_*.md` earlier entries; confirm it is not a commercial paper; note any doubtful wording (house rule 6).
  - Check scripts: read enough to confirm they read printed values from the HTML and recompute independently (no self-comparisons). Run each once.
  - Layout: contact-sheet the pages the task added (`python3 -I /home/user/Hw/workspace/tools/sheet.py <pdf> <prefix> 0.62 first last`) and look at every one; scan both PDFs' text for MathJax error strings.
- Name every check you ran.
- Read-only: never modify files, the index, HEAD or branch. Do not dispatch subagents.

## Calibration
Critical: wrong maths or answer a student would see; wrong transcription; invented or wrong source details; commercial or reused question; a kept doubtful item or a printed "correction". Important: missed requirement (missing textbook teaching content, missing questions, marks outside 15–22 without justification, missing hints/labels), clipped maths or overlap, vacuous checks, MathJax error. Minor: polish.

## Output (your final message is the report; begin with the verdict)
### Spec Compliance  (✅ / ❌ with file:line; ⚠️ cannot verify)
### Strengths
### Issues  (#### Critical / #### Important / #### Minor — file:line or PDF page, what, why, fix)
### Checks run
### Assessment
**Task quality:** Approved | Needs fixes
**Reasoning:** 1–2 sentences
