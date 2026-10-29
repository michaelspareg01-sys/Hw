"""Check of Lesson 13C (Y11 Ch 13 pack): Variance and standard deviation.

The script reads the values PRINTED in workspace/build/y11ch13/a_13c.html (lesson examples, textbook
homework answers, past-paper solutions) and in l13c.html (the concept boxes, worked examples, and the
data given inside the tutor demos, your-turn items, textbook questions and past-paper stems).  Every
distribution table is parsed cell by cell (rows x / p(x) / xp(x) / (x-mu)^2 / (x-mu)^2 p(x) / x^2 /
x^2 p(x) with a Sum column, or the transposed column layout; the side notes '(a check)' etc. are
skipped); every inline value is found with a template ('@' marks the printed value), and a template
must match exactly once in its block, otherwise the item FAILS.  Printed LaTeX (\\tfrac, mixed numbers
such as 3\\tfrac12, decimals, 24\\,500) is turned into an exact rational.

Each printed result is compared with an independent computation using fractions.Fraction:
  - distributions are ENUMERATED from the printed statements (coins, dice and their face lists,
    friends and their cash, the spinner), or read from the printed question tables, never copied
    from the answers; Worked example 7 takes its data from the statement of Worked example 3 in
    l13b.html (read only);
  - E(X), E(X^2) and Var(X) are recomputed as exact sums, by both formulas (they must agree);
    every cell of every table is checked; sigma is checked to the printed number of decimals;
  - the uniform-distribution formulas (Q12) are checked with sympy summation; the Q13/Q14 results
    E(kX + a) = kE(X) + a and sd(kX + a) = k sigma are checked on every distribution of the lesson;
  - past papers: the Bernoulli variance, the binomial table of BHHS 2020 (a and b recomputed from
    p, which is found from P(X = 4)), and the equation E(X) = 5Var(X) solved with sympy;
  - the four-coin figure is checked by re-running figs.build_13b() with the plotting call recorded.
No simulation is used.  It also checks the structure (concepts, boxes 7 and 8, the extension box,
demos, your-turns, worked examples 5-7, answer blocks, bands, past-paper labels, marks and time).

Exit status 1 if anything fails.  Run: python3 workspace/checks/y11ch13_13c.py
"""
import math
import os
import re
import sys
from fractions import Fraction as F
from itertools import product

import sympy as sp
from sympy.parsing.sympy_parser import (implicit_multiplication, parse_expr, rationalize,
                                        standard_transformations)

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.environ.get("Y11CH13_SRC", os.path.join(HERE, "..", "build", "y11ch13"))   # override only for mutation tests
FAILS = []
NCHECK = [0]
NS = sp.Symbol("n", positive=True, integer=True)
TR = standard_transformations + (implicit_multiplication, rationalize)
MONEY = '<span style="white-space:nowrap">\\(\\$\\)'


def read(name):
    with open(os.path.join(SRC, name), encoding="utf-8") as f:
        return f.read()


def report(ok, label, detail=""):
    NCHECK[0] += 1
    print(("OK       " if ok else "MISMATCH ") + label + ("  " + detail if detail else ""))
    if not ok:
        FAILS.append(label)


# ---------------------------------------------------------------- printed LaTeX -> exact value
def _arg(t, i):
    if t[i] == "{":
        depth, j = 0, i
        while True:
            depth += {"{": 1, "}": -1}.get(t[j], 0)
            if depth == 0:
                return t[i + 1:j], j + 1
            j += 1
    return t[i], i + 1


def _conv(t):
    out, i = [], 0
    while i < len(t):
        if t.startswith(("\\tfrac", "\\dfrac", "\\frac"), i):
            i = t.index("frac", i) + 4
            u, i = _arg(t, i)
            v, i = _arg(t, i)
            whole = ""
            while out and re.fullmatch(r"\d", out[-1]):
                whole = out.pop() + whole       # mixed number such as 3\tfrac12, kept together: (3+1/2)
            frac = f"(({_conv(u)})/({_conv(v)}))"
            out.append(f"({whole}+{frac})" if whole else frac)
        elif t.startswith("\\times", i):
            out.append("*")
            i += 6
        elif t.startswith("\\big(", i) or t.startswith("\\big)", i):
            out.append(t[i + 4])
            i += 5
        elif t[i] == "^":
            u, i = _arg(t, i + 1)
            out.append(f"**({_conv(u)})")
        elif t[i] == "\\":
            raise ValueError(f"unknown macro in {t!r}")
        elif t[i] in "{}":
            out.append("(" if t[i] == "{" else ")")
            i += 1
        else:
            out.append(t[i])
            i += 1
    return "".join(out)


def strip(cell):
    c = re.sub(r"<[^>]+>", "", cell)
    c = c.replace("\\(", "").replace("\\)", "").replace("&nbsp;", " ").replace("\\$", "")
    return re.sub(r"\\,|\\;|\\!|\\ ", "", c).strip()


def sym(t, loc=None):
    t = strip(t)
    return parse_expr(_conv(t.replace(" ", "")), local_dict=loc or {}, transformations=TR)


def val(t):
    e = sp.nsimplify(sym(t))
    if not e.is_Rational:
        raise ValueError(f"not a number: {t!r}")
    return F(int(e.p), int(e.q))


# ---------------------------------------------------------------- HTML blocks
ans = read("a_13c.html")
les = read("l13c.html")
l13b = read("l13b.html")
report(ans.count("{{ahead:Lesson 13C | Variance and standard deviation}}") == 2, "answers: two 'ahead' headings", "")
secs = re.findall(r'<div class="ans-sec">([^<]+)</div>', ans)
report(secs == ["Lesson Examples", "Textbook Homework", "Past-Paper Homework - Worked Solutions"], "answer sections in order", str(secs))
BLK = {}
for mt in re.finditer(r'<div class="a"(?: style="[^"]*")?><span class="an">([^<]+)</span><div class="ab">(.*?)(?=<div class="a"(?: style="[^"]*")?><span class="an">|<div class="ans-sec">|\{\{ahead|$)', ans, re.S):
    if mt.group(1) in BLK:
        report(False, f"block {mt.group(1)}", "duplicate answer number")
    BLK[mt.group(1)] = mt.group(2)
parts = les.split("<!-- ============ Homework ============ -->")
teach = parts[0]
hw, ppl = parts[1].split("<!-- ============ Past papers ============ -->")
TQ = {k: v for k, v in re.findall(r'<div class="q"><span class="q-num">(\d+)</span>(.*?)(?=<div class="q">|\{\{band|$)', hw, re.S)}
EX = re.findall(r'<div class="ex (demo|attempt|worked)"><div class="ex-top"><span class="tag">([^<]*)</span>(.*?)(?=<div class="ex |<!-- =====|$)', teach, re.S)
DEMO = [b for k, _, b in EX if k == "demo"]
YT = [b for k, _, b in EX if k == "attempt"]
WORK = {t: b for k, t, b in EX if k == "worked"}
report(len(DEMO) == 3 and len(YT) == 3 and sorted(WORK) == ["Worked example 5", "Worked example 6", "Worked example 7"],
       "lesson structure", f"{len(DEMO)} demos, {len(YT)} your turns, worked {sorted(WORK)}")
