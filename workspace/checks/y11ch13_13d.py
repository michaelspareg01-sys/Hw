"""Check of Lesson 13D (Y11 Ch 13 pack): Sampling, and the Chapter 13 review exercise.

The script reads the values PRINTED in workspace/build/y11ch13/l13d.html (concept boxes, worked examples,
the data in the demos, your-turns, textbook questions, past-paper stem and review questions) and in
a_13d.html (lesson-example answers, textbook homework answers, past-paper solution, review answers).
Every table is parsed cell by cell; every inline value is found with a template ('@' marks the printed
value) that must match exactly once in its block, otherwise the item FAILS.  Printed LaTeX (\\tfrac, mixed
numbers, decimals, 308\\,025) is turned into an exact rational.

Each printed result is compared with an independent computation (fractions.Fraction, exact sums):
  - theoretical distributions are ENUMERATED (coins with itertools.product, three dice, two dice: sum and
    difference), never copied from the answers;
  - sample tables: f_r = f/n, x f_r, x^2 f_r and the sums are recomputed from the PRINTED frequencies;
    x-bar, s^2 = sum x^2 f_r - x-bar^2 and s are recomputed exactly and compared with the printed
    rounding; Worked example 8 is checked against the book's 4-decimal rounding of f/2527 (exact values);
  - the correction factor n/(n-1); the uniform-distribution results quoted in Q5 (mu, sigma^2);
  - Benford's table (Q7): mu, E(X^2), sigma; the tank formula (Q14) and its diagram (SVG positions);
  - the table of random numbers is compared group by group with the text layer of the textbook pages
    (PDF 683-684), an independent source;
  - past paper: the event 'at most 12 of 18 rolls' is compared with each option's event for p-hat;
  - review: sums of probabilities, E, Var, sigma, linear transforms E(aX+b), Var(aX+b);
  - figures: figs.build_13d() is re-run with dist_graph recorded (no file written).
No simulation is used.  It also checks the structure (concepts, boxes 9 and 10, the extension box, demos,
your-turns, worked examples, answer blocks, bands, past-paper label, marks and time, review questions).

Exit status 1 if anything fails.  Run: python3 workspace/checks/y11ch13_13d.py
"""
import math
import os
import re
import sys
from decimal import Decimal, ROUND_HALF_UP
from fractions import Fraction as F
from itertools import product

import sympy as sp
from sympy.parsing.sympy_parser import (implicit_multiplication, parse_expr, rationalize,
                                        standard_transformations)

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.environ.get("Y11CH13_SRC", os.path.join(HERE, "..", "build", "y11ch13"))   # override only for mutation tests
BOOK = os.path.join(HERE, "..", "sources", "CSM6_EXT1Y11_book.pdf")
FAILS = []
NCHECK = [0]
TR = standard_transformations + (implicit_multiplication, rationalize)


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
                whole = out.pop() + whole
            frac = f"(({_conv(u)})/({_conv(v)}))"
            out.append(f"({whole}+{frac})" if whole else frac)
        elif t.startswith("\\times", i):
            out.append("*")
            i += 6
        elif t.startswith("\\sqrt", i):
            u, i = _arg(t, i + 5)
            out.append(f"sqrt({_conv(u)})")
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


def sym(t):
    t = strip(t)
    return parse_expr(_conv(t.replace(" ", "")), transformations=TR)


def val(t):
    e = sym(t)
    if not e.is_Rational:
        e = sp.nsimplify(e)
    if not e.is_Rational:
        raise ValueError(f"not a number: {t!r}")
    return F(int(e.p), int(e.q))


def r_half(x, dp):
    """Round half up, as the book does."""
    x = F(x)
    q = Decimal(1).scaleb(-dp)
    return F(str((Decimal(x.numerator) / Decimal(x.denominator)).quantize(q, rounding=ROUND_HALF_UP)))


def grab(block, template, where):
    pieces = template.split("@")
    cap = r"((?:(?!\\\)|\\\]|\\\\|</td>|<br>|</span>|,\\qquad|&ensp;).)+?)"
    rx = "".join(re.escape(pc) + (cap if i < len(pieces) - 1 else "") for i, pc in enumerate(pieces))
    found = re.findall(rx, block, re.S)
    if len(found) != 1:
        raise LookupError(f"template matched {len(found)} times in {where}: {template!r}")
    return found[0] if isinstance(found[0], tuple) else (found[0],)


def value(block, template, expected, where):
    label = f"{where}: {template[:70]}"
    try:
        got = grab(block, template, where)
        exp = expected if isinstance(expected, tuple) else (expected,)
        ok = len(got) == len(exp) and all(val(g) == e for g, e in zip(got, exp))
        report(ok, label, f"printed {got}, expected {tuple(str(e) for e in exp)}")
    except Exception as err:
        report(False, label, f"ERROR {err}")


def rounded(block, template, exact, where):
    """Printed decimal (after \\doteqdot) must be the exact value rounded to the printed decimals."""
    label = f"{where}: {template[:70]}"
    try:
        (g,) = grab(block, template, where)
        g = strip(g)
        dp = len(g.split(".")[1]) if "." in g else 0
        report(F(g) == r_half(F(exact) if not isinstance(exact, float) else F(exact), dp), label, f"printed {g}, exact {float(exact):.6f}")
    except Exception as err:
        report(False, label, f"ERROR {err}")


def present(block, s, where):
    report(block.count(s) == 1, f"{where}: printed once: {s[:70]}", f"found {block.count(s)}")


def tables(block, cls="t"):
    out = []
    for t in re.findall(r'<table class="' + cls + r'[^"]*"[^>]*>(.*?)</table>', block, re.S):
        rows = []
        for r in re.findall(r"<tr>(.*?)</tr>", t, re.S):
            cells = re.findall(r"<t([hd])([^>]*)>(.*?)</t[hd]>", r, re.S)
            rows.append([strip(c) for _, attr, c in cells if "border:none" not in attr])
        out.append(rows)
    return out


def hnorm(h):
    return re.sub(r"\s+|\\text\{|\}|\{", "", h)


def cellval(c):
    """A table cell: drop words such as 'suns' and a trailing '=\\bar{x}'."""
    c = re.sub(r"=\\bar\{?x\}?$", "", c).strip()
    c = re.sub(r"\s+[a-z ]+$", "", c).strip()
    return val(c)


def dist(outcomes, key):
    outcomes = list(outcomes)
    d = {}
    for o in outcomes:
        kk = key(o)
        d[kk] = d.get(kk, 0) + F(1, len(outcomes))
    return dict(sorted(d.items()))


def mom(d, k):
    return sum(F(x) ** k * p for x, p in d.items())


def stats(d):
    mu = mom(d, 1)
    v1 = sum((F(x) - mu) ** 2 * p for x, p in d.items())
    v2 = mom(d, 2) - mu ** 2
    assert v1 == v2
    return mu, mom(d, 2), v1


def sqrt_f(x):
    return math.sqrt(x.numerator / x.denominator)


def r_float(x, dp):
    return F(str(Decimal(repr(x)).quantize(Decimal(1).scaleb(-dp), rounding=ROUND_HALF_UP)))


