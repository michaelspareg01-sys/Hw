"""Check of Lesson 17C (Y12 Ext 1 Ch 17 pack): Normal approximations to a binomial.

The script reads the values PRINTED in workspace/build/ch17/l17c.html (worked examples, the data in
the tutor demos, your-turn items, textbook questions and past-paper stems) and in a_17c.html (lesson
example answers, textbook homework answers, past-paper worked solutions). Each value is found with a
template ('@' marks the printed text); a template must match exactly once in its block, otherwise the
item FAILS. Every printed value is compared with an independent computation:
  - exact binomial probabilities with fractions.Fraction and math.comb (sums of nCk p^k q^(n-k)),
    cross-checked by convolving n one-stage distributions; coin counts by enumerating 2^n sequences
    for n <= 16;
  - Phi(z) from math.erf. Table look-ups follow the textbook: z rounded half-up to 2 d.p., then
    Phi(|z|) to 4 d.p. (and 1 - that for negative z). Every table value used is also compared with
    the standard normal table printed in revision.html;
  - accurate (non-table) values in the worked examples are compared with erf to the printed places;
  - n from a probability (PP 6, PP 7) is solved independently by bisection on the z equation, and
    the answer is confirmed by recomputing the probability;
  - rule-of-thumb sample sizes by searching n.
It also checks the structure (concept blocks, worked-example tags, question numbers and bands, the
omitted technology questions Q10 and Q11) and the past-paper block: marks add to the intro total
(15-22), time is 1.5 x marks rounded to 5 minutes, part marks add to each question's marks, numbering
and source labels match in both files, one hint per question, one method line per solution.

Exit status 1 if anything fails. Run: python3 workspace/checks/ch17_17c.py
"""
import itertools
import math
import os
import re
import sys
from decimal import ROUND_HALF_UP, Decimal, getcontext
from fractions import Fraction as F

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
def binom_sum(n, p, a, b):
    p = F(p)
    return sum(math.comb(n, k) * p ** k * (1 - p) ** (n - k) for k in range(max(a, 0), min(b, n) + 1))


def conv_dist(n, p):
    d = [F(1)]
    for _ in range(n):
        e = [F(0)] * (len(d) + 1)
        for k, v in enumerate(d):
            e[k] += v * (1 - p)
            e[k + 1] += v * p
        d = e
    return d


def coin_count(n, a, b):
    """Number of the 2^n head/tail sequences with a <= heads <= b, by enumeration."""
    return sum(1 for s in itertools.product((0, 1), repeat=n) if a <= sum(s) <= b)


def Phi(z):
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


def D(v):
    if isinstance(v, F):
        return Decimal(v.numerator) / Decimal(v.denominator)
    return Decimal(repr(v)) if isinstance(v, float) else Decimal(v)


def rnd(v, places):
    return str(D(v).quantize(Decimal(1).scaleb(-places), rounding=ROUND_HALF_UP))


def sf(v, digits):
    d = D(v)
    return rnd(v, digits - 1 - d.adjusted())


def z2(z):
    """z rounded half-up to 2 d.p. (as a Decimal string)."""
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


def tabz(z):
    return Decimal(tab(z2(z)))


def clean(t):
    t = re.sub(r"<[^>]+>", "", t)
    t = re.sub(r"\\,|\\!|\\;|&nbsp;|&ensp;|&emsp;|\s", "", t)
    return t.replace("\\(", "").replace("\\)", "").rstrip(".,")


def grab(block, template, where):
    pieces = template.split("@")
    cap = r"([-\d.,\\]+?)"
    rx = "".join(re.escape(pc) + (cap if i < len(pieces) - 1 else "") for i, pc in enumerate(pieces))
    found = re.findall(rx, block, re.S)
    if len(found) != 1:
        raise LookupError(f"template matched {len(found)} times in {where}: {template!r}")
    return found[0] if isinstance(found[0], tuple) else (found[0],)


def chk(block, where, template, *want):
    label = f"{where} {template[:72]}"
    try:
        got = tuple(clean(g) for g in grab(block, template, where))
        report(got == tuple(want), label, "printed " + " | ".join(got) + "  want " + " | ".join(want))
    except Exception as err:
        report(False, label, f"ERROR {err}")


def present(block, where, text):
    report(block.count(text) == 1, f"{where} text", f"{text[:90]!r} appears {block.count(text)} time(s)")


def numv(block, where, template):
    (g,) = grab(block, template, where)
    return Decimal(clean(g))


def pct(v):
    return D(v) * 100


# ---------------------------------------------------------------- blocks
ans = read("a_17c.html")
les = read("l17c.html")
parts = ans.split('<div class="ans-sec">Past-Paper Homework - Worked Solutions</div>')
if len(parts) != 2:
    sys.exit("FAIL: past-paper solutions section not found exactly once in a_17c.html")
report(ans.count("{{ahead:Lesson 17C | Normal approximations to a binomial}}") == 2, "answers headings", "ahead twice")
report(parts[0].count('<div class="ans-sec">Lesson Examples</div>') == 1 and parts[0].count('<div class="ans-sec">Textbook Homework</div>') == 1
       and parts[0].index("Lesson Examples") < parts[0].index("Textbook Homework"), "answers sections order", "")
BLK = {}
for mt in re.finditer(r'<div class="a"><span class="an">([^<]+)</span><div class="ab">(.*?)(?=<div class="a"><span class="an">|<div class="ans-sec">|\{\{ahead|$)', parts[0], re.S):
    if mt.group(1) in BLK:
        report(False, f"block {mt.group(1)}", "duplicate")
    BLK[mt.group(1)] = mt.group(2)