report(re.findall(r"\{\{sec:teal:key:Concept (\d)", teach) == ["1", "2", "3"], "three concepts", "")
report('<div class="box take"><div class="bt">7 Variance of a discrete probability distribution</div>' in teach
       and '<div class="box take"><div class="bt">8 Standard deviation of a discrete probability distribution</div>' in teach
       and '<div class="bt">Extension: proof of the alternative formula</div>' in teach, "Boxes 7, 8 and the extension box present", "")
for box in ("Measures of spread", "The variance: first formula", "Deviations from the mean", "Setting out the calculation of variance",
            "Using columns instead of rows", "The variance as an expected value", "The variance: alternative formula",
            "The four coins again, using the alternative formula", "Standard deviation"):
    report(f'<div class="bt">{box}</div>' in teach, f"concept box '{box}'", "")


def src(key):
    if key not in BLK:
        raise LookupError(f"answer block {key} missing")
    return BLK[key]


def grab(block, template, where):
    pieces = template.split("@")
    cap = r"((?:(?!\\\)|\\\]|\\\\|</td>|<br>|</span>|,\\qquad).)+?)"
    rx = "".join(re.escape(pc) + (cap if i < len(pieces) - 1 else "") for i, pc in enumerate(pieces))
    found = re.findall(rx, block, re.S)
    if len(found) != 1:
        raise LookupError(f"template matched {len(found)} times in {where}: {template!r}")
    return found[0] if isinstance(found[0], tuple) else (found[0],)


def chain(block, template, expected, where, min_sides=2):
    """Template captures 'a=b=c...'; every side must equal expected."""
    label = f"{where}: {template}"
    try:
        (g,) = grab(block, template, where)
        sides = [t for t in g.split("=") if t.strip()]
        vals = [val(t) for t in sides]
        report(len(sides) >= min_sides and all(v == expected for v in vals), label, f"printed {g}, expected {expected}")
    except Exception as err:
        report(False, label, f"ERROR {err}")


def value(block, template, expected, where):
    label = f"{where}: {template}"
    try:
        got = grab(block, template, where)
        exp = expected if isinstance(expected, tuple) else (expected,)
        ok = len(got) == len(exp) and all(val(g) == e for g, e in zip(got, exp))
        report(ok, label, f"printed {got}, expected {tuple(str(e) for e in exp)}")
    except Exception as err:
        report(False, label, f"ERROR {err}")


def rounded(block, template, exact, where):
    """Printed decimal approximation (after \\doteqdot) must be exact rounded to the printed decimals."""
    label = f"{where}: {template}"
    try:
        (g,) = grab(block, template, where)
        g = strip(g)
        dp = len(g.split(".")[1]) if "." in g else 0
        report(abs(float(g) - exact) <= 0.5 * 10 ** -dp + 1e-12 and round(exact, dp) == float(g), label, f"printed {g}, exact {exact:.6f}")
    except Exception as err:
        report(False, label, f"ERROR {err}")


def tables(block):
    out = []
    for t in re.findall(r'<table class="t"[^>]*>(.*?)</table>', block, re.S):
        rows = []
        for r in re.findall(r"<tr>(.*?)</tr>", t, re.S):
            cells = re.findall(r"<t([hd])([^>]*)>(.*?)</t[hd]>", r, re.S)
            rows.append([strip(c) for _, attr, c in cells if "border:none" not in attr])   # side notes skipped
        out.append(rows)
    return out


def hnorm(h):
    return re.sub(r"\s+|\\text\{|\}|\{", "", h)


def mom(d, k):
    return sum(F(x) ** k * p for x, p in d.items())


def stats(d):
    mu = mom(d, 1)
    v1 = sum((F(x) - mu) ** 2 * p for x, p in d.items())
    v2 = mom(d, 2) - mu ** 2
    assert v1 == v2, "the two variance formulas disagree"
    return mu, mom(d, 2), v1


ROWS = {"p(x)": lambda x, p, mu: p, "xp(x)": lambda x, p, mu: x * p, "(x-\\mu)^2": lambda x, p, mu: (x - mu) ** 2,
        "(x-\\mu)^2p(x)": lambda x, p, mu: (x - mu) ** 2 * p, "x^2": lambda x, p, mu: x * x, "x^2p(x)": lambda x, p, mu: x * x * p}


def full_table(block, k, d, names, where, columns=False, sums=True, xname="x"):
    """Table k of block: first row x (header xname), then the rows in names; every cell recomputed from d."""
    label = f"{where} table {k + 1} ({', '.join(names)})"
    try:
        tb = tables(block)[k]
        if columns:
            tb = [list(r) for r in zip(*tb)]
        if [hnorm(r[0]) for r in tb] != [xname] + [hnorm(n) for n in names]:
            raise ValueError(f"row heads {[r[0] for r in tb]}")
        mu, ex2, var = stats(d)
        xs = list(d)
        cols = slice(1, -1) if sums else slice(1, None)
        ok = [val(c) for c in tb[0][cols]] == [F(x) for x in xs] and (not sums or tb[0][-1] == "Sum")
        total = {"p(x)": F(1), "xp(x)": mu, "(x-\\mu)^2p(x)": var, "x^2p(x)": ex2}
        for row, name in zip(tb[1:], names):
            n = hnorm(name)
            cells = [val(c) for c in row[cols]]
            ok = ok and cells == [ROWS[n](F(x), d[x], mu) for x in xs]
            if sums:
                ok = ok and (row[-1] == "—" if n in ("(x-\\mu)^2", "x^2") else val(row[-1]) == total[n])
        report(ok, label, f"mu {mu}, E(X^2) {ex2}, Var {var}")
    except Exception as err:
        report(False, label, f"ERROR {err}")


def dist(outcomes, key=lambda o: o):
    outcomes = list(outcomes)
    d = {}
    for o in outcomes:
        kk = key(o)
        d[kk] = d.get(kk, 0) + F(1, len(outcomes))
    return dict(sorted(d.items()))


def given(block, k, where, columns=False):
    """A question's data table: first row values, second row probabilities -> {x: p}."""
    tb = tables(block)[k]
    if columns:
        tb = [list(r) for r in zip(*tb)]
    xs = [val(c) for c in tb[0][1:] if c not in ("Sum", "")]
    ps = [val(c) for c in tb[1][1:1 + len(xs)]]
    if sum(ps) != 1:
        raise ValueError(f"{where}: probabilities add to {sum(ps)}")
    return dict(zip(xs, ps))


WORDS = {"no": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
         "twelve": 12, "sixteen": 16, "twenty": 20}


def plain(t):
    t = t.replace(MONEY, "$").replace("\\(\\$\\)", "$")
    return re.sub(r"\s+", " ", re.sub(r"</?span[^>]*>", "", t))


