r"""Check of Lesson 5D (Integration Part 1 pack): Proving the fundamental theorem.

The script reads the values PRINTED in workspace/build/int1/l5d.html and a_5d.html and recomputes them
independently. Blocks are found by their data-c attribute or by fixed markers; each must be found exactly
once, otherwise the item FAILS. Printed TeX is turned into sympy with workspace/checks/int3_tex.py.
  - signed area tables and their working lines (Example 13, C1 demo and your turn): every member of every
    printed chain A(k)=...=v is compared with sympy.integrate of the piecewise-linear f read off the
    textbook-style graph (f = c for t < 0, c - m t for t >= 0);
  - differential form (Example 14, C2, Ex 4, Ex 6a): the printed result must equal the printed integrand
    with t -> x, and is also compared numerically with a finite difference of mpmath.quad of the integrand;
  - integral form (Example 15, C3, Ex 5, Ex 6b): every member of every printed chain is evaluated
    (integrals with sympy.integrate, [F]_a^x brackets, d/dx(...) with sympy.diff) and must equal the
    integral (first chain) or the integrand at x (the 'so' chain); each printed primitive is differentiated;
  - Ex 1, Ex 2: the line through the points printed on each graph, the area chains, A'(x);
  - Ex 3, Ex 7, Ex 9: the printed behaviour statements are recomputed from the signs of f and f' (models
    of the sketched graphs for 3 and 9; exact f for 7);
  - Ex 8: the tables and chains against sympy.integrate of cos and sin;
  - C4, Ex 10: continuity classifications and domains from sympy.calculus.util (function_domain,
    continuous_domain) and one-sided limits at the special point;
  - the textbook's printed answers (Ext 1 Y12 PDF 890-891) are transcribed below and compared (two key
    slips are recorded and our printed answer is checked to be the correct one);
  - the timed-practice note names questions and parts that exist.

Exit status 1 if anything fails. Run: python3 workspace/checks/int1_5d.py
"""
import os
import re
import sys

import mpmath
import sympy as sp
from sympy.calculus.util import continuous_domain

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from int3_tex import tex as _tex, split_top  # noqa: E402

SRC = os.environ.get("INT1_SRC", os.path.join(HERE, "..", "build", "int1"))
FAILS, NCHECK = [], [0]
x = sp.Symbol("x", real=True)
t = sp.Symbol("t", real=True)


def read(name):
    with open(os.path.join(SRC, name), encoding="utf-8") as fh:
        return fh.read().replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")


def report(ok, label, detail=""):
    NCHECK[0] += 1
    print(("OK       " if ok else "MISMATCH ") + label.replace("\n", " ")[:100]
          + ("  " + detail.replace("\n", " ")[:170] if detail else ""))
    if not ok:
        FAILS.append(label)


def T(s):
    """Printed TeX -> sympy (x and t as real symbols)."""
    s = s.strip().rstrip(".,;:").strip()
    s = re.sub(r"\\(?:displaystyle|left|right|quad|qquad)", "", s)
    s = s.replace("\\lt", "<").replace("\\gt", ">")
    s = re.sub(r"\\sqrt\s*([A-Za-z0-9])", r"\\sqrt{\1}", s)
    return _tex(s, {"x": x, "t": t})


def eq(a, b):
    try:
        return sp.simplify(sp.sympify(a) - sp.sympify(b)) == 0
    except Exception:
        return False


def block(text, key):
    """The element carrying data-c="key" (its inner HTML up to the matching close tag)."""
    m = list(re.finditer(r'<(\w+)[^>]*data-c="' + re.escape(key) + r'"[^>]*>', text))
    if len(m) != 1:
        raise LookupError(f'data-c="{key}" found {len(m)} times')
    tag, i, depth = m[0].group(1), m[0].end(), 1
    for mm in re.finditer(r"<(/?)" + tag + r"\b[^>]*>", text[i:]):
        depth += -1 if mm.group(1) else 1
        if depth == 0:
            return text[i:i + mm.start()]
    raise LookupError(f"unclosed {key}")


def maths(text):
    return re.findall(r"\\\((.*?)\\\)", text, re.S)


def displays(text):
    return re.findall(r"\\\[(.*?)\\\]", text, re.S)


def lettered(text):
    bits = re.split(r"<b>([a-p])</b>", text)
    return {bits[i]: bits[i + 1] for i in range(1, len(bits), 2)}


les = read("l5d.html")
ans = read("a_5d.html")
for need in ("<!-- ============ Homework ============ -->", "<!-- ============ Past papers ============ -->"):
    if les.count(need) != 1:
        sys.exit(f"FAIL: {need} not found once in l5d.html")
teach, rest = les.split("<!-- ============ Homework ============ -->")
hw, ppl = rest.split("<!-- ============ Past papers ============ -->")