def sd_rounded(block, template, var, where):
    label = f"{where}: {template[:70]}"
    try:
        (g,) = grab(block, template, where)
        g = strip(g)
        dp = len(g.split(".")[1]) if "." in g else 0
        report(F(g) == r_float(sqrt_f(F(var)), dp), label, f"printed {g}, sqrt({var}) = {sqrt_f(F(var)):.6f}")
    except Exception as err:
        report(False, label, f"ERROR {err}")


def theory_table(tb, d, names, where, sums=True):
    """Rows x, then names (p(x), xp(x), x^2p(x), (x-mu)^2, (x-mu)^2p(x)); every cell from d."""
    label = f"{where} ({', '.join(names)})"
    try:
        heads = [hnorm(r[0]) for r in tb]
        if heads != ["x"] + [hnorm(n) for n in names]:
            raise ValueError(f"row heads {heads}")
        mu, ex2, var = stats(d)
        xs = list(d)
        cols = slice(1, -1) if sums else slice(1, None)
        ok = [cellval(c) for c in tb[0][cols]] == [F(x) for x in xs]
        fn = {"p(x)": lambda x: d[x], "xp(x)": lambda x: x * d[x], "x^2p(x)": lambda x: x * x * d[x],
              "(x-\\mu)^2": lambda x: (x - mu) ** 2, "(x-\\mu)^2p(x)": lambda x: (x - mu) ** 2 * d[x]}
        tot = {"p(x)": F(1), "xp(x)": mu, "x^2p(x)": ex2, "(x-\\mu)^2p(x)": var}
        for row, n in zip(tb[1:], names):
            n = hnorm(n)
            ok = ok and [cellval(c) for c in row[cols]] == [fn[n](F(x)) for x in xs]
            if sums:
                ok = ok and (row[-1] == "—" if n == "(x-\\mu)^2" else cellval(row[-1]) == tot[n])
        report(ok, label, f"mu {mu}, E(X^2) {ex2}, Var {var}")
    except Exception as err:
        report(False, label, f"ERROR {err}")


def freq_of(tb, where):
    """Rows x and f of a printed frequency table -> {x: f}."""
    if [hnorm(r[0]) for r in tb[:2]] != ["x", "f"]:
        raise ValueError(f"{where}: row heads {[r[0] for r in tb]}")
    xs, fs = tb[0][1:], tb[1][1:]
    if xs[-1] == "Sum":
        n = cellval(fs[-1])
        xs, fs = xs[:-1], fs[:-1]
        if sum(cellval(c) for c in fs) != n:
            raise ValueError(f"{where}: frequencies do not add to the printed sum")
    return {cellval(x): int(cellval(c)) for x, c in zip(xs, fs)}


def sample_stats(fr):
    n = sum(fr.values())
    d = {x: F(f, n) for x, f in fr.items()}
    xb = mom(d, 1)
    s2 = mom(d, 2) - xb ** 2
    return n, d, xb, mom(d, 2), s2


def sample_table(tb, fr, names, where, rnd=None):
    """Rows x, f, f_r, xf_r, x^2f_r (names gives the rows after x); every cell recomputed from the
    printed frequencies (rnd: decimals of the book's rounding, else exact)."""
    label = f"{where} ({', '.join(names)})"
    try:
        heads = [hnorm(r[0]) for r in tb]
        if heads != ["x"] + [hnorm(n) for n in names]:
            raise ValueError(f"row heads {heads}")
        n, d, xb, ex2, s2 = sample_stats(fr)
        xs = list(fr)
        has_sum = tb[0][-1] == "Sum"
        cols = slice(1, -1) if has_sum else slice(1, None)
        ok = [cellval(c) for c in tb[0][cols]] == [F(x) for x in xs]
        R = (lambda v: r_half(v, rnd)) if rnd else (lambda v: v)
        fn = {"f": lambda x: F(fr[x]), "xf": lambda x: x * fr[x], "f_r": lambda x: R(d[x]),
              "xf_r": lambda x: R(x * d[x]), "x^2f_r": lambda x: R(x * x * d[x])}
        tot = {"f": F(n), "xf": n * xb, "f_r": F(1), "xf_r": R(xb), "x^2f_r": R(ex2)}
        for row, nm in zip(tb[1:], names):
            nm = hnorm(nm)
            ok = ok and [cellval(c) for c in row[cols]] == [fn[nm](F(x)) for x in xs]
            if has_sum:
                ok = ok and cellval(row[-1]) == tot[nm]
        report(ok, label, f"n {n}, xbar {xb}, E(x^2) {ex2}, s^2 {s2}")
    except Exception as err:
        report(False, label, f"ERROR {err}")


def split_tables(tbs):
    """Join a sample table printed in two halves (same row heads) into one."""
    a, b = tbs
    return [ra + rb[1:] for ra, rb in zip(a, b)]


# ---------------------------------------------------------------- HTML blocks
les = read("l13d.html")
ans = read("a_13d.html")
teach, rest = les.split("<!-- ============ Homework ============ -->")
hw, rest2 = rest.split("<!-- ============ Past papers ============ -->")
ppl, rev = rest2.split("<!-- ============ Chapter review ============ -->")
CON = re.split(r"<!-- ============ Concept \d ============ -->", teach)[1:]
report(len(CON) == 4 and re.findall(r"\{\{sec:teal:key:Concept (\d)", teach) == ["1", "2", "3", "4"], "four concepts", "")
EX = re.findall(r'<div class="ex (demo|attempt|worked)"[^>]*><div class="ex-top"><span class="tag">([^<]*)</span><span class="ex-title">([^<]*)</span>(.*?)(?=<div class="ex |<div class="box|<!-- =====|$)', teach, re.S)
DEMO = [b for k, _, _, b in EX if k == "demo"]
YT = [b for k, _, _, b in EX if k == "attempt"]
WORK = [(t, b) for k, t, _, b in EX if k == "worked"]
report(len(DEMO) == 4 and len(YT) == 4 and [t for t, _ in WORK] == ["Worked example", "Worked example 8", "Worked example", "Worked example", "Worked example"],
       "lesson structure: 4 demos, 4 your-turns, worked examples (text, 8, text x3)", f"{len(DEMO)} {len(YT)} {[t for t, _ in WORK]}")
for c in range(4):
    report(sum(1 for k, _, _, b in EX if k == "demo" and b in CON[c]) == 1 and sum(1 for k, _, _, b in EX if k == "attempt" and b in CON[c]) == 1,
           f"Concept {c + 1}: one demo and one your-turn", "")
for box in ("Sampling", "Sampling of a theoretical probability distribution", "Rounding errors and simulations", "Sample statistics and theoretical statistics",
            "Populations: census and survey", "Sampling when there are no exact probabilities", "Predicting the future",
            "Extension: a correction factor for the sample variance"):
    report(f'<div class="bt">{box}</div>' in teach, f"box '{box}'", "")
report('<div class="box take"><div class="bt">9 Sample distribution</div>' in teach and '<div class="box take"><div class="bt">10 Population: census and survey</div>' in teach,
       "Boxes 9 and 10", "")
