"""Check of Lesson 15B (Y11 Ch 15 pack): Further binomial expansions.

The script reads the values PRINTED in workspace/build/y11ch15/a_15b.html (lesson examples,
textbook homework, past-paper worked solutions) and in l15b.html (the column expansions of
(x + y)^n, the tip-box example, worked examples 6-8, the results printed inside textbook
questions, the past-paper questions and options). Each value is found with a template ('@'
marks the printed LaTeX); a template must match exactly once in its block, otherwise the
item FAILS. The printed LaTeX is converted to a sympy expression and compared with an
independent computation:
  - expansions are built by repeated multiplication (sympy expand of the product of n
    brackets), not from a coefficient formula;
  - every printed row of Pascal's triangle is compared with math.comb;
  - coefficients, terms and equations are recomputed with sympy (coeff, solve, limit);
  - decimal approximations are recomputed with exact rationals and rounded.
It also checks the lesson fragment: past-paper marks add to the intro total (15-22), time
is 1.5 x marks rounded to 5 minutes, numbering and source labels match in both files, one
hint per question, and the MC letter is the one option equal to the computed value.

Exit status 1 if anything fails. Run: python3 workspace/checks/y11ch15_15b.py
"""
import os
import re
import sys
from fractions import Fraction
from math import comb

import sympy as sp
from sympy.parsing.sympy_parser import (parse_expr, standard_transformations,
                                        implicit_multiplication_application)

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.environ.get("Y11CH15_SRC", os.path.join(HERE, "..", "build", "y11ch15"))
FAILS = []
x, y, z, a, b, h, p, q, r, s, m, n = sp.symbols("x y z a b h p q r s m n")
SYMS = {"x": x, "y": y, "z": z, "a": a, "b": b, "h": h, "p": p, "q": q, "r": r, "s": s,
        "m": m, "n": n, "sqrt": sp.sqrt, "binomial": sp.binomial}
TR = standard_transformations + (implicit_multiplication_application,)


def read(name):
    with open(os.path.join(SRC, name), encoding="utf-8") as f:
        return f.read()


def report(ok, label, detail):
    print(("OK       " if ok else "MISMATCH ") + label.replace("\n", " ") + "  " + detail.replace("\n", " "))
    if not ok:
        FAILS.append(label)


# ---------------------------------------------------------------- LaTeX -> sympy
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
        if t.startswith(("\\dfrac", "\\tfrac", "\\frac"), i):
            i = t.index("frac", i) + 4
            u, i = _arg(t, i)
            v, i = _arg(t, i)
            out.append(f"(({_conv(u)})/({_conv(v)}))")
        elif t.startswith("\\sqrt", i):
            u, i = _arg(t, i + 5)
            out.append(f" sqrt({_conv(u)})")
        elif t.startswith("\\boxed", i):
            u, i = _arg(t, i + 6)
            out.append(f"({_conv(u)})")
        elif t.startswith("\\times", i):
            out.append("*")
            i += 6
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


def clean(t):
    t = re.sub(r"\\left|\\right|\\bigg|\\Big|\\big|\\qquad|\\quad|\\,|\\;|\\!|&nbsp;|\s", "", t)
    return re.sub(r"[+-]?\\cdots", "", t).replace("{}", "")


def tex(t):
    """Printed LaTeX -> sympy expression."""
    return parse_expr(_conv(clean(t)), local_dict=dict(SYMS), transformations=TR)


def same(u, v):
    return sp.simplify(sp.expand(u - v)) == 0


def power(base, k):
    """(base)^k by repeated multiplication."""
    res = sp.Integer(1)
    for _ in range(k):
        res = sp.expand(res * base)
    return res


def deg(t, var):
    return sp.degree(t * var ** 60, var) - 60


def term(e, j, var=x):
    """The term in var^j of an expansion (as an expression)."""
    return sp.Add(*[t for t in sp.Add.make_args(sp.expand(e)) if deg(t, var) == j])


def trunc(e, d, var=x):
    """Terms of degree <= d (an ascending expansion as far as var^d)."""
    return sp.Add(*[t for t in sp.Add.make_args(sp.expand(e)) if deg(t, var) <= d])


def top(e, d, var=x):
    """Terms of degree >= d (a descending expansion as far as var^d)."""
    return sp.Add(*[t for t in sp.Add.make_args(sp.expand(e)) if deg(t, var) >= d])


# ---------------------------------------------------------------- HTML blocks
ans = read("a_15b.html")
les = read("l15b.html")
parts = ans.split('<div class="ans-sec">Past-Paper Homework - Worked Solutions</div>')
if len(parts) != 2:
    sys.exit("FAIL: past-paper solutions section not found exactly once in a_15b.html")