report(list(BLK) == ["C1", "C2", "C3", "C4", "C5", "1", "2", "3", "5", "6", "7", "8", "9", "12"], "answer blocks", str(list(BLK)))
PPA = {int(k): v for k, v in re.findall(r'<div class="ppa"><div class="pp-src"><span><span class="pn">PP (\d+)</span>(.*?)(?=<div class="ppa">|$)', parts[1], re.S)}
pps = les.split("<!-- ============ Past papers ============ -->")
teach = les.split("<!-- ============ Homework ============ -->")[0]
hw = les.split("<!-- ============ Homework ============ -->")[1].split("<!-- ============ Past papers")[0]
PPQ = {int(k): v for k, v in re.findall(r'<div class="pp"><div class="pp-src"><span><span class="pn">PP (\d+)</span>(.*?)(?=<div class="pp">|$)', pps[1], re.S)}
TQ = {k: v for k, v in re.findall(r'<div class="q"(?: style="[^"]*")?><span class="q-num">(\d+)</span>(.*?)(?=<div class="q"|\{\{band|$)', hw, re.S)}
CON = {}
for k in range(1, 6):
    seg = teach.split(f"<!-- ============ Concept {k} ============ -->")[1].split("<!-- ============")[0]
    exs = re.findall(r'<div class="ex (demo|attempt|worked)"(?: style="[^"]*")?><div class="ex-top"><span class="tag">([^<]*)</span>(.*?)(?=<div class="ex |$)', seg, re.S)
    CON[k] = {"seg": seg, "demo": [b for kd, _, b in exs if kd == "demo"][0], "attempt": [b for kd, _, b in exs if kd == "attempt"][0],
              "worked": [b for kd, _, b in exs if kd == "worked"], "tags": [t for kd, t, _ in exs if kd == "worked"]}
    report([kd for kd, _, _ in exs] == ["demo", "attempt", "worked"], f"Concept {k} blocks", "tutor demo, your turn, worked example")
report([CON[k]["tags"] for k in range(1, 6)] == [["Worked example 11"], ["Worked example 12"], ["Worked example 13"], ["Worked example 14"], ["Worked example"]],
       "worked example tags", "Examples 11-14, then 'from the text'")
report(sorted(TQ, key=int) == ["1", "2", "3", "5", "6", "7", "8", "9", "12"], "textbook question numbers", "Q4 (doubtful), Q10, Q11 (technology) omitted")
fb, rest = hw.split("{{band:F}}")[1].split("{{band:D}}")
db, eb = rest.split("{{band:E}}")
report(re.findall(r'q-num">(\d+)', fb) == ["1", "2", "3", "5", "6"] and re.findall(r'q-num">(\d+)', db) == ["7", "8", "9"]
       and re.findall(r'q-num">(\d+)', eb) == ["12"], "bands", "F: Q1-6 (Q4 omitted), D: Q7-9 (Q10, Q11 omitted), E: Q12")
report("BINOM.DIST" not in les and "RANDBETWEEN" not in les, "no spreadsheet items", "")
for k in ("5 Normal approximation to a binomial distribution", "6 A rule of thumb for using the normal approximation", "Continuity corrections",
          "Notation for normal distributions", "An example of approximations", "The continuity correction for large numbers",
          "Sampling with replacement: when is a survey a binomial experiment?", "How good an approximation is the normal?",
          "The normal approximation to a binomial distribution is a special case"):
    present(teach, "teaching box", '<div class="bt">' + k)

# ================================================================ Worked examples (textbook values)
w11 = CON[1]["worked"][0]
cnt = sum(math.comb(20, k) for k in range(13, 21))
report(cnt == coin_count(20, 13, 20), "WE11 count by enumeration", str(cnt))
chk(w11, "WE11", r"&amp;=\big(\tfrac12\big)^{20}\times@\\", f"{cnt:,}".replace(",", ""))
chk(w11, "WE11", r"\\&amp;\doteq@.\end{aligned}\]</div>", rnd(F(cnt, 2 ** 20), 3))
zz = (12.5 - 10) / math.sqrt(5)
chk(w11, "WE11", r"&amp;=\frac{12.5-10}{\sqrt5}\\&amp;\doteq@,\end{aligned}", rnd(zz, 3))
chk(w11, "WE11", r"&amp;\doteq1-\Phi(1.118)\\&amp;\doteq1-@\\", rnd(Phi(1.118), 3))
chk(w11, "WE11", r"&amp;\doteq1-0.868\\&amp;\doteq@.\end{aligned}", rnd(1 - Phi(zz), 3))
w12 = CON[2]["worked"][0]
s5 = math.sqrt(5)
chk(w12, "WE12", r"=P(@\le X\le@)\\&amp;\qquad=P(X=8", rnd(10 - s5, 3), rnd(10 + s5, 3))
xs = [x for x in range(21) if 10 - s5 <= x <= 10 + s5]
report(xs == [8, 9, 10, 11, 12], "WE12 values within one sd", str(xs))
c12 = sum(math.comb(20, k) for k in xs)
report(c12 == coin_count(20, 8, 12), "WE12 count by enumeration", str(c12))
chk(w12, "WE12", r"&amp;\qquad=\frac{@}{1024\times1024}", f"{c12}")
chk(w12, "WE12", r"\\&amp;\qquad\doteq@.\end{aligned}\]</div>", rnd(F(c12, 2 ** 20), 3))
chk(w12, "WE12", r"&amp;=\frac{12.5-10}{\sqrt5}\\&amp;=@,\end{aligned}", rnd(zz, 3))
chk(w12, "WE12", r"&amp;=\frac{7.5-10}{\sqrt5}\\&amp;=@,\end{aligned}", rnd(-zz, 3))
chk(w12, "WE12", r"P(-1.118\le Z\le1.118)\\&amp;\doteq@.\end{aligned}", rnd(Phi(1.118) - Phi(-1.118), 3))
present(w12, "WE12", r"calculate <span style=\"white-space:nowrap\">\(P(7.5\le X\le12.5)\).</span>".replace('\\"', '"'))
w13 = CON[3]["worked"][0]
mu13, var13 = F(10000, 3), F(10000) * F(1, 3) * F(2, 3)
sd13 = math.sqrt(float(var13))
present(w13, "WE13", r"\(\mu=3333\tfrac13\) and \(\sigma^2=2222\tfrac29\)")
report(mu13 == 3333 + F(1, 3) and var13 == 2222 + F(2, 9), "WE13 mean and variance", "")
chk(w13, "WE13", r"and \(\sigma\doteq@\).<br>", rnd(sd13, 4))
chk(w13, "WE13", r"same mean \(3333\tfrac13\) and standard deviation @.</p>", rnd(sd13, 4))
za, zb = (3300 - float(mu13)) / sd13, (3400 - float(mu13)) / sd13
ca, cb = (3299.5 - float(mu13)) / sd13, (3400.5 - float(mu13)) / sd13
chk(w13, "WE13", r"The \(z\) scores are \(@\) and \(@\),</p>" + "\n" + r"\[\begin{aligned}\text{so}\quad P(3300", rnd(za, 4), rnd(zb, 4))
chk(w13, "WE13", r"The \(z\) scores are \(@\) and \(@\),</p>" + "\n" + r"\[\begin{aligned}\text{so}\quad P(3299.5", rnd(ca, 4), rnd(cb, 4))
chk(w13, "WE13", r"\le Z\le1.4142)\\&amp;\doteq@.\end{aligned}", rnd(Phi(zb) - Phi(za), 4))
chk(w13, "WE13", r"\le Z\le1.4248)\\&amp;\doteq@.\end{aligned}", rnd(Phi(cb) - Phi(ca), 4))
report(rnd(Phi(1.4248) - Phi(-0.7177), 4) == rnd(Phi(cb) - Phi(ca), 4), "WE13 b from the printed z-scores", "")
w14 = CON[4]["worked"][0]
p14 = Phi(0.7) - Phi(0.5)
report(((52.5 - 50) / 5, (53.5 - 50) / 5) == (0.5, 0.7), "WE14 z-scores 0.5 and 0.7", "")
chk(w14, "WE14", r"P(0.5\le Z\le0.7)\\&amp;\doteq@\\{}", rnd(p14, 6))
chk(w14, "WE14", r"&amp;\doteq2^{100}\times0.066\,574\\&amp;\doteq@\times10^{28}.", rnd(D(2 ** 100) * Decimal("0.066574") / Decimal(10) ** 28, 3))
chk(w14, "WE14", r"compares with \({}^{100}C_{53}\doteq@\times10^{28}\)", rnd(D(math.comb(100, 53)) / Decimal(10) ** 28, 3))
w5 = CON[5]["worked"][0]
rows = re.findall(r"<tr><th>([^<]+)</th>(.*?)</tr>", w5)
cells = {h: re.findall(r"<td>(.*?)</td>", r) for h, r in rows}
ps = [F(1, 2)] * 3 + [F(1, 6)] * 3
ns = [5, 10, 20] * 2
report([clean(c) for c in cells["\\(n\\)"]] == [str(n) for n in ns], "WE5 n row", "")
def tidy(v):
    if v.denominator == 1:
        return str(v.numerator)
    return str(float(v)) if 1000 * v == int(1000 * v) else rnd(v, 2)


