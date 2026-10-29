"""Check of Lesson 15D (Y11 Ch 15 pack): Identities in Pascal's triangle, and the Chapter 15 review.

The script reads the values PRINTED in workspace/build/y11ch15/a_15d.html (lesson examples,
textbook homework, chapter review answers, past-paper worked solutions) and in l15d.html (the
table of Pascal's triangle, the concept boxes, the worked examples, the identities and data
printed inside textbook, past-paper and review questions). Each value is found with a template
('@' marks the printed LaTeX); a template must match exactly once in its block, otherwise the
item FAILS. Printed LaTeX (including {}^nC_r, \\dbinom and n!) is converted to a sympy
expression and compared with an independent computation:
  - binomial coefficients are counted as subsets (itertools) for m <= 18, otherwise built in
    Pascal's triangle by addition; expansions are built by repeated multiplication;
  - every identity printed in the lesson, the exercise, the review or a past paper is checked by
    brute force over a range of n (and r, m, k), with the sum, product or coefficient computed
    directly from the expansion or by enumerating subsets, words or committees;
  - printed identities in terms of n and r are evaluated on a grid of whole numbers;
  - lists of subsets are compared with itertools enumerations.
It also checks the lesson fragment: past-paper marks add to the intro total (15-22), time is
1.5 x marks rounded to 5 minutes, numbering and source labels match in both files, one hint per
question, exercise numbering and bands, and the review numbering.

Exit status 1 if anything fails. Run: python3 workspace/checks/y11ch15_15d.py
"""
import itertools
import math
import os
import re
import sys
from fractions import Fraction

import sympy as sp
from sympy.parsing.sympy_parser import (parse_expr, standard_transformations,
                                        implicit_multiplication_application)

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.environ.get("Y11CH15_SRC", os.path.join(HERE, "..", "build", "y11ch15"))
FAILS = []
x, y, a, b, n, p, q, k, r, m = sp.symbols("x y a b n p q k r m")
SYMS = {"x": x, "y": y, "a": a, "b": b, "n": n, "p": p, "q": q, "k": k, "r": r, "m": m,
        "binomial": sp.binomial, "factorial": sp.factorial}
TR = standard_transformations + (implicit_multiplication_application,)


def read(name):
    with open(os.path.join(SRC, name), encoding="utf-8") as f:
        return f.read()


def report(ok, label, detail=""):
    print(("OK       " if ok else "MISMATCH ") + str(label).replace("\n", " ")[:110] + "  " + str(detail).replace("\n", " ")[:170])
    if not ok:
        FAILS.append(label)


_PASCAL = [[1]]


def ncr(m, r):
    """Number of r-subsets of an m-set: brute-force enumeration for m <= 18, otherwise
    Pascal's triangle built by addition (rows checked against enumeration up to 18)."""
    if r < 0 or r > m:
        return 0
    if m <= 18:
        return sum(1 for _ in itertools.combinations(range(m), r))
    while len(_PASCAL) <= m:
        prev = _PASCAL[-1]
        _PASCAL.append([1] + [prev[i] + prev[i + 1] for i in range(len(prev) - 1)] + [1])
    return _PASCAL[m][r]


def power(base, e):
    """(base)^e by repeated multiplication."""
    res = sp.Integer(1)
    for _ in range(e):
        res = sp.expand(res * base)
    return res


def deg(t, var):
    return sp.degree(t * var ** 200, var) - 200


def term(e, j, var=x):
    return sp.Add(*[t for t in sp.Add.make_args(sp.expand(e)) if deg(t, var) == j])


# ---------------------------------------------------------------- LaTeX -> sympy
def _arg(t, i):
    while t[i] == " ":
        i += 1
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
        elif t.startswith(("\\dbinom", "\\binom"), i):
            i = t.index("binom", i) + 5
            u, i = _arg(t, i)
            v, i = _arg(t, i)
            out.append(f" binomial({_conv(u)},{_conv(v)})")
        elif t.startswith("\\NCR", i):            # placeholder made by clean(): \NCR{n}{r}
            u, i = _arg(t, i + 4)
            v, i = _arg(t, i)
            out.append(f" binomial({_conv(u)},{_conv(v)})")
        elif t.startswith("\\sqrt", i):
            u, i = _arg(t, i + 5)
            out.append(f" sqrt({_conv(u)})")
        elif t.startswith("\\times", i):
            out.append("*")
            i += 6
        elif t.startswith("\\div", i):
            out.append("/")
            i += 4
        elif t[i] == "^":
            u, i = _arg(t, i + 1)
            out.append(f"**({_conv(u)})")
        elif t[i] == "\\":
            raise ValueError(f"unknown macro in {t!r}")
        elif t[i] in "{}":
            out.append("(" if t[i] == "{" else ")")
            i += 1
        elif t[i] == "!":
            out.append("!")
            i += 1
        else:
            out.append(t[i])
            i += 1
    return "".join(out)


def clean(t):
    t = re.sub(r"\{\}\^(\{[^{}]*\}|\w)C_(\{[^{}]*\}|\w)", r"\\NCR{\1}{\2}", t)
    t = re.sub(r"\\left|\\right|\\bigg|\\Big|\\big|\\qquad|\\quad|\\,|\\;|\\!|&nbsp;|\s", "", t)
    return re.sub(r"[+-]?\\cdots", "", t).replace("{}", "")


def tex(t):
    """Printed LaTeX -> sympy expression (n! is read as factorial(n))."""
    s = _conv(clean(t))
    s = re.sub(r"(\w+|\([^()]*\))!", r"factorial(\1)", s)
    return parse_expr(s, local_dict=dict(SYMS), transformations=TR)


def same(u, v):
    d = sp.expand_func(sp.expand(u - v))
    if sp.simplify(sp.combsimp(d)) == 0:
        return True
    if n in d.free_symbols:                    # results in terms of n: test whole numbers
        return all(sp.simplify(d.subs(n, nn)) == 0 for nn in range(4, 13))
    return False




# ---------------------------------------------------------------- templates
def grab(block, template, where=""):
    pieces = template.split("@")
    cap = r"((?:(?!\\\)|\\\]|\\\\&).)+?)"
    rx = "".join(re.escape(pc) + (cap if i < len(pieces) - 1 else "") for i, pc in enumerate(pieces))
    found = re.findall(rx, block, re.S)
    if len(found) != 1:
        raise LookupError(f"template matched {len(found)} times in {where}: {template!r}")
    return found[0] if isinstance(found[0], tuple) else (found[0],)


def once(block, text, label):
    c = block.count(text)
    report(c == 1, label, f"printed text found {c} time(s): {text[:90]}")
    return c == 1


def grid_ok(expr, target, nr=range(0, 11), cond=lambda nn, rr, mm: True, extra=None):
    """expr (sympy, in n, r, m, k) equals target(nn, rr, mm) for all whole numbers on a grid."""
    for nn in nr:
        for rr in range(0, nn + 2):
            for mm in (range(0, 7) if m in expr.free_symbols else [0]):
                if not cond(nn, rr, mm):
                    continue
                sub = {n: nn, r: rr, k: rr, m: mm}
                try:
                    v = sp.nsimplify(sp.expand_func(sp.combsimp(expr.subs(sub))))
                except Exception:
                    return False
                if sp.simplify(v - target(nn, rr, mm)) != 0:
                    return False
    return True


def chain(block, template, expected, where, min_sides=2):
    """Printed 'A=B=C' (one '@'): every side equals expected (a number or sympy expression)."""
    label = f"{where}: {template[:60]}"
    try:
        (g,) = grab(block, template, where)
        sd = [t.rstrip(".,") for t in g.split("=") if t.strip()]
        ok = len(sd) >= min_sides and all(same(tex(t), expected) for t in sd)
        report(ok, label, "printed " + g)
    except Exception as err:
        report(False, label, f"ERROR {err}")


def eqn(block, template, lhs_val, rhs_val, where):
    """Printed 'L=R' (one '@'): L equals lhs_val and R equals rhs_val."""
    label = f"{where}: {template[:60]}"
    try:
        (g,) = grab(block, template, where)
        lh, rh = g.rstrip(".,").split("=")
        report(same(tex(lh), lhs_val) and same(tex(rh), rhs_val), label, "printed " + g)
    except Exception as err:
        report(False, label, f"ERROR {err}")


def aligned_rows(block, lead, where):
    if block.count(lead) != 1:
        raise LookupError(f"lead {lead!r} found {block.count(lead)} times in {where}")
    body = re.search(r"\\begin\{aligned\}(.*?)\\end\{aligned\}", block.split(lead)[1], re.S).group(1)
    return [rw.strip() for rw in body.split("\\\\")]


def nc(mm, rr):
    return sp.Integer(ncr(mm, rr))


def sets_in(text):
    """All printed sets \\{A,B\\} in text, as frozensets of letters."""
    return [frozenset(s.split(",")) for s in re.findall(r"\\\{([A-E](?:,[A-E])*)\\\}", text)]


def fr(t):
    return Fraction(str(sp.nsimplify(tex(t))))


# ---------------------------------------------------------------- HTML blocks
ans = read("a_15d.html")
les = read("l15d.html")
report(ans.count("{{ahead:Lesson 15D | Identities in Pascal's triangle}}") == 2, "answers headings", "{{ahead:Lesson 15D | ...}} twice")
report(ans.count('<div class="ans-sec">{{ahead:Chapter 15 Review | Chapter review exercise}}</div>') == 1, "review answers heading", "once, as in the Ch 10 model")
try:
    a_les, rest = ans.split('<div class="ans-sec">{{ahead:Chapter 15 Review | Chapter review exercise}}</div>')
    a_rev, a_pp = rest.split('<div class="ans-sec">Past-Paper Homework - Worked Solutions</div>')
except ValueError:
    sys.exit("FAIL: answer sections not found in a_15d.html")


