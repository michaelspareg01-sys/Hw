"""Check of Lesson 17D (Y12 Ext 1 Ch 17 pack): Sample proportions, and the Chapter 17 review exercise.

The script reads the values PRINTED in workspace/build/ch17/l17d.html (worked examples, data in the tutor
demos and your-turn items, textbook questions, past-paper stems, the review questions) and in a_17d.html
(lesson example answers, textbook homework answers, past-paper worked solutions, review answers). Each value
is found with a template ('@' marks the printed text) or read from a printed table row; a template must match
exactly once in its block, otherwise the item FAILS. Every printed value is compared with an independent
computation:
  - exact binomial probabilities with fractions.Fraction and math.comb, cross-checked by convolving n
    one-stage distributions; dice and card probabilities by enumerating the sample space;
  - E(p-hat) and Var(p-hat) of each tabulated sample proportion distribution from sum(v P) and
    sum(v^2 P) - mean^2 of that table itself (not from pq/n);
  - simulation statistics from the printed frequency tables;
  - Phi(z) from math.erf. Table look-ups follow the textbook: z rounded half-up to 2 d.p., then Phi(|z|)
    to 4 d.p.; every table value used is also compared with the standard normal table in revision.html.
    Accurate values (Worked examples 17 and 19, the C4 tables) are compared with erf at the printed z;
  - sample sizes (Q15, Q18, PP 1, PP 6) by searching n directly against the condition;
  - Exercise 17D Q6 by drawing the ten samples from the printed class list.
It also checks the structure (concept blocks, worked-example tags, question numbers and bands, the omitted
items Q5, Q16b and Q17f, the review questions) and the past-paper block: marks add to the intro total
(15-22), time is 1.5 x marks rounded to 5 minutes, part marks add to each question's marks, numbering and
source labels match in both files, one hint per question (an identification question with no numbers or
method words, PP 2 and PP 3 as approved), a method line in each normal-approximation
solution, and the table pointers.

Exit status 1 if anything fails. Run: python3 workspace/checks/ch17_17d.py
"""
import math
import os
import re
import sys
from decimal import ROUND_HALF_UP, Decimal, getcontext
from fractions import Fraction as F
from itertools import product

getcontext().prec = 50
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.environ.get("CH17_SRC", os.path.join(HERE, "..", "build", "ch17"))   # override only for mutation tests
FAILS = []
NCHECK = [0]


def read(name):
    with open(os.path.join(SRC, name), encoding="utf-8") as fh:
        return fh.read()


def report(ok, label, detail=""):
    NCHECK[0] += 1
    print(("OK       " if ok else "MISMATCH ") + label.replace("\n", " ")[:100] + ("  " + detail.replace("\n", " ")[:170] if detail else ""))
    if not ok:
        FAILS.append(label)


# ---------------------------------------------------------------- independent tools
def pmf(n, p):
    p = F(p)
    return [math.comb(n, k) * p ** k * (1 - p) ** (n - k) for k in range(n + 1)]


def conv(n, p):
    d = [F(1)]
    for _ in range(n):
        e = [F(0)] * (len(d) + 1)
        for k, v in enumerate(d):
            e[k] += v * (1 - p)
            e[k + 1] += v * p
        d = e
    return d


def bsum(n, p, a, b):
    d = pmf(n, p)
    return sum(d[max(a, 0):min(b, n) + 1])


for n_, p_ in ((20, F(1, 3)), (12, F(1, 4)), (15, F(2, 3)), (80, F(1, 2)), (60, F(1, 20)), (20, F(1, 6)), (6, F(1, 8))):
    report(pmf(n_, p_) == conv(n_, p_), f"pmf B({n_},{p_}) = convolution", "")


def Phi(z):
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


def D(v):
    if isinstance(v, F):
        return Decimal(v.numerator) / Decimal(v.denominator)
    return Decimal(repr(v)) if isinstance(v, float) else Decimal(v)


def rnd(v, places):
    return str(D(v).quantize(Decimal(1).scaleb(-places), rounding=ROUND_HALF_UP))


def sf(v, digits):
    return rnd(v, digits - 1 - D(v).adjusted())


def z2(z):
    return rnd(z, 2)


REV = read("revision.html")
TAB = {}
for row in re.findall(r'<tr(?: class="gap")?><td class="z">(\d\.\d)</td>((?:<td>[\d.]+</td>){10})</tr>', REV):
    for j, v in enumerate(re.findall(r"<td>([\d.]+)</td>", row[1])):
        TAB[f"{Decimal(row[0]) + Decimal(j) / 100:.2f}"] = v
report(len(TAB) == 400, "revision table read", f"{len(TAB)} entries")


def tab(zs):
    """Table value Phi(z) for a 2-d.p. z string; checked against erf and the Revision table."""
    a = zs.lstrip("-")
    v = rnd(Phi(float(a)), 4)
    if TAB.get(a) != v:
        report(False, f"table Phi({a})", f"erf {v}, revision table {TAB.get(a)}")
    return v if not zs.startswith("-") else rnd(1 - Decimal(v), 4)


def T(z):
    return Decimal(tab(z2(z)))


def clean(t):
    t = re.sub(r"<[^>]+>", "", t)
    t = re.sub(r"\\,|\\!|\\;|&nbsp;|&ensp;|&emsp;|\s", "", t)
    return t.replace("\\(", "").replace("\\)", "").replace("−", "-").rstrip(".,")


def grab(block, template, where):
    pieces = template.split("@")
    cap = r"([-−\d.,\\]+?)"
    rx = "".join(re.escape(pc) + (cap if i < len(pieces) - 1 else "") for i, pc in enumerate(pieces))
    found = re.findall(rx, block, re.S)
    if len(found) != 1:
        raise LookupError(f"template matched {len(found)} times in {where}: {template!r}")
    return found[0] if isinstance(found[0], tuple) else (found[0],)


def chk(block, where, template, *want):
    label = f"{where} {template[:72]}"
    try:
        got = tuple(clean(g) for g in grab(block, template, where))
        report(got == tuple(str(w) for w in want), label, "printed " + " | ".join(got) + "  want " + " | ".join(str(w) for w in want))
    except Exception as err:
        report(False, label, f"ERROR {err}")


def present(block, where, text, n=1):
    report(block.count(text) == n, f"{where} text", f"{text[:90]!r} appears {block.count(text)} time(s)")


def frac_cell(c):
    c = clean(c)
    m = re.fullmatch(r"\\tfrac\{?(\d+)\}?\{?(\d+)\}?", c)
    if m:
        return F(int(m.group(1)), int(m.group(2)))
    return F(c) if c else None


def rows(block):
    """Printed table rows, in order: list of (header, [cells])."""
    out = []
    for h, r in re.findall(r"<tr><th>(.*?)</th>(.*?)</tr>", block, re.S):
        out.append((clean(h), re.findall(r"<td[^>]*>(.*?)</td>", r, re.S)))
    return out


def tables(block):
    return [rows(t) for t in re.findall(r"<table.*?</table>", block, re.S)]


def mean_var(vals, probs):
    m = sum(v * p for v, p in zip(vals, probs))
    return m, sum(v * v * p for v, p in zip(vals, probs)) - m * m


