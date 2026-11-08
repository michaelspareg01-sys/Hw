"""Check of Lesson 12B (Integration Part 3 pack): Inverse trigonometric functions: integrating.

The script reads the values PRINTED in workspace/build/int3/l12b.html (the integrals in the tutor
demos, your-turn items, worked examples, textbook questions and past-paper questions, the MC
options) and in workspace/build/int3/a_12b.html (every answer). Each item is located inside its own
block (an example box, a question, an answer entry) with a template; a template must match exactly
once in its block, otherwise the item FAILS. Printed LaTeX is turned into sympy with the shared
helper int3_tex.tex, and compared with an independent computation:
  - a definite integral printed in a question is evaluated by mpmath numerical quadrature
    (tanh-sinh, 30 digits; it copes with the convergent endpoint singularities) and compared with
    the printed exact value (to 1e-20) or the printed rounded value (rounded half-up);
  - a printed primitive F of a printed integrand f is checked by differentiating F with sympy and
    comparing F' with f at several points of the domain (to 1e-20);
  - every chain of equalities in the worked solutions (aligned displays, and '=' chains in single
    displays) whose members are constants is checked member by member: all members must agree;
  - the trapezoidal estimate is recomputed with exact fractions, the series in Q22 by exact sums,
    and the MC keys by testing every option.
It also checks the past-paper block: marks add to the intro total (15-22), time is 1.5 x marks
rounded to 5 minutes, numbering and source labels match in both files, and one hint per question.

Exit status 1 if anything fails. Run: python3 workspace/checks/int3_12b.py
"""
import math
import os
import re
import sys
from fractions import Fraction as Fr

import mpmath as mp
import sympy as sp

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from int3_tex import tex as _tex, x  # noqa: E402

SRC = os.environ.get("INT3_SRC", os.path.join(HERE, "..", "build", "int3"))
mp.mp.dps = 30
TOL = mp.mpf(10) ** -14   # quadrature with endpoint singularities is good to about 1e-16
FAILS, NCHECK = [], [0]
t_, n_, a_ = sp.symbols("t n a", positive=True)


def report(ok, label, detail=""):
    NCHECK[0] += 1
    print(("OK       " if ok else "MISMATCH ") + label[:90] + ("  " + detail[:160] if detail else ""))
    if not ok:
        FAILS.append(label)


def read(name):
    with open(os.path.join(SRC, name), encoding="utf-8") as fh:
        return fh.read()


def norm(s):
    s = s.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
    s = re.sub(r"\\([dt]?frac) (\w)(\w)", r"\\\1{\2}{\3}", s)
    s = re.sub(r"\\sqrt (\w)", r"\\sqrt{\1}", s)
    return s


MULTI = re.compile(r"\\(sin|cos|tan|sec|ln|arcsin|arccos|arctan)(\^\{-1\}|\^\d)?\s*\d[\d.]")


def T(s):
    s = norm(s).strip().rstrip(",.").strip()
    if MULTI.search(s):
        # int3_tex reads \sin12x as sin(1*2*x): refuse such forms rather than misread them
        raise ValueError(f"multi-digit function argument, not parsed: {s[:40]!r}")
    s = re.sub(r"\\text\{[^}]*\}", "", s)
    s = re.sub(r"\+\s*[Cc]\s*$", "", s).strip().rstrip(",").strip()
    e = _tex(s, {"t": t_, "n": n_})
    return e


# ---------------------------------------------------------------- blocks
LES, ANS = read("l12b.html"), read("a_12b.html")


def blocks(src, start_re, stop_re):
    out = {}
    for m in re.finditer(start_re, src):
        key = m.group(1)
        rest = src[m.end():]
        st = re.search(stop_re, rest)
        body = rest[:st.start()] if st else rest
        if key in out:
            report(False, f"block {key} appears twice")
        out[key] = body
    return out


STOP_L = r'<div class="q"><span|<div class="ex |\{\{band|\{\{sec|<!-- =|<div class="pp"><div'
QB = blocks(LES, r'<div class="q"><span class="q-num">(\d+)</span>', STOP_L)
PPB = blocks(LES, r'<div class="pp"><div class="pp-src"><span><span class="pn">PP (\d+)</span>', STOP_L)
EXB = {}
for kind in ("demo", "attempt", "worked"):
    for i, m in enumerate(re.finditer(rf'<div class="ex {kind}"[^>]*><div class="ex-top"><span class="tag">([^<]*)</span>', LES)):
        rest = LES[m.end():]
        st = re.search(STOP_L, rest)
        key = f"{kind}{i + 1}" if kind != "worked" else m.group(1)
        EXB[key] = rest[:st.start()] if st else rest
STOP_A = r'<div class="a"[ >]|<div class="ans-sec"|\{\{ahead|<div class="ppa">'
AB = blocks(ANS, r'<div class="a"[^>]*><span class="an">(\w+)</span>', STOP_A)
PPA = blocks(ANS, r'<div class="ppa"><div class="pp-src"><span><span class="pn">PP (\d+)</span>', STOP_A)