# ---------------------------------------------------------------- structure
CON = {}
for c in range(1, 5):
    seg = teach.split(f"<!-- ============ Concept {c} ============ -->")[1].split("<!-- ============")[0]
    exs = re.findall(r'<div class="ex (demo|attempt|worked)"(?: style="[^"]*")?><div class="ex-top"><span class="tag">([^<]*)</span>(.*?)(?=<div class="ex |$)', seg, re.S)
    CON[c] = {kind: body for kind, _, body in exs}
    CON[c]["tags"] = [tg for _, tg, _ in exs]
    report([kd for kd, _, _ in exs] == (["demo", "attempt"] if c == 4 else ["demo", "attempt", "worked"]),
           f"Concept {c} blocks", str([kd for kd, _, _ in exs]))
for c, name in ((1, "Worked example 13"), (2, "Worked example 14"), (3, "Worked example 15")):
    report(CON[c]["tags"][-1] == name, f"Concept {c} worked example is the textbook's {name}", str(CON[c]["tags"]))
for box in ("13 The signed area function", "The fundamental theorem: differential form",
            "The fundamental theorem: integral form"):
    report(teach.count(f'<div class="bt">{box}</div>') == 1, f"box printed once: {box}")
TQ = dict(re.findall(r'<div class="q"><span class="q-num">(\d+)</span>(.*?)(?=<div class="q"><span class="q-num">|\{\{band|$)', hw, re.S))
report(sorted(TQ, key=int) == [str(i) for i in range(1, 11)], "textbook questions 1-10", str(sorted(TQ, key=int)))
fb, db_ = hw.split("{{band:D}}")
db, eb = db_.split("{{band:E}}")
report(hw.count("{{band:F}}") == 1 and fb.count('class="q-num"') == 2 and db.count('class="q-num"') == 5
       and eb.count('class="q-num"') == 3, "bands", "F: Q1-2, D: Q3-7, E: Q8-10 (as the textbook)")
secs = ans.split('<div class="ans-sec">')
report(len(secs) == 3 and secs[1].startswith("Lesson Examples") and secs[2].startswith("Textbook Homework"),
       "answer sections", "Lesson Examples, Textbook Homework (no past-paper section: none selected)")
report("pp-src" not in les and "pp-src" not in ans and "{{sec:amber:clock:Past-paper homework:timed practice}}" in ppl,
       "no past-paper questions; timed-practice heading present")
BLK = dict(re.findall(r'<div class="a"(?: style="[^"]*")?><span class="an">([^<]+)</span><div class="ab"[^>]*>(.*?)(?=<div class="a"(?: style="[^"]*")?><span class="an">|<div class="ans-sec">|$)', ans, re.S))
report(sorted(BLK) == sorted(["C1", "C2", "C3", "C4"] + [str(i) for i in range(1, 11)]), "answer blocks", str(sorted(BLK)))


# ---------------------------------------------------------------- Concept 1: signed area tables
def step(c, m):
    return sp.Piecewise((c, t < 0), (c - m * t, True))


def A_of(f, k, lower=0):
    return sp.integrate(f, (t, lower, k))


def table(html, key, f, xs_expected, where):
    try:
        tb = block(html, key)
    except LookupError as err:
        report(False, where, f"ERROR {err}")
        return
    rows = re.findall(r"<tr>(.*?)</tr>", tb, re.S)
    xs = [T(v) for v in maths(rows[0])[1:]]
    vs = [T(v) for v in maths(rows[1])[1:]]
    report(xs == xs_expected, f"{where} x row", str(xs))
    for k, v in zip(xs, vs):
        a = A_of(f, k)
        report(eq(v, a), f"{where} A({k})", f"printed {v}, integral {a}")


def chains_A(html, key, f, where, arg=lambda s: T(s)):
    """Every inline chain 'A(k)=...=v' in the block: every member equals the integral from 0 to k."""
    try:
        tb = block(html, key)
    except LookupError as err:
        report(False, where, f"ERROR {err}")
        return
    used = 0
    for m in maths(tb):
        mm = re.match(r"A(\\big\(|\()(.+?)(\\big\)|\))=(.*)$", m.strip(), re.S)
        if not mm:
            continue
        k = arg(mm.group(2))
        a = A_of(f, k)
        for mem in split_top(mm.group(4)):
            used += 1
            report(eq(T(mem), a), f"{where} A({k}) member {mem[:40]}", f"integral {a}")
    report(used >= 5, f"{where}: chain members checked", str(used))


f13, fd1, fy1 = step(2, 2), step(4, 2), step(1, 1)
table(CON[1]["worked"], "we13", f13, [-3, -2, -1, 0, 1, 2, 3], "WE13 table")
chains_A(CON[1]["worked"], "we13w", f13, "WE13 working")
table(BLK["C1"], "d1t", fd1, [-2, -1, 0, 1, 2, 3, 4], "C1 demo table")
chains_A(BLK["C1"], "d1w", fd1, "C1 demo working")
table(BLK["C1"], "y1t", fy1, [-3, -2, -1, 0, 1, 2, 3], "C1 your-turn table")
chains_A(BLK["C1"], "y1w", fy1, "C1 your-turn working")
report("[-2,4]" in CON[1]["demo"] and "[-3,3]" in CON[1]["attempt"] and "[-3,3]" in CON[1]["worked"],
       "C1 intervals in the questions")
