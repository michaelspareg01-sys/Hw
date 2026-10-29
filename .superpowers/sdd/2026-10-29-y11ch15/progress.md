# SDD ledger — plan: docs/superpowers/plans/2026-10-29-y11ch15.md
Spec: docs/superpowers/specs/2026-10-29-y11ch15-design.md ; house rules (updated for parallel chapters)
Catalogue: docs/pp_candidates_y11ch15.md (commit 1755c07)
## Pre-flight: T1 creates placeholders; T2-T5 sequential on own files; T6 reads .pp-intro. Runs in parallel with the Y11 Ch14 plan (disjoint dirs, explicit staging, all pp_selected_*.md cross-checked).
Ruling: negative-power general-term items allowed in 15C only if 15C's exercise uses the method and the lesson teaches it first — 15E skipped by owner — cost if wrong: swap a few PP items.
Ruling: "Next:" line in PAST_PAPERS_USED owned by the controller at the end, not Ch15 Task 6 — parallel chapters — none.
## Tasks
Task 1: dispatched (sonnet) agent=a7a3b8419b6ba1a16 BASE=a671b03
Task 1: implementer DONE e9bdc7c (rev 85 OK, qa 0/0). @@M15x@@ filled by Task 6 (per plan).
Task 1: reviewer (sonnet) agent=aeb85200e642cfea9
Task 1: review Approved (minor: 15B starts PDF 748 — spec/briefs corrected; revision p1 tight).
Task 1: complete (commits a671b03..e9bdc7c, review clean)
Task 2: dispatched (opus) agent=aef64e54094c3fe92 BASE=183b045
Task 2: implementer DONE_WITH_CONCERNS 2a076cf (PP 8 marks: Kings21 Q2, Moriah23 Q9d(i)(ii), SGS23 Q13a, Abb21 Q12c; checks 125 OK).
Ruling: 15A must reach 15-22 marks using small-n coefficient rows (A5-A15) that 15A's Pascal method handles — house rule 8 applies only when genuinely too few; 15C has 25 candidates — cost if wrong: 15C loses a few small-n items.
Ruling: teaching-text avoidance of textbook slips ((1+x)^2 meaning (1+x)^1; "Petrus Adrianus" omitted) accepted — our own concept wording, not a transcribed question; no correction is printed — none.
Task 2: reviewer dispatched (sonnet)
Task 2: reviewer agent=a879bc2963af0e193
Task 2: review Needs fixes: Important 8 marks (ruled), pool justification; minors: parts layout, lesson table unchecked, hints PP1/PP3 give steps, forward refs to 15B, Q1 box tight / p5 orphan. Moriah school solution slip noted (not in student material).
Task 2: fix round 1/5 dispatched to original implementer (all items).
Task 2: fix round 1 DONE 7c95449 (17 marks/25 min; +A5 Asc20 Q8, A7 NSB20 Q2, A10 Gir21 Q2, A13 Gir23 Q16a, A14 NBHS22 Q11b; checks 158). Note: A6 (dup of A5) must not be used elsewhere.
Task 2: re-review agent=a8e093eb2e76974d6
Task 2: re-review round 1: 1-7 ADDRESSED.
Task 2: minor (deferred): l15a Q3 work box ~40mm tight for two expansions — Task 6 layout.
Task 2: complete (commits 183b045..7c95449, 1 fix round)
Task 3: dispatched (opus)
Task 3: implementer agent=adb9937674088ed03 BASE=73254ac
Task 3: implementer DONE_WITH_CONCERNS f6bb8b3 (15B PP 16 marks/25 min incl. C21 Knox23 Q11a, C22 JRAHS23 Q15b; checks 161 OK).
Ruling: fix duplicated word "to to" in Ex 15B Q10 — typographic, not mathematical (same as 14A spelling ruling) — none.
Ruling: 15B may take C21, C22 (Pascal-triangle-solvable) — 15C pool remains large — cost if wrong: 15C two fewer items.
Task 3: reviewer dispatched (sonnet)
Task 3: reviewer agent=ac3f3dbde9a60f41f
Task 3: review Approved (first pass). Minor: St Aloysius "neither a or b are" kept verbatim (grammar only).
Task 3: complete (commits 73254ac..f6bb8b3, review clean)
Task 4: dispatched (opus)
Task 4: implementer agent=a35767f6972d2ed3d BASE=f6bb8b3
Task 4: implementer DONE_WITH_CONCERNS 874d074 (15C PP 8 items/18 marks/25 min; neg-power in scope via Ex 15C Q15; checks 167 OK).
Ruling: keep worked example with powers of 20 (Q15 stays a genuine exercise) — none.
Ruling: Ex 15C Q18 — textbook printed answer has a slip; print our own independently solved answer with no remark (precedent: Ch10 9E Q8b) — students get an answer, no correction claimed — cost if wrong: remove one answer line.
Task 4: reviewer dispatched (sonnet)
Task 4: reviewer agent=a579f1ed3ff6fd288
Task 4: review Needs fixes: Important Q18 answer missing (ruling: own answer). Minor: PP6 NSB20 Q11b "in the expansion (...)" grammar — keep (precedent St Aloysius); PP4 hint borderline OK.
Task 4: fix round 1/5 dispatched (add Q18 proof + checks).
Task 4: fix round 1 DONE 7a546a4 (Q18 own proof + checks; 170 OK).
Ruling: controller verified the one-answer fix directly (read the added proof; ran y11ch15_15c.py All OK) instead of a re-review subagent — fix is a single answer line + checks — cost if wrong: final review catches.
Task 4: complete (commits f6bb8b3..7a546a4, 1 fix round)
Task 5: dispatched (opus)
Task 5: implementer agent=a6dab105f67854886 BASE=7a546a4
Task 5: implementer DONE_WITH_CONCERNS 06f4cde (15D PP 7 items/16 marks; review 13 Qs all in scope; checks 285 OK).
Ruling: omit Ex 15D Q12(d) (identity false as printed) and SBHS 2020 Q14(c)(ii) (school solution final answer wrong) — rule 6 — cost if wrong: minor.
Ruling: keep Ex 15D Q2 verbatim (n≥2 implied by context; no printed answer) — cost if wrong: add a condition later.
Ruling: accept typo fixes "occuring", "an r-member subsets", review Q6 wrong cross-ref to "Exercise 16A" dropped, PP7 "a_o"→a_0 — typographic — none.
Task 5: reviewer dispatched (sonnet)
Task 5: reviewer agent=a74fafede4c0dbbbe
Task 5: review Approved. Minor: PP2/PP6 hints point at near-identical worked examples, PP7 hint gives key step (soften in Task 6); review Q7 box short; answers p17 mostly empty; silent answer-slip corrections Q4(b), Q9(b)(i) per precedent.
Ruling: keep NSB 2023 Q14(c) — question pages print the school name; NSB23 items used in Ch11/12 — none.
Task 5: complete (commits 7a546a4..06f4cde, review clean)
Task 6: dispatched (opus) BASE=06f4cde
Task 6: implementer agent=a0a04f5ccf9513a0c
Task 6: implementer DONE_WITH_CONCERNS 049fef0 (lesson 80pp, answers 19pp; 5 checks OK; qa 0/0; MathJax 0). Controller verified outputs are Ch15 content, qa, checks.
Ruling: accept extra hint softenings (15B PP6, 15C PP6) and Q4/Q5 box trims — consistent with rule 4 / layout-only — none.
Ruling: house rules build command now uses flock (shared build dir collision risk) — none.
Ruling: merge Task 6 task-review into the final whole-pack review (opus), which inspects every page and the assembly diff — saves a cycle; final review is a superset — cost if wrong: none.
Final review: dispatched (opus)
Final review: agent=a5f95b6f5646df353
Final review: Ready to deliver; 3 cosmetic minors accepted (ghost hairline near \boxed{nCr} at Ch10-level, 'compare' hints within rule 4, 15A Q5 box 40mm).