def cash_people(stmt):
    t = plain(stmt)
    people = []
    for w, amt in re.findall(r"\b(one|two|three|four|five|six|seven|eight|nine|ten)\s+(?:has|have)\s+\$(\d+)\s+cash", t, re.I):
        people += [int(amt)] * WORDS[w.lower()]
    for w in re.findall(r"\b(one|two|three|four|five|six|seven|eight|nine|ten)\s+have\s+no\s+cash", t, re.I):
        people += [0] * WORDS[w.lower()]
    total = WORDS[re.search(r"\b(\w+) friends", t).group(1).lower()]
    return people, total


# ================================================================ LESSON: concept boxes (four coins)
coins4 = dist(product("HT", repeat=4), key=lambda o: o.count("H"))
mu4, e24, v4 = stats(coins4)
try:
    t1 = tables(teach)[0]
    report([val(c) for c in t1[0][1:]] == list(coins4) and [val(c) for c in t1[1][1:]] == list(coins4.values()) and hnorm(t1[1][0]) == "p(x)",
           "Concept 1: the four-coin table (enumerated)", " | ".join(t1[1][1:]))
except Exception as err:
    report(False, "Concept 1 table", f"ERROR {err}")
value(teach, r"its mean, was found to be \(\mu=@\).", mu4, "Concept 1: mu from Lesson 13B")
full_table(teach, 1, coins4, ["p(x)", "xp(x)", "(x-\\mu)^2", "(x-\\mu)^2p(x)"], "four coins, first formula (rows)")
value(teach, r"<p>Thus the mean is @ and the variance is @.</p>", (mu4, v4), "four coins: mean and variance")
full_table(teach, 2, coins4, ["p(x)", "xp(x)", "(x-\\mu)^2", "(x-\\mu)^2p(x)"], "four coins, columns", columns=True)
ALTBOX = teach.split('<div class="bt">The four coins again, using the alternative formula</div>')[1].split('<div class="box take">')[0]
full_table(ALTBOX, 0, coins4, ["p(x)", "xp(x)", "x^2p(x)"], "four coins, alternative formula")
value(teach, r"From the third row, &ensp;\(\text{E}(X)=@\), which is \(\mu\).", mu4, "four coins: E(X) from the third row")
try:
    g = grab(teach, r"\(\begin{aligned}[t]\text{Var}(X)&amp;=\text{E}(X^2)-\mu^2\\&amp;=@\\&amp;=@,\ \text{as we obtained before.}\end{aligned}\)</p></div>", "four coins chain")
    report(val(g[0].replace("-", "+(-1)*")) == e24 - mu4 ** 2 and strip(g[0]) == f"{e24}-{mu4}^2" and val(g[1]) == v4, "four coins: Var = 5 - 2^2 = 1", str(g))
except Exception as err:
    report(False, "four coins alternative chain", f"ERROR {err}")
for s in (r"\(\text{Var}(X)=\sum(x-\mu)^2p(x)\), &ensp;summed over the distribution.",
          r"\(\text{Var}(X)=\text{E}\big((X-\mu)^2\big)\).", r"\(\text{Var}(X)=\sum x^2p(x)-\mu^2\).", r"\(\text{Var}(X)=\text{E}(X^2)-\mu^2\).",
          r"\(\text{Var}(X)=\text{E}\big((X-\mu)^2\big)\) &ensp;or equivalently&ensp; \(\text{Var}(X)=\text{E}(X^2)-\mu^2\).",
          r"\(\text{Var}(X)=\sum(x-\mu)^2p(x)\) &ensp;or&ensp; \(\sum x^2p(x)-\mu^2\)",
          r"\(\sigma=\sqrt{\text{Var}(X)}\) &ensp;or equivalently&ensp; \(\sigma^2=\text{Var}(X)\)"):
    report(s in teach, f"formula printed: {s[:60]}", "")
report(teach.count(r"\(\sigma=\sqrt{\text{Var}(X)}\) &ensp;or equivalently&ensp; \(\sigma^2=\text{Var}(X)\)") == 2, "sigma formula in the text and in Box 8", "")
# extension: the proof lines, as printed in the textbook (PDF 664); the identity is checked on every distribution below
PROOF = [r"\text{Var}(X)&amp;=\textstyle\sum(x-\mu)^2p(x)", r"&amp;=\textstyle\sum(x^2-2\mu x+\mu^2)p(x)&amp;&amp;\text{(expand the square)}",
         r"&amp;=\textstyle\sum x^2p(x)-\sum2\mu xp(x)+\sum\mu^2p(x)&amp;&amp;\text{(expand the brackets)}",
         r"&amp;=\textstyle\sum x^2p(x)-2\mu\sum xp(x)+\mu^2\sum p(x)&amp;&amp;\text{(take out common factors)}",
         r"\text{Var}(X)&amp;=\textstyle\sum x^2p(x)-2\mu^2+\mu^2", r"&amp;=\textstyle\sum x^2p(x)-\mu^2."]
report(all(s in teach for s in PROOF), "extension proof: all six lines present", "")
ALL = [("four coins", coins4)]

# ================================================================ WE5, WE6 (die), WE7 (robbery from l13b)
die = dist(range(1, 7))
mud, e2d, vd = stats(die)
ALL.append(("die", die))
report("A die is thrown, producing a uniform distribution." in WORK["Worked example 5"] and "A die is thrown, producing a uniform distribution." in WORK["Worked example 6"], "WE5/WE6 statements", "")
full_table(WORK["Worked example 5"], 0, die, ["p(x)", "xp(x)", "(x-\\mu)^2", "(x-\\mu)^2p(x)"], "Worked example 5")
value(WORK["Worked example 5"], r"Hence the mean is \(@\) and the variance is \(@=@\).", (mud, vd, vd), "Worked example 5 result")
full_table(WORK["Worked example 6"], 0, die, ["p(x)", "xp(x)", "x^2p(x)"], "Worked example 6")
value(WORK["Worked example 6"], r"From the third row, &ensp;\(\text{E}(X)=@\).", mud, "Worked example 6 E(X)")
try:
    hits = re.findall(r"\\\(\\begin\{aligned\}\[t\]\\text\{Var\}\(X\)&amp;=\\text\{E\}\(X\^2\)-\\mu\^2\\\\(.*?),\\ \\text\{as we obtained before\.\}", WORK["Worked example 6"], re.S)
    if len(hits) != 1:
        raise LookupError(f"WE6 chain found {len(hits)} times")
    g = hits[0]
    lines = [s.replace("&amp;=", "").strip() for s in g.split("\\\\")]
    v = [sp.nsimplify(sym(s)) for s in lines]
    report(strip(lines[0]) == r"\tfrac{91}{6}-\tfrac{49}{4}" and val(r"\tfrac{91}{6}") == e2d and val(r"\tfrac{49}{4}") == mud ** 2
           and all(F(str(x)) == vd for x in v) and len(lines) == 3, "Worked example 6 chain: each line equals Var", " | ".join(lines))