def blocks(text):
    out = {}
    for mt in re.finditer(r'<div class="a"><span class="an">([^<]+)</span><div class="ab"[^>]*>(.*?)(?=<div class="a"><span class="an">|<div class="ans-sec">|\{\{ahead|$)', text, re.S):
        if mt.group(1) in out:
            report(False, f"block {mt.group(1)}", "duplicate answer number")
        out[mt.group(1)] = mt.group(2)
    return out


BLK = blocks(a_les)
RBLK = blocks(a_rev)
PPA = {int(kk): v for kk, v in re.findall(r'<div class="ppa"><div class="pp-src"><span><span class="pn">PP (\d+)</span>(.*?)(?=<div class="ppa">|$)', a_pp, re.S)}
pre_hw, hw_rest = les.split("<!-- ============ Homework ============ -->")
hw, pp_rest = hw_rest.split("<!-- ============ Past papers ============ -->")
pp_les, rev_les = pp_rest.split("<!-- ============ Chapter review ============ -->")
PPQ = {int(kk): v for kk, v in re.findall(r'<div class="pp"><div class="pp-src"><span><span class="pn">PP (\d+)</span>(.*?)(?=<div class="pp">|$)', pp_les, re.S)}
TQ = {kk: v for kk, v in re.findall(r'<div class="q"><span class="q-num">(\d+)</span>(.*?)(?=<div class="q">|\{\{band|<div class="page-break|$)', hw, re.S)}
RQ = {kk: v for kk, v in re.findall(r'<div class="q"><span class="q-num">(\d+)</span>(.*?)(?=<div class="q">|$)', rev_les, re.S)}
C1, C2, C3 = (pre_hw.split(f"<!-- ============ Concept {i} ============ -->")[1].split("<!-- ============")[0] for i in (1, 2, 3))


def exblock(conc, tag):
    parts_ = re.findall(r'<div class="ex ' + tag + r'">(.*?)(?=<div class="ex |$)', conc, re.S)
    if len(parts_) != 1:
        raise LookupError(f"{tag} block found {len(parts_)} times")
    return parts_[0]


def row_sum(nn, f=lambda rr: 1):
    return sum(f(rr) * ncr(nn, rr) for rr in range(nn + 1))


# ================================================================ lesson: Concept 1
try:
    rows = re.findall(r"<tr><th>(\d+)</th>(.*?)</tr>", C1.split("table class=\"t pt\"")[1].split("</table>")[0])
    ok = [int(rw[0]) for rw in rows] == list(range(11))
    for nn, cells in rows:
        vals = [int(v) for v in re.findall(r"<td>(\d+)</td>", cells)]
        ok &= vals == [ncr(int(nn), rr) for rr in range(int(nn) + 1)] and cells.count("<td></td>") == 10 - int(nn)
    report(ok, "lesson table rows 0-10 = subset counts", f"{len(rows)} rows")
except Exception as err:
    report(False, "lesson table", f"ERROR {err}")
take = C1.split('<div class="bt">The sum of a row</div>')[1].split("</div>")[0]
once(take, r"\[{}^nC_0+{}^nC_1+{}^nC_2+\cdots+{}^nC_n=2^n.\]", "C1 box: row sum identity")
report(all(row_sum(nn) == 2 ** nn for nn in range(0, 19)), "row sum identity, n = 0..18 (subsets)", "")
chain(take, r"adds to \(@\). The worked", sp.Integer(row_sum(5)), "C1 box", 3)
try:
    (g,) = grab(take, r"adds to \(@\). The worked", "C1 box")
    report(g.split("=")[0] == "+".join(str(ncr(5, rr)) for rr in range(6)), "C1 box: the printed row is row 5", g)
except Exception as err:
    report(False, "C1 box row 5", f"ERROR {err}")
once(C1, r"\[(x+y)^n={}^nC_0\,x^ny^0+{}^nC_1\,x^{n-1}y^1+{}^nC_2\,x^{n-2}y^2+\cdots+{}^nC_n\,x^0y^n,\]", "C1 methods: binomial expansion")
report(all(sp.expand(power(x + y, nn) - sum(ncr(nn, rr) * x ** (nn - rr) * y ** rr for rr in range(nn + 1))) == 0 for nn in range(0, 10)), "binomial expansion, n = 0..9", "")
# worked example (the textbook's three proofs)
W1 = exblock(C1, "worked")
report(all(sum(1 for _ in itertools.product((0, 1), repeat=nn)) == 2 ** nn == sum(1 for rr in range(nn + 1) for _ in itertools.combinations(range(nn), rr)) for nn in range(0, 12)),
       "W1 combinatorics: in/out choices = all subsets = 2^n, n = 0..11", "")
once(W1, r"\[2^n={}^nC_0+{}^nC_1+{}^nC_2+\cdots+{}^nC_n.\]", "W1 substitution result")
report(all(power(1 + x, nn).subs(x, 1) == 2 ** nn for nn in range(12)), "W1 substitute x = y = 1", "")
# addition-property argument: each entry used twice, so each row sum doubles
_rows = [[1]]
for _ in range(15):
    pr = [0] + _rows[-1] + [0]
    _rows.append([pr[i] + pr[i + 1] for i in range(len(pr) - 1)])
report(all(sum(_rows[i + 1]) == 2 * sum(_rows[i]) for i in range(15)) and _rows[0] == [1] and all(_rows[i] == [ncr(i, j) for j in range(i + 1)] for i in range(16)),
       "W1 addition property: row sum doubles, row 0 is 1", "")
# demo and your turn
for tag, c, nn_check, val in (("demo", 3, 4, 8), ("attempt", 4, 3, 9)):
    blk = exblock(C1, tag)
    lhs = r"{}^nC_0+%d\,{}^nC_1+%d\,{}^nC_2+\cdots+%d^n\,{}^nC_n=%d^n" % (c, c * c, c, c + 1)
    once(blk, lhs, f"C1 {tag} identity")
    report(all(row_sum(nn, lambda rr: c ** rr) == (c + 1) ** nn for nn in range(0, 16)), f"C1 {tag}: sum {c}^r nCr = {c+1}^n, n = 0..15", "")
C1t, C1y = BLK["C1"].split("<b>Your turn.</b>")
for half, c, nn, pair in ((C1t, 3, 4, (8, 3, 5)), (C1y, 4, 3, (9, 2, 7))):
    once(half, r"\(%d^n={}^nC_0+%d\,{}^nC_1+%d\,{}^nC_2+\cdots+%d^n\,{}^nC_n\)" % (c + 1, c, c * c, c), f"AC1 identity c = {c}")
    once(half, r"Because \(1+%d=%d\)" % (c, c + 1), f"AC1 1 + {c}")
    chain(half, r"<b>b</b> \(@\)<br>", sp.Integer(row_sum(nn, lambda rr: c ** rr)), f"AC1 b (c = {c})", 4)
    try:
        (g,) = grab(half, r"<b>b</b> \(@\)<br>", "AC1 b")
        first = g.split("=")[0]
        terms = first.split("+")
        report(len(terms) == nn + 1 and all(same(tex(t), c ** j * ncr(nn, j)) for j, t in enumerate(terms)), f"AC1 b terms are {c}^r x {nn}Cr", first)
    except Exception as err:
        report(False, "AC1 b terms", f"ERROR {err}")
    N, r1, r2 = pair
    chain(half, r"and \(@\).", sp.Integer(ncr(N, r1)), f"AC1 c {N}C{r1}", 3)
    try:
        (g,) = grab(half, r"and \(@\).", "AC1 c")
        report(g.split("=")[0] == f"{{}}^{N}C_{r1}" and g.split("=")[1] == f"{{}}^{N}C_{r2}" and ncr(N, r1) == ncr(N, r2), f"AC1 c pairs {r1}-subsets with {r2}-subsets", g)
        report(f"Choosing {r1} of the {N} elements" in half and f"leaves the other {r2} out" in half, f"AC1 c wording numbers {r1}, {N}, {r2}", "")
    except Exception as err:
        report(False, "AC1 c", f"ERROR {err}")

# ================================================================ lesson: Concept 2
for tag, N in (("demo", 5), ("attempt", 3)):
    blk = exblock(C2, tag)
    e = power(1 + x, N)
    try:
        (g,) = grab(blk, r"\[(1+x)^%d=@.\]" % N, f"C2 {tag}")
        report(same(tex(g), e) and g.count("C_") == N + 1, f"C2 {tag}: expansion of (1+x)^{N}", g)
        d = sp.diff(e, x)
        g1, g2 = grab(blk, r"<b>a</b> \(x=1\), to show that \(@=@\),<br>", f"C2 {tag}")
        report(same(tex(g1), d.subs(x, 1)) and same(tex(g2), d.subs(x, 1)), f"C2 {tag} a: derivative at 1", f"{g1} = {g2}")
        g1, g2 = grab(blk, r"<b>b</b> \(x=-1\), to show that \(@=@\).<br>", f"C2 {tag}")
        report(same(tex(g1), d.subs(x, -1)) and same(tex(g2), d.subs(x, -1)), f"C2 {tag} b: derivative at -1", f"{g1} = {g2}")
        (g,) = grab(blk, r"Check both results on the row \(@\).", f"C2 {tag}")
        report([int(v) for v in re.findall(r"\d+", g)] == [ncr(N, rr) for rr in range(N + 1)], f"C2 {tag}: row {N}", g)
    except Exception as err:
        report(False, f"C2 {tag}", f"ERROR {err}")
