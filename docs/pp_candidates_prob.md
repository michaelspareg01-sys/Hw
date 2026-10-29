## Past-paper candidates: discrete probability distributions (Y11 Ext 1 Ch 13) and binomial distributions (Y12 Ext 1 Ch 17)

All paths are relative to `pp/Ext 1/`. "p" is the PDF page number, not the printed page. I checked every candidate against the rendered page, so the question numbers, marks and wording below come from the paper itself. Solution pages were found by eye (many are handwritten scans). Nothing here is on `PAST_PAPERS_USED.md`, `pp_selected_ch10.md` or `pp_selected_y11ch14.md` (the last one was still empty when I finished). I left out all commercial papers (NEAP, PEM, TEC, CSSA, Independent and the BoS zip). I also left out questions whose main skill is counting (hypergeometric "choose r from n" probability, arrangements) or the binomial theorem.

"CC" = what the school solution does about a continuity correction. "Table" = the page where the paper prints a z-table. "No table" means the question needs z-values but the file has none.

Most trials have no statistics at all, so 13A–13D items are scarce. The statistics questions cluster in a few schools (Blacktown Boys', Killara, Sydney Tech, James Ruse, Caringbah, Baulkham Hills).

---

## Ch 13 (Y11): discrete probability distributions

No school paper has a general (non-binomial) discrete distribution table, E(X) from a table, or a 13D sampling item. Everything below is a Bernoulli or binomial item that also works for 13A–13C. List them in Ch 13 only if the Ch 17 pack does not need them.

| # | Tag | File, question page → solution page | Title as printed, school, year | Q, marks | What it asks | Flags |
|---|---|---|---|---|---|---|
| A1 | 13A (+17B) | `2020/2020 Bauklham Hills.pdf` p7 → p14 (left half) | No cover in the file. Solutions headed "Year 12 Trial Examination 2020 Mathematics Extension 1 Marking Guidelines", Baulkham Hills 2020 | Q12(a) (1,2,1,1 = 5) | Table of X ~ Bin(4,p) with P(0)=0.2401, P(1)=a, P(2)=b, P(3)=0.0756, P(4)=0.0081: find p, then a and b, Var(X), P(X ≥ 3) | Scanned, with a student's pen marks next to the question. Data consistent (p = 0.3). Best 13A-style table item found |
| A2 | 13A | `2020/2020 Manly.pdf` p2 → p13 | "Northern Beaches Secondary College, Manly Selective Campus, Year 12 Trial Examination 2020, Mathematics Extension 1" | Q2 (1, MC) | Which situation describes a Bernoulli random variable (100 m times / card value / red pen from red, black, blue / number of emails) | Scanned, clean. School answer C |
| A3 | 13A | `2021/3U JRAHS.pdf` p2 → none | "Mock Trial Paper 2021, Mathematics Extension 1" (no school named; file labelled JRAHS) | Q1 (1, MC) | Which formula is the "probability density function" of a Bernoulli distribution with p = 0.93 | Mostly images. Calls a discrete pmf a "probability density function". See the note on this file below |
| A4 | 13A (+17A) | `2021/3U Sydney Tech.pdf` p9 → p21 | "Extension 1 Mathematics, Trial HSC, August 2021", Sydney Technical HS | Q14(a)(i) (2) | Roulette (18 red, 18 black, 1 green), bet on black five times: write the distribution of Y in standard form and give its mean and variance | Typos "1 green numbers", "the ball land". Solutions headed "Mathematics Common Test Assessment 4 2019" |
| A5 | 13C | `2020/James Ruse 2020 3U Trials & Solutions.pdf` p2 → p10 (answers only) | "James Ruse Agricultural High School 2020 Year 12 Trial HSC Examination, Mathematics Extension 1" | Q1 (1, MC) | Bernoulli trial with p = 0.3: the variance | School answer D (0.21) |
| A6 | 13B/13C | `2023/Hurlstone 2023 3U.pdf` p3 → p19 | "Hurlstone Agricultural High School 2023 Higher School Certificate Trial Examination, Mathematics Extension 1" | Q8 (1, MC) | Bernoulli X with E(X) = 5Var(X), p ≠ 0: find p | School answer B (4/5) |
| A7 | 13C (Var(aX)) | `2021/3U JRAHS.pdf` p2 → none | Mock Trial Paper 2021 (as A3) | Q3 (1, MC) | 3 points per successful shot, p = 3/5, 800 shots: variance of the points | Needs Var(3X) = 9Var(X). See the note on this file |

13D: no candidates in any school paper.

Out of scope, so not listed: continuous probability density function questions (Advanced Y12), for example Caringbah 2020 Q8, Hornsby Girls 2020 Q8, Killara 2020 Q11(e), Western 2020 Q11(c) and Sydney Tech 2021 Q14(b).

---

## Ch 17 (Y12): binomial distributions

### 17A: binomial probability, "at least / at most", number of trials

| # | Tag | File, question page → solution page | Title as printed, school, year | Q, marks | What it asks | Flags |
|---|---|---|---|---|---|---|
| B1 | 17A | `2020/2020 Western.pdf` p2 → p20 | "Western Mathematics 2020 Trial Higher School Certificate Examination, Mathematics - Extension 1" | Q1 (1, MC) | 8 MC questions with 4 options: P(exactly 5 correct by guessing), to 3 s.f. | School answer D (0.0231). "Western Mathematics" may not be a single school; please confirm it counts as a school paper |
| B2 | 17A | same file, p10 → p32 | same | Q12(b) (1,1,2 = 4) | Netball: Option 1 (2 attempts, at least 1) gives 2p − p², Option 2 (3 attempts, at least 2) gives 3p² − 2p³; Option 1 three times as likely, find p | — |
| B3 | 17A | `2020/2020 Manly.pdf` p6 → p14 | Manly 2020 (title as A2) | Q11(a) (1,1,2 = 4) | Archer hits a bullseye 1 time in 3, 8 shots: exactly 2, at least 2, number of shots for 90% certainty of at least one | Scanned. Good "number of trials" part |
| B4 | 17A | `2020/2020 Blacktown Boys.pdf` p8 → p15 | "Blacktown Boys' High School 2020 HSC Trial Examination, Mathematics Extension 1" | Q12(a) (1,2 = 3) | 92% of lollipop bags contain 50; batch of 15; P(exactly 2 bags not 50), P(production stopped) = P(X > 2) | — |
| B5 | 17A | `2020/James Ruse 2020 3U Trials & Solutions.pdf` p5 → p11 | JR 2020 (title as A5) | Q11(b) (3) | Success = total of 9 with two dice; 6 rounds; P(at least 5 successes), 3 s.f. | Handwritten solutions |
| B6 | 17A | `2020/2020 Sydney Tech.pdf` p3 → p11 | "Sample 2 STHS Trial Higher School Certificate Examination, Mathematics EXTENSION 1" | Q5 (1, MC) | 40 MC questions, 4 options: P(exactly 7 correct by guessing) as an expression | **Doubtful:** option B (⁴⁰C₇…) and option C (⁴⁰C₃₃…) are equal, so two options are correct (school picks C). A revision sample paper |
| B7 | 17A | `2021/3U Caringbah.pdf` p9 → p25 | "Caringbah High School Year 12 2021 Mathematics Extension 1 HSC Course Assessment Task 4" | Q12(d) (2) | 15 students, P(unavailable) = 0.14: P(exactly 3 unavailable), 3 d.p. | Handwritten solutions |
| B8 | 17A | `2021/3U Killara.pdf` p9 → p25 | "2021 Year 12 Mathematics Extension 1 Trial Examination", Killara | Q12(a)(i) (1) | 90% shipped on time, 150 orders: P(exactly 135 on time), 3 s.f. | "This delivery will occur" is read as exactly 135 in the solution (0.108). (ii) is in 17D |
| B9 | 17A | `2021/3U Sydney Tech.pdf` p2 → p11 (answers only) | Sydney Tech 2021 (title as A4) | Q3 (1, MC) | Coin with P(head) = 0.7, 8 flips: P(exactly 3 tails) as an expression | School answer C |
| B10 | 17A | same file, p9 → p21 | same | Q14(a)(ii) (2) | Same roulette bet five times: P(wins more times than he loses), 3 d.p. | Pairs with A4 (14(a)(i)) |
| B11 | 17A | `2021/3U JRAHS.pdf` p8 → none | Mock Trial Paper 2021 (as A3) | Q13(d) (3) | X ~ Bin(n,p) with P(X=1) = (1−p)^(n−2), p < 1: possible n and p in terms of n | Hard and open-ended; no solutions |
| B12 | 17A | `2022/Blacktown Boys 3U Maths Paper _ Solutions 2022.pdf` p3 → p14 | "Blacktown Boys' High School 2022 HSC Trial Examination, Mathematics Extension 1" | Q3 (1, MC) | P(head) = 0.69, 50 tosses: expression for exactly 2 heads | School answer C |
| B13 | 17A | `2022/Knox 2022 3U Trials & Solutions.pdf` p5 (right half of spread) → p13 (right half) | "Knox Grammar School 2022 Higher School Certificate Trial Examination, Mathematics Extension 1" | Q13(c)(i)(ii) (1,2 = 3) | Tomatoes twice as likely from Farm A (60% determinate) as Farm B (70%): show P(determinate) = 19/30; 10 tomatoes, P(no more than 8 determinate) | Scanned 2-up. (i) is total probability, (ii) is binomial. (iii) is in 17D |
| B14 | 17A | `2023/2023_Killara_High_School_-_X1_-_Trial_-_Questions.pdf` p11 → none | "2023 Year 12 Examination, Mathematics Extension 1, Trial", Killara | Q12(f) (2) | 1% of battery cases fail, batch of 50: P(no more than 2 fail) | Questions only, no solutions |
| B15 | 17A | `2023/Baulkham Hills 2023 3U.pdf` p8 → p18 | "2023 Higher School Certificate Trial Examination, Mathematics Extension 1" (Baulkham Hills) | Q13(c) (2,1 = 3) | 5 MC questions, 4 options, random guessing: P(3 correct, 2 incorrect), P(at least one incorrect) | — |
| B16 | 17A | `2023/Blacktown Boys 2023 3U.pdf` p10 → p26 | "Blacktown Boys' High School 2023 Year 12 Trial Examination, Mathematics Extension 1" | Q13(b)(i)(ii) (1,1 = 2) | 3% of toy cars faulty, boxes of 50: P(exactly 5 faulty), P(at least 1 faulty), 4 d.p. | (iii) is in 17C. Handwritten solutions |
| B17 | 17A | `2023/Ruse 2023 3U.pdf` p7 → p20 | "James Ruse Agricultural High School 2023 Year 12 Trial HSC Examination, Mathematics Extension 1" | Q13(b)(i) (2) | 10% finish in under 12 min, 15 people: P(fewer than 2), 3 d.p. | (ii) is in 17C |
| B18 | 17A | `2023/Moriah 3U 2023 Paper w_ Solutions.pdf` p12 → p23 | "2023 Trial Higher School Certificate Examination, Mathematics Extension 1", Moriah College | Q11(c) (1,2 = 3) | P(correct pick) = 0.3, 8 games: P(exactly 5), P(at least 2) | Scanned, no text layer |
| B19 | 17A | `2024/Abbotsleigh 2024.pdf` p9 → p22 | "Abbotsleigh 2024 Higher School Certificate Assessment 4 Trial Examination, Mathematics Extension 1" | Q11(d) (1,2 = 3) | Brake pads replaced with p = 0.2, 12 races: exactly 3, at most 3, 2 d.p. | — |
| B20 | 17A | `2024/Ascham 2024 Extension 1 & Solutions.pdf` p6 → p13 | "Ascham School 2024 Year 12 Trial Examination, Mathematics Extension 1" | Q11(c) (2) | Five dice: P(exactly two show a 6) | Handwritten solutions |
| B21 | 17A | `2024/Blacktown Boys 2024.pdf` p3 (right half) → p9 | "Blacktown Boys' High School 2024 HSC Trial Examination, Mathematics Extension 1" | Q6 (1, MC) | Hits 2 of every 3 shots, 10 shots: P(exactly 9) as an expression | School answer D, 5(2/3)¹⁰. Pages are 2-up |
| B22 | 17A | same file, p5 (right half) → p10 | same | Q12(c) (3) | Radio picks 1 of 20 stations at random, switched on 30 times a month: P(right station at least twice), 4 s.f. | Typo "ratio" for radio |
| B23 | 17A | `2024/Killara 2024 3U Trials & Solutions.pdf` p6 → p16 | "2024 Year 12 Examination, Mathematics Extension 1, HSC Trial Examination", Killara | Q9 (1, MC) | P(sunny 3 days running) = 0.512; P(exactly 2 sunny in n days) = 0.0512: find n | School answer B (n = 5) |
| B24 | 17A | `2024/St Aloysius_ College 2024.pdf` p4 → none | "St Aloysius' College 2024 Trial Higher School Certificate Examination, Mathematics Extension 1" | Q6 (1, MC) | Die rolled 6 times, N = number of 3s: P(N < 2) to 4 d.p. | No solutions in the file |
| B25 | 17A (+17B mode) | `2020/2020 SBHS.pdf` p9 → p22 | "SBHS Term 3 Y12 Sample Paper, Trial HSC Extension 1" | Q13(a) (1,2 = 3) | Share price up $1 with p = 3/5, down with 2/5: show P($7 after 3 days from $6) = 54/125; most likely price after 5 days | A revision sample paper, and its text layer is garbled. **Label clash:** the used list has "SBHS20 Q13a" (Ch 13 DEs, almost certainly Q13(a) of `2020 SBHS 2.pdf`, a DE question). This is a different paper, but the labels match |

### 17B: E(X) = np, Var(X) = npq, mode, distributions

| # | Tag | File, question page → solution page | Title, school, year | Q, marks | What it asks | Flags |
|---|---|---|---|---|---|---|
| C1 | 17B | `2020/2020 Caringbah.pdf` p5 → p14 | "Caringbah High School 2020 Higher School Certificate Trial Examination, Mathematics Extension 1" | Q11(e) (3) | Binomial with mean 6 and standard deviation 2: find n and p | Handwritten solutions |
| C2 | 17B | `2020/James Ruse 2020 3U Trials & Solutions.pdf` p3 → p10 (answers only) | JR 2020 | Q6 (1, MC) | P(X=k) = ¹⁵Cₖ(0.29)ᵏ(0.71)¹⁵⁻ᵏ: mean of X | School answer C (4.35). For Q1 see A5 |
| C3 | 17B | `2020/2020 Sydney Tech.pdf` p4 → p12 | Sample 2 STHS (as B6) | Q10 (1, MC) | Bin(n,p) with mean = standard deviation: smallest n with p ≤ 0.01 | Sloppy wording ("The mean and The standard deviation", "such that P ≤ 0.01"). School answer D (99). Sample paper |
| C4 | 17B | `2020/2020 Western.pdf` p14 → p39 | Western 2020 (as B1) | Q14(d) (1,2 = 3) | 36 people, birth months equally likely: expected January births; P(number within one standard deviation of the mean) | Solution sums exact binomial terms for X = 2 to 4 |
| C5 | 17B | `2021/3U Caringbah.pdf` p6 → p18 | Caringbah 2021 (as B7) | Q10 (1, MC) | X ~ B(30, 0.4): which pair of E(X) and Var(X) or σ² is right | School answer D |
| C6 | 17B (→17C) | `2021/3U Kings.pdf` p9 → p22–23 | "The King's School 2021 Year 12 Alternative Higher School Certificate Trial Examination, Mathematics Extension 1" | Q12(c)(i)(ii) (1,1 = 2) | Drug cures with p = 0.8, 10 000 patients: E(X), show σ = 40 | (iii) is in 17C |
| C7 | 17B | `2021/3U JRAHS.pdf` p2 → none | Mock Trial Paper 2021 | Q3 (1, MC) | Variance of 3X (see A7) | See the note on this file |
| C8 | 17B | `2022/Knox 2022 3U Trials & Solutions.pdf` p2 (right half) → p7 | Knox 2022 (as B13) | Q6 (1, MC) | X ~ Bin(n, 0.2), mean = 2 × standard deviation: find n | Scanned. Answer n = 16 (D) |
| C9 | 17B | `2022/Blacktown Boys 3U Maths Paper _ Solutions 2022.pdf` p7 → p17 | BBHS 2022 (as B12) | Q11(c) (2,1 = 3) | X ~ B(n,p), μ = 3, σ² = 2: find p, then n | Not on the used list (BBHS22 Q11a/d/e were used) |
| C10 | 17B | same file, p10 → p22–23 | same | Q13(d) (2) | Coin tossed 30 times: P(number of heads within one standard deviation of the mean), by the binomial distribution, 3 d.p. | — |
| C11 | 17B | `2023/Baulkham Hills 2023 3U.pdf` p6 → p13 | BHHS 2023 (as B15) | Q11(c) (1,2 = 3) | p = P(sum of 7) with two dice; 30 rolls: mean and variance | Easy |
| C12 | 17B | `2023/Blacktown Boys 2023 3U.pdf` p3 → p16 | BBHS 2023 (as B16) | Q5 (1, MC) | Mean 225, variance 144: find p | School answer D (0.36) |
| C13 | 17B | `2023/Hurlstone 2023 3U.pdf` p9 → p26 | Hurlstone 2023 (as A6) | Q13(c)(i) (1) | 23% study Ext 1: describe and justify the skew of the binomial distribution | (ii) is in 17D. For Q8 see A6 |
| C14 | 17B | `2023/Sydney Technical 2023 3U.pdf` p10 → p22 | "Extension 1 Mathematics, Trial HSC, August 2023", Sydney Technical HS | Q12(a) (2,1,1,2 = 6) | X ~ Bin(n,p), μ = 12, σ² = 4: show p = 2/3, find n, describe a real-world (die) scenario, find P(X = 4) | Handwritten solutions |
| C15 | 17B | `2023/Moriah 3U 2023 Paper w_ Solutions.pdf` p13 → p24 | Moriah 2023 (as B18) | Q12(a) (1,3 = 4) | 3 blue, 5 green, k yellow marbles, 4 draws with replacement: P(first is blue); smallest k with Var(X) < 0.8 | Scanned. Nice inequality item |
| C16 | 17B | `2024/Abbotsleigh 2024.pdf` p3 → p18 | Abbotsleigh 2024 (as B19) | Q1 (1, MC) | 12 Bernoulli trials, p = 0.7: mean and variance | School answer B |
| C17 | 17B | `2024/St Aloysius_ College 2024.pdf` p4 → none | St Aloysius' 2024 (as B24) | Q7 (1, MC) | E(X) = 7, Var(X) = 6: which p | No solutions in the file |
| C18 | 17B | `2020/2020 Bauklham Hills.pdf` p7 → p14 | BHHS 2020 | Q12(a)(iii)(iv) | See A1; Var(X) and P(X ≥ 3) from the table | Use in only one pack |

### 17C: normal approximation to the binomial

| # | Tag | File, question page → solution page | Title, school, year | Q, marks | What it asks | Table | CC in school solution | Other flags |
|---|---|---|---|---|---|---|---|---|
| D1 | 17C | `2020/2020 Killara.pdf` p9 → p20 | "Killara High School 2020 Mathematics Extension 1 Trial HSC Examination" (date 05/08/20) | Q12(e) (3) | 27% order dessert, 288 bookings: P(fewer than 100 order dessert) | p10 (overleaf), but it gives **P(0 < Z < z)**, not P(Z < z) | No CC (z = 2.95, 0.998) | Handwritten solutions |
| D2 | 17C | `2020/James Ruse 2020 3U Trials & Solutions.pdf` p6 → p15 | JR 2020 | Q12(b) (2) | 80% cured, 150 patients: P(at most 37 not cured); justify the normal approximation | No table | No CC in either method (count or p̂). The solution adds a note: using a CC gives 0.937, but a CC "is not recommended in the HSC" | — |
| D3 | 17C | `2020/2020 Sydney Tech 3.pdf` p9 → p23 | "Sample 3 STHS Trial Higher School Certificate Examination, Mathematics EXTENSION 1" | Q14(c) (2) | "The discrete random variable ~B(40, 0.27). Find P(x ≥ 16)" | On p9 | No CC (z ≈ 1.86, 0.0314) | Wording: the variable name is missing. Sample paper; its solutions are headed "Year 11 Assessment 2 – June 2020" |
| D4 | 17C | `2021/3U Kings.pdf` p9 → p23 | Kings 2021 | Q12(c)(iii) (1) | Use a normal approximation for P(X < 8040) (μ = 8000, σ = 40) | No table: empirical rule | No CC (P(Z < 1) = 0.84) | Needs (i) and (ii) (C6), or give μ and σ in the stem |
| D5 | 17C | `2022/Blacktown Boys 3U Maths Paper _ Solutions 2022.pdf` p9 → p20 | BBHS 2022 | Q12(e) (3) | 33% order take-away, 600 bookings: "the probability that 200 will order a take-away meal" | On p9, but it gives **P(0 < Z < z)** | No CC; the solution computes P(198 < X < 200) = 0.068 | **Doubtful wording and maths:** "200 will order" is answered as the area between the mean and 200 |
| D6 | 17C | `2023/Blacktown Boys 2023 3U.pdf` p10 → p27 | BBHS 2023 | Q13(b)(iii) (3) | Pallet of 80 boxes; P(between 65 and 70 boxes, inclusive, contain at least 1 faulty car), 4 d.p. | p15 | No CC; uses p̂ with p = 1 − 0.97⁵⁰ (0.2329) | Needs (ii). "To 4 d.p." clashes with an approximation (the exact binomial value differs) |
| D7 | 17C | `2023/Knox 2023 3U.pdf` p10 → p19 | "2023 Higher School Certificate Trial Examination, Mathematics Extension 1", Knox | Q13(b) (3) | Claim: 75% of bottles hold more than 375 mL; 9 of 18 hold less. Normal approximation for P(at least 9 less), and explain why the method may not be valid (np < 5) | p13 | **Both:** without CC 0.71%, then "with the continuity correction" 1.46% | Typo "Find the value the value of P". Good critique item |
| D8 | 17C | `2023/Ruse 2023 3U.pdf` p7 → p20–21 | JR 2023 | Q13(b)(ii) (4) | P(fewer than 9 of n take under 12 min) = 0.3446: normal approximation, solve for n | No table (needs inverse normal, z = −0.4) | No CC (n = 102; rejects 79) | The question prints 0.3446 but the solution uses 0.3466 (both round to z = −0.40). Hard |
| D9 | 17C/17D | `2024/Ascham 2024 Extension 1 & Solutions.pdf` p6 → p14–15 | Ascham 2024 | Q11(e) (3) | 10% left-handed, 100 people: P(fewer than 5% left-handed) | p10 ("table on page 11") | Main solution uses p̂ with no CC (0.0475). Alternatives on p14–15: count with no CC, count **with CC** (0.0336), and the exact binomial (0.0237) | Handwritten solutions |
| D10 | 17C | `2024/Killara 2024 3U Trials & Solutions.pdf` p11 → p24–25 | Killara 2024 | Q13(d) (3) | 5% absent per lecture; P(no more than 20 absent) = 0.90658: find n | **No table:** "attached with this paper" but not in the file | Main solution has no CC (z = 1.32). Alternative with CC (20.5) on p24–25 | Hard (quadratic in √n). The solution has the typo 0.095n |
| D11 | 17C (doubtful) | `2021/3U Caringbah.pdf` p12 → p28 | Caringbah 2021 | Q14(a) (2,2 = 4) | 70% do athletics, sample of 83: "show the mean is 58.1 and standard deviation 4.17 for such sample proportions"; P(at most 55) | On p12 | No CC | **Doubtful:** 58.1 and 4.17 are the count's mean and SD, not the proportion's. **The solution on p28 is for different numbers** (n = 96, p = 0.6, 54). Better avoided |
| D12 | 17C/17D | `2024/Abbotsleigh 2024.pdf` p16 → p31 | Abbotsleigh 2024 | Q14(c)(ii) (2) | 1 615 580 successes in 2 000 000 trials: P(more than 8100 successes in 10 000 trials), as a % to 1 d.p. | p17 | No CC (p̂ form, 28.8%) | See E15 for (i). p is estimated as 0.80779 from the 2 million trials |

### 17D: sample proportions p̂

| # | Tag | File, question page → solution page | Title, school, year | Q, marks | What it asks | Table | CC in school solution | Other flags |
|---|---|---|---|---|---|---|---|---|
| E1 | 17D | `2020/2020 Caringbah.pdf` p6 → p16 | Caringbah 2020 | Q12(b) (2,3 = 5) | 64% travel by bus, samples of 100: show mean 0.64 and SD 0.048; P(at least 58 and at most 64 in a sample) | On p6 (z 1.1–1.3 only) | No CC (0.3944) | The same question appears as Sydney Tech 2021 Q12(c) (E6) and Moriah 2023 Q11(d) (E14). Use only one |
| E2 | 17D | `2020/2020 Sydney Tech 2.pdf` p7 → p17 | "Sample 1 STHS Trial Higher School Certificate Examination, Mathematics EXTENSION 1" | Q12(b) (2,2 = 4) | 40% use the canteen, survey of 200: show mean 0.4 and SD √3/50; P(at most 70) | On p7 | No CC | Sample paper. The solution rounds σ to 0.035 before finding z (−1.43, against −1.44 unrounded) |
| E3 | 17D | `2020/2020 Manly.pdf` p10 → p19 | Manly 2020 | Q13(d) (2,2 = 4) | 15% of cookies faulty, 10 boxes of 20: mean and SD of the sampling distribution (4 d.p.); P(more than 20% faulty) | On p10 (z 1.8–2.0) | No CC (z = 1.98, 0.0239) | Scanned. The solution takes n = 200 cookies |
| E4 | 17D | `2020/2020 Bauklham Hills.pdf` p2 → p12 | BHHS 2020 | Q4 (1, MC) | p = 0.3 left-handed: smallest n with SD(p̂) ≤ 0.07 | — | n/a | Scanned with student marks. Answer B (43). The same item with p = 0.18 is Knox 2023 Q11(e) (E12) |
| E5 | 17D | `2021/3U Killara.pdf` p9 → p25 | Killara 2021 | Q12(a)(ii) (2) | Show E(p̂) = 0.9 and SD = 0.0245 (n = 150) | — | n/a | Pairs with B8 |
| E6 | 17D | `2021/3U Sydney Tech.pdf` p7 → p16 | Sydney Tech 2021 | Q12(c) (2,2 = 4) | Same bus question as E1 | On p7 | No CC | Duplicate of E1 |
| E7 | 17D | `2021/3U JRAHS.pdf` p9 → none | Mock Trial Paper 2021 | Q14(d) (1,1,3 = 5) | p = 0.20, 5 samples of 100: why a normal approximation; SD of p̂; P(at least 1 of the 5 samples has p̂ < 0.22) | On p9 | No solutions | Good two-stage item (normal, then binomial). See the note on this file |
| E8 | 17D | `2022/Knox 2022 3U Trials & Solutions.pdf` p5 (right half) → p14 (right half) | Knox 2022 | Q13(c)(iii) (3) | 33 tomatoes, need at least 55% determinate (p = 19/30): P(fine paste) by a normal approximation to p̂ | No table: empirical rule (z ≈ −1) | No CC (0.84) | Uses (i); its result 19/30 can be given in the stem |
| E9 | 17D | `2023/2023_Killara_High_School_-_X1_-_Trial_-_Questions.pdf` p13 → none | Killara 2023 | Q14(b) (2,3 = 5) | Population 21% smokers; 226 of 1200 young adults: sample proportion and "sample standard deviation"; P(no more than 226), successful if under 5% | No table | No solutions | "Sample standard deviation" is ambiguous (p = 0.21 or p̂?) |
| E10 | 17D | `2023/Baulkham Hills 2023 3U.pdf` p8 → p18 | BHHS 2023 | Q13(d) (3) | 7% faulty batteries, sample of 50: P(percentage faulty between 5% and 10%), nearest % | **No table** in the paper; the solution quotes table values | No CC (51%) | — |
| E11 | 17D | `2023/Hurlstone 2023 3U.pdf` p9 → p26 | Hurlstone 2023 | Q13(c)(ii) (4) | p = 0.23, sample of 60: P(more than 30% study Ext 1) | On p9 (z 1.1–1.3) | No CC (0.0985) | — |
| E12 | 17D | `2023/Knox 2023 3U.pdf` p8 → p17 | Knox 2023 | Q11(e) (2) | p = 0.18 red hair: smallest n with SD(p̂) ≤ 0.07 | — | n/a | Same item as E4 |
| E13 | 17D | `2023/Ruse 2023 3U.pdf` p9 → p25 | JR 2023 | Q15(c) (1,1,2 = 4) | Biased coin, p = 0.2, 100 flips: justify a normal approximation, mean and SD of p̂, P(0.1 ≤ p̂ ≤ 0.3), 4 d.p. | No table (z = ±2.5) | No CC (0.9876) | Handwritten solutions |
| E14 | 17D | `2023/Moriah 3U 2023 Paper w_ Solutions.pdf` p12 → p23 | Moriah 2023 | Q11(d) (1,3 = 4) | Bus question again; the mean is given, show SD = 0.048; P(58 to 64) | On p12 | No CC | Duplicate of E1 (marks split 1+3) |
| E15 | 17D | `2024/Abbotsleigh 2024.pdf` p16 → p31 | Abbotsleigh 2024 | Q14(c)(i) (3) | p ≈ 0.81: minimum n so that p̂ is within 0.001 of p with 99.7% certainty | p17 (empirical rule used) | n/a | Large answer (1 385 100). (ii) is D12 |
| E16 | 17D | `2023/Sydney Technical 2023 3U.pdf` p13 → p26 | Sydney Tech 2023 | Q13(d) (2,2 = 4) | 1/3 of coffees meet the standard, 50 sampled: mean and SD of p̂; P(at least 40% pleasing) | On p13 | No CC (z = 1) | Wording "assuming that the sample is normally distributed", "the mean and standard deviation of the sample" |
| E17 | 17D | `2023/Blacktown Boys 2023 3U.pdf` p13 → p35–36 | BBHS 2023 | Q14(e) (3) | p = 0.007 misprints, shut down if p̂ ≥ 0.008; choose n so P(unnecessary shutdown) < 0.15%; nearest thousand | p15 (empirical rule used) | n/a (threshold) | Odd wording "Pages printed by this printer will be shut down". Hard |
| E18 | 17D | `2024/Blacktown Boys 2024.pdf` p2 (left half) → p9 | BBHS 2024 | Q2 (1, MC) | Die rolled 18 times, p̂ = proportion of 3s: which expression is P(at most 12 rolls show 3) | — | n/a | School answer B, P(p̂ ≤ 2/3) |
| E19 | 17D | same file, p5 (left half) → p10 | same | Q11(e) (2,2 = 4) | 55% use public transport, sample of 600: show Var(p̂) = 33/80000; P(p̂ ≤ 0.575), 2 d.p. | p8 (right half) | No CC (0.89) | **Doubtful wording:** the census is about public transport, but p̂ is defined as the proportion "born overseas" |
| E20 | 17D | `2024/Killara 2024 3U Trials & Solutions.pdf` p12 → p29–30 | Killara 2024 | Q14(c) (2,3 = 5) | 70% drink the cereal milk; 67% of 1012 said they do: mean and SD of p̂; is there doubt about the poll? | **No table** in the file | No CC (P(Z ≤ −2.08) = 0.0188) | Good inference-style item |

### NORM: plain normal distribution (Advanced content), a few only

| # | Tag | File, question page → solution page | Title, school, year | Q, marks | What it asks | Flags |
|---|---|---|---|---|---|---|
| N1 | NORM | `2021/3U Sydney Tech.pdf` p6 → p12 | Sydney Tech 2021 | Q11(f) (2) | Weights N(80, 8²): empirical rule, P(weight under 64 kg) | School answer 0.025 |

No other plain normal question appears in the school papers. Every other z-score question is attached to a binomial or p̂ setting (17C and 17D above).

---

### Notes and concerns

- **`2021/3U JRAHS.pdf`** is headed "Mock Trial Paper 2021" and names no school. Its MC Q2 and Q4–Q10 and most of Section II are word-for-word the same as North Sydney Boys 2021 (`2021/3U NSB.pdf`). The probability items (Q1, Q3, Q13(d), Q14(d)) are extra. It has no solutions. Please check whether it should count as a school paper.
- **Sample papers:** `2020/2020 SBHS.pdf` and the three Sydney Tech 2020 files are revision samples, not the real trials. The Sydney Tech 2021 solutions are headed "Mathematics Common Test Assessment 4 2019".
- **Possible exclusion clash:** SBHS 2020 (Sample Paper) Q13(a) (B25) carries the same label as "SBHS20 Q13a" in `PAST_PAPERS_USED.md`. I believe the used one is `2020 SBHS 2.pdf` Q13(a), a DE question.
- **Duplicates:** the bus proportion question appears three times (E1, E6, E14). The left-handed and red-hair SD(p̂) ≤ 0.07 item appears twice (E4, E12).
- **Continuity correction:** most school solutions use no CC. Exceptions: Knox 2023 Q13(b) gives both answers. Ascham 2024 Q11(e) and Killara 2024 Q13(d) give a CC version as an alternative. James Ruse 2020 Q12(b) says a CC "is not recommended in the HSC".
- **Tables in P(0 < Z < z) form:** Killara 2020 (p10) and BBHS 2022 (p9).
- **Doubtful items (avoid or use with care):** B6 (two correct MC options), D5 (BBHS 2022 Q12(e)), D11 (Caringbah 2021 Q14(a), mismatched solution), E19 (BBHS 2024 Q11(e), inconsistent context).

### Papers with no text layer (checked by eye)
Fully scanned: 2020 Baulkham Hills, Manly, NSB and Ruse; 2021 Girraween and NSB; 2022 Knox; 2023 Moriah; 2024 NSB and PLC. 2021 JRAHS is mostly images. I viewed all of them as page sheets and rendered the candidate pages larger. All are readable.
- 2020 NSB, 2021 Girraween, 2021 NSB, 2024 NSB and 2024 PLC have no statistics questions.
- `2020/2020 Ruse.pdf` is a marked student copy of James Ruse 2020, so I used the clean `James Ruse 2020 3U Trials & Solutions.pdf`.
- `2024/Killara 3U.pdf` is a garbled scan of Killara 2024, so I used the clean Killara file.
- The text-layer papers with no binomial or statistics content were also spot-checked: SGGHS 2020, SBHS 2 2020, NSG 2020/2023, SGS 2020–2023, Kinross 2023, Gosford 2022/2023, Normanhurst, Hornsby, Fort Street, Girraween 2020/2023, Abbotsleigh 2020/2021/2023, Ascham 2020/2023, NSB 2022/2023, PLC 2023, SGHS, Saint Ignatius 2024 and Epping 2024. Their probability content is only counting-based probability, which I excluded.

Scripts and images are in `/tmp/claude-0/-home-user-Hw/33fce1a1-283b-5e23-bc89-9ac277c110f5/scratchpad/ppprob/`.