for box in ("Approaching the following exercise", "Using a spreadsheet", "A table of random numbers"):
    report(f'<div class="bt">{box}</div>' in hw, f"homework box '{box}'", "")
report(ans.count("{{ahead:Lesson 13D | Sampling}}") == 2 and ans.count("{{ahead:Chapter 13 Review | Chapter review exercise}}") == 1, "answers: ahead headings", "")
secs = re.findall(r'<div class="ans-sec">([^<{]+)</div>', ans)
report(secs == ["Lesson Examples", "Textbook Homework", "Past-Paper Homework - Worked Solutions"], "answer sections in order", str(secs))
a_les, a_rest = ans.split('<div class="ans-sec">Textbook Homework</div>')
a_hw, a_rest = a_rest.split("{{ahead:Lesson 13D | Sampling}}")
a_pp, a_rev = a_rest.split("{{ahead:Chapter 13 Review | Chapter review exercise}}")


def blocks(part):
    out = {}
    for mt in re.finditer(r'<div class="a"(?: style="[^"]*")?><span class="an">([^<]+)</span><div class="ab">(.*?)(?=<div class="a"(?: style="[^"]*")?><span class="an">|<div class="ans-sec">|\{\{ahead|$)', part, re.S):
        if mt.group(1) in out:
            report(False, f"block {mt.group(1)}", "duplicate")
        out[mt.group(1)] = mt.group(2)
    return out


BL, BH, BR = blocks(a_les), blocks(a_hw), blocks(a_rev)
report(list(BL) == ["C1", "C2", "C3", "C4"], "lesson example answers C1-C4", str(list(BL)))
report(list(BH) == ["1", "2", "4", "7", "12", "14"], "homework answers: items with a final answer in the book", str(list(BH)))
report(list(BR) == [str(i) for i in range(1, 13)], "review answers 1-12", str(list(BR)))
TQ = dict(re.findall(r'<div class="q"><span class="q-num">(\d+)</span>(.*?)(?=<div class="q">|\{\{band|<div class="box|$)', hw, re.S))
RQ = dict(re.findall(r'<div class="q"><span class="q-num">(\d+)</span>(.*?)(?=<div class="q">|$)', rev, re.S))
report(list(TQ) == [str(i) for i in range(1, 15)], "Exercise 13D: questions 1-14", str(list(TQ)))
report(list(RQ) == [str(i) for i in range(1, 13)], "review: questions 1-12", str(list(RQ)))
bands = re.findall(r"\{\{band:([FDE])\}\}(.*?)(?=\{\{band|<div class=\"box concept\"><div class=\"bt\">A table|$)", hw, re.S)
report([(b, re.findall(r'q-num">(\d+)<', t)) for b, t in bands] ==
       [("F", ["1", "2", "3", "4", "5"]), ("D", [str(i) for i in range(6, 14)]), ("E", ["14"])], "bands F 1-5, D 6-13, E 14 (as the book)", "")

# ================================================================ Concept 1
coins4 = dist(product("HT", repeat=4), key=lambda o: o.count("H"))
try:
    t = tables(CON[0])[0]
    mu, ex2, var = stats(coins4)
    ok = [hnorm(r[0]) for r in t] == ["x", "p(x)", "xp(x)", "x^2p(x)"]
    ok = ok and [cellval(c) for c in t[1][1:-1]] == [r_half(p, 2) for p in coins4.values()]          # rounded probabilities
    ok = ok and [cellval(c) for c in t[2][1:-1]] == [x * p for x, p in coins4.items()]                # 'not recalculated': exact values
    ok = ok and [cellval(c) for c in t[3][1:-1]] == [x * x * p for x, p in coins4.items()]
    ok = ok and [cellval(r[-1]) for r in t[1:]] == [1, mu, ex2]
    report(ok, "Concept 1: four coins, probabilities rounded to 2 dp, last two rows exact", f"mu {mu}, E(X^2) {ex2}")
    report(t[3][3] == "1.50" and r_half(coins4[2], 2) == F("0.38") and F("1.50") != 4 * F("0.38"), "Concept 1: 1.50 is not 2^2 x 0.38 (the book's remark)", "")
except Exception as err:
    report(False, "Concept 1 table", f"ERROR {err}")
value(CON[0], r"<p>We concluded that \(\text{E}(X)=@\) and \(\text{Var}(X)=5-2^2=@\).</p>", (stats(coins4)[0], stats(coins4)[2]), "Concept 1: E(X) and Var(X)")
present(CON[0], r"\(\text{Var}(X)=5-2^2=1\)", "Concept 1: Var = E(X^2) - mu^2 written as 5 - 2^2")
for s in (r"\(\bar{x}=\sum xf_r\)", r"\(s^2=\sum(x-\bar{x})^2f_r\) &ensp;or&ensp; \(s^2=\sum x^2f_r-\bar{x}^2\)"):
    present(CON[0], s, "Box 9 formula")
# worked example from the text: the authors' 100 simulations of four coins
we = WORK[0][1]
try:
    fr = freq_of(tables(we)[0], "four-coin sample statement")
    sample_table(tables(we)[1], fr, ["f", "f_r", "xf_r", "x^2f_r"], "four-coin sample (solution table)")
    n, d, xb, ex2, s2 = sample_stats(fr)
    value(we, r"which is written as \(\bar{x}=@\).", xb, "four-coin sample: x-bar")
    value(we, r"just as the <i>theoretical mean</i> \(\mu=@\)", stats(coins4)[0], "four-coin sample: mu")
    try:
        g = grab(we, r"\(\begin{aligned}[t]s^2&amp;=\textstyle\sum x^2f_r-\bar{x}^2\\&amp;=@-(@)^2\\&amp;\doteqdot@\ \ \text{(compare with 1)}\end{aligned}\)", "s^2")
        report(val(g[0]) == ex2 and val(g[1]) == xb and F(strip(g[2])) == r_half(s2, 2) and stats(coins4)[2] == 1, "four-coin sample: s^2 = 4.98 - 1.96^2 ~ 1.14 (theory 1)", str(g))
    except Exception as err:
        report(False, "four-coin s^2", f"ERROR {err}")
    sd_rounded(we, r"&amp;\doteqdot@\text{ heads}", s2, "four-coin sample: s")
except Exception as err:
    report(False, "four-coin sample", f"ERROR {err}")