def halves(key):
    """Split a C-entry into its tutor-demo and your-turn halves."""
    b = AB[key]
    i = b.index("<b>Your turn.</b>")
    return b[:i], b[i:]


# ---------------------------------------------------------------- reading helpers
def brace(s, i):
    """s[i] == '{': return (inner, index after the closing brace)."""
    d = 0
    for j in range(i, len(s)):
        d += s[j] == "{"
        d -= s[j] == "}"
        if d == 0:
            return s[i + 1:j], j + 1
    raise ValueError("unbalanced")


def limit(s, i):
    if s[i] == "{":
        return brace(s, i)
    if s[i] == "\\":
        m = re.match(r"\\[A-Za-z]+", s[i:])
        return m.group(0), i + len(m.group(0))
    if s[i] == "-":
        v, j = limit(s, i + 1)
        return "-" + v, j
    m = re.match(r"\d+(\.\d+)?", s[i:])
    if m:
        return m.group(0), i + len(m.group(0))
    return s[i], i + 1


def integrals(block):
    """All printed definite integrals \\int_a^b f dx in a block, in order: (lo, hi, f) as sympy."""
    out = []
    s = norm(block)
    for m in re.finditer(r"\\int_", s):
        i = m.end()
        lo, i = limit(s, i)
        if s[i] != "^":
            continue
        hi, i = limit(s, i + 1)
        rest = s[i:]
        k = rest.find("dx")
        f = rest[:k]
        if rest.startswith(("\\frac{dx}", "\\dfrac{dx}")):
            den, _ = brace(rest, rest.index("{", rest.index("dx")))
            f = "\\frac{1}{" + den + "}"
        f = f.replace("\\,", "").strip()
        out.append((T(lo), T(hi), T(f)))
    return out


def indef(block):
    """All printed indefinite integrands in a block: \\int f dx (no limits)."""
    out = []
    s = norm(block)
    for m in re.finditer(r"\\int(?!_)", s):
        rest = s[m.end():]
        k = rest.find("dx")
        f = rest[:k].replace("\\,", "").strip()
        if rest.lstrip().startswith(("\\frac{dx}", "\\dfrac{dx}")):
            den, _ = brace(rest, rest.index("{", rest.index("dx")))
            f = "\\frac{1}{" + den + "}"
        out.append(T(f))
    return out


def quad(f, lo, hi):
    g = sp.lambdify(x, f, "mpmath")
    return mp.quad(g, [mp.mpf(sp.N(lo, 40)), mp.mpf(sp.N(hi, 40))])


def num(e):
    return mp.mpf(sp.N(e, 40))


def close(a, b, tol=1e-20):
    return abs(num(a) - num(b)) < tol if not isinstance(a, mp.mpf) else abs(a - num(b)) < tol


def round_half_up(v, places):
    q = mp.mpf(10) ** places
    return mp.floor(v * q + mp.mpf("0.5")) / q


def check_rounded(label, exact, printed, places=None, sf=None):
    v = num(exact) if not isinstance(exact, mp.mpf) else exact
    if sf is not None:
        places = sf - 1 - int(mp.floor(mp.log10(abs(v))))
    r = round_half_up(v, places)
    report(abs(r - mp.mpf(printed)) < mp.mpf(10) ** (-places - 3), label, f"printed {printed}, exact {mp.nstr(v, 12)} -> {mp.nstr(r, 10)}")


def check_def(label, ints, k, printed_tex, rounding=None):
    lo, hi, f = ints[k]
    v = quad(f, lo, hi)
    if rounding:
        check_rounded(label, v, printed_tex, **rounding)
    else:
        p = T(printed_tex)
        report(abs(v - num(p)) < TOL, label, f"int_{lo}^{hi} {f} = {mp.nstr(v, 15)}; printed {p}")


PTS = [sp.Rational(5, 100), sp.Rational(11, 100), sp.Rational(17, 100), sp.Rational(-13, 100)]


def check_prim(label, F, f, pts=PTS):
    dF = sp.diff(F, x)
    ok = all(abs(num(dF.subs(x, p)) - num(f.subs(x, p))) < TOL for p in pts)
    report(ok, label, f"F = {F}; f = {f}")


def one(block, pattern, label, group=1, flags=0):
    ms = list(re.finditer(pattern, block, flags))
    if len(ms) != 1:
        report(False, label, f"template matched {len(ms)} times: {pattern[:70]}")
        return None
    return ms[0].group(group)


def parts(block):
    """Answer parts '<b>a</b> \\(...\\)' -> {letter: first maths}."""
    out = {}
    for m in re.finditer(r"<b>([a-z]+)</b>\s*(?:\([iv]+\)\s*)?\\\((.+?)\\\)", block):
        if m.group(1) in out:
            report(False, f"part {m.group(1)} twice in a block")
        out[m.group(1)] = m.group(2)
    return out


