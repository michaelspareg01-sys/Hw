# Task 0 report: Y11 Ch 14 past-paper candidate catalogue

Status: DONE_WITH_CONCERNS (the concerns are doubtful source items, flagged below; none of them affects the catalogue itself)

## What I built
`docs/pp_candidates_y11ch14.md` (149 lines, commit 5c7218c). It holds 88 candidate rows in the Ch 10 table format (`docs/pp_candidates_ch10.md`), grouped by lesson tag:

| Tag | Rows | Marks (clean rows only) | Notes |
|---|---|---|---|
| 14A | A1–A5 | 10 | Thin, as expected. E6 and E26 are factorial algebra too (+3) |
| 14B | B1–B10 | 15 | B10 is from a sample paper |
| 14C | C1–C11 | 14 | C7 and C8 are the same idea |
| 14D | D1–D10 | 13 | D8 and D9 are the same wording |
| 14E | E1–E34 | about 55 | E34 is from a sample paper |
| 14F | F1–F18 | 25 | Leaves out F4, F17 and F18 (doubtful) |

There are 33 MC items in all. Each row gives the file, question page and solution page (or "none"), the cover title as printed with the school and year, Q and marks per part, a one-line summary, whether there is a diagram, and flags.

There are also sections for overlaps, rejected items (circular, pigeonhole, binomial, induction) and "Papers with no text layer", modelled on Ch 10.

## Method and sources
- I extracted text page by page with `pdftotext -layout` for every school paper in `pp/Ext 1/2020`–`2024`. NEAP, PEM, TEC, CSSA and Independent were excluded; the BoS zip is not in these folders. I searched with broad regexes: arrange, ways, how many, committee, chosen/selected, digits, letters, identical, paths, factorial patterns, nCr/nPr, probability, "number of …". Script: `scratchpad/pp14/scan.py`.
- I rendered every candidate page and read it, and pinned the solution pages by eye.
- Fully scanned papers were checked as page sheets: 2020 BHHS, Manly, NSB and Ruse; 2021 Girraween, NSB and JRAHS; 2022 Knox; 2023 Moriah; 2024 NSB, PLC and Saint Ignatius. So were text-less pages inside typed papers and Western 2020's image-only pages.
- I read the covers from the text layer, and rendered them where the school appears only as a crest: the three Killara papers, BHHS 2023, Knox 2023, Girraween 2023, PLC 2023, KWS 2023, STHS 2021 and 2023, SGS 2021–23, Kings 2021, NBHS 2022 and NSB 2022.
- I excluded everything in `docs/PAST_PAPERS_USED.md`, `docs/pp_selected_ch10.md` and `docs/pp_selected_y11ch15.md` (empty), re-read just before committing.
- 14E scope check: the textbook (PDF 711–719) Box 12 includes nC0 + … + nCn = 2ⁿ by counting subsets, so NSB 2020 Q14(a) is in scope.
- Answer check: `scratchpad/pp14/verify.py` brute-forces or computes every MC key and short answer (itertools enumeration, math.comb, Fraction). All match the school answers except F4.

## Doubtful items (report to controller; do not use in student material)
1. **James Ruse 2020 Q14(c)** (`2020/James Ruse 2020 3U Trials & Solutions.pdf` p9, solution p25): the printed answer is 53/2163. The school's own expression, and my direct count, both give 53/2162.
2. **STHS Sample 1 Q8** (`2020/2020 Sydney Tech 2.pdf` p4): it asks for a probability, but every option is a count with no division by 32C15.
3. **STHS Sample 2 Q14(c)(ii)** (`2020/2020 Sydney Tech.pdf` p8): garbled wording ("has any one of the letters must appearing exactly twice").
4. **Fort Street 2023 Q3(d)(ii)**: garbled wording ("groups of made up of c, k, and r members"). Part (i) is fine.
5. **Western 2020**: the cover reads "Western Mathematics" and names no school. Ch 10 found a question word-for-word in NSB 2020. Its Q10 (F17) is usable only if you accept it as a school paper.
6. Minor typos (usable at your discretion, since fidelity means the typo stays):
   - Caringbah 2021 Q7: "a least one boy"
   - Girraween 2023 Q5: "commitee"
   - Knox 2023 Q12(d): "Find n the number dancers"
   - STHS 2023 Q12(e): "positive affect"

## Other concerns
- Source label: Fort Street 2023 (E17, E18) and NSB 2024 (B4) have no cover, and no school name appears anywhere in either file, only in the file name. BHHS 2020 has no cover either, but its solutions show the crest and title.
- STHS 2021's solutions are headed "Mathematics Common Test Assessment 4 2019", while the cover says Trial HSC August 2021; the answers do match. STHS 2023's solutions are headed "Official STHS Mathematics Paper: Boohoo 95 edition - 2023" (informal).
- HGHS 2023 Q4 (C10) treats Y as a consonant (the solution says "4 vowels"); the question does not say so.
- "Numbers greater than …" items B2 and B4 include 5-digit numbers. The school solution for B2 counts them.
- NSB 2020 Q14(a) (E12): the school solution uses the binomial expansion. Ch 15 (binomial) is being built in parallel, so whichever pack uses it should claim it first.
- Overlaps to avoid inside one pack: C7/C8 (EPSILON vowels), D8/D9 (grid wording), E8/E30 (teams and umpire), E10/E21 (5-member committee), and STATISTICS in C5/D2, C9 and D5.
- Gosford 2022 (E13) has no Ext 1 solutions, because the bound solutions are for Ext 2. Several other rows have no solutions; each is marked "none".

## Verification
- `python3 -I scratchpad/pp14/verify.py`: every printed key reproduced except JRAHS 2020 Q14(c) (53/2162 vs printed 53/2163, confirmed two ways).
- Rendered and read every candidate question page, every cited solution page, and the covers listed above.

## Files changed and commits
- `docs/pp_candidates_y11ch14.md` (new), commit `5c7218c` "Y11Ch14: past-paper candidate catalogue" on `ch10-pack`, with the attribution lines. Not pushed. `workspace/build/` was not touched.
- Scratch: `/tmp/claude-0/-home-user-Hw/33fce1a1-283b-5e23-bc89-9ac277c110f5/scratchpad/pp14/` (scan.py, verify.py, txt/, img/).