W2 = exblock(C2, "worked")
once(W2, r"\[1\times{}^nC_1+2\times2\times{}^nC_2+3\times2^2\times{}^nC_3+\cdots+n\times2^{n-1}\times{}^nC_n=n\times3^{n-1}.\]", "W2 identity")
once(W2, r"\[n(1+x)^{n-1}={}^nC_1+2\times{}^nC_2\,x+3\times{}^nC_3\,x^2+\cdots+n\times{}^nC_n\,x^{n-1}.\]", "W2 derivative")
once(W2, r"\[n\times3^{n-1}=1\times{}^nC_1+2\times2\times{}^nC_2+3\times2^2\times{}^nC_3+\cdots+n\times2^{n-1}\times{}^nC_n.\]", "W2 after x = 2")
report(all(sp.diff(power(1 + x, nn), x) == sp.expand(sum(rr * ncr(nn, rr) * x ** (rr - 1) for rr in range(1, nn + 1))) for nn in range(1, 12)), "W2 derivative of expansion, n = 1..11", "")
report(all(row_sum(nn, lambda rr: rr * 2 ** (rr - 1) if rr else 0) == nn * 3 ** (nn - 1) for nn in range(1, 16)), "W2 identity brute force, n = 1..15", "")
try:
    rw = aligned_rows(W2, "is \\(1\\ \\,3\\ \\,3\\ \\,1\\), so</p>", "W2")
    l1 = rw[0].replace("\\text{LHS}&=", "").rstrip(",.").split("=")
    r1 = rw[1].replace("\\text{RHS}&=", "").rstrip(",.").split("=")
    target = row_sum(3, lambda rr: rr * 2 ** (rr - 1) if rr else 0)
    report(len(rw) == 2 and all(same(tex(t), target) for t in l1) and all(same(tex(t), 3 * 3 ** 2) for t in r1) and target == 27, "W2 check n = 3", " | ".join(rw))
except Exception as err:
    report(False, "W2 check", f"ERROR {err}")
C2t, C2y = BLK["C2"].split("<b>Your turn.</b>")
for half, N in ((C2t, 5), (C2y, 3)):
    e = power(1 + x, N)
    d = sp.diff(e, x)
    try:
        (g,) = grab(half, r"\(%d(1+x)^%d=@\)<br>" % (N, N - 1), f"AC2 n={N}")
        report(same(tex(g), d) and same(tex(f"{N}(1+x)^{N-1}"), d), f"AC2 n={N} derivative", g)
    except Exception as err:
        report(False, f"AC2 n={N} derivative", f"ERROR {err}")
    for part, xv in (("a", 1), ("b", -1)):
        chain(half, r"<b>%s</b> \(x=%d\): \(@\). Check:" % (part, xv), d.subs(x, xv), f"AC2 n={N} {part}")
        try:
            mt = re.search(r"<b>%s</b> \\\(x=%s\\\): \\\((.*?)\\\)\. Check: \\\((.*?)\\\)\." % (part, re.escape(str(xv))), half)
            sides = mt.group(2).split("=")
            terms = re.split(r"(?=[+-])", sides[0])
            ok = len(sides) == 2 and same(tex(sides[0]), d.subs(x, xv)) and same(tex(sides[1]), d.subs(x, xv))
            ok &= len(terms) == N and all(same(tex(t), (j + 1) * ncr(N, j + 1) * xv ** j) for j, t in enumerate(terms))
            report(ok, f"AC2 n={N} {part} check row", mt.group(2))
        except Exception as err:
            report(False, f"AC2 n={N} {part} check", f"ERROR {err}")

# ================================================================ lesson: Concept 3
T3 = exblock(C3, "demo")
Y3 = exblock(C3, "attempt")
W3 = exblock(C3, "worked")
once(T3, r"\(r\times{}^nC_r=n\times{}^{n-1}C_{r-1}\), for \(1\le r\le n\)", "C3 demo a")
report(all(rr * ncr(nn, rr) == nn * ncr(nn - 1, rr - 1) for nn in range(1, 16) for rr in range(1, nn + 1)), "C3 demo a brute force", "")
once(Y3, r"\((n-r)\times{}^nC_r=n\times{}^{n-1}C_r\), for \(0\le r\le n-1\)", "C3 your turn a")
report(all((nn - rr) * ncr(nn, rr) == nn * ncr(nn - 1, rr) for nn in range(1, 16) for rr in range(0, nn)), "C3 your turn a brute force", "")
for blk, j, cond, label in ((T3, 2, 2, "demo"), (Y3, 3, 3, "attempt")):
    once(blk, r"\((1+x)^2(1+x)^n=(1+x)^{n+2}\)", f"C3 {label} b identity of polynomials")
    lhs = {2: r"{}^nC_2+2\,{}^nC_1+{}^nC_0={}^{n+2}C_2", 3: r"{}^nC_3+2\,{}^nC_2+{}^nC_1={}^{n+2}C_3"}[j]
    once(blk, r"\(%s\), for \(n\ge%d\)" % (lhs, cond), f"C3 {label} b")
    report(all(sp.expand(power(1 + x, 2) * power(1 + x, nn)).coeff(x, j) == ncr(nn, j) + 2 * ncr(nn, j - 1) + ncr(nn, j - 2) == ncr(nn + 2, j) for nn in range(cond, 15)),
           f"C3 {label} b: coefficient of x^{j}, brute force", "")
once(W3, r"\(\dfrac{{}^nC_{r+1}}{{}^nC_r}=\dfrac{n-r}{r+1}\), for \(0\le r\le n-1\)", "W3 a")
report(all(Fraction(ncr(nn, rr + 1), ncr(nn, rr)) == Fraction(nn - rr, rr + 1) for nn in range(1, 16) for rr in range(0, nn)), "W3 a brute force", "")
try:
    rw = [re.sub(r"^(\\dfrac\{\{\}\^nC_\{r\+1\}\}\{\{\}\^nC_r\})?&=", "", t).rstrip(".,") for t in aligned_rows(W3, "\\((n-r)!=(n-r)\\times(n-r-1)!\\),</p>", "W3")]
    ok = len(rw) == 3 and all(grid_ok(tex(t), lambda nn, rr, mm: Fraction(nn - rr, rr + 1), range(1, 11), lambda nn, rr, mm: rr <= nn - 1) for t in rw)
    report(ok, "W3 a rows on grid 0 <= r <= n-1", " | ".join(rw))
except Exception as err:
    report(False, "W3 a rows", f"ERROR {err}")
once(W3, r"\({}^mC_2+{}^mC_1\times{}^nC_1+{}^nC_2={}^{m+n}C_2\), for \(m\ge2\) and \(n\ge2\)", "W3 b")
report(all(sp.expand(power(1 + x, mm) * power(1 + x, nn)).coeff(x, 2) == ncr(mm, 2) + ncr(mm, 1) * ncr(nn, 1) + ncr(nn, 2) == ncr(mm + nn, 2) for mm in range(2, 9) for nn in range(2, 9)),
       "W3 b brute force m, n = 2..8", "")
once(W3, r"=\cdots+\big({}^mC_0\times{}^nC_2+{}^mC_1\times{}^nC_1+{}^mC_2\times{}^nC_0\big)x^2+\cdots", "W3 b coefficient of x^2 on the left")
chain(W3, r"the LHS is \(@\), and", sp.Integer(ncr(3, 2) + 3 * 4 + ncr(4, 2)), "W3 b check")
chain(W3, r"and the RHS is \(@\).</p>", sp.Integer(ncr(7, 2)), "W3 b check RHS")
# answers C3
C3t, C3y = BLK["C3"].split("<b>Your turn.</b>")
for half, target, cond, label in ((C3t, lambda nn, rr, mm: rr * ncr(nn, rr), lambda nn, rr, mm: 1 <= rr <= nn, "tutor a"),
                                  (C3y, lambda nn, rr, mm: (nn - rr) * ncr(nn, rr), lambda nn, rr, mm: 0 <= rr <= nn - 1, "your turn a")):
    try:
        (g,) = grab(half, r"<b>a</b> \(@\)", f"AC3 {label}")
        sd = g.split("=")
        report(len(sd) == 4 and all(grid_ok(tex(t), target, range(1, 11), cond) for t in sd), f"AC3 {label} chain on grid", g)
    except Exception as err:
        report(False, f"AC3 {label}", f"ERROR {err}")
eqn(C3t, r"<b>b</b> \(@\). On the left", sp.expand(power(1 + x, 2)), sp.expand(power(1 + x, 2)), "AC3 tutor b")
for half, j, nn, label in ((C3t, 2, 3, "tutor"), (C3y, 3, 4, "your turn")):
    try:
        g1, g2 = grab(half, r"the coefficient of \(x^%d\) is \(@\). On the right it is \(@\)." % j, f"AC3 {label}")
        okk = all(tex(g1).subs(n, v) == sp.expand(power(1 + x, 2) * power(1 + x, v)).coeff(x, j) and tex(g2).subs(n, v) == ncr(v + 2, j) for v in range(j, 13))
        report(okk, f"AC3 {label} b coefficients, n = {j}..12", f"{g1} | {g2}")
    except Exception as err:
        report(False, f"AC3 {label} b", f"ERROR {err}")
    chain(half, r"Check: \(@\).", sp.Integer(ncr(nn + 2, j)), f"AC3 {label} check n = {nn}", 3)
    try:
        (g,) = grab(half, r"Check: \(@\).", f"AC3 {label}")
        ts = g.split("=")[0].split("+")
        report([int(t) for t in ts] == [ncr(nn, j), 2 * ncr(nn, j - 1), ncr(nn, j - 2)], f"AC3 {label} check terms from row {nn}", g)
    except Exception as err:
        report(False, f"AC3 {label} check terms", f"ERROR {err}")

# ================================================================ identities printed in the textbook questions
report(sorted(TQ, key=int) == [str(i) for i in range(1, 15)], "textbook questions 1-14", f"{sorted(TQ, key=int)}")
report(hw.count("{{band:F}}") == hw.count("{{band:D}}") == hw.count("{{band:E}}") == 1 and hw.index('q-num">3<') < hw.index("{{band:D}}") < hw.index('q-num">4<')
       and hw.index('q-num">10<') < hw.index("{{band:E}}") < hw.index('q-num">11<'), "bands F 1-3, D 4-10, E 11-14", "")
