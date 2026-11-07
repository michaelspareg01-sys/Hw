"""Check of Lesson 12F (Integration Part 3 pack): Volumes of rotation, and the Chapter 12 review.

The script reads the values PRINTED in workspace/build/int3/l12f.html (the curves, lines and limits in the
tutor demos, your-turn items, worked examples, textbook questions, past-paper questions and review
questions, and the MC options) and in workspace/build/int3/a_12f.html (every answer). Each item is
located inside its own block (an example box, a question, an answer entry) with a template; a template
must match exactly once in its block, otherwise the item FAILS. Printed LaTeX is turned into sympy with
the shared helper int3_tex.tex, and compared with an independent computation:
  - a volume is recomputed with sympy as pi * integral of y^2 dx (or x^2 dy), from the region data
    read from the question (for the shaded regions of Ex 12F Q3, Q4 and Q16, which are given only by
    the diagrams, from the region data of the textbook diagrams, which figs_12f.py also draws);
    washers are recomputed as pi * integral of (outer^2 - inner^2), and the outer curve is checked
    to be the outer one on the interval;
  - printed derivatives and primitives are checked by differentiating with sympy at sample points;
  - printed definite integrals in the review are checked by mpmath quadrature;
  - every chain of equalities in the worked solutions whose members are constants is checked member
    by member: all members must agree;
  - MC keys are found by evaluating every option (the true volume is computed independently);
  - the trapezoidal estimate in Review Q21 is recomputed with exact integers.
It also checks the past-paper block: marks add to the intro total (15-22), time is 1.5 x marks rounded
to 5 minutes, numbering and source labels match in both files, and one hint per question; and that the
review omits Q3 and Q20.

Exit status 1 if anything fails. Run: python3 workspace/checks/int3_12f.py
"""
import os
import re
import sys

import mpmath as mp
import sympy as sp

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from int3_tex import tex as _tex, x  # noqa: E402

SRC = os.environ.get("INT3_SRC", os.path.join(HERE, "..", "build", "int3"))
mp.mp.dps = 30
TOL = mp.mpf(10) ** -14
FAILS, NCHECK = [], [0]
y = sp.Symbol("y", real=True)
th = sp.Symbol("theta", real=True)
PI = sp.pi


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
        raise ValueError(f"multi-digit function argument, not parsed: {s[:40]!r}")
    s = re.sub(r"\\text\{[^}]*\}", "", s)
    s = re.sub(r"\+\s*[Cc]\s*$", "", s).strip().rstrip(",").strip()
    e = _tex(s, {"y": y, "theta": th})
    return e


def num(e):
    return mp.mpf(sp.N(e, 40))


def same(a, b, tol=TOL):
    return abs(num(a) - num(b)) < tol


# ---------------------------------------------------------------- blocks
LES_ALL, ANS_ALL = read("l12f.html"), read("a_12f.html")
k = LES_ALL.index("<!-- ============ Chapter review")
LES, REV = LES_ALL[:k], LES_ALL[k:]
k = ANS_ALL.index("{{ahead:Review | Chapter review exercise}}")
ANS, RANS = ANS_ALL[:k], ANS_ALL[k:]
report(ANS_ALL.count("{{ahead:Review | Chapter review exercise}}") == 1, "answers: review heading as in the brief")


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


STOP_L = r'<div class="q"><span|<div class="ex |\{\{band|\{\{sec|<!-- =|<div class="pp"><div|<p class="small">There is no'
QB = blocks(LES, r'<div class="q"><span class="q-num">(\d+)</span>', STOP_L)
RB = blocks(REV, r'<div class="q"><span class="q-num">(\d+)</span>', STOP_L)
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
RA = blocks(RANS, r'<div class="a"[^>]*><span class="an">(\w+)</span>', STOP_A)
PPA = blocks(ANS, r'<div class="ppa"><div class="pp-src"><span><span class="pn">PP (\d+)</span>', STOP_A)


def one(block, pattern, label, group=1, flags=0):
    ms = list(re.finditer(pattern, block, flags))
    if len(ms) != 1:
        report(False, label, f"template matched {len(ms)} times: {pattern[:70]}")
        return None
    return ms[0].group(group)


def halves(key):
    b = AB[key]
    i = b.index("<b>Your turn.</b>")
    return b[:i], b[i:]


def chain_members(disp):
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


def finals(block):
    """Last member of every aligned display in a block, in order."""
    out = []
    for m in re.finditer(r"\\begin\{aligned\}(.*?)\\end\{aligned\}", norm(block), re.S):
        out.append(chain_members(m.group(1))[-1])
    return out


def chains_of(d):
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
            if "\\doteq" in m or "\\ldots" in m or "\\int" in m or "\\Big" in m or "\\big[" in m or "\\Rightarrow" in m:
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


def vol_x(f2, a, b, var=x):
    """pi * integral of (squared radius) from a to b."""
    return sp.simplify(PI * sp.integrate(sp.expand(f2), (var, a, b)))


def vol_y(g2, a, b):
    return vol_x(g2, a, b, y)


def check_val(label, printed_tex, exact):
    try:
        p = T(printed_tex)
    except Exception as e:  # noqa: BLE001
        report(False, label, f"cannot parse {printed_tex!r}: {e}")
        return
    report(same(p, exact), label, f"printed {p}; computed {sp.nsimplify(exact)}")


def outer_ok(top, bot, a, b, var=x):
    pts = [a + (b - a) * sp.Rational(i, 20) for i in range(1, 20)]
    return all(num(top.subs(var, t)) >= num(bot.subs(var, t)) - 1e-20 and num(bot.subs(var, t)) >= -1e-20 for t in pts)


