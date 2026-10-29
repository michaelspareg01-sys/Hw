### Task 6: Assemble, record, final QA, deliver
- [ ] Fill `@@M15X@@` from each `.pp-intro` (no `@@` left). Append to `docs/PAST_PAPERS_USED.md`: "Y11 Ch 15 Binomial theorem (15A–15D) built <date>. Past papers used: …" (from `docs/pp_selected_y11ch15.md`; new abbreviations into Key). Do not change "Next:" (another chapter owns it).
- [ ] Build both PDFs; all `workspace/checks/y11ch15_*.py` pass; qa 0/0; MathJax 0; contact-sheet and look at EVERY page of both PDFs; layout-only fixes.
- [ ] Copy to `/home/user/Hw/output/` with the spec names; report page counts. Commit `Y11Ch15: assemble, record, final QA`.

## Controller additions
- Deferred layout: l15a.html Q3 work box (~line 189, work:46) is tight for two column expansions; enlarge.
- Cover: @@M15A@@ = "17 marks · 25 min"; take 15B–15D values from their .pp-intro lines.
- qa.py misses MathJax errors: run the MathJax error-string scan on both PDFs.
- Soften past-paper hints (starting idea only): 15D PP2 and PP6 (currently point at near-identical worked examples), 15D PP7 (gives the key step). Re-check every hint in the pack against house rule 4 while you look at each page.
- 15D review Q7 work box (~35 mm) may be enlarged if layout allows; answers p17 mostly empty is acceptable.
- Cover values from .pp-intro lines: expected 15A 17 marks · 25 min, 15B 16 · 25, 15C 18 · 25, 15D 16 · 25 (confirm).
- PAST_PAPERS_USED.md: do NOT change the "Next:" line (controller owns it).
