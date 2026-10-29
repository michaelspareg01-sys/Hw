"""Check of Lesson 15A (Y11 Ch 15 pack): Binomial expansions and Pascal's triangle.

The script reads the values PRINTED in workspace/build/y11ch15/a_15a.html (lesson examples,
textbook homework, past-paper worked solutions) and in the worked examples of l15a.html.
Each value is found with a template ('@' marks the printed LaTeX); a template must match
exactly once in its block, otherwise the item FAILS. The printed LaTeX is converted to a
sympy expression and compared with an independent computation:
  - expansions are built by repeated multiplication (sympy expand of the product of n
    brackets), not from a coefficient formula;
  - Pascal's triangle is built by the addition property and compared with math.comb;
  - coefficients, terms and equations are recomputed with sympy (coeff, solve);
  - decimal approximations are recomputed with exact rationals and rounded.
It also checks the lesson fragment: past-paper marks add to the intro total, time is
1.5 x marks rounded to 5 minutes, numbering and source labels match in both files, and
the MC letter is the option equal to the computed expansion.

Exit status 1 if anything fails. Run: python3 workspace/checks/y11ch15_15a.py
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
x, y, a, c, z, k = sp.symbols("x y a c z k")
SYMS = {"x": x, "y": y, "a": a, "c": c, "z": z, "k": k, "sqrt": sp.sqrt, "binomial": sp.binomial}
TR = standard_transformations + (implicit_multiplication_application,)


def read(name):
    with open(os.path.join(SRC, name), encoding="utf-8") as f:
        return f.read()


def report(ok, label, detail):
    print(("OK       " if ok else "MISMATCH ") + label.replace("\n", " ") + "  " + detail.replace("\n", " "))
    if not ok:
        FAILS.append(label)


# ---------------------------------------------------------------- LaTeX -> sympy
def _arg(s, i):
    if s[i] == "{":
        depth, j = 0, i
        while True:
            depth += {"{": 1, "}": -1}.get(s[j], 0)
            if depth == 0:
                return s[i + 1:j], j + 1
            j += 1
    return s[i], i + 1


def _conv(s):
    out, i = [], 0
    while i < len(s):
        if s.startswith(("\\dfrac", "\\tfrac", "\\frac"), i):
            i = s.index("frac", i) + 4
            p, i = _arg(s, i)
            q, i = _arg(s, i)
            out.append(f"(({_conv(p)})/({_conv(q)}))")
        elif s.startswith("\\sqrt[", i):          # n-th root \sqrt[n]{...}
            j = s.index("]", i)
            nth = s[i + 6:j]
            p, i = _arg(s, j + 1)
            out.append(f"(({_conv(p)})**(1/({nth})))")
        elif s.startswith("\\sqrt", i):
            p, i = _arg(s, i + 5)
            out.append(f"sqrt({_conv(p)})")
        elif s.startswith("\\dbinom", i):
            p, i = _arg(s, i + 7)
            q, i = _arg(s, i)
            out.append(f"binomial({_conv(p)},{_conv(q)})")
        elif s.startswith("\\boxed", i):
            p, i = _arg(s, i + 6)
            out.append(f"({_conv(p)})")
        elif s.startswith("\\times", i):
            out.append("*")
            i += 6
        elif s[i] == "^":
            p, i = _arg(s, i + 1)
            out.append(f"**({_conv(p)})")
        elif s[i] == "\\":
            raise ValueError(f"unknown macro in {s!r}")
        elif s[i] in "{}":
            out.append("(" if s[i] == "{" else ")")
            i += 1
        else:
            out.append(s[i])
            i += 1
    return "".join(out)


def clean(tex):
    s = re.sub(r"\\left|\\right|\\bigg|\\Big|\\big|\\,|\\;|\\!|&nbsp;|\s", "", tex)
    s = re.sub(r"[+-]?\\cdots", "", s)
    return s


def tex(texs):
    """Printed LaTeX -> sympy expression."""
    s = clean(texs)
    m = re.fullmatch(r"(-?)(\d+)\\tfrac\{(\d+)\}\{(\d+)\}", s)       # mixed number 1\tfrac{10}{27}
    if m:
        v = int(m.group(2)) + sp.Rational(int(m.group(3)), int(m.group(4)))
        return -v if m.group(1) else v
    return parse_expr(_conv(s), local_dict=dict(SYMS), transformations=TR)


def same(p, q):
    return sp.simplify(sp.expand(p - q)) == 0


def power(base, n):
    """(base)^n by repeated multiplication."""
    r = sp.Integer(1)
    for _ in range(n):
        r = sp.expand(r * base)
    return r


def poly_terms(e, var=x):
    e = sp.expand(e)
    return {int(t.as_coeff_exponent(var)[1]): t for t in sp.Add.make_args(e)}


def term(e, j, var=x):
    """The term in var^j of an expansion (as an expression)."""
    e = sp.expand(e)
    return sp.Add(*[t for t in sp.Add.make_args(e) if sp.degree(t * var ** 20, var) - 20 == j]) if e != 0 else 0


def trunc(e, deg, var=x):
    e = sp.expand(e)
    return sp.Add(*[t for t in sp.Add.make_args(e) if (sp.degree(t * var ** 50, var) - 50) <= deg])


# ---------------------------------------------------------------- HTML blocks
ans = read("a_15a.html")
les = read("l15a.html")
parts = ans.split('<div class="ans-sec">Past-Paper Homework - Worked Solutions</div>')
if len(parts) != 2:
    sys.exit("FAIL: past-paper solutions section not found exactly once in a_15a.html")
if ans.count("{{ahead:Lesson 15A | Binomial expansions and Pascal's triangle}}") != 2:
    report(False, "answers headings", "expected {{ahead:Lesson 15A | ...}} twice")
pre = parts[0]
BLK = {}
for m in re.finditer(r'<div class="a"><span class="an">([^<]+)</span><div class="ab">(.*?)(?=<div class="a"><span class="an">|<div class="ans-sec">|\{\{ahead|$)', pre, re.S):
    if m.group(1) in BLK:
        report(False, f"block {m.group(1)}", "duplicate answer number")
    BLK[m.group(1)] = m.group(2)
PPA = {int(n): b for n, b in re.findall(r'<div class="ppa"><div class="pp-src"><span><span class="pn">PP (\d+)</span>(.*?)(?=<div class="ppa">|$)', parts[1], re.S)}

pps = les.split("<!-- ============ Past papers ============ -->")
if len(pps) != 2:
    sys.exit("FAIL: past-paper section not found in l15a.html")
PPQ = {int(n): b for n, b in re.findall(r'<div class="pp"><div class="pp-src"><span><span class="pn">PP (\d+)</span>(.*?)(?=<div class="pp">|$)', pps[1], re.S)}
WORKED = {int(n): b for n, b in re.findall(r'<span class="tag">Worked example (\d+)</span>(.*?)(?=<div class="ex |<!-- =====|$)', les, re.S)}


def grab(block, template, where):
    pieces = template.split("@")
    cap = r"((?:(?!\\\)|\\\]|\\\\&).)+?)"    # one value: never crosses \) or \] or a new aligned row
    rx = "".join(re.escape(p) + (cap if i < len(pieces) - 1 else "") for i, p in enumerate(pieces))
    found = re.findall(rx, block, re.S)
    if len(found) != 1:
        raise LookupError(f"template matched {len(found)} times in {where}: {template!r}")
    return found[0] if isinstance(found[0], tuple) else (found[0],)


def src(kind, key):
    table = {"A": BLK, "PP": PPA, "W": WORKED}[kind]
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
        oks, shown = [], []
        for g, e in zip(got, exp):
            if mode == "round":          # e = (exact value, decimals)
                val, dp = e
                ok = Fraction(g) == round(Fraction(val), dp) and len(g.split(".")[1]) == dp
            else:
                ok = same(tex(g), e)
            oks.append(ok)
            shown.append(g)
        report(all(oks), label, "printed " + " | ".join(shown))
    except Exception as err:
        report(False, label, f"ERROR {err}")


def check_chain(kind, key, template, expected):
    """Printed 'A=B=C' (sides separated by '='): every side must equal expected."""
    label = f"{kind}{key} {template}"
    try:
        (g,) = grab(src(kind, key), template, f"{kind} {key}")
        sides = [s for s in re.split(r"=|\\doteq", g) if s.strip()]
        report(all(same(tex(s), expected) for s in sides), label, f"printed {g}")
    except Exception as err:
        report(False, label, f"ERROR {err}")


def check_ratio(kind, key, template, num, den):
    """Printed 'P:Q' equal to the ratio num:den."""
    label = f"{kind}{key} {template}"
    try:
        (g,) = grab(src(kind, key), template, f"{kind} {key}")
        p, q = g.split(":")
        report(same(tex(p) * den, tex(q) * num), label, f"printed {g}")
    except Exception as err:
        report(False, label, f"ERROR {err}")


# ================================================================ lesson examples (C1-C5)
# C1: expansions
check("A", "C1", r"<b>a</b> \((1+3a)^4=@\)", power(1 + 3 * a, 4))
check("A", "C1", r"<b>b</b> \((1-x)^5=@\)", power(1 - x, 5))
check("A", "C1", r"<b>c</b> \(\big(1-\tfrac12x\big)^5=@\)", power(1 - x / 2, 5))
check("A", "C1", r"<b>a</b> \((1+5a)^3=@\)", power(1 + 5 * a, 3))
check("A", "C1", r"<b>b</b> \((1-x)^3=@\)", power(1 - x, 3))
check("A", "C1", r"<b>c</b> \(\big(1-\tfrac13x\big)^4=@\)", power(1 - x / 3, 4))


# C2: approximations; the listed terms are the first binomial terms, the total is rounded correctly
def approx_terms(h, n):
    e = power(1 + x, n)
    return [sp.Rational(e.coeff(x, j)) * h ** j for j in range(n + 1)]


def check_approx(template, h, n, dp):
    label = f"AC2 {template}"
    try:
        terms_tex, final = grab(BLK["C2"], template, "C2")
        s = clean(terms_tex)
        nums = [sp.Rational(t) for t in re.findall(r"[+-]?\d*\.?\d+", s)]
        want = approx_terms(h, n)
        ok_terms = nums == want[:len(nums)] and len(nums) >= 3
        exact = (1 + h) ** n
        ok_round = Fraction(final) == round(Fraction(str(sp.nsimplify(exact))), dp)
        # the dropped terms cannot change the rounding
        partial = sum(nums)
        ok_stable = round(Fraction(str(partial)), dp) == round(Fraction(str(exact)), dp)
        report(ok_terms and ok_round and ok_stable, label, f"terms {[str(v) for v in nums]}, printed {final}, exact {float(exact):.10f}")
    except Exception as err:
        report(False, label, f"ERROR {err}")


check_approx(r"<b>a</b> \(@\doteq@\)<br><b>b</b> \(1-0.05", sp.Rational(1, 100), 7, 5)
check_approx(r"<b>b</b> \(@\doteq@\)<br>" + "\n<b>Your turn.", -sp.Rational(1, 100), 5, 5)
check_approx(r"<b>a</b> \(@\doteq@\)<br><b>b</b> \(1-0.08", sp.Rational(2, 100), 6, 5)
try:   # Your turn b is the full expansion of (1 - 0.02)^4, written without dots
    (g, fin) = grab(BLK["C2"], r"<b>b</b> \(1-0.08@\doteq@\)</div>", "C2")
    nums = [sp.Rational(t) for t in re.findall(r"[+-]?\d*\.?\d+", "1-0.08" + clean(g))]
    report(nums == approx_terms(-sp.Rational(2, 100), 4) and Fraction(fin) == round(Fraction(str(sp.Rational(98, 100) ** 4)), 5),
           "AC2 your turn b", f"terms {[str(v) for v in nums]}, printed {fin}")
except Exception as err:
    report(False, "AC2 your turn b", f"ERROR {err}")

# C3: (1 + 3/x)^2 (1 - x)^6 and (1 + 2/x)^2 (1 - x)^5
for p, n, i_t, ii_t, first in (
        (3, 6, r"(i) \(@\) &nbsp; (ii) \(-6x", r"(ii) \(-6x+@\)<br>", r"\(\Big(1+\dfrac3x\Big)^2=@\) and \((1-x)^6=@\)<br>"),
        (2, 5, r"(i) \(@\) &nbsp; (ii) \(-5x", r"(ii) \(-5x+@\)</div>", r"\(\Big(1+\dfrac2x\Big)^2=@\) and \((1-x)^5=@\)<br>")):
    f1, f2 = power(1 + p / x, 2), power(1 - x, n)
    prod = sp.expand(f1 * f2)
    check("A", "C3", first, (f1, trunc(f2, 3)))
    check_chain("A", "C3", i_t, term(prod, 0))
    try:
        (g,) = grab(BLK["C3"], ii_t, "C3")
        lead = -n * x
        sides = [lead + tex(s) for s in g.split("=")[:-1]] + [tex(g.split("=")[-1])]
        report(all(same(s, term(prod, 1)) for s in sides), f"AC3 term in x (p={p}, n={n})", f"printed {-n}x+{g}")
    except Exception as err:
        report(False, f"AC3 term in x (p={p}, n={n})", f"ERROR {err}")

# C4: terms and k
for templ, n, m, r_num, r_den in ((r"<b>Tutor demo.</b> <b>a</b> \(@\) and \(@\)", 5, 2, 3, 4),
                                  (r"<b>Your turn.</b> <b>a</b> \(@\) and \(@\)", 6, 1, 2, 1)):
    e = power(1 + m * k * x, n)
    check("A", "C4", templ, (term(e, 3), term(e, 2)))
    ks = [s for s in sp.solve(sp.Eq(e.coeff(x, 3) * r_den, e.coeff(x, 2) * r_num), k) if s != 0]
    tk = r"so \(k=@\)</div><div" if n == 5 else r"so \(k=@\)</div></div>"
    check("A", "C4", tk, ks[0] if len(ks) == 1 else sp.nan)

# C5: trinomials
check("A", "C5", r"\(\big(1+x+x^2\big)^3=@\)", power(1 + x + x ** 2, 3))
check("A", "C5", r"\(\big(1+x-x^2\big)^3=@\) (the", power(1 + x - x ** 2, 3))

# lesson questions really are the ones answered (each appears once in l15a.html)
for q in (r"\((1+3a)^4\)", r"<b>b</b> \((1-x)^5\)<br>", r"\(\big(1-\tfrac12x\big)^5\)", r"\((1+5a)^3\)", r"\((1-x)^3\)", r"\(\big(1-\tfrac13x\big)^4\)",
          r"\(1.01^7\), using \((1+0.01)^7\)", r"\(0.99^5\), using \((1-0.01)^5\)", r"\(1.02^6\), using \((1+0.02)^6\)", r"\(0.98^4\), using \((1-0.02)^4\)",
          r"\(\Big(1+\dfrac3x\Big)^2(1-x)^6\)", r"\(\Big(1+\dfrac2x\Big)^2(1-x)^5\)", r"\((1+2kx)^5\)", r"ratio \(3:4\)", r"\((1+kx)^6\)", r"ratio \(2:1\)",
          r"Expand \(\big(1+x+x^2\big)^3\)", r"Expand \(\big(1+x-x^2\big)^3\)"):
    report(les.count(q) == 1, "lesson question", f"{q} appears {les.count(q)} time(s)")

# ================================================================ lesson concept 1: displayed table and column expansions
try:
    tbl = re.search(r'<table class="t pt"[^>]*>(.*?)</table>', les, re.S).group(1)
    rows = re.findall(r"<tr><th>(\d+)</th>(.*?)</tr>", tbl, re.S)
    ok = [int(n) for n, _ in rows] == list(range(9))
    for n, cells in rows:
        vals = [int(v) for v in re.findall(r"<td>(?:<b>)?(\d+)(?:</b>)?</td>", cells)]
        blanks = len(re.findall(r"<td></td>", cells))
        ok &= vals == [comb(int(n), r) for r in range(int(n) + 1)] and blanks == 8 - int(n)
        ok &= vals == [power(1 + x, int(n)).coeff(x, r) for r in range(int(n) + 1)]
    report(ok, "lesson Pascal table rows 0-8", f"{len(rows)} rows checked against comb and expand")
except Exception as err:
    report(False, "lesson Pascal table", f"ERROR {err}")
cols = re.findall(r"\\\[\(1\+x\)\^(\d)=1\(1\+x\)(?:\^(\d))?\+x\(1\+x\)(?:\^(\d))?\\\]\s*\\\[\\begin\{alignedat\}\{\d\}(.*?)\\end\{alignedat\}\\\]", les, re.S)
report(sorted(int(c_[0]) for c_ in cols) == [2, 3, 4], "lesson column expansions found", f"n = {[c_[0] for c_ in cols]}")
for n, e1_, e2_, body in cols:
    n = int(n)
    try:
        hdr_ok = int(e1_ or 1) == n - 1 and int(e2_ or 1) == n - 1
        r = [re.sub(r"[&=]", "", row).replace("{}", "") for row in body.split(r"\\")]
        top, mid, bot = (tex(v) for v in r)
        ok = hdr_ok and same(top, power(1 + x, n - 1)) and same(mid, x * power(1 + x, n - 1)) and same(bot, power(1 + x, n)) and same(top + mid, bot)
        report(ok, f"lesson (1+x)^{n} in columns", " | ".join(r))
    except Exception as err:
        report(False, f"lesson (1+x)^{n} in columns", f"ERROR {err}")
# the boxed numbers of the addition property: boxed 1 and 3 in the x^3 column add to the boxed 4
try:
    boxed = [int(b) for b in re.findall(r"\\boxed\{(\d+)\}", les)]
    report(boxed == [1, 3, 4] and power(1 + x, 3).coeff(x, 3) + power(1 + x, 3).coeff(x, 2) == power(1 + x, 4).coeff(x, 3) == 4, "lesson boxed 1 + 3 = 4", f"{boxed}")
except Exception as err:
    report(False, "lesson boxed", f"ERROR {err}")

# ================================================================ worked examples (textbook Examples 1-5)
try:
    w1 = WORKED[1]
    a1 = re.search(r"\\\\&=(1\+12a[^.]*)\.\\end\{aligned\}", w1).group(1)
    b1 = re.search(r"\\\\&=(1-4x[^.]*)\.\\end\{aligned\}", w1).group(1)
    c1 = re.search(r"\\\\&=(1-\\tfrac\{10\}[^\]]*?)\.\\end\{aligned\}", w1).group(1)
    report(same(tex(a1), power(1 + 2 * a, 6)), "W1 a", a1)
    report(same(tex(b1), power(1 - x, 4)), "W1 b", b1)
    report(same(tex(c1), power(1 - sp.Rational(2, 3) * x, 5)), "W1 c", c1)
except Exception as err:
    report(False, "W1", f"ERROR {err}")
try:
    w2 = WORKED[2]
    t2 = re.search(r"\\\\&=(1\+0\.16[^\\]*)\+\\cdots", w2).group(1)
    nums = [sp.Rational(t) for t in re.findall(r"[+-]?\d*\.?\d+", t2)]
    f2 = re.search(r"\\doteq(\d\.\d+)\.", w2).group(1)
    ex = sp.Rational(102, 100) ** 8
    report(nums == approx_terms(sp.Rational(2, 100), 8)[:5] and Fraction(f2) == round(Fraction(str(ex)), 5)
           and round(Fraction(str(sum(nums))), 5) == round(Fraction(str(ex)), 5), "W2", f"terms {[str(v) for v in nums]}, printed {f2}")
except Exception as err:
    report(False, "W2", f"ERROR {err}")
p3 = sp.expand(power(1 + 5 / x, 2) * power(1 - x, 8))
check("W", 3, r"\(\Big(1+\dfrac5x\Big)^2=@\) and \((1-x)^8=@\)</p>", (power(1 + 5 / x, 2), trunc(power(1 - x, 8), 3)))
try:
    w3 = WORKED[3]
    (i3,) = grab(w3, r"\\&=1-80+700\\&=@.\end{aligned}", "W3")
    (ii3,) = grab(w3, r"\\&=-8x+280x-1400x\\&=@.\end{aligned}", "W3")
    report(same(tex(i3), term(p3, 0)), "W3 constant term", i3)
    report(same(tex(ii3), term(p3, 1)) and same(tex("-8x+280x-1400x"), term(p3, 1)), "W3 term in x", ii3)
except Exception as err:
    report(False, "W3", f"ERROR {err}")
e4 = power(1 + 2 * k * x, 6)
check("W", 4, r"<p>The terms are \(@\) and \(@\).", (term(e4, 4), term(e4, 3)))
k4 = [s for s in sp.solve(sp.Eq(3 * e4.coeff(x, 4), 2 * e4.coeff(x, 3)), k) if s != 0]
check("W", 4, r"so \(k=@\).</p>", k4[0])
try:
    w5 = re.search(r"&=(1\+4x\+10x\^2[^\\]*)\\end\{aligned\}", WORKED[5]).group(1)
    report(same(tex(w5), power(1 + x + x ** 2, 4)), "W5", w5)
except Exception as err:
    report(False, "W5", f"ERROR {err}")

# ================================================================ textbook homework
# Q1: Pascal's triangle rows 0-12 built by the addition property, checked against comb
try:
    rows = re.findall(r"<tr><th>(\d+)</th>(.*?)</tr>", BLK["1"], re.S)
    tri = [[1]]
    for n in range(1, 13):
        prev = tri[-1]
        tri.append([1] + [prev[r - 1] + prev[r] for r in range(1, n)] + [1])
    ok = len(rows) == 13
    for n, cells in rows:
        vals = [int(v) for v in re.findall(r"<td>(\d+)</td>", cells)]
        ok &= vals == tri[int(n)] == [comb(int(n), r) for r in range(int(n) + 1)]
    report(ok, "A1 Pascal's triangle rows 0-12", f"{len(rows)} rows")
except Exception as err:
    report(False, "A1", f"ERROR {err}")

Q2 = {"a": power(1 + x, 6), "b": power(1 - x, 6), "c": power(1 + x, 9), "d": power(1 - x, 9),
      "e": power(1 + c, 5), "f": power(1 + 2 * y, 4), "g": power(1 + x / 3, 7), "h": power(1 - 3 * z, 3),
      "i": power(1 - 1 / x, 8), "j": power(1 + 2 / x, 5), "k": power(1 + y / x, 5), "l": power(1 + 3 * x / y, 4)}
for part, e in Q2.items():
    check("A", "2", rf"<b>{part}</b> \(@\)</div>", e)

for part, (base, n, j1, j2) in {"a": (1 + x, 11, 2, 8), "b": (1 - x, 7, 3, 5), "c": (1 + 2 * x, 6, 4, 5), "d": (1 - 3 / x, 4, -1, -2)}.items():
    e = power(base, n)
    check("A", "4", rf"<b>{part}</b> (i) \(@\) (ii) \(@\)", (term(e, j1), term(e, j2)))

check_chain("A", "6", r"<b>a</b> \(@\) &nbsp;", sp.expand(1 + 3 * (x - 1) + 3 * (x - 1) ** 2 + (x - 1) ** 3))
check_chain("A", "6", r"<b>b</b> \(@\)</div>", sp.expand(1 - 6 * (x + 1) + 15 * (x + 1) ** 2 - 20 * (x + 1) ** 3 + 15 * (x + 1) ** 4 - 6 * (x + 1) ** 5 + (x + 1) ** 6))
check("A", "7", r"\(@\)", sp.expand(power(1 - x, 4) + power(1 - x, 5) + power(1 - x, 6)).coeff(x, 4))
r3, r5 = sp.expand(power(1 + sp.sqrt(3), 5)), sp.expand(power(1 - sp.sqrt(5), 3))
check("A", "8", r"<b>a</b> \(a=@\), \(b=@\)", (r3.subs(sp.sqrt(3), 0), r3.coeff(sp.sqrt(3))))
check("A", "8", r"<b>b</b> \(a=@\), \(b=@\)", (r5.subs(sp.sqrt(5), 0), r5.coeff(sp.sqrt(5))))
check("A", "10", r"<b>a</b> \(@\)", ((Fraction(1003, 1000) ** 6, 5),), mode="round")
check("A", "10", r"<b>b</b> \(@\)", ((Fraction(96, 100) ** 5, 5),), mode="round")
for part, (base, deg, other, j) in {"a": (1 + x, 2, 1 - 5 * x, 2), "b": (1 + 2 * x, 3, 2 - 3 * x, 3), "c": (1 - 3 * x, 3, (2 + x) ** 2, 3)}.items():
    n = {"a": 4, "b": 5, "c": 4}[part]
    e = power(base, n)
    check("A", "11", rf"<b>{part}</b> (i) \(@\) (ii) \(@\)", (trunc(e, deg), sp.expand(e * other).coeff(x, j)))
# Q12: third and fourth terms of (1 + 2x)^5 equal; sixth term of (1 + x)^7 the average of fifth and seventh
t = [t for t in sorted(poly_terms(power(1 + 2 * x, 5)).items())]
s12a = set(sp.solve(sp.Eq(t[2][1], t[3][1]), x))
t7 = [t for t in sorted(poly_terms(power(1 + x, 7)).items())]
s12b = set(sp.solve(sp.Eq(2 * t7[5][1], t7[4][1] + t7[6][1]), x))
try:
    g = grab(BLK["12"], r"<b>a</b> \(x=@\) or \(@\) &nbsp;", "12")
    report({tex(v) for v in g} == s12a, "A12 a", f"printed {g}, solutions {s12a}")
    g = grab(BLK["12"], r"<b>b</b> \(x=@\), \(@\) or \(@\)</div>", "12")
    report({tex(v) for v in g} == s12b, "A12 b", f"printed {g}, solutions {s12b}")
except Exception as err:
    report(False, "A12", f"ERROR {err}")
Q13 = {"a": sp.expand((3 - 4 * x) * power(1 + x, 4)).coeff(x, 3),
       "b": sp.expand((1 + 3 * x + x ** 2) * power(1 - x, 3)).coeff(x, 1),
       "c": sp.expand((5 - 2 * x ** 3) * power(1 + 2 * x, 5)).coeff(x, 4),
       "d": sp.expand(power(1 - x / 3, 3) * power(1 + 2 / x, 2)).coeff(x, 0)}
for part, v in Q13.items():
    check("A", "13", rf"<b>{part}</b> \(@\)", v)
check("A", "14", r"<b>a</b> \(@\)", sp.expand(power(1 + 2 * x, 4) * power(1 - 1 / x ** 2, 6)).coeff(x, 0))
check("A", "14", r"<b>b</b> \(@\)", sp.expand(power(1 - x / 3, 5) * power(1 + 2 / x, 3)).coeff(x, 0))
e15a, e15b = power(1 + x, 6), power(1 + 2 / (3 * x), 7)
check("A", "15", r"<b>a</b> (i) \(@\) (ii) \(@\)", (term(e15a, 2), term(e15a, 3)))
check_ratio("A", "15", r"(iii) \(@\) (iv) \(135", term(e15a, 2), term(e15a, 3))
check("A", "15", r"(iv) \(@\), \(@\), \(1:4\)", (term(e15a, 2).subs(x, 3), term(e15a, 3).subs(x, 3)))
check_ratio("A", "15", r"\(540\), \(@\)<br>", term(e15a, 2).subs(x, 3), term(e15a, 3).subs(x, 3))
check("A", "15", r"<b>b</b> (i) \(@\) (ii) \(@\) (iii)", (term(e15b, -5), term(e15b, -6)))
check_ratio("A", "15", r"(iii) \(@\) (iv) \(\tfrac{7}{81}", term(e15b, -5), term(e15b, -6))
check("A", "15", r"(iv) \(@\), \(@\), \(9:1\)", (term(e15b, -5).subs(x, 2), term(e15b, -6).subs(x, 2)))
check_ratio("A", "15", r"\(\tfrac{7}{729}\), \(@\)</div>", term(e15b, -5).subs(x, 2), term(e15b, -6).subs(x, 2))
e16a, e16b = power(1 + k * x, 8), power(1 - sp.Rational(3, 4) * k * x, 9)
k16a = {s for s in sp.solve(sp.Eq(4 * e16a.coeff(x, 4), e16a.coeff(x, 5)), k) if s != 0}   # ratio needs non-zero coefficients
k16b = set(sp.solve(sp.Eq(e16b.coeff(x, 5), e16b.coeff(x, 6)), k))
try:
    g = grab(BLK["16"], r"<b>a</b> \(k=@\) &nbsp;", "16")
    report({tex(v) for v in g} == k16a, "A16 a", f"printed {g}, solutions {k16a}")
    g = grab(BLK["16"], r"<b>b</b> \(k=@\) or \(@\)</div>", "16")
    report({tex(v) for v in g} == k16b, "A16 b", f"printed {g}, solutions {k16b}")
except Exception as err:
    report(False, "A16", f"ERROR {err}")
s18 = trunc(power(1 + x + 3 * x ** 2, 6), 3)
v18 = Fraction(str(s18.subs(x, sp.Rational(1, 100))))
try:
    (g,) = grab(BLK["18"], r"\(@\)", "18")
    report(Fraction(g) == round(v18, 4) == round(Fraction(10103, 10000) ** 6, 4), "A18", f"printed {g}, series to x^3 gives {float(v18)}, 1.0103^6 = {float(Fraction(10103, 10000) ** 6):.8f}")
except Exception as err:
    report(False, "A18", f"ERROR {err}")
for n in range(5):
    tmpl = {0: r"\((1+x+y)^0=@\), ", 1: r"\((1+x+y)^1=@\),<br>", 2: r"\((1+x+y)^2=@\),<br>", 3: r"\((1+x+y)^3=@\),<br>", 4: r"\((1+x+y)^4=@\)<br>"}[n]
    check("A", "19", tmpl, power(1 + x + y, n))

# ================================================================ past papers
try:
    intro = re.search(r"Suggested time: (\d+) minutes</b></span><span><b>(\d+) marks", pps[1])
    marks = [int(m) for m in re.findall(r'<span class="mk">(\d+) marks?</span>', pps[1])]
    T, M = int(intro.group(1)), int(intro.group(2))
    report(sum(marks) == M, "PP marks", f"PP marks {marks} sum {sum(marks)}, intro {M}")
    if not 15 <= M <= 22:
        print(f"NOTE     PP total {M} marks is below 15: house rule 8 (too few clean 15A school-paper items; see report)")
    report(T == 5 * round(1.5 * M / 5), "PP time", f"{T} min for {M} marks")
    report(sorted(PPQ) == sorted(PPA) == list(range(1, len(PPQ) + 1)), "PP numbering", f"lesson {sorted(PPQ)}, answers {sorted(PPA)}")
    for n in PPQ:
        sub = [int(m) for m in re.findall(r'<div class="pp-sub"><span>.*?</span><span class="mk">(\d+)</span></div>', PPQ[n], re.S)]
        tot = int(re.search(r'<span class="mk">(\d+) marks?</span>', PPQ[n]).group(1))
        if sub:
            report(sum(sub) == tot, f"PP{n} part marks", f"parts {sub} sum {sum(sub)}, block {tot}")
        sq = re.search(r"^(.*?)</span>", PPQ[n]).group(1)
        sa = re.search(r"^(.*?)</span>", PPA[n]).group(1) if n in PPA else None
        report(sq == sa, f"PP{n} source label", sq)
        report(PPQ[n].count('<div class="hint">') == 1, f"PP{n} hint", "exactly one hint")
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

# PP1 Kings: (2x - 1)^3
e1 = power(2 * x - 1, 3)
check_chain("PP", 1, r"\[(1-2x)^3=@.\]", power(1 - 2 * x, 3))
check("PP", 1, r"Hence \((2x-1)^3=@\).", e1)
mc(1, e1, PAREN)
# PP2 Ascham: coefficient of the fourth term of (3x - 4)^6 (7 terms, so the 4th is the middle term from either end)
e2 = power(3 * x - 4, 6)
desc = [e2.coeff(x, 6 - j) for j in range(7)]
asc = [e2.coeff(x, j) for j in range(7)]
report(desc[3] == asc[3], "PP2 fourth term is the same from either end", f"{desc[3]}")
check("PP", 2, r"so \((3x-4)^6=(-4)^6\Big(1-\dfrac{3x}{4}\Big)^6=@\Big(1-\dfrac{3x}{4}\Big)^6\)", sp.Integer(4) ** 6)
check_chain("PP", 2, r"\[4096\times20\Big(-\dfrac{3x}{4}\Big)^3=@.\]", term(e2, 3))
check("PP", 2, r"fourth term is \(@\). <b>", desc[3])
mc(2, desc[3], DOT)
# PP3 NSB: coefficient of x^3 in (a + x)^6 is 1280
c3 = power(a + x, 6).coeff(x, 3)
sol3 = [r for r in sp.solve(sp.Eq(c3, 1280), a) if r.is_real]
check("PP", 3, r"the term in \(x^3\) is \(x^6\times\dfrac{20a^3}{x^3}=@\).</p>", term(power(a + x, 6), 3))
check("PP", 3, r"so \(a^3=@\) and", sp.Integer(1280) / (c3 / a ** 3))
check("PP", 3, r"and \(a=@\). <b>", sol3[0] if len(sol3) == 1 else sp.nan)
mc(3, sol3[0], DOT)
# PP4 Girraween 2021: coefficients of x and x^2 in (2x + k)^6 equal
e4g = power(2 * x + k, 6)
check("PP", 4, r"so it is \(64x^6\times\dfrac{6k^5}{32x^5}=@\).</p>", term(e4g, 1))
check("PP", 4, r"so it is \(64x^6\times\dfrac{15k^4}{16x^4}=@\).</p>", term(e4g, 2))
ks4 = set(sp.solve(sp.Eq(e4g.coeff(x, 1), e4g.coeff(x, 2)), k))
try:
    g = grab(PPA[4], r"so \(k=@\) or \(k=@\). None", "PP 4")
    report({tex(v) for v in g} == ks4, "PP4 solutions", f"printed {g}, solve gives {ks4}")
except Exception as err:
    report(False, "PP4 solutions", f"ERROR {err}")
mc(4, sp.Integer(5), PAREN)
report(sp.Integer(0) not in [tex(v) for v in re.findall(r"<span>\([A-D]\) \\\((.+?)\\\)</span>", PPQ[4])], "PP4 options", "0 is not an option, so 5 is the only listed solution")
# PP5 Moriah: (1 + x)^3, coefficient of x^4 in (2x - 1)^2 (1 + x)^3
check("PP", 5, r"so \((1+x)^3=@\).</p>", power(1 + x, 3))
check("PP", 5, r"First \((2x-1)^2=@\), so", power(2 * x - 1, 2))
check("PP", 5, r"coefficient of \(x^4\) is \(12-4=@\).", sp.expand(power(2 * x - 1, 2) * power(1 + x, 3)).coeff(x, 4))
# PP6 SGS: (x - 2/x)^4
check("PP", 6, r"\Big)^4=1+4\Big(-\dfrac{2}{x^2}\Big)+6\Big(-\dfrac{2}{x^2}\Big)^2+4\Big(-\dfrac{2}{x^2}\Big)^3+\Big(-\dfrac{2}{x^2}\Big)^4=@.\]", power(1 - 2 / x ** 2, 4))
check("PP", 6, r"\[\Big(x-\dfrac2x\Big)^4=@.\]", power(x - 2 / x, 4))
# PP7 Girraween 2023: constant term of (x + 2/x)^6
check("PP", 7, r"fourth term, \(20\Big(\dfrac{2}{x^2}\Big)^3=@\).", term(power(1 + 2 / x ** 2, 6), -6))
check("PP", 7, r"the constant term is \(@\).</p>", power(x + 2 / x, 6).coeff(x, 0))
# PP8 Abbotsleigh: coefficient of x^6 in (3x^2 - 2a)^5
e8 = power(3 * x ** 2 - 2 * a, 5)
check("PP", 8, r"\[243x^{10}\times\dfrac{40a^2}{9x^4}=@,\]", term(e8, 6))
check("PP", 8, r"the coefficient of \(x^6\) is \(@\).", e8.coeff(x, 6))
check("PP", 8, r"10\Big(-\dfrac{2a}{3x^2}\Big)^2=@\). So", term(power(1 - 2 * a / (3 * x ** 2), 5), -4))
# PP9 Normanhurst Boys 2022: constant term of (3x - 1/x^2)^6, also as C(6,2) 3^4
e9 = power(3 * x - 1 / x ** 2, 6)
check("PP", 9, r"third term, \(15\Big(-\dfrac{1}{3x^3}\Big)^2=@\).", term(power(1 - 1 / (3 * x ** 3), 6), -6))
try:
    (g,) = grab(PPA[9], r"\[729\times\dfrac{15}{9}=@.\]", "PP 9")
    vals = [s_ for s_ in g.split("=")]
    ok = len(vals) == 2 and same(tex(vals[0]), e9.coeff(x, 0)) and same(tex(vals[1]), e9.coeff(x, 0)) and "\\dbinom62" in vals[1] and comb(6, 2) * 3 ** 4 == e9.coeff(x, 0)
    report(ok, "PP9 constant term", f"printed {g}, computed {e9.coeff(x, 0)}")
except Exception as err:
    report(False, "PP9 constant term", f"ERROR {err}")

print(f"\n{len(FAILS)} problem(s)" if FAILS else "\nAll OK")
sys.exit(1 if FAILS else 0)
