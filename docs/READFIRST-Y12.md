# READFIRST: Year 12 Maths Lessons, Textbook Homework and Past-Paper Homework

## 0. Instruction Priority and Conflict Resolution

These instructions are cumulative, but **later user updates override earlier rules** unless the user explicitly says otherwise.

Follow the user's latest explicit instructions for scope, length, sources and delivery. Maintain mathematical correctness; flag and correct source errors rather than reproduce them. Within the agreed scope, use the school course plan to determine what belongs in the lesson, the textbook for teaching detail, and this file and the template for structure and presentation. Readability and teaching completeness take priority over compactness.

This file governs future tutoring-material requests. Reading or updating it does not itself instruct you to generate a lesson or send an email.

---

# 1. Core Objective

Create **one maths tutoring lesson at a time** using:

1. A full textbook PDF.
2. The provided lesson/homework design template and authoring files.
3. The requested topic, chapter, section, subtopic, or lesson focus.
4. An optional revision topic.
5. Any provided student level, ability, school context, or curriculum context.
6. The Year 12 school scope and sequence.
7. Past-paper sources specified by the user, such as uploaded papers, links, named schools, examination years or a question repository.

The standard pack has three distinct parts: a lesson, textbook homework, and additional past-paper homework. Past-paper homework supplements textbook practice; do not silently replace or reduce textbook homework to make room for it. See Section 11A for source, selection and solution rules.

The textbook is not just a question source. It is the:

- teaching reference within the agreed syllabus,
- teaching sequence,
- method source,
- notation source,
- difficulty source,
- main question bank.

The final material should support:

- concept mastery,
- textbook-aligned methods,
- independent homework practice,
- exam/homework readiness,
- clean printable PDF output.

Do **not** generate from the topic name alone.

---

# 1A. Year 12 Course and Planning

Default to Year 12 Mathematics Advanced for this student unless the user specifies otherwise. The supplied school document is the **2026–27 RGHS Maths Advanced-only scope and sequence (Draft 1)**. Treat it as the supplied draft plan, not as proof of the latest official syllabus or final assessment dates.

The uploaded **Math Textbook CMS6 Ext1 Y12.pdf** covers both Advanced and Extension 1. Its title does not mean the student takes Extension 1. Select only course-relevant sections and questions; do not include Extension 1-only topics simply because they occur in the book.

Use the school plan to choose topic boundaries and order, then use relevant textbook teaching and exercises for depth. Where the older textbook and the school plan differ, do not assume a one-to-one chapter match. Consult current official syllabus material if a scope question remains unresolved, or ask the user for the required school detail.

The supplied Year 12 plan starts with further graph transformations and modelling, followed by polynomial-only applications of calculus and polynomial-only integration. Respect such restrictions until the corresponding later material has been taught.

For a full-chapter lesson, teach each subchapter thoroughly before moving to the next. Repeat explanation → worked example → student practice for each knowledge point; do not put all theory before all practice. No fixed two-page limit applies.

Before constructing a substantial full-length pack, propose its approximate lesson/homework/solution page counts and teaching workload, and check preferences unless already settled for that task. Include the extra past-paper workload in that estimate. Do not ask again for preferences already supplied. Do not apply another student's pace or time limit to this student without evidence.

Google Slides or another slide deck is an additional deliverable only when requested. If requested, match the lesson sequence and notation and state accurately whether a native Google Slides deck or an importable presentation was created.

---

# 2. File Intake

## 2.1 Read All Non-Textbook Files First

Before generating output, inspect **all non-textbook files** provided by the user, including:

- lesson design/template files,
- authoring guides,
- formatting instructions,
- style guides,
- example finished lessons,
- component files,
- marking/answer-format instructions,
- user notes,
- `READFIRST` files.

These files define how the final output should be structured, formatted, rendered, exported, and checked.

## 2.2 Textbook PDF Intake

For the textbook PDF, do **not** read the entire textbook unless necessary.

Instead:

1. Use the user’s topic/chapter/section/page information to locate the relevant textbook section.
2. Create a PDF-page-to-printed-page conversion map for the relevant area.
3. Read the relevant teaching pages, worked examples, exercises, and nearby supporting pages.
4. Inspect adjacent pages if the section seems incomplete.
5. Avoid unrelated textbook chapters unless needed for revision, prerequisites, or context.

Summary:

```text
Read all uploaded instruction/template/design files.
For the textbook, read only the relevant section and nearby supporting pages.
```

If multiple textbook PDFs are uploaded, identify which one matches the requested lesson before extracting content.

---

# 3. Textbook Navigation and Page Mapping

When a full textbook PDF is provided, do not assume the PDF page number equals the printed textbook page number.

Distinguish between:

1. **PDF page number**  
   The page index used by the PDF viewer or file reader.

2. **Printed textbook/content page number**  
   The page number visible on the textbook page.

Before generating the lesson:

1. Locate the relevant chapter/section/subtopic.
2. Identify the printed textbook page numbers.
3. Identify the corresponding actual PDF pages.
4. Create a local page-conversion map.
5. Check whether the offset is consistent.
6. If the offset changes, use a local mapping instead of assuming one global offset.
7. Record both printed page numbers and PDF page numbers in the tutor/audit notes.

Example:

```text
Textbook Navigation Note:
Relevant section: Chapter 5, Section 5.2
Printed textbook pages: 112–116
PDF pages: 128–132
Observed local offset: PDF page = printed page + 16
```

This navigation note belongs in tutor/audit notes, not in the student-facing material.

---

# 4. Lesson Scope and Textbook Sequence

## 4.1 One Lesson Per Textbook Topic

A lesson should normally correspond to **one textbook topic, subtopic, or clearly bounded textbook section**.

Default:

```text
One textbook topic/subtopic/section = one tutoring lesson.
```

Do not merge multiple unrelated textbook sections into one lesson unless the user explicitly asks.

Do not split one textbook subtopic into multiple lessons unless:

- the section is too large for the template,
- important teaching detail would be too compressed,
- the topic naturally contains multiple distinct methods,
- the user asks for a split.

If a split is needed, recommend it clearly:

```text
Recommended split:
Lesson 1: [first part]
Lesson 2: [second part]
```

Do not compress away important textbook teaching detail just to force everything into one lesson.

## 4.2 Follow Textbook Chapter Sequence

Follow the school plan for topic order and scope. Within each selected topic, follow the textbook’s teaching sequence unless there is a clear pedagogical reason not to.

The order of lessons should normally match the order of textbook topics/subtopics, because the textbook sequence usually builds prerequisites gradually.

Within a lesson, teach the subskills in the same order the textbook introduces them.

Do not jump ahead to:

- later methods,
- harder cases,
- later-chapter techniques,
- off-syllabus shortcuts.

If reordering, skipping, combining, or splitting textbook content, explain the reason in tutor/audit notes.

Default:

```text
One textbook chapter sequence = the lesson sequence.
One textbook topic/subtopic = one tutoring lesson.
```

---

# 5. Textbook Teaching-Part Rule

The textbook’s **teaching part** is the primary source for how the concept should be taught within the agreed Year 12 course scope. The no-omission rule applies to relevant in-scope content, not every Extension 1 section in the book.

Use the textbook as the source of truth for:

- concept explanation,
- terminology,
- notation,
- definitions,
- formulas,
- key derivations,
- taught methods,
- method sequence,
- worked-example reasoning,
- diagrams and visual reasoning,
- warnings and common mistakes,
- prerequisite assumptions,
- level of abstraction,
- difficulty.

Do **not** use the textbook only as a question bank.

## 5.1 Required Textbook Reading

After locating the correct textbook section, inspect:

- chapter heading,
- section heading,
- subheading,
- learning objective if present,
- textbook teaching explanation,
- definitions,
- formulas,
- key derivations,
- method derivations,
- stated rules,
- worked examples,
- exercise questions,
- challenge/application questions,
- diagrams, graphs, tables, or special notation,
- answer section if available,
- order of difficulty,
- repeated question structures,
- common implied misconceptions,
- warnings or special cases.

## 5.2 No-Omission Rule

Do **not** reduce the textbook’s teaching part to only a few key points.

Preserve all relevant teaching details for the requested textbook topic, including:

- the textbook’s stated method,
- each important step in the method,
- why the method works if the textbook explains it,
- any derivation used to introduce a formula or rule,
- any special notation or convention,
- diagram-based reasoning,
- constraints, exceptions, special cases, or warnings,
- worked-example techniques students are expected to imitate.

You may compress wording, but you must not delete important mathematical content.

If the textbook teaches a derivation, include the derivation or a compact version of it.

If the textbook teaches multiple cases within the requested topic, include all relevant cases unless the user explicitly narrows the lesson.

If the textbook introduces a formula through reasoning, do not present only the final formula unless space genuinely prevents it. If space is limited, add a page or place the reasoning in a student-facing worked example; do not move essential teaching into tutor-only notes.

## 5.3 Teaching Detail Inventory

Before generating the student-facing lesson, create a tutor/audit inventory:

```text
Teaching details found:
1. Definition/rule:
2. Formula:
3. Derivation or reasoning:
4. Required method steps:
5. Worked-example method:
6. Diagram/table/graph details:
7. Special cases/restrictions:
8. Common warnings/mistakes:
9. Prerequisite assumptions:
10. Details included in final lesson:
11. Details not included and why:
```

Do not omit an item silently. If a textbook detail is excluded, explain why.

## 5.4 No Off-Syllabus Drift

Do not introduce off-syllabus methods, shortcuts, alternative techniques, or advanced extensions unless:

1. the textbook already uses them,
2. the user explicitly asks for them,
3. they are needed to clarify a misconception.

If adding anything not directly from the textbook teaching part, label it in tutor/audit notes as:

```text
Supplementary explanation added by AI
```

and explain why it was added.

If the textbook method differs from a common alternative method, follow the textbook method by default.

---

# 6. Flexible Pedagogy vs Fixed Formatting

The design/template is mainly a **formatting, layout, and visual style system**, not a strict pedagogical limit.

The design controls:

- visual style,
- typography,
- spacing,
- page layout,
- section appearance,
- print/PDF formatting,
- student-facing cleanliness.

The textbook controls:

- teaching sequence,
- concept depth,
- number of subskills,
- method structure,
- worked-example needs,
- amount of practice,
- mathematical content.

If the textbook requires more teaching structure than the default template shows, adapt the content structure while preserving the design style.

## 6.1 Concept Teaching Flexibility

The Concept section does **not** have to follow the default concept layout rigidly.

Use the textbook teaching part to decide what the Concept section needs.

Depending on the topic, the Concept section may include any suitable combination of:

- definition,
- rule,
- formula,
- derivation,
- diagram,
- notation explanation,
- method steps,
- special cases,
- restrictions,
- warnings,
- compact mini-example,
- visual reasoning,
- multiple sub-concepts.

Do not force every topic into only:

```text
rule + formula + vocab + steps
```

Use those fields only when they fit the textbook content.

If the textbook teaches through a derivation, diagram, or worked reasoning, include that structure even if it requires adapting the concept area.

If the concept is too large for the standard concept box, use one of these approaches:

1. split the concept into smaller labelled subparts,
2. move part of the reasoning into the worked example,
3. add a second concept/method block,
4. add a diagram or table,
5. use an extra page if necessary,
6. recommend splitting the textbook topic into two lessons if it cannot fit without losing important teaching detail.

Do not omit important teaching detail just because the default concept layout is small.

## 6.2 Worked Example Flexibility

The default template may show one worked example, but the lesson does **not** have to contain only one worked example.

Use as many worked examples as the textbook topic reasonably requires.

Multiple worked examples are appropriate when:

- the textbook has multiple distinct worked-example styles,
- the topic has multiple cases,
- the method changes depending on question type,
- the textbook teaches a derivation followed by a procedure,
- students need one example per main question archetype,
- homework would be difficult without a reference example for each style.

Default:

```text
One main question style usually needs its own worked reference example.
```

If space is limited, prioritise worked examples for the most important or most error-prone styles, then record omitted examples in tutor/audit notes.