# demos and answers C1
coins3 = dist(product("HT", repeat=3), key=lambda o: o.count("H"))
coins2 = dist(product("HT", repeat=2), key=lambda o: o.count("H"))
for who, stmt, d_th, blk in (("C1 demo", DEMO[0], coins3, BL["C1"].split("<b>Your turn.</b>")[0]),
                             ("C1 your turn", YT[0], coins2, BL["C1"].split("<b>Your turn.</b>")[1])):
    try:
        report(re.search(r"(Three|Two) coins are tossed", stmt).group(1) == {3: "Three", 2: "Two"}[len(d_th) - 1], f"{who}: statement number of coins", "")
        tb = tables(blk)
        theory_table(tb[0], d_th, ["p(x)", "xp(x)", "x^2p(x)"], f"{who} (a) theoretical table, enumerated")
        mu, ex2, var = stats(d_th)
        value(blk, r"\(\mu=@\), &ensp;", mu, f"{who}: mu")
        g = grab(blk, r"\(\sigma^2=@-\big(@\big)^2=@\), &ensp;", who) if "\\big(" in blk.split("\\sigma^2=")[1][:40] else grab(blk, r"\(\sigma^2=@-@^2=@\), &ensp;", who)
        report(val(g[0]) == ex2 and val(g[1]) == mu and val(g[2]) == var, f"{who}: sigma^2 = E(X^2) - mu^2", str(g))
        rx = re.search(r"\\sigma=\\sqrt\{([\d.]+)\}\\doteqdot([\d.]+)", blk)
        report(F(rx.group(1)) == var and F(rx.group(2)) == r_float(sqrt_f(var), 2), f"{who}: sigma", rx.group(0))
        fr = freq_of(tables(stmt)[0], f"{who} statement")
        sample_table(tb[1], fr, ["f", "f_r", "xf_r", "x^2f_r"], f"{who} (b) sample table")
        n, d, xb, sx2, s2 = sample_stats(fr)
        report(re.search(rf"Divide each frequency by (\d+)", blk).group(1) == str(n) and f"simulated {n} times" in stmt, f"{who}: n = {n}", "")
        g = grab(blk, r"\(\bar{x}=@\), &ensp;\(s^2=@-@^2=@\doteqdot@\), &ensp;\(s=\sqrt{@}\doteqdot@\)", who)
        report(val(g[0]) == xb and val(g[1]) == sx2 and val(g[2]) == xb and val(g[3]) == s2 and F(g[4]) == r_half(s2, 2)
               and val(g[5]) == s2 and F(g[6]) == r_float(sqrt_f(s2), 2), f"{who}: x-bar, s^2, s", str(g))
        cmp_ = re.search(r"<b>c</b> The sample mean ([\d.]+) is[^,]*\\\(\\mu=([\d.]+)\\\), and \\\(s\\doteqdot([\d.]+)\\\) is [^\\]*\\\(\\sigma\\doteqdot([\d.]+)\\\)", blk)
        report(cmp_ is not None and F(cmp_.group(1)) == xb and F(cmp_.group(2)) == mu and F(cmp_.group(3)) == r_float(sqrt_f(s2), 2)
               and F(cmp_.group(4)) == r_float(sqrt_f(var), 2), f"{who}: (c) comparison quotes the right values", cmp_.group(0)[:60] if cmp_ else "missing")
    except Exception as err:
        report(False, who, f"ERROR {err}")

# ================================================================ Concept 2
# demos C2
for who, stmt, blk, n_expected in (("C2 demo", DEMO[1], BL["C2"].split("<b>Your turn.</b>")[0], 50),
                                   ("C2 your turn", YT[1], BL["C2"].split("<b>Your turn.</b>")[1], 40)):
    try:
        fr = freq_of(tables(stmt)[0], f"{who} statement")
        sample_table(tables(blk)[0], fr, ["f", "f_r", "xf_r", "x^2f_r"], f"{who} sample table")
        n, d, xb, sx2, s2 = sample_stats(fr)
        report(n == n_expected and re.search(r"Divide each frequency by (\d+)", blk).group(1) == str(n), f"{who}: n = {n}", "")
        g = grab(blk, r"\(\bar{x}=@\), &ensp;\(s^2=@-@^2=@\), &ensp;\(s=\sqrt{@}\doteqdot@\)", who)
        report(val(g[0]) == xb and val(g[1]) == sx2 and val(g[2]) == xb and val(g[3]) == s2 and val(g[4]) == s2
               and F(g[5]) == r_float(sqrt_f(s2), 2), f"{who}: x-bar, s^2, s", str(g))
        report("survey" in blk.split("<b>b</b>")[0], f"{who}: (a) survey", "")
    except Exception as err:
        report(False, who, f"ERROR {err}")
report("A school of 800 students chooses 50 students at random" in DEMO[1] and "only 50 of the 800 students" in BL["C2"], "C2 demo: 50 of 800 (statement and answer agree)", "")
report("Forty visitors answer" in YT[1], "C2 your turn: forty visitors (n = 40)", "")

# Worked example 8: exoplanets
we8 = WORK[1][1]
try:
    tb = tables(we8)[0]
    fr = freq_of(tb, "WE8")
    n, d, xb, ex2, s2 = sample_stats(fr)
    report(n == 2527 and sum(x * f for x, f in fr.items()) == 3457 and "3457 known planets orbiting 2527 single stars" in we8, "WE8: 2527 stars, 3457 planets (statement and table)", "")
    sample_table(tb, fr, ["f", "xf", "f_r", "xf_r", "x^2f_r"], "WE8 table (book rounding to 4 dp of the exact values)", rnd=4)
    value(we8, r"\(\begin{aligned}[t]\bar{x}&amp;=\textstyle\sum xf_r\\&amp;\doteqdot@\text{ planets}\end{aligned}\)", r_half(xb, 2), "WE8: x-bar ~ 1.37")
    g = grab(we8, r"\(\begin{aligned}[t]s^2&amp;=\textstyle\sum x^2f_r-\bar{x}^2\\&amp;=@-@^2\\&amp;\doteqdot@\end{aligned}\)", "WE8 s^2")
    report(F(g[0]) == r_half(ex2, 4) and F(g[1]) == r_half(xb, 4) and F(g[2]) == r_half(s2, 2) == r_half(F(g[0]) - F(g[1]) ** 2, 2), "WE8: s^2 = 2.5235 - 1.3680^2 ~ 0.65", str(g))
    sd_rounded(we8, r"&amp;\doteqdot@\text{ planets.}", s2, "WE8: s ~ 0.81")
except Exception as err:
    report(False, "WE8", f"ERROR {err}")

# ================================================================ Concept 3
for who, stmt, blk, n_expected in (("C3 demo", DEMO[2], BL["C3"].split("<b>Your turn.</b>")[0], 40),
                                   ("C3 your turn", YT[2], BL["C3"].split("<b>Your turn.</b>")[1], 25)):
    try:
        fr = freq_of(tables(stmt)[0], f"{who} statement")
        sample_table(tables(blk)[0], fr, ["f", "f_r", "xf_r", "x^2f_r"], f"{who} sample table")
        n, d, xb, sx2, s2 = sample_stats(fr)
        report(n == n_expected and re.search(r"Divide each frequency by (\d+)", blk).group(1) == str(n) and f"{n}" in stmt, f"{who}: n = {n}", "")
        g = grab(blk, r"\(\bar{x}=@\) @, &ensp;\(s^2=@-@^2=@\), &ensp;\(s=\sqrt{@}\doteqdot@\) ", who)
        report(val(g[0]) == xb and val(g[2]) == sx2 and val(g[3]) == xb and val(g[4]) == s2 and val(g[5]) == s2
               and F(g[6]) == r_float(sqrt_f(s2), 2), f"{who}: x-bar, s^2, s", str(g))
    except Exception as err:
        report(False, who, f"ERROR {err}")