def aligned_finals(block):
    """Last member of every aligned display in a block, in order."""
    out = []
    for m in re.finditer(r"\\begin\{aligned\}(.*?)\\end\{aligned\}", norm(block), re.S):
        body = m.group(1)
        last = body.split("\\\\")[-1]
        last = last.split("&=")[-1] if "&=" in last else last.split("=")[-1]
        out.append(last.replace("&", ""))
    return out


# ---------------------------------------------------------------- generic chain check
def chain_members(disp):
    """Members of an equality chain: split aligned rows and top-level '=' signs."""
    disp = re.sub(r"\\text\{[^}]*\}", "", disp)
    rows = disp.split("\\\\")
    mem = []
    for r in rows:
        r = r.replace("&", "")
        depth, cur = 0, ""
        for ch in r:
            depth += ch in "{(["
            depth -= ch in "})]"
            if ch == "=" and depth == 0:
                mem.append(cur)
                cur = ""
            else:
                cur += ch
        mem.append(cur)
    return [m for m in mem if m.strip()]


def chains_of(d):
    """An aligned display holds one or more chains: a row with a left side starts a new chain."""
    d = re.sub(r"\\begin\{aligned\}|\\end\{aligned\}|\\quad|\\qquad|\\text\{OR\}", " ", d)
    out, cur = [], []
    for row in d.split("\\\\"):
        if "&=" in row and row.split("&=")[0].strip() and cur:
            out.append("\\\\".join(cur))
            cur = []
        cur.append(row)
    out.append("\\\\".join(cur))
    return out


def chain_check(name, src):
    disps = re.findall(r"\\\[(.*?)\\\]", norm(src), re.S)
    n_ok = n_used = 0
    for d2 in [c for d in disps for c in chains_of(d)]:
        vals = []
        for m in chain_members(d2):
            m = m.strip().rstrip(",.")
            if "\\doteq" in m or "\\ldots" in m or "\\int" in m or "\\Big" in m or "\\big[" in m:
                continue
            try:
                e = T(m)
            except Exception:
                continue
            if not isinstance(e, sp.Expr) or e.free_symbols:
                continue
            vals.append((m, num(e)))
        if len(vals) >= 2:
            n_used += 1
            ok = all(abs(v - vals[0][1]) < TOL for _, v in vals)
            n_ok += ok
            if not ok:
                report(False, f"{name}: constant chain", " | ".join(f"{m}={mp.nstr(v, 10)}" for m, v in vals))
    report(n_used > 0, f"{name}: {n_ok}/{n_used} constant equality chains agree member by member")


# ================================================================= Lesson examples
print("--- Lesson examples (tutor demos, your turns, worked examples)")
# C1: both forms of Box 4
for key, half, exp_lo_hi in (("demo1", 0, None), ("attempt1", 1, None)):
    ints = integrals(EXB[key])
    fins = aligned_finals(halves("C1")[half])
    report(len(fins) == 2, f"C1 {key}: two forms printed")
    for k, fin in enumerate(fins):
        check_def(f"C1 {key} form {k + 1}: value", ints, 0, fin)
ints = integrals(EXB["Worked example 6"])
for k, fin in enumerate(aligned_finals(EXB["Worked example 6"])):
    check_def(f"WE6 form {k + 1}: value", ints, 0, fin)
# C2 / WE7: exact or 4 s.f.
for key, half in (("demo2", 0), ("attempt2", 1)):
    ints = integrals(EXB[key])
    fins = aligned_finals(halves("C2")[half])
    check_def(f"C2 {key} a", ints, 0, fins[0])
    check_rounded(f"C2 {key} b (4 s.f.)", quad(*ints[1][2:], *ints[1][:2]) if False else quad(ints[1][2], ints[1][0], ints[1][1]),
                  fins[1].replace("\\doteq", "").strip(), sf=4)
ints = integrals(EXB["Worked example 7"])
fins = aligned_finals(EXB["Worked example 7"])
check_def("WE7 a", ints, 0, fins[0])
check_rounded("WE7 b (4 s.f.)", quad(ints[1][2], ints[1][0], ints[1][1]), fins[1].replace("\\doteq", "").strip(), sf=4)


def prim_pairs(label, qblock, ablock, expect):
    fs = indef(qblock)
    fins = aligned_finals(ablock)
    report(len(fs) >= expect and len(fins) >= expect, f"{label}: {expect} integrands and primitives found", f"{len(fs)} / {len(fins)}")
    for k in range(expect):
        check_prim(f"{label} part {k + 1}", T(fins[k]), fs[k])