e4 = power(1 + x, 4)
d4 = sp.diff(e4, x)
try:
    (g,) = grab(TQ["1"], r"\[(1+x)^4=@,\qquad(*)\]", "Q1")
    report(same(tex(g), e4), "Q1 (*) expansion", g)
    for templ, val in ((r"(i) By substituting \(x=1\), show that \(@=@\).", (e4.subs(x, 1),) * 2),
                       (r"(ii) By substituting \(x=1\), show that \(@=@\).", (d4.subs(x, 1),) * 2),
                       (r"(iii) By substituting \(x=-1\), show that \(@=@\).</span>", (d4.subs(x, -1),) * 2),
                       (r"(iii) Hence, by using the result of part (i), show that \(@=@\).", (sp.Integer(1 + 6 + 1),) * 2)):
        g1, g2 = grab(TQ["1"], templ, "Q1")
        report(same(tex(g1), val[0]) and same(tex(g2), val[1]), f"Q1 {templ[:40]}", f"{g1} = {g2}")
    g1, g2 = grab(TQ["1"], r"(ii) By substituting \(x=-1\), show that \(@=@\).<br>", "Q1")
    report(same(tex(g1), ncr(4, 0) + ncr(4, 2) + ncr(4, 4)) and same(tex(g2), ncr(4, 1) + ncr(4, 3)) and e4.subs(x, -1) == 0, "Q1 a(ii)", f"{g1} = {g2}")
except Exception as err:
    report(False, "Q1", f"ERROR {err}")
for nn in range(1, 16):
    ev = sum(ncr(nn, rr) for rr in range(0, nn + 1, 2))
    od = sum(ncr(nn, rr) for rr in range(1, nn + 1, 2))
    assert ev == od == 2 ** (nn - 1), nn
report(True, "Q2a, Q8: even and odd sums equal 2^(n-1), n = 1..15", "")
report(all(row_sum(nn, lambda rr: rr) == nn * 2 ** (nn - 1) for nn in range(1, 16)) and all(row_sum(nn, lambda rr: (-1) ** (rr - 1) * rr) == 0 for nn in range(2, 16)),
       "Q2b(ii)(iii), Q13a review: sum r nCr = n 2^(n-1); alternating sum = 0 (n >= 2)", "")
for txt, lab in ((r"\({}^nC_0+{}^nC_1+\cdots+{}^nC_n=2^n\)", "Q2a(i)"), (r"\({}^nC_0+{}^nC_2+{}^nC_4+\cdots={}^nC_1+{}^nC_3+{}^nC_5+\cdots\)", "Q2a(ii)"),
                 (r"\({}^nC_0+{}^nC_2+{}^nC_4+\cdots=2^{n-1}\)", "Q2a(iii)"), (r"\(1\times{}^nC_1+2\times{}^nC_2+\cdots+n\times{}^nC_n=n2^{n-1}\)", "Q2b(ii)"),
                 (r"\(1\times{}^nC_1-2\times{}^nC_2+\cdots+(-1)^{n-1}n\times{}^nC_n=0\)", "Q2b(iii)")):
    once(TQ["2"], txt, lab)
once(TQ["2"], r"the row \(1\ \,5\ \,10\ \,10\ \,5\ \,1\) indexed by \(n=5\)", "Q2 row 5 printed")
report([1, 5, 10, 10, 5, 1] == [ncr(5, rr) for rr in range(6)] and [1, 4, 6, 4, 1] == [ncr(4, rr) for rr in range(5)], "rows 4 and 5", "")
for txt, lab in ((r"\({}^{2n}C_0+{}^{2n}C_1+\cdots+{}^{2n}C_{2n}=2^{2n}\)", "Q3a(i)"), (r"\({}^{2n}C_1+{}^{2n}C_3+{}^{2n}C_5+\cdots+{}^{2n}C_{2n-1}=2^{2n-1}\)", "Q3a(ii)"),
                 (r"\(1\times{}^{2n}C_1+2\times{}^{2n}C_2+\cdots+2n\times{}^{2n}C_{2n}=n2^{2n}\)", "Q3b(i)"),
                 (r"\(1\times{}^{2n}C_1-2\times{}^{2n}C_2+\cdots+(-1)^{2n-1}2n\times{}^{2n}C_{2n}=0\)", "Q3b(ii)")):
    once(TQ["3"], txt, lab)
report(all(row_sum(2 * v) == 2 ** (2 * v) and sum(ncr(2 * v, rr) for rr in range(1, 2 * v, 2)) == 2 ** (2 * v - 1)
           and row_sum(2 * v, lambda rr: rr) == v * 2 ** (2 * v) and row_sum(2 * v, lambda rr: (-1) ** (rr - 1) * rr) == 0 for v in range(1, 9)), "Q3 identities, n = 1..8", "")
once(TQ["4"], r"\({}^5C_2={}^5C_3\)", "Q4d")
report(ncr(5, 2) == ncr(5, 3) and all(ncr(nn, rr) == ncr(nn, nn - rr) for nn in range(16) for rr in range(nn + 1)), "Q4d,e symmetry, n = 0..15", "")
once(TQ["5"], r"\(\dbinom40+\dbinom41+\dbinom42+\dbinom43+\dbinom44=2^4\)", "Q5b")
once(TQ["5"], r"\(\dbinom n0+\dbinom n1+\cdots+\dbinom nn=2^n\)", "Q5c")
eqn(TQ["6"], r"Hence explain why \(@\).</span>", nc(4, 2) + nc(4, 3), nc(5, 3), "Q6c")
once(TQ["6"], r"\({}^nC_{r-1}+{}^nC_r={}^{n+1}C_r\), for any whole numbers \(n\) and \(r\) with \(1\le r\le n\)", "Q6d")
report(all(ncr(nn, rr - 1) + ncr(nn, rr) == ncr(nn + 1, rr) for nn in range(1, 17) for rr in range(1, nn + 1)), "Q6d, Q10b, Q13 addition property, n = 1..16", "")
once(TQ["7"], r"\[\dfrac{a}{a+b}+\dfrac{c}{c+d}=\dfrac{2b}{b+c}.\]", "Q7 identity")
report(all(Fraction(ncr(nn, j), ncr(nn, j) + ncr(nn, j + 1)) + Fraction(ncr(nn, j + 2), ncr(nn, j + 2) + ncr(nn, j + 3)) == Fraction(2 * ncr(nn, j + 1), ncr(nn, j + 1) + ncr(nn, j + 2))
           for nn in range(3, 17) for j in range(0, nn - 2)), "Q7 identity on every 4 consecutive terms, rows 3..16", "")
once(TQ["7"], r"\(1,\ 7,\ 21,\ 35,\ 35,\ 21,\ 7,\ 1\) indexed by \(n=7\)", "Q7a row 7")
report([1, 7, 21, 35, 35, 21, 7, 1] == [ncr(7, rr) for rr in range(8)], "row 7", "")
once(TQ["8"], r"&{}^nC_0+{}^nC_1+{}^nC_2+{}^nC_3+\cdots=2^n.&&(1)", "Q8 (1)")
once(TQ["8"], r"&{}^nC_0-{}^nC_1+{}^nC_2-{}^nC_3+\cdots=0,\ \text{for }n\ge1.&&(2)", "Q8 (2)")
report(all(row_sum(nn, lambda rr: (-1) ** rr) == 0 for nn in range(1, 17)), "Q8 (2) n = 1..16", "")
try:
    pairs_ok = True
    for nn in range(1, 9):
        subsets = [frozenset(c) for rr in range(nn + 1) for c in itertools.combinations(range(nn), rr)]
        without = [s_ for s_ in subsets if 0 not in s_]
        partners = {s_ | {0} for s_ in without}
        pairs_ok &= len(partners) == len(without) and set(without) | partners == set(subsets) and all(len(s_) % 2 != len(s_ | {0}) % 2 for s_ in without)
    report(pairs_ok, "Q8b pairing U with U u {A} covers all subsets once, parities differ, n = 1..8", "")
except Exception as err:
    report(False, "Q8b", f"ERROR {err}")
chain(TQ["9"], r"\[@.\qquad(*)\]", nc(7, 3), "Q9 (*)", 3)
try:
    (g,) = grab(TQ["9"], r"\[@.\qquad(*)\]", "Q9")
    report([tex(t) for t in g.split("=")[0].split("+")] == [nc(j, 2) for j in range(2, 7)] and [int(t) for t in g.split("=")[1].split("+")] == [ncr(j, 2) for j in range(2, 7)], "Q9 (*) terms", g)
except Exception as err:
    report(False, "Q9 (*) terms", f"ERROR {err}")
once(TQ["9"], r"\[{}^rC_r+{}^{r+1}C_r+{}^{r+2}C_r+\cdots+{}^nC_r={}^{n+1}C_{r+1}\qquad(**)\]", "Q9 (**)")
report(all(sum(ncr(j, rr) for j in range(rr, nn + 1)) == ncr(nn + 1, rr + 1) for nn in range(0, 17) for rr in range(0, nn + 1)), "Q9 hockey stick, 0 <= r <= n <= 16", "")
eqn(TQ["9"], r'padding:1mm 0">\(@\),</span>', nc(7, 3), nc(6, 3) + nc(6, 2), "Q9a(i) 7C3 = 6C3 + 6C2")
chain(TQ["9"], r"the fact that \(@\).<br>", sp.Integer(1), "Q9a(i) 3C3 = 2C2 = 1", 3)
try:
    cnt = {kk: sum(1 for c in itertools.combinations(range(1, 8), 3) if max(c) == kk) for kk in range(1, 8)}
    report([kk for kk, v in cnt.items() if v] == [3, 4, 5, 6, 7] and all(cnt[kk] == ncr(kk - 1, 2) for kk in range(3, 8)), "Q9b greatest element 3..7, (k-1)C2 subsets each", str(cnt))
    once(TQ["9"], r"This must be one of the numbers 3, 4, 5, 6 or 7", "Q9b printed numbers")