report(ans.count("{{ahead:Lesson 15B | Further binomial expansions}}") == 2, "answers headings", "{{ahead:Lesson 15B | ...}} twice")
pre = parts[0]
BLK = {}
for mt in re.finditer(r'<div class="a"><span class="an">([^<]+)</span><div class="ab">(.*?)(?=<div class="a"><span class="an">|<div class="ans-sec">|\{\{ahead|$)', pre, re.S):
    if mt.group(1) in BLK:
        report(False, f"block {mt.group(1)}", "duplicate answer number")
    BLK[mt.group(1)] = mt.group(2)
PPA = {int(k): v for k, v in re.findall(r'<div class="ppa"><div class="pp-src"><span><span class="pn">PP (\d+)</span>(.*?)(?=<div class="ppa">|$)', parts[1], re.S)}

pps = les.split("<!-- ============ Past papers ============ -->")
if len(pps) != 2:
    sys.exit("FAIL: past-paper section not found in l15b.html")
hw = les.split("<!-- ============ Homework ============ -->")[1].split("<!-- ============ Past papers")[0]
PPQ = {int(k): v for k, v in re.findall(r'<div class="pp"><div class="pp-src"><span><span class="pn">PP (\d+)</span>(.*?)(?=<div class="pp">|$)', pps[1], re.S)}
WORKED = {int(k): v for k, v in re.findall(r'<span class="tag">Worked example (\d+)</span>(.*?)(?=<div class="ex |<!-- =====|$)', les, re.S)}
TQ = {k: v for k, v in re.findall(r'<div class="q"><span class="q-num">(\d+)</span>(.*?)(?=<div class="q">|\{\{band|$)', hw, re.S)}
LES = {"tip": les.split('<div class="box tip">')[1].split("</div></div>")[0]}


def grab(block, template, where):
    pieces = template.split("@")
    cap = r"((?:(?!\\\)|\\\]|\\\\&).)+?)"    # one value: never crosses \) or \] or a new aligned row
    rx = "".join(re.escape(pc) + (cap if i < len(pieces) - 1 else "") for i, pc in enumerate(pieces))
    found = re.findall(rx, block, re.S)
    if len(found) != 1:
        raise LookupError(f"template matched {len(found)} times in {where}: {template!r}")
    return found[0] if isinstance(found[0], tuple) else (found[0],)


def src(kind, key):
    table = {"A": BLK, "PP": PPA, "W": WORKED, "Q": TQ, "PQ": PPQ, "L": LES}[kind]
    if key not in table:
        raise LookupError(f"{kind} {key} block missing")
    return table[key]


def check(kind, key, template, expected, mode="expr"):
    """expected: sympy expression, or a tuple matching the number of '@'."""
    label = f"{kind}{key} {template}"
    try:
        got = grab(src(kind, key), template, f"{kind} {key}")
        exp = expected if isinstance(expected, tuple) else (expected,)
        if len(exp) != len(got):
            raise ValueError("number of '@' does not match expected values")
        oks = []
        for g, e in zip(got, exp):
            if mode == "round":          # e = (exact value, decimals)
                val, dp = e
                oks.append(Fraction(g) == round(Fraction(val), dp) and len(g.split(".")[1]) == dp)
            else:
                oks.append(same(tex(g), e))
        report(all(oks), label, "printed " + " | ".join(got))
    except Exception as err:
        report(False, label, f"ERROR {err}")


def check_chain(kind, key, template, expected, min_sides=1, use_lhs=True):
    """Printed 'A=B=C': every side must equal expected. The literal left side written in the
    template just before '=@' (after the last \\( or \\[) is checked as one more side."""
    label = f"{kind}{key} {template}"
    try:
        (g,) = grab(src(kind, key), template, f"{kind} {key}")
        sides = [t for t in g.split("=") if t.strip()]
        lhs = re.split(r"\\\[|\\\(", template.split("@")[0])[-1]
        if use_lhs and lhs.endswith("=") and lhs[:-1].strip():
            sides.insert(0, lhs[:-1])
        report(len(sides) >= min_sides and all(same(tex(t), expected) for t in sides), label, f"printed {g}")
    except Exception as err:
        report(False, label, f"ERROR {err}")


def check_set(kind, key, template, expected):
    """Several '@' values: as a set, equal to the expected set of solutions."""
    label = f"{kind}{key} {template}"
    try:
        got = grab(src(kind, key), template, f"{kind} {key}")
        vals = {tex(g) for g in got}
        report(vals == set(expected) and len(got) == len(set(expected)), label, f"printed {got}, solutions {set(expected)}")
    except Exception as err:
        report(False, label, f"ERROR {err}")


