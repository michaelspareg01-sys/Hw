"""Check of Lesson 6J (Integration Part 2 pack): Applications of integration of 1/x.

The script reads the values PRINTED in workspace/build/int2/l6j.html (the tip example, the tutor demos and
your-turn items, Worked example 38, Exercise 6J, the timed-practice note) and in a_6j.html (lesson-example
answers and textbook answers). Printed LaTeX is turned into sympy with the shared helper int3_tex.py and
every result is recomputed independently:
  - every printed chain 'A = B = C' (inline or aligned) that holds an integral or a bracket [F]_a^b is
    checked line by line: definite integrals with sympy.integrate, brackets by substitution, plain
    arithmetic by simplification; a closing '\\doteq d' is compared with the exact value rounded;
  - every region of the lesson and of the exercise is set up here from its description (curves, lines,
    limits; intersections and x-intercepts found with sympy.solve) and its area is found as the sum of
    |integral| over the pieces between the roots; the printed answer must match, and the question text
    must contain the curves and limits used;
  - decimals are compared with the exact values rounded as asked; the trapezoidal estimate is recomputed;
    derivatives use sympy.diff; Q20's primitive is differentiated back.
It also checks the structure (questions 1-23, bands F 1-9, D 10-17, E 18-23), the timed-practice note
(no past-paper block, referenced questions exist) and that every {{svg:...}} exists. A template must match
exactly once; a missing template FAILS.

Exit status 1 if anything fails. Run: python3 workspace/checks/int2_6j.py
"""
import os
import re
import sys

import sympy as sp

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import int3_tex as T  # noqa: E402

SRC = os.environ.get("INT2_SRC", os.path.join(HERE, "..", "build", "int2"))
x = T.x
t = sp.Symbol("t", positive=True)
nn = sp.Symbol("n", positive=True)
E = sp.E
EXTRA = {"C": sp.Integer(0), "t": t}
FAILS, CNT = [], [0]


def report(ok, label, detail=""):
    CNT[0] += 1
    print(("OK       " if ok else "MISMATCH ") + label[:90] + ("  " + str(detail).replace("\n", " ")[:170] if detail else ""))
    if not ok:
        FAILS.append(label)


def read(name):
    with open(os.path.join(SRC, name), encoding="utf-8") as fh:
        return fh.read()


# ---------------------------------------------------------------- TeX -> sympy
def prep(t_):
    t_ = t_.replace("&amp;", "").replace("&", "").replace("\\displaystyle", "")
    t_ = re.sub(r"\\text\{[^{}]*\}", "", t_)
    t_ = re.sub(r"\\qquad\\big\(\\times\\tfrac2x\\big\)", "", t_)
    t_ = re.sub(r"\\sqrt\s*(\w)", r"\\sqrt{\1}", t_)
    t_ = re.sub(r"(?<![\^\w{])(\d+)\\tfrac(\d)(\d)", r"(\1+\\tfrac{\2}{\3})", t_)  # mixed numbers
    t_ = t_.replace("\\,", " ").replace("\\ ", " ")
    return t_.strip().rstrip(".,").strip()


def tex(t_, extra=None):
    loc = dict(EXTRA)
    if extra:
        loc.update(extra)
    return T.tex(prep(t_), loc)


LIM = r"(\{(?:[^{}]|\{[^{}]*\})*\}|-?\w)"


def unbrace(g):
    return g[1:-1] if g.startswith("{") else g


def side(t_, var=x):
    """One side of a chain -> sympy, with integrals and [F]_a^b brackets replaced by values."""
    t_ = prep(t_)
    extra, n = {}, [0]

    def ph(val):
        name = f"Z{n[0]}Z"
        n[0] += 1
        extra[name] = val
        return " " + name + " "

    def brk(mt):
        F = tex(mt.group(1))
        return "(" + ph(F.subs(var, tex(unbrace(mt.group(3)))) - F.subs(var, tex(unbrace(mt.group(2))))) + ")"

    t_ = re.sub(r"\\Big\[(.*?)\\Big\]_" + LIM + r"\^" + LIM, brk, t_)

    def itg(mt):
        g = tex(mt.group(3))
        return "(" + ph(sp.integrate(g, (x, tex(unbrace(mt.group(1))), tex(unbrace(mt.group(2)))))) + ")"

    t_ = re.sub(r"\\int_" + LIM + r"\^" + LIM + r"(.*?)\s*dx", itg, t_)
    for name in extra:
        T.LOCAL.setdefault(name, sp.Symbol(name))
    return tex(t_, extra)


def same(a, b):
    return sp.simplify(sp.expand(sp.expand_log(a - b, force=True))) == 0


def aligned_chain(body):
    body = re.sub(r"\\begin\{aligned\}|\\end\{aligned\}", "", body)
    return "".join(ln.replace("&amp;", "").strip() for ln in body.split("\\\\"))


