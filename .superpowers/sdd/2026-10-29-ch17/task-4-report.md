# Task 4 report: Lesson 17C Normal approximations to a binomial

Status: DONE_WITH_CONCERNS (minor; see Concerns)

## What I built
`workspace/build/ch17/l17c.html` replaces the placeholder. It uses the house lesson layout, copied from 17A and 17B. A small `<style>` block (l.1-9) sizes the tables and figures.
- **Lesson head** (l.10-12). The focus line is pack-written. It names B(n,p) ≈ N(np,npq), the continuity correction (CC) for small n, and the rule of thumb. It refers to "the standard normal table at the end of the Revision section".
- **Concept 1, the normal approximation** (l.14). Text boxes:
  - "Why approximate?": the pollster introduction and the 10 000-term sum.
  - "An example of approximations": 20 coins, with the SVG `c17c_coin20` (polygon and the N(10,5) curve).
  - "Notation for normal distributions".
  - "Treating X as if it were continuous": the CC idea in the textbook's words, taken from Example 11b. One pack sentence says how to use z and the table.

  Then the tutor demo (16 coins, P(X > 10)), the your-turn (12 coins, P(X > 8)), and Worked example 11 (l.45) with the shaded figure `c17c_ex11`.
- **Concept 2, continuity corrections** (l.63). It has the textbook text and Box 5, and a pack-written tip box "Writing the continuity correction" (l.75). The tip is a table taking X = a, X ≤ a, X < a, X ≥ a and X > a to their half-unit intervals. Then:
  - tutor demo: CC intervals for six events of B(30, 0.4), then 16 coins within one SD by the binomial and the normal;
  - your-turn: B(40, 0.25), and 12 coins;
  - Worked example 12 (l.90), with `c17c_ex12`.
- **Concept 3, the CC for large numbers** (l.110). Tutor demo: n = 10 000, p = 0.2, P(1950 ≤ X ≤ 2060) with and without the CC. Your-turn: n = 4800, p = 0.25. Then Worked example 13 (l.127).
- **Concept 4, approximating a binomial coefficient** (l.144). The box adds one pack sentence, nCx = 2^n P(X = x) ≈ 2^n P(x − 0.5 ≤ X ≤ x + 0.5). Tutor demo: 36C20. Your-turn: 100C55. Then Worked example 14 (l.156).
- **Concept 5** (l.168). Boxes:
  - "Sampling with replacement".
  - "How good an approximation is the normal?", with the five comparison graphs: p = 1/2 with n = 5, 10, and p = 1/6 with n = 5, 10, 20.
  - Box 6.
  - The central limit theorem remark.

  Tutor demo and your-turn: is it binomial or nearly binomial, the rule of thumb for three distributions, and the smallest n for a given p. The worked example "From the text" (l.207) tests np > 5 and nq > 5 on the six graphs in the lesson. It is pack-written on the textbook's graphs, because the textbook has no example for this part, which is the same approach as 17A/17B.
- **Textbook homework, Exercise 17C** (l.218). The exercise intro text "The standard normal probability distribution" comes first, with the shaded figure `phi_area` reused from the Revision section and the Note. The questions are verbatim, banded as in the book:
  - Foundation: Q1-6
  - Development: Q7-9
  - Enrichment: Q12

  Q3 has its histogram recreated as `c17c_q3`.
- **Past-paper homework** (l.254): 7 questions, 18 marks, 25 minutes, ordered from accessible to demanding, with one starting-idea hint each.
  - The pp-intro says "use the standard normal table at the end of the Revision section".
  - One plain pack line says that most questions are silent on the CC, and that the solutions say which method each one uses.

`workspace/build/ch17/a_17c.html` replaces the placeholder, in this order: ahead heading, Lesson Examples C1-C5 (l.9), Textbook Homework (l.55), ahead heading again, Past-Paper Worked Solutions PP 1-7 (l.100).
- A one-line note before the homework answers says that normal values use the table with z to 2 d.p.
- Q12 has the OC curves `a17c_q12a` (part a) and `a17c_q12b` (both curves).