def check_powers(kind, key, template, e, count):
    """Printed list of the powers of x in the first terms of a descending expansion."""
    label = f"{kind}{key} {template}"
    try:
        (g,) = grab(src(kind, key), template, f"{kind} {key}")
        items = [t for t in re.split(r",\\ |,\s*", g.strip()) if t and "dots" not in t]
        printed = [int(sp.degree(tex(t) * x ** 60, x)) - 60 for t in items]
        degs = sorted({deg(t, x) for t in sp.Add.make_args(sp.expand(e))}, reverse=True)
        report(printed == degs[:count] and len(printed) == count, label, f"printed {printed}, expansion powers {degs[:count]}")
    except Exception as err:
        report(False, label, f"ERROR {err}")


# ================================================================ rows of Pascal's triangle printed anywhere
for name, txt in (("l15b.html", les), ("a_15b.html", ans)):
    rows = re.findall(r"Row (\d+)(?: of Pascal's triangle)? is ((?:\d+, )*\d+)", txt)
    bad = [nn for nn, vals in rows if [int(v) for v in vals.split(", ")] != [comb(int(nn), k) for k in range(int(nn) + 1)]]
    report(not bad and len(rows) >= (4 if name == "l15b.html" else 9), f"{name} Pascal rows", f"{len(rows)} rows printed, wrong: {bad}")

# ================================================================ lesson concept 1: (x + y)^n in columns
cols = re.findall(r"\\\[\(x\+y\)\^(\d)=x\(x\+y\)(?:\^(\d))?\+y\(x\+y\)(?:\^(\d))?\\\]\s*\\\[\\begin\{alignedat\}\{\d\}(.*?)\\end\{alignedat\}\\\]", les, re.S)
report(sorted(int(c_[0]) for c_ in cols) == [2, 3, 4], "lesson column expansions found", f"n = {[c_[0] for c_ in cols]}")
for k, e1_, e2_, body in cols:
    k = int(k)
    try:
        hdr_ok = int(e1_ or 1) == k - 1 and int(e2_ or 1) == k - 1
        rw = [re.sub(r"[&=]", "", row).replace("{}", "") for row in body.split(r"\\")]
        t1, t2, t3 = (tex(v) for v in rw)
        ok = (hdr_ok and same(t1, x * power(x + y, k - 1)) and same(t2, y * power(x + y, k - 1))
              and same(t3, power(x + y, k)) and same(t1 + t2, t3) and len(sp.Add.make_args(t3)) == k + 1)
        # homogeneous of degree k: indices add to k in every term
        ok &= all(sp.Poly(t, x, y).total_degree() == k for t in sp.Add.make_args(t3))
        report(ok, f"lesson (x+y)^{k} in columns", " | ".join(rw))
    except Exception as err:
        report(False, f"lesson (x+y)^{k} in columns", f"ERROR {err}")
try:
    boxed = [int(v) for v in re.findall(r"\\boxed\{(\d+)\}", les)]
    e3 = power(x + y, 3)
    report(boxed == [1, 3, 4] and sp.Poly(e3, x, y).coeff_monomial(x * y ** 2) + sp.Poly(e3, x, y).coeff_monomial(y ** 3) == 4 == sp.Poly(power(x + y, 4), x, y).coeff_monomial(x * y ** 3),
           "lesson boxed 1 + 3 = 4", f"{boxed}")
except Exception as err:
    report(False, "lesson boxed", f"ERROR {err}")
check("L", "tip", r"in brackets</b>: \((2-3x)^4=@+\cdots\)", trunc(power(2 - 3 * x, 4), 1))

# lesson questions really are the ones answered (each appears once in l15b.html)
for qs in (r"<b>a</b> \((3-2x)^4\)", r"\(\big(2x+\tfrac12a\big)^5\)", r"<b>a</b> \((2-5x)^3\)", r"\(\big(3x+\tfrac13a\big)^4\)",
           r"expansion of \(\big(x+3x^{-2}\big)^6\)", r"expansion of \(\big(x+2x^{-1}\big)^4\)",
           r"Expand \((3-2x)^6\) as far as the term in \(x^2\)", r"\((4+x)(3-2x)^6\)",
           r"Expand \((2-x)^5\) as far as the term in \(x^2\)", r"\((3+x)(2-x)^5\)"):
    report(les.count(qs) == 1, "lesson question", f"{qs} appears {les.count(qs)} time(s)")