except Exception as err:
    report(False, "Q9b", f"ERROR {err}")
try:
    (g,) = grab(TQ["10"], r'padding:1mm 0">\(@\).</span>', "Q10")
    lh, rh = g.split("=")
    l1, l2 = re.split(r"\+(?=\\dfrac)", lh)
    ok = grid_ok(tex(lh), lambda nn, rr, mm: ncr(nn + 1, rr), range(1, 12), lambda nn, rr, mm: 1 <= rr <= nn)
    ok &= grid_ok(tex(rh), lambda nn, rr, mm: ncr(nn + 1, rr), range(1, 12), lambda nn, rr, mm: 1 <= rr <= nn)
    ok &= grid_ok(tex(l1), lambda nn, rr, mm: ncr(nn, rr), range(1, 12), lambda nn, rr, mm: 1 <= rr <= nn)
    ok &= grid_ok(tex(l2), lambda nn, rr, mm: ncr(nn, rr - 1), range(1, 12), lambda nn, rr, mm: 1 <= rr <= nn)
    report(ok, "Q10a printed identity on grid 1 <= r <= n <= 11 (terms nCr, nC(r-1), (n+1)Cr)", g)
except Exception as err:
    report(False, "Q10a", f"ERROR {err}")
once(TQ["11"], r"\[\big({}^nC_0\big)^2+\big({}^nC_1\big)^2+\big({}^nC_2\big)^2+\big({}^nC_3\big)^2+\cdots+\big({}^nC_n\big)^2={}^{2n}C_n.\]", "Q11 identity")
report(all(row_sum(nn, lambda rr: ncr(nn, rr)) == ncr(2 * nn, nn) == sp.expand(power(1 + x, nn) ** 2).coeff(x, nn) for nn in range(0, 13)), "Q11 sum of squares = 2nCn = coefficient of x^n, n = 0..12", "")
once(TQ["12"], r"\({}^{a+b}C_a={}^{a+b}C_b\)", "Q12a identity")
report(all(len(set(itertools.permutations("A" * aa + "B" * bb))) == ncr(aa + bb, aa) == ncr(aa + bb, bb) for aa in range(0, 5) for bb in range(0, 5)), "Q12a words with a As and b Bs, a, b = 0..4", "")
report("Hence prove" not in TQ["12"] and "<span class=\"pl\">d</span>" not in TQ["12"], "Q12d omitted (printed identity is false)", "")
report(sum(ncr(2, j) ** 2 for j in range(3)) != ncr(2, 1), "Q12d as printed fails at n = 1 (so it is left out)", "")
once(TQ["13"], r"\[(1+x)(1+x)^n=(1+x)^{n+1}.\]", "Q13 identity")
report(all(sp.expand((1 + x) * power(1 + x, nn)).coeff(x, rr) == ncr(nn, rr) + ncr(nn, rr - 1) == ncr(nn + 1, rr) for nn in range(1, 12) for rr in range(1, nn + 1)), "Q13 coefficients of x^r", "")
once(TQ["14"], r"\({}^{2n}C_r&lt;{}^{2n}C_{r+1}\), for all whole numbers \(n\) and \(r\) with \(r&lt;n\)", "Q14a")
once(TQ["14"], r"\({}^{2n+1}C_r&lt;{}^{2n+1}C_{r+1}\), for all whole numbers \(n\) and \(r\) with \(r&lt;n\)", "Q14b")
report(all(ncr(2 * v, rr) < ncr(2 * v, rr + 1) and ncr(2 * v + 1, rr) < ncr(2 * v + 1, rr + 1) for v in range(1, 9) for rr in range(0, v)), "Q14 inequalities, n = 1..8", "")

# ================================================================ textbook homework answers
A1 = BLK["1"]
chain(A1, r"<b>a</b> (i) \(@\)<br>", e4.subs(x, 1), "A1a(i)", 3)
try:
    g1, g2 = grab(A1, r"(ii) The sum \(@\) of the first, third and fifth terms on the row equals the sum \(@\) of the second and fourth terms.", "A1")
    report([int(t) for t in g1.split("+")] == [ncr(4, 0), ncr(4, 2), ncr(4, 4)] and [int(t) for t in g2.split("+")] == [ncr(4, 1), ncr(4, 3)] and tex(g1) == tex(g2), "A1a(ii)", f"{g1} | {g2}")
    report(2 * (ncr(4, 0) + ncr(4, 2) + ncr(4, 4)) == row_sum(4), "A1a(iii) half the row", "")
    eqn(A1, r"<b>b</b> (i) \(@\)<br>", d4, d4, "A1b(i)")
except Exception as err:
    report(False, "A1a(ii)", f"ERROR {err}")
for part, xv in (("ii", 1), ("iii", -1)):
    chain(A1, r"(%s) \(@\)" % part + ("<br>" if part == "ii" else "</div>"), d4.subs(x, xv), f"A1b({part})", 2 if xv == -1 else 3)
    try:
        (g,) = grab(A1, r"(%s) \(@\)" % part + ("<br>" if part == "ii" else "</div>"), "A1")
        terms = re.split(r"(?=[+-])", g.split("=")[0])
        report(len(terms) == 4 and all(same(tex(t), (j + 1) * ncr(4, j + 1) * xv ** j) for j, t in enumerate(terms)), f"A1b({part}) terms r x 4Cr x^(r-1)", g)
    except Exception as err:
        report(False, f"A1b({part}) terms", f"ERROR {err}")
A4 = BLK["4"]
try:
    la = A4.split("<b>a</b>")[1].split("<b>b</b>")[0]
    lb = A4.split("<b>b</b>")[1].split("<b>c</b>")[0]
    want2 = {frozenset(c) for c in itertools.combinations("ABCDE", 2)}
    want3 = {frozenset(c) for c in itertools.combinations("ABCDE", 3)}
    report(sorted(map(sorted, sets_in(la))) == sorted(map(sorted, want2)) and "There are 10:" in la and len(want2) == 10, "A4a the ten 2-letter subsets", "")
    report(sorted(map(sorted, sets_in(lb))) == sorted(map(sorted, want3)) and "There are 10:" in lb and len(want3) == 10, "A4b the ten 3-letter subsets", "")
    g = re.search(r"<b>c</b> (.*?)<br>", A4).group(1)
    report(re.findall(r"\\\(([A-E])\\\)", g) == ["C", "D", "E"] and set("ABCDE") - {"A", "B"} == {"C", "D", "E"}, "A4c letters omitted from {A,B}", g)
    eqn(A4, r"Thus \(@\).<br>", nc(5, 2), nc(5, 3), "A4d")
except Exception as err:
    report(False, "A4", f"ERROR {err}")
A5 = BLK["5"]
try:
    la = A5.split("<b>a</b>")[1].split("To form")[0]
    found = sets_in(la) + ([frozenset()] if "\\varnothing" in la else [])
    allsub = {frozenset(c) for rr in range(5) for c in itertools.combinations("ABCD", rr)}
    report(len(found) == 16 == len(allsub) and set(found) == allsub and "The 16 subsets" in la, "A5a all 16 subsets of {A,B,C,D}", f"{len(found)} printed")
    chain(A5, r"is \(@\).<br>", sp.Integer(len(allsub)), "A5a 2 x 2 x 2 x 2", 2)
except Exception as err:
    report(False, "A5", f"ERROR {err}")
A6 = BLK["6"]
try:
    pa = A6.split("<b>a</b>")[1].split("<b>b</b>")[0]
    pb = A6.split("<b>b</b>")[1].split("(ii)")[0]
    w_a = {frozenset(c) for c in itertools.combinations("ABCDE", 3) if "E" not in c}
    w_b = {frozenset(c) for c in itertools.combinations("ABCDE", 3) if "E" in c}
    report(set(sets_in(pa)) == w_a and len(sets_in(pa)) == len(w_a) == 4 and "four" in pa, "A6a(i) 3-letter subsets without E", "")
    report(set(sets_in(pb)) == w_b and len(sets_in(pb)) == len(w_b) == 6 and "six" in pb, "A6b(i) 3-letter subsets with E", "")
    report({s_ - {"E"} for s_ in w_b} == {frozenset(c) for c in itertools.combinations("ABCD", 2)}, "A6b(ii) omitting E gives the 2-letter subsets of U", "")
except Exception as err:
    report(False, "A6", f"ERROR {err}")