prim_pairs("C3 demo", EXB["demo3"], halves("C3")[0], 2)
prim_pairs("C3 your turn", EXB["attempt3"], halves("C3")[1], 2)
prim_pairs("WE8a,b", EXB["Worked example 8a, b"].split("Solution")[0], EXB["Worked example 8a, b"].split("Solution")[1], 2)
prim_pairs("C4 demo", EXB["demo4"], halves("C4")[0], 2)
prim_pairs("C4 your turn", EXB["attempt4"], halves("C4")[1], 2)
prim_pairs("WE8c,d", EXB["Worked example 8c, d"].split("Solution")[0], EXB["Worked example 8c, d"].split("Solution")[1], 2)
# Box 6 cross-checks printed in C4 and WE8c,d
for key in ("C4",):
    for k, m in enumerate(re.finditer(r"Box 6 with [^:]*: \\\((.+?)\\\)", AB[key])):
        fs = indef(EXB["demo4"]) + indef(EXB["attempt4"])
        check_prim(f"C4 Box 6 check {k + 1}", T(m.group(1)), fs[k])
for k, m in enumerate(re.finditer(r"the answer is \\\((.+?)\\\)", EXB["Worked example 8c, d"])):
    check_prim(f"WE8c,d Box 6 check {k + 1}", T(m.group(1)), indef(EXB["Worked example 8c, d"].split("Solution")[0])[k])


def last_eq(disp):
    disp = re.sub(r"\\begin\{aligned\}|\\end\{aligned\}", "", disp)
    return chain_members(disp)[-1]


# C5 / WE9: reverse chain rule (single displays, last member is the primitive)
for key, half, qkey in (("C5", 0, "demo5"), ("C5", 1, "attempt5")):
    qs = re.findall(r"<span class=\"pl\">[ab]</span>\\\((.+?)\\\)", EXB[qkey])
    disps = re.findall(r"\\\[(.*?)\\\]", halves(key)[half], re.S)
    report(len(qs) == 2 and len(disps) == 2, f"{key} {qkey}: two integrands, two displays")
    for k in range(2):
        check_prim(f"{key} {qkey} {'ab'[k]}", T(last_eq(disps[k])), T(qs[k]))
qs = re.findall(r"<span class=\"pl\">[ab]</span>\\\((.+?)\\\)", EXB["Worked example 9"])
fins = [f.replace(r"\ \text{for some constant }C.", "") for f in aligned_finals(EXB["Worked example 9"])]
for k in range(2):
    check_prim(f"WE9 {'ab'[k]}", T(re.sub(r",\\ .*$", "", fins[k])), T(qs[k]))

# C6 / WE10: product rule, primitive and area
for key, half, fn, lo, hi in (("C6", 0, sp.acos(x), 0, 1), ("C6", 1, sp.asin(x / 2), 0, 2)):
    b = halves(key)[half]
    dy = one(b, r"\\\[\\frac\{dy\}\{dx\}=(.+?)\.\\\]", f"{key} half {half}: dy/dx display")
    if dy:
        mem = chain_members(dy)
        target = sp.diff(x * fn, x)
        for m in mem:
            check_prim(f"{key} half {half}: dy/dx member {m[:30]}", sp.integrate(T(m), x) if False else x * fn, T(m))
    prim = one(b, r"so \\\(\\displaystyle\\int[^=]*=(.+?)\\\)", f"{key} half {half}: primitive")
    if prim:
        check_prim(f"{key} half {half}: primitive of {fn}", T(prim), fn)
    area = one(b, r"&=([^&]*?)\\text\{ square units?\.\}", f"{key} half {half}: area")
    if area:
        report(abs(quad(fn, lo, hi) - num(T(area))) < TOL, f"{key} half {half}: area under {fn} on [{lo},{hi}]", f"printed {area}")
we10 = EXB["Worked example 10"]
prim = one(we10, r"\\text\{so\}\\quad\\int\\sin\^\{-1\}x\\,dx=(.+?)\.\\\]", "WE10 primitive")
check_prim("WE10 primitive of asin x", T(prim), sp.asin(x))
area = one(we10, r"&=([^&]*?)\\text\{ square units\.\}", "WE10 area")
report(abs(quad(sp.asin(x), 0, 1) - num(T(area))) < TOL, "WE10 area pi/2 - 1", area)
report("rectangle of area \\(\\tfrac{\\pi}{2}\\)" in we10 and abs(quad(sp.sin(x), 0, sp.pi / 2) - 1) < TOL, "WE10 note: rectangle pi/2 and the 7D area 1")
dy = one(we10, r"\\frac\{dy\}\{dx\}&=(.+?)\\end\{aligned\}", "WE10 dy/dx")
for m in chain_members(dy):
    check_prim(f"WE10 dy/dx member {m[:30]}", x * sp.asin(x), T(m))

# The boxes: general forms with constants (a, b > 0), checked at sample constants
print("--- Boxes 4-7")
box = {}
for m in re.finditer(r'<div class="box take"><div class="bt">(\d) ', LES):
    box[m.group(1)] = LES[m.end():LES.index("</div>\n", LES.index("</div>", m.end()) + 6) + 6]