# ================================================================ worked examples 6-8 (textbook Examples 6-8)
check("W", 6, r"\[\begin{aligned}(2-3x)^4&=@\\&=@.\end{aligned}\]", (power(2 - 3 * x, 4), power(2 - 3 * x, 4)))
try:
    body = re.search(r"\\big\(5x\+\\tfrac15a\\big\)\^5&=(.*?)\\end\{aligned\}", WORKED[6], re.S).group(1)
    rw = [re.sub(r"^&=?|\.$", "", t.strip()) for t in body.split("\\\\")]
    e6b = power(5 * x + a / 5, 5)
    report(len(rw) == 3 and same(tex(rw[0]) + tex(rw[1]), e6b) and same(tex(rw[2]), e6b), "W6 b", " | ".join(rw))
except Exception as err:
    report(False, "W6 b", f"ERROR {err}")
e7 = power(2 * x + x ** -2, 6)
try:
    body = re.search(r"\\big\(2x\+x\^\{-2\}\\big\)\^6&=(.*?)\\end\{aligned\}", WORKED[7], re.S).group(1)
    rw = [re.sub(r"^&", "", t.strip()) for t in body.split("\\\\")]
    report(len(rw) == 2 and same(tex(rw[0]) + tex(rw[1]), e7), "W7 unsimplified expansion", " | ".join(rw))
except Exception as err:
    report(False, "W7 expansion", f"ERROR {err}")
for lead, j in ((r"<b>a</b> The constant term is</p>", 0), (r"<b>b</b> The term in \(x^{-3}\) is</p>", -3)):
    try:
        blk = WORKED[7].split(lead)[1]
        body = re.search(r"\\begin\{aligned\}(.*?)\\end\{aligned\}", blk, re.S).group(1)
        rw = [re.sub(r"^&=?|\.$", "", t.strip()) for t in body.split("\\\\")]
        report(len(rw) == 3 and all(same(tex(t), term(e7, j)) for t in rw), f"W7 term in x^{j}", " | ".join(rw))
    except Exception as err:
        report(False, f"W7 term in x^{j}", f"ERROR {err}")
e8 = power(2 - 3 * x, 7)
check("W", 8, r"\[\begin{aligned}(2-3x)^7&=@\\&=@\end{aligned}\]", (trunc(e8, 2), trunc(e8, 2)))
check_chain("W", 8, r"\[\begin{aligned}&5\times6048x^2-x\times1344x\\&=@.\end{aligned}\]", term(sp.expand((5 + x) * e8), 2), use_lhs=False)
report(same(tex(r"5\times6048x^2-x\times1344x"), term(sp.expand((5 + x) * e8), 2)), "W8 products", "5 x 6048x^2 - x x 1344x")

# ================================================================ results printed inside textbook questions
check("Q", "5", r"\(5^6+5^5\times3^3+5^3\times3^5+3^6=@\)", tex(r"5^6+5^5\times3^3+5^3\times3^5+3^6"))
e5 = sp.expand(power(x + y, 6) + power(x - y, 6))
report(e5.subs({x: 5, y: 3}) == 2 * (5 ** 6 + 5 ** 5 * 3 ** 3 + 5 ** 3 * 3 ** 5 + 3 ** 6) and (5 + 3) ** 6 + (5 - 3) ** 6 == 2 * 2 ** 5 * (2 ** 12 + 1),
       "Q5b identity from (x+y)^6 + (x-y)^6 at x = 5, y = 3", "")
check("Q", "8", r"\(\big(3+\sqrt5\big)^6+\big(3-\sqrt5\big)^6=@\)", sp.expand(power(3 + sp.sqrt(5), 6) + power(3 - sp.sqrt(5), 6)))
try:
    (lhs, rhs) = grab(TQ["9"], r"Show that \(@=@\) by", "Q 9")
    s3 = sp.sqrt(3)
    report(same(tex(lhs), 1 / (s3 - 1) ** 4 + 1 / (s3 + 1) ** 4) and same(tex(rhs), tex(lhs)), "Q9 printed identity", "both sides equal")
except Exception as err:
    report(False, "Q9 identity", f"ERROR {err}")
e13 = power(m * a + n / a ** 2, 6)
try:
    (rat,) = grab(TQ["13"], r"Prove that \(m^2:n^2=@\)", "Q 13")
    u, v = [int(t) for t in rat.split(":")]
    c3, cm3 = e13.coeff(a, 3), e13.coeff(a, -3)      # 6 m^5 n and 20 m^3 n^3
    report(sp.simplify((c3 - cm3) / (2 * m ** 3 * n)) == 3 * m ** 2 - 10 * n ** 2 and Fraction(u, v) == Fraction(10, 3), "Q13 printed ratio", f"{rat}; coefficients {c3}, {cm3}")
except Exception as err:
    report(False, "Q13 ratio", f"ERROR {err}")