report([clean(c) for c in cells["\\(np\\)"]] == [tidy(n * p) for n, p in zip(ns, ps)], "WE5 np row", str([clean(c) for c in cells["\\(np\\)"]]))
report([clean(c) for c in cells["\\(nq\\)"]] == [tidy(n * (1 - p)) for n, p in zip(ns, ps)], "WE5 nq row", str([clean(c) for c in cells["\\(nq\\)"]]))
verdict = ["holds" if n * p > 5 and n * (1 - p) > 5 else "fails" for n, p in zip(ns, ps)]
report([c.replace(" (just)", "") for c in cells["Rule of thumb"]] == verdict and cells["Rule of thumb"][1] == "fails (just)" and ns[1] * ps[1] == 5,
       "WE5 rule of thumb row", str(cells["Rule of thumb"]))
nmin = next(n for n in range(1, 1000) if n * F(1, 6) > 5 and n * F(5, 6) > 5)
report(nmin == 31, "WE5 p = 1/6 needs n > 30", str(nmin))
present(w5, "WE5", r"\(p=\tfrac16\) needs \(n&gt;30\)")

# ================================================================ Lesson examples C1-C5
def coin_demo(q, a_blk, where, n, gt):
    """P(X > gt) for n coins: exact and with the continuity correction."""
    present(q, where, f"A coin is tossed {n} times")
    present(q, where, f"the number of heads is greater than {gt},")
    c = coin_count(n, gt + 1, n)
    report(c == sum(math.comb(n, k) for k in range(gt + 1, n + 1)), f"{where} count", str(c))
    chk(a_blk, where, r"=\dfrac{@}{@}\doteq@\)<br>", f"{c}", f"{2 ** n:,}".replace(",", ""), rnd(F(c, 2 ** n), 3))
    mu, sd = n / 2, math.sqrt(n) / 2
    z = (gt + 0.5 - mu) / sd
    chk(a_blk, where, r"\(P(X\ge@)\doteq P(X\ge@)\).<br>", f"{gt + 1}", f"{gt + 0.5}")
    chk(a_blk, where, r"\doteq P(Z\ge@)=1-\Phi(", z2(z))
    chk(a_blk, where, r"\doteq1-@=@\doteq@\).", tab(z2(z)), rnd(1 - tabz(z), 4), rnd(1 - tabz(z), 3))
    return mu, sd


d1, y1 = BLK["C1"].split("<b>Your turn.</b>")
coin_demo(CON[1]["demo"], d1, "C1 demo", 16, 10)
coin_demo(CON[1]["attempt"], y1, "C1 your turn", 12, 8)
chk(d1, "C1 demo", r"\(\mu=np=@\), \(\sigma^2=npq=@\), \(\sigma=@\).", "8", "4", "2")
chk(y1, "C1 yt", r"\(\mu=np=@\), \(\sigma^2=npq=@\), \(\sigma=\sqrt3\doteq@\).", "6", "3", rnd(math.sqrt(3), 3))

# C2 a: continuity-correction intervals, by rule: event set of integers -> [min - 0.5, max + 0.5]
def cc_interval(n, lo, hi):
    return (lo - 0.5 if lo > 0 else None, hi + 0.5 if hi < n else None)


d2, y2 = BLK["C2"].split("<b>Your turn.</b>")
present(CON[2]["demo"], "C2 demo", r"\(X\sim B(30,0.4)\)")
present(CON[2]["attempt"], "C2 yt", r"\(X\sim B(40,0.25)\)")
for blk, where, items in ((d2, "C2 demo a", [("(i)", 12, 12, r"P(@\le X\le@)"), ("(ii)", 0, 10, r"P(X\le@)"), ("(iii)", 0, 9, r"\doteq P(X\le@)"),
                                             ("(iv)", 15, 30, r"P(X\ge@)"), ("(v)", 16, 30, r"\doteq P(X\ge@)"), ("(vi)", 8, 13, r"\doteq P(@\le X\le@)")]),
                          (y2, "C2 yt a", [("(i)", 10, 10, r"P(@\le X\le@)"), ("(ii)", 0, 7, r"P(X\le@)"), ("(iii)", 0, 11, r"\doteq P(X\le@)"),
                                           ("(iv)", 13, 40, r"P(X\ge@)"), ("(v)", 7, 40, r"\doteq P(X\ge@)"), ("(vi)", 6, 9, r"\doteq P(@\le X\le@)")])):
    n = 30 if "demo" in where else 40
    for lab, lo, hi, tmpl in items:
        seg = blk.split(lab, 1)[1].split("&ensp;")[0].split("<br>")[0]
        lo2, hi2 = cc_interval(n, lo, hi)
        want = tuple(str(v) for v in (lo2, hi2) if v is not None)
        chk(seg, f"{where}{lab}", tmpl + r"\)", *want)