## 6.3 Other Section Flexibility

Other lesson sections may also be adapted when the textbook requires it.

You may adjust:

- number of guided practice questions,
- number of worked examples,
- number of concept blocks,
- whether a diagram is included,
- whether an exam strategy section is useful,
- whether common mistakes need a larger or smaller section,
- whether a key takeaway is enough or needs multiple takeaways,
- whether an additional page is needed.

Do not add filler sections merely because the template has them.

Do not omit useful sections merely because the example template does not show them.

---

# 7. Lesson Structure

Default lesson structure:

```text
Revision, if mentioned
→ Concept
→ Tutor Demo Example(s)
→ Student Attempt(s)
→ Worked Example(s) for Homework Reference
→ Textbook Homework
→ Past-Paper Homework
→ Answers and Worked Solutions
```

This structure may be expanded when the textbook topic requires multiple concept blocks, multiple methods, or multiple worked examples.

## 7.1 Revision

Include revision only if the user provides a revision topic or explicitly asks for revision.

If no revision topic is provided:

- do not create a formal revision section,
- optionally include a short prerequisite note in tutor/audit notes.

If revision is included:

- keep it short,
- use it to activate prerequisite knowledge,
- include only questions directly relevant to the lesson.

## 7.2 Concept

The Concept section should be based mainly on the textbook teaching explanation.

It should include whatever the topic genuinely needs:

- main rule or idea,
- textbook method,
- essential notation,
- key formula if relevant,
- derivation or reasoning if the textbook teaches one,
- key warning or common trap,
- diagram or visual reasoning if useful,
- special cases if part of the textbook section.

Be concise, but do not delete important mathematical content.

## 7.3 Tutor Demo Example

For each main question style:

- include 1 tutor demo example where appropriate,
- source it mainly from textbook worked examples,
- exact textbook questions are allowed sometimes,
- close value-changed variants are usually preferred,
- keep the structure aligned with the textbook.

## 7.4 Student Attempt

For each main question style:

- include 1 student attempt where appropriate,
- make it structurally parallel to the tutor demo,
- make it equal or slightly easier than the tutor demo,
- avoid introducing a difficulty jump,
- usually use a close value-changed variant.

Bad:

```text
Tutor demo: Expand 4(x + 7)
Student attempt: Expand and simplify 3(x + 4) - 2(x - 5)
```

Good:

```text
Tutor demo: Expand 4(x + 7)
Student attempt: Expand 3(y + 5)
```

## 7.5 Worked Reference Example

For each main question style:

- usually include 1 worked reference example,
- make it student-facing,
- use full step-by-step working,
- keep the working clean and compact,
- source mainly from textbook worked examples or close variants.

If the textbook contains multiple important worked-example types, include multiple worked examples where applicable.

This section helps the student remember the method while doing homework.

---

# 8. Question Archetype Extraction

Do not treat every textbook question as a different style.

Group similar textbook questions into **question archetypes** or **question styles**.

For each useful question style, identify:

- source reference,
- printed textbook page,
- PDF page,
- skill tested,
- required prerequisite,
- structure,
- textbook difficulty ranking,
- typical number style,
- expected method,
- common mistake,
- whether it is suitable for demo, student attempt, worked reference, homework, challenge, or revision.

Example:

```text
Textbook questions:
Expand 3(x + 4)
Expand 5(y + 2)
Expand 7(a + 6)

These are one style, not three styles.

Question style:
a(x + b)

Skill:
Expanding a single bracket with positive integer coefficient and positive constant.

Difficulty:
Foundation / Easy.

Common mistake:
Multiplying only the first term.

Variant rule:
Change coefficient, variable, and constant while keeping the same structure and difficulty.
```

---

# 9. Question Source and Adaptation

The textbook is the main question bank for lesson examples and textbook homework. The additional past-paper homework must use the sources specified by the user; the textbook adaptation preferences below do not override Section 11A.

Use this priority order.

## 9.1 Exact Textbook Question

Exact textbook questions are allowed selectively, especially when:

- the question is particularly well-designed,
- the student may need to complete the exact assigned textbook question,
- the question is central to the textbook progression,
- using it exactly avoids distorting the skill.

Do not use exact textbook questions for everything.

## 9.2 Close Value-Changed Variant

Preferred most of the time.

Preserve:

- same mathematical structure,
- same target skill,
- same number of reasoning steps,
- same difficulty band,
- same style of numbers,
- same notation style.

Change:

- values,
- variable names,
- simple context details,
- surface wording where appropriate.

Example:

```text
Original:
Expand 3(x + 4)

Close variant:
Expand 5(y + 6)
```

## 9.3 Moderate Variant

Use when useful.

Preserve the same core skill but slightly vary the arrangement, representation, or context.

Example:

```text
Original:
Expand 3(x + 4)

Moderate variant:
A rectangle has width x + 4 and length 3. Write an expression for its area.
```

## 9.4 New Original Question

Use only when justified.

Create a new question if:

- the textbook does not provide enough practice for a subskill,
- the textbook progression has a gap,
- a common misconception needs to be targeted directly,
- an exam-style question is needed,
- an application question is needed,
- textbook questions are too repetitive,
- existing questions are poorly scaffolded,
- the student needs a smoother difficulty ramp.

When creating an original question, keep it aligned with the textbook topic, notation, level, method, and difficulty.

---

# 10. Difficulty and Textbook Ranking

Many maths textbooks classify exercises using their own ranking system, such as:

```text
Foundation
Intermediate
Extension
```

When the textbook provides this kind of ranking, use it as the primary difficulty source.

Do not rely mainly on your own judgement if the textbook already labels the question level.

The supplied Cambridge Year 12 book uses **Foundation, Development and Enrichment**, as explained in its rationale. Preserve these actual source labels in tutor notes. Development spans a range of difficulty, and Enrichment can exceed the course; do not mechanically assign these to easy, medium and hard. Check the actual skills, scope and student readiness. A hard Advanced question is not automatically Extension 1 content.

## 10.1 Default Difficulty Mapping

Use this mapping unless the textbook defines a different system:

| Textbook ranking | Internal difficulty | Template difficulty value | Colour group |
|---|---|---|---|
| Foundation | Easy / basic fluency | `easy` | Green |
| Intermediate | Medium / core practice | `med` | Amber |
| Extension | Hard / challenge | `chal` | Rose |

If a question is adapted from a textbook question, inherit the original textbook ranking unless the adaptation clearly changes the difficulty.

If the adaptation changes the difficulty, record the reason in tutor/audit notes.

## 10.2 Difficulty Tracking Across the Whole Lesson

The design/template may only visibly display coloured difficulty labels in some sections, especially homework sections.

However, difficulty should still be tracked for **all questions**, including:

- revision questions,
- tutor demo examples,
- student attempts,
- worked reference examples,
- guided practice,
- homework questions,
- standalone homework groups,
- challenge/application questions.

If the template does not visibly show a difficulty tag for a section, do **not** force a visible label into the student-facing design unless it fits cleanly.

Instead, record difficulty in tutor/audit notes.

Default:

```text
Visible difficulty labels: only where the template naturally supports them.
Internal/audit difficulty labels: every question.
```

## 10.3 Difficulty Progression

For each meaningful question style, prefer:

```text
Foundation → Intermediate → Extension
```

where the textbook provides enough material.

This replaces or refines the generic:

```text
Easy → Medium → Hard
```

If a textbook subtopic only has Foundation questions, do not invent unnecessary Intermediate/Extension questions just to fill the pattern.

If a textbook subtopic only has Foundation and Intermediate questions, do not invent Extension unless there is a clear pedagogical reason.

If Extension questions require methods not taught in the relevant textbook section, exclude them or move them to optional challenge, and explain why.

---

# 11. Textbook Homework Structure

Keep textbook homework and additional past-paper homework under separate headings. Place solutions at the end or in a separate solutions file. The rules in this section apply to textbook homework.

For each main question style, aim for approximately:

```text
3 homework questions:
1 Foundation/easy
1 Intermediate/medium
1 Extension/hard
```

Use the textbook’s Foundation/Intermediate/Extension ranking where available.

This is a guideline, not a hard quota.

Homework length should be proportional to:

- the amount of textbook content,
- the number of meaningful question styles,
- the importance of the subtopic,
- the amount of practice needed for mastery,
- the amount of space available in the template.

If a subtopic has very little content, keep the homework short rather than padding it.

If a topic has many meaningful question styles, include enough homework to cover them, but do not overload the student. Expand the template when needed rather than crowding the page.

Do not force three questions per style if doing so makes the homework bloated, repetitive, or off-topic.

Homework questions should:

- mostly come from the textbook exercise/homework section,
- include some exact textbook questions if useful,
- include close value-changed variants,
- increase difficulty gradually,
- reinforce the lesson,
- be doable independently,
- avoid requiring untaught methods,
- include hard questions only if the lesson prepared the student for them.

Hard homework questions may be:

- harder textbook-style questions,
- mixed questions,
- application questions,
- exam-style questions if appropriate.

---

# 11A. Additional Past-Paper Homework

## 11A.1 Sources Supplied by the User

Add a separate **Past-Paper Homework** section after textbook homework. The user will specify where to source these questions. Sources may be uploaded PDFs, links, named school/year papers, official examination papers, or a specified collection.

- Use only the user's specified sources for this section unless the user authorises a broader search.
- Once a source collection has been specified for this student, continue using it within its stated scope unless the user changes it. Do not repeatedly ask for the same source.
- If no source has been specified, ask which source to use. Continue useful lesson and textbook work where possible; do not invent a source or silently substitute original exam-style questions.
- If a source is inaccessible, request an upload or another authorised source. If no suitable questions are available, explain the gap to the tutor and ask whether to broaden the sources. Do not fill the section with unrelated material or imply it is complete.
- Inspect the actual paper and question, including relevant preceding parts and diagrams. A search snippet, filename or answer alone is insufficient evidence.
- Never invent school names, years, examination types, question numbers, marks or source links.

## 11A.2 Selection and Workload

Select questions that practise the current lesson and previously taught prerequisites. Prioritise varied, useful exam practice: interpretation, multi-step reasoning, unfamiliar representations, applications and common misconceptions, where the available papers support them.

- Progress from accessible applications to more demanding questions.
- Keep all required methods within the student's taught course scope. Older papers and Extension papers need individual screening; a matching topic title is insufficient.
- Do not force a fixed count, mark total or page length. As a starting estimate for an ordinary single-topic lesson, consider 3–6 substantial questions or suitable subparts, then adjust for length, complexity, source quality and the user's workload preference. This is not a minimum or quota.
- Avoid repeated questions within the pack and, where prior materials are accessible, across previous packs. Prefer different reasoning styles over near-identical numerical versions.
- Keep a reusable tutor-only record of source, year, paper, question/subpart, topic and pack used. If prior usage cannot be checked, state that limitation to the tutor rather than claiming a complete no-repeat check.
- If a repeat is deliberately requested for revision, label it briefly as “Previously practised” and identify the earlier pack if known.
- Do not extract a later part that depends on omitted results or definitions. Include the necessary earlier part or explicitly supply its given result, without revealing the answer to the retained task.
- Keep original marks where provided. Any added marks or completion times must be labelled as estimates, not official allocations.

## 11A.3 Question Fidelity and Attribution

Past-paper homework should normally contain genuine questions from the selected papers, not value-changed textbook variants presented as exam questions.

Retain original wording, mathematical conditions, values, units, diagrams, subpart dependencies and marks where available. Retyping for legibility is acceptable if it does not change meaning. Recreate diagrams accurately, checking scales, labels, shading, axes and stated conditions.

Beside each question, provide a compact source reference in this form:

```text
[School or examination authority], [year], [paper/exam title], Q[number and subpart]
```

Include a useful source link when available. Student-facing question references are useful labels and are allowed; internal page mappings and retrieval notes belong in tutor notes.

If a question is changed, identify it as **Adapted from** and keep a tutor note of the changes. Do not call an adaptation an exact past-paper question. Original exam-style questions, if separately authorised, must be labelled as original and must not be counted as sourced past-paper questions.