except Exception as err:
    report(False, "WE6 chain", f"ERROR {err}")
try:
    w3 = re.search(r'<span class="tag">Worked example 3</span>(.*?)<div class="sol-label">', l13b, re.S).group(1)
    people, total = cash_people(w3)
    rob = dist(people)
    report(len(people) == total == 20, "WE7: data from the statement of Worked example 3 (l13b)", str(sorted(people)))
    ALL.append(("robbery", rob))
    mur, e2r, vr = stats(rob)
    full_table(WORK["Worked example 7"], 0, rob, ["p(x)", "xp(x)", "x^2p(x)"], "Worked example 7")
    hits = re.findall(r"\\text\{Var\}\(X\)&amp;=\\text\{E\}\(X\^2\)-\\mu\^2\\\\&amp;=([^\\&]*(?:\\,[^\\&]*)*)\\\\&amp;=", WORK["Worked example 7"])
    if len(hits) != 1:
        raise LookupError(f"WE7 chain found {len(hits)} times")
    g = hits[0]
    a, b = strip(g).split("-")
    c = grab(WORK["Worked example 7"], r"\\&amp;=44\,960-140^2\\&amp;=@\end{aligned}", "WE7 Var")[0]
    report(val(a) == e2r and val(b) == mur ** 2 and val(c) == vr, "Worked example 7: Var = E(X^2) - mu^2", f"{g} = {c}; exact {vr}")
    rounded(WORK["Worked example 7"], r"&amp;\doteqdot@\end{aligned}", math.sqrt(vr), "Worked example 7 sigma")
    value(WORK["Worked example 7"], "giving a spread of " + MONEY + "@</span> about the mean of " + MONEY + "@</span>.", (F(round(math.sqrt(vr), 2)).limit_denominator(100), mur), "WE7 spread and mean")
    report("Worked example 3 of Lesson 13B" in WORK["Worked example 7"], "WE7 refers to Worked example 3 of Lesson 13B", "")
except Exception as err:
    report(False, "Worked example 7", f"ERROR {err}")

# ================================================================ lesson examples C1-C3
def faces_from(stmt):
    m = re.search(r"faces numbered ((?:\d+, )+\d+)\.", stmt)
    return [int(v) for v in m.group(1).split(", ")]


try:
    m8 = re.search(r"its (\w+) faces numbered 1 to (\d+)", DEMO[0])
    m4 = re.search(r"its (\w+) faces numbered 1 to (\d+)", YT[0])
    oct8 = dist(range(1, int(m8.group(2)) + 1))
    tet = dist(range(1, int(m4.group(2)) + 1))
    report(WORDS[m8.group(1)] == 8 and WORDS[m4.group(1)] == 4 and "octahedral" in DEMO[0] and "tetrahedral" in YT[0], "C1 statements: 8 and 4 faces", "")
    c1 = src("C1").split("<b>Your turn.</b>")
    for blk, d, who in ((c1[0], oct8, "demo"), (c1[1], tet, "your turn")):
        mu, e2, v = stats(d)
        full_table(blk, 0, d, ["p(x)", "xp(x)", "(x-\\mu)^2", "(x-\\mu)^2p(x)"], f"C1 {who}")
        value(blk, r"Each value has probability \(@\).", F(1, len(d)), f"C1 {who}")
        value(blk, r"Hence the mean is \(@\) and the variance is \(@=@\).", (mu, v, v), f"C1 {who} result")
        ALL.append((f"C1 {who}", d))
except Exception as err:
    report(False, "C1", f"ERROR {err}")
try:
    fd, fy = faces_from(DEMO[1]), faces_from(YT[1])
    report(len(fd) == len(fy) == 6, "C2 statements: six faces each", f"{fd} {fy}")
    c2 = src("C2").split("<b>Your turn.</b>")
    for blk, faces, who in ((c2[0], fd, "demo"), (c2[1], fy, "your turn")):
        d = dist(faces)
        mu, e2, v = stats(d)
        ALL.append((f"C2 {who}", d))
        full_table(blk, 0, d, ["p(x)", "xp(x)", "x^2p(x)"], f"C2 {who}")
        value(blk, r"From the third row, \(\text{E}(X)=@=@\).", (mu, mu), f"C2 {who} E(X)")
        value(blk, r"From the last row, \(\text{E}(X^2)=@=@\), so", (e2, e2), f"C2 {who} E(X^2)")
        tpl = r"\[\text{Var}(X)=\text{E}(X^2)-\mu^2=@.\]" if who == "demo" else r"\(\text{Var}(X)=\text{E}(X^2)-\mu^2=@\)."
        (g,) = grab(blk, tpl, f"C2 {who} chain")
        sides = g.split("=")
        report(all(F(str(sp.nsimplify(sym(s)))) == v for s in sides) and val(sides[-1]) == v and len(sides) >= 2, f"C2 {who}: Var chain, every side", f"{g}; exact {v}")
        report(strip(sides[0]).replace("\\big(", "(").replace("\\big)", ")").startswith(f"{e2}-"), f"C2 {who}: chain starts with E(X^2) - mu^2", sides[0])
        cnt = {x: faces.count(x) for x in d}
        words = {1: "one", 2: "two", 3: "three", 4: "four"}
        report(f"The values are {', '.join(str(x) for x in list(d)[:-1])} and {list(d)[-1]}, on " in blk
               and ", ".join(words[cnt[x]] for x in list(d)[:-1]) + f" and {words[cnt[list(d)[-1]]]} of the six faces" in blk, f"C2 {who}: face counts in words", str(cnt))
except Exception as err:
    report(False, "C2", f"ERROR {err}")
try:
    c3 = src("C3").split("<b>Your turn.</b>")
    for blk, stmt, n, who in ((c3[0], DEMO[2], 16, "demo"), (c3[1], YT[2], 10, "your turn")):
        people, total = cash_people(stmt)
        report(len(people) == total == n, f"C3 {who}: {n} friends in the statement", str(sorted(people)))
        d = dist(people)
        ALL.append((f"C3 {who}", d))
        mu, e2, v = stats(d)
        full_table(blk, 0, d, ["p(x)", "xp(x)", "x^2p(x)"], f"C3 {who}")
        value(blk, r"Each friend is chosen with probability \(@\).", F(1, n), f"C3 {who}")
        value(blk, r"From the third row, \(\mu=@\).", mu, f"C3 {who} mu")
        (g,) = grab(blk, r"\text{Var}(X)=\text{E}(X^2)-\mu^2=@,\qquad", f"C3 {who} chain")
        s0, s1 = g.split("=")
        a, b = strip(s0).split("-")
        report(val(a) == e2 and val(b) == mu ** 2 and val(s1) == v, f"C3 {who}: Var = E(X^2) - mu^2", f"{g}; exact {v}")
        value(blk, r"\sigma=\sqrt{@}\doteqdot", v, f"C3 {who} sigma radicand")
        rounded(blk, r"}\doteqdot@.\]", math.sqrt(v), f"C3 {who} sigma")
        value(blk, "The mean is " + MONEY + "@</span> and the standard deviation is about " + MONEY + "@</span>.",
              (mu, F(str(round(math.sqrt(v), 2)))), f"C3 {who} sentence")