Figures: `workspace/build/ch17/figs_17c.py` (new, same pattern as figs_17a/17b; it imports Fig/save from figs.py, which is untouched). It writes 11 SVGs: c17c_coin20, c17c_ex11, c17c_ex12, c17c_h5, c17c_h10, c17c_s5, c17c_s10, c17c_s20, c17c_q3, a17c_q12a and a17c_q12b.

Record: `docs/pp_selected_ch17.md`, new section `## 17C`.

## Continuity-correction handling (spec ruling)
- The teaching follows 17C exactly:
  - Box 5: "for small values of n, apply the continuity correction";
  - Examples 11 and 12 use the CC;
  - Example 13 shows that the CC is negligible for large numbers;
  - Example 14 shows that it is vital for a single value.
- Textbook homework answers follow the textbook: CC in Q1-4 and Q7-9, none in Q6c, as asked.
- Every past-paper school solution uses no CC. Each worked solution begins "Using the normal approximation without a continuity correction, as in the school solution." No method is called wrong.
  - Killara 2024 also gives a CC version (n ≐ 309), and my solution mentions it.
  - JR 2020's marker note on the CC is not repeated.
- The catalogue's CC column is honoured. All seven rows used are "No CC" in the school solution, or the school's main method has no CC.

## Sources
Textbook (Y12 CMS6 Ext 1):
- 17C teaching: PDF 823-828.
- Exercise 17C: PDF 829-834, with the table extract on 829-830.
- Answers: PDF 961 (right column) to 963 (top left).

I rendered and read every page, and zoomed in on Example 11's solution and Example 13.

Past papers. Each entry gives the school, year, title as printed on the cover, Q, marks, file, question page and solution page.
1. The King's School, 2021, Year 12 Alternative Higher School Certificate Trial Examination, Mathematics Extension 1, Q12(c)(iii) (1). `2021/3U Kings.pdf`, question p9, solution p23 (0.84).
   - (i)(ii) are used in 17B. The stem supplies "In earlier parts of the question, it was found that E(X) = 8000 and that X has a standard deviation of 40." (controller note).
2. James Ruse Agricultural High School, 2020, Year 12 Trial HSC Examination, Mathematics Extension 1, Q12(b) (2). `2020/James Ruse 2020 3U Trials & Solutions.pdf`, question p6, solution p15 (0.9236).
3. Ascham School, 2024, Year 12 Trial Examination, Mathematics Extension 1, Q11(e) (3). `2024/Ascham 2024 Extension 1 & Solutions.pdf`, question p6, solution p14-15 (0.0475).
   - The school's main method is p̂ (17D). Its alternative 1 is the count without a CC, with the same z, and I use the count.
4. Killara High School, 2020, Mathematics Extension 1 Trial HSC Examination, Q12(e) (3). `2020/2020 Killara.pdf`, question p9, solution p20 (0.998).
5. Abbotsleigh, 2024, Higher School Certificate Assessment 4 Trial Examination, Mathematics Extension 1, Q14(c)(ii) (2). `2024/Abbotsleigh 2024.pdf`, question p16, solution p31 (28.8%).
   - The school uses p̂, and the count gives the same z.
6. Killara High School, 2024, Year 12 Examination, Mathematics Extension 1 HSC Trial Examination, Q13(d) (3). `2024/Killara 2024 3U Trials & Solutions.pdf`, question p11, solution p24-25 (n = 300; the CC alternative gives 309).
7. James Ruse Agricultural High School, 2023, Year 12 Trial HSC Examination, Mathematics Extension 1, Q13(b)(ii) (4). `2023/Ruse 2023 3U.pdf`, question p7, solution p20-21 (n = 102).

I re-read every `docs/pp_selected_*.md` file and `docs/PAST_PAPERS_USED.md` before choosing and again just before committing. This included the new 13D entry (BBHS 2024 Q2) and the uncommitted Y11 Ch 13 line in PAST_PAPERS_USED.md. None of my seven items is used anywhere else.

## Omitted, rejected, changed
Textbook homework:
- **Q10 and Q11** ([Technology], a spreadsheet and BINOM.DIST/RANDBETWEEN simulation) are omitted under the spec's spreadsheet ruling.
- Q1-9 and Q12 are complete. The answers leave out only explanation-free items. Every part has an answer.