# mice (from the text)
wem = WORK[2][1]
try:
    fr = freq_of(tables(wem)[0], "mice statement")
    tb = tables(wem)[1]
    report(freq_of(tb, "mice solution") == fr, "mice: solution frequencies = statement frequencies", "")
    sample_table(tb, fr, ["f", "xf", "f_r", "xf_r", "x^2f_r"], "mice table (exact fractions)")
    n, d, xb, ex2, s2 = sample_stats(fr)
    g = grab(wem, r"\(\begin{aligned}[t]\bar{x}&amp;=\textstyle\sum xf_r\\&amp;=@\\&amp;\doteqdot@\text{ baby mice}\end{aligned}\)", "mice x-bar")
    report(val(g[0]) == xb and F(g[1]) == r_half(xb, 2), "mice: x-bar = 555/121 ~ 4.59", str(g))
    g = grab(wem, r"\(\begin{aligned}[t]s^2&amp;=\textstyle\sum x^2f_r-\bar{x}^2\\&amp;=@-@\\&amp;\doteqdot@\end{aligned}\)", "mice s^2")
    report(val(g[0]) == ex2 and val(g[1]) == xb ** 2 and F(g[2]) == r_half(s2, 4), "mice: s^2 = 2917/121 - 308025/14641 ~ 3.0689", str(g))
    sd_rounded(wem, r"&amp;\doteqdot@\text{ baby mice.}", s2, "mice: s ~ 1.75")
    report("121 litters" in wem and "555 babies" in wem, "mice: sums labelled", "")
except Exception as err:
    report(False, "mice", f"ERROR {err}")
# rainy days (from the text)
wer = WORK[3][1]
try:
    tbs = tables(wer)
    fr = freq_of(tbs[0], "rainy-days statement")
    report(sum(fr.values()) == 2012 - 1913 + 1, "rainy days: 100 years from 1913 to 2012", str(sum(fr.values())))
    joined = split_tables(tbs[1:3])
    report(freq_of(joined, "rainy solution") == fr, "rainy days: solution frequencies = statement frequencies", "")
    sample_table(joined, fr, ["f", "f_r", "xf_r", "x^2f_r"], "rainy-days table (two halves, exact)")
    n, d, xb, ex2, s2 = sample_stats(fr)
    value(wer, r"\(\begin{aligned}[t]\bar{x}&amp;=\textstyle\sum xf_r\\&amp;=@\text{ rainy days}\end{aligned}\)", xb, "rainy: x-bar = 12.64")
    g = grab(wer, r"\(\begin{aligned}[t]s^2&amp;=\textstyle\sum x^2f_r-\bar{x}^2\\&amp;=@-@^2\\&amp;\doteqdot@\end{aligned}\)", "rainy s^2")
    report(val(g[0]) == ex2 and val(g[1]) == xb and F(g[2]) == r_half(s2, 2), "rainy: s^2 = 180.66 - 12.64^2 ~ 20.89", str(g))
    sd_rounded(wer, r"&amp;\doteqdot@\text{ rainy days.}", s2, "rainy: s ~ 4.57")
    RAINY = (n, xb, s2)
except Exception as err:
    report(False, "rainy days", f"ERROR {err}")
    RAINY = None

# ================================================================ Concept 4: correction factor
present(CON[3], r"a correction factor \(\tfrac{n}{n-1}\), where \(n\) is the size of the sample", "extension box")
present(CON[3], r"there were 100 results, and we were using a sample mean rather than a theoretical mean, so the correction factor is \(\tfrac{100}{99}\)", "extension box")
wec = WORK[4][1]
try:
    n, xb, s2 = RAINY
    value(wec, r"There were @ results, so the correction factor is \(\tfrac{@}{@}\).", (F(n), F(n), F(n - 1)), "correction WE: n and factor")
    value(wec, r"\(\begin{aligned}[t]\bar{x}&amp;=@\text{ rainy days}", xb, "correction WE: x-bar as before")
    g = grab(wec, r"\(\begin{aligned}[t]s^2&amp;=@\times\dfrac{@}{@}\\&amp;\doteqdot@\end{aligned}\)", "correction s^2")
    report(F(g[0]) == r_half(s2, 2) and val(g[1]) == n and val(g[2]) == n - 1 and F(g[3]) == r_half(F(g[0]) * n / (n - 1), 2), "correction WE: 20.89 x 100/99 ~ 21.10", str(g))
    sd_rounded(wec, r"&amp;\doteqdot@\text{ rainy days.}", F(g[0]) * n / (n - 1), "correction WE: s ~ 4.59")
    report(r_half(s2 * n / (n - 1), 2) == F(g[3]), "correction WE: same result from the unrounded s^2", "")
except Exception as err:
    report(False, "correction WE", f"ERROR {err}")
for who, stmt, blk in (("C4 demo", DEMO[3], BL["C4"].split("<b>Your turn.</b>")[0]), ("C4 your turn", YT[3], BL["C4"].split("<b>Your turn.</b>")[1])):
    try:
        n = int(re.search(r"A sample of (\d+)", stmt).group(1))
        s2 = F(re.search(r"variance \\\(s\^2=([\d.]+)\\\)", stmt).group(1))
        value(blk, r"The correction factor is \(\tfrac{@}{@}\).", (F(n), F(n - 1)), f"{who}: factor")
        g = re.search(r"\\\[\\text\{corrected variance\}=([\d.]+)\\times\\tfrac\{(\d+)\}\{(\d+)\}=([\d.]+),\\qquad\\text\{corrected standard deviation\}=\\sqrt\{?([\d.]+)\}?(=[\d.]+|\\doteqdot[\d.]+)\.\\\]", blk)
        if g is None:
            raise LookupError("corrected display not found")
        g = g.groups()
        cv = s2 * n / (n - 1)
        sdtxt = g[5]
        sd_ok = (F(sdtxt.lstrip("=")) == F(math.isqrt(cv.numerator)) and cv.denominator == 1 and math.isqrt(cv.numerator) ** 2 == cv.numerator) \
            if sdtxt.startswith("=") else F(sdtxt.replace("\\doteqdot", "")) == r_float(sqrt_f(cv), 2)
        report(F(g[0]) == s2 and val(g[1]) == n and val(g[2]) == n - 1 and F(g[3]) == cv and F(g[4]) == cv and sd_ok, f"{who}: corrected variance and sd", str(g))
        rx = re.search(r"\\\(s=\\sqrt\{([\d.]+)\}\\doteqdot([\d.]+)\\\)", blk)
        report(F(rx.group(1)) == s2 and F(rx.group(2)) == r_float(sqrt_f(s2), 2), f"{who}: uncorrected s", rx.group(0))
        if "mean of 1.8 goals" in stmt:
            report(F("1.8") == sample_stats(freq_of(tables(DEMO[2])[0], "C3"))[2] and s2 == sample_stats(freq_of(tables(DEMO[2])[0], "C3"))[4],
                   "C4 demo: data are the C3 demo's 40 matches (x-bar 1.8, s^2 1.56)", "")
    except Exception as err:
        report(False, who, f"ERROR {err}")