except Exception as err:
    report(False, "C3", f"ERROR {err}")

# ================================================================ textbook homework answers
try:
    q1 = given(TQ["1"], 0, "Q1")
    report(given(TQ["2"], 0, "Q2") == q1, "Q2 uses the Q1 distribution", "")
    m1, e21, v1 = stats(q1)
    ALL.append(("Q1", q1))
    full_table(src("1"), 0, q1, ["p(x)", "xp(x)", "(x-\\mu)^2", "(x-\\mu)^2p(x)"], "A1a")
    value(src("1"), r"\(\mu=@\), \(\text{Var}(X)=@\)", (m1, v1), "A1a")
    value(src("1"), r"<b>b</b> \(\sigma=\sqrt{@}\doteqdot", v1, "A1b radicand")
    rounded(src("1"), r"}\doteqdot@\)", math.sqrt(v1), "A1b sigma")
    full_table(src("2"), 0, q1, ["p(x)", "xp(x)", "x^2", "x^2p(x)"], "A2a")
    (g,) = grab(src("2"), r"<b>b</b> \(\text{Var}(X)=@\)", "A2b")
    s = g.split("=")
    report(strip(s[0]) == f"{float(e21):g}-{m1}^2" and val(s[1]) == v1, "A2b: Var = 4.8 - 2^2 = 0.8", g)
    heads = [[hnorm(r[0]) for r in tables(TQ[k])[0]] for k in ("1", "2")]
    report(heads == [["x", "p(x)", "xp(x)", "(x-\\mu)^2", "(x-\\mu)^2p(x)"], ["x", "p(x)", "xp(x)", "x^2", "x^2p(x)"]], "Q1/Q2 table rows as printed", str(heads))
except Exception as err:
    report(False, "A1/A2", f"ERROR {err}")
try:
    q3 = [given(TQ["3"], 0, "Q3a"), given(TQ["3"], 1, "Q3b"), given(TQ["3"], 2, "Q3c", columns=True), given(TQ["3"], 3, "Q3d", columns=True)]
    for part, d in zip("abcd", q3):
        mu, e2, v = stats(d)
        ALL.append((f"Q3{part}", d))
        got = grab(src("3"), rf"<b>{part}</b> \(\text{{E}}(X)=@\), \(\text{{E}}(X^2)=@\), \(\text{{Var}}(X)=@\)", f"A3{part}")
        lhs, rhs = got[2].split("=")
        a, b = strip(lhs).split("-")
        report(val(got[0]) == mu and val(got[1]) == e2 and val(a) == e2 and val(b) == mu ** 2 and val(rhs) == v, f"A3{part}: E, E(X^2), Var", f"{got}; exact {mu}, {e2}, {v}")
except Exception as err:
    report(False, "A3", f"ERROR {err}")
try:
    q4 = {"Y": given(TQ["4"], 0, "Q4i"), "Z": given(TQ["4"], 1, "Q4ii"), "V": given(TQ["4"], 2, "Q4iii", columns=True), "W": given(TQ["4"], 3, "Q4iv", columns=True)}
    for rn, L in zip(("i", "ii", "iii", "iv"), "YZVW"):
        d = q4[L]
        mu, e2, v = stats(d)
        ALL.append((f"Q4 {L}", d))
        sd = math.sqrt(v)
        got = grab(src("4"), rf"({rn}) \(\text{{E}}({L})=@\), \(\text{{Var}}({L})=@\), \(\sigma@\)", f"A4a({rn})")
        sg = strip(got[2])
        ok = val(got[0]) == mu and val(got[1]) == v
        if sg.startswith("\\doteqdot"):
            num = sg[len("\\doteqdot"):]
            ok = ok and round(sd, len(num.split(".")[1])) == float(num) and sd != float(num)
        else:
            ok = ok and sg.startswith("=") and val(sg[1:]) ** 2 == v
        report(ok, f"A4a({rn}): E({L}), Var({L}), sigma", f"{got}; exact {mu}, {v}, {sd:.4f}")
    report(stats(q4["Y"])[0] == stats(q4["Z"])[0] and math.isclose(math.sqrt(stats(q4["Z"])[2]), 2 * math.sqrt(stats(q4["Y"])[2]))
           and "the standard deviation is doubled" in src("4"), "A4b(i): same centre, standard deviation doubled", "")
    report(dict(sorted({4 - x: p for x, p in q4["V"].items()}.items())) == q4["W"]
           and stats(q4["V"])[2] == stats(q4["W"])[2] and r"\(W=4-V\)" in src("4"), "A4b(ii): W = 4 - V, variance unchanged", "")
except Exception as err:
    report(False, "A4", f"ERROR {err}")
try:
    tb = tables(TQ["5"])[0]
    d5 = {val(x): val(p) for x, p in zip(tb[0][1:], tb[1][1:]) if val(p) != 0}
    mu, e2, v = stats(d5)
    ALL.append(("Q5", d5))
    value(src("5"), r"\(\text{E}(X)=@\), \(\text{Var}(X)=(2-2)^2\times1=@\)", (mu, v), "A5")
    report(list(d5) == [2] and "deterministic" in TQ["5"], "Q5 is deterministic (single value 2)", "")
except Exception as err:
    report(False, "A5", f"ERROR {err}")
try:
    J, L = given(TQ["6"], 0, "Q6 J"), given(TQ["6"], 1, "Q6 L")
    ALL += [("J", J), ("L", L)]
    for nm, d in (("J", J), ("L", L)):
        mu, e2, v = stats(d)
        got = grab(src("6"), rf"\(\text{{E}}({nm})=@\), \(\text{{E}}({nm}^2)=@\), \(\text{{Var}}({nm})=@\)", f"A6a {nm}")
        sides = strip(got[2]).split("=")
        a, b = sides[0].split("-")
        ok = val(got[0]) == mu and val(got[1]) == e2 and val(a) == e2 and val(b) == mu ** 2
        last = sides[-1]
        if "\\doteqdot" in last:
            ex, ap = last.split("\\doteqdot")
            ok = ok and val(ex) == v and round(float(v), len(ap.split(".")[1])) == float(ap)
        else:
            ok = ok and val(last) == v
        report(ok, f"A6a: E({nm}), E({nm}^2), Var({nm})", f"{got}; exact {mu}, {e2}, {v}")
    report(stats(J)[0] > stats(L)[0] and "his expected value is higher" in src("6") and stats(L)[2] < stats(J)[2] and "Liam is the more consistent player, with the lower variance" in src("6"),
           "A6b/c: John higher mean, Liam lower variance", "")
except Exception as err:
    report(False, "A6", f"ERROR {err}")