# ================================================================ lesson examples (C1-C3)
check("A", "C1", r"<b>a</b> \((3-2x)^4=@\)", power(3 - 2 * x, 4))
check("A", "C1", r"<b>b</b> \(\big(2x+\tfrac12a\big)^5=@\)", power(2 * x + a / 2, 5))
check("A", "C1", r"<b>a</b> \((2-5x)^3=@\)", power(2 - 5 * x, 3))
check("A", "C1", r"<b>b</b> \(\big(3x+\tfrac13a\big)^4=@\)", power(3 * x + a / 3, 4))
ed, ey = power(x + 3 * x ** -2, 6), power(x + 2 * x ** -1, 4)
check("A", "C2", r"<b>Tutor demo.</b> \(\big(x+3x^{-2}\big)^6=@\)", ed)
for templ, e, j in ((r"<b>a</b> \(@\) &nbsp; <b>b</b> \(20", ed, 0), (r"<b>b</b> \(@\)<br>", ed, -3),
                    (r"<b>a</b> \(@\) &nbsp; <b>b</b> \(4", ey, 0), (r"<b>b</b> \(@\)</div>", ey, -2)):
    check_chain("A", "C2", templ, term(e, j), 2)
check("A", "C2", r"<b>Your turn.</b> \(\big(x+2x^{-1}\big)^4=@\)", ey)
for templ, e, other in ((r"<b>Tutor demo.</b> \((3-2x)^6=@\), so the term in \(x^2\) is \(@\)", power(3 - 2 * x, 6), 4 + x),
                        (r"<b>Your turn.</b> \((2-x)^5=@\), so the term in \(x^2\) is \(@\)", power(2 - x, 5), 3 + x)):
    try:
        g1, g2 = grab(BLK["C3"], templ, "C3")
        ok = same(tex(g1), trunc(e, 2)) and all(same(tex(t), term(sp.expand(other * e), 2)) for t in g2.split("="))
        report(ok and len(g2.split("=")) == 2, f"AC3 {templ[:30]}", f"printed {g1} | {g2}")
    except Exception as err:
        report(False, "AC3", f"ERROR {err}")

# ================================================================ textbook homework answers
Q1 = {"a": power(x + y, 4), "b": power(x - y, 4), "c": power(r - s, 6), "d": power(p + q, 10), "e": power(a - b, 9),
      "f": power(2 * x + y, 5), "g": power(p - 2 * q, 7), "h": power(3 * x + 2 * y, 4), "i": power(a - b / 2, 3),
      "j": power(r / 2 + s / 3, 5), "k": power(x + 1 / x, 6)}
for part, e in Q1.items():
    check("A", "1", rf"<b>{part}</b> \(@\)</div>", e)
Q2 = {"a": power(1 + x ** 2, 4), "b": power(1 - 3 * x ** 2, 3), "c": power(x ** 2 + 2 * y ** 3, 6), "d": power(x - 1 / x, 9),
      "e": power(sp.sqrt(x) + sp.sqrt(y), 7), "f": power(2 / x + 3 * x ** 2, 5)}
for part, e in Q2.items():
    check("A", "2", rf"<b>{part}</b> \(@\)</div>", e)
Q3 = {"a": y ** 5 + 5 * y ** 4 * (x - y) + 10 * y ** 3 * (x - y) ** 2 + 10 * y ** 2 * (x - y) ** 3 + 5 * y * (x - y) ** 4 + (x - y) ** 5,
      "b": a ** 4 - 4 * a ** 3 * (a - b) + 6 * a ** 2 * (a - b) ** 2 - 4 * a * (a - b) ** 3 + (a - b) ** 4,
      "c": x ** 3 + 3 * x ** 2 * (2 * y - x) + 3 * x * (2 * y - x) ** 2 + (2 * y - x) ** 3,
      "d": sum(sp.binomial(6, k) * (-1) ** k * (x + y) ** (6 - k) * (x - y) ** k for k in range(7))}
# the lesson's Q3 statement is the expression checked here
try:
    for part in "abc":
        (g,) = grab(TQ["3"], rf'<span class="pl">{part}</span>\(@\)</span>', "Q 3")
        report(same(tex(g), Q3[part]), f"Q3{part} statement", g)
    (g1, g2) = grab(TQ["3"], r'<span class="pl">d</span>\(@\)<br>\(@\)</span>', "Q 3")
    report(same(tex(g1) + tex(g2), Q3["d"]), "Q3d statement", g1 + " " + g2)
except Exception as err:
    report(False, "Q3 statement", f"ERROR {err}")