PTS = [sp.Rational(23, 100), sp.Rational(41, 100), sp.Rational(-17, 100), sp.Rational(7, 10)]


def check_prim(label, F, f, pts=PTS, var=x):
    dF = sp.diff(F, var)
    ok = all(abs(num(dF.subs(var, p)) - num(f.subs(var, p))) < TOL for p in pts)
    report(ok, label, f"F = {F}; f = {f}")


def parts(block):
    out = {}
    for m in re.finditer(r"<b>([a-z]+)</b>\s*(?:\([iv]+\)\s*)?\\\((.+?)\\\)", block):
        if m.group(1) in out:
            report(False, f"part {m.group(1)} twice in a block")
        out[m.group(1)] = m.group(2)
    return out


# ================================================================= Lesson examples
print("--- Lesson examples")
# C1 and WE22: region of y = sqrt(R2 - x^2) to the right of x = c
for key, src in (("demo1", halves("C1")[0]), ("attempt1", halves("C1")[1]), ("Worked example 22", EXB["Worked example 22"])):
    b = EXB[key]
    R2 = int(one(b, r"semicircle \\\(y=\\sqrt\{(\d+)-x\^2\}\\\)", f"{key}: semicircle"))
    c = int(one(b, r"by the line \\\(x=(\d+)\\\)", f"{key}: line"))
    V = vol_x(R2 - x ** 2, c, sp.sqrt(R2))
    fin = finals(src)
    check_val(f"C1 {key}: volume", fin[-1], V)
# C2 and WE23: region between y = k x^2 and y = h about the y-axis
for key, src in (("demo2", halves("C2")[0]), ("attempt2", halves("C2")[1]), ("Worked example 23", EXB["Worked example 23"])):
    b = EXB[key]
    f = T(one(b, r"region between \\\(y=(.+?)\\\) and the line", f"{key}: curve"))
    h = int(one(b, r"and the line \\\(y=(\d+)\\\) about the \\\(y\\\)-axis", f"{key}: line"))
    kcoef = f.coeff(x, 2)
    report(sp.simplify(f - kcoef * x ** 2) == 0, f"{key}: curve is y = k x^2")
    V = vol_y(y / kcoef, 0, h)
    check_val(f"C2 {key}: volume", finals(src)[-1], V)
# C3 and WE24: region between y = A - (A/B^2) x^2 ... curve and chord AB, both axes
for key, src in (("demo3", halves("C3")[0]), ("attempt3", halves("C3")[1]), ("Worked example 24", EXB["Worked example 24"])):
    b = EXB[key]
    f = T(one(b, r"The curve \\\(y=(.+?)\\\) meets", f"{key}: curve"))
    A = int(one(b, r"\\\(A\(0,(\d+)\)\\\)", f"{key}: A"))
    B = int(one(b, r"\\\(B\((\d+),0\)\\\)", f"{key}: B"))
    report(f.subs(x, 0) == A and f.subs(x, B) == 0, f"{key}: A and B lie on the curve")
    line = A - sp.Rational(A, B) * x
    report(outer_ok(f, line, 0, B), f"{key}: parabola is the outer curve on [0, B]")
    Va = vol_x(f ** 2 - line ** 2, 0, B)
    xp2 = sp.solve(sp.Eq(y, f), x)[0] ** 2          # x^2 on the parabola
    xl = sp.solve(sp.Eq(y, line), x)[0]
    report(outer_ok(sp.sqrt(xp2), xl, 0, A, y), f"{key}: parabola is the outer curve on [0, A] (about y)")
    Vb = vol_y(xp2 - xl ** 2, 0, A)
    fin = [chain_members(m.group(1))[-1] for m in re.finditer(r"\\begin\{aligned\}(.*?)\\end\{aligned\}", norm(src), re.S) if "volume" in m.group(1)]
    report(len(fin) == 2, f"{key}: two aligned volume solutions (a, b)")
    check_val(f"C3 {key} a", fin[0], Va)
    check_val(f"C3 {key} b", fin[-1], Vb)
    report(Va != Vb, f"{key}: the two volumes differ")
# C4: cone and sphere
b = EXB["demo4"]
m = T(one(b, r"under the line \\\(y=(.+?)\\\) from", "demo4: line"))
lo, hi = [int(v) for v in re.search(r"from \\\(x=(\d+)\\\) to \\\(x=(\d+)\\\)", b).groups()]
V = vol_x(m ** 2, lo, hi)
r, h = m.subs(x, hi), hi - lo
check_val("C4 demo: cone by integration", finals(halves("C4")[0])[-1], V)
report(same(V, PI * r ** 2 * h / 3), "C4 demo: agrees with (1/3) pi r^2 h")
report("So \\(r=3\\) and \\(h=6\\)" in halves("C4")[0] and r == 3 and h == 6, "C4 demo: r = 3, h = 6 printed")
b = EXB["attempt4"]
R2 = int(one(b, r"semicircle \\\(y=\\sqrt\{(\d+)-x\^2\}\\\)", "attempt4: semicircle"))
V = vol_x(R2 - x ** 2, -sp.sqrt(R2), sp.sqrt(R2))
check_val("C4 your turn: sphere by integration", finals(halves("C4")[1])[-1], V)
report(same(V, sp.Rational(4, 3) * PI * sp.sqrt(R2) ** 3), "C4 your turn: agrees with (4/3) pi r^3")
for half, lab in ((0, "demo"), (1, "your turn")):
    chk = one(halves("C4")[half], r"Check: \\\((.+?)\\\)", f"C4 {lab}: check line")
    vals = [num(T(p)) for p in chk.split("=")[1:]]
    report(len(vals) == 2 and abs(vals[0] - vals[1]) < TOL, f"C4 {lab}: check line consistent")

