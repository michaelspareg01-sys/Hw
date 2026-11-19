# Spec: two Year 11 Ext 1 packs. Ch 6 Trigonometry (6G–6K) and Ch 17 Inverse trigonometric functions

## Owner request (19 Nov)
> "use the y11 textbook (and pastpaper) to make y11 content: hw with revision on trig identities, and then teach on trig equations (6H), revision on 6I to 6J, teach 6K. Output this pdf. And then make ch17 (teaching)."

Binding rules:
- `docs/superpowers/specs/house-rules.md`;
- the model specs `2026-10-29-y11ch13-design.md`, `y11ch14` and `y11ch15`, which describe the finished Y11 packs in `workspace/build/y11ch13/` to `y11ch15/`. Use those packs as the style model;
- the rulings settled by the later reviews:
  - hints are neutral starting questions;
  - no tip leaks a homework answer or method;
  - no homework item repeats a worked example;
  - book boxes are verbatim, and added lines go in "Steps the book skips" tips;
  - figure labels are at least 8 pt and circles are round;
  - text is 11.3 pt;
  - no em dashes in new text.

Book: `workspace/sources/CSM6_EXT1Y11_book.pdf` (PDF page = printed page + 24). Answers are at the back.

Past papers: real school Ext 1 trial papers in `workspace/pp/Ext 1/2020`–`2024`. These are the same pool and exclusions as the earlier packs: never NEAP, PEM, TEC, CSSA, Independent or BoS. Exclude the papers listed in the y11ch13 spec. Never reuse an item that appears in `docs/PAST_PAPERS_USED.md` or in any `docs/pp_selected_*.md`. Integration Part 3 already used inverse-trig calculus items.

## Pack A: Year 11 Ch 6 Trigonometry (6G–6K)
- **Build dir:** `workspace/build/y11ch6/`.
- **Outputs:** `output/Year_11_Ext1_Ch6_Trigonometry_6G-6K_{Lesson_and_Homework,Homework_Answers}.pdf`.
- **Structure:**
  1. **Revision 6G Trigonometric identities (PDF ~286–291), homework only.** Short summary boxes of the book's identity boxes (verbatim), then a revision homework set from Exercise 6G in Easy, Medium and Hard bands, using the book's Foundation, Development and Challenge labels. Add a past-paper set if clean identity items exist.
  2. **Lesson 6H Trigonometric equations (PDF ~292–297), full teaching.** Concepts, tutor demo, your turn, the book's worked examples, Exercise 6H in its bands, then a past-paper mini exam of 15–22 marks.
  3. **Revision 6I The sine rule and the area formula (~298–307) and 6J The cosine rule (~308–313), homework only.** Summary boxes, then a revision homework set from 6I and 6J in bands, plus a past-paper set.
  4. **Lesson 6K Problems involving general triangles (~314–), full teaching,** with the same structure as 6H. End with the in-scope questions from the Chapter 6 review.
- **Past-paper catalogue:** `docs/pp_candidates_y11ch6.md`. Selection record: `docs/pp_selected_y11ch6.md`.

## Pack B: Year 11 Ch 17 Inverse trigonometric functions (teaching)
- **Build dir:** `workspace/build/y11ch17/`.
- **Outputs:** `output/Year_11_Ext1_Ch17_Inverse_Trig_{Lesson_and_Homework,Homework_Answers}.pdf`.
- **Lessons:** one per section, 17A–17G (PDF ~794–835: 17A 794, 17B 805, 17C 809, 17D 814, 17E 820, 17F 824, 17G 830). Read the real titles of 17E and 17F from the book. Full teaching in each, with the Chapter 17 review at the end.
- **Revision page:** the prerequisites, which are inverse functions (Y11 Ch 16), exact values and the graphs of sin, cos and tan.
- **Past papers:**
  - Catalogue: `docs/pp_candidates_y11ch17.md`. Selection record: `docs/pp_selected_y11ch17.md`.
  - Take only items that need nothing beyond the section they are used in. Calculus of the inverse trig functions belongs to Year 12.
  - A shortfall is allowed under house rule 8.