Adaptations:
- The exercise intro's "The table below gives some further values" now reads "The standard normal table at the end of the Revision section gives values". The table itself is the Revision page.
- Q1d's "using the normal tables at the start of this exercise" now reads "using the standard normal table at the end of the Revision section".
- I used Φ for the CDF and φ for the PDF throughout, matching the Revision section. The 17C book writes ϕ for both, for example "1 − ϕ(1.118)" and "P(Z ≤ z) = ϕ(z) = ∫ϕ(t)dt".
- "the next worked example" now reads "Worked example 12", since the 20-coin text points to the within-one-SD example.
- "In the example in the introduction to this chapter" now reads "... to this lesson (the pollster)".
- "Section 16G in the last chapter" now reads "Section 16G of the textbook, in the last chapter". The pack's Revision section covers only 16D-16F.
- Em dashes became colons, commas or brackets.

Silent fixes in copied worked material (the house ruling: print the correct version and report it). Please confirm:
- **Example 11b**: the book prints "≐ 1 − 0.881 ≐ 0.132". Φ(1.118) = 0.868, and 1 − 0.881 = 0.119 does not give 0.132. I print "1 − 0.868".
- **Example 13**: the book prints σ ≐ 47.1416. √(2222 2/9) = 47.1405, and the book's own z-scores (−0.7071, 1.4142, −0.7177, 1.4248) come from 47.1405. I print 47.1405.
- **Example 13b**: the book prints 0.6859. From its own z-scores, Φ(1.4248) − Φ(−0.7177) = 0.6864, and the exact binomial is 0.6861. I print 0.6864.
- **Example 14**: the book prints "≐ 8.438 × 10^28", but 2^100 × 0.066574 = 8.4393 × 10^28. I print 8.439 × 10^28.
- The text before Box 6 says "Here are the ogive and the normal approximation". The graphs are frequency polygons, so I print "frequency polygon".
- Example 12b "the discrete random X" becomes "the discrete random variable X".
- "central limit limit theorem" becomes "central limit theorem".

Book answers I did not copy. I solved each item myself, and the answers say that values may vary with interpolation or technology:
- **Q2a**: the book gives 8.46% with a percentage error of 0.1%, which is inconsistent with its exact value 8.49%. The table gives 8.50% (error 0.1%).
- **Q2e**: the book gives 46.0%. The table gives 45.92% (error 1.4%).
- **Q2 percentage errors**: I print them to 1 d.p., from the printed percentages (book: whole numbers).
- **Q5h**: the book gives n > 11. I print n > 11.1, that is, n ≥ 12.
- **Q4f**: I print 0.4%, less than 1% (book: "less than 1%").
- **Q7a**: I print 0.0134 ≐ 1% (book: "≐ 1%").

Past-paper changes:
- Table pointers are left out of the stems, as in 17A's BBHS line. Each paper prints a full table elsewhere, and the pp-intro points to the pack table:
  - Ascham: "[You may refer to the table on page 11.]" (a full P(Z ≤ z) table);
  - Killara 2020: "A normal distribution table is included overleaf." (a full P(0 < Z < z) table, unlabelled);
  - Abbotsleigh: "You may use the information on page 17 to answer this question.";
  - Killara 2024: "(A Standard Normal Distribution table is attached with this paper." The table is not in the file, and the line has no closing bracket.
- Abbotsleigh (ii): (i) is not included, so the stem adds "In an earlier part of the question, a mathematician planned to perform n trials to find a more accurate estimate of p." This gives "The mathematician" in (ii) its referent. Nothing in (ii) depends on (i)'s result.
- School-solution slips I did not copy:
  - JR 2023 writes 0.3466 for the printed 0.3446. Both give z = −0.40, and my solution uses the printed 0.3446.
  - Killara 2024 writes 0.90588, 0.9088 and 0.095n.
- Kept as printed: "less than 100 will order dessert", "less than 5% are left-handed", and "A random sample of n people is taken, the probability that ...".