def chain(text, label, var=x):
    """Check a printed chain; return (last exact value, printed decimal or None)."""
    seg = aligned_chain(text) if "aligned" in text else text
    dec = None
    m = re.search(r"\\doteq\s*(-?[\d.]+)", seg)
    if m:
        dec = m.group(1)
        seg = seg[:m.start()]
    seg = seg.replace("\\text{Area}", "").replace("\\text{Hence area}", "")
    sides = [q_ for q_ in T.split_top(prep(seg), "=") if q_.strip()]
    try:
        vals = [side(q_, var) for q_ in sides]
    except Exception as err:  # noqa: BLE001
        report(False, label, f"ERROR {err} in {seg[:80]!r}")
        return None, None
    ok = len(vals) >= 2 and all(same(vals[0], v) for v in vals[1:])
    if dec is not None:
        nd = len(dec.split(".")[1]) if "." in dec else 0
        ok = ok and dec == f"{float(vals[-1]):.{nd}f}"
    report(ok, label, f"{len(vals)} sides" + (f", ~{dec}" if dec else "") + ": " + " | ".join(sides)[:140])
    return vals[-1], dec


TOPLINE = re.compile(r"\\int_\d\^\d\(\\text\{top curve\}-\\text\{bottom curve\}\)\\,dx\\\\&amp;=")


def displays(block):
    return re.findall(r"\\\[(.*?)\\\]", block, re.S)


def grab(block, pattern, where, flags=re.S):
    found = re.findall(pattern, block, flags)
    if len(found) != 1:
        raise LookupError(f"{where}: pattern matched {len(found)} times: {pattern[:70]!r}")
    return found[0]


def area_abs(f, a, b):
    """Area between y = f(x) and the x-axis on [a, b]: split at the roots, add |integral| of each piece."""
    roots = sorted({r for r in sp.solve(sp.Eq(f, 0), x) if r.is_real and a < r < b}, key=float)
    pts = [a] + roots + [b]
    return sp.nsimplify(sum(sp.Abs(sp.integrate(f, (x, p, q))) for p, q in zip(pts, pts[1:])))


def num_area(f, a, b, n=20000):
    fl = sp.lambdify(x, f, "math")
    a, b = float(a), float(b)
    h = (b - a) / n
    return sum(abs(fl(a + (i + 0.5) * h)) for i in range(n)) * h


# ---------------------------------------------------------------- files and blocks
les, ans = read("l6j.html"), read("a_6j.html")
teach = les.split("<!-- ============ Homework ============ -->")[0]
hw = les.split("<!-- ============ Homework ============ -->")[1].split("<!-- ============ Past papers")[0]
ppl = les.split("<!-- ============ Past papers ============ -->")[1]
CON = {}
for c in (1, 2):
    seg = teach.split(f"<!-- ============ Concept {c} ============ -->")[1].split("<!-- ============")[0]
    blocks = re.findall(r'<div class="ex (demo|attempt|worked)"[^>]*><div class="ex-top"><span class="tag">([^<]*)</span>(.*?)(?=<div class="ex |<div class="box|$)', seg, re.S)
    CON[c] = {"worked": [], "all": seg}
    for kind, tag, body in blocks:
        if kind == "worked":
            CON[c]["worked"].append((tag, body))
        else:
            CON[c][kind] = body
report([[t_ for t_, _ in CON[c]["worked"]] for c in (1, 2)] == [[], ["Worked example 38"]],
       "worked examples", "textbook Example 38 (the only example of 6J) in Concept 2")
report(all("demo" in CON[c] and "attempt" in CON[c] for c in (1, 2)), "every concept has a tutor demo and a your turn")
report(ans.count("{{ahead:Lesson 6J | Applications of integration of 1/x}}") == 1 and "Past-Paper" not in ans
       and ans.index("Lesson Examples") < ans.index("Textbook Homework"), "answers: ahead, Lesson Examples, Textbook Homework (no past-paper section)")
BLK = dict(re.findall(r'<div class="a"[^>]*><span class="an">([^<]+)</span><div class="ab">(.*?)(?=<div class="a"[^>]*><span class="an">|<div class="ans-sec">|\{\{ahead|$)', ans, re.S))

for name in sorted(set(re.findall(r"\{\{svg:([\w-]+)\}\}", les + ans))):
    report(os.path.exists(os.path.join(SRC, "svg", name + ".svg")), f"figure {name}")

# ---------------------------------------------------------------- Concept 1: tip example
try:
    tip = teach.split("Regions to the left of the \\(y\\)-axis")[1].split('<div class="ex ')[0]
    v, _ = chain(displays(tip)[0], "tip chain: integral of 1/x from -e to -1")
    report(same(v, sp.integrate(1 / x, (x, -E, -1))) and same(v, -1) and area_abs(1 / x, -E, -1) == 1
           and "is \\(1\\) square unit" in tip, "tip: integral -1, area 1 square unit")
except Exception as err:  # noqa: BLE001
    report(False, "tip", f"ERROR {err}")


def halves(block):
    a_, b_ = block.split("<b>Your turn.</b>")
    return a_, b_