# increasing / decreasing statements: f changes sign at its zero
for txt, f, where in ((CON[1]["worked"], f13, "WE13"), (BLK["C1"].split("Your turn")[0], fd1, "C1 demo"),
                      (BLK["C1"].split("Your turn")[1], fy1, "C1 your turn")):
    z = sp.solve(sp.Eq(f.args[1][0], 0), t)[0]
    ok = re.search(r"increasing for \\\((?:t|x)\\lt" + str(z) + r"\\\)", txt) and re.search(r"decreasing for \\\(x\\gt" + str(z) + r"\\\)", txt)
    report(bool(ok), f"{where}: increasing for x < {z}, decreasing for x > {z}")
# the graph descriptions printed in the answers: heights of the line
for txt, f, pts in ((BLK["C1"].split("Your turn")[0], fd1, ((1, 2), (3, -2), (4, -4))),
                    (BLK["C1"].split("Your turn")[1], fy1, ((2, -1), (3, -2)))):
    for k, h in pts:
        report(f.subs(t, k) == h, f"C1 line height {h} at t={k}")
report(r"\(-4\) when \(t=3\)" in CON[1]["worked"] and r"height \(-2\) when \(t=2\)" in CON[1]["worked"]
       and f13.subs(t, 2) == -2 and f13.subs(t, 3) == -4, "WE13 line heights at t=2, 3")


# ---------------------------------------------------------------- differential form
def num_ftc(f, a, x0):
    g = sp.lambdify(t, f, "mpmath")
    F = lambda X: mpmath.quad(g, [a, X])  # noqa: E731
    return mpmath.diff(F, x0)


INTX = r"\\frac\{d\}\{dx\}\\int_(\{[^}]*\}|-?\w)\^x\s*(.+?)\\,dt"


def diff_form(chunk, where, x0=1.7):
    """Every 'd/dx \\int_a^x f dt = r' in chunk: r = f(x), and a numerical FTC check at x0."""
    n = 0
    for m in maths(chunk):
        mm = re.match(r"\s*(?:\\displaystyle)?" + INTX + r"\s*=(.+)$", m.strip(), re.S)
        if not mm:
            continue
        a, f, r = T(mm.group(1).strip("{}")), T(mm.group(2)), T(mm.group(3))
        n += 1
        report(eq(r, f.subs(t, x)), f"{where} d/dx int_{a}^x {mm.group(2)[:30]}", f"printed {r}")
        val = num_ftc(f, a, x0)
        report(abs(complex(val) - complex(r.subs(x, x0))) < 1e-6, f"{where} numeric FTC at x={x0}", f"{val}")
    return n


def q_integrals(chunk):
    return [(T(a.strip("{}")), T(f)) for a, f in re.findall(INTX, chunk) if f.strip() != "f(t)"]


we14 = block(CON[2]["worked"], "we14")
report(diff_form(we14, "WE14") == 3, "WE14 three parts checked")
for i, key, kind in (("d2", "d2", "demo"), ("y2", "y2", "attempt")):
    b = block(BLK["C2"], key)
    report(diff_form(b, f"C2 {key}") == 3, f"C2 {key} three parts checked")
    report(q_integrals(CON[2][kind]) == q_integrals(b), f"C2 {key}: answer integrals match the lesson parts")
    for m in re.findall(r"\\\(f\(t\)=(.+?)\\\)", b):
        report(any(eq(T(m), fq) for _, fq in q_integrals(b)), f"C2 {key}: f(t) = {m[:30]} is an integrand")
report(q_integrals(CON[2]["worked"].split("Solution")[0]) == q_integrals(we14), "WE14 solution matches the question")


# ---------------------------------------------------------------- integral form chains
def ev(mem):
    """Evaluate one printed member of a chain (TeX)."""
    s = mem.strip()
    s = re.sub(r"\\(?:qquad|quad)\s*\\text\{[^}]*\}", "", s)
    s = re.sub(r"^\\text\{so\}\s*\\quad", "", s).strip().rstrip(",.").strip()
    s = s.replace("\\displaystyle", "")
    m = re.fullmatch(r"\\frac\{d\}\{dx\}(.*)", s, re.S)
    if m:
        inner = m.group(1).strip()
        if inner.startswith("\\int"):
            return sp.diff(ev(inner), x)
        inner = re.sub(r"^\\(?:big|Big)\((.*)\\(?:big|Big)\)$", r"(\1)", inner, flags=re.S)
        return sp.diff(T(inner), x)
    m = re.fullmatch(r"\\int_(\{[^}]*\}|-?\w)\^(\{[^}]*\}|\w)\s*(.+?)\\,dt", s, re.S)
    if m:
        return sp.integrate(T(m.group(3)), (t, T(m.group(1).strip("{}")), T(m.group(2).strip("{}"))))
    m = re.fullmatch(r"\\Big\[(.*?)\\Big\]_(\{[^}]*\}|-?\w)\^(\w)", s, re.S)
    if m:
        F = T(m.group(1))
        return F.subs(t, T(m.group(3))) - F.subs(t, T(m.group(2).strip("{}")))
    return T(s)