# the event rewrites: P(X<10)=P(X<=9) etc. (strict inequalities move to the next whole number)
present(d2, "C2 demo", r"(iii) \(P(X&lt;10)=P(X\le9)")
present(d2, "C2 demo", r"(v) \(P(X&gt;15)=P(X\ge16)")
present(d2, "C2 demo", r"(vi) \(P(8\le X&lt;14)=P(8\le X\le13)")
present(y2, "C2 yt", r"(iii) \(P(X&lt;12)=P(X\le11)")
present(y2, "C2 yt", r"(v) \(P(X&gt;6)=P(X\ge7)")
present(y2, "C2 yt", r"(vi) \(P(5&lt;X\le9)=P(6\le X\le9)")
for (i, sym) in ((CON[2]["demo"], r"(i) \(P(X=12)\)"), (CON[2]["demo"], r"(vi) \(P(8\le X&lt;14)\)"), (CON[2]["attempt"], r"(vi) \(P(5&lt;X\le9)\)")):
    present(i, "C2 question", sym)


def within_one_sd(blk, q, where, n):
    present(q, where, f"A coin is tossed {n} times")
    mu, sd = n / 2, math.sqrt(n) / 2
    xs = [x for x in range(n + 1) if mu - sd <= x <= mu + sd]
    c = coin_count(n, xs[0], xs[-1])
    chk(blk, where, r"=\dfrac{@}{@}\doteq@\).<br>", f"{c}", f"{2 ** n}", rnd(F(c, 2 ** n), 3))
    z = (xs[-1] + 0.5 - mu) / sd
    return xs, z, c


xs, z, c = within_one_sd(d2, CON[2]["demo"], "C2 demo b", 16)
report(xs == list(range(6, 11)), "C2 demo b values", str(xs))
chk(d2, "C2 demo b", r"\(P(@\le X\le@)\doteq P(-1.25\le Z\le1.25)", "5.5", "10.5")
chk(d2, "C2 demo b", r"\le Z\le1.25)\doteq@-@=@\doteq@\).", tab(z2(z)), tab("-" + z2(z)), rnd(tabz(z) - tabz(-z), 4), rnd(tabz(z) - tabz(-z), 3))
report(z2(z) == "1.25", "C2 demo z", z2(z))
xs, z, c = within_one_sd(y2, CON[2]["attempt"], "C2 yt b", 12)
report(xs == [5, 6, 7], "C2 yt b values", str(xs))
chk(y2, "C2 yt b", r"means \(@\le X\le@\), that is", rnd(6 - math.sqrt(3), 3), rnd(6 + math.sqrt(3), 3))
chk(y2, "C2 yt b", r"\(z=\pm\dfrac{1.5}{\sqrt3}\doteq\pm@\)", z2(z))
chk(y2, "C2 yt b", r"0.87\le Z\le0.87)\doteq@-@=@\doteq@\).", tab(z2(z)), tab("-" + z2(z)), rnd(tabz(z) - tabz(-z), 4), rnd(tabz(z) - tabz(-z), 3))


def large(blk, q, where, n, p, a, b):
    present(q, where, f"has \\(n={n:,}\\)".replace(",", "\\,") if n > 9999 else f"has \\(n={n}\\)")
    present(q, where, f"find \\(P({a}\\le X\\le{b})\\)")
    mu, var = n * p, n * p * (1 - p)
    sd = math.sqrt(var)
    chk(blk, where, r"\(\mu=np=@\), \(\sigma^2=npq=@\), \(\sigma=@\).", f"{mu:g}", f"{var:g}", f"{sd:g}")
    za, zb = (a - mu) / sd, (b - mu) / sd
    pa = tabz(zb) - tabz(za)
    zA, zB = (a - 0.5 - mu) / sd, (b + 0.5 - mu) / sd
    pb = tabz(zB) - tabz(zA)
    return za, zb, pa, zA, zB, pb, float(binom_sum(n, p, a, b))


d3, y3 = BLK["C3"].split("<b>Your turn.</b>")
za, zb, pa, zA, zB, pb, ex = large(d3, CON[3]["demo"], "C3 demo", 10000, F(1, 5), 1950, 2060)
chk(d3, "C3 demo a", r"The \(z\)-scores are \(@\) and \(@\), so", rnd(za, 2), rnd(zb, 1))
chk(d3, "C3 demo a", r"\Phi(1.5)-\Phi(-1.25)\doteq@-@=@\).", tab(z2(zb)), tab(z2(za)), str(pa))
chk(d3, "C3 demo b", r"\(P(@\le X\le@)\): the", "1949.5", "2060.5")
chk(d3, "C3 demo b", r"are \(@\doteq@\) and \(@\doteq@\), so", rnd(zA, 4), z2(zA), rnd(zB, 4), z2(zB))
chk(d3, "C3 demo b", r"probability is \(\doteq@-@=@\).", tab(z2(zB)), tab(z2(zA)), str(pb))
chk(d3, "C3 demo", r"differ by only @, so", rnd(abs(pb - pa), 3))
report(abs(ex - float(pb)) < 0.002, "C3 demo exact binomial close", f"exact {ex:.4f}")
za, zb, pa, zA, zB, pb, ex = large(y3, CON[3]["attempt"], "C3 yt", 4800, F(1, 4), 1150, 1260)
chk(y3, "C3 yt a", r"The \(z\)-scores are \(@\) and \(@\), so", z2(za), z2(zb))
chk(y3, "C3 yt a", r"\Phi(2.00)-\Phi(-1.67)\doteq@-@=@\).", tab(z2(zb)), tab(z2(za)), str(pa))
chk(y3, "C3 yt b", r"\(P(@\le X\le@)\): the", "1149.5", "1260.5")
chk(y3, "C3 yt b", r"are \(@\doteq@\) and \(@\doteq@\), so", rnd(zA, 4), z2(zA), rnd(zB, 4), z2(zB))
chk(y3, "C3 yt b", r"probability is \(\doteq@-@=@\).", tab(z2(zB)), tab(z2(zA)), str(pb))
chk(y3, "C3 yt", r"differ by only @, so", rnd(abs(pb - pa), 3).rstrip("0"))
report(abs(ex - float(pb)) < 0.002, "C3 yt exact binomial close", f"exact {ex:.4f}")