# ---------------------------------------------------------------- Concept 1: demo and your turn
for who, qb, ab in (("demo", CON[1]["demo"], halves(BLK["C1"])[0]), ("your turn", CON[1]["attempt"], halves(BLK["C1"])[1])):
    try:
        k = int(grab(qb, r"Sketch \\\(y=\\dfrac(\d)x-1\\\)", f"C1 {who} curve"))
        lo, hi = grab(qb, r"the \\\(x\\\)-axis, \\\(x=(\d)\\\) and \\\(x=(\d)\\\)\.", f"C1 {who} limits")
        lo, hi = int(lo), int(hi)
        report(qb.count(f"y=\\dfrac{k}x-1") == 2, f"C1 {who} same curve in a and b")
        f = k / x - 1
        xi = int(grab(ab, r"=1\\\), so \\\(x=(\d)\\\)\.", f"C1 {who} x-intercept"))
        report(sp.solve(f, x) == [xi] and lo < xi < hi, f"C1 {who} x-intercept", f"x = {xi}")
        report("The asymptotes are \\(x=0\\) and \\(y=-1\\)" in ab and sp.limit(f, x, sp.oo) == -1, f"C1 {who} asymptotes x = 0, y = -1")
        d = displays(ab)
        v1, _ = chain(d[0], f"C1 {who} first piece")
        v2, _ = chain(d[1], f"C1 {who} second piece")
        report(same(v1, sp.integrate(f, (x, lo, xi))) and v1 > 0 and same(v2, sp.integrate(f, (x, xi, hi))) and v2 < 0,
               f"C1 {who} pieces: positive then negative", f"{v1}, {v2}")
        report(f"\\int_{lo}^{xi}" in d[0] and f"\\int_{xi}^{hi}" in d[1], f"C1 {who} limits of the pieces")
        for val in (v1, v2):
            about = f"about \\({float(val):.3f}\\)"
            report(about in ab, f"C1 {who} 'about' decimal", about)
        vt, _ = chain(d[2], f"C1 {who} total")
        A = area_abs(f, lo, hi)
        report(same(vt, A) and abs(float(A) - num_area(f, lo, hi)) < 1e-6, f"C1 {who} area = {A}", str(vt))
        unit = "square unit." if A == 1 else "square units."
        report(re.search(rf"&amp;={A}\\text{{ {unit}}}", d[2]) is not None, f"C1 {who} printed area {A} {unit}")
        logn = re.findall(r"(\d)\\log_e(\d)-\1\\log_e(\d)=\1\\log_e\\dfrac(\d)(\d)=\1\\log_e(\d)", ab)
        report(len(logn) >= 1 and all(same(sp.Integer(a1) * (sp.log(b1) - sp.log(c1)), sp.Integer(a1) * sp.log(sp.Rational(int(n1), int(d1))))
                                      and same(sp.Rational(int(n1), int(d1)), int(r1)) and int(n1) == int(b1) and int(d1) == int(c1)
                                      for a1, b1, c1, n1, d1, r1 in logn), f"C1 {who} log-law notes", str(logn))
    except Exception as err:  # noqa: BLE001
        report(False, f"C1 {who}", f"ERROR {err}")

# ---------------------------------------------------------------- Concept 2: demo, your turn, WE38
def hyperbola_line(who, qb, ab):
    k, s = grab(qb, r"hyperbola \\\(xy=(\d)\\\) meets the line \\\(x\+y=(\d)\\\)", f"{who} curves")
    k, s = int(k), int(s)
    hyp, line = k / x, s - x
    roots = sorted(sp.solve(sp.Eq(hyp, line), x))
    pts = [(r, line.subs(x, r)) for r in roots]
    printed = re.findall(r"meet at \\\(\((\d),(\d)\)\\\) and \\\(\((\d),(\d)\)\\\)", ab)
    report(len(printed) == 1 and [(int(printed[0][0]), int(printed[0][1])), (int(printed[0][2]), int(printed[0][3]))] == pts,
           f"{who} intersection points", str(pts))
    quad = sp.expand(-(x * (s - x) - k))
    report(f"x^2-{s}x+{k}" in ab.replace("\\(", "").replace("\\)", "").replace("</td><td>", "")
           and sp.factor(quad) == (x - roots[0]) * (x - roots[1]), f"{who} quadratic x^2 - {s}x + {k} and its factors")
    report(f"(x-{roots[0]})(x-{roots[1]})" in ab, f"{who} factorised form printed")
    report(f"\\(x\\)-intercept \\(({s},0)\\) and \\(y\\)-intercept \\((0,{s})\\)" in ab.replace("\\(y\\)-intercept", "\\(y\\)-intercept"),
           f"{who} intercepts of the line")
    d = [z for z in displays(ab) if "\\int" in z][0]
    v, dec = chain(TOPLINE.sub("", d), f"{who} area chain")
    A = sp.integrate(line - hyp, (x, roots[0], roots[1]))
    mid = (roots[0] + roots[1]) / 2
    report(line.subs(x, mid) > hyp.subs(x, mid) and same(v, A) and dec == f"{float(A):.3f}"
           and abs(float(A) - num_area(line - hyp, roots[0], roots[1])) < 1e-6, f"{who} area {sp.nsimplify(A)} ~ {float(A):.3f}")
    return k, s, roots, A