try:
    m = re.search(r"sectors of equal size marked ((?:\d, )+\d)\.", TQ["7"])
    d7 = dist(int(v) for v in m.group(1).split(", "))
    mu, e2, v = stats(d7)
    ALL.append(("Q7", d7))
    value(src("7"), r"Each outcome has probability \(@\). This is a uniform distribution.", F(1, len(d7)), "A7a")
    value(src("7"), r"<b>b</b> \(\text{E}(X)=@\)", mu, "A7b")
    value(src("7"), r"<b>c</b> \(\text{Var}(X)=@\)", v, "A7c")
except Exception as err:
    report(False, "A7", f"ERROR {err}")


def zsc(x, mu, s):
    return F(x - mu, s)


try:
    t8 = plain(TQ["8"])
    e = re.search(r"English test was (\d+)\. The test mean was \\\(\\mu=(\d+)\\\) and the standard deviation was \\\(\\sigma=(\d+)\\\)", t8)
    mm = re.search(r"Mathematics test was (\d+)\. The test mean was \\\(\\mu=(\d+)\\\) and the standard deviation was \\\(\\sigma=(\d+)\\\)", t8)
    ze, zm = zsc(*map(int, e.groups())), zsc(*map(int, mm.groups()))
    chain(src("8"), r"<b>a</b> \(\frac{55-65}{5}=@\): two", ze, "A8a", 1)
    chain(src("8"), r"<b>b</b> \(\frac{54-72}{12}=@\): one", zm, "A8b", 1)
    report(ze == -2 and zm == F(-3, 2) and "two standard deviations below" in src("8") and "one and a half standard deviations below" in src("8")
           and r"\frac{55-65}{5}" in src("8") and r"\frac{54-72}{12}" in src("8"), "A8: printed fractions use the statement data; words match", f"{ze}, {zm}")
    report(abs(ze) > abs(zm) and "The English score was more standard deviations below the mean" in src("8"), "A8c: English further below", "")
except Exception as err:
    report(False, "A8", f"ERROR {err}")
try:
    t9 = plain(TQ["9"])
    pairs = re.findall(r"score of (\d+) for ([A-Z][\w ]*?) \(mean (?:of )?(\d+), standard deviation (?:of )?(\d+)\)", t9)
    report(len(pairs) == 6, "Q9: six scores parsed", str(pairs))
    for part, (a, b) in zip("abc", (pairs[0:2], pairs[2:4], pairs[4:6])):
        za, zb = zsc(int(a[0]), int(a[2]), int(a[3])), zsc(int(b[0]), int(b[2]), int(b[3]))

        def words(z):
            side = "above" if z > 0 else "below"
            n = abs(z)
            ns = str(int(n)) if n.denominator == 1 else f"{float(n):g}"
            return f"{ns} standard deviation{'s' if n != 1 else ''} {side}"
        blk = src("9").split(f"<b>{part}</b>")[1].split("<br>")[0]
        ok = f"{a[1]} is {words(za)} the mean" in blk and (f"{b[1]} is {words(zb)} the mean" in blk or f"{b[1]} is also {words(zb)} the mean" in blk)
        better = a[1] if za > zb else b[1] if zb > za else None
        ok = ok and (f"hence the {better} score is" in blk if better else "equally impressive" in blk)
        report(ok, f"A9{part}: z-scores and verdict", f"{a[1]} {za}, {b[1]} {zb}")
except Exception as err:
    report(False, "A9", f"ERROR {err}")
try:
    t10a = given(TQ["10"], 0, "Q10 first")
    t10d = given(TQ["10"], 1, "Q10 corrected")
    d10a = {x: p for x, p in t10a.items() if p}
    d10d = {x: p for x, p in t10d.items() if p}
    ALL += [("Q10 first", d10a), ("Q10 corrected", d10d)]
    ma, _, va = stats(d10a)
    md, _, vd2 = stats(d10d)
    value(src("10"), r"<b>a</b> \(\text{E}(X)=@\),", ma, "A10a E(X)")
    rounded(src("10"), r"<b>a</b> \(\text{E}(X)=3.3\), \(\sigma\doteqdot@\)", math.sqrt(va), "A10a sigma")
    z8 = (8 - ma) / math.sqrt(va)
    (g,) = grab(src("10"), r"<b>c</b> 8 is @ standard deviations above the mean", "A10c")
    report(round(float(z8), 1) == float(g) and float(z8) >= 3 and max(d10a) == 8, "A10c: 8 is 3.2 standard deviations above, an outlier", f"exact {z8:.4f}")
    report(t10d == {x: (t10a[x] if x != 5 else t10a[8]) for x in range(0, 6)}, "Q10d: corrected table moves 0.05 from 8 to 5", "")
    value(src("10"), r"<b>d</b> \(\text{E}(X)=@\),", md, "A10d E(X)")
    rounded(src("10"), r"<b>d</b> \(\text{E}(X)=3.15\), \(\sigma\doteqdot@\)", math.sqrt(vd2), "A10d sigma")
    report(vd2 < va and md < ma, "A10e: mean and spread both smaller after the correction", f"{va} -> {vd2}")
except Exception as err:
    report(False, "A10", f"ERROR {err}")
try:
    kk = sp.Symbol("k")
    xs11 = [int(v) for v in re.search(r"with values ((?:\d, )+\d) is defined by", TQ["11"]).group(1).split(", ")]
    ks = sp.solve(sp.Eq(sum(kk * x for x in xs11), 1), kk)
    k11 = F(str(ks[0]))
    d11 = {x: k11 * x for x in xs11}
    mu, e2, v = stats(d11)
    ALL.append(("Q11", d11))
    value(src("11"), r"\(k=@\), \(\text{E}(X)=@\), \(\sigma=@\)", (k11, mu, F(math.isqrt(v.numerator), math.isqrt(v.denominator))), "A11")
    report(F(math.isqrt(v.numerator), math.isqrt(v.denominator)) ** 2 == v, "A11: Var is a perfect square, sigma exact", str(v))
except Exception as err:
    report(False, "A11", f"ERROR {err}")