d4, y4 = BLK["C4"].split("<b>Your turn.</b>")
for blk, q, where, n, x, err in ((d4, CON[4]["demo"], "C4 demo", 36, 20, "1"), (y4, CON[4]["attempt"], "C4 yt", 100, 55, "0.2")):
    present(q, where, f"Approximate \\({{}}^{{{n}}}C_{{{x}}}\\) using")
    mu, sd = n / 2, math.sqrt(n) / 2
    z1, z_2 = (x - 0.5 - mu) / sd, (x + 0.5 - mu) / sd
    pr = tabz(z_2) - tabz(z1)
    est = D(2 ** n) * pr
    e = est.adjusted()
    chk(blk, where, r"\doteq@\times10^{@}\).<br>" + "\nThe calculator", rnd(est / Decimal(10) ** e, 3), str(e))
    exact_c = math.comb(n, x)
    report(exact_c == coin_count(n, x, x) if n <= 16 else exact_c == math.factorial(n) // (math.factorial(x) * math.factorial(n - x)), f"{where} exact coefficient", str(exact_c))
    chk(blk, where, r"\doteq@\times10^{@}\), so the error", rnd(D(exact_c) / Decimal(10) ** e, 3), str(e))
    rel = abs(D(exact_c) - est) / D(exact_c) * 100
    chk(blk, where, r"the error is about @%", err)
    report(abs(rel - Decimal(err)) < Decimal("0.15"), f"{where} relative error", f"{rel:.3f}%")
    chk(blk, where, r"\doteq@-@=@\), and", tab(z2(z_2)), tab(z2(z1)), str(pr))
chk(d4, "C4 demo", r"The \(z\)-scores are 0.5 and \(@\doteq@\), so", rnd((20.5 - 18) / 3, 4), z2((20.5 - 18) / 3))
chk(d4, "C4 demo", r"\({}^{36}C_{20}=@\doteq", f"{math.comb(36, 20):,}".replace(",", ""))
chk(d4, "C4 demo", r"\(\mu=18\) and \(\sigma=\sqrt{36\times\tfrac12\times\tfrac12}=@\).", "3")

d5, y5 = BLK["C5"].split("<b>Your turn.</b>")
for blk, where, cases in ((d5, "C5 demo", [(40, F(1, 10), "not reasonable"), (60, F(1, 4), "reasonable"), (200, F(98, 100), "not reasonable")]),
                          (y5, "C5 yt", [(25, F(3, 10), "reasonable"), (100, F(3, 100), "not reasonable"), (30, F(9, 10), "not reasonable")])):
    bpart = blk.split("<b>b</b>")[1].split("<b>c</b>")[0]
    segs = re.split(r"\((?:i|ii|iii)\) ", bpart)[1:]
    for (n, p, verdict), seg in zip(cases, segs):
        ok = (n * p > 5 and n * (1 - p) > 5)
        seg = seg.replace("<br>", "").strip()
        report(ok == (verdict == "reasonable") and seg.endswith(f"is {verdict}."), f"{where} b B({n},{p})", seg[:70])
        nums = re.findall(r"\\\((?:np|nq)=([\d.]+)\\\)", seg)
        want = [str(n * p) if (n * p).denominator == 1 else str(float(n * p))]
        if n * p > 5:
            want.append(str(n * (1 - p)) if (n * (1 - p)).denominator == 1 else str(float(n * (1 - p))))
        report(nums[:len(want)] == want, f"{where} b np/nq B({n},{p})", f"{nums} want {want}")
nmin = next(n for n in range(1, 10000) if n * F(4, 100) > 5 and n * F(96, 100) > 5)
report(nmin == 126, "C5 demo c by search", str(nmin))
present(d5, "C5 demo c", r"gives \(n&gt;125\)")
nmin = next(n for n in range(1, 10000) if n * F(95, 100) > 5 and n * F(5, 100) > 5)
report(nmin == 101, "C5 yt c by search", str(nmin))
present(y5, "C5 yt c", r"gives \(n&gt;100\)")
present(CON[5]["demo"], "C5 demo", r"\(B(40,0.1)\)")
present(CON[5]["attempt"], "C5 yt", r"\(B(100,0.03)\)")

# ================================================================ Textbook homework answers
# Q1, Q2: exact binomial %, table approximation with CC, percentage error from the printed values
q1 = BLK["1"]
ex1 = binom_sum(20, F(3, 10), 9, 11)
report(ex1 == sum(conv_dist(20, F(3, 10))[9:12]), "Q1 exact by convolution", "")
chk(q1, "Q1b", r"(0.7)^{9}\doteq@\%\)", rnd(pct(ex1), 2))
chk(q1, "Q1c", r"\(np=@&gt;5\) and \(nq=@&gt;5\).", "6", "14")
sd1 = math.sqrt(4.2)
chk(q1, "Q1d", r"\(\sigma^2=4.2\), \(\sigma\doteq@\).", rnd(sd1, 3))
z1, z_2 = (8.5 - 6) / sd1, (11.5 - 6) / sd1
chk(q1, "Q1d", r"\dfrac{8.5-6}{\sqrt{4.2}}\doteq@\) and \(\dfrac{11.5-6}{\sqrt{4.2}}\doteq@\)", z2(z1), z2(z_2))
ap1 = tabz(z_2) - tabz(z1)
chk(q1, "Q1d", r"\doteq@-@=@=@\%\).", tab(z2(z_2)), tab(z2(z1)), str(ap1), rnd(ap1 * 100, 2))
e_, a_ = Decimal(rnd(pct(ex1), 2)), Decimal(rnd(ap1 * 100, 2))
chk(q1, "Q1e", r"\(\dfrac{10.82-10.75}{10.82}\doteq@\%\)", rnd(abs(e_ - a_) / e_ * 100, 2))
present(TQ["1"], "Q1", r"each with probability of success \(p=0.3\)")
present(TQ["1"], "Q1", r"\(P(8.5\le X\le11.5)\)")

q2 = BLK["2"]
Q2 = {"a": (50, F(1, 2), 18, 20), "b": (20, F(2, 5), 8, 9), "c": (30, F(3, 10), 5, 7), "d": (40, F(1, 5), 9, 12),
      "e": (22, F(3, 5), 13, 15), "f": (80, F(1, 10), 10, 13), "g": (500, F(1, 4), 100, 103), "h": (200, F(9, 10), 170, 172)}
for lab, (n, p, a, b) in Q2.items():
    present(TQ["2"], f"Q2{lab}", f"\\(n={n}\\), \\(p={float(p):g}\\), find \\(P({a}\\le X\\le{b})\\)")
    line = q2.split(f"<b>{lab}</b>")[1].split("<br>")[0].split("</div>")[0]
    ex = binom_sum(n, p, a, b)
    if n <= 50:
        report(ex == sum(conv_dist(n, p)[a:b + 1]), f"Q2{lab} exact by convolution", "")
    mu, var = n * p, n * p * (1 - p)
    sd = math.sqrt(var)
    za_, zb_ = (a - 0.5 - float(mu)) / sd, (b + 0.5 - float(mu)) / sd
    ap = tabz(zb_) - tabz(za_)
    ep, apc = Decimal(rnd(pct(ex), 2)), Decimal(rnd(ap * 100, 2))
    err = rnd(abs(ep - apc) / ep * 100, 1)

    def g(v):
        return f"{float(v):g}"
    chk(line, f"Q2{lab}", r"\(B(@,@)\), \(P(@\le X\le@)\doteq@\%\); \(np=@\), \(nq=@\); normal approximation using \(N(@,@)\): \(z=@\) and \(@\), \(@-@=@\%\), percentage error @%",
        str(n), g(p), str(a), str(b), str(ep), g(mu), g(n - mu), g(mu), g(var), z2(za_), z2(zb_), tab(z2(zb_)), tab(z2(za_)), str(apc), err)
q3 = BLK["3"]
chk(q3, "Q3d", r"\(p=@\), \(\mu=np=@\), \(\sigma^2=np(1-p)=@\), so \(\sigma\doteq@\).", "0.6", "12", "4.8", rnd(math.sqrt(4.8), 2))
present(TQ["3"], "Q3", "600 pink and 400 blue counters")
chk(q3, "Q3e", r"(0.4)^6\doteq@\)", rnd(binom_sum(20, F(3, 5), 14, 14), 3))
zA, zB = (13.5 - 12) / math.sqrt(4.8), (14.5 - 12) / math.sqrt(4.8)
chk(q3, "Q3f", r"\doteq P(@&lt;Z&lt;@)\doteq@-@=@\doteq@\).", z2(zA), z2(zB), tab(z2(zB)), tab(z2(zA)), str(tabz(zB) - tabz(zA)), rnd(tabz(zB) - tabz(zA), 3))
report(sf(tabz(zB) - tabz(zA), 2) == sf(binom_sum(20, F(3, 5), 14, 14), 2) == "0.12", "Q3f both 0.12 to 2 s.f.", "")
q5 = BLK["5"]
for lab, pv in zip("abcdefgh", ("0.5", "0.25", "0.125", "0.01", "0.75", "0.875", "0.9", "0.55")):
    p = F(pv)
    present(TQ["5"], f"Q5{lab}", f"<span class=\"pl\">{lab}</span>\\(p={pv}\\)")
    nmin = next(n for n in range(1, 100000) if n * p > 5 and n * (1 - p) > 5)
    bound = 5 / min(p, 1 - p)
    seg = q5.split(f"<b>{lab}</b>")[1].split("&emsp;")[0]
    if bound.denominator == 1:
        report(clean(seg) == f"n&gt;{bound}" and nmin == bound + 1, f"Q5{lab}", f"{clean(seg)}; smallest n {nmin}")
    else:
        report(clean(seg).startswith(f"n&gt;{rnd(bound, 1)}") and f"n\\ge{nmin}" in clean(seg), f"Q5{lab}", f"{clean(seg)}; smallest n {nmin}")
q6 = BLK["6"]
mu6, sd6 = 854 * 0.08, math.sqrt(854 * 0.08 * 0.92)
chk(q6, "Q6c", r"\(\mu=854\times0.08=@\), \(\sigma=\sqrt{854\times0.08\times0.92}\doteq@\).", rnd(mu6, 2), rnd(sd6, 2))
chk(q6, "Q6c", r"Here 7% of 854 is @ and 9% is @, so we need @ to @ people.", rnd(0.07 * 854, 2), rnd(0.09 * 854, 2), "60", "76")
report(math.ceil(0.07 * 854) == 60 and math.floor(0.09 * 854) == 76, "Q6 60 to 76", "")
zA, zB = (60 - mu6) / sd6, (76 - mu6) / sd6
chk(q6, "Q6c", r"\(P(60&lt;X&lt;76)\doteq P(@&lt;Z&lt;@)\doteq@-@=@\doteq@\%\)", z2(zA), z2(zB), tab(z2(zB)), tab(z2(zA)), str(tabz(zB) - tabz(zA)), rnd((tabz(zB) - tabz(zA)) * 100, 1))
zC = (76.5 - mu6) / sd6
chk(q6, "Q6d", r"\(P(76&lt;X&lt;76.5)\doteq P(@&lt;Z&lt;@)\doteq@-@=@\doteq@\%\)", z2(zB), z2(zC), tab(z2(zC)), tab(z2(zB)), str(tabz(zC) - tabz(zB)), rnd((tabz(zC) - tabz(zB)) * 100, 1))
present(TQ["6"], "Q6", "A representative random sample includes 854 people")
q7 = BLK["7"]
chk(q7, "Q7a", r"\(\big(\tfrac34\big)^{15}\doteq@\doteq@\%\)", rnd(F(3, 4) ** 15, 4), rnd(F(3, 4) ** 15 * 100, 0))
chk(q7, "Q7b", r"\(1-\big(\tfrac34\big)^{15}\doteq@\%\)", rnd((1 - F(3, 4) ** 15) * 100, 0))
report(F(20, 100) * 15 == 3, "Q7c 20% of 15 is 3", "")
sd7 = math.sqrt(15 * 0.25 * 0.75)
chk(q7, "Q7c", r"\(\mu=@\), \(\sigma^2=@\), \(\sigma\doteq@\).", "3.75", "2.8125", rnd(sd7, 3))
z7 = (2.5 - 3.75) / sd7
chk(q7, "Q7c", r"\doteq P(Z\ge@)\doteq@\doteq@\%\)", z2(z7), str(1 - tabz(z7)), rnd((1 - tabz(z7)) * 100, 0))
q8 = BLK["8"]
sd8 = math.sqrt(20 * 0.45 * 0.55)
z8 = (10.5 - 9) / sd8
chk(q8, "Q8", r"\(\mu=@\), \(\sigma\doteq@\), and \(P(X\ge10.5)\doteq P(Z\ge@)\doteq1-@=@\), so a normal approximation gives @%", "9", rnd(sd8, 3), z2(z8), str(tabz(z8)), str(1 - tabz(z8)), rnd((1 - tabz(z8)) * 100, 0))
report(math.floor(20 / 2) + 1 == 11, "Q8 more than half of 20 is at least 11", "")
q9 = BLK["9"]
sd9 = math.sqrt(30 * 0.6 * 0.4)
z9 = (20.5 - 18) / sd9
chk(q9, "Q9", r"\(\mu=@\), \(\sigma\doteq@\).", "18", rnd(sd9, 3))
chk(q9, "Q9", r"\doteq P(Z\ge@)\doteq1-@=@\doteq@\%\).", z2(z9), str(tabz(z9)), str(1 - tabz(z9)), rnd((1 - tabz(z9)) * 100, 1))
q12 = BLK["12"]
chk(q12, "Q12a(i)", r"\(1-0.95^{10}\doteq@\)", rnd(1 - F(95, 100) ** 10, 2))
tabs = re.findall(r'<tr><th>\\\(P\(\\text\{reject\}\)\\\)</th>(.*?)</tr>', q12)
pv = [F(0), F(5, 100), F(1, 10), F(2, 10), F(3, 10), F(4, 10)]
wa = [rnd(1 - binom_sum(10, p, 0, 0), 2) if p else "0" for p in pv]
wb = [rnd(1 - binom_sum(15, p, 0, 1), 2) if p else "0" for p in pv]
got = [re.findall(r"<td>([^<]*)</td>", t) for t in tabs]
report(len(got) == 2 and got[0] == wa and got[1] == wb, "Q12 tables", f"{got} want {wa} / {wb}")
# the OC SVGs: dot heights must match the probabilities
for name, curves in (("a17c_q12a", [wa]), ("a17c_q12b", [wa, wb])):
    svg = read(os.path.join("svg", name + ".svg"))
    cy = [float(v) for v in re.findall(r'<circle cx="[\d.]+" cy="([\d.]+)"', svg)]
    h, t, b = 150, 18, 26
    vals = [(t + (1.1 - y) / 1.1 * (h - t - b)) for c in curves for y in [float(1 - (1 - p) ** 10) if c is wa else float(1 - binom_sum(15, p, 0, 1)) for p in pv]]
    report(len(cy) == len(vals) and all(abs(a - b) < 0.11 for a, b in zip(cy, vals)), f"{name} dot heights", f"{len(cy)} dots")

# ================================================================ Past papers
intro = re.search(r'<div class="pp-intro"><span><b>Suggested time: (\d+) minutes</b></span><span><b>(\d+) marks</b></span>', pps[1])
marks = {k: int(re.search(r'<span class="mk">(\d+) marks?</span>', v).group(1)) for k, v in PPQ.items()}
total = sum(marks.values())
report(intro is not None and int(intro.group(2)) == total and 15 <= total <= 22, "PP total marks", f"{total}")
report(intro is not None and int(intro.group(1)) == 5 * round(1.5 * total / 5), "PP time", f"{intro.group(1) if intro else None} min for {total} marks")
report(sorted(PPQ) == list(range(1, 8)) and sorted(PPA) == list(range(1, 8)), "PP numbering", str(sorted(PPQ)))
report([marks[k] for k in sorted(marks)] == [1, 2, 3, 3, 2, 3, 4], "PP marks as printed", str(marks))
for k in PPQ:
    lq = re.sub(r"<span class=\"mk\">.*", "", PPQ[k].split("</div>")[0])
    la = PPA[k].split("</div>")[0]
    report(lq.strip() == la.strip().replace("</span></span>", "</span></span>"), f"PP{k} label identical", re.sub(r"<[^>]+>", "", la)[:90])
    report(PPQ[k].count('<div class="hint"><b>Hint:</b>') == 1, f"PP{k} one hint", "")
    sub = [int(m) for m in re.findall(r'<div class="pp-sub"><span>.*?</span><span class="mk">(\d+)</span></div>', PPQ[k], re.S)]
    report(not sub or sum(sub) == marks[k], f"PP{k} part marks", str(sub))
    report(PPA[k].count("Using the normal approximation without a continuity correction, as in the school solution") == 1, f"PP{k} method line", "")
report("use the standard normal table at the end of the Revision section" in pps[1].split("</div>")[0] + pps[1][:600], "PP intro table line", "")
R = "[the standard normal table at the end of the Revision section]"
for k, keep in ((3, "the probability that less than 5% are left-handed? [You may refer to " + R + ".]"),
                (4, "A normal distribution table is included [at the end of the Revision section]."),
                (5, "<i>You may use the information [in the standard normal table at the end of the Revision section] to answer this question.</i>"),
                (6, "(A Standard Normal Distribution table is [at the end of the Revision section].")):
    present(PPQ[k], f"PP{k} table sentence kept, location replaced", keep)
for k, bad in ((3, "page 11"), (4, "overleaf"), (5, "page 17"), (6, "attached with this paper")):
    report(bad not in PPQ[k], f"PP{k} page/location reference replaced", bad)
for k, keep in ((1, "(iii) Use a normal approximation to find the probability that \\(X\\) is less than 8040."),
                (2, "You must justify the use of the normal approximation."),
                (7, "Use normal approximation to solve for \\(n\\), to the nearest integer.")):
    present(PPQ[k], f"PP{k} method sentence verbatim", keep)


# PP1 Kings: mu 8000, sd 40 supplied
present(PPQ[1], "PP1", r"it was found that \(E(X)=8000\) and that \(X\) has a standard deviation of 40.")
report(10000 * F(8, 10) == 8000 and math.isqrt(int(10000 * F(8, 10) * F(2, 10))) == 40, "PP1 supplied values", "")
chk(PPA[1], "PP1", r"=P(Z&lt;@)\doteq@\doteq@.\]", "1", tab("1.00"), rnd(Decimal(tab("1.00")), 2))
# PP2
sd2 = math.sqrt(150 * 0.2 * 0.8)
chk(PPA[2], "PP2", r"with \(np=@\) and \(nq=@\).", "30", "120")
chk(PPA[2], "PP2", r"=\sqrt{24}\doteq@\]", rnd(sd2, 3))
z = (37 - 30) / sd2
chk(PPA[2], "PP2", r"\doteq P(Z\le@)\doteq@.\]", z2(z), tab(z2(z)))
report(z2((113 - 120) / sd2) == "-1.43", "PP2 school's cured version same z", "")
# PP3
chk(PPA[3], "PP3", r"\mu=np=@,\qquad\sigma^2=npq=@,\qquad\sigma=@.", "10", "9", "3")
z = (5 - 10) / 3
chk(PPA[3], "PP3", r"&amp;=P(Z&lt;@)\\&amp;=1-\Phi(@)\\&amp;\doteq1-@\\&amp;=@.\end{aligned}", z2(z), z2(-z), tab(z2(-z)), str(1 - Decimal(tab(z2(-z)))))
report(F(5, 100) * 100 == 5, "PP3 5% of 100", "")
# PP4
mu4, var4 = 288 * F(27, 100), 288 * F(27, 100) * F(73, 100)
chk(PPA[4], "PP4", r"with \(np=@\) and \(nq=@\), both", str(float(mu4)), str(float(288 - mu4)))
chk(PPA[4], "PP4", r"\mu=np=@,\qquad\sigma^2=npq=@,\qquad\sigma\doteq@\]", str(float(mu4)), str(float(var4)), rnd(math.sqrt(var4), 3))
z = (100 - float(mu4)) / math.sqrt(var4)
chk(PPA[4], "PP4", r"\doteq P(Z&lt;@)\doteq@\doteq@.\]", z2(z), tab(z2(z)), rnd(Decimal(tab(z2(z))), 3))
# PP5
p5 = F(1615580, 2000000)
chk(PPA[5], "PP5", r"=@\). In 10&nbsp;000 trials", str(float(p5)))
mu5 = 10000 * p5
sd5 = math.sqrt(10000 * p5 * (1 - p5))
chk(PPA[5], "PP5", r"\mu=np=@,\qquad\sigma=", str(float(mu5)))
chk(PPA[5], "PP5", r"\times0.19221}\doteq@.\]", rnd(sd5, 2))
z = (8100 - float(mu5)) / sd5
chk(PPA[5], "PP5", r"&amp;\doteq P(Z&gt;@)\\&amp;=1-@\\&amp;=@\doteq@\%.", z2(z), tab(z2(z)), str(1 - Decimal(tab(z2(z)))), rnd((1 - Decimal(tab(z2(z)))) * 100, 1))
# PP6: solve (20 - 0.05n)/sqrt(0.0475 n) = z, z from the table in reverse (closest entry to 0.90658)
target = Decimal("0.90658")
zr = min(TAB, key=lambda k: abs(Decimal(TAB[k]) - target))
report(zr == "1.32", "PP6 reverse look-up", zr)
chk(PPA[6], "PP6", r"\(\Phi(1.32)\doteq@\), so", TAB["1.32"])


def bisect(f, lo, hi):
    for _ in range(200):
        mid = (lo + hi) / 2
        if (f(lo) > 0) == (f(mid) > 0):
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


n6 = bisect(lambda n: (20 - 0.05 * n) / math.sqrt(0.0475 * n) - 1.32, 10, 400)
present(PPA[6], "PP6", r"0.05n+1.32\sqrt{0.0475}\,\sqrt n-20=0.\]")
chk(PPA[6], "PP6", r"\(0.05u^2+@u-20=0\)", rnd(1.32 * math.sqrt(0.0475), 5))
chk(PPA[6], "PP6", r"\doteq@,\qquad n=u^2\doteq@,\qquad\text{so}\qquad n=@.\]", rnd(math.sqrt(n6), 3), rnd(n6, 1), str(round(n6)))
n6c = bisect(lambda n: (20.5 - 0.05 * n) / math.sqrt(0.0475 * n) - 1.32, 10, 400)
chk(PPA[6], "PP6", r"leads to \(n\doteq@\).)", str(round(n6c)))
chk(PPA[6], "PP6", r"(Check: \(np=@\) and \(nq=@\),", f"{300 * 0.05:g}", f"{300 * 0.95:g}")
zc = (20 - 15) / math.sqrt(300 * 0.05 * 0.95)
report(z2(zc) == "1.32", "PP6 n = 300 gives z = 1.32 back", z2(zc))
# PP7
zr = min(TAB, key=lambda k: abs(1 - Decimal(TAB[k]) - Decimal("0.3446")))
report(zr == "0.40" and rnd(1 - Decimal(TAB["0.40"]), 4) == "0.3446", "PP7 reverse look-up", zr)
chk(PPA[7], "PP7", r"\(\Phi(0.40)\doteq@\), so \(\Phi(-0.40)\doteq@\).", TAB["0.40"], rnd(1 - Decimal(TAB["0.40"]), 4))
n7 = bisect(lambda n: (9 - 0.1 * n) / (0.3 * math.sqrt(n)) + 0.4, 85, 400)
chk(PPA[7], "PP7", r"\doteq@,\qquad n=u^2\doteq@,\qquad\text{so}\qquad n=@.\]", rnd(math.sqrt(n7), 3), rnd(n7, 2), str(round(n7)))
disc = 1.8144 ** 2 - 4 * 0.01 * 81
r1, r2 = (1.8144 + math.sqrt(disc)) / 0.02, (1.8144 - math.sqrt(disc)) / 0.02
chk(PPA[7], "PP7", r"with roots \(n\doteq@\) and \(n\doteq@\).", rnd(r1, 2), rnd(r2, 2))
report(abs((0.1 * r2 - 9) ** 2 - 0.0144 * r2) < 1e-9 and (9 - 0.1 * r2) > 0, "PP7 79.31 root has 9 above the mean", "")
report(round(n7) == 102 and abs((9 - 0.1 * 102) / (0.3 * math.sqrt(102)) + 0.4) < 0.005, "PP7 n = 102 gives z = -0.40 back", "")
present(PPQ[7], "PP7", "is 0.3446, to 4 decimal places.")

print(f"\n{NCHECK[0]} checks, {len(FAILS)} failed")
if FAILS:
    print("FAILED:", *FAILS, sep="\n  ")
    sys.exit(1)
print("ALL OK")