for who, qb, ab in (("C2 demo", CON[2]["demo"], halves(BLK["C2"])[0]), ("C2 your turn", CON[2]["attempt"], halves(BLK["C2"])[1])):
    try:
        k, s, roots, A = hyperbola_line(who, qb, ab)
        tv = grab(ab, r"at \\\(x=(\d)\\\), the line gives \\\((\d)\\\) and the hyperbola gives \\\(([^\\]*?(?:\\tfrac\d\d)?)\\\)", f"{who} test")
        xt = int(tv[0])
        report(roots[0] < xt < roots[1] and int(tv[1]) == s - xt and same(tex(tv[2]), sp.Rational(k, xt)), f"{who} test value", str(tv))
        sub = grab(ab, r"\\\(x\((\d)-x\)=(\d)\\\), &ensp;so \\\((\d)x-x\^2=(\d)\\\)", f"{who} expanded line")
        report([int(z) for z in sub] == [s, k, s, k], f"{who} expansion line")
    except Exception as err:  # noqa: BLE001
        report(False, who, f"ERROR {err}")
try:
    b38 = CON[2]["worked"][0][1]
    hyperbola_line("WE38", b38, b38)
    report("\\int_1^2(\\text{top curve}-\\text{bottom curve})\\,dx" in b38, "WE38 first line (top curve minus bottom curve)")
    report("Note:" not in b38 and "Finally" not in b38, "WE38 box holds only the textbook lines (no pack note)")
    note = grab(CON[2]["all"], r'<div class="box tip"><div class="bt">Reading Worked example 38, line by line</div>\n<p>(.*?)</p>', "WE38 tip")
    report(CON[2]["all"].index("Reading Worked example 38") > CON[2]["all"].index("Worked example 38</span>"), "WE38 tip comes after the example")
    report("\\(3x-x^2=2\\)" in note and "\\(x^2-3x+2=0\\)" in note and same(sp.expand(x * (3 - x)), 3 * x - x ** 2), "WE38 note: expansion line")
    tv = re.findall(r"at \\\(x=1\\tfrac12\\\), the line gives \\\(1\\tfrac12\\\) and the hyperbola gives \\\(1\\tfrac13\\\)", note)
    report(len(tv) == 1 and (3 - sp.Rational(3, 2)) == sp.Rational(3, 2) and 2 / sp.Rational(3, 2) == sp.Rational(4, 3), "WE38 note: test value")
    ar = re.findall(r"\\\((\d)\\times(\d)=(\d)\\\)|\\\(\\tfrac12\\times(\d)\^2=(\\tfrac12|\d)\\\)", note)
    okar = len(ar) == 4
    for a1, b1, c1, d1, e1 in ar:
        if a1:
            okar = okar and int(a1) * int(b1) == int(c1)
        else:
            okar = okar and same(sp.Rational(1, 2) * int(d1) ** 2, tex(e1))
    report(okar, "WE38 note: fourth-line arithmetic", str(ar))
    fin = grab(note, r"Finally, \\\((.*?)\\\)\.", "WE38 final decimal")
    p0, p1, p2 = fin.split("\\doteq")[0], fin.split("\\doteq")[1].split("=")[0], fin.split("=")[-1]
    report(same(tex(p0), sp.Rational(3, 2) - 2 * sp.log(2)) and p1 == f"1.5-{float(2 * sp.log(2)):.4f}" and p2 == f"{float(sp.Rational(3, 2) - 2 * sp.log(2)):.4f}",
           "WE38 note: decimal", fin)
except Exception as err:  # noqa: BLE001
    report(False, "WE38", f"ERROR {err}")

# ---------------------------------------------------------------- textbook homework: structure and text
TQ = dict(re.findall(r'<div class="q"><span class="q-num">(\d+)</span>(.*?)(?=<div class="q">|\{\{band|<p style|$)', hw, re.S))
report(sorted(TQ, key=int) == [str(i) for i in range(1, 24)], "textbook questions 1-23", str(sorted(TQ, key=int)))
bf, rest = hw.split("{{band:D}}")
bd, be = rest.split("{{band:E}}")
report(bf.count('class="q-num"') == 9 and bd.count('class="q-num"') == 8 and be.count('class="q-num"') == 6,
       "bands", "F: Q1-9, D: Q10-17, E: Q18-23 (as the textbook)")
report(set(BLK) == {"C1", "C2"} | {str(i) for i in range(1, 24) if i != 22}, "answer blocks", "C1, C2, Q1-21, Q23 (Q22 is all 'show')")


def has(n, *snips):
    body = TQ[n].replace(" ", "")
    miss = [s_ for s_ in snips if s_.replace(" ", "") not in body]
    report(not miss, f"Q{n} question text", "missing " + ", ".join(miss) if miss else ", ".join(snips)[:150])


def aparts(n):
    return dict(re.findall(r'<span class="ap6j"><b>(\w+)</b> (.*?)</span>', BLK[n], re.S))


def first(t_):
    return re.findall(r"\\\((.*?)\\\)", t_, re.S)