try:
    kx = sp.Symbol("k", integer=True, positive=True)
    E12 = sp.factor(sp.summation(kx / NS, (kx, 1, NS)))
    E212 = sp.factor(sp.summation(kx ** 2 / NS, (kx, 1, NS)))
    V12 = sp.factor(E212 - E12 ** 2)
    loc = {"n": NS}
    (g,) = grab(src("12"), r"<b>a</b> \(@\)<br>", "A12a")
    report(sp.simplify(sym(g, loc) - 1 / NS) == 0, "A12a: 1/n", g)
    (g,) = grab(src("12"), r"<b>b</b> \(\text{E}(X)=@\)<br>", "A12b")
    sides = [s.replace("\\dfrac", "\\frac") for s in g.split("=")]
    report(all(sp.simplify(sym(s, loc) - E12) == 0 for s in sides) and len(sides) == 2, "A12b: E(X) = (n+1)/2 (sympy summation)", g)
    (g,) = grab(src("12"), r"<b>c</b> \(\text{E}(X^2)=@\), so", "A12c E(X^2)")
    report(all(sp.simplify(sym(s, loc) - E212) == 0 for s in g.split("=")), "A12c: E(X^2) = (n+1)(2n+1)/6", g)
    (g,) = grab(src("12"), r"\(\text{Var}(X)=@\)<br>", "A12c Var")
    report(all(sp.simplify(sym(s, loc) - V12) == 0 for s in g.split("=")) and sp.simplify(V12 - (NS ** 2 - 1) / 12) == 0, "A12c: Var = (n^2 - 1)/12", g)
    report(r"1+2+3+\cdots+n=\tfrac12n(n+1)" in TQ["12"] and r"1+4+9+\cdots+n^2=\tfrac16n(n+1)(2n+1)" in TQ["12"]
           and sp.simplify(sp.summation(kx, (kx, 1, NS)) - NS * (NS + 1) / 2) == 0 and sp.simplify(sp.summation(kx ** 2, (kx, 1, NS)) - NS * (NS + 1) * (2 * NS + 1) / 6) == 0,
           "Q12 formulae printed and true", "")
    e3, v3 = F(str(E12.subs(NS, 3))), F(str(V12.subs(NS, 3)))
    e6, v6 = F(str(E12.subs(NS, 6))), F(str(V12.subs(NS, 6)))
    value(src("12"), r"With \(n=3\), the formulas give \(\text{E}(X)=@\) and \(\text{Var}(X)=@=@\), as in Question 7.", (e3, v3, v3), "A12d n = 3")
    value(src("12"), r"With \(n=6\), they give \(\text{E}(X)=@\) and \(\text{Var}(X)=@=@\), as for the die", (e6, v6, v6), "A12d n = 6")
    report((e3, v3) == stats(d7)[::2] and (e6, v6) == (mud, vd), "A12d agrees with Q7 and with Worked examples 5 and 6", "")
except Exception as err:
    report(False, "A12", f"ERROR {err}")

# Q13, Q14: the results E(kX + a) = kE(X) + a and sd(kX + a) = k sigma, checked on every distribution of the lesson
okE = okS = True
for name, d in ALL:
    mu, _, v = stats(d)
    for k, a in ((F(2), F(3)), (F(1, 2), F(-5)), (F(3), F(0)), (F(1), F(7))):
        dist_t = {}
        for x, p in d.items():
            dist_t[k * x + a] = dist_t.get(k * x + a, 0) + p
        mt, _, vt = stats(dist_t)
        okE = okE and mt == k * mu + a
        okS = okS and vt == k * k * v
report(okE and len(ALL) >= 20, f"Q13 result E(kX + a) = kE(X) + a on all {len(ALL)} lesson distributions", "")
report(okS, f"Q14 result Var(kX + a) = k^2 Var(X), so sd = k sigma (k > 0), on all {len(ALL)} lesson distributions", "")
for s in (r"&amp;=\mu+a,\end{aligned}\]", r"because \(\sum P(X=x)=1\).", r"&amp;=k\mu.\end{aligned}\]", r"&amp;=\textstyle\sum(x+a)P(X=x)\\", r"&amp;=\textstyle\sum(kx)P(X=x)\\"):
    report(s in src("13"), f"A13 proof line {s[:40]}", "")
for s in (r"&amp;=\text{E}\big((X-\mu)^2\big)\\", r"&amp;=\text{Var}(X)\end{aligned}\]", r"&amp;=k^2\times\text{E}\big((X-\mu)^2\big)\\",
          r"&amp;=k^2\,\text{Var}(X)\end{aligned}\]", r"\(\sqrt{k^2\sigma^2}=k\sigma\)", "remains \\(\\sigma\\)"):
    report(s in src("14"), f"A14 proof line {s[:40]}", "")
report(r"\(k&gt;0\)" in TQ["14"] and r"\(\text{E}(kX+a)=k\text{E}(X)+a\)" in TQ["13"], "Q13/Q14 statements (k > 0 in Q14)", "")
report("(Questions 13 and 14)" in teach, "Standard deviation box points to Questions 13 and 14 (the proportionality proofs)", "")

want_blocks = ["C1", "C2", "C3"] + [str(i) for i in range(1, 15)]
report(sorted(BLK, key=lambda t: (len(t), t)) == sorted(want_blocks, key=lambda t: (len(t), t)), "answer blocks C1-C3 and 1-14", str(sorted(BLK, key=lambda t: (len(t), t))))
report(sorted(TQ, key=int) == [str(i) for i in range(1, 15)], "textbook questions 1-14", str(sorted(TQ, key=int)))
report(re.findall(r"\{\{band:([FDE])\}\}", hw) == ["F", "D", "E"] and hw.index('q-num">3<') < hw.index("{{band:D}}") < hw.index('q-num">4<')
       and hw.index('q-num">11<') < hw.index("{{band:E}}") < hw.index('q-num">12<'), "bands F 1-3, D 4-11, E 12-14", "")

# ================================================================ past papers
PPQ = re.findall(r'<div class="pp"><div class="pp-src"><span><span class="pn">(PP \d)</span>(.*?)</span><span class="mk">(\d) marks?</span></div>(.*?)(?=<div class="pp">|$)', ppl, re.S)
PPA = re.findall(r'<div class="ppa"><div class="pp-src"><span><span class="pn">(PP \d)</span>(.*?)</span></div>(.*?)(?=<div class="ppa">|$)', ans.split("Past-Paper Homework - Worked Solutions")[1], re.S)
LABELS = ["James Ruse Agricultural High School, 2020, Year 12 Trial HSC Examination, Mathematics <span style=\"white-space:nowrap\">Extension&nbsp;1,&nbsp;Q1</span>",
          "Baulkham Hills High School, 2020, Year 12 Trial Examination, Mathematics <span style=\"white-space:nowrap\">Extension&nbsp;1,&nbsp;Q12(a)(iii)</span>",
          "Hurlstone Agricultural High School, 2023, Higher School Certificate Trial Examination, Mathematics <span style=\"white-space:nowrap\">Extension&nbsp;1,&nbsp;Q8</span>"]