A7 = BLK["7"]
try:
    seqs = re.findall(r"\\\((\d+),(\d+),(\d+),(\d+)\\\): both sides are \\\((.*?)\\\)", A7)
    row7 = [ncr(7, j) for j in range(8)]
    windows = [tuple(row7[j:j + 4]) for j in range(5)]
    ok = [tuple(int(v) for v in s_[:4]) for s_ in seqs] == windows
    for s_ in seqs:
        aa, bb, cc, dd = (int(v) for v in s_[:4])
        lhs = Fraction(aa, aa + bb) + Fraction(cc, cc + dd)
        ok &= lhs == Fraction(2 * bb, bb + cc) == fr(s_[4])
    report(ok and len(seqs) == 5, "A7a the five sequences of row 7, both sides", str([s_[4] for s_ in seqs]))
    g1, g2 = grab(A7, r"\(\text{LHS}=@\) and \(\text{RHS}=@\).", "A7")
    def L(nn, rr, mm):
        A_, B_, C_, D_ = ncr(nn, rr - 1), ncr(nn, rr), ncr(nn, rr + 1), ncr(nn, rr + 2)
        return Fraction(A_, A_ + B_) + Fraction(C_, C_ + D_)
    def R(nn, rr, mm):
        B_, C_ = ncr(nn, rr), ncr(nn, rr + 1)
        return Fraction(2 * B_, B_ + C_)
    cond = lambda nn, rr, mm: 1 <= rr and rr + 2 <= nn
    report(grid_ok(tex(g1), L, range(3, 12), cond) and grid_ok(tex(g2), R, range(3, 12), cond), "A7c LHS and RHS after the addition property (grid)", f"{g1} | {g2}")
    for templ, tgt in ((r"\(\dfrac{{}^nC_{r-1}}{{}^{n+1}C_r}=@\)", lambda nn, rr, mm: Fraction(ncr(nn, rr - 1), ncr(nn + 1, rr))),
                       (r"\(\dfrac{{}^nC_{r+1}}{{}^{n+1}C_{r+2}}=@\)", lambda nn, rr, mm: Fraction(ncr(nn, rr + 1), ncr(nn + 1, rr + 2))),
                       (r"\(\dfrac{{}^nC_r}{{}^{n+1}C_{r+1}}=@\)", lambda nn, rr, mm: Fraction(ncr(nn, rr), ncr(nn + 1, rr + 1)))):
        (g,) = grab(A7, templ, "A7")
        report(grid_ok(tex(g), tgt, range(3, 12), cond), f"A7c {templ[:40]}", g)
    (g,) = grab(A7, r"so both sides equal \(@\).", "A7")
    report(grid_ok(tex(g), L, range(3, 12), cond) and grid_ok(tex(g), R, range(3, 12), cond), "A7c both sides equal", g)
except Exception as err:
    report(False, "A7", f"ERROR {err}")
A9 = BLK["9"]
try:
    rw = aligned_rows(A9, "<b>a</b> (i)", "A9")
    sides = [t for rw_ in rw for t in rw_.replace("&", "").rstrip(",.").split("=") if t]
    report(len(rw) == 3 and len(sides) == 5 and all(same(tex(t), nc(7, 3)) for t in sides), "A9a(i) expanding 7C3", " | ".join(sides))
    chain(A9, r"and \(@\).<br>", sp.Integer(1), "A9a(i) 3C3 = 2C2 = 1", 3)
    items = re.findall(r"There are \\\(\{\}\^(\d)C_2=(\d+)\\\) subsets with highest element (\d)", A9)
    cnt = {kk: sum(1 for c in itertools.combinations(range(1, 8), 3) if max(c) == kk) for kk in range(1, 8)}
    report(len(items) == 5 and all(int(v) == ncr(int(t), 2) == cnt[int(h)] and int(h) == int(t) + 1 for t, v, h in items), "A9b counts by greatest element", str(items))
    (g,) = grab(A9, r"This makes @ subsets with 3 members.", "A9")
    report(int(g) == sum(int(v) for _, v, _ in items) == ncr(7, 3), "A9b total", g)
except Exception as err:
    report(False, "A9", f"ERROR {err}")
try:
    rw = aligned_rows(BLK["10"], "A common denominator for the two fractions is required:", "A10")
    rw = [re.sub(r"^(\\text\{(LHS)\})?&=", "", t).rstrip(".,") for t in rw]
    ok = rw[-1] == r"\text{RHS}" and len(rw) == 6
    ok &= all(grid_ok(tex(t), lambda nn, rr, mm: ncr(nn + 1, rr), range(1, 11), lambda nn, rr, mm: 1 <= rr <= nn) for t in rw[:-1])
    report(ok, "A10a rows on grid 1 <= r <= n <= 10", " | ".join(rw))
except Exception as err:
    report(False, "A10", f"ERROR {err}")
A12 = BLK["12"]
try:
    (g,) = grab(A12, r"the number of permutations is \(@\).<br>", "A12")
    sd = g.split("=")
    ok = len(sd) == 3
    for aa in range(0, 5):
        for bb in range(0, 5):
            cntw = len(set(itertools.permutations("A" * aa + "B" * bb)))
            ok &= all(sp.expand_func(tex(t).subs({a: aa, b: bb})) == cntw for t in sd)
    report(ok, "A12a (a+b)!/(a!b!) = (a+b)Ca = (a+b)Cb vs permutations", g)
    (g,) = grab(A12, r"<b>b</b> \(@\)<br>", "A12")
    report(all(sp.expand_func(tex(g).subs(n, v)) == len(set(itertools.permutations("A" * v + "B" * v))) for v in range(1, 5)), "A12b words with n As and n Bs, n = 1..4", g)
    g1, g2, g3 = grab(A12, r"<b>c</b> (i) \(@\) (ii) \(@\) (iii) \(@\)</div>", "A12")
    ok = all(sp.expand_func(tex(g1).subs(n, v)) == sum(1 for c in itertools.combinations(range(v), 2)) for v in range(2, 9))
    ok &= all(sp.expand_func(tex(t).subs(n, v)) == ncr(v, 2) for t in g2.split("=") for v in range(2, 9)) and len(g2.split("=")) == 2
    words = [c for c in itertools.combinations(range(10), 5) if sum(1 for i in c if i < 5) == 2]
    sd = g3.split("=")
    ok &= len(sd) == 2 and all(same(tex(t), len(words)) for t in sd)
    report(ok, "A12c (i) nC2, (ii) nC(n-2) = nC2, (iii) ten-letter words counted", f"{g1} | {g2} | {g3}; enumerated {len(words)}")
except Exception as err:
    report(False, "A12", f"ERROR {err}")
report(set(BLK) == {"C1", "C2", "C3", "1", "4", "5", "6", "7", "8", "9", "10", "12"}, "textbook answer blocks (as in the textbook answers)", f"{sorted(BLK, key=lambda t: (len(t), t))}")

# ================================================================ chapter review: questions and answers
report(sorted(RQ, key=int) == [str(i) for i in range(1, 14)], "review questions 1-13", f"{sorted(RQ, key=int)}")
report(set(RBLK) == {str(i) for i in range(1, 14)}, "review answer blocks 1-13", f"{sorted(RBLK, key=int)}")
try:
    rows = re.findall(r"\\\(([\d\\ ]+)\\\)", RBLK["1"])
    report([[int(v) for v in re.findall(r"\d+", rw)] for rw in rows] == [[ncr(i, j) for j in range(i + 1)] for i in range(5)], "R1 first five rows", str(rows))
except Exception as err:
    report(False, "R1", f"ERROR {err}")
for part, base, e_ in (("a", "(1+x)^5", 1 + x), ("b", "(1+2x)^5", 1 + 2 * x), ("c", "(1-3x)^3", 1 - 3 * x), ("d", "(1-xy)^4", 1 - x * y)):
    N = int(base[-1])
    once(RQ["2"], r'<span class="pl">%s</span>\(%s\)</span>' % (part, base), f"R2{part} question")
    chain(RBLK["2"], r"<b>%s</b> \(@\)" % part, power(e_, N), f"R2{part}", 1)
try:
    once(RQ["3"], r"Expand \((1+7x)^5\) as far as the term in \(x^2\).", "R3a question")
    once(RQ["3"], r"the expansion of \((1-5x)(1+7x)^5\).", "R3b question")
    e = power(1 + 7 * x, 5)
    (g,) = grab(RBLK["3"], r"<b>a</b> \(@\)<br>", "R3")
    report(g.endswith("+\\cdots") and same(tex(g), sum(e.coeff(x, j) * x ** j for j in range(3))), "R3a", g)
    (g,) = grab(RBLK["3"], r"=\cdots+@x^2+\cdots\)", "R3")
    c2 = sp.expand((1 - 5 * x) * e).coeff(x, 2)
    report(same(tex(g), c2), "R3b bracket", g)
    (g,) = grab(RBLK["3"], r"The coefficient of \(x^2\) is \(@\).", "R3")
    report(same(tex(g), c2), "R3b coefficient", g)
except Exception as err:
    report(False, "R3", f"ERROR {err}")
chain(RBLK["4"], r"<b>a</b> \(@\)<br>", power(1 + x, 7), "R4a", 1)
try:
    (g,) = grab(RBLK["4"], r"<b>b</b> \(@\), and the remaining", "R4")
    sd = [t for t in g.split("=")]
    e7 = power(1 + x, 7)
    t0 = sd[0] == "(1+0.02)^7"
    terms1 = [t for t in sd[1].split("+") if "cdots" not in t]
    terms2 = [t for t in sd[2].split("+") if "cdots" not in t]
    ok = t0 and len(terms1) == len(terms2) == 3
    ok &= all(sp.nsimplify(tex(t)) == sp.nsimplify(e7.coeff(x, j) * sp.Rational(2, 100) ** j) for j, t in enumerate(terms1))
    ok &= all(sp.nsimplify(tex(t)) == sp.nsimplify(e7.coeff(x, j) * sp.Rational(2, 100) ** j) for j, t in enumerate(terms2))
    val = sp.Rational(102, 100) ** 7
    (dp,) = grab(RBLK["4"], r"The first decimal place will be @.</div>", "R4")
    rest = sum(e7.coeff(x, j) * sp.Rational(2, 100) ** j for j in range(3, 8))
    ok &= int(dp) == int(val * 10) % 10 and rest < sp.Rational(1, 1000)
    report(ok, "R4b terms of (1 + 0.02)^7 and first decimal place", f"{g}; 1.02^7 = {float(val):.6f}")
except Exception as err:
    report(False, "R4b", f"ERROR {err}")
for part, e_, N in (("a", 3 + 2 * x, 4), ("b", 5 - x, 3), ("c", 2 * x + 4 * y, 5), ("d", x - 1 / x, 4)):
    chain(RBLK["5"], r"<b>%s</b> \(@\)" % part, power(e_, N), f"R5{part}", 1)