for part, templ in (("a", r"<b>a</b> \(@\) &nbsp;"), ("b", r"<b>b</b> \(@\)<br>"), ("c", r"<b>c</b> \(@\) &nbsp;"), ("d", r"<b>d</b> \(@\)</div>")):
    check_chain("A", "3", templ, sp.expand(Q3[part]), 2)
for part, base, d, other, var in (("a", 4 + x, 3, 3 - x, x), ("b", 1 - 2 * x, 4, 1 - 3 * x, x), ("c", 3 - y, 4, (1 - y) ** 2, y)):
    k = {"a": 5, "b": 6, "c": 7}[part]
    e = power(base, k)
    check("A", "4", rf"<b>{part}</b> (i) \(@\) (ii) \(@\)", (trunc(e, d, var), sp.expand(other * e).coeff(var, d)))
check("A", "5", r"<b>a</b> \(@\)", e5)
Q6 = {"a": sp.expand((2 - 5 * x) * power(x ** 2 - 3, 4)).coeff(x, 3), "b": sp.expand((x ** 2 - 3 * x + 11) * power(4 + x ** 3, 3)).coeff(x, 5),
      "c": sp.expand(power(3 - 2 * x, 2) * power(x + 2 / x, 5)).coeff(x, 0), "d": sp.expand(power(x + 2, 3) * power(x - 2, 7)).coeff(x, 9)}
for part, v in Q6.items():
    check("A", "6", rf"<b>{part}</b> \(@\)", v)
check("A", "7", r"<b>a</b> (i) \(@\) (ii) \(@\) (iii) \(@\)",
      (power(x + h, 3), sp.expand(power(x + h, 3) - x ** 3), sp.limit((power(x + h, 3) - x ** 3) / h, h, 0)))
check("A", "7", r"<b>b</b> \(@\)", sp.limit((power(x + h, 5) - x ** 5) / h, h, 0))
check("A", "8", r"<b>b</b> \(@\)", sp.expand(power(2 + sp.sqrt(7), 4) + power(2 - sp.sqrt(7), 4)))
check("A", "8", r"<b>c</b> \(@\)", sp.expand(power(sp.sqrt(6) + sp.sqrt(3), 3) - power(sp.sqrt(6) - sp.sqrt(3), 3)) / sp.sqrt(3))
check("A", "9", r"\(@\)", sp.nsimplify(sp.simplify(1 / (sp.sqrt(3) - 1) ** 4 + 1 / (sp.sqrt(3) + 1) ** 4)))
e10 = power(x + 2 * y, 5)
for part, yy in (("a", Fraction(1, 100)), ("b", Fraction(-1, 100))):
    val = Fraction(str(e10.subs({x: 1, y: sp.Rational(yy.numerator, yy.denominator)})))
    report(val == (1 + 2 * yy) ** 5, f"A10{part} expansion value", f"{float(val)}")
    check("A", "10", rf"<b>{part}</b> \(@\)", ((val, 5),), mode="round")
for k, templ in ((3, r"<b>a</b> (i) \(@\)</div>"), (5, r"(ii) \(@\)</div>"), (7, r"(iii) \(@\)</div><div")):
    check("A", "11", templ, power(x + 1 / x, k))
xs = sp.solve(sp.Eq(x + 1 / x, 2), x)
check("A", "11", r"<b>b</b> (i) \(@\) (ii) \(@\) (iii) \(@\)</div>",
      tuple(sp.simplify(xs[0] ** k + xs[0] ** -k) for k in (3, 5, 7)) if len(xs) == 1 else (sp.nan,) * 3)
e12 = power(3 * x - a / x, 5)
s12 = [v for v in sp.solve(sp.Eq(e12.coeff(x, 1), 2 * e12.coeff(x, -3)), a) if v != 0]   # a = 0 makes the ratio undefined
check_set("A", "12", r"\(a=@\) or \(a=@\)", s12)
check("A", "14", r"<b>a</b> \(@\)</div>", power(x + 1 / x, 6))
try:
    A_, B_, C_ = grab(BLK["14"], r"<b>b</b> \(A=@\), \(B=@\) and \(C=@\).", "14")
    U = x + 1 / x
    A_, B_, C_ = tex(A_), tex(B_), tex(C_)
    report(same(power(U, 6) + A_ * power(U, 4) + B_ * power(U, 2) + C_, x ** 6 + x ** -6), "A14 b", f"A={A_}, B={B_}, C={C_}")
except Exception as err:
    report(False, "A14 b", f"ERROR {err}")