Rejected 17C rows:
- D3: Sydney Tech 2020 Sample 3 is a sample paper, and "The discrete random variable ~B(40, 0.27)" has no variable name.
- D5, D11: doubtful (controller ruling).
- **D6** (BBHS 2023 Q13(b)(iii), 3 marks): ambiguous. The stem asks for the probability "to 4 decimal places" and never names the normal approximation, only "the information on page 15". The exact binomial value is therefore an equally valid reading, and it differs from the school's 0.2329.
- **D7** (Knox 2023 Q13(b), 3 marks): the stem typo "Find the value the value of P" makes it doubtful under house rule 6. It was the only "both CC methods" item.

Left free: Kings 2021 (i)(ii) are used, JR 2023 Q13(b)(i) (B17), Abbotsleigh 2024 Q14(c)(i) (E15), and all 17D rows.

## Verification
- `python3 workspace/checks/ch17_17c.py` reports **308 checks, 0 failed, ALL OK**. The script reads every printed value from l17c.html, a_17c.html and the two OC SVGs. Each template must match exactly once, or the check FAILs. It recomputes each value independently:
  - exact binomials by Fraction + math.comb, cross-checked by convolution;
  - coin counts by enumerating 2^n (n ≤ 20);
  - Φ from math.erf. Table look-ups use z rounded half-up to 2 d.p., then Φ to 4 d.p., as the textbook's answers do; this reproduces Q1d's 10.75% exactly. Every table value used is also compared with the table in revision.html, and all 400 entries are read.
  - Accurate values in Worked examples 11-14 are checked against erf to the printed places.
  - The CC intervals come from the event sets.
  - Rule-of-thumb n values come from a search.
  - PP 6 and PP 7 are solved for n by bisection, then confirmed by recomputing z. PP 7's school quadratic roots are checked, and the reverse look-ups (0.90658 → 1.32, 0.3446 → −0.40) use the closest table entry.

  It also checks the structure:
  - concept blocks and worked-example tags;
  - question numbers and bands (Q10 and Q11 omitted), and no spreadsheet items;
  - PP marks 18 in the range 15-22, and 25 min = 1.5 × 18 rounded to 5;
  - part marks, numbering, identical labels in both files, and one hint per question;
  - one method line per solution, and the table pointers left out.
- Mutation test: a copy with seven planted errors gave 8 FAILs, and every planted error was caught. The errors were in C1, Q2b, PP4, PP6, a Q12 table cell, Example 11's 0.868, and a your-turn datum.
- Build: `cd workspace/build && flock …/build.lock sh -c 'python3 build.py ch17 all && mv lesson.pdf answers.pdf ch17/'`.
  - lesson.pdf has 75 pages; 17C is pp 56-75.
  - answers.pdf has 17 pages; 17C is pp 13-17.
- `qa.py`: lesson 75 pages, 0 problems; answers 17 pages, 0 problems.
- MathJax error scan (all seven strings) on both PDFs: 0.
- I looked at every 17C page as contact sheets (lesson pp 56-75, answers pp 12-17), and zoomed in on the Concept 5 graphs, the Q3 histogram and answers p14. While doing this I fixed:
  - the crowded x-axis labels on the 20-coin figures (now 380 px wide);
  - the inconsistent sizes of the small graphs;
  - the CC part lists, which were split onto two lines;
  - a stranded "Worked example 12" header;
  - several half-empty pages. Worked examples 11 and 12 and two concept boxes may now break, and the work boxes were resized.

  Remaining white space: the lower part of the PP 7 page is a large work box (4-mark question), and Q5's page has about 25% free.