def chain_members(disp):
    """Members of a display: aligned rows joined, '&' removed, rows that are only text skipped."""
    d = disp.replace("\\begin{aligned}", "").replace("\\end{aligned}", "")
    rows = [r.replace("&", "") for r in d.split("\\\\")]
    rows = [r for r in rows if re.sub(r"\\(?:qquad|quad)|\\text\{[^}]*\}|\s", "", r)]
    joined = "".join(r if r.lstrip().startswith("=") or i == 0 else "=" + r for i, r in enumerate(rows))
    return [m for m in split_top(joined) if m.strip()]


def int_form(b, a, f, where):
    """b: an answer chunk. First display chain = integral; later chains (display or inline) = f(x)."""
    I = sp.integrate(f, (t, a, x))
    ds = displays(b)
    used = 0
    for i, d in enumerate(ds):
        target = I if i == 0 else f.subs(t, x)
        for mem in chain_members(d):
            try:
                v = ev(mem)
            except Exception as err:
                report(False, f"{where} member {mem[:40]}", f"ERROR {err}")
                continue
            used += 1
            report(eq(v, target), f"{where} chain {i} member {mem.strip()[:45]}", f"= {sp.simplify(v)}; expected {sp.simplify(target)}")
    for m in maths(b):              # inline 'd/dx( ... ) = ...' chains
        if m.lstrip().startswith("\\dfrac{d}{dx}") or m.lstrip().startswith("\\frac{d}{dx}"):
            for mem in split_top(m.replace("\\dfrac{d}{dx}", "\\frac{d}{dx}")):
                used += 1
                report(eq(ev(mem), f.subs(t, x)), f"{where} inline member {mem[:45]}", f"expected {f.subs(t, x)}")
    # primitives: 'The primitive of P is Q=R' and 'Write P=Q. Its primitive is R=S.'
    for p, q in re.findall(r"primitive of \\\((.+?)\\\) is \\\((.+?)\\\)", b):
        for mem in split_top(q):
            report(eq(sp.diff(T(mem), t), T(p)), f"{where} primitive member {mem[:40]}", f"of {p}")
    for w, q in re.findall(r"Write \\\((.+?)\\\)\. Its primitive is \\\((.+?)\\\)", b):
        w1, w2 = split_top(w)
        report(eq(T(w1), T(w2)), f"{where} rewrite {w}")
        for mem in split_top(q):
            report(eq(sp.diff(T(mem), t), T(w2)), f"{where} primitive member {mem[:40]}", f"of {w2}")
    report(used >= 4, f"{where}: members checked", str(used))


QW15 = q_integrals(CON[3]["worked"].split("Solution")[0])
QD3, QY3 = q_integrals(CON[3]["demo"]), q_integrals(CON[3]["attempt"])
report(len(QW15) == 3 and len(QD3) == 3 and len(QY3) == 3, "C3 question parts read", f"{QW15} {QD3} {QY3}")
for qs, html, keys, where in ((QW15, CON[3]["worked"], ("we15a", "we15b", "we15c"), "WE15"),
                              (QD3, BLK["C3"], ("d3a", "d3b", "d3c"), "C3 demo"),
                              (QY3, BLK["C3"], ("y3a", "y3b", "y3c"), "C3 your turn")):
    for (a, f), key in zip(qs, keys):
        try:
            int_form(block(html, key), a, f, f"{where} {key}")
        except LookupError as err:
            report(False, f"{where} {key}", f"ERROR {err}")

# ---------------------------------------------------------------- Concept 4 and Ex 10: continuity
INF = sp.oo


def function_domain(expr):
    """Natural domain: remove zeros of denominators, keep radicands >= 0."""
    dom = sp.S.Reals
    for pw in expr.atoms(sp.Pow):
        b, e = pw.as_base_exp()
        if e.is_negative:
            dom -= sp.solveset(sp.Eq(b, 0), x, sp.S.Reals)
        if not e.is_integer:
            dom = dom.intersect(sp.solveset(b >= 0, x, sp.S.Reals))
    return dom


def classify(expr, special=None):
    """(domain, is a continuous function) for expr, optionally redefined as 0 at x = special."""
    dom = function_domain(expr)
    cont = continuous_domain(expr, x, sp.S.Reals)
    ok = (dom == cont)
    if special is not None:
        dom = dom.union(sp.FiniteSet(special))
        sides = []
        for d in ("+", "-"):
            probe = special + (sp.Rational(1, 10**6) if d == "+" else -sp.Rational(1, 10**6))
            if probe in dom:
                sides.append(sp.limit(expr, x, special, d))
        ok = ok and all(s == 0 for s in sides)
    return dom, ok