check("A", "15", r"<b>a</b> \(@\)<br>", power(x + y + z, 3))
check("A", "15", r"<b>b</b> \(@\)</div>", power(x + 1 + 1 / x, 4).coeff(x, 0))
report("{{svg:sierpinski}}" in BLK.get("16", "") and os.path.exists(os.path.join(SRC, "svg", "sierpinski.svg")), "A16 figure", "sierpinski.svg present")
# answered questions: the textbook prints no answer for 8(a), 13 (show / prove); 5(b) is a proof
report(sorted(BLK, key=lambda t: (len(t), t)) == ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "14", "15", "16", "C1", "C2", "C3"],
       "answer blocks", f"{sorted(BLK, key=lambda t: (len(t), t))}")
report(sorted(TQ, key=int) == [str(i) for i in range(1, 17)], "textbook questions 1-16", f"{sorted(TQ, key=int)}")

# ================================================================ past papers: structure
try:
    intro = re.search(r"Suggested time: (\d+) minutes</b></span><span><b>(\d+) marks", pps[1])
    marks = [int(v) for v in re.findall(r'<span class="mk">(\d+) marks?</span>', pps[1])]
    T, M = int(intro.group(1)), int(intro.group(2))
    report(sum(marks) == M and 15 <= M <= 22, "PP marks", f"PP marks {marks} sum {sum(marks)}, intro {M} (house rule: 15-22)")
    report(T == 5 * round(1.5 * M / 5), "PP time", f"{T} min for {M} marks")
    report(sorted(PPQ) == sorted(PPA) == list(range(1, len(PPQ) + 1)), "PP numbering", f"lesson {sorted(PPQ)}, answers {sorted(PPA)}")
    for k in PPQ:
        sq = re.search(r"^(.*?)</span>", PPQ[k]).group(1)
        sa = re.search(r"^(.*?)</span>", PPA[k]).group(1) if k in PPA else None
        report(sq == sa, f"PP{k} source label", sq)
        report(PPQ[k].count('<div class="hint">') == 1, f"PP{k} hint", "exactly one hint")
except Exception as err:
    report(False, "PP structure", f"ERROR {err}")


def mc(pp, expected, pattern):
    """The printed letter must be the one option whose value equals expected."""
    try:
        opts = dict(re.findall(pattern, PPQ[pp]))
        good = [L for L, v in opts.items() if same(tex(v), expected)]
        (letter,) = grab(PPA[pp], "<b>Answer (@).</b>", f"PP {pp}")
        report(len(opts) == 4 and good == [letter], f"PP{pp} MC letter", f"printed {letter}, option(s) equal to {expected}: {good}")
    except Exception as err:
        report(False, f"PP{pp} MC letter", f"ERROR {err}")


PAREN = r"<span>\(([A-D])\) \\\((.+?)\\\)</span>"
DOT = r"<span>([A-D])\. \\\((.+?)\\\)</span>"