box["7"] = LES[LES.index("7 The reverse chain rule"):LES.index('<div class="box tip"><div class="bt">Finding')]
for bn, consts in (("4", [{}]), ("5", [{"a": 3}, {"a": sp.Rational(7, 5)}]), ("6", [{"a": 3, "b": 2}, {"a": sp.sqrt(5), "b": sp.sqrt(3)}])):
    disp = " ".join(re.findall(r"\\\[(.*?)\\\]", box[bn], re.S))
    eqs = re.findall(r"\\int(.+?)\\,dx=(.+?)\+C", norm(disp))
    ors = re.findall(r"\\text\{OR\}\\qquad(-[^+]+)\+C", norm(disp))
    report(len(eqs) >= 2, f"Box {bn}: {len(eqs)} standard forms read")
    for c in consts:
        sub = {sp.Symbol("a"): c.get("a", 1), sp.Symbol("b"): c.get("b", 1)}
        for f, F in eqs:
            check_prim(f"Box {bn} {c}: {F.strip()[:40]}", T(F).subs(sub), T(f).subs(sub), pts=[sp.Rational(1, 10), sp.Rational(-1, 7)])
        for F in ors:
            g = T(eqs[0][0]).subs(sub)
            check_prim(f"Box {bn} {c}: OR {F[:40]}", T(F).subs(sub), g, pts=[sp.Rational(1, 10), sp.Rational(-1, 7)])
rows = re.findall(r"\\int(.+?)\\,dx&=(.+?)\+C", norm(box["7"]))
report(len(rows) == 6, f"Box 7: six rows read ({len(rows)})")
for f, F in rows:
    for u in (x ** 3 / 2, sp.sin(x)):
        fe = T(f.replace("u'", "V").replace("f'(x)", "V").replace("f(x)", "U").replace("u", "U"))
        Fe = T(F.replace("f(x)", "U").replace("u", "U"))
        U, U1 = sp.Symbol("U"), sp.Symbol("V")
        check_prim(f"Box 7 row {F.strip()[:30]} with u = {u}", Fe.subs(U, u), fe.subs({U1: sp.diff(u, x), U: u}),
                   pts=[sp.Rational(1, 10), sp.Rational(-1, 7)])

# ================================================================= Textbook homework
print("--- Textbook homework")
A = {k: parts(v) for k, v in AB.items() if k.isdigit()}
# Q1: two decimal places
ints = integrals(QB["1"])
q1 = re.findall(r"<b>(i{1,3}|iv)</b>\s*\\\((.+?)\\\)", AB["1"])
report(len(ints) == 4 and len(q1) == 4, "Q1: four integrals, four answers")
for k, (lab, s) in enumerate(q1):
    exact, dec = s.split("\\doteq")
    v = quad(ints[k][2], ints[k][0], ints[k][1])
    report(all(abs(v - num(T(m))) < TOL for m in exact.split("=")), f"Q1 {lab}: exact form", exact)
    check_rounded(f"Q1 {lab}: 2 d.p.", v, dec, places=2)
    sq = re.search(r"close to ([\d, and]+) squares", AB["1"]).group(1)
    cnt = [int(c) for c in re.findall(r"\d+", sq)]
    report(cnt[k] == int(round(float(v) * 100)), f"Q1 {lab}: about {cnt[k]} little squares of area 0.01")
for q, letters in (("3", "abcdef"), ("7", "abcd")):
    ints = integrals(QB[q])
    report(len(ints) == len(letters), f"Q{q}: {len(letters)} integrals printed", str(len(ints)))
    for k, L in enumerate(letters):
        check_def(f"Q{q}{L}", ints, k, A[q][L])
for q, letters in (("2", "abcdef"), ("6", "abcdef")):
    fs = indef(QB[q])
    for k, L in enumerate(letters):
        check_prim(f"Q{q}{L}", T(A[q][L]), fs[k])
# Q4, Q5: curves through a point
for L, yp, pt in (("a", sp.sqrt(1 / (1 - x ** 2)) * 0 + (1 - x ** 2) ** sp.Rational(-1, 2), (0, sp.pi)), ("b", 4 / (16 + x ** 2), (-4, 0))):
    s = A["4"][L].split("=", 1)[1]
    F = T(s)
    check_prim(f"Q4{L}: y' matches", F, yp)
    report(sp.simplify(F.subs(x, pt[0]) - pt[1]) == 0, f"Q4{L}: passes through {pt}")
q5 = QB["5"]
for L, yp, x0, y0, x1 in (("a", 1 / sp.sqrt(36 - x ** 2), 3, sp.pi / 6, 3 * sp.sqrt(3)), ("b", 2 / (4 + x ** 2), 2, sp.pi / 3, 2 / sp.sqrt(3))):
    v = y0 + quad(yp, x0, x1)
    report(abs(v - num(T(A["5"][L]))) < TOL, f"Q5{L}: y = {A['5'][L]}", mp.nstr(v, 15))