def dom_tex(d):
    m = re.search(r"The domain is \\\((.+?)\\\)", d)
    if m:
        s = m.group(1).replace("\\ne", "!=").replace("\\ge", ">=").replace("\\gt", ">")
        mm = re.fullmatch(r"x(!=|>=|>)(.+)", s)
        v = T(mm.group(2))
        return {"!=": sp.Reals - sp.FiniteSet(v), ">=": sp.Interval(v, INF), ">": sp.Interval.open(v, INF)}[mm.group(1)]
    if "all real" in d or "every real number" in d:
        return sp.Reals
    m = re.search(r"Now \\\((.+?)\\\) lies in the domain", d)
    return ("contains", T(m.group(1))) if m else None


C4FUN = {"d4": {"a": (x**2 + 1, None), "b": (1 / (x + 3), None), "c": (1 / (x + 3), -3), "d": (sp.sqrt(x + 3), None)},
         "y4": {"a": (3 - x, None), "b": (1 / x**2, None), "c": (1 / x**2, 0), "d": (1 / sp.sqrt(x + 1), None)},
         "q10": {"a": (x - 2, None), "b": (1 / (x - 2), None), "c": (1 / (x - 2), 2), "d": (sp.sqrt(x), None),
                 "e": (1 / sp.sqrt(x), None), "f": (1 / sp.sqrt(x), 0)}}
for key, funcs in C4FUN.items():
    b = lettered(block(ans, key) if key != "q10" else BLK["10"])
    for L, (expr, sp_) in funcs.items():
        dom, ok = classify(expr, sp_)
        d = b.get(L, "")
        printed_ok = ("so it is a continuous function" in d) and ("not a continuous" not in d)
        printed_not = "so it is not a continuous function" in d
        report(printed_ok == ok and printed_not == (not ok), f"{key} {L}: {'continuous' if ok else 'not continuous'}")
        pd = dom_tex(d)
        if isinstance(pd, tuple):
            report(pd[1] in dom and pd[1] == sp_, f"{key} {L}: {pd[1]} lies in the domain")
        elif pd is not None:
            report(pd == dom, f"{key} {L}: domain", f"printed {pd}, sympy {dom}")
        else:
            report(False, f"{key} {L}: no domain statement found")
# the lesson's C4 functions are the ones checked
for kind, key in (("demo", "d4"), ("attempt", "y4")):
    printed = [T(m.split("=", 1)[1]) for m in maths(CON[4][kind]) if m.startswith("y=") and "cases" not in m]
    want = [e for L, (e, s) in C4FUN[key].items() if s is None]
    report(len(printed) == 3 and all(eq(p, w) for p, w in zip(printed, want)), f"C4 {kind} functions", str(printed))
q10fs = [T(m.split("=", 1)[1]) for m in maths(TQ["10"]) if m.startswith("y=") and "cases" not in m]
report(len(q10fs) == 4 and all(eq(p, w) for p, w in zip(q10fs, [x - 2, 1 / (x - 2), sp.sqrt(x), 1 / sp.sqrt(x)])),
       "Ex 10 functions a, b, d, e", str(q10fs))

# ---------------------------------------------------------------- Ex 1 and Ex 2
q1 = block(ans, "q1")
for m in maths(q1):
    if m.startswith("A(x)="):
        for mem in split_top(m)[1:]:
            report(eq(T(mem), sp.integrate(3 * t, (t, 0, x))), f"Q1 A member {mem}")
    if m.startswith("A'(x)="):
        for mem in split_top(m)[1:]:
            report(eq(T(mem), 3 * x), f"Q1 A' member {mem}")
report(r"\(y=3t\), for \(0\le t\le3\)" in TQ["1"], "Q1 stem y = 3t on [0, 3]")

# graphs of Q2: the points marked on each textbook graph (value at t = 0, value at t = 4)
Q2PTS = {"a": (3, 3), "b": (0, 8), "c": (2, 6), "d": (5, 1)}
for L, (y0, y4) in Q2PTS.items():
    svg = open(os.path.join(SRC, "svg", f"q5d_2{L}.svg"), encoding="utf-8").read()
    labels = re.findall(r">([0-9])</text>", svg)
    report(str(y4) in labels and (y0 == 0 or str(y0) in labels), f"Q2{L} graph shows the printed values {y0}, {y4}", str(labels))
q2 = lettered(block(ans, "q2"))
for L, (y0, y4) in Q2PTS.items():
    f = y0 + sp.Rational(y4 - y0, 4) * t
    d = q2[L]
    ms = maths(d)
    yeq = [m for m in ms if m.startswith("y=")]
    report(len(yeq) >= 1 and eq(T(yeq[0][2:]), f), f"Q2{L} equation {yeq[:1]}", f"line {f}")
    Ax = sp.integrate(f, (t, 0, x))
    n = 0
    for m in ms:
        if m.startswith("A(x)="):
            for mem in split_top(m)[1:]:
                n += 1
                report(eq(T(mem), Ax), f"Q2{L} A member {mem[:40]}", f"integral {Ax}")
        if m.startswith("A'(x)="):
            report(eq(T(m.split("=", 1)[1]), f.subs(t, x)), f"Q2{L} A'(x)", m)
        if m.startswith("\\tfrac") and "=" in m:
            a_, b_ = split_top(m)
            report(eq(T(a_), T(b_)) and eq(T(b_), sp.Rational(y4 - y0, 4)), f"Q2{L} gradient {m}")
    report(n >= 1, f"Q2{L} A(x) chain found")

