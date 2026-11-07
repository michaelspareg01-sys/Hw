# Spec: "Year 12 Ext 1 Integration" — three packs, from primitives to volumes of rotation

Owner request (7 Nov): the existing Ch 12 pack skips steps; make a new integration course "from the beginning of integration all the way to the appropriate end", using the given sources. Owner choices: full range (primitives → volumes; no motion chapter), Ext 1 trial papers for mini exams with short sets accepted where too few fit (timed-practice note, as in Y11 Ch 13), split into three parts.

Binding: `docs/superpowers/specs/house-rules.md` (all rules, including past-paper rules 1–8 and no reuse against `docs/PAST_PAPERS_USED.md` and EVERY `docs/pp_selected_*.md`).

## Source
Ext 1 Year 12 book `workspace/zip/Math Textbook CMS6 Ext1 Y12.pdf` (PDF page = printed + 26; it contains all Advanced Year 12 content). Answers from PDF 850. Y11 Advanced book `workspace/zip/Cambridge Maths Advanced 2019.pdf` for revision references only.

## The three packs
| Part | Build dir | Lessons (book section, PDF pages) | Revision page (prerequisites) |
|---|---|---|---|
| 1 Integration basics | `workspace/build/int1/` | L1 4J Primitive functions (202–207); L2 5A Areas and the definite integral (213–222); L3 5B The fundamental theorem of calculus (223–230); L4 5C The definite integral and its properties (231–239); L5 5D Proving the fundamental theorem (240–246); L6 5E The indefinite integral (247–253); L7 5F Finding areas by integration (254–262); L8 5G Areas of compound regions (263–269); L9 5H The trapezoidal rule (270–279); L10 5I The reverse chain rule (280–286) + Chapter 5 review (287–289) | Y11 differentiation rules (power, chain), index laws incl. fractional/negative, sigma notation (Y12 1E), area formulae |
| 2 Exponential, logarithmic and trigonometric integrals | `workspace/build/int2/` | L1 6D Integration of exponential functions (308–314); L2 6E Applications of integration (315–320); L3 6I Integration of the reciprocal function (341–349); L4 6J Applications of integration of 1/x (350–354); L5 6K Calculus with other bases (355–361); L6 7D Integrating the trigonometric functions (393–402); L7 7E Applications of integration (403–408) + review: integration questions only from the Chapter 6 and Chapter 7 reviews | derivatives of e^x, ln x, a^x, sin x, cos x, tan x (6B, 6G, 7B), log laws, radians and exact values, integration basics from Part 1 |
| 3 Further integration (Ext 1) | `workspace/build/int3/` | L1 12A Inverse trigonometric functions: differentiating (542–548); L2 12B Inverse trigonometric functions: integrating (549–556); L3 12C Further trigonometric integrals (557–560); L4 12D Integration by substitution (561–565); L5 12E Further integration by substitution (566–569); L6 12F Volumes of rotation (570–576) + Chapter 12 review (577–579) | inverse trig functions (Y11 Ext 1), double-angle identities, standard integrals from Parts 1–2 |

Section page ranges above are approximate starts/ends from the contents; render and confirm. Exercise and answer pages: find them. Part 2 L5 (6K) covers differentiation and integration with other bases: teach the whole section (the integration depends on it). 5D is the textbook's proof section: teach it in full (the owner complained about skipped steps).

## Deliverables
Outputs (copy to `/home/user/Hw/output/` and `git add -f`):
- `Year_12_Ext1_Integration_Part1_Basics_{Lesson_and_Homework,Homework_Answers}.pdf`
- `Year_12_Ext1_Integration_Part2_Exp_Log_Trig_{Lesson_and_Homework,Homework_Answers}.pdf`
- `Year_12_Ext1_Integration_Part3_Further_Integration_{Lesson_and_Homework,Homework_Answers}.pdf`
pack.json footers "Integration Part N … | Lesson and Homework" / "| Homework Answers"; header default (Year 12 Ext 1).

## Teaching standard (the owner's complaint)
No skipped steps: every concept box, derivation, worked example and warning in each section, with full working lines in demos, worked examples and answers (show the primitive, the substitution of limits, the arithmetic). Where the textbook says "clearly" or jumps a line, the pack's own Tutor demo shows the missing line.

## Past papers
Catalogue: `docs/pp_candidates_integration.md` (Task 0), every school Ext 1 trial 2020–2024 integration item tagged by lesson (int1-L1…int3-L6), with flags (doubtful, already used, needs a later method). Record per part: `docs/pp_selected_int1.md`, `pp_selected_int2.md`, `pp_selected_int3.md`. A question must only need methods taught up to that lesson. Short sets: house rule 8 plus a timed-practice note pointing to textbook questions (as Y11 Ch 13). Hints: a starting question only (no value, step, event or technique).