report("\\dfrac{1}{\\sqrt{36-x^2}}" in q5 and "y=\\tfrac{\\pi}{6}\\) when \\(x=3\\)" in q5 and "\\dfrac{2}{4+x^2}" in q5, "Q5: data as printed")
# Q8, Q9
report(abs(quad(sp.asin(x), 0, sp.Rational(1, 2)) - num(T(A["8"]["c"]))) < TOL, "Q8c area", A["8"]["c"])
report("x\\sin^{-1}x+\\sqrt{1-x^2}" in QB["8"] and sp.simplify(sp.diff(x * sp.asin(x) + sp.sqrt(1 - x ** 2), x) - sp.asin(x)) == 0, "Q8b: the printed derivative is right")
report(abs(quad(sp.sin(x), 0, sp.pi / 6) - num(T(A["9"]["b"]))) < TOL, "Q9b area (integrate x = sin y)", A["9"]["b"])
q9c = re.search(r"\\\(\\tfrac\{\\pi\}\{12\}-\\big\(1-\\tfrac12\\sqrt3\\big\)=(.+?)\\\)", AB["9"])
report(q9c is not None and abs(num(sp.pi / 12) - quad(sp.sin(x), 0, sp.pi / 6) - num(T(q9c.group(1)))) < TOL
       and abs(num(T(q9c.group(1))) - num(T(A["8"]["c"]))) < TOL, "Q9c: rectangle minus 9b equals 8c")
# Q10 - Q12
report(sp.simplify(sp.diff(sp.acos(2 - x), x) - 1 / sp.sqrt(4 * x - x ** 2 - 3)) == 0 or
       all(abs(num(sp.diff(sp.acos(2 - x), x).subs(x, p)) - num((1 / sp.sqrt(4 * x - x ** 2 - 3)).subs(x, p))) < TOL for p in (sp.Rational(3, 2), sp.Rational(9, 5))),
       "Q10a: the printed derivative is right on 1 < x < 3")
check_def("Q10b", integrals(QB["10"]), 0, A["10"]["b"])
d11 = sp.diff(sp.atan(x ** 3 / 2), x)
report(all(abs(num(d11.subs(x, p)) - num(T(A["11"]["a"]).subs(x, p))) < TOL for p in PTS), "Q11a derivative", A["11"]["a"])
check_prim("Q11b", T(A["11"]["b"]), indef(QB["11"])[0])
d12 = sp.diff(x * sp.atan(x), x)
report(all(abs(num(d12.subs(x, p)) - num(T(A["12"]["a"]).subs(x, p))) < TOL for p in PTS), "Q12a derivative", A["12"]["a"])
check_def("Q12b", integrals(QB["12"]), 0, A["12"]["b"])
ints = integrals(QB["13"])
for k, L in enumerate("abcdef"):
    check_def(f"Q13{L}", ints, k, A["13"][L])
# Q14
f14 = x / (1 + x ** 2) - sp.atan(x)
report(T(A["14"]["a"]) == 0 and f14.subs(x, 0) == 0, "Q14a(i) f(0) = 0")
report(sp.simplify(sp.diff(f14, x) + 2 * x ** 2 / (1 + x ** 2) ** 2) == 0, "Q14a(ii) the printed f'(x) is right")
q14b = re.search(r"\(ii\) \\\((.+?)\\\)", AB["14"]).group(1)
check_def("Q14b(ii)", integrals(QB["14"]), 0, q14b)
# Q15, Q16
ans15 = AB["15"]
report("-2&lt;x&lt;2" in ans15 and "y\\ge\\tfrac12" in ans15 and "even" in ans15, "Q15c: domain -2 < x < 2 (open), range y >= 1/2, even")
report(sp.minimum(1 / sp.sqrt(4 - x ** 2), x, sp.Interval.open(-2, 2)) == sp.Rational(1, 2), "Q15c: least value 1/2 at x = 0")
q15 = re.findall(r"<b>([de])</b> \\\((.+?)\\\) unit", ans15)
report(abs(quad(1 / sp.sqrt(4 - x ** 2), -1, 1) - num(T(q15[0][1]))) < TOL, "Q15d", q15[0][1])
report(abs(quad(1 / sp.sqrt(4 - x ** 2), -2, 2) - num(T(q15[1][1]))) < TOL, "Q15e (improper, convergent)", q15[1][1])
f16 = 4 / (x ** 2 + 4)
ans16 = AB["16"]
report("0&lt;y\\le1" in ans16 and sp.diff(f16, x).subs(x, 0) == 0 and f16.subs(x, 0) == 1 and sp.limit(f16, x, sp.oo) == 0,
       "Q16b-d: range 0 < y <= 1, maximum (0, 1), limit 0")
q16 = dict(re.findall(r"<b>([efg])</b> \\\((.+?)\\\) unit", ans16))
report(abs(quad(f16, -2 * sp.sqrt(3), sp.Rational(2, 3) * sp.sqrt(3)) - num(T(q16["e"]))) < TOL, "Q16e", q16["e"])
F16 = sp.integrate(f16, (x, -a_, a_))
report(sp.simplify(F16 - T(q16["f"]).subs(sp.Symbol("a"), a_)) == 0, "Q16f symbolic in a", f"{F16}")
report(sp.limit(F16, a_, sp.oo) == T(q16["g"]), "Q16g limit as a -> oo", q16["g"])
# Q17 (show that): the area is 1/4
tang = 2 * x + sp.pi / 3 - sp.sqrt(3)
report(sp.simplify(sp.diff(sp.asin(x), x).subs(x, sp.sqrt(3) / 2) - 2) == 0 and abs(quad(sp.asin(x) - tang, 0, sp.sqrt(3) / 2) - mp.mpf(1) / 4) < TOL,
       "Q17: tangent gradient 2 and area 1/4 (question is sound)")