def exact_and_dec(lab_, exact, txt, dp=None, sf=None):
    """First math item of txt: 'A', 'A=B' or 'A\\doteq d'; every exact side must equal exact."""
    main = first(txt)[0]
    dec = None
    if "\\doteq" in main:
        main, dec = main.split("\\doteq")
    sides = T.split_top(prep(main), "=")
    ok = all(same(tex(z), exact) for z in sides)
    if dec is not None:
        if sf:
            ok = ok and float(dec) == float(f"{float(exact):.{sf}g}") and len(dec.replace(".", "").lstrip("0")) == sf
        else:
            ok = ok and dec == f"{float(exact):.{dp}f}"
    else:
        ok = ok and dp is None and sf is None or (ok and exact.is_Integer)
    report(ok, lab_, f"{first(txt)[0]}  vs  {sp.nsimplify(exact)} ~ {float(exact):.5f}")


f = 1 / x
# Q1, Q2
has("1", "\\int_1^e\\dfrac1x\\,dx=1", "The graph has been drawn", "10 little divisions to 1 unit", "100 of the little squares make 1 square unit", "x=1.0\\) to \\(1.1")
try:
    report(first(aparts("1")["b"])[0] == f"e\\doteq{float(E):.1f}" and same(sp.integrate(f, (x, 1, E)), 1), "Q1b e ~ 2.7 (the integral from 1 to e is 1)")
except Exception as err:  # noqa: BLE001
    report(False, "Q1", f"ERROR {err}")
has("2", "four significant figures", "1\\le x\\le5", "e\\le x\\le e^2", "2\\le x\\le8")
an = aparts("2")
for lt, a_, b_, sf in (("i", 1, 5, 4), ("ii", E, E ** 2, None), ("iii", 2, 8, 4)):
    try:
        exact_and_dec(f"Q2{lt}", area_abs(f, a_, b_), an[lt], sf=sf)
    except Exception as err:  # noqa: BLE001
        report(False, f"Q2{lt}", f"ERROR {err}")

# Q3 - Q9 (regions read from the descriptions; Q3 from the figures: 2..3 and 1/2..2)
an = aparts("3")
for lt, a_, b_ in (("a", 2, 3), ("b", sp.Rational(1, 2), 2)):
    try:
        exact_and_dec(f"Q3{lt}", area_abs(f, a_, b_), an[lt])
    except Exception as err:  # noqa: BLE001
        report(False, f"Q3{lt}", f"ERROR {err}")
has("4", "y=\\dfrac{1}{3x+2}", "0\\le x\\le1", "y=\\dfrac{3}{x-1}", "2\\le x\\le e^3+1", "y=\\dfrac1x+x", "x=\\tfrac12\\) to \\(x=2",
    "y=\\dfrac1x+x^2", "x=1\\) to \\(x=3")
an = aparts("4")
for lt, g, a_, b_ in (("a", 1 / (3 * x + 2), 0, 1), ("b", 3 / (x - 1), 2, E ** 3 + 1), ("c", 1 / x + x, sp.Rational(1, 2), 2), ("d", 1 / x + x ** 2, 1, 3)):
    try:
        exact_and_dec(f"Q4{lt}", area_abs(g, a_, b_), an[lt])
    except Exception as err:  # noqa: BLE001
        report(False, f"Q4{lt}", f"ERROR {err}")
has("5", "y=3-\\dfrac3x\\), the \\(x\\)-axis and \\(x=3", "y=2-\\dfrac1x\\), the \\(x\\)-axis, \\(x=1\\) and \\(x=3")
an = aparts("5")
try:
    g = 3 - 3 / x
    exact_and_dec("Q5a", area_abs(g, sp.solve(g, x)[0], 3), an["a"])
    exact_and_dec("Q5b", area_abs(2 - 1 / x, 1, 3), an["b"])
except Exception as err:  # noqa: BLE001
    report(False, "Q5", f"ERROR {err}")


def between(g1, g2):
    r = sorted(sp.solve(sp.Eq(g1, g2), x))
    return r, area_abs(g1 - g2, r[0], r[-1])


has("6", "y=2-\\dfrac2x\\) and the line \\(y=\\tfrac12(x-1)", "y=\\dfrac2x\\) and the line \\(x+2y-5=0")
an = aparts("6")
try:
    r6a, A6a = between(2 - 2 / x, (x - 1) / 2)
    r6b, A6b = between(2 / x, (5 - x) / 2)
    report(r6a == [1, 4] and r6b == [1, 4], "Q6 intersections x = 1 and 4 (as the figures)")
    exact_and_dec("Q6a", A6a, an["a"])
    exact_and_dec("Q6b", A6b, an["b"])
except Exception as err:  # noqa: BLE001
    report(False, "Q6", f"ERROR {err}")
has("7", "y=2-\\dfrac2x\\) and \\(y=2\\), and lying between \\(x=1\\) and \\(x=2", "y=\\dfrac{1}{x+2}\\), the \\(y\\)-axis and the horizontal line \\(y=1")
an = aparts("7")
try:
    exact_and_dec("Q7a", area_abs(2 - (2 - 2 / x), 1, 2), an["a"])
    xm = sp.solve(sp.Eq(1 / (x + 2), 1), x)[0]
    exact_and_dec("Q7b", area_abs(1 - 1 / (x + 2), xm, 0), an["b"])
except Exception as err:  # noqa: BLE001
    report(False, "Q7", f"ERROR {err}")