# ================================================================= Textbook homework
print("--- Exercise 12F")
A = {k2: parts(v) for k2, v in AB.items()}


def ans(q, part, exact, label=None):
    if part not in A.get(q, {}):
        report(False, f"Q{q}{part}: answer missing")
        return
    check_val(label or f"Q{q}{part}", A[q][part], exact)


# Q1, Q2
report("line \\(y=3x\\)" in QB["1"] and "between \\(x=0\\) and \\(x=3\\)" in QB["1"], "Q1: printed data")
V1 = vol_x((3 * x) ** 2, 0, 3)
check_val("Q1b volume", one(AB["1"], r"volume \\\((.+?)\\\)", "Q1b"), V1)
report(same(V1, PI * 9 ** 2 * 3 / 3) and "radius 9, height 3" in AB["1"], "Q1b: radius 9, height 3 and (1/3) pi r^2 h")
ans("1", "c", V1)
report("\\(y=\\sqrt{9-x^2}\\)" in QB["2"], "Q2: printed data")
V2 = vol_x(9 - x ** 2, -3, 3)
check_val("Q2b volume", one(AB["2"], r"volume \\\((.+?)\\\)", "Q2b"), V2)
report(same(V2, sp.Rational(4, 3) * PI * 27) and "radius 3" in AB["2"], "Q2b: radius 3 and (4/3) pi r^3")
ans("2", "c", V2)
# Q3 (diagram data, about x)
Q3 = {"a": (4, -2, 2), "b": (x ** 2, 0, 3), "c": (x ** 4, 0, 2), "d": (x, 2, 4), "e": (4 - x ** 2, 0, 2),
      "f": (x ** 6, -1, 0), "g": ((x + 2) ** 2, -5, -2), "h": (4 - 4 * x ** 2 / 9, -3, 3)}
for p_, (f2, a_, b_) in Q3.items():
    ans("3", p_, vol_x(f2, a_, b_))
Q4 = {"a": (1, 0, 3), "b": (4 * y ** 2, 0, 4), "c": (y ** 4, 2, 5), "d": (y, 0, 1), "e": (16 - y ** 2, -4, 4),
      "f": (y ** 4, -3, 0), "g": ((2 * y - y ** 2) ** 2, 0, 2), "h": (4 - 4 * y ** 2, -1, 1)}
for p_, (g2, a_, b_) in Q4.items():
    ans("4", p_, vol_y(g2, a_, b_))