# ---------------------------------------------------------------- Ex 3 (models of the sketched graphs)
F3 = {"a": 1 + (t - 2)**2 / 4, "b": 1 / (1 + (t - 2)**2)}
q3 = lettered(block(ans, "q3"))
for L, f in F3.items():
    d = q3[L]
    for lo, hi, iv in ((sp.Rational(1, 2), sp.Rational(3, 2), r"In \([0,2]\)"), (3, 6, r"In \([2,\infty)\)")):
        inc = all(sp.diff(f, t).subs(t, v) > 0 for v in (lo, hi))
        dec = all(sp.diff(f, t).subs(t, v) < 0 for v in (lo, hi))
        want = ("increasing" if inc else "decreasing") + (" towards 0" if (L == "b" and dec) else "")
        rate = "increasing at an increasing rate" if inc else "increasing at a decreasing rate"
        seg = d.split(iv)[1][:200] if iv in d else ""
        report(seg.startswith(r", \(f(t)\) is " + want) and rate in seg, f"Q3{L} {iv}", seg[:90])
    report(all(f.subs(t, v) > 0 for v in (0, 1, 2, 3, 10)) and r"\(f(t)\gt0\)" in d, f"Q3{L} f > 0 so A increasing")
    report(r"inflection at \(x=2\)" in d and sp.diff(f, t).subs(t, 2) == 0, f"Q3{L} inflection at x = 2")
    report(r"\(A(0)=0\)" in d, f"Q3{L} A(0) = 0")

# ---------------------------------------------------------------- Ex 4, 5, 6
q4 = block(ans, "q4")
q4stem = q_integrals(TQ["4"])
q4ans = [T(m) for m in maths(q4)]
report(len(q4stem) == 3 and len(q4ans) == 3, "Q4 parts read", f"{q4stem} {q4ans}")
for (a, f), r, L in zip(q4stem, q4ans, "abc"):
    report(eq(r, f.subs(t, x)), f"Q4{L} = integrand at x", str(r))
    report(abs(complex(num_ftc(f, a, 1.3)) - complex(r.subs(x, 1.3))) < 1e-6, f"Q4{L} numeric FTC")
q5stem = q_integrals(TQ["5"])
report(len(q5stem) == 3, "Q5 stem parts read", str(q5stem))
for (a, f), L in zip(q5stem, "abc"):
    b = block(ans, f"q5{L}")
    first = maths(b)[0]
    report(eq(T(first), f.subs(t, x)), f"Q5{L} differential-form answer {first}")
    int_form(b, a, f, f"Q5{L}")
q6 = q_integrals(TQ["6"])
report(len(q6) == 4, "Q6 stem parts read", str(q6))
q6a = block(ans, "q6a")
q6ans = [T(m) for m in maths(q6a)]
for (a, f), r, L in zip(q6, q6ans, ["i", "ii", "iii", "iv"]):
    report(eq(r, f.subs(t, x)), f"Q6a {L}", str(r))
    lo = 2 if a.free_symbols else a           # check the general lower limit a with a = 2
    fn = f.subs(sp.Symbol("a"), 2)
    report(abs(complex(num_ftc(fn, lo, 2.6)) - complex(r.subs(x, 2.6))) < 1e-6, f"Q6a {L} numeric FTC")
q6b = block(ans, "q6b")
parts6 = q6b.split("&emsp;ii")
report(len(parts6) == 2, "Q6b split into i and ii")
for (a, f), chunk, L in zip(q6[:2], parts6, ["i", "ii"]):
    I = sp.integrate(f, (t, a, x))
    if L == "i":
        m0 = maths(chunk)[0]
        for mem in split_top(m0):
            report(eq(ev(mem), I), f"Q6b i member {mem.strip()[:40]}", f"expected {I}")
        for mem in split_top(maths(chunk)[1].replace("\\dfrac{d}{dx}", "\\frac{d}{dx}")):
            report(eq(ev(mem), f.subs(t, x)), f"Q6b i derivative member {mem[:40]}")
    else:
        int_form(chunk, a, f, "Q6b ii")