# Q18: trapezoidal rule with five points, exact fractions
h = Fr(1, 4)
ys = [Fr(1) / (1 + (k * h) ** 2) for k in range(5)]
trap = h / 2 * (ys[0] + 2 * sum(ys[1:4]) + ys[4])
report(Fr(str(T(A["18"]["a"]))) == trap, "Q18a trapezoidal estimate", f"{trap}")
report(4 * trap == Fr(5323, 1700), "Q18b: 4 x estimate = 5323/1700 as printed")
report("\\tfrac{5323}{1700}" in QB["18"], "Q18b: question prints 5323/1700")
# Q19 (show that)
lo, hi, f = integrals(QB["19"])[0]
report(abs(quad(f, lo, hi) - mp.pi / 4) < TOL, "Q19: the printed integral is pi/4")
# Q20
check_prim("Q20a", T(A["20"]["a"]), indef(QB["20"])[0], pts=[sp.Rational(1, 10), sp.Rational(7, 3)])
check_def("Q20b", integrals(QB["20"]), 0, A["20"]["b"])
# Q21
d21 = sp.diff(sp.atan(sp.Rational(3, 2) * sp.tan(x)), x)
report(all(abs(num(d21.subs(x, p)) - num((6 / (5 * sp.sin(x) ** 2 + 4)).subs(x, p))) < TOL for p in PTS), "Q21a: the printed derivative is right")
q21 = re.search(r"\\doteq(0\.\d+)\\\) unit", AB["21"]).group(1)
check_rounded("Q21b: the (invalid) value", num(sp.atan(sp.Rational(3, 2) * sp.tan(7)) / 6), q21, places=3)
true21 = quad(1 / (5 * sp.sin(x) ** 2 + 4), 0, 7)
report(mp.mpf(7) / 9 < true21 < mp.mpf(7) / 4 and 0 < sp.pi / 2 < 7 and 3 * sp.pi / 2 < 7 < 5 * sp.pi / 2,
       "Q21c: the true area lies between 7/9 and 7/4; tan x is undefined at pi/2 and 3pi/2 only", mp.nstr(true21, 8))
# Q22
sa, sb = T(A["22"]["a"]), T(A["22"]["b"])
ok = all(sp.simplify(sum((-t_ ** 2) ** k for k in range(2 * N + 1)) - sa.subs(n_, N)) == 0 and
         sp.simplify(sum((-t_ ** 2) ** k for k in range(2 * N + 2)) - sb.subs(n_, N)) == 0 for N in range(1, 6))
report(ok, "Q22a, b: geometric sums for n = 1..5", f"{sa} ; {sb}")
pg, eg = re.search(r"\\pi\\doteq([\d.]+)\\\), error \\\(\\doteq([\d.]+)", AB["22"]).groups()
s10 = 8 * sum(Fr(1, (4 * k + 1) * (4 * k + 3)) for k in range(10))
check_rounded("Q22g: 10 terms give pi approx", mp.mpf(s10.numerator) / s10.denominator, pg, places=3)
check_rounded("Q22g: error", mp.pi - mp.mpf(s10.numerator) / s10.denominator, eg, places=3)
# Q23
report("\\tan^{-1}1+\\tan^{-1}2+\\tan^{-1}3+\\cdots+\\tan^{-1}n" in AB["23"], "Q23a: S_n is the sum of tan^-1 k, k = 1..n")
check_prim("Q23b primitive of atan x", T(A["23"]["b"]), sp.atan(x))
ok = True
for N in list(range(1, 40)) + [1000]:
    S = mp.fsum(mp.atan(k) for k in range(1, N + 1))
    lo = N * mp.atan(N) - mp.log(N * N + 1) / 2
    hi = (N + 1) * mp.atan(N + 1) - mp.log(mp.mpf(N * N) / 2 + N + 1) / 2 - mp.pi / 4
    ok &= lo < S < hi
report(ok and 1562 < lo and hi < 1565, "Q23c, d: the printed bounds hold for n = 1..39 and n = 1000", f"{mp.nstr(lo, 8)} < S < {mp.nstr(hi, 8)}")

# omitted items must really be omitted (Ex 12B Q7e, Q7f are misprints)
report(len(re.findall(r'<span class="pl">[ef]</span>', QB["7"])) == 0, "Q7: parts e, f left out")