has("8", "y=-\\dfrac1x\\), the \\(x\\)-axis, \\(x=1\\) and \\(x=4", "y=\\dfrac3x-3\\), the \\(x\\)-axis and \\(x=3")
an = aparts("8")
try:
    exact_and_dec("Q8a", area_abs(-1 / x, 1, 4), an["a"])
    g = 3 / x - 3
    exact_and_dec("Q8b", area_abs(g, sp.solve(g, x)[0], 3), an["b"])
except Exception as err:  # noqa: BLE001
    report(False, "Q8", f"ERROR {err}")
has("9", "y=\\dfrac1x-1\\), the \\(x\\)-axis, \\(x=\\tfrac12\\) and", "\\(x=2\\).", "y=1-\\dfrac2x\\), the \\(x\\)-axis, \\(x=1\\) and \\(x=3")
an = aparts("9")
try:
    g = 1 / x - 1
    report(abs(float(area_abs(g, sp.Rational(1, 2), 2)) - num_area(g, 0.5, 2)) < 1e-6, "Q9a area_abs agrees with a numeric |f| sum")
    exact_and_dec("Q9a", area_abs(g, sp.Rational(1, 2), 2), an["a"])
    exact_and_dec("Q9b", area_abs(1 - 2 / x, 1, 3), an["b"])
except Exception as err:  # noqa: BLE001
    report(False, "Q9", f"ERROR {err}")

# Q10 - Q13
try:
    has("10", "bounded by \\(y=1\\), \\(x=8\\) and the curve \\(y=\\dfrac4x")
    xm = sp.solve(sp.Eq(4 / x, 1), x)[0]
    A10 = area_abs(1 - 4 / x, xm, 8)
    exact_and_dec("Q10b (the key prints 4 - log 2: a slip)", A10, aparts("10")["b"])
    report(abs(float(A10) - num_area(1 - 4 / x, 4, 8)) < 1e-6, "Q10 numeric check", f"{float(A10):.4f}")
    has("11", "y=\\dfrac1x\\) with the line \\(y=4-3x")
    r11 = sorted(sp.solve(sp.Eq(1 / x, 4 - 3 * x), x))
    an = aparts("11")
    pts = first(an["a"])
    report([tex(z.strip("()").split(",")[0].replace("\\big(", "").replace("\\big)", "")) for z in pts] == r11
           and [tex(z.replace("\\big(", "").replace("\\big)", "").strip("()").split(",")[1]) for z in pts] == [1 / r for r in r11], "Q11a points", str(pts))
    exact_and_dec("Q11b", area_abs(4 - 3 * x - 1 / x, r11[0], r11[1]), an["b"])
    has("12", "Differentiate \\(x^2+1\\)", "y=\\dfrac{x}{x^2+1}\\), between \\(x=0\\) and \\(x=2", "Differentiate \\(x^2+2x+3\\)",
        "y=\\dfrac{x+1}{x^2+2x+3}\\), between \\(x=0\\) and \\(x=1")
    an = aparts("12")
    da, ea = first(an["a"])[:2]
    report(same(tex(da), sp.diff(x ** 2 + 1, x)), "Q12a derivative", da)
    exact_and_dec("Q12a area", area_abs(x / (x ** 2 + 1), 0, 2), "\\(" + ea.replace(" u\\(^2", "") + "\\)", dp=3)
    db, eb = first(an["b"])[:2]
    report(same(tex(db), sp.diff(x ** 2 + 2 * x + 3, x)), "Q12b derivative", db)
    exact_and_dec("Q12b area", area_abs((x + 1) / (x ** 2 + 2 * x + 3), 0, 1), "\\(" + eb + "\\)")
    has("13", "the \\(x\\)-axis, \\(y=x\\), \\(y=\\dfrac1x\\) and \\(x=e")
    A13 = sp.integrate(sp.Min(x, 1 / x), (x, 0, 1)) + sp.integrate(1 / x, (x, 1, E))
    report(sp.solve(sp.Eq(x, 1 / x), x) == [-1, 1], "Q13 y = x meets y = 1/x at x = 1 in the first quadrant")
    exact_and_dec("Q13b", sp.integrate(x, (x, 0, 1)) + sp.integrate(1 / x, (x, 1, E)), aparts("13")["b"])
    report(same(A13, sp.Rational(3, 2)), "Q13 area by min(x, 1/x)")
except Exception as err:  # noqa: BLE001
    report(False, "Q10-Q13", f"ERROR {err}")