report(os.path.exists(os.path.join(SRC, "svg", "q12f_q3a.svg")) and os.path.exists(os.path.join(SRC, "svg", "q12f_q4b.svg")), "Q3, Q4: diagrams present")
# Q5 - Q7
report("\\(y=e^x\\)" in QB["5"] and "from \\(x=0\\) to \\(x=1\\)" in QB["5"], "Q5: printed data")
check_val("Q5", one(AB["5"], r'<div class="ab"[^>]*>\\\((.+?)\\\)', "Q5"), vol_x(sp.exp(2 * x), 0, 1))
f6 = T(one(QB["6"], r"curve \\\(y=(.+?)\\\) and", "Q6 curve"))
check_val("Q6", one(AB["6"], r'<div class="ab"[^>]*>\\\((.+?)\\\)', "Q6"), vol_x(f6 ** 2, 2, 4))
f7 = T(one(QB["7"], r"curve \\\(y=(.+?)\\\) \(called", "Q7 curve"))
report("from \\(y=1\\) to \\(y=6\\)" in QB["7"], "Q7: limits")
xx7 = sp.solve(sp.Eq(y, f7), x)
check_val("Q7", one(AB["7"], r'<div class="ab"[^>]*>\\\((.+?)\\\)', "Q7"), vol_y(xx7[-1] ** 2, 1, 6))
# Q8, Q9
idt = A["8"]["a"].split("=")
report(all(same(T(idt[0]).subs(x, p), T(idt[1]).subs(x, p)) for p in PTS), "Q8a identity")
ans("8", "b", vol_x(sp.tan(x) ** 2, 0, PI / 3))
idt = A["9"]["a"].split("=")
report(all(same(T(idt[0]).subs(x, p), T(idt[1]).subs(x, p)) for p in PTS), "Q9a identity")
ans("9", "b", vol_x(sp.sin(x) ** 2, 0, PI / 2))
# Q10 about x
q10 = dict(re.findall(r'<span class="pl">([a-h])</span>\\\((.+?)\\\)', QB["10"]))
report("y=x+3,\\ x=3,\\ x=5" in q10["a"] and "y=1+\\sqrt x,\\ x=1,\\ x=4" in q10["b"] and "y=5x-x^2" in q10["c"] and "y=x^3-x" in q10["d"], "Q10: printed boundaries")
ans("10", "a", vol_x((x + 3) ** 2, 3, 5))
ans("10", "b", vol_x((1 + sp.sqrt(x)) ** 2, 1, 4))
ans("10", "c", vol_x((5 * x - x ** 2) ** 2, 0, 5))
ans("10", "d", vol_x((x ** 3 - x) ** 2, -1, 1))
# Q11 about y
q11 = dict(re.findall(r'<span class="pl">([a-h])</span>\\\((.+?)\\\)', QB["11"]))
report("x=y-2,\\ y=3,\\ x=1" in q11["a"] and "x=y^2+1,\\ y=0,\\ y=1" in q11["b"] and "x=y(y-3)" in q11["c"] and "y=1-x^2" in q11["d"], "Q11: printed boundaries")
ans("11", "a", vol_y((y - 2) ** 2, 2, 3))       # triangle (0,2), (1,3), (0,3)
ans("11", "b", vol_y((y ** 2 + 1) ** 2, 0, 1))
ans("11", "c", vol_y((y * (y - 3)) ** 2, 0, 3))
ans("11", "d", vol_y(1 - y, 0, 1))
# Q12, Q13 (show that): the printed results
v12 = T(one(QB["12"], r"Show that its volume is \\\((.+?)\\\) u", "Q12 result"))
report(same(v12, vol_x((1 + 1 / x) ** 2, sp.Rational(1, 2), 3)), "Q12: printed result is the volume")
v13 = T(one(QB["13"], r"the stud is \\\((.+?)\\\) u", "Q13 result"))
report(same(v13, vol_x((sp.exp(x) - sp.exp(-x)) ** 2, 0, sp.Rational(1, 2))), "Q13: printed result is the volume")
# Q14
V14 = vol_x((4 + 4 * sp.sin(x / 4)) ** 2, 4 * PI, 6 * PI)
t14 = one(AB["14"], r"\\\((.+?)\\doteq71\.62\\\) mL", "Q14")
report(same(T(t14), V14) and round(float(V14), 2) == 71.62, "Q14: 16 pi (3 pi - 8) = 71.62 (4 s.f.)", f"{float(V14):.6f}")
# Q15
ans("15", "a", PI * 4 ** 2 * 16)
ans("15", "b", vol_y(y, 0, 16))
ans("15", "c", PI * 4 ** 2 * 16 - vol_y(y, 0, 16))
# Q16 (diagram data): i about x, ii about y
q16 = re.findall(r"<b>([a-d])</b> \\\((.+?)\\\) u\\\(\^3\\\), \\\((.+?)\\\) u\\\(\^3\\\)", AB["16"])
report(len(q16) == 4, "Q16: four pairs printed")
exp16 = {"a": (vol_x(x ** 4, 0, 2), PI * 4 * 4 - vol_y(y, 0, 4)),
         "b": (PI * 25 * 1 - vol_x(25 * x ** 2, 0, 1), vol_y(y ** 2 / 25, 0, 5)),
         "c": (vol_x(x, 0, 4), PI * 16 * 2 - vol_y(y ** 4, 0, 2)),
         "d": (PI * 16 * 1 - vol_x((x ** 2 + 3) ** 2, 0, 1), vol_y(y - 3, 3, 4))}
for p_, i_, ii_ in q16:
    check_val(f"Q16{p_} i", i_, exp16[p_][0])
    check_val(f"Q16{p_} ii", ii_, exp16[p_][1])