If text or a diagram is illegible or incomplete, verify it against another authorised copy or omit it and tell the tutor. Never reconstruct missing mathematical conditions by guesswork.

## 11A.4 Hints and Worked Solutions

By default, put one brief hint below each past-paper question, separated clearly from the question. The hint should suggest a starting point or relevant idea without revealing the answer. Omit or relocate hints if the user requests exam conditions.

Provide full worked solutions to every past-paper question in a solutions section at the end or in a separate solutions file. Include all selected subparts, key reasoning, domain restrictions, exact values or appropriate rounding, units and relevant graph features. For multiple choice, explain the correct choice; do not provide only its letter.

Solve each question independently and compare with supplied official or school solutions when available. Distinguish your worked solution from an official marking scheme. If solutions disagree, investigate and disclose any unresolved discrepancy to the tutor. Do not copy an apparent error merely because it appears in a supplied answer key.

The past-paper solution requirement overrides the normal final-answer-only default in Section 16.

---

# 12. Controlled Variation

When changing textbook questions, vary values intelligently.

Do not randomly make the question harder.

Preserve the original difficulty unless intentionally increasing difficulty for progression.

Control these features:

| Feature | Rule |
|---|---|
| Coefficients | Keep similar size unless intentionally increasing difficulty |
| Negatives | Only introduce if the textbook has introduced them or the lesson requires them |
| Fractions | Avoid unless present in the textbook section or requested |
| Decimals | Avoid unless present in the textbook section or requested |
| Variables | Can change, but keep notation simple |
| Diagrams | Preserve diagram logic if adapting a diagram-based question |
| Context | Keep realistic and age-appropriate |
| Number of steps | Match the source question unless intentionally increasing difficulty |
| Answers | Prefer clean answers unless messy answers are pedagogically useful |

Bad adaptation:

```text
Original:
Expand 3(x + 4)

Bad variant:
Expand and simplify 3(x + 4) - 2(5x - 7)
```

Good adaptation:

```text
Original:
Expand 3(x + 4)

Good variant:
Expand 5(y + 6)
```

---

# 13. Misconception Targeting

Include misconception targeting where useful.

Common methods:

- one carefully chosen trap question,
- one error-correction question,
- one student attempt that tests a common mistake,
- a brief warning in the concept section,
- a tutor note explaining what mistake to watch for.

Do not overuse trick questions.

A misconception question should target a real likely error, not just be difficult for its own sake.

---

# 14. Mathematical Typesetting

Maths should be typeset cleanly.

Use **LaTeX as the source format for mathematical notation** wherever practical, especially for:

- fractions,
- indices and powers,
- square roots,
- algebraic expressions,
- equations,
- inequalities,
- functions,
- coordinates,
- ratios,
- surds,
- logarithms,
- exponential notation,
- trigonometric notation,
- set notation,
- probability notation,
- multi-line worked solutions.

## 14.1 Render LaTeX

LaTeX source should be **rendered**, not printed as raw LaTeX.

Preferred rendering options:

1. Use an existing math-rendering component if the template provides one.
2. Use KaTeX or MathJax if available.
3. Add a small reusable `MathInline` / `MathBlock` component if modifying the template is allowed and necessary.
4. For very simple expressions only, use clean Unicode formatting if LaTeX rendering is unavailable.
5. If no rendering option is available, keep the expression readable and record the limitation in tutor/audit notes.

Do not output raw expressions like:

```text
sqrt(x^2 + 4)/3
```

when they should be properly typeset.

Prefer rendered forms equivalent to:

```latex
\dfrac{\sqrt{x^2+4}}{3}
```

## 14.2 Inline vs Display Maths

Use inline maths for short expressions inside sentences.

Examples:

```latex
\(x+3=7\)
\(a^2+b^2=c^2\)
```

Use display maths for important formulas, derivations, and multi-line working.

Examples:

```latex
\[
a^2+b^2=c^2
\]
```

```latex
\[
\begin{aligned}
3x+5 &= 20 \\
3x &= 15 \\
x &= 5
\end{aligned}
\]
```

## 14.3 Fractions

Fractions should look like proper mathematical fractions.

Do not write student-facing fractions as slash notation such as:

```text
2/3
(x+1)/(x-4)
sqrt(5)/2
```

unless slash notation is genuinely part of the textbook style or is being discussed as notation.

Use LaTeX fraction notation.

For student-facing lesson content, worked examples, homework questions, and answer keys, use display-style fractions where readability matters:

```latex
\dfrac{2}{3}
\dfrac{x+1}{x-4}
\dfrac{\sqrt{5}}{2}
```

Use `\dfrac{...}{...}` especially for:

- standalone fractions,
- algebraic fractions,
- fractions inside equations,
- worked-solution lines,
- homework questions,
- answer keys,
- formulas students need to read clearly.

Use `\frac{...}{...}` only when the rendered result remains clear and well-sized in the final PDF.

If inline `\dfrac` makes the line too tall or causes spacing problems, move the expression to display maths instead of reverting to slash notation.

Avoid:

```text
Solve x + 2/3 = 5.
```

Prefer:

```latex
Solve \(x + \dfrac{2}{3} = 5\).
```

or:

```latex
\[
x + \dfrac{2}{3} = 5
\]
```

## 14.4 Worked Solutions

Worked examples should use clean aligned mathematical working where possible.

Prefer aligned steps over long inline strings.

Good:

```latex
\[
\begin{aligned}
3x+5 &= 20 \\
3x &= 15 && \text{subtract 5 from both sides} \\
x &= 5 && \text{divide both sides by 3}
\end{aligned}
\]
```

Avoid:

```text
3x + 5 = 20 -> 3x = 15 -> x = 5
```

unless the template cannot render multi-line maths.

## 14.5 Consistency

Use consistent mathematical notation throughout:

- proper superscripts for powers,
- fraction notation instead of slash notation for non-trivial fractions,
- radical notation for square roots,
- aligned equations for solving,
- consistent mathematical symbols,
- no raw ASCII where typeset notation is practical.