# Q14 - Q17
try:
    has("14", "four subintervals", "y=\\ln x\\) and the \\(x\\)-axis, between \\(x=1\\) and \\(x=5", "Differentiate \\(y=x\\log_ex")
    an = aparts("14")
    trap = sp.Rational(1, 2) * (sp.log(1) + 2 * (sp.log(2) + sp.log(3) + sp.log(4)) + sp.log(5))
    report(first(an["a"])[0] == f"{float(trap):.4f}", "Q14a trapezoidal, h = 1", first(an["a"])[0])
    d14, a14 = first(an["b"])[0], first(an["b"])[1]
    report(same(tex(d14.split("=")[1]), sp.diff(x * sp.log(x), x)), "Q14b derivative", d14)
    exact_and_dec("Q14b area", sp.integrate(sp.log(x), (x, 1, 5)), "\\(" + a14.split("=", 1)[1] + "\\)", dp=4)
    report(float(trap) < float(sp.integrate(sp.log(x), (x, 1, 5))) and sp.diff(sp.log(x), x, 2).subs(x, 2) < 0
           and "less" in an["c"] and "concave down" in an["c"] and "below the curve" in an["c"], "Q14c less, concave down")
    has("15", "4x=2(2x+1)-2", "y=\\dfrac{4x}{2x+1}\\) between \\(x=0\\) and \\(x=1")
    report(same(4 * x, 2 * (2 * x + 1) - 2), "Q15a identity")
    exact_and_dec("Q15b", area_abs(4 * x / (2 * x + 1), 0, 1), aparts("15")["b"])
    has("16", "y=\\dfrac6x\\) and \\(y=x^2-6x+11\\) intersect when \\(x=1\\), \\(2\\) and \\(3")
    r16 = sorted(sp.solve(sp.Eq(6 / x, x ** 2 - 6 * x + 11), x))
    report(r16 == [1, 2, 3], "Q16a intersections 1, 2, 3")
    exact_and_dec("Q16c", area_abs(x ** 2 - 6 * x + 11 - 6 / x, 1, 3), aparts("16")["c"])
    has("17", "\\tfrac12\\lt\\displaystyle\\int_{2^n}^{2^{n+1}}\\dfrac1x\\,dx\\lt1", "n\\ge0")
    a17 = aparts("17")["a"]
    h_up, h_lo, wd = first(a17)[0], first(a17)[1], first(a17)[2]
    W = 2 ** (nn + 1) - 2 ** nn
    report(h_up == "2^{-n}" and h_lo == "2^{-n-1}" and same(tex(wd.split("=")[1].replace("n", "(N)").replace("(N)", "n"), {"n": nn}), W)
           and sp.simplify(W - 2 ** nn) == 0 and sp.simplify(W * 2 ** (-nn)) == 1 and sp.simplify(W * 2 ** (-nn - 1)) == sp.Rational(1, 2)
           and same(sp.integrate(1 / x, (x, 2 ** nn, 2 ** (nn + 1))), sp.log(2)), "Q17a rectangles: areas 1 and 1/2 (exact value log 2)", f"{h_up}, {h_lo}, {wd}")
except Exception as err:  # noqa: BLE001
    report(False, "Q14-Q17", f"ERROR {err}")