# ---------------------------------------------------------------- Ex 7
q7 = lettered(block(ans, "q7"))
F7 = {"a": (sp.exp(t), 0), "b": (sp.log(t), 1), "c": (1 / t, 1)}
xp = sp.Symbol("xp", positive=True)
for L, (f, a) in F7.items():
    A = sp.integrate(f.subs(t, sp.Symbol("u", positive=True)), (sp.Symbol("u", positive=True), a, xp))
    A = sp.simplify(A)
    d = q7[L]
    Ad, Add = sp.diff(A, xp), sp.diff(A, xp, 2)
    if L == "a":
        Aa = sp.integrate(sp.exp(t), (t, 0, x))
        report(r"looks like \(y=e^x-1\)" in d and eq(Aa, sp.exp(x) - 1), "Q7a A(x) = e^x - 1", str(Aa))
        report(all(sp.exp(v) - 1 < 0 for v in (-3, -1, -sp.Rational(1, 10))) and r"\(A(x)\lt0\) for \(x\lt0\)" in d, "Q7a A < 0 for x < 0")
        report("increasing at an increasing rate" in d, "Q7a increasing at an increasing rate (e^t > 0, increasing)")
    else:
        pts_r = (sp.Rational(3, 2), 3, 10)
        inc = all(Ad.subs(xp, v) > 0 for v in pts_r)
        acc = all(Add.subs(xp, v) > 0 for v in pts_r)
        phrase = "increasing at an increasing rate" if (inc and acc) else "increasing at a decreasing rate"
        report(r"zero at \(x=1\)" in d and A.subs(xp, 1) == 0 and phrase in d, f"Q7{L} zero at 1, {phrase}")
        left = [A.subs(xp, v) for v in (sp.Rational(1, 10), sp.Rational(1, 2), sp.Rational(9, 10))]
        if L == "b":
            report(all(v > 0 for v in left) and r"so \(A(x)\gt0\)" in d, "Q7b A > 0 on (0, 1)", str(left))
            report(all(Ad.subs(xp, v) < 0 for v in (sp.Rational(1, 10), sp.Rational(1, 2))) and "is decreasing" in d, "Q7b decreasing on (0, 1)")
            report(r"lowest point is \((1,0)\)" in d, "Q7b lowest point (1, 0)")
        else:
            report(all(v < 0 for v in left) and r"\(0\lt x\lt1\), \(A(x)\lt0\)" in d, "Q7c A < 0 on (0, 1)", str(left))

# ---------------------------------------------------------------- Ex 8
for L, f in (("a", sp.cos(t)), ("b", sp.sin(t))):
    b = block(ans, f"q8{L}")
    pi = sp.pi
    rows = re.findall(r"<tr>(.*?)</tr>", b, re.S)
    xs = [T(v) for v in maths(rows[0])[1:]]
    vs = [T(v) for v in maths(rows[1])[1:]]
    report(xs == [0, pi / 2, pi, 3 * pi / 2, 2 * pi], f"Q8{L} x row", str(xs))
    for k, v in zip(xs, vs):
        report(eq(v, sp.integrate(f, (t, 0, k))), f"Q8{L} A({k})", f"printed {v}")
    n = 0
    for m in maths(b.split("<table")[0]):
        mm = re.match(r"A(\\big\(|\()(.+?)(\\big\)|\))=(.*)$", m.strip(), re.S)
        if mm:
            k = T(mm.group(2))
            for mem in split_top(mm.group(4)):
                n += 1
                report(eq(T(mem), sp.integrate(f, (t, 0, k))), f"Q8{L} chain A({k}) member {mem}")
    report(n >= 5, f"Q8{L} chains checked", str(n))
    report(sp.integrate(sp.cos(t), (t, 0, pi / 2)) == 1, "Q8 region P has area 1")
report(r"looks like \(y=\sin x\)" in block(ans, "q8a") and eq(sp.integrate(sp.cos(t), (t, 0, x)), sp.sin(x)), "Q8a looks like sin x")
report(r"looks like \(y=1-\cos x\)" in block(ans, "q8b") and eq(sp.integrate(sp.sin(t), (t, 0, x)), 1 - sp.cos(x)), "Q8b looks like 1 - cos x")
report(eq(sp.diff(sp.sin(x), x), sp.cos(x)) and eq(sp.diff(sp.cos(x), x), -sp.sin(x)), "Q8 suggested derivatives")

# ---------------------------------------------------------------- Ex 9 (model of the sketched f: point symmetric about c)
LET = {1: "a", 2: "b", 3: "c", 4: "d", 5: "e"}
u = t - 3
f9 = -u / (1 + u**2 / 3)**2
report(eq(f9.subs(t, 6 - t), -f9), "Q9 model has point symmetry in (c, 0)")
zero = [s for s in sp.solve(f9, t)]
tp = sorted(sp.solve(sp.diff(f9, t), t))
A9 = sp.integrate(f9, (t, 1, x))
zA = sorted(s for s in sp.solve(sp.simplify(A9), x) if s.is_real)
q9 = lettered(block(ans, "q9"))
c_ = LET[int(zero[0])]
report(rf"for \(x\lt {c_}\)" .replace(" ", "") in q9["a"].replace(" ", "") and rf"decreasing for \(x\gt {c_}\)".replace(" ", "") in q9["a"].replace(" ", "").replace("<br>", "")
       or (rf"\(x\lt {c_}\)".replace(" ", "") in q9["a"].replace(" ", "") and rf"\(x\gt {c_}\)".replace(" ", "") in q9["a"].replace(" ", "")),
       f"Q9a increasing for x < {c_} (f > 0), decreasing after")