Avoid mixing raw ASCII, Unicode, and LaTeX in the same section unless unavoidable.

---

# 15. Template and Authoring Rules

The user will provide an existing design/template.

Place generated lesson and homework content directly into that design/template where possible.

Treat the template primarily as a **formatting and visual design guide**, not as a rigid pedagogical limit.

Follow the template’s:

- typography,
- spacing,
- visual style,
- section styling,
- page structure where suitable,
- student-facing vs tutor-facing separation.

You may adapt the section structure when textbook teaching requires it, especially for:

- concept teaching,
- derivations,
- multiple worked examples,
- multiple methods or cases,
- diagrams,
- extended worked reasoning,
- additional reference examples.

Do not redesign the visual style unless asked.

Do not force textbook content into a template shape that causes important teaching details to be omitted.

If the template has placeholders, replace them cleanly.

Keep internal tutor/audit notes in a separate tutor file by default, under:

```text
Tutor/Audit Notes
```

## 15.1 JSX / React Template Handling

If the template is React/JSX-based:

- put lesson content in the intended content file/module,
- avoid editing renderer/layout files unless necessary,
- use JSX values where helpful,
- use reusable diagram/math components where available,
- add minimal new components only when needed,
- preserve the design system.

If modifying the renderer is necessary, do so minimally and explain the change in tutor/audit notes.

## 15.2 Diagrams

Use diagrams when they aid understanding, especially for geometry, graphs, probability, ratio, transformations, and measurement.

If none of the provided diagram components fit, create a simple clean inline SVG or reusable diagram component.

Diagram rules:

- keep labels readable,
- avoid label overlap,
- preserve mathematical structure,
- use clean geometric diagrams,
- keep grayscale visibility,
- avoid decorative illustration.

---

# 16. Answers and Hints

For ordinary textbook practice questions:

- provide final answers only, unless full working is requested.

For past-paper homework:

- provide a brief hint below every question and full worked solutions at the end, following Section 11A.

For hard questions:

- provide a brief hint if useful.

For worked reference examples:

- provide full step-by-step working.

For tutor demo examples:

- include enough working or explanation for the tutor to teach from if the design requires it.

For student attempts and homework:

- do not place answers immediately beside the question unless the design requires it,
- put answers in a separate answer section or tutor section.

Include a complete proof when it is the task set by a selected question or part of the agreed teaching scope; omit unrelated extended proofs.

---

# 17. Student-Facing Output vs Tutor/Audit Notes

## 17.1 Student-Facing Material

Student-facing material should include only what the student needs:

- lesson title,
- revision if provided,
- concept,
- tutor demo example,
- student attempt,
- worked reference example,
- textbook homework,
- past-paper homework with compact source references and hints,
- answers and worked solutions in their separate end section.

Keep it clean and uncluttered.

Do not include:

- tutor/audit source notes,
- page conversion notes,
- internal difficulty rationale,
- raw source mappings,
- excessive labels,
- debugging comments,
- file names,
- code comments,
- unrendered JSX,
- unrendered LaTeX,
- placeholder text,
- unused template fields.

## 17.2 Tutor/Audit Notes

Tutor/audit notes should include:

- textbook navigation note,
- page conversion map,
- textbook section used,
- teaching detail inventory,
- question archetype map,
- source mapping,
- adaptation type,
- textbook ranking,
- internal difficulty,
- visible difficulty label status,
- answer key,
- hints for hard questions,
- skipped textbook styles and reasons,
- assumptions made,
- supplementary explanation added by AI,
- template/rendering changes if any.

Keep audit notes separate from the student-facing material unless the user explicitly wants them included.

---

# 18. Source Mapping

Every generated or selected question should have a source mapping in tutor/audit notes.

For past-paper questions also record: school/authority, year, paper title and course, original question/subparts, original marks if given, source file/link and page, exact/adapted status, verified solution source if available, prerequisite fit, and prior-use status. Do not apply invented textbook rankings to past-paper questions.

Use this format:

```text
Item:
Source:
Printed textbook page:
PDF page:
Original reference:
Adaptation type:
Textbook ranking:
Internal difficulty:
Visible difficulty label:
Purpose:
Reason for selection:
```

Adaptation types:

```text
Exact textbook question
Close value-changed variant
Moderate variant
New original question
Exact past-paper question
Adapted past-paper question
```

Example:

```text
Item: Homework Q3
Source: Textbook Exercise 4B Q7
Printed textbook page: p. 112
PDF page: p. 126
Adaptation type: Close value-changed variant
Textbook ranking: Intermediate
Internal difficulty: med
Visible difficulty label: Medium, if the template section supports it
Purpose: Independent practice on expanding a single bracket
Reason for selection: Reinforces the same archetype as the tutor demo with changed values
```

---

# 19. Question Archetype Map

Include a tutor/audit archetype map.

Suggested fields:

```text
Style ID:
Source examples:
Printed pages:
PDF pages:
Question structure:
Skill:
Textbook ranking range:
Difficulty range:
Common mistake:
Used for:
Variant rule:
```

Example:

```text
Style A
Source examples: Worked Example 3, Exercise 4B Q1–4
Printed pages: 112–113
PDF pages: 126–127
Question structure: a(x + b)
Skill: Expand a single bracket
Textbook ranking range: Foundation
Difficulty range: Easy
Common mistake: Multiplying only the first term
Used for: Tutor demo, student attempt, worked reference, homework Q1–3
Variant rule: Change coefficient, variable, and constant while keeping positive integers
```

---

# 20. Skipping, Combining, or Scaling Textbook Styles

You may skip or combine textbook question styles if they are:

- repetitive,
- too similar to another style,
- outside the lesson focus,
- too easy for the student,
- too advanced for the lesson,
- low pedagogical value,
- unsupported by the textbook teaching section.

If you skip or combine a style, explain why in tutor/audit notes.

Example:

```text
Skipped Exercise 4B Q15–17 because they introduce fractions, which are not taught in this lesson section and would create an unnecessary difficulty jump.
```

Scale practice to the textbook content.

If the subtopic is short, homework should be short.