## Files changed
- workspace/build/ch17/l17c.html
- workspace/build/ch17/a_17c.html
- workspace/build/ch17/figs_17c.py (new)
- workspace/build/ch17/svg/c17c_*.svg (9) and svg/a17c_q12a.svg, svg/a17c_q12b.svg (all new)
- workspace/checks/ch17_17c.py (new)
- docs/pp_selected_ch17.md (## 17C appended)

The commit is c5556f1 "Ch17: lesson 17C". I staged only these paths; nothing is pushed.

## Concerns
1. Please confirm the silent teaching-part fixes:
   - Example 11: 0.881 → 0.868
   - Example 13: σ 47.1416 → 47.1405, and 0.6859 → 0.6864
   - Example 14: 8.438 → 8.439
   - "ogive" → "frequency polygon"
2. Exercise 17C Q4 has a stem/part mismatch. The teacher asks for P(more than 8 girls), but part c asks for "9 or 10 girls", and the book's answer 14.04% is P(9 or 10). I kept Q4, because each part is self-contained. Rule if you want it omitted as doubtful.
3. The past-paper set is 18 marks. It is short of 21 because D6 (ambiguous: exact vs normal at 4 d.p.) and D7 (stem typo) were rejected. Both are 3 marks, and either would bring the set to 21 if you rule it usable.
4. Pack-written material:
   - the focus line;
   - the sentence on using z and the table in Concept 1;
   - the tip box "Writing the continuity correction";
   - the nCx = 2^n P(X = x) line in Concept 4;
   - the "From the text" rule-of-thumb worked example;
   - the pp-intro CC line;
   - the Abbotsleigh context sentence;
   - all tutor demos and your-turns.
5. Some stems lose their table-pointer lines, so Killara 2020, Ascham, Abbotsleigh and Killara 2024 no longer say to use a normal approximation. The lesson context, the pp-intro and the hints make this clear. Each school's full table is replaced by the pack's table. Killara 2020's own table is in P(0 < Z < z) form, and it is not reproduced.

## Fix round 1 (controller rulings before review)
1. **18 marks:** accepted. D6 and D7 stay out. No change.
2. **Stem fidelity.** Every stem sentence is now kept verbatim. Only the page or location reference is replaced, by a bracketed editorial note.
   - The method sentences in PP 1 (Kings), PP 2 (JR 2020) and PP 7 (JR 2023) were already verbatim. The check script now asserts them.
   - PP 3 Ascham: "[You may refer to the table on page 11.]" becomes "[You may refer to [the standard normal table at the end of the Revision section].]". Ascham's table is a P(Z ≤ z) table, the same form as the pack's.
   - PP 4 Killara 2020: "A normal distribution table is included overleaf." becomes "A normal distribution table is included [at the end of the Revision section]."
     - The paper's own table (PDF p10) is a full P(0 < Z < z) table with no heading.
     - The question does not need that form: P(X < 100) = Φ(2.95) is read directly from a P(Z ≤ z) table. The school's 0.5 + 0.498 is the same value. So I did not reproduce the paper's table. Please say if you want the paper's table reproduced anyway.
   - PP 5 Abbotsleigh: the italic line "You may use the information on page 17 to answer this question." is restored at the head of the (c) stem, as "You may use the information [in the standard normal table at the end of the Revision section] to answer this question." Abbotsleigh's table is a P(Z < z) table, the same form.
   - PP 5, the added context sentence "In an earlier part of the question, a mathematician planned to perform n trials to find a more accurate estimate of p." supplies only what (i) set up. In the paper, (i) reads "To find a more accurate estimate of p, the mathematician plans to perform n trials, and find p̂." It is kept.
   - PP 6 Killara 2024: "(A Standard Normal Distribution table is attached with this paper." becomes "(A Standard Normal Distribution table is [at the end of the Revision section]." I kept the paper's missing closing bracket verbatim, under rule 6 (no corrections to student material).
3. **Ex 17C Q4.** On re-reading, the sample is 15 pupils, not 10, so the two events are not the same.
   - "More than 8 girls" is X = 9, …, 15, with P(X ≥ 9) ≐ 0.1615.
   - Part c, and the book's answer 14.04%, is P(X = 9 or 10) ≐ 0.1404.
   - The stem and the parts are therefore inconsistent. Under house rule 6, I have **omitted Q4** from the lesson and the answers. The Foundation band is now Q1-3 and Q5-6.
4. The silent example fixes and the pack-written material are unchanged, for the reviewer.

Other changes:
- The PP 7 work box went from 170 to 100, so PP 6 and PP 7 now share the last page. Previously PP 6 sat alone on a 60%-empty page.
- docs/pp_selected_ch17.md: the stem notes are updated to the new wording.

Check script: `workspace/checks/ch17_17c.py`
- The Q4 checks are removed, and the expected question numbers, bands and answer blocks are updated (Q4 omitted).
- For PP 3-6 it now checks that the table sentence is present with its location replaced, and that the old page/location wording is gone.
- It also checks that the method sentences of PP 1, PP 2 and PP 7 are present verbatim.

Verification:
- `python3 workspace/checks/ch17_17c.py`: 308 checks, 0 failed, ALL OK.
- Rebuilt with flock.
- qa.py: lesson 75 pages, 0 problems; answers 17 pages, 0 problems.
- MathJax error scan: 0 on both PDFs.
- Pages inspected: lesson pp 68-76 (homework Q5-Q12 and the past papers, before and after the work-box change) and answers pp 14-15.

Files: workspace/build/ch17/l17c.html, a_17c.html, workspace/checks/ch17_17c.py, docs/pp_selected_ch17.md. Commit "Ch17: 17C stem fidelity".

## Fix round 2 (review findings)
1. **Pack-written worked example title.** The Concept 5 worked example (l17c.html:207) is now titled "Testing the rule of thumb: keep for homework", not "From the text: keep for homework". The tag stays "Worked example".
2. **Hints.** Every PP hint is now a starting question. None states a value, a method step or the key technique:
   - PP 1: "which normal distribution approximates X?" It no longer gives z = 1.
   - PP 2: "what is the distribution of the number of patients who cannot be cured?"
   - PP 3: "which binomial distribution is this?"
   - PP 4: "what are n and p here?" It no longer points to the np, nq > 5 check.
   - PP 5: "what do the 2 million trials tell you?"
   - PP 6: "what is the distribution of the number of students absent from a lecture?"
   - PP 7: "what is the distribution of the number in the sample who take less than 12 minutes?" The pointer to the quadratic in √n is gone.
3. **PP 3 bracket.** The paper's own brackets are kept and only the location phrase changes: "[You may refer to the table at the end of the Revision section.]". No other stem had nested brackets. The other replacements in Killara 2020, Abbotsleigh and Killara 2024 are single editorial brackets inside the paper's sentence.
4. **Method lines.** These are now literally true:
   - PP 3 Ascham: "Using the normal approximation to the count, without a continuity correction. (The school solution’s main method uses the sample proportion, Lesson 17D, and gets the same z-score. Its alternatives include the count without a continuity correction, as here, and the count with one, which gives 0.0336.)" The CC alternative is mentioned, consistent with PP 6.
   - PP 5 Abbotsleigh: "Using the normal approximation to the count, without a continuity correction. (The school solution uses the sample proportion, Lesson 17D, and gets the same z-score.)"
   - The old trailing notes in PP 3 and PP 5 are removed to avoid repetition.
   - PP 1, 2, 4 and 7 keep "…, as in the school solution." In PP 2, the school also counts and uses no CC (it works with the number cured), and the trailing note says so. PP 6 keeps "…, as in the school solution’s main method." with its CC note.

docs/pp_selected_ch17.md: the Ascham stem note and the method-line description are updated.

Check script `workspace/checks/ch17_17c.py` (now 317 checks):
- The method-line check accepts the count wording for PP 3 and PP 5, and requires exactly one method line per solution.
- A new per-hint check: the hint must end in "?", contain no numbers that are not in the stem, and contain no "quadratic", "reverse", "z-score", "sqrt", "continuity", "np" or "nq".
- New checks: PP 3's CC alternative value 0.0336, recomputed from the table, and the Concept 5 worked-example title (no "From the text").
- The PP 3 stem template is updated.

Verification:
- `python3 workspace/checks/ch17_17c.py`: 317 checks, 0 failed, ALL OK.
- Rebuilt with flock.
- qa.py: lesson 75 pages, 0 problems; answers 17 pages, 0 problems.
- MathJax error scan: 0 on both PDFs.
- Pages inspected: lesson p67 (the retitled worked example) and pp 73-75 (all PP stems and hints); answers p16 (PP 2-5 solutions). The layout is unchanged.

Files: workspace/build/ch17/l17c.html, a_17c.html, workspace/checks/ch17_17c.py, docs/pp_selected_ch17.md. Commit "Ch17: 17C review fixes". No 17D files were touched.