# ================================================================ Exercise 13D
dice3 = dist(product(range(1, 7), repeat=3), key=lambda o: sum(1 for v in o if v >= 5))
try:
    t = tables(TQ["1"])[0]
    report([cellval(c) for c in t[0][1:]] == list(dice3) and [cellval(c) for c in t[1][1:]] == list(dice3.values()), "Q1(a) table = enumeration of 6^3 throws", str(t[1][1:]))
    theory_table(tables(BH["1"])[0], dice3, ["p(x)", "xp(x)", "x^2p(x)"], "answer 1(a) table (p(2) = 6/27 as in the question)")
    mu, ex2, var = stats(dice3)
    g = grab(BH["1"], r"\(\mu=@\), &ensp;\(\sigma^2=@-1^2=@\), &ensp;\(\sigma\doteqdot@\)", "1a")
    report(val(g[0]) == mu and val(g[1]) == ex2 and val(g[2]) == var and F(g[3]) == r_float(sqrt_f(var), 2), "answer 1(a): mu, sigma^2, sigma", str(g))
    fr = freq_of(tables(TQ["1"])[1], "Q1(b)")
    sample_table(tables(BH["1"])[1], fr, ["f", "f_r", "xf_r", "x^2f_r"], "answer 1(b) table")
    n, d, xb, sx2, s2 = sample_stats(fr)
    g = grab(BH["1"], r"\(\bar{x}=@\), &ensp;\(s^2=@-(@)^2=@\), &ensp;\(s\doteqdot@\)", "1b")
    report(val(g[0]) == xb and val(g[1]) == sx2 and val(g[2]) == xb and val(g[3]) == s2 and F(g[4]) == r_float(sqrt_f(s2), 2), "answer 1(b): x-bar, s^2, s", str(g))
    report(xb < mu and "a little below" in BH["1"], "answer 1(c): sample mean 0.91 below mu = 1", "")
except Exception as err:
    report(False, "Q1", f"ERROR {err}")
dice2sum = dist(product(range(1, 7), repeat=2), key=lambda o: o[0] + o[1])
try:
    theory_table(tables(TQ["2"])[0], dice2sum, ["p(x)", "xp(x)", "(x-\\mu)^2", "(x-\\mu)^2p(x)"], "Q2(a) table = enumeration of 36 throws")
    mu, ex2, var = stats(dice2sum)
    g = grab(BH["2"], r"\(\mu=@\), &ensp;\(\sigma^2=@=@\), &ensp;\(\sigma\doteqdot@\)", "2a")
    report(val(g[0]) == mu and val(g[1]) == var and val(g[2]) == var and F(g[3]) == r_float(sqrt_f(var), 2), "answer 2(a)", str(g))
    report("72 times" in TQ["2"], "Q2(b): 72 throws", "")
except Exception as err:
    report(False, "Q2", f"ERROR {err}")
dice2diff = dist(product(range(1, 7), repeat=2), key=lambda o: abs(o[0] - o[1]))
try:
    t = tables(TQ["4"])[0]
    theory_table(t, dice2diff, ["p(x)", "xp(x)"], "Q4(c)(iii) table = enumeration of |difference|")
    theory_table(tables(BH["4"])[0], dice2diff, ["p(x)", "xp(x)", "x^2p(x)"], "answer 4(c)(iii) table")
    mu, ex2, var = stats(dice2diff)
    g = grab(BH["4"], r"\(\mu\doteqdot@\), &ensp;\(\sigma^2=@-\big(@\big)^2\), &ensp;\(\sigma\doteqdot@\)", "4c")
    report(F(g[0]) == r_half(mu, 2) and val(g[1]) == ex2 and val(g[2]) == mu and F(g[3]) == r_float(sqrt_f(var), 2), "answer 4(c)(iii): mu, sigma", str(g))
    report("39 <i>differences</i>" in TQ["4"] and "40 times" in TQ["4"], "Q4: 40 throws give 39 differences", "")
    report("Question 10 of Exercise 13B" in TQ["4"] and "Two dice are thrown. Let \\(X\\) be the difference" in read("l13b.html"), "Q4(c)(iii): cross-reference to Exercise 13B Q10 (difference of two dice)", "")
except Exception as err:
    report(False, "Q4", f"ERROR {err}")
for lo, hi, mtxt, vtxt in ((0, 9, r"\(\mu=4\tfrac12\) and \(\sigma^2=8\tfrac14\)", "0,1,\\dots,9"), (1, 8, r"\(\mu=4\tfrac12\) and \(\sigma^2=5\tfrac14\)", "1,2,\\dots,8")):
    d = {x: F(1, hi - lo + 1) for x in range(lo, hi + 1)}
    mu, ex2, var = stats(d)
    g = re.search(re.escape(vtxt) + r"\\\), where \\\(\\mu=([^\\]+\\tfrac\d+)\\\) and \\\(\\sigma\^2=([^\\]+\\tfrac\d+)\\\)", TQ["5"])
    report(g is not None and val(g.group(1)) == mu and val(g.group(2)) == var, f"Q5: uniform on {lo}..{hi}: mu {mu}, sigma^2 {var}", g.group(0)[:60] if g else "missing")
report("Question 12 of Exercise 13C" in TQ["5"] and "uniform" in read("l13c.html").split('q-num">12<')[1][:300], "Q5: cross-reference to Exercise 13C Q12 (uniform distribution)", "")
try:
    t = tables(TQ["7"])[0]
    xs = [int(c) for c in t[0][1:]]
    ps = [F(c.rstrip("%")) / 100 for c in t[1][1:]]
    report(xs == list(range(1, 10)) and sum(ps) == 1, "Q7: Benford percentages add to 100%", str(sum(ps)))
    d = dict(zip(xs, ps))
    mu, ex2, var = stats(d)
    g = grab(BH["7"], r"\(\mu=\sum xp(x)=@\), &ensp;\(\text{E}(X^2)=\sum x^2p(x)=@\), &ensp;\(\sigma^2=@-@^2\doteqdot@\), &ensp;\(\sigma\doteqdot@\)", "7a")
    report(F(g[0]) == mu and F(g[1]) == ex2 and F(g[2]) == ex2 and F(g[3]) == mu and F(g[4]) == r_half(var, 2) and F(g[5]) == r_float(sqrt_f(var), 2),
           "answer 7(a): mu = 3.441, sigma ~ 2.46", str(g))
    report(f"\\(2^d\\doteqdot6.8719\\times10^{{10}}\\), so \\(X=6\\)" in TQ["7"] and F("6.8719") == r_float(2 ** 36 / 10 ** 10, 4), "Q7(b): 2^36 ~ 6.8719 x 10^10, leading digit 6", "")
except Exception as err:
    report(False, "Q7", f"ERROR {err}")