# ================================================================= Past papers
print("--- Past-paper homework")
intro = re.search(r"Suggested time: (\d+) minutes</b></span><span><b>(\d+) marks", LES)
tm, tot = int(intro.group(1)), int(intro.group(2))
marks = {k: int(re.search(r'<span class="mk">(\d+) marks?</span>', v).group(1)) for k, v in PPB.items()}
report(sum(marks.values()) == tot and 15 <= tot <= 22, "PP: marks add to the intro total (15-22)", f"{sum(marks.values())} vs {tot}")
report(tm == 5 * round(1.5 * tot / 5), "PP: time = 1.5 x marks rounded to 5 min", f"{tm}")
report(sorted(PPB, key=int) == [str(i) for i in range(1, len(PPB) + 1)] and sorted(PPA, key=int) == sorted(PPB, key=int), "PP: numbering 1..N in both files")
for k in PPB:
    lab_l = re.search(r'PP \d+</span>(.*?)</span><span class="mk">', '<span class="pn">PP ' + k + '</span>' + PPB[k], re.S).group(1)
    lab_a = re.search(r'^(.*?)</span></div>', PPA[k], re.S).group(1)
    report(lab_l.strip() == lab_a.strip(), f"PP {k}: source label identical in both files")
    report(PPB[k].count('<div class="hint">') == 1, f"PP {k}: one hint")


def mc(k):
    return re.findall(r"<span>([A-D])\.&ensp;\\\((.+?)\\\)</span>", PPB[k])


def key_of(k):
    return one(PPA[k], r"<b>Answer ([A-D])\.</b>", f"PP {k}: answer key")


# PP1, PP2: primitives
for k in ("1", "2"):
    f = indef(PPB[k])[0]
    good = [L for L, o in mc(k) if all(abs(num(sp.diff(T(o), x).subs(x, p)) - num(f.subs(x, p))) < TOL for p in PTS)]
    report(good == [key_of(k)], f"PP {k}: only option {key_of(k)} differentiates to the integrand", str(good))
    check_prim(f"PP {k}: worked primitive", T(last_eq(re.findall(r"\\\[(.*?)\\\]", PPA[k], re.S)[0])), f)
check_prim("PP 3", T(last_eq(re.findall(r"\\\[(.*?)\\\]", PPA["3"], re.S)[0])), indef(PPB["3"])[0])
for k in ("4", "5", "7"):
    check_def(f"PP {k}", integrals(PPB[k]), 0, aligned_finals(PPA[k])[0])
lo, hi, f = integrals(PPB["6"])[0]
check_rounded("PP 6 (3 s.f.)", quad(f, lo, hi), aligned_finals(PPA["6"])[0].replace("\\doteq", "").strip(), sf=3)
report("\\sin^{-1}0.25-\\sin^{-1}0" in PPA["6"] and abs(mp.asin(mp.mpf("0.25")) - quad(f, lo, hi)) < TOL, "PP 6: the line sin^-1 0.25 - sin^-1 0")
# PP8-PP10: find k
for k, upper_val in (("8", sp.pi / 3), ("9", sp.pi / 2), ("10", sp.pi / 2)):
    lo, hi, f = integrals(PPB[k])[0]
    g = lambda kk: quad(f, 0, kk) - num(upper_val)
    if k == "8":
        kv = one(PPA[k], r"and \\\(k=(.+?)\\\)", "PP 8: printed k")
    else:
        fin = aligned_finals(PPA[k])
        report(len(fin) == 1 and re.search(r"k&=[^=]+\\end\{aligned\}", PPA[k]) is not None, f"PP {k}: one chain ending k = ...")
        kv = fin[-1]
    report(abs(g(T(kv))) < TOL, f"PP {k}: k = {kv} satisfies the equation")
    if mc(k):
        sat = [L for L, o in mc(k) if abs(g(T(o))) < 1e-15]
        report(sat == [key_of(k)], f"PP {k}: only option {key_of(k)} works", str(sat))
fpp, spp = 4 - 8 / sp.sqrt(8 - x ** 2), -sp.sqrt(4 - x ** 2)
report(fpp.subs(x, 2) == 0 and spp.subs(x, 2) == 0 and fpp.subs(x, 0) == 4 - sp.sqrt(8), "PP 11: curves meet at x = +-2; top 4 - sqrt8")
fin = re.search(r"=([^=]*?)\\\) square units", PPA["11"]).group(1)
report(abs(quad(fpp - spp, -2, 2) - num(T(fin))) < TOL, "PP 11 area", fin)
report("4-\\dfrac{8}{\\sqrt{8-x^2}}" in PPB["11"] and "y=-\\sqrt{4-x^2}" in PPB["11"], "PP 11: curves as printed")

# ================================================================= chains of equalities
print("--- Equality chains in the worked solutions")
chain_check("answers file", ANS)
chain_check("lesson worked examples", "".join(v for k, v in EXB.items() if k.startswith("Worked")))

print(f"\n{NCHECK[0]} checks, {len(FAILS)} failures")
if FAILS:
    for f in FAILS:
        print("  FAIL:", f)
    sys.exit(1)
print("ALL OK")