# PP1 SGS 2021: coefficient of x^2 in (2x + 5)^6
e = power(2 * x + 5, 6)
check("PQ", 1, r"expansion of \(@\)?", (2 * x + 5) ** 6)
check_chain("PP", 1, r"\[15\times(2x)^2\times5^4=@.\]", term(e, 2), 3)
check("PP", 1, r"The coefficient is \(@\). <b>", e.coeff(x, 2))
mc(1, e.coeff(x, 2), PAREN)
# PP2 HAHS 2021: coefficient of x^4 in (x - sqrt2)^6
e = power(x - sp.sqrt(2), 6)
check("PP", 2, r"\[\big(x-\sqrt2\big)^6=@+\cdots\]", top(e, 4))
check_chain("PP", 2, r"The term in \(x^4\) is \(@\), because", term(e, 4), 2)
check("PP", 2, r"The coefficient is \(@\). <b>", e.coeff(x, 4))
mc(2, e.coeff(x, 4), DOT)
check_chain("PP", 2, r"because \(\big(-\sqrt2\big)^2=@\) is", sp.Integer(2), 2)
# PP3 HAHS 2023: coefficient of x in (2x^2 + 1/x)^5
e = power(2 * x ** 2 + 1 / x, 5)
check_chain("PP", 3, r"Write \(@\). Row 5", e, 2)
check_powers("PP", 3, r"down by 3: \(@\) The term", e, 4)
check_chain("PP", 3, r"\[10\times\big(2x^2\big)^2\times\big(x^{-1}\big)^3=@.\]", term(e, 1), 3)
check("PP", 3, r"The coefficient is \(@\). <b>", e.coeff(x, 1))
mc(3, e.coeff(x, 1), PAREN)
# PP4 SGHS 2023: constant term of (x - 2/x^2)^6
e = power(x - 2 / x ** 2, 6)
check_chain("PP", 4, r"Write \(@\). Row 6", e, 2)
check("PP", 4, r"\[\big(x-2x^{-2}\big)^6=@+\cdots\]", top(e, -3))
check_powers("PP", 4, r"The powers of \(x\) are \(@\), going down by 3", e, 3)
check_chain("PP", 4, r"\[15\times x^4\times4x^{-4}=@.\]", term(e, 0), 2)
# PP5 Knox 2023: coefficient of x^4 in (x + 2/x)^10
e = power(x + 2 / x, 10)
check_chain("PP", 5, r"Write \(@\). Row 10", e, 2)
check_powers("PP", 5, r"The powers of \(x\) are \(@\), going down by 2", e, 4)
check_chain("PP", 5, r"\[120\times x^7\times\big(2x^{-1}\big)^3=@.\]", term(e, 4), 3)
check("PP", 5, r"The coefficient of \(x^4\) is \(@\).", e.coeff(x, 4))
# PP6 Ascham 2023: coefficient of x^2 in (2 + x^2)(3 - 2x)^5
e = power(3 - 2 * x, 5)
check("PP", 6, r"\[\begin{aligned}(3-2x)^5&=@\\&=@\end{aligned}\]", (trunc(e, 2), trunc(e, 2)))
check_chain("PP", 6, r"\[2\times1080+243=@.\]", sp.expand((2 + x ** 2) * e).coeff(x, 2), 2)
check("PP", 6, r"the terms in \(x^2\) are \(@\) and \(@\).", (2 * term(e, 2), x ** 2 * term(e, 0)))
# PP7 PLC 2023: constant term of (2 - 3/x^3)(2x + 5/x^2)^6
e = power(2 * x + 5 / x ** 2, 6)
check_chain("PP", 7, r"Write \(@\). Row 6", e, 2)
check("PP", 7, r"\[\begin{aligned}\big(2x+5x^{-2}\big)^6&=@\\&=@\end{aligned}\]", (top(e, 0), top(e, 0)))
check_chain("PP", 7, r"\[2\times6000-3x^{-3}\times960x^3=@.\]", sp.expand((2 - 3 / x ** 3) * e).coeff(x, 0), 3)
check("PP", 7, r"needs the constant term @, and", term(e, 0))
check("PP", 7, r"needs the term \(@\). So", term(e, 3))
# PP8 St Aloysius 2024: coefficient of x^8 in (1 + x)(a - bx)^12 is zero
e = power(a - b * x, 12)
c8 = sp.expand((1 + x) * e).coeff(x, 8)
check_chain("PP", 8, r"\[792a^5(-bx)^7=@\quad", term(e, 7), 2)
check_chain("PP", 8, r"\quad495a^4(-bx)^8=@.\]", term(e, 8), 2)
check_chain("PP", 8, r"\[495a^4b^8-792a^5b^7=@.\]", c8, 2)
ratios = {sp.simplify(sol[a] / b) for sol in sp.solve(c8, [a], dict=True) if sol[a] != 0}
try:
    (g,) = grab(PPA[8], r"so \(@\). Hence", "PP 8")
    lh, rh = g.split("=")
    report(sp.solve(sp.Eq(tex(lh), tex(rh)), a) == [sp.Rational(5, 8) * b] and same(c8.subs(a, sp.Rational(5, 8) * b), 0), "PP8 8a = 5b", g)
except Exception as err:
    report(False, "PP8 8a = 5b", f"ERROR {err}")
check("PP", 8, r"Hence \(\dfrac ab=@\).", ratios.pop() if len(ratios) == 1 else sp.nan)
# PP9 James Ruse 2023: constant term of (x^3/2 + a/x)^8 is 5103
e = power(x ** 3 / 2 + a / x, 8)
check_chain("PP", 9, r"Write \(@\). Row 8", e, 2)
check("PP", 9, r"\Big)^8\) has \(@\). From", x ** max(deg(t, x) for t in sp.Add.make_args(e)))
report(sorted({deg(t, x) for t in sp.Add.make_args(e)}, reverse=True).index(0) == 6, "PP9 constant term is the seventh term", "6 steps of -4 from x^24")
check_chain("PP", 9, r"\[28\times\Big(\dfrac{x^3}{2}\Big)^2\times\big(ax^{-1}\big)^6=@.\]", term(e, 0), 3)
check("PP", 9, r"Then \(7a^6=@\), so", sp.Integer(5103))
check_chain("PP", 9, r"so \(a^6=@\), and", sp.Integer(5103) / (term(e, 0) / a ** 6), 2, use_lhs=False)
check_set("PP", 9, r"and \(a=@\) or \(a=@\).", [v for v in sp.solve(sp.Eq(term(e, 0), 5103), a) if v.is_real])

print(f"\n{len(FAILS)} problem(s)" if FAILS else "\nAll OK")
sys.exit(1 if FAILS else 0)
