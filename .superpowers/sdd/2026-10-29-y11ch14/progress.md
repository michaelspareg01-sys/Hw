# SDD ledger — plan: docs/superpowers/plans/2026-10-29-y11ch14.md
Spec: docs/superpowers/specs/2026-10-29-y11ch14-design.md ; house rules: docs/superpowers/specs/house-rules.md
## Pre-flight scan
| Pair / task | Shared file | Finding |
|---|---|---|
| T0 vs T1 | none (docs/pp_candidates vs build/y11ch14) | parallel-safe if each stages only its own files |
| T1 vs T2-T7 | placeholders l14x/a_14x, figs.py, pack.json | T1 creates placeholders; T2-T7 replace one each; sequential |
| T2-T7 | docs/pp_selected_y11ch14.md, figs.py | append-only; sequential |
| T7 | review in l14f/a_14f | consistent with spec |
| T8 | cover @@M@@ | reads .pp-intro from T2-T7 |
Ruling: pack named Year_12_Ext1_Y11_Ch14_Combinatorics_* (distinguishes Y11 chapter numbering from Y12 book) — cost if wrong: rename files.
Ruling: revision page = Advanced Y11 probability basics (needed by 14F) — handover gives no revision topic for Ch 14; earlier packs always had one — cost if wrong: one page to drop.
Ruling: T0 and T1 run in parallel (disjoint files, explicit git add) — saves ~15 min — cost if wrong: a commit to untangle.
## Tasks
Task 0: dispatched (opus) agent=a85d72f9f01e1514b BASE=8130ff8
Task 1: dispatched (sonnet) agent=a7e9a966596b07c29 BASE=8130ff8
Side: Ch15 catalogue agent=a34b988ace5c499a3 -> docs/pp_candidates_y11ch15.md; Ch13/Ch17 catalogue agent=a2761508147bf9411 -> docs/pp_candidates_prob.md (correction sent re continuity).
Task 1: implementer DONE ea82a81 (rev checks 57 OK, qa 0/0)
Task 1: reviewer (sonnet) agent=a97ae88eeb3eff212
Task 1: review Approved. minor (deferred): revision p2 quarter empty, p4 40% full; suit glyphs not red — Task 8.
Task 1: complete (commits 8130ff8..ea82a81, review clean)
Side: Ch15 catalogue DONE 1755c07 (15A 4+11, 15B 6, 15C 25 (20 neg-power), 15D 11; 19 MC). Pending ruling for Ch15 plan: neg-power general-term items in 15C.
Side: Ch13/Ch17 catalogue DONE f582f2e (13A 4, 13B/C 3, 13D 0, 17A 25, 17B 18, 17C 12, 17D 20, NORM 1).
Ruling (for Ch13/Ch17 specs): exclude "3U JRAHS.pdf" (2021 mock naming no school) and "Western Mathematics" 2020 (school unclear); allow SBHS 2020 and Sydney Tech 2020 school revision samples (precedent: SydTech20 samples used in Ch13 pack) — cost if wrong: a few more candidates.
Ruling: doubtful items flagged in the catalogue (SydTech S2 Q5, BBHS22 Q12e, Caringbah21 Q14a, BBHS24 Q11e) must not be used — house rule 6 — none.
Task 0: DONE_WITH_CONCERNS 5c7218c (88 rows; 14A ~10 marks thin).
Ruling: exclude papers whose file does not print the school name/title (Western 2020, Fort Street 2023, NSB 2024) — a label must come from the paper — cost if wrong: fewer candidates.
Ruling: catalogue not separately reviewed; every chosen item is re-verified by its lesson reviewer — research artifact — cost if wrong: none (lesson reviews catch errors).
Ruling: do not use JRAHS20 Q14(c), STHS S1 Q8, STHS S2 Q14(c)(ii), FS23 Q3(d)(ii) (doubtful) — house rule 6.
Task 0: complete
Task 2: dispatched (opus) BASE=5c7218c
Task 2: implementer agent=a73d17a155d7a99ac
Task 2: implementer DONE_WITH_CONCERNS b47caab (14A PP 9 marks/15 min: SBHS20 Q12c, NBHS22 Q11a(i), NBHS21 Q11e(i), HAHS23 Q12d, CTHS20 Q1, Ascham23 Q12e(i); checks 180 OK).
Ruling: keep CTHS20 Q1 and Ascham23 Q12(e)(i) in 14A (9 marks, house rule 8) — 14A pool thinnest — cost if wrong: 14B 2 marks fewer.
Ruling: accept textbook spelling fix "interchangeable" (14A Q1d) — spelling, not maths; house rule 6 targets mathematical errors — none.
Ruling: house rules updated: per-agent scratch subfolders (an agent deleted shared PNGs) — none.
Task 2: reviewer (sonnet) agent=abd049932a371c140
Task 2: review Needs fixes: Important p7 clipped derivative line; minor PP6 hint gives a step (rule 4), Q13c label layout. Deferred minor: PP3/PP4 same identity (thin pool), p9 quarter blank.
Task 2: fix round 1/5 dispatched to original implementer (clip + hint + Q13c).
Task 2: fix round 1 DONE b4400cb
Task 2: re-review (sonnet) agent=ac72383b17eb1d3a7
Task 2: re-review round 1: 1-3 ADDRESSED.
Task 2: complete (commits 5c7218c..b4400cb, 1 fix round)
Task 3: dispatched (opus) BASE=2a076cf
Task 3: implementer agent=ac13752b2542caee2
Task 3: implementer DONE_WITH_CONCERNS 73254ac (14B PP 13 marks/8 Qs; checks 218 OK).
Ruling: omit Ex 14B Q22b (repetition allowed → infinitely many; printed answer assumes ≤4 digits) — doubtful item, rule 6 — cost if wrong: one question restored.
Ruling: keep Hurlstone 2021 Q11(b) in 14B — needs only 14B counting + revision probability; 14F pool 25 marks — cost if wrong: 14F slightly thinner.
Task 3: reviewer dispatched (sonnet); reviewer to judge whether eligible rows remain for 15+ marks.
Task 3: reviewer agent=a0f06de7e03f34e5f
Task 3: review Approved; 13-mark set justified (catalogue sweep; max clean eligible = 13).
Task 3: minor (deferred): 14B PP5 hint nearly gives the step (soften: "think about how many digits such a number could have"); lesson p22/p28 ~35-40% blank, p38 half — Task 8.
Task 3: complete (commits 2a076cf..73254ac, review clean)
Task 4: dispatched (opus)
Task 4: implementer agent=a9e2c906ccc011be8 BASE=73254ac
Task 4: implementer DONE_WITH_CONCERNS fbb43b1 (14C PP 10 Qs/15 marks incl. C7+C8 same EPSILON problem; F2, F8, F14 used; checks 209 OK).
Ruling: drop PP8 (C8 James Ruse 2023 Q10), the near-duplicate of PP4 (Ascham 2023 Q12(e)(ii)), for variety → 14 marks under rule 8 (other rows need 14D) — cost if wrong: one mark short.
Task 4: reviewer dispatched (sonnet), asked to judge F8 STHS 2021 Q11(c) cleanliness.
Task 4: reviewer agent=a71e85c12a2483eb8
Task 4: review Needs fixes: Important PP9 (F8 STHS21 Q11c) genuine but plain probability, mislabelled as 14C counting. F2, F14 kept.
Ruling: remove PP9 (free for 14F) along with ruled PP8 drop → 12 marks/20 min, rule 8 (reviewer re-scanned all school papers; nothing clean remains for 14C) — cost if wrong: 2 marks.
Task 4: fix round 1/5 dispatched (PP8+PP9 removal, hints PP5/PP10, ordered-model sentence, p41 arc, PP6 label wrap).
Task 4: fix round 1 DONE 7f854b4 (8 Qs/12 marks/20 min; JRAHS23 Q10 removed, Ascham23 Q12e(ii) kept; checks 205/180/218 OK).
Ruling: accept removal of James Ruse 2023 Q10 (keeping Ascham 2023 Q12(e)(ii)) — either breaks the duplicate; marks unchanged — none.
Task 4: re-review dispatched (sonnet)
Task 4: re-review agent=a860f3e21c9c8e6cd
Task 4: re-review round 1: 1-6 ADDRESSED. Minor (must fix, routed to Task 8): BBHS sentence "every count below, and the total, is 4 times the unordered count" — intermediate counts in (ii) are 2x; reword to "each count of selections of all four batteries".
Task 4: complete (commits fbb43b1..7f854b4, 1 fix round)
Task 5: dispatched (opus)
Task 5: implementer agent=a00807e30b06708f6 BASE=7f854b4
Task 5: implementer DONE_WITH_CONCERNS d9f914d (14D PP 12 items/16 marks/25 min; checks 239 OK).
Ruling: allow BHHS 2020 Q8 — file has no cover but its marking-guidelines header and crest print school and title (unlike Western/FS23/NSB24 which print no school) — cost if wrong: 1 mark.
Ruling: fix "part B" → "part b" in Ex 14D Q19(c) (typographic; consistent with earlier typo rulings) — routed to Task 8.
Ruling: grid-paths concept box accepted as supplementary (identical-elements arrangements; spec topic map lists grids; two PP items need it) — cost if wrong: one box to drop.
Task 5: reviewer dispatched (sonnet)
Task 5: reviewer agent=a58c66f26c2c014f2
Task 5: review Approved.
Ruling: keep WE12(a) "5 alike" (book typo "2 alike" in a copied worked example; printing it would mis-teach; no correction note printed) — cost if wrong: revert one word.
Ruling: accept PP1/PP4/PP2/PP5 single-Box-10 warm-ups (different words) and "Baulkham Hills High School" label — none.
Task 5: minor (deferred → Task 8): soften 14D hints PP6 ("think of the Es as one item") and PP11 ("where do the two grids meet?").
Task 5: complete (commits 7f854b4..d9f914d, review clean)
Task 6: dispatched (opus)
Task 6: implementer agent=a196714f9c2317d74 BASE=7a546a4
Task 6: implementer DONE_WITH_CONCERNS c39ea6f (14E PP 11 items/20 marks/30 min; checks 298 OK).
Ruling: omit Ex 14E Q6 (says identical balls; book answers count distinct) — rule 6 — cost if wrong: one question.
Ruling: accept silent typo fixes (Box 13 "o"→0, Ex 19(c) missing comma, Q16(a)(ii) answer "Laura"→"one particular person") and keep PP grammar slips verbatim (precedent) — none.
Task 6: minor (deferred → Task 8): lesson p86 WE20 alone ~40% blank.
Task 6: reviewer dispatched (sonnet), incl. check that circle10.svg item is not 14G circular arrangement.
Task 6: reviewer agent=a54c13f3f6fd377d1
Task 6: review Approved (circle10 is selection, not 14G).
Task 6: minor (deferred → Task 8): C5 demo box 26mm cramped vs Your turn 120mm (p84/85); stray box sliver p82 bottom; STHS 2021 label order should be as printed ("Extension 1 Mathematics, Trial HSC"); label style PP5/PP8 omit "(i)(ii)".
Task 6: complete (commits 06f4cde..c39ea6f, review clean)
Task 7: dispatched (opus)
Task 7: implementer agent=a11ef0427309779ea BASE=edb427b
Task 7: implementer DONE_WITH_CONCERNS 68b0d30 (14F PP 7 Qs/15 marks/25 min; review Q1-14, Q15 (14G) and Q16-17 (14H) omitted; checks 376 OK).
Ruling: labels must follow the cover word order; Task 8 aligns all NBHS labels across 14A–14E to the cover order — house rule 4 — none.
Ruling: keep Kings 2021 Q8 "identical marbles" (probability unaffected; answers consistent) — unlike 14E Q6 whose answers contradicted the wording — cost if wrong: 1 mark.
Ruling: keep Ex 14F Q19, Q27 (book answers match the natural readings); accept "a women"→"a woman" — none.
Task 7: reviewer dispatched (sonnet)
Task 7: reviewer agent=a35606fb931885517
Task 7: review APPROVED (0 Critical, 0 Important). Minors: PP4 kept (only replacement drops below 15 marks); PP variety thin (pool); PP6/PP7 hints softened + PP6(i) full stop moved, folded into Task 8 brief.
Ruling: keep STHS 2021 Q11(c) in 14F (solved by unordered hands + complement, a 14F method) — cost if wrong: 2 marks of plain probability.
Task 8: implementer dispatched (opus)
Task 8: DONE 7f0360b (126/38 pp; all checks pass; qa 0/0; MathJax 0). Remaining gaps judged acceptable (boxes taller than gaps). Final whole-pack review dispatched (opus).
Final review: NEEDS FIXES (2 Important: answers p33 Q5 row overlap, p1 warm-up Q3 overlap; minors: 14A PP1-3 hints, 14B PP7 P style, review-answer order). ~150 answers verified correct. Fix round sent to Task 8 implementer.
Final review fix round DONE 0310834; controller viewed answers p1 and p33 (clean) and new 14A hints (starting ideas). PACK COMPLETE and delivered (126/38 pp).