# Q17
report("y=x^2\\) and \\(y=x^3" in QB["17"], "Q17: printed curves")
report("\\((0,0)\\) and \\((1,1)\\)" in AB["17"] and sp.solve(x ** 2 - x ** 3, x) == [0, 1], "Q17a: intersections")
q17 = re.findall(r"\(i+\) \\\((.+?)\\\) u", AB["17"])
check_val("Q17b i", q17[0], vol_x(x ** 4 - x ** 6, 0, 1))
check_val("Q17b ii", q17[1], vol_y(y ** sp.Rational(2, 3) - y, 0, 1))
# Q18
report(set(sp.solve([x * y - 5, x + y - 6], [x, y])) == {(1, 5), (5, 1)} and "\\((1,5)\\) and \\((5,1)\\)" in AB["18"], "Q18a: intersections")
report(outer_ok(6 - x, 5 / x, 1, 5), "Q18: line above hyperbola")
ans("18", "b", vol_x((6 - x) ** 2 - 25 / x ** 2, 1, 5))
# Q19
f19 = T(one(QB["19"], r"hyperbola \\\(y=(.+?)\\\), the vertical", "Q19 curve"))
report(sp.solve(sp.Eq(f19, 1), x) == [2] and f19.subs(x, 1) == 0, "Q19: hyperbola meets y = 1 at x = 2, x-axis at x = 1")
check_val("Q19", one(AB["19"], r'<div class="ab"[^>]*>\\\((.+?)\\\) u', "Q19"), vol_x(1 - f19 ** 2, 1, 2))
# Q20
cur = x ** 3 + 2
tang = sp.expand(cur.subs(x, 1) + sp.diff(cur, x).subs(x, 1) * (x - 1))
report(sp.simplify(T(A["20"]["a"].split("=")[1]) - tang) == 0, "Q20a tangent", str(tang))
report(outer_ok(cur, tang, 0, 1), "Q20: curve above tangent on [0, 1]")
q20 = re.findall(r"\(i+\) \\\((.+?)\\\) u", AB["20"])
check_val("Q20c i", q20[0], vol_x(cur ** 2 - tang ** 2, 0, 1))
Vii = vol_y((y / 3) ** 2, 0, 3) - vol_y((y - 2) ** sp.Rational(2, 3), 2, 3)
check_val("Q20c ii", q20[1], Vii)
# Q21 rubber washer
check_val("Q21", one(AB["21"], r'<div class="ab"[^>]*>\\\((.+?)\\\) u', "Q21"), vol_y(4 - sp.exp(2 * y), 0, sp.log(2)))
# Q22 results
r_, h_ = sp.symbols("r h", positive=True)
report(sp.simplify(PI * sp.integrate((r_ * x / h_) ** 2, (x, 0, h_)) - PI * r_ ** 2 * h_ / 3) == 0, "Q22a: cone")
report(sp.simplify(PI * sp.integrate(r_ ** 2, (x, 0, h_)) - PI * r_ ** 2 * h_) == 0, "Q22b: cylinder")
report(sp.simplify(PI * sp.integrate(r_ ** 2 - x ** 2, (x, -r_, r_)) - sp.Rational(4, 3) * PI * r_ ** 3) == 0, "Q22c(i): sphere")
report(sp.simplify(PI * sp.integrate(r_ ** 2 - x ** 2, (x, r_ - h_, r_)) - PI * h_ ** 2 * (3 * r_ - h_) / 3) == 0, "Q22c(ii): cap")
# Q23
check_prim("Q23a primitive of sec", T(A["23"]["a"]).subs(x, th), sp.sec(th), var=th)
v23 = T(one(QB["23"], r"about the \\\(y\\\)-axis is \\\((.+?)\\\) units", "Q23b result"))
xx2 = 16 * y ** 2 / (1 - y ** 2)
V23 = PI * 16 * (1 / sp.sqrt(2)) - mp.pi * mp.quad(sp.lambdify(y, xx2, "mpmath"), [0, 1 / mp.sqrt(2)])
report(abs(num(v23) - num(V23)) < TOL, "Q23b: printed result is the volume (cylinder minus inner)")
# Q24
nn = sp.Symbol("n", positive=True, integer=True)
report("\\((0,0)\\) and \\((1,1)\\)" in AB["24"], "Q24a points")
Vn = sp.simplify(PI * sp.integrate(x ** (2 * nn) - x ** (2 * nn + 2), (x, 0, 1)))
report(sp.simplify(Vn - PI * (1 / (2 * nn + 1) - 1 / (2 * nn + 3))) == 0, "Q24b: V_n formula")
ans("24", "d", sp.limit(sp.summation(Vn, (nn, 1, sp.Symbol("N", positive=True, integer=True))), sp.Symbol("N", positive=True, integer=True), sp.oo))
report(same(PI / 3, vol_x(x ** 2, 0, 1)) and "rotating the line \\(y=x\\) from \\(x=0\\) to \\(x=1\\)" in AB["24"], "Q24c: the cone, volume pi/3")
report(sp.summation(1 / ((2 * nn + 1) * (2 * nn + 3)), (nn, 1, sp.oo)) == sp.Rational(1, 6), "Q24e: limiting sum 1/6")
# Q25
q25 = -x ** 2 + 6 * x - 8
report(sp.solve(q25, x) == [2, 4] and "\\(x=2\\) and \\(x=4\\), with vertex \\((3,1)\\)" in AB["25"], "Q25a")
report(all(sp.simplify(q25.subs(x, 3 + s * sp.sqrt(1 - y)) - y) == 0 for s in (1, -1)), "Q25b: both branches")
report(sp.simplify(sp.expand((3 + sp.sqrt(1 - y)) ** 2 - (3 - sp.sqrt(1 - y)) ** 2) - 12 * sp.sqrt(1 - y)) == 0, "Q25c: integrand 12 sqrt(1 - y)")
ans("25", "c", vol_y(12 * sp.sqrt(1 - y), 0, 1))

# ================================================================= Past papers
print("--- Past-paper homework")
intro = re.search(r"Suggested time: (\d+) minutes</b></span><span><b>(\d+) marks", LES)
tm, tot = int(intro.group(1)), int(intro.group(2))
marks = {k2: int(re.search(r'<span class="mk">(\d+) marks?</span>', v).group(1)) for k2, v in PPB.items()}
report(sum(marks.values()) == tot and 15 <= tot <= 22, "PP: marks add to the intro total (15-22)", f"{sum(marks.values())} vs {tot}")
report(tm == 5 * round(1.5 * tot / 5), "PP: time = 1.5 x marks rounded to 5 min", f"{tm}")
report(sorted(PPB, key=int) == [str(i) for i in range(1, len(PPB) + 1)] and sorted(PPA, key=int) == sorted(PPB, key=int), "PP: numbering 1..N in both files")
for k2 in PPB:
    lab_l = re.search(r'PP \d+</span>(.*?)</span><span class="mk">', '<span class="pn">PP ' + k2 + '</span>' + PPB[k2], re.S).group(1)
    lab_a = re.search(r'^(.*?)</span></div>', PPA[k2], re.S).group(1)
    report(lab_l.strip() == lab_a.strip(), f"PP {k2}: source label identical in both files")
    report(PPB[k2].count('<div class="hint">') == 1, f"PP {k2}: one hint")
    sub = re.findall(r'<div class="pp-sub"><span>.*?</span><span class="mk">(\d+)</span>', PPB[k2], re.S)
    if sub:
        report(sum(map(int, sub)) == marks[k2], f"PP {k2}: part marks add up")


def key_of(k2):
    return one(PPA[k2], r"<b>Answer ([A-D])\.</b>", f"PP {k2}: answer key")


def opts(k2):
    return dict(re.findall(r"<span>([A-D])\.&ensp;\\\((.+?)\\\)</span>", PPB[k2]))