report([p[0] for p in PPQ] == ["PP 1", "PP 2", "PP 3"] and [p[1] for p in PPQ] == LABELS, "past-paper labels in the lesson", str([p[1][:40] for p in PPQ]))
report([p[0] for p in PPA] == ["PP 1", "PP 2", "PP 3"] and [p[1] for p in PPA] == LABELS, "past-paper labels in the answers (same)", "")
marks = sum(int(p[2]) for p in PPQ)
mins = 5 * round(1.5 * marks / 5) if 1.5 * marks % 5 != 2.5 else 5 * math.ceil(1.5 * marks / 5)
report(f"<b>Suggested time: {mins} minutes</b>" in ppl and f"<b>{marks} marks</b>" in ppl and marks == 3, "pp-intro: 3 marks, 5 minutes", f"{marks} marks, {mins} min")
report(all(p[3].count('<div class="hint"><b>Hint:</b>') == 1 for p in PPQ), "one hint per past-paper question", "")
report(sum(p[3].count('class="mk">1<') for p in PPQ) == 1 and "(iii) Calculate \\(\\text{Var}(X)\\)." in PPQ[1][3], "PP 2 part mark and wording", "")
mc = lambda blk: {k: v for k, v in re.findall(r"<span>\(([A-D])\) (.*?)</span>", re.search(r'<div class="mc">(.*?)</div>', blk, re.S).group(1))}
try:
    p = val(re.search(r"The probability of success in a Bernoulli trial is ([\d.]+)\.", PPQ[0][3]).group(1))
    bern = {0: 1 - p, 1: p}
    mu, e2, v = stats(bern)
    opts = mc(PPQ[0][3])
    right = [k for k, s in opts.items() if val(s) == v]
    report(right == ["D"] and "<b>Answer (D).</b>" in PPA[0][2], "PP 1: Var = p(1 - p) = 0.21, answer D", f"{v}; options {opts}")
    full_table(PPA[0][2], 0, bern, ["p(x)", "xp(x)", "x^2p(x)"], "PP 1 table")
    (g,) = grab(PPA[0][2], r"\text{Var}(X)=\text{E}(X^2)-\mu^2=@.\]", "PP 1 chain")
    report(all(val(s.replace("-", "+(-1)*")) == v for s in g.split("=")), "PP 1 chain, every side 0.21", g)
    report(val(opts["A"]) == mu ** 2 and val(opts["B"]) == 1 - p and val(opts["C"]) == p
           and "Option (A), 0.09, is \\(\\mu^2\\) only" in PPA[0][2] and "(B), 0.7, is the probability of failure" in PPA[0][2] and "(C), 0.3, is the mean" in PPA[0][2],
           "PP 1: the wrong options explained correctly", "")
except Exception as err:
    report(False, "PP 1", f"ERROR {err}")
try:
    tb = tables(PPQ[1][3])[0]
    p4 = val(tb[1][5])
    q = 1 - F(str(sp.Rational(str(p4)) ** sp.Rational(1, 4)))                 # P(X = 4) = p^4, so p = 0.3
    pb = 1 - q
    binom = {k: F(math.comb(4, k)) * pb ** k * q ** (4 - k) for k in range(5)}
    ab = re.search(r"it was found that \\\(a=([\d.]+)\\\) and \\\(b=([\d.]+)\\\)\.", PPQ[1][3])
    a, b = F(ab.group(1)), F(ab.group(2))
    report(pb == F(3, 10) and [val(tb[1][1]), val(tb[1][4]), val(tb[1][5])] == [binom[0], binom[3], binom[4]] and (a, b) == (binom[1], binom[2])
           and tb[1][2] == "a" and tb[1][3] == "b", "PP 2: printed table and the supplied a, b agree with Bin(4, 0.3)", f"a {a}, b {b}")
    d2 = {0: binom[0], 1: a, 2: b, 3: binom[3], 4: binom[4]}
    mu, e2, v = stats(d2)
    full_table(PPA[1][2], 0, d2, ["p(x)", "xp(x)", "x^2p(x)"], "PP 2 answer table")
    value(PPA[1][2], r"From the third row, \(\mu=@\). From the last row, \(\text{E}(X^2)=@\).", (mu, e2), "PP 2 mu, E(X^2)")
    (g,) = grab(PPA[1][2], r"\text{Var}(X)=\text{E}(X^2)-\mu^2=@.\]", "PP 2 chain")
    report(all(val(s.replace("-", "+(-1)*")) == v for s in g.split("=")) and v == 4 * pb * q, "PP 2: Var = 0.84 (also 4pq, the school's value)", g)
    value(PPA[1][2], r"Put \(a=@\) and \(b=@\) into the table", (a, b), "PP 2 a, b")
except Exception as err:
    report(False, "PP 2", f"ERROR {err}")
try:
    pp = sp.Symbol("p")
    Ebern = 0 * (1 - pp) + 1 * pp
    Vbern = sp.expand((0 ** 2) * (1 - pp) + 1 ** 2 * pp - Ebern ** 2)
    k5 = int(re.search(r"E\(X\)=(\d)Var\(X\)", PPQ[2][3]).group(1))
    sols = [s for s in sp.solve(sp.Eq(Ebern, k5 * Vbern), pp) if s != 0]
    opts = mc(PPQ[2][3])
    right = [k for k, s in opts.items() if val(s) == F(str(sols[0]))]
    report(len(sols) == 1 and right == ["B"] and "<b>Answer (B).</b>" in PPA[2][2] and r"p\ne0" in PPQ[2][3], "PP 3: p = 4/5, answer B", f"{sols}; options {opts}")
    value(PPA[2][2], r"\[1=5(1-p),\qquad1-p=@,\qquad p=@.\]", (1 - F(str(sols[0])), F(str(sols[0]))), "PP 3 solving")
    for o in ("A", "D"):
        pv = val(opts[o])
        report(strip(opts[o]) == rf"\tfrac{pv.numerator}{pv.denominator}", f"PP 3 option {o} printed as a fraction", opts[o])
        value(PPA[2][2], rf"\(\tfrac{pv.numerator}{pv.denominator}\) gives \(\text{{E}}(X)=@\) but \(5\,\text{{Var}}(X)=@\)", (pv, 5 * pv * (1 - pv)), f"PP 3 option {o}")
    report(val(opts["C"]) == 1 - F(str(sols[0])), "PP 3: option C is 1 - p", "")
    value(PPA[2][2], r"\(\text{Var}(X)=\tfrac45\times\tfrac15=@\), and \(5\times\tfrac{4}{25}=@\)", (F(4, 25), F(4, 5)), "PP 3 check line")
except Exception as err:
    report(False, "PP 3", f"ERROR {err}")

# ================================================================ figure (four coins, shared with 13B: c13b_coins)
sys.path.insert(0, os.path.join(HERE, "..", "build"))
sys.path.insert(0, SRC)
try:
    import figs                                    # noqa: E402
    rec = {}
    figs.dist_graph = lambda name, xs, ps, yt, **kw: rec.__setitem__(name, (list(xs), [F(p) for p in ps], kw))
    figs.build_13b()
    xs, ps, kw = rec["c13b_coins"]
    report(xs == list(coins4) and ps == list(coins4.values()) and kw.get("ylab") == "p(x)" and os.path.exists(os.path.join(SRC, "svg", "c13b_coins.svg")),
           "figure c13b_coins: the four-coin distribution, ticks 0-4", str(xs))
    report(les.count("{{svg:") == 1 and les.count("{{svg:c13b_coins}}") == 1 and "{{svg:" not in ans, "only figure in 13C: c13b_coins, once", "")
except Exception as err:
    report(False, "figure", f"ERROR {err}")
report("$" not in re.sub(r"\\\$", "", les + ans), "no literal dollar signs (money is \\(\\$\\))", "")

print(f"\n{NCHECK[0]} checks, {len(FAILS)} problem(s)" if FAILS else f"\n{NCHECK[0]} checks, all OK")
sys.exit(1 if FAILS else 0)