for part, g_q in (("a", r"{}^5C_3"), ("b", r"{}^7C_4"), ("c", r"{}^8C_5"), ("d", r"{}^{120}C_{60}\div{}^{119}C_{60}")):
    once(RQ["6"], r'<span class="pl">%s</span>\(%s\)</span>' % (part, g_q), f"R6{part} question")
check_vals = []
try:
    got = grab(RBLK["6"], r"<b>a</b> \(@\) &nbsp; <b>b</b> \(@\) &nbsp; <b>c</b> \(@\) &nbsp; <b>d</b> \(@\)</div>", "R6")
    want = [ncr(5, 3), ncr(7, 4), ncr(8, 5), Fraction(math.comb(120, 60), math.comb(119, 60))]
    report(all(fr(g_) == w for g_, w in zip(got, want)), "R6 values", f"{got} vs {want}")
    got = grab(RBLK["7"], r"<b>a</b> \(@\) &nbsp; <b>b</b> \(@\) &nbsp; <b>c</b> \(@\) &nbsp; <b>d</b> \(@\) &nbsp; <b>e</b> \(@\) &nbsp; <b>f</b> \(@\)</div>", "R7")
    want = [ncr(10, 8), ncr(12, 7), ncr(9, 6), Fraction(ncr(10, 3), ncr(3, 2)), Fraction(ncr(10, 5), ncr(6, 2)), Fraction(ncr(16, 6), ncr(10, 5))]
    report(all(fr(g_) == w for g_, w in zip(got, want)), "R7 values", f"{got} vs {want}")
    for templ in (r"\({}^{10}C_8\)", r"\(\dbinom{12}7\)", r"\({}^9C_6\)", r"\(\dbinom{10}3\div\dbinom32\)", r"\(\dfrac{{}^{10}C_5}{{}^6C_2}\)", r"\(\dfrac{{}^{16}C_6}{{}^{10}C_5}\)"):
        once(RQ["7"], templ, f"R7 question {templ}")
except Exception as err:
    report(False, "R6/R7", f"ERROR {err}")
try:
    got = grab(RBLK["8"], r"<b>a</b> \(@\) (first entry in a row)<br><b>b</b> \(@\) (reversibility of rows)<br><b>c</b> \(@\) (sum of a row)<br><b>d</b> \(@\) (addition formula)</div>", "R8")
    ok = tex(got[0]) == 1 and all(ncr(v, 0) == 1 for v in range(15))
    ok &= tex(got[1]) == ncr(9, 4) - ncr(9, 5)
    ok &= all(tex(t) == row_sum(5) for t in got[2].split("="))
    ok &= tex(got[3]) == 0 and all(ncr(2 * v + 1, v) - ncr(2 * v, v) - ncr(2 * v, v - 1) == 0 for v in range(1, 9))
    report(ok, "R8 a-d", " | ".join(got))
    once(RQ["8"], r"\({}^{2n+1}C_n-{}^{2n}C_n-{}^{2n}C_{n-1}\)", "R8d question")
except Exception as err:
    report(False, "R8", f"ERROR {err}")
try:
    (g,) = grab(RBLK["9"], r"\(n=@\)</div>", "R9")
    once(RQ["9"], r"Solve \({}^nC_2=28\).", "R9 question")
    report([v for v in range(0, 60) if ncr(v, 2) == 28] == [int(g)], "R9 n by search", g)
except Exception as err:
    report(False, "R9", f"ERROR {err}")
try:
    e = power(1 + 5 * x, 14)
    g1, g2 = grab(RBLK["10"], r"(1-3x)\big(\cdots+@+@+\cdots\big)\)", "R10")
    report(same(tex(g1), term(e, 7)) and same(tex(g2), term(e, 8)), "R10 the two terms needed", f"{g1} | {g2}")
    chain(RBLK["10"], r"will be \(@\).</div>", sp.expand((1 - 3 * x) * e).coeff(x, 8), "R10 coefficient", 2)
    once(RQ["10"], r"\(x^8\) in the expansion of \((1-3x)(1+5x)^{14}\)", "R10 question")
except Exception as err:
    report(False, "R10", f"ERROR {err}")
once(RQ["11"], r"\(\dbinom n0+2\times\dbinom n1+4\times\dbinom n2+8\times\dbinom n3+\cdots=3^n\)", "R11b identity")
report(all(row_sum(v, lambda rr: 2 ** rr) == 3 ** v for v in range(0, 16)), "R11b brute force, n = 0..15", "")
once(RBLK["11"], r"\((1+x)^n=\dbinom n0+\dbinom n1x+\dbinom n2x^2+\dbinom n3x^3+\cdots\)", "R11a")
once(RBLK["11"], r"Substitute \(x=2\): \((1+2)^n=\dbinom n0+\dbinom n1\times2+\dbinom n2\times4+\dbinom n3\times8+\cdots\)", "R11b")
chain(RBLK["11"], r"\(n=4\), \(\text{LHS}=@\).</div>", sp.Integer(power(1 + x, 4).subs(x, 2)), "R11c", 4)
try:
    (g,) = grab(RBLK["11"], r"\(n=4\), \(\text{LHS}=@\).</div>", "R11c")
    terms = g.split("=")[0].split("+")
    report(len(terms) == 5 and all(same(tex(t), ncr(4, j) * 2 ** j) for j, t in enumerate(terms)), "R11c terms 4Cr x 2^r", g)
except Exception as err:
    report(False, "R11c terms", f"ERROR {err}")
once(RQ["12"], r"Prove that \({}^nC_0+{}^nC_1+{}^nC_2+{}^nC_3+\cdots=2^n\).", "R12a question")
report("\\(2^n\\)." in RBLK["12"].split("<b>c</b>")[0] and "which is \\(2^n\\)." in RBLK["12"], "R12 b, c state 2^n", "")
once(RQ["13"], r"\(1\times{}^nC_1+2\times{}^nC_2+\cdots+n\times{}^nC_n=n2^{n-1}\)", "R13a identity")
once(RQ["13"], r"\(1\times2\times{}^nC_2+2\times3\times{}^nC_3+3\times4\times{}^nC_4+\cdots+(n-1)\times n\times{}^nC_n\)<br>\(=(n-1)\times n\times2^{n-2}\)", "R13b identity")
report(all(row_sum(v, lambda rr: (rr - 1) * rr) == (v - 1) * v * 2 ** (v - 2) for v in range(2, 16)) and all(sp.diff(power(1 + x, v), x, 2).subs(x, 1) == (v - 1) * v * 2 ** (v - 2) for v in range(2, 10)),
       "R13b brute force and second derivative, n = 2..15", "")
d1, d2 = sp.diff(power(1 + x, 5), x).subs(x, 1), sp.diff(power(1 + x, 5), x, 2).subs(x, 1)
for lab, templ, val, f in (("first", r"First identity: \(@\).<br>", d1, lambda j: j * ncr(5, j)), ("second", r"Second identity: \(@\).</div>", d2, lambda j: (j - 1) * j * ncr(5, j))):
    chain(RBLK["13"], templ, val, f"R13c {lab}", 3)
    try:
        (g,) = grab(RBLK["13"], templ, "R13c")
        terms = g.split("=")[0].split("+")
        js = list(range(1, 6)) if lab == "first" else list(range(2, 6))
        report(len(terms) == len(js) and all(same(tex(t), f(j)) for j, t in zip(js, terms)), f"R13c {lab} terms from row 5", g)
    except Exception as err:
        report(False, f"R13c {lab} terms", f"ERROR {err}")

# ================================================================ past papers: structure
try:
    intro = re.search(r"Suggested time: (\d+) minutes</b></span><span><b>(\d+) marks", pp_les)
    marks = [int(v) for v in re.findall(r'<span class="mk">(\d+) marks?</span>', pp_les)]
    T, M = int(intro.group(1)), int(intro.group(2))
    report(sum(marks) == M and 15 <= M <= 22, "PP marks", f"PP marks {marks} sum {sum(marks)}, intro {M} (house rule: 15-22)")
    report(T == 5 * round(1.5 * M / 5), "PP time", f"{T} min for {M} marks")
    report(sorted(PPQ) == sorted(PPA) == list(range(1, len(PPQ) + 1)), "PP numbering", f"lesson {sorted(PPQ)}, answers {sorted(PPA)}")
    for kk in PPQ:
        sq = re.search(r"^(.*?)</span>", PPQ[kk]).group(1)
        sa = re.search(r"^(.*?)</span>", PPA[kk]).group(1) if kk in PPA else None
        report(sq == sa, f"PP{kk} source label", sq)
        report(PPQ[kk].count('<div class="hint">') == 1, f"PP{kk} hint", "exactly one hint")
        report(re.search(r",&nbsp;Q\d", sq) is not None and "Extension 1, Q" not in sq, f"PP{kk} label keeps the last words and Q together", "")
except Exception as err:
    report(False, "PP structure", f"ERROR {err}")