# PP1: y = e^{x/2}, 1 <= y <= 2, about the y-axis
report("\\(y=e^{\\frac x2}\\)" in PPB["1"] and "\\(1\\le y\\le2\\)" in PPB["1"], "PP 1: printed data")
true1 = PI * sp.integrate((2 * sp.log(y)) ** 2, (y, 1, 2))
o = opts("1")
vals = {}
for L, t in o.items():
    t = norm(t).replace("\\displaystyle", "")
    mm = re.match(r"V=4\\pi\\int_1\^2(.+?)\\,d([xy])$", t)
    var = y if mm.group(2) == "y" else x
    vals[L] = 4 * PI * sp.integrate(T(mm.group(1)).subs(x, var) if var == y else T(mm.group(1)), (var, 1, 2))
good = [L for L, v in vals.items() if same(v, true1)]
report(good == [key_of("1")] == ["D"], "PP 1: only option D gives the volume", str(good))
# PP2: Caringbah
f = T(one(PPB["2"], r"curve \\\(y=(.+?)\\\) and", "PP 2 curve"))
report("between \\(x=8\\) and \\(x=10\\)" in PPB["2"], "PP 2: limits")
check_val("PP 2 volume", finals(PPA["2"])[-1], vol_x(f ** 2, 8, 10))
# PP3: NSB MC
aa = mp.findroot(lambda t: (t - 1) ** 2 - mp.log(t), 1.8)
report(abs((aa - 1) ** 2 - mp.log(aa)) < TOL, "PP 3: A(a, ln a) found", mp.nstr(aa, 10))
true3 = mp.pi * mp.quad(lambda t: (mp.sqrt(t) + 1) ** 2 - mp.e ** (2 * t), [0, mp.log(aa)])
report(true3 > 0 and all((mp.sqrt(t) + 1) > mp.e ** t for t in mp.linspace(mp.mpf("0.01"), mp.log(aa) - mp.mpf("0.01"), 30)), "PP 3: the parabola is the outer curve", mp.nstr(true3, 10))
exp_opts = {"A": (r"V=\pi\displaystyle\int_0^{\ln a}\big(\sqrt y+1-e^y\big)^2\,dy", lambda t: (mp.sqrt(t) + 1 - mp.e ** t) ** 2, "y"),
            "B": (r"V=\pi\displaystyle\int_0^{\ln a}\big(y+2\sqrt y+1-e^{2y}\big)\,dy", lambda t: t + 2 * mp.sqrt(t) + 1 - mp.e ** (2 * t), "y"),
            "C": (r"V=\pi\displaystyle\int_1^a(\ln x)^2-(x-1)^4\,dx", lambda t: mp.log(t) ** 2 - (t - 1) ** 4, "x"),
            "D": (r"V=\pi\displaystyle\int_0^{\ln a}\big(\sqrt y+1-e^y\big)\,dy", lambda t: mp.sqrt(t) + 1 - mp.e ** t, "y")}
o = opts("3")
good = []
for L, (txt, fn, var) in exp_opts.items():
    report(o.get(L) == txt, f"PP 3 option {L} printed as expected")
    v = mp.pi * mp.quad(fn, [0, mp.log(aa)] if var == "y" else [1, aa])
    if abs(v - true3) < TOL:
        good.append(L)
report(good == [key_of("3")] == ["B"], "PP 3: only option B gives the volume", str(good))
# PP4: Killara
report("\\(f(x)=\\sin x\\cos x\\)" in PPB["4"] and "x\\in\\big[0,\\tfrac{\\pi}{2}\\big]" in PPB["4"], "PP 4: printed data")
check_val("PP 4 volume", finals(PPA["4"])[-1], vol_x((sp.sin(x) * sp.cos(x)) ** 2, 0, PI / 2))
sq = finals(PPA["4"])[0]
report(all(same(T(sq).subs(x, p), ((sp.sin(x) * sp.cos(x)) ** 2).subs(x, p)) for p in PTS), "PP 4: (f(x))^2 = 1/8 (1 - cos 4x)")
# PP5: BBHS
d5 = one(PPA["5"], r"=e\^\{2\\sin x\}\\times2\\cos x=(.+?)\.\\\]", "PP 5 (i)")
report(d5 == "2\\cos x\\,e^{2\\sin x}" and sp.simplify(sp.diff(sp.exp(2 * sp.sin(x)), x) - 2 * sp.cos(x) * sp.exp(2 * sp.sin(x))) == 0, "PP 5 (i) derivative", d5 or "")
f5 = sp.sqrt(sp.cos(x)) * sp.exp(sp.sin(x))
report("\\(y=\\sqrt{\\cos x}\\,e^{\\sin x}\\)" in PPB["5"], "PP 5: printed curve")
check_val("PP 5 (ii) volume", finals(PPA["5"])[-1], vol_x(sp.cos(x) * sp.exp(2 * sp.sin(x)), 0, PI / 2))
report(same(sp.Integral(f5 ** 2, (x, 0, PI / 2)).evalf(30) * PI, sp.pi / 2 * (sp.E ** 2 - 1)), "PP 5: quadrature agrees")
# PP6: STHS
report("\\(y=x^2\\) and \\(y=5-4x^2\\)" in PPB["6"], "PP 6: printed curves")
report(sp.solve([y - x ** 2, y - 5 + 4 * x ** 2], [x, y]) and (1, 1) in sp.solve([y - x ** 2, y - 5 + 4 * x ** 2], [x, y]), "PP 6: curves meet at (1, 1)")
check_val("PP 6 volume", finals(PPA["6"])[-1], vol_y(y, 0, 1) + vol_y((5 - y) / 4, 1, 5))
# PP7: SGHS
report("\\(y=\\dfrac12x+3\\)" in PPB["7"] and "\\(y=x^2\\)" in PPB["7"], "PP 7: printed curves")
report(sp.solve(x ** 2 - x / 2 - 3, x) == [sp.Rational(-3, 2), 2], "PP 7: meet at x = 2 (and -3/2)")
V7 = vol_y(y, 0, 3) + vol_y(y - (2 * y - 6) ** 2, 3, 4)
report(outer_ok(sp.sqrt(y), 2 * y - 6, 3, 4, y), "PP 7: parabola outer on [3, 4]")
check_val("PP 7 volume", finals(PPA["7"])[-1], V7)
V7b = PI * sp.integrate((x / 2 + 3 - x ** 2) * 2 * x, (x, 0, 2))     # shells, an independent route
report(same(V7, V7b), "PP 7: agrees with a shell-method computation")
# PP8: JR
report("\\(x^2=8(y-3)\\)" in PPB["8"] and "line \\(y=5\\)" in PPB["8"], "PP 8: printed data")
p8 = 3 + x ** 2 / 8
report(sp.solve(p8 - 5, x) == [-4, 4] and "vertex \\((0,3)\\)" in PPA["8"], "PP 8: meets y = 5 at x = -4, 4; vertex (0, 3)")
check_val("PP 8 volume", finals(PPA["8"])[-1], vol_x(25 - p8 ** 2, -4, 4))
report(same(PI * 25 * 8 - vol_x(p8 ** 2, -4, 4), vol_x(25 - p8 ** 2, -4, 4)), "PP 8: cylinder-minus route agrees")