# Q14: tank formula and diagram
try:
    k = int(re.search(r"The case \\\(k=(\d+)\\\)", TQ["14"]).group(1))
    m = int(re.search(r"and \\\(m=(\d+)\\\) is shown", TQ["14"]).group(1))
    Nest = m + F(m, k) - 1
    report(Nest == m + F(m - k, k), "Q14: m + (m - k)/k = m + m/k - 1", "")
    svg = open(os.path.join(SRC, "svg", "c13d_tank.svg"), encoding="utf-8").read()
    ticks = {int(t): float(x) for x, t in re.findall(r'<text x="([\d.]+)"[^>]*>(\d+)</text>', svg)}
    dots = sorted(float(x) for x in re.findall(r'<circle cx="([\d.]+)"', svg))
    lab = {t: float(x) for x, t in re.findall(r'<text x="([\d.]+)"[^>]*font-style="italic"[^>]*>([mN])</text>', svg)}
    crosses = sorted({round((float(a) + float(b)) / 2, 1) for a, b in re.findall(r'<line x1="([\d.]+)" y1="[\d.]+" x2="([\d.]+)" y2="[\d.]+" stroke="#e11d48"', svg)})
    found = sorted(n for n, x in ticks.items() if any(abs(x - c) < 0.5 for c in crosses))
    report(sorted(ticks) == list(range(1, 13)) and len(found) == k and max(found) == m, f"Q14 diagram: {k} discovered serials {found}, largest m = {m}", "")
    report([n for n, x in ticks.items() if any(abs(x - c) < 0.5 for c in dots)] == [1, Nest] and abs(lab["m"] - ticks[m]) < 0.5 and abs(lab["N"] - ticks[Nest]) < 0.5,
           f"Q14 diagram: dots at 1 and N = {Nest} (the formula's estimate), labels m and N placed", "")
    present(BH["14"], r"\[N=m+\frac{m-k}{k}=m+\frac{m}{k}-1\]", "answer 14(b)")
except Exception as err:
    report(False, "Q14", f"ERROR {err}")
# random numbers vs the book's text layer
try:
    import pymupdf
    book = pymupdf.open(BOOK)
    rows = []
    for pg in (682, 683):
        ws = [w for w in book[pg].get_text("words") if re.fullmatch(r"\d{5}", w[4])]
        rr = {}
        for w in ws:
            rr.setdefault(round(w[1]), []).append(w)
        rows += [[w[4] for w in sorted(rr[y], key=lambda w: w[0])] for y in sorted(rr)]
    printed = tables(hw, "rn")
    printed = printed[0] if len(printed) == 1 else None
    report(printed == rows and sum(len(r) for r in rows) == 1000, "random-number table = the book's PDF 683-684 group by group", f"{sum(len(r) for r in rows)} groups, {len(rows)} rows")
except Exception as err:
    report(False, "random numbers", f"ERROR {err}")

# ================================================================ past paper
LABEL = "Blacktown Boys’ High School, 2024, HSC Trial Examination, Mathematics <span style=\"white-space:nowrap\">Extension&nbsp;1,&nbsp;Q2</span>"
report(ppl.count(LABEL) == 1 and a_pp.count(LABEL) == 1, "PP 1: label identical in both files", "")
report('<span class="mk">1 mark</span>' in ppl and "<b>1 mark</b>" in ppl and "<b>Suggested time: 5 minutes</b>" in ppl and ppl.count('<div class="hint">') == 1,
       "PP: 1 mark, 5 minutes, one hint", "")
try:
    n = int(re.search(r"rolled (\d+) times", ppl).group(1))
    k_max = int(re.search(r"at most (\d+) of the rolls", ppl).group(1))
    target = {k for k in range(n + 1) if k <= k_max}
    full = re.findall(r"<span>([A-D])\. \\\(P\\left\(\\hat\{p\}(\\le|\\ge)\\dfrac(\d)(\d)\\right\)\\\)</span>", ppl)
    ev = {L: {k for k in range(n + 1) if (F(k, n) <= F(int(a), int(b)) if op == "\\le" else F(k, n) >= F(int(a), int(b)))} for L, op, a, b in full}
    right = [L for L in ev if ev[L] == target]
    report(len(full) == 4 and right == ["B"] and "<b>Answer B.</b>" in a_pp, "PP: only option B gives the event 'at most 12 of 18'", str(right))
    report(ev["D"] == {k for k in range(n + 1) if k >= k_max}, "PP: option D is 'at least 12' (as the solution says)", "")
    value(a_pp, r"\(\hat{p}=\tfrac{12}{18}=@\)", F(12, 18), "PP: 12/18 = 2/3")
    present(a_pp, r"The probability is \(P\big(\hat{p}\le\tfrac23\big)\).", "PP: final expression")
except Exception as err:
    report(False, "PP", f"ERROR {err}")