report(rf"maximum turning point at \(x={c_}\)" in q9["b"] and "no minimum" in q9["b"], f"Q9b maximum at x = {c_}, no minimum")
report([LET[int(v)] for v in tp] == ["b", "d"] and r"at \(x=b\) and \(x=d\)" in q9["c"], "Q9c inflections at the turning points b, d of f", str(tp))
report([LET[int(v)] for v in zA] == ["a", "e"] and r"\(x=a\)" in q9["d"] and r"\(x=e\)" in q9["d"], "Q9d zeros a and e", str(zA))
signs = {v: sp.sign(A9.subs(x, v)) for v in (0, 2, 3, 4, 6)}
report(signs == {0: -1, 2: 1, 3: 1, 4: 1, 6: -1} and r"positive for \(a\lt x\lt e\)" in q9["e"]
       and r"negative for \(x\lt a\) and for \(x\gt e\)" in q9["e"], "Q9e signs of A", str(signs))

# ---------------------------------------------------------------- textbook key (PDF 890-891) compared with our answers
KEY = {
    "1a": sp.Rational(3, 2) * x**2, "1b": 3 * x,
    "2a": 3 * x, "2b": x**2, "2c": 2 * x + x**2 / 2, "2d": 5 * x - x**2 / 2,
    "4a": 1 / x, "4c": sp.exp(-x**2 / 2),
    "5a": (3 * x**2 - 12, x**3 - 12 * x + 11), "5b": (x**3 + 4 * x, x**4 / 4 + 2 * x**2 - 12),
    "5c": (1 / x**2, sp.Rational(1, 2) - 1 / x),
    "6a": [x**2, x**3 + 3 * x, 1 / x, (x**3 - 3)**4],
    "7a": sp.exp(x) - 1,
    "8a": [0, 1, 0, -1, 0], "8b": [0, 1, 2, 1, 0],
    "10": {"a": True, "b": True, "c": False, "d": True, "e": True, "f": False},
}
report(eq(KEY["1a"], sp.integrate(3 * t, (t, 0, x))), "key 1a")
for L in "abcd":
    y0, y4 = Q2PTS[L]
    report(eq(KEY["2" + L], sp.integrate(y0 + sp.Rational(y4 - y0, 4) * t, (t, 0, x))), f"key 2{L} agrees with our A(x)")
for L, (a, f) in zip("ac", [q4stem[0], q4stem[2]]):
    report(eq(KEY["4" + L], f.subs(t, x)), f"key 4{L}")
report(eq(q4ans[1], 1 / (1 + x**3)), "key slip 4b: the key prints 1/(1+t^3); our answer 1/(1+x^3) is the integrand at x")
for (a, f), L in zip(q5stem, "abc"):
    d_, A_ = KEY["5" + L]
    report(eq(d_, f.subs(t, x)) and eq(A_, sp.integrate(f, (t, a, x))), f"key 5{L}")
report(all(eq(k, f.subs(t, x)) for k, (a, f) in zip(KEY["6a"], q6)), "key 6a i-iv")
report(eq(KEY["7a"], sp.integrate(sp.exp(t), (t, 0, x))), "key 7a")
report(KEY["8a"] == [sp.integrate(sp.cos(t), (t, 0, k)) for k in (0, sp.pi / 2, sp.pi, 3 * sp.pi / 2, 2 * sp.pi)], "key 8a table")
report(KEY["8b"] == [sp.integrate(sp.sin(t), (t, 0, k)) for k in (0, sp.pi / 2, sp.pi, 3 * sp.pi / 2, 2 * sp.pi)], "key 8b table")
report(all(classify(*C4FUN["q10"][L])[1] == v for L, v in KEY["10"].items()), "key 10 classifications (key 10c says x = 0; the point is x = 2)")
report(r"not continuous at \(x=2\)" in BLK["10"], "our 10c names x = 2")

# ---------------------------------------------------------------- timed-practice note
note = ppl
m = re.search(r"do Questions (.+?) above in (\d+) minutes", note)
report(bool(m), "timed-practice sentence")
if m:
    items = re.findall(r"(\d+)(?:\((\w)\))?", m.group(1))
    for q, part in items:
        okq = q in TQ and (not part or re.search(r'<span class="pl">' + part + "</span>", TQ[q]))
        report(bool(okq), f"timed practice names Q{q}{'(' + part + ')' if part else ''}, which exists")
    report(m.group(2) == "30", "timed practice: 30 minutes")
report("first needs this lesson" in note and "2020–2024" in note, "timed-practice note wording (catalogue: no int1-L5 row)")

print(f"\n{NCHECK[0]} checks, {len(FAILS)} failures")
if FAILS:
    print("FAILED:", *FAILS[:40], sep="\n  ")
    sys.exit(1)
print("ALL OK")