# ---------------------------------------------------------------- blocks
les = read("l17d.html")
ans = read("a_17d.html")
lesson, review_q = les.split("<!-- ============ Chapter review ============ -->")
teach = lesson.split("<!-- ============ Homework ============ -->")[0]
hw = lesson.split("<!-- ============ Homework ============ -->")[1].split("<!-- ============ Past papers")[0]
pps = lesson.split("<!-- ============ Past papers ============ -->")[1]
a_main, a_rest = ans.split('<div class="ans-sec">Past-Paper Homework - Worked Solutions</div>')
a_pp, a_rev = a_rest.split("{{ahead:Chapter 17 Review | Chapter review exercise}}")
report(ans.count("{{ahead:Lesson 17D | Sample proportions}}") == 2, "answers headings", "ahead twice")
report(ans.count("{{ahead:Chapter 17 Review | Chapter review exercise}}") == 1, "review answers heading", "")
report(a_main.index("Lesson Examples") < a_main.index("Textbook Homework"), "answers sections order", "")
BLKRX = r'<div class="a"(?: style="[^"]*")?><span class="an">([^<]+)</span><div class="ab"[^>]*>(.*?)(?=<div class="a"(?: style="[^"]*")?><span class="an">|<div class="ans-sec">|\{\{ahead|$)'
BLK = dict(re.findall(BLKRX, a_main, re.S))
report(list(BLK) == ["C1", "C2", "C3", "C4", "1", "2", "3", "4", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18"],
       "answer blocks", str(list(BLK)))
RA = dict(re.findall(BLKRX, a_rev, re.S))
report(list(RA) == [str(k) for k in range(1, 15)], "review answer blocks", str(list(RA)))
PPA = {int(k): v for k, v in re.findall(r'<div class="ppa"><div class="pp-src"><span><span class="pn">PP (\d+)</span>(.*?)(?=<div class="ppa">|$)', a_pp, re.S)}
PPQ = {int(k): v for k, v in re.findall(r'<div class="pp"><div class="pp-src"><span><span class="pn">PP (\d+)</span>(.*?)(?=<div class="pp">|$)', pps, re.S)}
QRX = r'<div class="q"(?: style="[^"]*")?><span class="q-num">(\d+)</span>(.*?)(?=<div class="q"|\{\{band|$)'
TQ = dict(re.findall(QRX, hw, re.S))
RQ = dict(re.findall(QRX, review_q, re.S))
CON = {}
for k in range(1, 5):
    seg = teach.split(f"<!-- ============ Concept {k} ============ -->")[1].split("<!-- ============")[0]
    exs = re.findall(r'<div class="ex (demo|attempt|worked)"(?: style="[^"]*")?><div class="ex-top"(?: style="[^"]*")?><span class="tag">([^<]*)</span>(.*?)(?=<div class="ex |$)', seg, re.S)
    CON[k] = {"seg": seg, "demo": [b for kd, _, b in exs if kd == "demo"][0], "attempt": [b for kd, _, b in exs if kd == "attempt"][0],
              "worked": [b for kd, _, b in exs if kd == "worked"], "tags": [t for kd, t, _ in exs if kd == "worked"]}
    report([kd for kd, _, _ in exs][:3] == ["demo", "attempt", "worked"], f"Concept {k} blocks", "tutor demo, your turn, worked example")
report([CON[k]["tags"] for k in range(1, 5)] == [["Worked example 15"], ["Worked example 16"], ["Worked example 17", "Worked example 18"], ["Worked example 19"]],
       "worked example tags", "Examples 15-19")
report(list(TQ) == ["1", "2", "3", "4", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18"], "textbook question numbers", "Q5 omitted (doubtful)")
fb, rest = hw.split("{{band:F}}")[1].split("{{band:D}}")
db, eb = rest.split("{{band:E}}")
report(re.findall(r'q-num">(\d+)', fb) == ["1", "2", "3", "4", "6"] and re.findall(r'q-num">(\d+)', db) == [str(k) for k in range(7, 17)]
       and re.findall(r'q-num">(\d+)', eb) == ["17", "18"], "bands", "F: 1-6, D: 7-16, E: 17-18")
report('<span class="pl">b</span>' not in TQ["16"] and "Toss 10 coins" not in TQ["16"], "Q16 part b (physical experiment) omitted", "")
report('<span class="pl">f</span>' not in TQ["17"] and "0.2+" not in TQ["17"], "Q17 part f omitted", "")
report("result will be a head" not in les, "Q5 omitted", "")
report(list(RQ) == [str(k) for k in range(1, 15)], "review question numbers", str(list(RQ)))
for k in ("7 The sample proportion", "8 Using the sample proportion", "Population proportions", "Sample proportions",
          "The sample proportion distribution: mean and variance", "Why all this machinery of sample proportions?",
          "Using the normal approximation to the sample proportion", "The data, the sample proportion, and the normal approximation"):
    present(teach, "teaching box", '<div class="bt">' + k)

# ================================================================ Concept 1 and Worked example 15
c1 = CON[1]["worked"][0]
tb = tables(c1)
half = F(1, 2)
d6 = pmf(6, half)
report([frac_cell(c) for c in tb[0][1][1]] == d6 and [frac_cell(c) for c in tb[0][0][1]] == list(range(7)), "WE15 table of X", "")
report([frac_cell(c) for c in tb[1][1][1]] == d6 and [frac_cell(c) for c in tb[1][0][1]] == [F(k, 6) for k in range(7)], "WE15 table of p-hat", "")
mX, vX = mean_var(range(7), d6)
mP, vP = mean_var([F(k, 6) for k in range(7)], d6)
report((mX, vX) == (3, F(3, 2)), "WE15 E(X), Var(X) from the table", f"{mX} {vX}")
present(c1, "WE15", r"E(X)=np=3\qquad\text{and}\qquad\operatorname{Var}(X)=npq=1\tfrac12.")
report((mP, vP) == (half, F(1, 24)), "WE15 E(p-hat), Var(p-hat) from the table", f"{mP} {vP}")
present(c1, "WE15", r"\frac{pq}n=\tfrac1{24}.\]")
coin_count = [sum(1 for s in product((0, 1), repeat=6) if sum(s) == k) for k in range(7)]
report([F(c, 64) for c in coin_count] == d6, "WE15 by enumeration of 64 sequences", "")

C1 = BLK["C1"]
for where, blk, n, p, ex, vx, ep, vp in (("C1 demo", C1.split("<b>Your turn.</b>")[0], 3, F(1, 3), "1", r"\tfrac23", r"\tfrac13", r"\tfrac2{27}"),
                                         ("C1 your turn", C1.split("<b>Your turn.</b>")[1], 4, half, "2", "1", r"\tfrac12", r"\tfrac1{16}")):
    tb = tables(blk)
    d = pmf(n, p)
    report([frac_cell(c) for c in tb[0][1][1]] == d and [frac_cell(c) for c in tb[1][1][1]] == d, f"{where} probabilities", "")
    report([frac_cell(c) for c in tb[1][0][1]] == [F(k, n) for k in range(n + 1)], f"{where} p-hat values", "")
    mX, vX = mean_var(range(n + 1), d)
    mP, vP = mean_var([F(k, n) for k in range(n + 1)], d)
    report((frac_cell(ex), frac_cell(vx), frac_cell(ep), frac_cell(vp)) == (mX, vX, mP, vP), f"{where} means and variances", f"{mX} {vX} {mP} {vP}")
    present(blk, where, rf"\(E(X)=np={ex}\) and \(\operatorname{{Var}}(X)=npq={vx}\)")
    present(blk, where, rf"\(E(\hat p)=p={ep}\) and \(\operatorname{{Var}}(\hat p)=\dfrac{{pq}}n={vp}\)")
present(CON[1]["demo"], "C1 demo", "one red and two blue. It is spun three times")
present(CON[1]["attempt"], "C1 your turn", "A coin is tossed four times")

# ================================================================ Concept 2 and Worked example 16
w16 = CON[2]["worked"][0]


def within(n, p, eps):
    return [k for k in range(n + 1) if abs(F(k, n) - p) <= eps]


report(within(20, F(1, 3), F(5, 100)) == [6, 7] and within(20, F(1, 3), F(1, 10)) == [5, 6, 7, 8], "WE16 values within 0.05 and 0.1", "")
report(F(20, 3).denominator != 1, "WE16 20 is not a multiple of 3", "")
pa, pb = bsum(20, F(1, 3), 6, 7), pmf(20, F(1, 3))[5] + pmf(20, F(1, 3))[8]
chk(w16, "WE16", r"\\&amp;=@\ldots\quad\text{(save", str(D(pa))[:7])
chk(w16, "WE16", r"is within 0.05 of \(p\) is about @.</p>", rnd(pa, 3))
chk(w16, "WE16", r"\\&amp;=@\ldots,\end{aligned}", str(D(pb))[:7])
chk(w16, "WE16", r"of the actual value is about @.</p>", rnd(pa + pb, 3))
present(w16, "WE16", r"P\big(\hat p=\tfrac5{20}\ \text{ or }\ \hat p=\tfrac8{20}\big)")
C2 = BLK["C2"]
for where, blk, n, p in (("C2 demo", C2.split("<b>Your turn.</b>")[0], 12, F(1, 4)), ("C2 your turn", C2.split("<b>Your turn.</b>")[1], 15, F(2, 3))):
    ka, kb = within(n, p, F(5, 100)), within(n, p, F(1, 10))
    d = pmf(n, p)
    report(len(ka) == 1 and len(kb) == 3, f"{where} values", f"{ka} {kb}")
    chk(blk, where, r"\big)^" + str(n - ka[0]) + r"\doteq@\)<br>", rnd(d[ka[0]], 3))
    chk(blk, where, r"\doteq@+@+@\doteq@\)", *[rnd(d[k], 4) for k in kb], rnd(sum(d[k] for k in kb), 3))
    report(rnd(sum(Decimal(rnd(d[k], 4)) for k in kb), 3) == rnd(sum(d[k] for k in kb), 3), f"{where} sum of rounded terms", "")
present(CON[2]["demo"], "C2 demo", r"12 Bernoulli trials")
present(CON[2]["demo"], "C2 demo", r"actual value of \(p\) is \(\tfrac14\)")
present(CON[2]["attempt"], "C2 your turn", r"actual value of \(p\) is \(\tfrac23\)")

# ================================================================ Concept 3 and Worked example 17
w17 = CON[3]["worked"][0]
s17 = math.sqrt(F(1, 3) * F(2, 3) / 2000)
report(F(1, 3) * F(2, 3) / 2000 == F(1, 9000), "WE17 variance 1/9000", "")
chk(w17, "WE17", r"the standard deviation is about @.</p>", rnd(s17, 5))
chk(w17, "WE17", r"find \(P(@\le\hat p\le@)\), so", rnd(F(1, 3) - F(1, 100), 4), rnd(F(1, 3) + F(1, 100), 4))
chk(w17, "WE17", r"find \(P(@\le\hat p\le@)\). The", rnd(F(1, 3) - F(2, 100), 4), rnd(F(1, 3) + F(2, 100), 4))
for e, places in ((0.01, 4), (0.02, 4)):
    z = e / s17
    chk(w17, "WE17", r"z&amp;=\frac{" + f"{e}" + r"}{0.01054}\\&amp;\doteq@.\end{aligned}", rnd(z, 4))
    chk(w17, "WE17", r"z&amp;=\frac{-" + f"{e}" + r"}{0.01054}\\&amp;\doteq@.\end{aligned}", rnd(-z, 4))
    chk(w17, "WE17", r"P(-" + rnd(z, 4) + r"\le Z\le" + rnd(z, 4) + r")\doteq@.\]", rnd(2 * Phi(z) - 1, 2))
    report(rnd(2 * Phi(e / s17) - 1, 2) == rnd(2 * Phi(z) - 1, 2), f"WE17 within {e} with unrounded sigma", "")
present(w17, "WE17", r"\text{For }0.3133,\quad z")
present(w17, "WE17", r"\text{For }0.3533,\quad z")
C3 = BLK["C3"]
for where, blk, n, p, e1, e2, cside, cval in (("C3 demo", C3.split("<b>Your turn.</b>")[0], 1000, 0.4, 0.02, 0.03, "&gt;", 0.42),
                                              ("C3 your turn", C3.split("<b>Your turn.</b>")[1], 1500, 0.3, 0.01, 0.02, "&lt;", 0.28)):
    s = math.sqrt(p * (1 - p) / n)
    chk(blk, where, r"\(\sigma=\sqrt{@}\doteq@\)", f"{p * (1 - p) / n:.5f}".rstrip("0"), rnd(s, 5))
    for part, e in (("a", e1), ("b", e2)):
        zs = z2(e / s)
        prob = Decimal(tab(zs)) - Decimal(tab("-" + zs))
        chk(blk, where, f"<b>{part}</b> " + r"\(z=\pm" + f"{e}" + r"\div" + rnd(s, 5) + r"\doteq\pm@\), so \(P(@\le\hat p\le@)\doteq@-@=@\)",
            zs, f"{p - e:.2f}", f"{p + e:.2f}", tab(zs), tab("-" + zs), str(prob))
    zc = z2((cval - p) / s)
    pc = 1 - Decimal(tab(zc)) if cside == "&gt;" else Decimal(tab(zc))
    chk(blk, where, r"\doteq P(Z" + cside + r"@)=1-@=@\)", zc, tab(zc.lstrip("-")), str(pc))
present(CON[3]["demo"], "C3 demo", "A survey of 1000 voters is being used")
present(CON[3]["demo"], "C3 demo", r"value of \(p\) is 0.4")
present(CON[3]["attempt"], "C3 your turn", r"value of \(p\) is 0.3")

# ================================================================ Concept 4 and Worked example 19
w19 = CON[4]["worked"][0]
f19 = [0, 2, 6, 15, 20, 23, 17, 13, 1, 3, 0]
LB = read("l17b.html")
we9 = LB.split('Worked example 9</span>')[1].split('Worked example 10</span>')[0]
report([c for h, c in rows(we9) if h == "f"][0] == [str(v) for v in f19], "WE19 data are the 17B Worked example 9 data", "")


def sim(f, n, p, half):
    N = sum(f)
    fr = [F(v, N) for v in f]
    cf = [sum(fr[:k + 1]) for k in range(n + 1)]
    m, v = mean_var([F(k, n) for k in range(n + 1)], fr)
    d = pmf(n, p)
    cb = [sum(d[:k + 1]) for k in range(n + 1)]
    sd = math.sqrt(p * (1 - p) / n)
    zs = [(k / n + half - float(p)) / sd for k in range(n + 1)]
    return fr, cf, m, math.sqrt(v), d, cb, sd, zs


fr, cf, m, s, d, cb, sd, zs = sim(f19, 10, half, 0.05)
tb = tables(w19)
r = {h: c for h, c in tb[0]}
report([F(clean(c)) for c in r["f_r"]] == fr, "WE19 f_r", "")
report([clean(c) for c in r["cf_r"]] == [rnd(v, 2) for v in cf], "WE19 cf_r", str([clean(c) for c in r["cf_r"]]))
chk(w19, "WE19", r"Calculation gives \(\bar x=@\) and \(s\doteq@\)", str(D(m)), rnd(s, 3))
chk(w19, "WE19", r"\sqrt{2.5}\doteq@\)", rnd(sd, 3))
r = {h: c for h, c in tb[1]}
report([clean(c) for c in r["P(\\hatp)"]] == [rnd(v, 3) for v in d], "WE19 P(p-hat)", "")
report([clean(c) for c in r["Cmlve"]] == [rnd(v, 3) for v in cb], "WE19 cumulative", "")
r = {h: c for h, c in tb[2]}
pz = [clean(c) for c in r["z"]]
report(all(abs(float(a) - b) < 0.006 for a, b in zip(pz, zs)), "WE19 z-scores (CC +0.05)", str(pz))
report([clean(c) for c in r["\\Phi(z)"]] == [rnd(Phi(float(a)), 3) for a in pz], "WE19 Phi at the printed z", "")
C4 = BLK["C4"]
for where, qblk, blk, f, p in (("C4 demo", CON[4]["demo"], C4.split("<b>Your turn.</b>")[0], [0, 4, 10, 22, 28, 20, 11, 4, 1], half),
                               ("C4 your turn", CON[4]["attempt"], C4.split("<b>Your turn.</b>")[1], [5, 15, 29, 26, 16, 7, 2, 0, 0], F(1, 3))):
    report([c for h, c in rows(qblk) if h == "f"][0] == [str(v) for v in f], f"{where} data printed", "")
    src = LB.split("Concept 5", 1)[1]
    report(("<tr><th>\\(f\\)</th>" + "".join(f"<td>{v}</td>" for v in f) + "</tr>") in src, f"{where} data match Lesson 17B", "")
    fr, cf, m, s, d, cb, sd, zs = sim(f, 8, p, 1 / 16)
    tb = tables(blk)
    r = {h: c for h, c in tb[0]}
    report([F(clean(c)) for c in tb[0][0][1]] == [F(k, 8) for k in range(9)], f"{where} p-hat row", "")
    report([F(clean(c)) for c in r["f_r"]] == fr, f"{where} f_r", "")
    report([F(clean(c)) for c in r["cf_r"]] == cf, f"{where} cf_r", "")
    N = sum(f)
    xbar = F(sum(k * v for k, v in enumerate(f)), N)
    sx = math.sqrt(F(sum(k * k * v for k, v in enumerate(f)), N) - xbar ** 2)
    chk(blk, where, r"\bar x=\dfrac{@}8=@\)", str(D(xbar)), str(D(m)))
    chk(blk, where, r"\(s\doteq\dfrac{@}8\doteq@\)", rnd(sx, 3), rnd(s, 3))
    report(abs(sx / 8 - s) < 1e-12, f"{where} s of p-hat = s of x / 8", "")
    report([clean(c) for c in tb[1][1][1]] == [rnd(v, 3) for v in cb], f"{where} cumulative binomial", str([clean(c) for c in tb[1][1][1]]))
    chk(blk, where, "\\doteq@\\).\n<table", rnd(sd, 3))
    pz = [clean(c) for c in tb[2][1][1]]
    report(pz == [rnd(z, 3) for z in zs], f"{where} z-scores with CC 1/16", str(pz))
    report([clean(c) for c in tb[2][2][1]] == [rnd(Phi(z), 3) for z in zs], f"{where} Phi(z)", "")

# ================================================================ Textbook homework (Exercise 17D)
B = BLK
# Q1
seq = "♡♣♠♢♢♠♡♠♠♢"
report(TQ["1"].count(r"\spadesuit") == seq.count("♠") == 4 and TQ["1"].count(r"\diamondsuit") == 3, "Q1b suits printed", "")
report(TQ["1"].count("H T H T T") == 1 and "P P P F F P P P P F P P" in TQ["1"], "Q1 data printed", "")
chk(B["1"], "Q1", r"<b>a</b> \(\tfrac@\)", "25")
present(B["1"], "Q1", r"<b>b</b> \(\tfrac4{10}=\tfrac25\)")
present(B["1"], "Q1", r"<b>c</b> \(\tfrac9{12}=\tfrac34\)")
report("P P P F F P P P P F P P".split().count("P") == 9 and "HTHTT".count("H") == 2, "Q1 counts", "")
# Q2, Q3
tb = tables(B["2"])
d5 = pmf(5, half)
report([frac_cell(c) for c in tb[0][1][1]] == d5 and [frac_cell(c) for c in tb[1][1][1]] == d5 and [frac_cell(c) for c in tb[1][0][1]] == [F(k, 5) for k in range(6)], "Q2 tables", "")
report(mean_var([F(k, 5) for k in range(6)], d5)[0] == half, "Q2c mean 0.5", "")
present(B["2"], "Q2", "<b>c</b> 0.5")
f3 = [1, 1, 3, 2, 6, 7]
report([c for h, c in rows(TQ["3"]) if h == "f"][0] == [str(v) for v in f3], "Q3 data", "")
tb = tables(B["3"])
report([frac_cell(c) for c in tb[0][1][1]] == [F(v, 20) for v in f3], "Q3a f_r", "")
m3 = sum(F(k, 5) * F(v, 20) for k, v in enumerate(f3))
chk(B["3"], "Q3", r"<b>b</b> @ &emsp;", str(D(m3)))
# Q4
c4 = sum(math.comb(10, k) for k in range(11) if F(k, 10) > F(3, 4))
report(c4 == sum(1 for s_ in product((0, 1), repeat=10) if sum(s_) > 7.5), "Q4 count by enumeration", str(c4))
chk(B["4"], "Q4", r"=\dfrac{@}{1024}\doteq@\%\)", str(c4), rnd(F(c4, 1024) * 100, 2))
# Q6: draw the samples from the printed class list
cls = dict((int(a), b) for a, b in re.findall(r"<span>(\d+)\. [A-Za-z]+ ([YN])</span>", TQ["6"]))
report(len(cls) == 32, "Q6 class list read", str(len(cls)))
sets = [[int(x) for x in s_.split("&ensp;")] for s_ in re.findall(r'<span>((?:\d+&ensp;){4}\d+)</span>', TQ["6"].split('class="rn17d"')[1])]
report(len(sets) == 10 and sets[0] == [12, 15, 3, 30, 17], "Q6 ten random samples read", str(len(sets)))
ph = [F(sum(cls[i] == "Y" for i in s_), 5) for s_ in sets]
pop = F(sum(v == "Y" for v in cls.values()), 32)
chk(B["6"], "Q6", r"<b>a</b> \(12\div32=@\)", str(D(pop)))
report(pop == F(12, 32), "Q6a 12 of 32", "")
chk(B["6"], "Q6", r"<b>b</b> @ (only", str(D(ph[0])))
present(B["6"], "Q6", r"\(\hat p=" + r",\ ".join(f"{float(v):g}" for v in ph) + r"\)")
freq = [ph.count(F(k, 5)) for k in range(6)]
report([clean(c) for c in tables(B["6"])[0][1][1]] == [str(v) for v in freq], "Q6c frequencies", str(freq))
svg6 = read("svg/a17d_q6d.svg")
report(svg6.count("<circle") == sum(freq), "Q6d dot plot has one dot per sample", "")
present(TQ["6"], "Q6", "obtained in part <b>c</b>.")


def zline(blk, where, template, z, *extra):
    chk(blk, where, template, z2(z), *extra)


# Q7
s = math.sqrt(0.2 * 0.8 / 500)
chk(B["7"], "Q7", r"\div500}\doteq@\)", rnd(s, 5))
z = 0.02 / s
chk(B["7"], "Q7", r"P(Z&gt;@)=1-@=@\doteq@\%\)", z2(z), tab(z2(z)), str(1 - T(z)), rnd((1 - T(z)) * 100, 0))
# Q8
s = math.sqrt(80 * 0.25 * 0.75)
z = 4.5 / s
chk(B["8"], "Q8a", r"\sigma=\sqrt{15}\doteq@\)", rnd(s, 3))
chk(B["8"], "Q8a", r"P(-@\le Z\le@)=2\times@-1=@\doteq@\%\).<br>", z2(z), z2(z), tab(z2(z)), str(2 * T(z) - 1), rnd((2 * T(z) - 1) * 100, 0))
s = math.sqrt(0.25 * 0.75 / 80)
z = 0.05 / s
chk(B["8"], "Q8b", r"\div80}\doteq@\)", rnd(s, 4))
chk(B["8"], "Q8b", r"P(-@\le Z\le@)=2\times@-1=@\doteq@\%\). (The", z2(z), z2(z), tab(z2(z)), str(2 * T(z) - 1), rnd((2 * T(z) - 1) * 100, 0))
chk(B["8"], "Q8", r"exact answer is @%", rnd(bsum(80, F(1, 4), 16, 24) * 100, 0))
# Q9
s = math.sqrt(0.7 * 0.3 / 300)
z = -0.05 / s
chk(B["9"], "Q9", r"\div300}\doteq@\)", rnd(s, 5))
chk(B["9"], "Q9a", r"P(Z\ge@)=@\doteq@\%\)", z2(z), tab(z2(-z)), rnd(T(-z) * 100, 0))
chk(B["9"], "Q9b", r"P(-@\le Z\le@)=2\times@-1=@\doteq@\%\)", z2(-z), z2(-z), tab(z2(-z)), str(2 * T(-z) - 1), rnd((2 * T(-z) - 1) * 100, 0))
# Q10
chk(B["10"], "Q10a", r"0.95^{100}\doteq@\doteq@\%\) &emsp;", rnd(F(95, 100) ** 100, 4), rnd(F(95, 100) ** 100 * 100, 1))
report(bsum(100, F(1, 20), 0, 1) == F(95, 100) ** 100 + 100 * F(5, 100) * F(95, 100) ** 99 and [k for k in range(101) if F(k, 100) < F(2, 100)] == [0, 1], "Q10a(ii) is X <= 1", "")
chk(B["10"], "Q10a", r"0.95^{99}\doteq@\doteq@\%\)", rnd(bsum(100, F(1, 20), 0, 1), 4), rnd(bsum(100, F(1, 20), 0, 1) * 100, 1))
s = math.sqrt(0.05 * 0.95 / 1000)
z = -0.02 / s
chk(B["10"], "Q10b", r"\div1000}\doteq@\)", rnd(s, 4))
chk(B["10"], "Q10b", r"P(Z&lt;@)=1-@=@\doteq@\%\)", z2(z), tab(z2(-z)), str(T(z)), rnd(T(z) * 100, 1))
# Q11
s = math.sqrt(F(6, 10) * F(4, 10) / 20)
chk(B["11"], "Q11a", r"\sigma^2=@\), so \(\sigma\doteq@\)", str(D(F(6, 10) * F(4, 10) / 20)), rnd(s, 4))
z = (0.4 - 0.6) / s
chk(B["11"], "Q11c", r"P(Z\le@)=1-@=@\doteq@\%\)<br>", z2(z), tab(z2(-z)), str(T(z)), rnd(T(z) * 100, 1))
report(rnd(bsum(20, F(3, 5), 0, 8) * 100, 1) == "5.7" and rnd(bsum(20, F(3, 5), 0, 15) * 100, 0) == "95", "Q11 the quoted exact results 5.7% and 95%", "")
chk(B["11"], "Q11d", r"\dfrac{5.7-3.4}{5.7}\doteq@\%\)", rnd((Decimal("5.7") - Decimal(rnd(T(z) * 100, 1))) / Decimal("5.7") * 100, 0))
z = (0.75 - 0.6) / s
chk(B["11"], "Q11e", r"P(Z\le@)=@\doteq@\%\)<br>", z2(z), tab(z2(z)), rnd(T(z) * 100, 1))
chk(B["11"], "Q11f", r"\dfrac{95-91.5}{95}\doteq@\%\)", rnd((95 - Decimal(rnd(T(z) * 100, 1))) / 95 * 100, 1))
# Q12
ns = [1000, 500, 100, 50, 25]
tq = {h: c for h, c in rows(TQ["12"])}
ex12 = [bsum(n, half, 0, math.floor(F(52, 100) * n)) for n in ns]
report([clean(c) for c in tq["exact"]] == [rnd(v, 4) for v in ex12], "Q12 printed exact row", str([rnd(v, 4) for v in ex12]))
ta = {h: c for h, c in rows(B["12"])}
zz = [0.02 / (0.5 / math.sqrt(n)) for n in ns]
ap = [Decimal(tab(z2(z))) for z in zz]
chk(B["12"], "Q12", r"(\(z\doteq@\), @, @, @, @)", *[z2(z) for z in zz])
report([clean(c) for c in ta["approx"]] == [str(v) for v in ap], "Q12 approx row", str([str(v) for v in ap]))
report([clean(c) for c in ta["%error"]] == [rnd((Decimal(rnd(e, 4)) - a) / Decimal(rnd(e, 4)) * 100, 1) for e, a in zip(ex12, ap)], "Q12 % error row",
       str([rnd((Decimal(rnd(e, 4)) - a) / Decimal(rnd(e, 4)) * 100, 1) for e, a in zip(ex12, ap)]))
# Q13, Q14
s = math.sqrt(0.25 / 50)
z = 0.1 / s
chk(B["13"], "Q13", r"\div50}\doteq@\)", rnd(s, 4))
chk(B["13"], "Q13", r"P(Z&gt;@)=1-@=@\doteq@\%\)", z2(z), tab(z2(z)), str(1 - T(z)), rnd((1 - T(z)) * 100, 0))
s = math.sqrt(0.3 * 0.7 / 100)
z = 0.1 / s
chk(B["14"], "Q14", r"\sqrt{p(1-p)/n}\doteq@\)", rnd(s, 4))
chk(B["14"], "Q14", r"P(Z\ge@)=1-@=@\doteq@\%\)", z2(z), tab(z2(z)), str(1 - T(z)), rnd((1 - T(z)) * 100, 1))
# Q15: smallest n with sqrt(pq/n) < k%
for part, p, lab in (("a", F(7, 10), "2100"), ("b", F(8, 10), "1600"), ("c", F(1, 2), "2500")):
    seg = B["15"].split(f"<b>{part}</b>")[1].split("<b>")[0]
    for i, k in zip(("i", "ii", "iii", "iv"), (4, 3, 2, 1)):
        bound = 10000 * p * (1 - p) / k ** 2
        nmin = next(n for n in range(1, 5000) if p * (1 - p) / n < F(k, 100) ** 2)
        shown = rnd(bound, 2).rstrip("0").rstrip(".") if bound.denominator in (1, 2, 4) else rnd(bound, 1)
        chk(seg, f"Q15{part}({i})", f"({i}) " + r"\(n&gt;@\), so @ &ensp;", shown, str(nmin))
    chk(seg, f"Q15{part}(v)", r"(v) \(n&gt;\dfrac{@}{k^2}\)", str(int(10000 * p * (1 - p))))
    report(str(int(10000 * p * (1 - p))) == lab, f"Q15{part} 10000pq", "")
# Q16
chk(B["16"], "Q16", r"=\dfrac{@}{1024}\doteq@\) &emsp; (ii) \(40\times@\doteq@\)", str(math.comb(10, 6)), rnd(F(210, 1024), 3), rnd(F(210, 1024), 3), str(round(40 * 0.205)))
# Q17 (sum at least 10 with two dice)
dice = [a + b for a in range(1, 7) for b in range(1, 7)]
p17 = F(sum(s_ >= 10 for s_ in dice), 36)
report(p17 == F(1, 6), "Q17a by enumeration", str(p17))
present(B["17"], "Q17", r"\(p=\tfrac6{36}=\tfrac16\)")
chk(B["17"], "Q17b", r"P(0\le X\le4)\doteq@\)", rnd(bsum(20, p17, 0, 4), 4))
mu, sg = 20 * p17, math.sqrt(20 * p17 * (1 - p17))
report(sg == 5 / 3 or abs(sg - 5 / 3) < 1e-12, "Q17 sigma = 5/3", "")
zc, zd = (4 - float(mu)) / sg, (4.5 - float(mu)) / sg
chk(B["17"], "Q17c", r"P(X\le4)\doteq P(Z\le@)=@\)<br>", z2(zc), tab(z2(zc)))
chk(B["17"], "Q17d", r"P(X\le4.5)\doteq P(Z\le@)=@\)", z2(zd), tab(z2(zd)))
ze = (0.2 - float(p17)) / math.sqrt(p17 * (1 - p17) / 20)
report(math.sqrt(p17 * (1 - p17) / 20) - 1 / 12 < 1e-12 and abs(ze - zc) < 1e-12, "Q17e same z as part c", "")
chk(B["17"], "Q17e", r"P(\hat p\le0.2)\doteq P(Z\le@)=@\)", z2(ze), tab(z2(ze)))
# Q18
s = math.sqrt(0.67 * 0.33 / 100)
chk(B["18"], "Q18b", r"\div100}\doteq@\)", rnd(s, 3))
chk(B["18"], "Q18b", r"1.96\sigma\doteq@=@\%\)", rnd(1.96 * s, 2), rnd(1.96 * s * 100, 0))
report(rnd((0.67 - 1.96 * s) * 100, 0) == "58" and rnd((0.67 + 1.96 * s) * 100, 0) == "76", "Q18b interval [58%, 76%]", "")
present(B["18"], "Q18", r"\([58\%,\ 76\%]\)")
nb = 1.96 ** 2 * 0.67 * 0.33 / 0.01 ** 2
n18 = next(n for n in range(8000, 9000) if 1.96 * math.sqrt(0.67 * 0.33 / n) <= 0.01)
chk(B["18"], "Q18b", r"gives \(n\ge@\), so \(n\ge@\)", rnd(nb, 1), str(n18))
report(abs(Phi(1.96) - Phi(-1.96) - 0.95) < 0.0005, "Q18a 1.96 gives 95%", "")

# ================================================================ Past papers
intro = re.search(r'<div class="pp-intro"><span><b>Suggested time: (\d+) minutes</b></span><span><b>(\d+) marks</b></span><span>([^<]*)</span>', pps)
marks = {k: int(re.search(r'<span class="mk">(\d+) marks?</span>', v).group(1)) for k, v in PPQ.items()}
total = sum(marks.values())
report(intro is not None and int(intro.group(2)) == total and 15 <= total <= 22, "PP total marks", f"{total}")
report(intro is not None and int(intro.group(1)) == 5 * round(1.5 * total / 5), "PP time", f"{intro.group(1) if intro else None} min for {total} marks")
report(intro is not None and "use the standard normal table at the end of the Revision section" in intro.group(3), "PP intro table line", "")
report(sorted(PPQ) == list(range(1, 7)) and sorted(PPA) == list(range(1, 7)), "PP numbering", "")
report([marks[k] for k in sorted(marks)] == [1, 2, 4, 4, 5, 3], "PP marks as printed", str(marks))
for k in sorted(PPQ):
    lq = re.match(r"(.*?)</span><span class=\"mk\">", PPQ[k], re.S).group(1)
    la = re.match(r"(.*?)</span></div>", PPA[k], re.S).group(1)
    report(clean(lq) == clean(la), f"PP{k} labels match", clean(lq)[:80])
    report(PPQ[k].count('<div class="hint"><b>Hint:</b>') == 1, f"PP{k} one hint", "")
    sub = [int(x) for x in re.findall(r'<div class="pp-sub"><span>.*?</span><span class="mk">(\d+)</span></div>', PPQ[k], re.S)]
    report(not sub or sum(sub) == marks[k], f"PP{k} part marks", str(sub))
    hint = re.search(r'<div class="hint"><b>Hint:</b> (.*?)</div>', PPQ[k]).group(1)
    if k in (2, 3):
        report(hint == {2: r"what are \(n\) and \(p\) here?", 3: "for (i), recall the rule of thumb from Lesson 17C."}[k], f"PP{k} hint unchanged", hint)
    else:
        bad = re.search(r"\d|%|standard deviation|deviation|sigma|mean|variance|formula|z-score|z\b|normal|empirical|continuity|sqrt|rule|np|nq|table|times|probabilit", hint.replace(r"\hat p", "").replace(r"\(n\)", "").replace(r"\(p\)", ""))
        report(hint.endswith("?") and not bad, f"PP{k} hint is an identification question (no numbers or method words)", hint)
    meth = PPA[k].count("Using the normal approximation to \\(\\hat p\\) without a continuity correction, as in the school solution.")
    report(meth == (1 if k in (3, 4, 5) else 0), f"PP{k} method line", str(meth))
labels = {1: "Baulkham Hills High School, 2020, Year 12 Trial Examination, Mathematics Extension1,Q4",
          2: "Killara High School, 2021, Year 12 Mathematics Extension1 Trial Examination,Q12(a)(ii)",
          3: "James Ruse Agricultural High School, 2023, Year 12 Trial HSC Examination, Mathematics Extension1,Q15(c)",
          4: "Hurlstone Agricultural High School, 2023, Higher School Certificate Trial Examination, Mathematics Extension1,Q13(c)(ii)",
          5: "Killara High School, 2024, Year 12 Examination, Mathematics Extension1 HSC Trial Examination,Q14(c)",
          6: "Abbotsleigh, 2024, Higher School Certificate Assessment 4 Trial Examination, Mathematics Extension1,Q14(c)(i)"}
for k, lab in labels.items():
    got = re.sub(r"<[^>]+>", "", re.match(r"(.*?)</span><span class=\"mk\">", PPQ[k], re.S).group(1)).replace("&nbsp;", "")
    report(got.replace(" ", "") == lab.replace(" ", ""), f"PP{k} source label", got[:90])
present(PPQ[6], "PP6", "<i>You may use the information [in the standard normal table at the end of the Revision section] to answer this question.</i>")
present(PPQ[4], "PP4", "make reference to the extract below from a table of \\(z\\) scores).")
# PP4 printed extract = the Revision table rows 1.1-1.3
ext = {h: c for h, c in rows(PPQ[4]) if h in ("1.1", "1.2", "1.3")}
report(all([clean(c) for c in ext[h]] == [TAB[f"{h}{j}"] for j in range(10)] for h in ext) and len(ext) == 3, "PP4 extract equals the table", "")
# PP1
nmin = next(n for n in range(1, 200) if 0.3 * 0.7 / n <= 0.07 ** 2)
report(nmin == 43 and "B.&ensp;\\(n=43\\)" in PPQ[1], "PP1 smallest n = 43 is option B", str(nmin))
chk(PPA[1], "PP1", r"n\ge\frac{0.21}{0.0049}\doteq@.\]", rnd(0.21 / 0.0049, 2))
chk(PPA[1], "PP1", r"With \(n=42\), the standard deviation is about @,", rnd(math.sqrt(0.21 / 42), 4))
report(math.sqrt(0.21 / 42) > 0.07 >= math.sqrt(0.21 / 43), "PP1 A fails, B works", "")
present(PPA[1], "PP1", "<b>Answer B.</b>")
# PP2
present(PPA[2], "PP2", r"=\frac3{5000},")
report(F(9, 10) * F(1, 10) / 150 == F(3, 5000), "PP2 variance 3/5000", "")
chk(PPA[2], "PP2", r"\sqrt{\frac3{5000}}\doteq@.\]", rnd(math.sqrt(3 / 5000), 4))
# PP3
chk(PPA[3], "PP3", r"\(np=100\times0.2=@\) and \(nq=100\times0.8=@\)", "20", "80")
chk(PPA[3], "PP3", r"{100}}=@\).</p>", rnd(math.sqrt(0.2 * 0.8 / 100), 2))
chk(PPA[3], "PP3", r"=P(-@\le Z\le@)\\&amp;=@-@\\&amp;=@.\end{aligned}", "2.5", "2.5", tab("2.50"), tab("-2.50"), str(Decimal(tab("2.50")) - Decimal(tab("-2.50"))))
# PP4
v4 = 0.23 * 0.77 / 60
chk(PPA[4], "PP4", r"{60}\doteq@,\qquad\sigma\doteq@.\]", f"{v4:.7f}", rnd(math.sqrt(v4), 6))
z = 0.07 / math.sqrt(v4)
chk(PPA[4], "PP4", r"\doteq@\doteq@\]", rnd(z, 4), z2(z))
chk(PPA[4], "PP4", r"P(Z&gt;@)=1-@=@.\]", z2(z), tab(z2(z)), str(1 - T(z)))
report(TAB[z2(z)] == "0.9015" and [c for h, c in rows(PPQ[4]) if h == "1.2"][0][9] == "<td>0.9015</td>".replace("<td>", "").replace("</td>", ""), "PP4 value in the printed extract", "")
# PP5
s5 = math.sqrt(0.7 * 0.3 / 1012)
chk(PPA[5], "PP5", r"{1012}}\doteq@.\]", rnd(s5, 7))
chk(PPA[5], "PP5", r"=1012\times0.7=@\) and \(n(1-p)=1012\times0.3=@\)", rnd(1012 * 0.7, 1), rnd(1012 * 0.3, 1))
z = -0.03 / s5
chk(PPA[5], "PP5", r"\doteq P(Z\le@)\\&amp;=1-@\\&amp;=@\doteq@\%.", z2(z), tab(z2(-z)), str(T(z)), rnd(T(z) * 100, 1))
report(T(z) < Decimal("0.05"), "PP5 below 0.05, so doubt", "")
# PP6
n6 = F(81 * 19, 10000) * 9_000_000
report(n6 == 1385100 and math.sqrt(0.81 * 0.19 / 1385100) <= 1 / 3000 + 1e-15 and math.sqrt(0.81 * 0.19 / 1385099) > 1 / 3000, "PP6 minimum n = 1 385 100", str(n6))
present(PPA[6], "PP6", r"n\ge0.1539\times9\,000\,000=1\,385\,100.\]")
present(PPA[6], "PP6", "at least 1&nbsp;385&nbsp;100 trials")
report(abs(Phi(3) - Phi(-3) - 0.997) < 0.0005, "PP6 99.7% within 3 sd", "")

# ================================================================ Chapter 17 review
R = RA
chk(R["1"], "R1", r"=\tfrac{@}{324}\doteq@\)", "125", rnd(F(125, 324), 3))
report(math.comb(4, 3) * F(5, 6) ** 3 * F(1, 6) == F(125, 324) and math.comb(4, 2) * F(5, 6) ** 2 * F(1, 6) ** 2 == F(25, 216), "R1 exact", "")
chk(R["1"], "R1", r"=\tfrac{25}{216}\doteq@\)", rnd(F(25, 216), 3))
chk(R["2"], "R2", r"\big(\tfrac16\big)^2\doteq@\)", rnd(bsum(15, F(5, 6), 13, 15), 3))
chk(R["3"], "R3", r"(0.8)^3\doteq@\)", sf(pmf(10, F(1, 5))[7], 3))
n4 = next(n for n in range(1, 50) if 1 - F(3, 4) ** n > F(95, 100))
chk(R["4"], "R4", r"\doteq@\). The experiment needs to be repeated @ times", rnd(math.log(0.05) / math.log(0.75), 1), str(n4))
d8 = pmf(6, F(1, 8))
report([clean(c) for c in tables(R["5"])[0][1][1]] == [rnd(v, 4) for v in d8], "R5 table", "")
chk(R["5"], "R5", r"\(1000\times@\doteq@\) times", rnd(d8[3], 4), str(round(1000 * d8[3])))
chk(R["5"], "R5", r"\(1000\times(@+@+@)\doteq@\) times", rnd(d8[3], 4), rnd(d8[4], 4), rnd(d8[5], 4), str(round(1000 * sum(d8[3:]))))
p6 = F(sum(s_ > 10 for s_ in dice), 36)
report(p6 == F(1, 12), "R6b sum more than 10", str(p6))
present(R["6"], "R6", r"\(p=\tfrac1{12}\) and \(q=\tfrac{11}{12}\)")
present(RQ["6"], "R6", "the player wins if the sum is more than 10.")
for part, n, p in zip("abcdef", (20, 70, 6, 120, 300, 5), (F(1, 5), F(1, 2), F(4, 5), F(2, 5), F(1, 10), F(1, 4))):
    mu, var = n * p, n * p * (1 - p)
    def g(v):
        v = D(v)
        return str(int(v)) if v == v.to_integral() else str(v.normalize())
    chk(R["7"], f"R7{part}", f"<b>{part}</b> " + r"@, @, @" + (" &emsp;" if part != "f" else "</div>"), g(mu), g(var), rnd(math.sqrt(var), 2))
mu, var = 3, F(285, 100)
s = math.sqrt(var)
chk(R["8"], "R8a", r"mean 3, variance @, standard deviation \(\doteq@\)", "2.85", rnd(s, 2))
ks = [k for k in range(61) if 3 - s <= k <= 3 + s]
report(ks == [2, 3, 4], "R8b values within one sd", str(ks))
chk(R["8"], "R8b", r"\(P(X=2,\ 3\text{ or }4)\doteq@\%\)", rnd(bsum(60, F(1, 20), 2, 4) * 100, 1))
chk(R["8"], "R8c", r"\(P(0\le X\le4)\doteq@\%\). The probability of rejection is @%.", rnd(bsum(60, F(1, 20), 0, 4) * 100, 0), rnd((1 - bsum(60, F(1, 20), 0, 4)) * 100, 0))
s2 = math.sqrt(60 * 0.02 * 0.98)
chk(R["8"], "R8d", r"Mean 1.2, standard deviation \(\doteq@\), so \(X\le@\)", rnd(s2, 2), rnd(1.2 + s2, 2))
chk(R["8"], "R8d", r"\(P(X=0,\ 1\text{ or }2)\doteq@\%\). The probability of rejection is @%.", rnd(bsum(60, F(1, 50), 0, 2) * 100, 0), rnd((1 - bsum(60, F(1, 50), 0, 2)) * 100, 0))
e9 = bsum(80, half, 38, 40)
chk(R["9"], "R9a", r"\doteq@\%\) &emsp;", rnd(e9 * 100, 2))
chk(R["9"], "R9b", r"40, \(\sqrt{20}\doteq@\)", rnd(math.sqrt(20), 2))
za, zb = -2.5 / math.sqrt(20), 0.5 / math.sqrt(20)
a9 = T(zb) - T(za)
chk(R["9"], "R9e", r"are \(@\) and @, so \(P(37.5\le X\le40.5)\doteq@-@=@=@\%\)", z2(za), z2(zb), tab(z2(zb)), tab(z2(za)), str(a9), rnd(a9 * 100, 2))
chk(R["9"], "R9f", r"\dfrac{25.62-25.61}{25.62}\times100\%\doteq@\%\)", rnd((Decimal("25.62") - Decimal("25.61")) / Decimal("25.62") * 100, 2))
report(abs(Decimal(rnd(e9, 6)) - a9) / Decimal(rnd(e9, 6)) < Decimal("0.001"), "R9f error below 0.1% from unrounded values", "")
zg = 9.5 / math.sqrt(20)
chk(R["9"], "R9g", r"P(Z\ge@)=1-@=@\doteq@\%\)", z2(zg), tab(z2(zg)), str(1 - T(zg)), rnd((1 - T(zg)) * 100, 1))
p10 = F(sum(s_ >= 10 for s_ in dice), 36)
mu, sg = 80 * p10, math.sqrt(80 * p10 * (1 - p10))
report(mu == F(40, 3) and abs(sg - 10 / 3) < 1e-12, "R10 mean 40/3, sd 10/3", "")
z = (14.5 - float(mu)) / sg
chk(R["10"], "R10", r"P(Z\ge@)=1-@=@\doteq@\%\)", z2(z), tab(z2(z)), str(1 - T(z)), rnd((1 - T(z)) * 100, 0))
d12 = pmf(5, F(3, 5))
report([frac_cell(c) for c in tables(R["12"])[0][1][1]] == d12 and [F(clean(c)) for c in tables(R["12"])[0][0][1]] == [F(k, 5) for k in range(6)], "R12a table", "")
present(R["12"], "R12", r"(i) \(\tfrac{" + str(int((d12[0] + d12[1]) * 3125)) + r"}{3125}\) &emsp; (ii) \(\tfrac{" + str(int((d12[0] + d12[1] + d12[2]) * 3125)) + r"}{3125}\)")
m12, v12 = mean_var([F(k, 5) for k in range(6)], d12)
report((m12, v12) == (F(3, 5), F(6, 125)), "R12c from the table", f"{m12} {v12}")
present(R["12"], "R12", r"Mean \(\mu_{\hat p}=\tfrac35\), variance \(\tfrac6{125}\)")
chk(R["12"], "R12", r"\sqrt{30}\doteq@\)", rnd(math.sqrt(6 / 125), 3))
report(abs(math.sqrt(30) / 25 - math.sqrt(6 / 125)) < 1e-12, "R12c sqrt30/25", "")
report(F(1, 6) * F(5, 6) / 500 == F(1, 3600), "R13a sigma = 1/60", "")
chk(R["13"], "R13", r"\div\dfrac1{60}=@\)", str(D((F(70, 500) - F(1, 6)) * 60)))
s = math.sqrt(0.53 * 0.47 / 653)
z = 0.01 / s
chk(R["14"], "R14", r"\div653}\doteq@\)", rnd(s, 5))
chk(R["14"], "R14", r"P(Z&gt;@)=1-@=@\doteq@\%\)", z2(z), tab(z2(z)), str(1 - T(z)), rnd((1 - T(z)) * 100, 1))
present(RQ["8"], "R8", "no more than one standard deviation above the mean")

print(f"\n{NCHECK[0]} checks, {len(FAILS)} failed")
if FAILS:
    print("FAILED:", *FAILS, sep="\n  ")
    sys.exit(1)
print("ALL OK")