# ================================================================ review
try:
    sums = []
    for t in tables(RQ["2"]):
        sums.append(sum(cellval(c) for c in t[1][1:]))
    report([s == 1 for s in sums] == [True, False, False] and "<b>a</b> Yes" in BR["2"], "review 2: a is a distribution, b and c are not", str(sums))
    g = re.search(r"<b>b</b> No \(the probabilities add to ([\d.]+)\)", BR["2"])
    report(g is not None and F(g.group(1)) == sums[1], "review 2(b): sum 1.2", str(sums[1]))
    g = re.search(r"add to \\\(\\tfrac\{(\d+)\}\{(\d+)\}\\\)", BR["2"])
    report(g is not None and F(int(g.group(1)), int(g.group(2))) == sums[2], "review 2(c): sum 19/24", str(sums[2]))
    t = tables(RQ["3"])[0]
    ps = [cellval(c) for c in t[1][1:]]
    report(min(ps) < 0 and sum(ps) != 1 and max(ps) > 1, "review 3: a negative probability, sum not 1, a probability above 1", str(ps))
    for part, t in zip("ab", tables(RQ["4"])):
        d = {cellval(x): cellval(p) for x, p in zip(t[0][1:-1], t[1][1:-1])}
        row = re.search(rf"<b>{part}</b> The \\\(xp\(x\)\\\) row is (.*?), so \\\(\\text{{E}}\(X\)=([^\\]+)\\\)", BR["4"])
        cells = [val(c.strip().replace("\\(", "").replace("\\)", "")) for c in row.group(1).split(",")]
        report(cells == [x * p for x, p in d.items()] and val(row.group(2)) == mom(d, 1), f"review 4({part}): xp(x) row and E(X) = {mom(d, 1)}", "")
    stmt = re.sub(r'<span style="white-space:nowrap">\\\(\\\$\\\)(\d+)</span>', r"$\1", RQ["5"])
    meals = [(int(c), F(int(a), int(b))) for c, a, b in re.findall(r"cost \$(\d+) and he rated it \\\(\\tfrac(\d)(\d)\\\)", stmt)]
    E5 = sum(c * p for c, p in meals)
    report(len(meals) == 4 and sum(p for _, p in meals) == 1, "review 5: four meals, ratings add to 1", str(meals))
    g = grab(BR["5"], r"\[\text{E}(X)=\frac{27\times4+32\times2+23\times1+25\times2}{9}=\frac{245}{9}\doteqdot@\]", "5a")
    report(F(245, 9) == E5 and F(g[0]) == r_half(E5, 2), "review 5(a): E = 245/9 ~ 27.22", str(g))
    report("27\\times4+32\\times2+23\\times1+25\\times2" in BR["5"] and all(f"{c}\\times{p.numerator}" in BR["5"] for c, p in meals), "review 5(a): numerator uses the printed prices and ratings", "")
    g = grab(BR["5"], r"\(52\times\tfrac{245}{9}\doteqdot@\)", "5b")
    report(F(g[0]) == r_half(52 * E5, 2) and "52 times a year" in RQ["5"], "review 5(b): 52 x 245/9 ~ 1415.56", str(g))
    D6 = [{cellval(x): cellval(p) for x, p in zip(t[0][1:-1], t[1][1:-1])} for t in tables(RQ["6"])]
    D7 = [{cellval(x): cellval(p) for x, p in zip(t[0][1:-1], t[1][1:-1])} for t in tables(RQ["7"])]
    report(D6 == D7, "review 7 uses the distributions of review 6", "")
    a6 = BR["6"].split("<b>b</b>")
    a7 = BR["7"].split("<b>b</b>")
    for i, part in enumerate("ab"):
        mu, ex2, var = stats(D6[i])
        g = re.search(r"\\\(\\text\{E\}\(X\)=([\d.]+)\\\), \\\(\\text\{Var\}\(X\)=([\d.]+)\\\), \\\(\\sigma(=|\\doteqdot)([\d.]+)\\\)", a6[i])
        sd = sqrt_f(var)
        report(F(g.group(1)) == mu and F(g.group(2)) == var and (F(g.group(4)) == F(str(sd)) if g.group(3) == "=" else F(g.group(4)) == r_float(sd, 2)),
               f"review 6({part}): E {mu}, Var {var}", g.group(0))
        g = re.search(r"\\\(\\text\{E\}\(X\)=([\d.]+)\\\), \\\(\\text\{E\}\(X\^2\)=([\d.]+)\\\), \\\(\\text\{Var\}\(X\)=([\d.]+)\\\)", a7[i])
        report(F(g.group(1)) == mu and F(g.group(2)) == ex2 and F(g.group(3)) == var, f"review 7({part}): E, E(X^2), Var", g.group(0))
    a8 = BR["8"].split("<b>b</b>")
    for i, (part, t) in enumerate(zip("ab", tables(RQ["8"]))):
        d = {cellval(x): cellval(p) for x, p in zip(t[0][1:], t[1][1:])}
        report(sum(d.values()) == 1, f"review 8({part}): probabilities add to 1", "")
        mu, ex2, var = stats(d)
        g = re.search(r"\\\(\\text\{E\}\(X\)=([\d.]+)\\\), \\\(\\text\{Var\}\(X\)=([\d.]+)\\\), \\\(\\sigma(=|\\doteqdot)([\d.]+)\\\)", a8[i])
        sd = sqrt_f(var)
        report(F(g.group(1)) == mu and F(g.group(2)) == var and (abs(F(g.group(4)) - F(str(sd))) < F(1, 10 ** 9) if g.group(3) == "=" else F(g.group(4)) == r_float(sd, 2)),
               f"review 8({part}): E {mu}, Var {var}, sigma {sd:.4f}", g.group(0))
    E0, V0 = (F(int(v)) for v in re.search(r"\\\(\\text\{E\}\(X\)=(\d+)\\\) and \\\(\\text\{Var\}\(X\)=(\d+)\\\)", RQ["11"]).groups())
    X = sp.Symbol("X")
    for part, (a, b) in zip("abc", ((2, 0), (1, 5), (3, -1))):
        g = re.search(rf"<b>{part}</b> ([\d]+), ([\d]+), \\\(([^\\]*)(\\sqrt2)?\\\)", BR["11"])
        sd_print = (int(g.group(3)) if g.group(3) else 1) * math.sqrt(2)
        report(F(g.group(1)) == a * E0 + b and F(g.group(2)) == a * a * V0 and abs(sd_print - a * math.sqrt(V0)) < 1e-12, f"review 11({part}): E, Var, sigma of {a}X{b:+d}", g.group(0))
    report(r"\(\text{E}(3X-1)\)" in RQ["11"] and r"\(\text{E}(X+5)\)" in RQ["11"] and r"\(\text{E}(2X)\)" in RQ["11"], "review 11: the three transforms 2X, X + 5, 3X - 1", "")
    ss = [int(v) for v in re.search(r"\\\(\\\{([\d,]+)\\\}\\\)", RQ["12"]).group(1).split(",")]
    d = {x: F(1, len(ss)) for x in ss}
    mu, ex2, var = stats(d)
    t = tables(BR["12"])[0]
    report([cellval(c) for c in t[0][1:]] == ss and [cellval(c) for c in t[1][1:]] == list(d.values()), "review 12(a): uniform table on {5,...,9}", "")
    g = re.search(r"\\\(\\text\{E\}\(X\)=(\d+)\\\), \\\(\\text\{Var\}\(X\)=(\d+)\\\), \\\(\\sigma=\\sqrt(\d)\\\)", BR["12"])
    report(F(g.group(1)) == mu and F(g.group(2)) == var and F(int(g.group(3))) == var, "review 12(a): E 7, Var 2, sigma sqrt 2", g.group(0))
    report(r"\(\text{Var}(X)=\text{E}\big((X-\mu)^2\big)\)" in RQ["6"], "review 6: definition printed as E((X - mu)^2)", "")
except Exception as err:
    report(False, "review", f"ERROR {err}")

# ================================================================ figures
try:
    sys.path.insert(0, SRC)
    import figs                                    # noqa: E402
    rec = {}
    figs.dist_graph = lambda name, xs, ps, yt, **kw: rec.__setitem__(name, (list(xs), [F(p) for p in ps], kw))
    figs.save = lambda name, g: None
    figs.build_13d()
    fr = freq_of(tables(WORK[0][1])[0], "four-coin sample")
    report(rec["c13d_sample"][0] == list(fr) and rec["c13d_sample"][1] == [F(f, 100) for f in fr.values()], "figure c13d_sample = relative frequencies of the authors' sample", "")
    report(rec["a13d_q1a"][0] == list(dice3) and rec["a13d_q1a"][1] == list(dice3.values()), "figure a13d_q1a = Q1(a) distribution", "")
    fr1 = freq_of(tables(TQ["1"])[1], "Q1b")
    report(rec["a13d_q1b"][0] == list(fr1) and rec["a13d_q1b"][1] == [F(f, 100) for f in fr1.values()], "figure a13d_q1b = Q1(b) relative frequencies", "")
    report("{{svg:c13b_coins}}" in CON[0] and "{{svg:c13d_sample}}" in WORK[0][1] and "{{svg:c13d_tank}}" in TQ["14"]
           and "{{svg:a13d_q1a}}" in BH["1"] and "{{svg:a13d_q1b}}" in BH["1"], "figures placed", "")
except Exception as err:
    report(False, "figures", f"ERROR {err}")

# ================================================================ text checks
report("$" not in re.sub(r"\\\$", "", les + ans), "no literal dollar sign", "")
report("—" not in re.sub(r"<td>—</td>", "", les.split("<!-- ============ Past papers")[0].split('<div class="bt">Approaching')[0]), "no em dash in lesson prose (table dashes allowed)", "")

print(f"\n{NCHECK[0]} checks, {len(FAILS)} failed")
sys.exit(1 if FAILS else 0)