If the subtopic is substantial and contains many meaningful question styles, homework may be longer.

Do not pad homework just to reach a fixed number of questions.

---

# 21. PDF Export and Delivery

The final tutoring lesson and homework material should be output as a **PDF**.

After generating the material inside the provided design/template:

1. Export the final student-facing material as a polished PDF.
2. Put student answers and worked solutions at the end or in a separate solutions PDF, according to the agreed format. Keep internal tutor/audit notes in a separate tutor file unless explicitly requested otherwise.
3. Name the PDF clearly using lesson topic, year level, and date if available.

Default filename:

```text
[Year Level]_[Topic]_Lesson_and_Homework.pdf
```

Example:

```text
Year_12_Graph_Transformations_Lesson_and_Homework.pdf
```

Deliver the requested student PDF and any separate solutions/tutor file with clear download links. Keep internal source mappings and production notes out of the student PDF; use a separate tutor file if needed.

Email only when the user explicitly requests or has already authorised it for the current task. The usual recipient, when requested, is `c888michael@gmail.com`. Do not treat reading this file as permission to email. Verify the recipient, send only the requested finished files, and never claim an email was sent unless it actually succeeded. If email is unavailable, provide the files and state that limitation.

---

# 22. Visual QA and Defect Prevention

The final PDF must be clean enough to hand to a student without manual repair.

Do not rely only on HTML/browser preview.

After exporting to PDF:

1. Render the final PDF pages as images or screenshots.
2. Inspect every page visually.
3. Check mathematical notation carefully.
4. Fix layout or rendering issues.
5. Re-export and re-check if needed.

Do not say the PDF was visually checked unless the exported PDF itself was inspected.

If PDF visual inspection cannot be performed in the available environment, state that limitation clearly and do not claim verification.

## 22.1 Common Visual Defects to Prevent

Check for and prevent:

- cramped sections,
- too much content forced onto one page,
- text overflow,
- clipped text,
- clipped equations,
- clipped diagrams,
- equations extending outside boxes,
- diagrams extending outside boxes,
- tiny unreadable maths,
- fractions rendered too small,
- slash-style fractions such as `2/3`,
- raw LaTeX appearing in the PDF,
- broken or unrendered LaTeX,
- overlapping stacked fractions,
- clipped square roots,
- misplaced exponents or subscripts,
- multi-line equations with poor alignment,
- inconsistent maths font sizes,
- answers or hints beside student questions when they should be separate,
- missing answer spaces,
- answer spaces covering or touching question text,
- ruled/grid working space interfering with text,
- black artefacts from borders, backgrounds, or line patterns,
- unnecessary thick borders,
- section headings orphaned at the bottom of a page,
- a question split awkwardly across pages,
- headers or footers overlapping content,
- content hidden behind fixed-position elements,
- diagram labels too small,
- diagram labels overlapping lines,
- low colour contrast,
- low grayscale contrast,
- inconsistent spacing between question groups,
- empty sections rendered accidentally,
- duplicate section headings,
- incorrect page numbers or footer text,
- final PDF differing from the HTML/browser preview.

## 22.2 Layout Prevention

Do not force everything into the default page count if readability suffers.

If the lesson needs more room:

1. add a page,
2. reduce non-essential decorative elements,
3. shorten wording without deleting mathematical content,
4. move tutor/audit notes to a separate section or separate PDF,
5. split the textbook topic into multiple lessons if necessary.

Do not reduce maths size until it becomes difficult to read.

Do not compress worked solutions until alignment becomes unclear.

Do not keep a diagram if it becomes too small to read; resize or redesign it.

## 22.3 Maths Layout

For mathematical notation:

- use display maths for important formulas and worked lines,
- use aligned equations for multi-step working,
- use `\dfrac{...}{...}` for readable student-facing fractions,
- avoid long equations inside narrow boxes,
- break long equations over multiple aligned lines,
- avoid nested fractions unless necessary,
- avoid placing large display fractions inside dense paragraphs,
- keep enough vertical spacing around display maths,
- check that equation labels and explanations do not collide.

If an expression is too long for the available width, rewrite the layout, not the mathematics.

## 22.4 Diagram Layout

For diagrams:

- keep labels readable,
- keep labels away from lines and vertices,
- ensure arrows, axes, ticks, and labels fit inside the frame,
- preserve aspect ratio,
- avoid overly decorative diagrams,
- use clean geometric diagrams,
- check grayscale visibility,
- check that diagrams do not make the worked example too cramped.

If the textbook uses a diagram, reproduce the mathematical structure of the diagram, not necessarily its exact visual style.

## 22.5 Print and Grayscale

Before final output, check the material in print/PDF view.

If the template has a grayscale preview mode, use it.

Verify:

- colour is not the only way information is communicated,
- difficulty labels remain distinguishable in grayscale,
- lines, boxes, and grids are not too dark,
- faint lines are still visible but not distracting,
- backgrounds do not create black patches,
- text remains readable when printed.

If ruled working lines or grid backgrounds create artefacts, simplify them or use clean blank working space.

## 22.6 Final Visual Pass

Before delivering, perform a final page-by-page visual pass.

For each page, check:

```text
Page:
1. Any overflow?
2. Any clipped text/math?
3. Any raw LaTeX?
4. Any ugly slash fractions?
5. Any equation misalignment?
6. Any diagram issue?
7. Any crowded section?
8. Any orphan heading?
9. Any missing answer space?
10. Any print/grayscale issue?
Fix needed:
```

Only deliver the PDF after all pages pass this check.

---

# 23. Quality-Control Checklist

Before finalising, check:

1. Did you inspect all non-textbook instruction/template/design files?
2. Did you locate and read the relevant textbook section?
3. Did you distinguish PDF page numbers from printed textbook page numbers?
4. Did you create a page-conversion map for the relevant section?
5. Did you follow the textbook’s chapter/topic sequence?
6. Did you cover the agreed lesson or full-chapter scope without compressing away essential teaching?
7. Did you use the textbook teaching part as the main source for the Concept section and method?
8. Did you preserve relevant teaching details, including methods, derivations, notation, warnings, and special cases?
9. Did you avoid off-syllabus methods unless justified?
10. Did you use the textbook for ordinary practice and the specified papers for additional past-paper homework?
11. Did you group similar textbook questions into archetypes?
12. Did you avoid treating every question as a separate style?
13. Did you use worked examples mainly for lesson examples?
14. Did you use exercise/homework questions mainly for homework?
15. Did the lesson follow the required structure or a justified flexible extension?
16. Did each main question style get a tutor demo, student attempt, worked reference, and homework practice where appropriate?
17. Did textbook homework progress sensibly using actual source labels and course-scope screening?
18. Is homework length proportional to the textbook content and number of meaningful question styles?
19. Did you track difficulty for every question in tutor/audit notes?
20. Did you avoid unnecessary difficulty jumps?
21. Did you include exact textbook questions only selectively?
22. Did you use close value-changed variants where useful?
23. Did you create original questions only when justified?
24. Did you provide answers?
25. Did you include hints for hard questions where useful?
26. Did you keep student-facing material clean?
27. Did you include tutor/audit notes separately?
28. Did you use the provided design/template as the formatting/style system without letting it erase necessary teaching detail?
29. Did you adapt concept/worked-example structure where the textbook required it?
30. Did you typeset mathematical expressions cleanly using rendered LaTeX or the best available equivalent?
31. Did you use proper rendered fractions such as `\dfrac{2}{3}` instead of slash-style fractions such as `2/3`?
32. Did you render the exported PDF pages as images/screenshots and visually inspect every page?
33. Did you check for equation misalignment, overlapping fractions, clipping, raw LaTeX, and page overflow?
34. Did you check for cramped sections, orphan headings, bad page breaks, missing answer space, diagram issues, low contrast, and print/grayscale artefacts?
35. Did you verify that mathematical notation renders correctly in the exported PDF?
36. Did you export the final material as a PDF?
37. Was any email delivery explicitly authorised and actually completed before claiming success?
38. Did you add distinct textbook and past-paper homework sections, or clearly report missing past-paper sources?
39. Did every past-paper question come from an inspected, user-specified source, with accurate attribution and marks?
40. Did you verify course alignment, prerequisite coverage, question dependencies and prior use where records were available?
41. Did you provide a brief hint and independently checked full worked solution for each past-paper question?
42. Did you screen the mixed Advanced/Extension textbook and older papers against the agreed school scope?

If any check fails, revise before giving the final output.

---

# 24. Default Behaviour

Unless the user specifies otherwise, use these defaults:

```text
Subject: Year 12 Mathematics Advanced unless specified otherwise
Scope: One lesson at a time
Lesson boundary: Requested topic/subtopic; for a full chapter, teach each subchapter thoroughly in order
Course scope: User instructions and school scope and sequence
Textbook role: Teaching detail, methods, notation and textbook practice within the agreed course scope
Chapter order: Follow school topic order; use textbook sequence within selected topics
Revision: Only if provided
Concept: Based on textbook teaching section; flexible structure; concise but complete
Teaching details: Do not omit relevant methods, derivations, notation, warnings, special cases, or worked-example reasoning
Tutor demo: Usually 1 per main question style
Student attempt: Usually 1 per main question style
Worked reference example: Usually 1 per main question style, full step-by-step; include multiple where needed
Textbook homework: Around 3 questions per main question style where useful; use actual textbook bands and screen for course fit
Past-paper homework: Additional separate section, from user-specified sources only, selected for variety and taught skills
Difficulty source: Actual textbook labels; the supplied Cambridge Year 12 book uses Foundation/Development/Enrichment. Check scope and individual difficulty.
Difficulty labels: Track difficulty for every question in tutor/audit notes; show visible labels only where the template supports them
Question source: Textbook and variants for ordinary practice; genuine past-paper questions from user-specified sources for the extra section
Original questions: Allowed only with rationale
Math rendering: Use rendered LaTeX/KaTeX/MathJax or a clean equivalent
Fractions: Prefer proper rendered fractions such as `\dfrac{2}{3}` over slash notation such as `2/3`
Answers: Final answers for ordinary textbook practice; full worked solutions for all past-paper homework
Hints: Brief hints for hard textbook questions and each past-paper question unless exam conditions are requested
Student-facing output: Clean and uncluttered
Tutor/audit output: Include navigation, page mapping, teaching inventory, source mapping, archetype map, answers, and rationale
Design/template: Use the provided template as the formatting/style system; adapt section structure when textbook teaching requires it
Visual QA: Prevent cramped layout, clipping, overflow, raw LaTeX, unreadable maths, diagram issues, bad page breaks, and print/grayscale artefacts before delivery
Final output format: Export as PDF
Email delivery: Only when explicitly authorised for the task and supported by available tools
```

---

# 25. Workflow for Future Lesson Requests

When the user requests a lesson or homework pack:

1. Inspect the supplied instructions, template and relevant school plan.
2. Confirm unresolved topic, course, length or workload preferences when material; reuse decisions already made.
3. Locate and read relevant textbook teaching, examples and exercises. Keep page conversions in tutor notes.
4. Identify all in-scope subskills and teach them progressively with examples and immediate practice.
5. Prepare textbook homework with a sensible difficulty progression.
6. Inspect the user's specified past-paper sources. Select complementary questions, check previous use where possible, and preserve attribution and dependencies.
7. Add separate past-paper homework with hints and full worked solutions.
8. Check the mathematics and compare with source answers where available.
9. Export the requested PDFs, inspect every rendered page, and repair layout defects before delivery.
10. Keep internal production notes separate. Save and provide the finished files. Email only if explicitly authorised for the task.

When the user asks only to edit these instructions, edit the instruction file; do not start producing a lesson.

Use natural student-facing headings such as the topic name, “Worked Example”, “Practice”, “Textbook Homework”, “Past-Paper Homework” and “Worked Solutions”. Avoid “Textbook Method”, page-mapping labels, audit language, AI-related wording and unnecessary production commentary in student materials.

Do not claim source access, duplicate checking, mathematical verification, visual inspection or delivery that did not actually occur.