# ================================================================= Chapter review
print("--- Chapter review")
report(sorted(RB, key=int) == ["1", "2", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "21"], "Review: Q3 and Q20 omitted, others present", str(sorted(RB, key=int)))
R = {k2: parts(v) for k2, v in RA.items()}


def rq(q):
    """Question parts: letter -> maths (first \\( \\) after the part label)."""
    return dict(re.findall(r'<span class="pl">([a-f])</span>\\\((.+?)\\\)', RB[q]))


def brace(s, i):
    d = 0
    for j in range(i, len(s)):
        d += s[j] == "{"
        d -= s[j] == "}"
        if d == 0:
            return s[i + 1:j], j + 1
    raise ValueError("unbalanced")


def lim(s, i):
    if s[i] == "{":
        return brace(s, i)
    m = re.match(r"-?\d+|\\[A-Za-z]+|\w", s[i:])
    return m.group(0), i + len(m.group(0))


def integrand(t):
    t = norm(t).replace("\\displaystyle", "").strip()
    assert t.startswith("\\int")
    i = 4
    lo = hi = None
    if t[i] == "_":
        lo, i = lim(t, i + 1)
        assert t[i] == "^"
        hi, i = lim(t, i + 1)
    k = t.rindex("\\,d")
    return (T(lo) if lo else None), (T(hi) if hi else None), T(t[i:k])


# Q1 derivatives
q1 = rq("1")
for p_ in "abcdef":
    fn = T(q1[p_].split("=", 1)[1])
    pts = {"a": [sp.Rational(1, 20), sp.Rational(1, 10), sp.Rational(-1, 5)], "c": [sp.Rational(1, 5), sp.Rational(7, 10), sp.Rational(3, 2)],
           "f": [sp.Rational(3, 2), 2, sp.Rational(-17, 10)]}.get(p_, PTS)
    check_prim(f"Review Q1{p_}", fn, T(R["1"][p_]), pts)
# Q2 show
yy = sp.atan(x)
report(sp.simplify((1 + x ** 2) * sp.diff(yy, x, 2) + 2 * x * sp.diff(yy, x)) == 0, "Review Q2: tan^-1 x satisfies the equation")
# Q4, Q6, Q9, Q11 primitives
for q, pts in (("4", [sp.Rational(1, 5), sp.Rational(-1, 3), sp.Rational(2, 5)]), ("6", PTS), ("9", [sp.Rational(1, 5), sp.Rational(1, 3), sp.Rational(3, 5)]),
               ("11", [sp.Rational(3, 2), 2, sp.Rational(5, 2)])):
    for p_, t in rq(q).items():
        _, _, f_ = integrand(t)
        check_prim(f"Review Q{q}{p_}", T(R[q][p_]), f_, pts)
# Q5, Q7, Q10, Q12 definite integrals
for q in ("5", "7", "10", "12"):
    for p_, t in rq(q).items():
        lo, hi, f_ = integrand(t)
        v = mp.quad(sp.lambdify(x, f_, "mpmath"), [num(lo), num(hi)])
        pr = T(R[q][p_])
        report(abs(v - num(pr)) < TOL, f"Review Q{q}{p_}", f"quad {mp.nstr(v, 12)}; printed {pr}")
# Q8
for t in re.findall(r"\\int_0\^\{\\frac\{\\pi\}\{2\}\}(\\cos\^2\w*x)\\,dx", norm(RB["8"])):
    v = mp.quad(sp.lambdify(x, T(t), "mpmath"), [0, mp.pi / 2])
    report(abs(v - mp.pi / 4) < TOL, f"Review Q8: {t} over [0, pi/2] is pi/4")