# Q18 - Q23
try:
    has("18", "y=6e^{-x}\\) and \\(y=e^x-1", "u^2-u-6=0", "bounded by them and the \\(y\\)-axis")
    u = sp.Symbol("u", positive=True)
    report(sp.expand(sp.expand((6 / u - (u - 1)) * -u)) == u ** 2 - u - 6, "Q18a quadratic in u")
    xi = sp.solve(sp.Eq(6 * sp.exp(-x), sp.exp(x) - 1), x)
    xi = [r for r in xi if r.is_real][0]
    an = aparts("18")
    pb = first(an["b"])[0].replace("\\,", "")
    pxy = re.match(r"\((.*),(.*)\)", pb)
    report(same(tex(pxy.group(1)), xi) and same(tex(pxy.group(2)), 6 * sp.exp(-xi)), "Q18b point (log 3, 2)", pb)
    exact_and_dec("Q18d", area_abs(6 * sp.exp(-x) - (sp.exp(x) - 1), 0, xi), an["d"])
    has("19", "y=\\dfrac1x+1\\) meets the \\(x\\)-axis at \\((-1,0)", "a</span>\\(x=-e\\) to \\(x=-1\\)", "b</span>\\(x=-1\\) to \\(x=-e^{-1}\\)", "c</span>\\(x=-e\\) to \\(x=-e^{-1}\\)")
    an = aparts("19")
    g = 1 / x + 1
    for lt, a_, b_ in (("a", -E, -1), ("b", -1, -1 / E), ("c", -E, -1 / E)):
        exact_and_dec(f"Q19{lt}", area_abs(g, a_, b_), an[lt])
        report(abs(float(area_abs(g, a_, b_)) - num_area(g, a_, b_)) < 1e-6, f"Q19{lt} numeric")
    has("20", "\\dfrac{1}{x+\\sqrt x}")
    p20 = tex(first(BLK["20"])[0])
    report(sp.simplify(sp.diff(p20, x) - 1 / (x + sp.sqrt(x))).subs(x, sp.Symbol("w", positive=True)) == 0
           or all(abs(float((sp.diff(p20, x) - 1 / (x + sp.sqrt(x))).subs(x, v_))) < 1e-12 for v_ in (0.3, 1.7, 5)), "Q20 primitive differentiates back", str(p20))
    has("21", "\\int_0^1\\dfrac{1}{\\sqrt{x^2+1}}\\,dx", "\\int_4^8\\dfrac{1}{\\sqrt{x^2-16}}\\,dx")
    aa = sp.Symbol("a", positive=True)
    xp = sp.Symbol("xp", positive=True)
    report(same(sp.diff(sp.log(x + sp.sqrt(x ** 2 + aa ** 2)), x), 1 / sp.sqrt(x ** 2 + aa ** 2))
           and sp.simplify(sp.diff(sp.log(xp + sp.sqrt(xp ** 2 - aa ** 2)), xp) - 1 / sp.sqrt(xp ** 2 - aa ** 2)) == 0, "Q21a derivatives (question)")
    i21 = re.findall(r"<b>i+</b> \\\((.*?)\\\)</span>", BLK["21"])
    report(len(i21) == 2 and same(tex(i21[0]), sp.log(1 + sp.sqrt(2))) and same(tex(i21[1]), sp.log(8 + sp.sqrt(48)) - sp.log(4))
           and abs(float(tex(i21[0])) - float(sp.Integral(1 / sp.sqrt(x ** 2 + 1), (x, 0, 1)).evalf())) < 1e-12
           and abs(float(tex(i21[1])) - float(sp.Integral(1 / sp.sqrt(x ** 2 - 16), (x, 4, 8)).evalf())) < 1e-9, "Q21b i, ii", str(i21))
    has("22", "\\dfrac{1}{n+1}\\lt\\displaystyle\\int_n^{n+1}\\dfrac1x\\,dx\\lt\\dfrac1n", "\\lim_{n\\to\\infty}\\big(1+\\tfrac1n\\big)^n=e",
        "\\lim_{n\\to\\infty}\\big(1+\\tfrac tn\\big)^n=e^t")
    has("23", "\\int_1^{\\sqrt x}\\dfrac1t\\,dt", "\\text{area }ABCO", "0\\lt\\dfrac{\\log_ex}{x}\\lt\\dfrac{2}{\\sqrt x}",
        "\\lim_{x\\to0^+}x\\log_ex=0", "\\lim_{x\\to-\\infty}xe^x=0", "\\lim_{x\\to\\infty}xe^{-x}=0")
    d23 = aligned_chain(displays(BLK["23"])[0])
    rows = [r for r in d23.split("0\\lt") if r.strip()]
    X = sp.Symbol("X", positive=True)
    mids = []
    for r in rows:
        mid = r.split("\\lt")[0]
        mid = re.sub(r"\\Big\[\\log_et\\Big\]_1\^\{\\sqrt x\}", r"(\\log_e\\sqrt{x}-\\log_e1)", mid)
        mids.append(tex(mid).subs(x, X))
    rights = [tex(r.split("\\lt")[1]).subs(x, X) for r in rows]
    report(len(rows) == 4 and same(mids[0], sp.integrate(1 / t, (t, 1, sp.sqrt(X)))) and same(mids[1], mids[0]) and same(mids[2], mids[0])
           and same(mids[3], mids[2] * 2 / X) and all(same(rights[i], sp.sqrt(X)) for i in range(3)) and same(rights[3], rights[2] * 2 / X),
           "Q23a ii every line (x 2/x on both sides)", f"{len(rows)} rows")
    report(sp.limit(2 / sp.sqrt(X), X, sp.oo) == 0 and "sandwiching" in BLK["23"], "Q23a iii sandwich: 2/sqrt x -> 0")
except Exception as err:  # noqa: BLE001
    report(False, "Q18-Q23", f"ERROR {err}")

# ---------------------------------------------------------------- generic: every remaining printed chain in the answers
cnt = 0
for disp in displays(ans):
    if ("\\int_" in disp or "\\Big[" in disp) and "aligned" in disp and "\\lt" not in disp:
        cnt += 1
        chain(TOPLINE.sub("", disp), f"answers chain {cnt}")
report(cnt == 6, "answers: six worked chains found", str(cnt))

# ---------------------------------------------------------------- timed-practice note (no past-paper question exists)
try:
    report('<div class="pp"' not in ppl and "Past-paper homework:timed practice" in ppl, "no past-paper block; timed-practice section")
    note = grab(ppl, r"have no question that first needs this lesson: (.*?)For timed practice, do Exercise 6J Questions (.*?) above in (\d+) minutes\.", "practice note")
    refs = re.findall(r"(\d+)(?:\((\w)\))?", note[1])
    ok = refs and all(n in TQ and (not lt or f'<span class="pl">{lt}</span>' in TQ[n]) for n, lt in refs)
    report(bool(ok) and [n for n, _ in refs] == ["6", "9", "11", "16"], "timed-practice references exist", note[1])
    with open(os.path.join(HERE, "..", "..", "docs", "pp_candidates_integration.md"), encoding="utf-8") as fh:
        cat = fh.read()
    rows = re.findall(r"^\| [\d.]+-\d+ \| int2-L4 \|", cat, re.M)
    report(not rows and "| int2-L4 | 6J Applications of integration of 1/x | 0 | 0 | 0 | **0** | 0 | 0 |" in cat,
           "catalogue: no row tagged int2-L4 (the note's claim)")
except Exception as err:  # noqa: BLE001
    report(False, "timed-practice note", f"ERROR {err}")

print(f"\n{CNT[0]} checks, {len(FAILS)} failures")
sys.exit(1 if FAILS else 0)