# PP1 NSB 2020 Q14(a)
once(PPQ[1], r"Show that \(\dbinom n0+\dbinom n1+\dbinom n2+\cdots\cdots+\dbinom nn=2^n\)", "PP1 question")
once(PPA[1], r"\[(1+x)^n=\dbinom n0+\dbinom n1x+\dbinom n2x^2+\cdots+\dbinom nnx^n.\]", "PP1 expansion")
once(PPA[1], r"\[2^n=\dbinom n0+\dbinom n1+\dbinom n2+\cdots+\dbinom nn.\]", "PP1 result")
report(all(row_sum(v) == 2 ** v == power(1 + x, v).subs(x, 1) for v in range(0, 16)), "PP1 identity, n = 0..15", "")
# PP2 SBHS 2020 Q14(c)(i)
once(PPQ[2], r"\[n2^{n-1}={}^nC_1+2\,{}^nC_2+3\,{}^nC_3+\cdots+n\,{}^nC_n.\]", "PP2 question")
once(PPA[2], r"\[n(1+x)^{n-1}={}^nC_1+2\,{}^nC_2\,x+3\,{}^nC_3\,x^2+\cdots+n\,{}^nC_n\,x^{n-1}.\]", "PP2 derivative")
once(PPA[2], r"\[n2^{n-1}={}^nC_1+2\,{}^nC_2+3\,{}^nC_3+\cdots+n\,{}^nC_n.\]", "PP2 result")
report(all(sp.diff(power(1 + x, v), x).subs(x, 1) == v * 2 ** (v - 1) == row_sum(v, lambda rr: rr) for v in range(1, 16)), "PP2 identity, n = 1..15", "")
# PP3 Killara 2021 Q13(e)
once(PPQ[3], r"\[1+{}^{100}C_2+{}^{100}C_4+\cdots+{}^{100}C_{100}\]", "PP3 question")
even100 = sum(math.comb(100, j) for j in range(0, 101, 2))
report(even100 == 2 ** 99 and all(sp.expand(power(1 + x, 2 * v) + power(1 - x, 2 * v)) == sp.expand(2 * sum(ncr(2 * v, j) * x ** j for j in range(0, 2 * v + 1, 2))) for v in range(1, 7)),
       "PP3: (1+x)^2n + (1-x)^2n = 2(even terms), n = 1..6; even sum of row 100 = 2^99", "")
once(PPA[3], r"\[(1+x)^{2n}+(1-x)^{2n}=2\big({}^{2n}C_0+{}^{2n}C_2\,x^2+{}^{2n}C_4\,x^4+\cdots+{}^{2n}C_{2n}\,x^{2n}\big).\]", "PP3 sum")
once(PPA[3], r"\[2^{100}+0^{100}=2\big(1+{}^{100}C_2+{}^{100}C_4+\cdots+{}^{100}C_{100}\big),\]", "PP3 at x = 1")
report(2 ** 100 + 0 ** 100 == 2 * even100, "PP3 2^100 + 0 = 2 x (even sum)", "")
try:
    (g,) = grab(PPA[3], r"\[1+{}^{100}C_2+{}^{100}C_4+\cdots+{}^{100}C_{100}=@.\]", "PP3")
    sd = g.split("=")
    report(len(sd) == 2 and all(tex(t) == even100 for t in sd), "PP3 value", g)
except Exception as err:
    report(False, "PP3 value", f"ERROR {err}")
# PP4 BBHS 2024 Q12(d)
once(PPQ[4], r"\[{}^{2026}C_{1924}-{}^{2024}C_{100}-{}^{2024}C_{101}={}^pC_q\]", "PP4 question")
once(PPQ[4], r"\({}^nC_r={}^{n-1}C_{r-1}+{}^{n-1}C_r\) for all integers such that \(1\le r\le n-1\)", "PP4 given identity")
lhs4 = math.comb(2026, 1924) - math.comb(2024, 100) - math.comb(2024, 101)
chain(PPA[4], r"and \(@\), so", sp.Integer(102), "PP4 2026 - 1924", 2)
for templ, l_, r_ in ((r"so \(@\). By the given", math.comb(2026, 1924), math.comb(2026, 102)),
                      (r"\[@.\]" + "\n<p>By the given identity again", math.comb(2024, 100) + math.comb(2024, 101), math.comb(2025, 101)),
                      (r"\[@.\]" + "\n<p>Hence", math.comb(2026, 102), math.comb(2025, 101) + math.comb(2025, 102))):
    try:
        (g,) = grab(PPA[4], templ, "PP4")
        lh, rh = g.split("=")
        report(tex(lh) == l_ and tex(rh) == r_ and l_ == r_, f"PP4 {g}", "")
    except Exception as err:
        report(False, f"PP4 {templ[:30]}", f"ERROR {err}")
try:
    rw = aligned_rows(PPA[4], "<p>Hence</p>", "PP4")
    sides = [t for rw_ in rw for t in rw_.replace("&", "").rstrip(".,").split("=") if t]
    report(len(sides) == 3 and all(tex(t) == lhs4 for t in sides), "PP4 chain", " | ".join(sides))
    g1, g2, g3, g4 = grab(PPA[4], r"one possible set is \(p=@\) and \(q=@\). (Another is \(p=@\) and \(q=@\).)", "PP4")
    sols = {(int(g1), int(g2)), (int(g3), int(g4))}
    report(len(sols) == 2 and all(math.comb(pp_, qq_) == lhs4 for pp_, qq_ in sols), "PP4 p, q", str(sols))
except Exception as err:
    report(False, "PP4 answer", f"ERROR {err}")
# PP5 PLC 2023 Q14(b)
once(PPQ[5], r"\[n\,{}^nC_2+{}^nC_3=\dfrac12\,{}^{2n}C_3,\quad\text{where }n\ge3.\]", "PP5 question")
try:
    trs = re.findall(r'<tr><td style="text-align:center">(\d)</td><td style="text-align:center">(\d)</td><td style="text-align:center">\\\((.*?)\\\)</td></tr>', PPA[5])
    ok = len(trs) == 4
    for v in range(3, 8):
        people = [("M", i) for i in range(v)] + [("F", i) for i in range(v)]
        by = {}
        for c in itertools.combinations(people, 3):
            mm_ = sum(1 for s_ in c if s_[0] == "M")
            by[mm_] = by.get(mm_, 0) + 1
        for males, females, expr in trs:
            ok &= int(males) + int(females) == 3 and sp.expand_func(tex(expr).subs(n, v)) == by[int(males)]
        ok &= sum(by.values()) == ncr(2 * v, 3)
        ok &= Fraction(v * ncr(v, 2) + ncr(v, 3)) == Fraction(ncr(2 * v, 3), 2)
    report(ok and sorted(int(t[0]) for t in trs) == [0, 1, 2, 3], "PP5 committees by number of males, enumerated n = 3..7", str([t[2] for t in trs]))
    g1, g2 = grab(PPA[5], r"\[@,\quad\text{that is,}\quad@.\]", "PP5")
    report(all(sp.expand_func(tex(t.split("=")[0]).subs(n, v)) == sp.expand_func(tex(t.split("=")[1]).subs(n, v)) for t in (g1, g2) for v in range(3, 12)), "PP5 final equations hold, n = 3..11", f"{g1} | {g2}")
except Exception as err:
    report(False, "PP5", f"ERROR {err}")
# PP6 KWS 2023 Q14(d)
e36 = sp.expand(power(1 + x, 3) * power(1 + x, 6))
try:
    (g,) = grab(PPQ[6], r"show that:" + "\n" + r"\[@\]", "PP6")
    lh, rh = g.split("=")
    report(tex(lh) == e36.coeff(x, 6) == tex(rh) == ncr(9, 6) and e36 == power(1 + x, 9), "PP6 identity: both sides = coefficient of x^6", g)
    (g,) = grab(PPA[6], r"coefficient of \(x^6\) on the left is</p>" + "\n" + r"\[@.\]", "PP6")
    report(tex(g) == e36.coeff(x, 6) and len(re.findall(r"\\dbinom3", g)) == 4, "PP6 coefficient on the left", g)
    (g,) = grab(PPA[6], r"the coefficient of \(x^6\) is \(@\).", "PP6")
    report(tex(g) == power(1 + x, 9).coeff(x, 6), "PP6 coefficient on the right", g)
except Exception as err:
    report(False, "PP6", f"ERROR {err}")
# PP7 NSB 2023 Q14(c)
def pp7_value(v):
    av = [power(1 + x, v).coeff(x, j) for j in range(v + 1)]
    prod = Fraction(1)
    for j in range(v):
        prod *= av[j] + av[j + 1]
    for j in range(v + 1):
        prod /= av[j]
    return prod


try:
    (g,) = grab(PPA[7], r"\[\dfrac{n+1}{n}\times\dfrac{n+1}{n-1}\times\cdots\times\dfrac{n+1}{1}=@.\]", "PP7")
    report(all(Fraction(str(sp.nsimplify(tex(g).subs(n, v)))) == pp7_value(v) for v in range(1, 12)), "PP7 final expression vs the product computed from the expansions, n = 1..11", g)
    (g,) = grab(PPA[7], r"\[\dfrac{b_k}{a_k}=@.\]", "PP7")
    sd = g.split("=")
    report(len(sd) == 2 and all(grid_ok(tex(t), lambda nn, rr, mm: Fraction(ncr(nn + 1, rr), ncr(nn, rr)), range(1, 12), lambda nn, rr, mm: 1 <= rr <= nn) for t in sd), "PP7 b_k / a_k on grid", g)
    once(PPA[7], r"\(a_{k-1}+a_k=b_k\) for \(k=1,2,\dots,n\). Also \(a_0=1\).", "PP7 a_(k-1) + a_k = b_k")
    report(all(power(1 + x, v).coeff(x, j - 1) + power(1 + x, v).coeff(x, j) == power(1 + x, v + 1).coeff(x, j) for v in range(1, 10) for j in range(1, v + 1)), "PP7 a_(k-1) + a_k = b_k, n = 1..9", "")
    once(PPA[7], r"\[\big(a_0+a_1x+\cdots+a_nx^n\big)(1+x)=a_0+(a_0+a_1)x+(a_1+a_2)x^2+\cdots+a_nx^{n+1}.\]", "PP7 product expanded")
    once(PPQ[7], r"\[\dfrac{1}{a_0a_1a_2\cdots a_n}\times(a_0+a_1)(a_1+a_2)\cdots(a_{n-1}+a_n)\quad\text{for }n=1,2,3,\dots\]", "PP7 question")
except Exception as err:
    report(False, "PP7", f"ERROR {err}")

print(f"\n{len(FAILS)} problem(s)" if FAILS else "\nAll OK")
sys.exit(1 if FAILS else 0)