report(len(re.findall(r"\\int_0\^\{\\frac\{\\pi\}\{2\}\}", norm(RB["8"]))) == 3, "Review Q8: three integrals printed")
# Q13
report("y=\\sqrt{9-x}" in RB["13"], "Review Q13: printed function")
report("domain \\(x\\le9\\), range \\(y\\ge0\\)" in RA["13"], "Review Q13a")
check_val("Review Q13c area", one(RA["13"], r"<b>c</b> \\\((.+?)\\\) u", "Q13c"), sp.integrate(sp.sqrt(9 - x), (x, 0, 9)))
q13 = re.findall(r"\(i+\) \\\((.+?)\\\) u", RA["13"])
check_val("Review Q13d i", q13[0], vol_x(9 - x, 0, 9))
check_val("Review Q13d ii", q13[1], vol_y((9 - y ** 2) ** 2, 0, 3))
# Q14, Q15
f14 = T(one(RB["14"], r"curve \\\(y=(.+?)\\\) and", "Q14 curve"))
report("to \\(x=3\\tfrac34\\)" in RB["14"], "Review Q14: limit 3 3/4")
check_val("Review Q14", one(RA["14"], r'<div class="ab"[^>]*>\\\((.+?)\\\) u', "R14"), vol_x(f14 ** 2, 0, sp.Rational(15, 4)))
report("\\(y^2=18(x-6)\\) from \\(y=-6\\) to \\(y=6\\)" in RB["15"], "Review Q15: printed data")
check_val("Review Q15", one(RA["15"], r'<div class="ab"[^>]*>\\\((.+?)\\\) u', "R15"), vol_y((6 + y ** 2 / 18) ** 2, -6, 6))
# Q16
idt = R["16"]["a"].split("=")
report(all(same(T(idt[0]).subs(x, p), T(idt[1]).subs(x, p)) for p in PTS), "Review Q16a identity")
v16 = T(one(RB["16"], r"has volume \\\((.+?)\\\) \\\(u", "R16 result"))
report(same(v16, vol_x(sp.cos(2 * x) ** 2, -PI / 6, PI / 6)), "Review Q16b: printed result is the volume")
# Q17
V17 = vol_x((1 + sp.exp(-x)) ** 2, 1, 3)
report("\\(8.49\\) u" in RA["17"] and round(float(V17), 2) == 8.49, "Review Q17 (2 d.p.)", f"{float(V17):.6f}")
# Q18
report("\\(\\big(\\tfrac{\\pi}{4},0\\big)\\)" in RA["18"] and sp.solve(1 - sp.tan(x), x)[0] == PI / 4, "Review Q18a: R meets the x-axis at pi/4")
check_val("Review Q18b", one(RA["18"], r"<b>b</b> \\\((.+?)\\\) u", "R18b"), vol_x((1 - sp.tan(x)) ** 2, 0, PI / 4))
# Q19
g19 = x + 1 / x
sps = sorted((s, g19.subs(x, s)) for s in sp.solve(sp.diff(g19, x), x))
report(sps == [(-1, -2), (1, 2)] and "Minimum turning point at \\((1,2)\\), maximum turning point at \\((-1,-2)\\)" in RA["19"]
       and sp.diff(g19, x, 2).subs(x, 1) > 0 > sp.diff(g19, x, 2).subs(x, -1), "Review Q19a: stationary points and their nature")
report(sorted(sp.solve(g19 - sp.Rational(5, 2), x)) == [sp.Rational(1, 2), 2], "Review Q19b")
report(outer_ok(sp.Rational(5, 2) + 0 * x, g19, sp.Rational(1, 2), 2), "Review Q19: line above curve")
check_val("Review Q19c", one(RA["19"], r"<b>c</b> \\\((.+?)\\\) u", "R19c"), vol_x(sp.Rational(25, 4) - g19 ** 2, sp.Rational(1, 2), 2))
# Q21
report("\\(y=2^{x+1}\\) between \\(x=1\\) and \\(x=3\\)" in RB["21"], "Review Q21: printed data")
ia = one(RA["21"], r"<b>a</b> \\\(\\pi\\displaystyle\\int_1\^3(.+?)\\,dx\\\)", "R21a")
report(all(same(T(ia).subs(x, p), ((2 ** (x + 1)) ** 2).subs(x, p)) for p in PTS), "Review Q21a: integrand is y^2")
hh = sp.Rational(1, 2)
vals21 = [((2 ** (x + 1)) ** 2).subs(x, 1 + i * hh) for i in range(5)]
trap = hh / 2 * (vals21[0] + 2 * sum(vals21[1:4]) + vals21[4])
check_val("Review Q21b trapezoidal (5 values)", one(RA["21"], r"<b>b</b> \\\((.+?)\\\) u", "R21b"), PI * trap)
exact21 = vol_x((2 ** (x + 1)) ** 2, 1, 3)
c21 = one(RA["21"], r"<b>c</b> \\\((.+?)\\doteq173\\pi\\\)", "R21c")
report(same(T(c21), exact21) and round(float(exact21 / PI)) == 173 and exact21 < PI * trap, "Review Q21c: exact 120 pi / ln 2 = 173 pi, below the trapezoidal value")
report(sp.diff((2 ** (x + 1)) ** 2, x, 2).subs(x, 2) > 0, "Review Q21c: integrand concave up")

# ================================================================= chains of equalities
print("--- Equality chains in the worked solutions")
chain_check("answers file (lesson)", ANS)
chain_check("lesson worked examples", "".join(v for k2, v in EXB.items() if k2.startswith("Worked")))

print(f"\n{NCHECK[0]} checks, {len(FAILS)} failures")
if FAILS:
    for f_ in FAILS:
        print("  FAIL:", f_)
    sys.exit(1)
print("ALL OK")
