"""Check of Lesson 7E (Integration Part 2 pack): Applications of integration, plus the review section
(the integration questions of the Chapter 6 and Chapter 7 reviews).

The script reads the values PRINTED in workspace/build/int2/l7e.html and a_7e.html and recomputes them
independently with sympy (helper: int3_tex.py turns printed TeX into sympy):
  - every printed chain 'A = B = C' (aligned displays in Worked examples 24 and 25, the lesson-example
    answers and the past-paper solutions) is checked side by side: integrals are evaluated with
    sympy.integrate (dx or dy), brackets [F]_a^b by substitution, the rest numerically (1e-9);
  - every region of the lesson (tutor demos, your turns, worked examples) is set up from the QUESTION text
    (curves, intervals, intersection values are read from l7e.html); intercepts and intersections are
    found with sympy, and the area is the sum of |integral| between the roots, compared with the printed
    answer;
  - every textbook answer (Exercise 7E, Chapter 6 and Chapter 7 review) is compared with an independent
    computation: areas and definite integrals with sympy.integrate, primitives by differentiating the
    printed answer and comparing with the integrand at sample points, decimals by rounding;
  - the past-paper answers are recomputed by integrating with respect to x (the solutions integrate with
    respect to y), and the MC answer is checked against all four options;
  - structure: questions, bands, worked-example contents (book lines only, tips after), hints (neutral),
    source labels in both files, marks and time, figures exist and svg_overlap.py reports nothing.
A template must match exactly once; a missing template FAILS. Exit status 1 if anything fails.
Run: python3 workspace/checks/int2_7e.py
"""
import os
import re
import subprocess
import sys

import sympy as sp

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import int3_tex as T  # noqa: E402

SRC = os.environ.get("INT2_SRC", os.path.join(HERE, "..", "build", "int2"))
x = T.x
y = sp.Symbol("y")
N_ = sp.Symbol("N", positive=True)
m_, n_ = sp.symbols("m n")
E, PI = sp.E, sp.pi
FAILS, CNT = [], [0]


def report(ok, label, detail=""):
    CNT[0] += 1
    print(("OK       " if ok else "MISMATCH ") + label[:92] + ("  " + str(detail).replace("\n", " ")[:160] if detail else ""))
    if not ok:
        FAILS.append(label)


def read(name):
    with open(os.path.join(SRC, name), encoding="utf-8") as fh:
        return fh.read()


def grab(block, pattern, where, flags=re.S):
    found = re.findall(pattern, block, flags)
    if len(found) != 1:
        raise LookupError(f"{where}: pattern matched {len(found)} times: {pattern[:80]!r}")
    return found[0]


def close(a, b, tol=1e-9):
    try:
        return abs(complex(sp.N(a, 30)) - complex(sp.N(b, 30))) < tol
    except (TypeError, ValueError):
        return False


# ---------------------------------------------------------------- TeX -> sympy
def prep(t_):
    t_ = t_.replace("&amp;", "").replace("&", "").replace("\\displaystyle", "")
    t_ = re.sub(r"\\text\{[^{}]*\}", "", t_)
    t_ = t_.replace("\\,", " ").replace("\\ ", " ").replace("\\quad", " ")
    t_ = re.sub(r"(?<![\^\w{])(\d+)\\tfrac(\d)(\d)", r"(\1+\\tfrac{\2}{\3})", t_)
    t_ = re.sub(r"\\log_e\\cos\s*(\\tfrac\{[^{}]*\}\{[^{}]*\}|\\big\(.*?\\big\)|\d+|[a-z])", r"\\log_e(\\cos \1)", t_)
    t_ = re.sub(r"\\(sin|cos)\(([^()]*)\)x", r"\\\1((\2)x)", t_)
    t_ = re.sub(r"(\d)e", r"\1 e", t_)          # 4e-3 is 4 times e minus 3, not 0.004
    return t_.strip().rstrip(".,").strip()


def tex(t_, extra=None):
    loc = {"y": y, "N": N_, "m": m_, "n": n_, "C": sp.Integer(0)}
    if extra:
        loc.update(extra)
    return T.tex(prep(t_), loc)


LIM = r"(\{(?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*\}|\\pi|-?\w)"


def unbrace(g):
    return g[1:-1] if g.startswith("{") else g


def side(t_):
    """One side of a chain: integrals and [F]_a^b brackets are replaced by their values."""
    t_ = prep(t_)
    extra, cnt = {}, [0]

    def ph(val):
        name = f"Z{cnt[0]}Z"
        cnt[0] += 1
        extra[name] = val
        T.LOCAL.setdefault(name, sp.Symbol(name))
        return " " + name + " "

    def brk(mt):
        F = tex(mt.group(1))
        var = y if y in F.free_symbols else x
        return "(" + ph(F.subs(var, tex(unbrace(mt.group(3)))) - F.subs(var, tex(unbrace(mt.group(2))))) + ")"

    t_ = re.sub(r"\\Big\[(.*?)\\Big\]_" + LIM + r"\^" + LIM, brk, t_)

    def itg(mt):
        var = y if mt.group(4) == "y" else x
        g = tex(mt.group(3))
        return "(" + ph(sp.integrate(g, (var, tex(unbrace(mt.group(1))), tex(unbrace(mt.group(2)))))) + ")"

    t_ = re.sub(r"\\int_" + LIM + r"\^" + LIM + r"(.*?)\s*d([xy])(?![a-z])", itg, t_)
    return tex(t_, extra)


def aligned_lines(body):
    body = re.sub(r"\\begin\{aligned\}|\\end\{aligned\}", "", body)
    return [ln.strip() for ln in body.split("\\\\")]


def chain(display, label):
    """Check a printed display chain; return the last value."""
    seg = "".join(ln.replace("&amp;", "") for ln in aligned_lines(display))
    sides = [q for q in T.split_top(prep(seg), "=") if q.strip() and q.strip() not in ("A",)]
    try:
        vals = [side(q) for q in sides]
    except Exception as err:  # noqa: BLE001
        report(False, label, f"ERROR {err!r} in {seg[:90]!r}")
        return None
    ok = len(vals) >= 2 and all(close(vals[0], v) for v in vals[1:])
    report(ok, label, f"{len(vals)} sides = {sp.N(vals[-1], 8)}: " + " | ".join(sides)[:120])
    return vals[-1]


def displays(block):
    return re.findall(r"\\\[(.*?)\\\]", block, re.S)


def area_abs(f, a, b, var=x):
    roots = sorted({r for r in sp.solveset(f, var, sp.Interval.open(a, b)) if r.is_real}, key=float) \
        if isinstance(sp.solveset(f, var, sp.Interval.open(a, b)), sp.FiniteSet) else []
    pts = [a] + roots + [b]
    return sp.nsimplify(sum(sp.Abs(sp.integrate(f, (var, p, q))) for p, q in zip(pts, pts[1:])))


def num_area(f, a, b, n=20000):
    fl = sp.lambdify(x, f, "math")
    a, b = float(a), float(b)
    h = (b - a) / n
    return sum(abs(fl(a + (i + 0.5) * h)) for i in range(n)) * h


def deriv_match(F, f, pts=(0.31, 0.47, 0.73, 1.13, 1.37), subs=None):
    """d/dx F equals f at sample points (complex parts from logs of negatives cancel in the difference)."""
    dF = sp.diff(F, x)
    good = 0
    for p in pts:
        try:
            a_ = complex(sp.N(dF.subs(subs or {}).subs(x, p)))
            b_ = complex(sp.N(f.subs(subs or {}).subs(x, p)))
        except (TypeError, ValueError, ZeroDivisionError):
            continue
        if abs(a_ - b_) > 1e-8:
            return False
        good += 1
    return good >= 3


# ---------------------------------------------------------------- files and blocks
les, ans = read("l7e.html"), read("a_7e.html")
teach = les.split("<!-- ============ Homework ============ -->")[0]
hw = les.split("<!-- ============ Homework ============ -->")[1].split("<!-- ============ Past papers")[0]
ppl = les.split("<!-- ============ Past papers ============ -->")[1].split("<!-- ============ Chapter review")[0]
rvl = les.split("<!-- ============ Chapter review ============ -->")[1]
rv6l, rv7l = rvl.split("{{sec:blue:pencil:Chapter 7 review:integration questions}}")
CON = {}
for c in (1, 2, 3):
    seg = teach.split(f"<!-- ============ Concept {c} ============ -->")[1].split("<!-- ============")[0]
    CON[c] = seg
EX = {}
for kind, tag, body in re.findall(r'<div class="ex (demo|attempt|worked)"><div class="ex-top"><span class="tag">([^<]*)</span>(.*?)(?=<div class="ex |<div class="box|<!-- =|$)', teach, re.S):
    EX.setdefault(kind, []).append((tag, body))
report([t for t, _ in EX.get("worked", [])] == ["Worked example 24", "Worked example 25"], "worked examples 24 and 25 (Example 26 omitted: doubtful limit)")
report(len(EX.get("demo", [])) == 3 and len(EX.get("attempt", [])) == 3, "three tutor demos and three your turns")
for c in (1, 2, 3):
    report(CON[c].count('class="ex demo"') == 1 and CON[c].count('class="ex attempt"') == 1, f"concept {c}: one tutor demo, one your turn")

a_les, a_rest = ans.split('<div class="ans-sec">Textbook Homework</div>')
a_hw, a_rest = a_rest.split("{{ahead:Lesson 7E | Applications of integration}}")
a_pp, a_rv = a_rest.split("{{ahead:Review | Chapter review exercise}}")
a_rv6, a_rv7 = a_rv.split('<div class="ans-sec">Chapter 7 review: integration questions</div>')
report(ans.count("{{ahead:Lesson 7E | Applications of integration}}") == 2 and ans.index("Lesson Examples") < ans.index("Textbook Homework")
       < ans.index("Past-Paper Homework") < ans.index("{{ahead:Review | Chapter review exercise}}"),
       "answers order: ahead, Lesson Examples, Textbook Homework, ahead, Past-Paper, Review")


def blocks(part):
    return dict(re.findall(r'<div class="a"[^>]*><span class="an">([^<]+)</span><div class="ab">(.*?)(?=<div class="a"[^>]*><span class="an">|<div class="ans-sec">|\{\{ahead|$)', part, re.S))


BL, BH, B6, B7 = blocks(a_les), blocks(a_hw), blocks(a_rv6), blocks(a_rv7)

for name in sorted(set(re.findall(r"\{\{svg:([\w-]+)\}\}", les + ans))):
    report(os.path.exists(os.path.join(SRC, "svg", name + ".svg")), f"figure {name}")
figs = sorted(os.path.join(SRC, "svg", f) for f in os.listdir(os.path.join(SRC, "svg")) if f.split("_")[0] in ("c7e", "q7e", "p7e", "r7e", "a7e"))
ov = subprocess.run([sys.executable, "-I", os.path.join(HERE, "..", "tools", "svg_overlap.py")] + figs, capture_output=True, text=True)
report(ov.returncode == 0 and len(figs) >= 30, f"svg_overlap.py on the {len(figs)} 7E figures", ov.stdout.strip().splitlines()[-1] if ov.stdout else ov.stderr[:100])


# ---------------------------------------------------------------- worked examples and lesson examples
def check_all_chains(block, label):
    vals = []
    for k, d in enumerate(displays(block)):
        if re.match(r"\s*\\begin\{aligned\}\s*(y|x|\\dfrac\{[xy]\}|\\cos)", d):
            continue        # rearranging an equation (checked separately)
        if "=" not in d:
            continue
        vals.append(chain(d, f"{label} display {k + 1}"))
    return vals


def interval(q):
    a_, b_ = grab(q, r"in the interval \\\((-?[^\\]*?|-?\\dfrac\{[^}]*\}\{\d\}|-\\pi)\\le x\\le([^)]*?)\\\)", "interval")
    return tex(a_), tex(b_)


# Concept 1: y = cos(kx), sketch on an interval, area between curve and x-axis
for tag, qb, ab in (("WE24", EX["worked"][0][1], EX["worked"][0][1]), ("C1 demo", EX["demo"][0][1], BL["C1"].split("<b>Your turn.</b>")[0]),
                    ("C1 your turn", EX["attempt"][0][1], BL["C1"].split("<b>Your turn.</b>")[1])):
    try:
        cur = grab(qb.split('<div class="sol-label">')[0], r"<b>a</b> Sketch \\\(y=(\\cos[^\\]*?(?:\\tfrac\d\d)?\w*)\\\) in the interval", f"{tag} curve")
        f = tex(cur)
        lo, hi = tex(grab(qb.split('<div class="sol-label">')[0], r"in the interval \\\((0)\\le x\\le", f"{tag} lo")), \
            tex(grab(qb.split('<div class="sol-label">')[0], r"in the interval \\\(0\\le x\\le([^\\]*?\\pi)\\\)", f"{tag} hi"))
        roots = sorted(sp.solveset(f, x, sp.Interval.open(lo, hi)), key=float)
        report(len(roots) == 2, f"{tag}: two x-intercepts inside [0, {hi}]", str(roots))
        A = area_abs(f, lo, hi)
        report(abs(float(A) - num_area(f, lo, hi)) < 1e-6, f"{tag}: area {A} (numeric check)")
        vals = check_all_chains(ab, tag)
        pieces = [sp.integrate(f, (x, p, q)) for p, q in zip([lo] + roots, roots + [hi])]
        report(len(vals) == 4 and all(close(v, w) for v, w in zip(vals[:3], pieces)) and close(vals[3], A),
               f"{tag}: pieces {pieces} and total {A}", str(vals))
        per = sp.simplify(2 * PI / sp.Poly(sp.expand(f.args[0]), x).coeffs()[0])
        report(f"={sp.latex(per).replace(' ', '')}" in ab.replace(" ", "").replace("\\pi", "\\pi"), f"{tag}: period {per} printed")
        for r in roots:
            rt = sp.latex(r).replace("\\frac", "\\dfrac").replace(" ", "")
            ok = (rt in ab.replace(" ", "")) or (f"x={sp.latex(r).replace(' ', '')}" in ab.replace(" ", ""))
            report(ok, f"{tag}: intercept {r} printed")
    except Exception as err:  # noqa: BLE001
        report(False, tag, f"ERROR {err!r}")


# Concept 2: two curves meeting at a given x; area on a given interval
def two_curves(tag, qb, ab, n_chains):
    q = qb.split('<div class="sol-label">')[0]
    c1, c2, xi = grab(q, r"the curves \\\(y=([^\\]*?\\(?:sin|cos)[^\\]*?)\\\) and \\\(y=([^\\]*?\\(?:sin|cos)[^\\]*?)\\\) intersect when \\\(x=(\\dfrac\{\\pi\}\{\d\})\\\)", f"{tag} curves")
    f1, f2, x0 = tex(c1), tex(c2), tex(xi)
    report(sp.simplify(f1.subs(x, x0) - f2.subs(x, x0)) == 0, f"{tag}: curves meet at x = {x0}", f"{f1}, {f2}")
    iv = re.findall(r"in the interval \\\(\\Big\[(.*?),(.*?)\\Big\]\\\)", q)
    a_, b_ = tex(iv[-1][0]), tex(iv[-1][1])
    inside = [r for r in sp.solveset(f1 - f2, x, sp.Interval.open(a_, b_))]
    report(inside == [], f"{tag}: no crossing inside ({a_}, {b_})")
    mid = (a_ + b_) / 2
    top, bot = (f1, f2) if (f1 - f2).subs(x, mid) > 0 else (f2, f1)
    A = sp.nsimplify(sp.integrate(top - bot, (x, a_, b_)))
    vals = check_all_chains(ab, tag)
    report(len(vals) == n_chains and close(vals[-1], A) and abs(float(A) - num_area(top - bot, a_, b_)) < 1e-6,
           f"{tag}: area {A} (top {top})", str(vals))
    return A


try:
    report(two_curves("WE25", EX["worked"][1][1], EX["worked"][1][1], 2) == sp.Rational(1, 4), "WE25 area 1/4 (book)")
    report(two_curves("C2 demo", EX["demo"][1][1], BL["C2"].split("<b>Your turn.</b>")[0], 1) == sp.Rational(9, 4), "C2 demo area 9/4")
    report(two_curves("C2 your turn", EX["attempt"][1][1], BL["C2"].split("<b>Your turn.</b>")[1], 1) == sp.Rational(1, 4), "C2 your turn area 1/4")
except Exception as err:  # noqa: BLE001
    report(False, "concept 2", f"ERROR {err!r}")

# Concept 3: two curves crossing twice in an interval
for tag, qb, ab in (("C3 demo", EX["demo"][2][1], BL["C3"].split("<b>Your turn.</b>")[0]),
                    ("C3 your turn", EX["attempt"][2][1], BL["C3"].split("<b>Your turn.</b>")[1])):
    try:
        lo, hi = grab(qb, r"in the interval \\\((-?\\pi|0)\\le x\\le(2\\pi|\\pi)\\\)", f"{tag} interval")
        lo, hi = tex(lo), tex(hi)
        c1, c2 = grab(qb, r"the curves \\\(y=(\\sin x)\\\) and \\\(y=(-?\\cos x)\\\) intersect", f"{tag} curves")
        f1, f2 = tex(c1), tex(c2)
        p1, p2 = grab(qb, r"intersect when \\\(x=(-?\\dfrac\{\d?\\pi\}\{4\})\\\) and when \\\(x=(\\dfrac\{\d?\\pi\}\{4\})\\\)", f"{tag} points")
        sol = sorted(sp.solveset(f1 - f2, x, sp.Interval(lo, hi)), key=float)
        report(sol == [tex(p1), tex(p2)], f"{tag}: intersections {sol}")
        A = sp.nsimplify(sp.Abs(sp.integrate(f1 - f2, (x, sol[0], sol[1]))))
        vals = check_all_chains(ab, tag)
        report(len(vals) == 1 and close(vals[0], A) and A == 2 * sp.sqrt(2), f"{tag}: area {A}")
        pts = re.findall(r"\\Big\((-?\\dfrac\{\d?\\pi\}\{4\}),(-?\\tfrac12\\sqrt2)\\Big\)", ab)
        report(len(pts) == 2 and all(close(tex(py), f1.subs(x, tex(px))) for px, py in pts), f"{tag}: printed points", str(pts))
    except Exception as err:  # noqa: BLE001
        report(False, tag, f"ERROR {err!r}")

# worked examples hold only the book's lines; the tips come after them
for k, w in enumerate(EX["worked"]):
    body = w[1]
    report("Note" not in body and "box tip" not in body and "test value" not in body, f"{w[0]}: only the textbook lines (no pack note)")
for c, t_ in ((1, "Reading Worked example 24, line by line"), (2, "Reading Worked example 25, line by line")):
    report(t_ in CON[c] and CON[c].index(t_) > CON[c].index("Keep for homework"), f"tip '{t_}' comes after the example")
try:
    tip = CON[2].split("Reading Worked example 25, line by line")[1]
    report("\\(-\\tfrac12\\times\\big(-\\tfrac12\\big)=\\tfrac14\\)" in tip and "\\(-\\tfrac12\\times1+1=\\tfrac12\\)" in tip
           and sp.Rational(-1, 2) * sp.Rational(-1, 2) == sp.Rational(1, 4) and sp.Rational(3, 4) - sp.Rational(1, 2) == sp.Rational(1, 4),
           "WE25 tip arithmetic")
    report(sp.sin(PI / 2) > sp.sqrt(2) / 2, "WE25 tip test value: sin 2x = 1 above sin x = sqrt2/2 at pi/4")
    tip24 = CON[1].split("Reading Worked example 24, line by line")[1]
    report(all(s_ in tip24 for s_ in ("\\(\\sin0=0\\)", "\\(\\sin\\dfrac{\\pi}{2}=1\\)", "\\(\\sin\\dfrac{3\\pi}{2}=-1\\)", "\\(\\sin2\\pi=0\\)", "\\(2+4+2=8\\)")),
           "WE24 tip values")
except Exception as err:  # noqa: BLE001
    report(False, "tips", f"ERROR {err!r}")

# ---------------------------------------------------------------- textbook homework: structure and text
TQ = dict(re.findall(r'<div class="q"><span class="q-num">(\d+)</span>(.*?)(?=<div class="q">|\{\{band|$)', hw, re.S))
report(sorted(TQ, key=int) == [str(i) for i in range(1, 24)], "Exercise 7E questions 1-23")
bf, rest = hw.split("{{band:D}}")
bd, be = rest.split("{{band:E}}")
report(bf.count('class="q-num"') == 7 and bd.count('class="q-num"') == 15 and be.count('class="q-num"') == 1, "bands F 1-7, D 8-22, E 23 (as the textbook)")
report(set(BH) == {str(i) for i in range(1, 24)} - {"13"}, "answer blocks Q1-23 except Q13 ('show that' only)", str(sorted(BH, key=int)))


def has(qtext, n, *snips):
    body = qtext[n].replace(" ", "")
    miss = [s_ for s_ in snips if s_.replace(" ", "") not in body]
    report(not miss, f"Q{n} question text", "missing " + ", ".join(miss) if miss else "")


def part(block, p, nth=0):
    """First math of part p in an answer block."""
    found = re.findall(r"<b>" + p + r"</b>\s*(?:<b>\w+</b>\s*)?\\\((.*?)\\\)", block, re.S)
    if not found:
        raise LookupError(f"part {p} missing")
    return found[nth]


def val_of(t_):
    t_ = re.sub(r"\\text\{[^}]*\}|\\?\s*u\\\)\^2|u\^2", "", t_)
    sides = T.split_top(prep(t_), "=")
    return [tex(z) for z in sides if z.strip()]


def eq_hw(n, p, expected, block=None, label=None, dp=None):
    lab = label or f"7E Q{n}{p}"
    try:
        t_ = part(block if block is not None else BH[n], p) if p else re.findall(r"\\\((.*?)\\\)", (block if block is not None else BH[n]))[0]
        if dp is not None:
            report(t_.strip() == f"{float(expected):.{dp}f}", f"{lab} = {float(expected):.{dp}f}", t_)
            return
        vs = val_of(t_)
        report(len(vs) >= 1 and all(close(v, expected) for v in vs), f"{lab} = {expected}", t_)
    except Exception as err:  # noqa: BLE001
        report(False, lab, f"ERROR {err!r}")


s, c_ = sp.sin, sp.cos
has(TQ, "1", "y=\\cos x", "\\dfrac{\\pi}{2}", "\\dfrac{\\pi}{6}")
eq_hw("1", "a", sp.integrate(c_(x), (x, 0, PI / 2)))
eq_hw("1", "b", sp.integrate(c_(x), (x, 0, PI / 6)))
has(TQ, "2", "y=\\sec^2x", "\\dfrac{\\pi}{4}", "\\dfrac{\\pi}{3}")
eq_hw("2", "a", sp.integrate(sp.sec(x) ** 2, (x, 0, PI / 4)))
eq_hw("2", "b", sp.integrate(sp.sec(x) ** 2, (x, 0, PI / 3)))
has(TQ, "3", "y=\\sin x")
eq_hw("3", "a", sp.integrate(s(x), (x, 0, PI / 4)))
eq_hw("3", "b", sp.integrate(s(x), (x, 0, PI / 6)))
has(TQ, "4", "q7e_q4a", "q7e_q4b")
eq_hw("4", "a", sp.integrate(s(x), (x, PI / 6, PI / 2)))
eq_hw("4", "b", -sp.integrate(c_(x), (x, 2 * PI / 3, PI)))
Q5 = {"a": (s(x), PI / 3, PI / 2, "y=\\sin x\\), from \\(x=\\dfrac{\\pi}{3}\\) to \\(x=\\dfrac{\\pi}{2}"),
      "b": (s(2 * x), PI / 4, PI / 2, "y=\\sin2x\\), from \\(x=\\dfrac{\\pi}{4}\\) to \\(x=\\dfrac{\\pi}{2}"),
      "c": (c_(x), PI / 3, PI / 2, "y=\\cos x\\), from \\(x=\\dfrac{\\pi}{3}\\) to \\(x=\\dfrac{\\pi}{2}"),
      "d": (c_(3 * x), PI / 12, PI / 6, "y=\\cos3x\\), from \\(x=\\dfrac{\\pi}{12}\\) to \\(x=\\dfrac{\\pi}{6}"),
      "e": (sp.sec(x) ** 2, PI / 6, PI / 3, "y=\\sec^2x\\), from \\(x=\\dfrac{\\pi}{6}\\) to \\(x=\\dfrac{\\pi}{3}"),
      "f": (sp.sec(x / 2) ** 2, -PI / 2, PI / 2, "y=\\sec^2\\tfrac12x\\), from \\(x=-\\dfrac{\\pi}{2}\\) to \\(x=\\dfrac{\\pi}{2}")}
for p, (f, a_, b_, snip) in Q5.items():
    has(TQ, "5", snip)
    eq_hw("5", p, area_abs(f, a_, b_))
has(TQ, "6", "q7e_q6a", "q7e_q6d")
eq_hw("6", "a", sp.integrate(s(x) - c_(x), (x, PI / 4, PI / 2)))
eq_hw("6", "b", sp.integrate(s(2 * x) - s(x), (x, 0, PI / 3)))
eq_hw("6", "c", sp.integrate(x - s(x), (x, 0, PI / 2)))
eq_hw("6", "d", sp.integrate(1 - c_(x), (x, -PI / 2, PI / 2)))
eq_hw("7", "a", sp.integrate(s(x), (x, 0, PI / 4)) + sp.integrate(c_(x), (x, PI / 4, PI / 2)))
eq_hw("7", "b", sp.integrate(x + 1, (x, -1, 0)) + sp.integrate(c_(x), (x, 0, PI / 2)))
eq_hw("8", "a", area_abs(s(x), 0, PI))
eq_hw("8", "b", area_abs(c_(2 * x), -PI / 4, PI / 4))
Q9 = {"a": (c_(x), 0, PI), "b": (s(x), PI / 4, 3 * PI / 4), "c": (c_(2 * x), 0, PI), "d": (s(2 * x), PI / 3, 2 * PI / 3),
      "e": (s(x), -5 * PI / 6, 7 * PI / 6), "f": (c_(3 * x), PI / 6, 2 * PI / 3)}
has(TQ, "9", "x=-\\dfrac{5\\pi}{6}", "x=\\dfrac{7\\pi}{6}", "y=\\cos3x")
for p, (f, a_, b_) in Q9.items():
    eq_hw("9", p, area_abs(f, a_, b_))
roots10 = sorted(sp.solveset(2 * c_(PI * x), x, sp.Interval(-1, 1)), key=float)
report(roots10 == [-sp.Rational(1, 2), sp.Rational(1, 2)], "Q10 x-intercepts -1/2 and 1/2")
eq_hw("10", "b", area_abs(2 * c_(PI * x), roots10[0], roots10[1]))
has(TQ, "11", "y=3\\cos\\Big(\\dfrac{\\pi}{2}x\\Big)", "one decimal place")
report(BH["11"].count("\\(3.8\\)") == 1 and f"{float(sp.integrate(3 * c_(PI * x / 2), (x, -1, 1))):.1f}" == "3.8", "Q11 window 12/pi = 3.8 m^2")
eq_hw("12", "", area_abs(x - (x - s(x)), 0, 2 * PI))
has(TQ, "13", "y=\\tan x", "\\ln2")
report(sp.simplify(sp.integrate(sp.tan(x), (x, 0, PI / 3)) - sp.log(2)) == 0, "Q13 (show): integral of tan x from 0 to pi/3 is ln 2")
eq_hw("14", "b", sp.integrate(sp.Abs(c_(x) - s(x)), (x, -PI / 2, PI / 6)) if False else sp.integrate(c_(x) - s(x), (x, -PI / 2, PI / 6)))
report(all((c_(x) - s(x)).subs(x, t) > 0 for t in (-PI / 2, -PI / 4, 0, PI / 6)) and sp.solveset(c_(x) - s(x), x, sp.Interval(-PI / 2, PI / 6)) == sp.EmptySet,
       "Q14 cos x above sin x on the whole interval")
report(all(sp.simplify(s(t) - c_(2 * t)) == 0 for t in (-PI / 2, PI / 6)), "Q15a the curves meet at -pi/2 and pi/6")
eq_hw("15", "c", sp.integrate(c_(2 * x) - s(x), (x, -PI / 2, PI / 6)))
report(sp.simplify(sp.expand_trig(sp.sqrt(2) * s(x + PI / 4)) - s(x) - c_(x)) == 0, "Q16a identity")
eq_hw("16", "b", sp.integrate(s(x) + c_(x), (x, -PI / 4, 3 * PI / 4)))
report("They are all \\(4\\) u\\(^2\\)" in BH["17"] and all(area_abs(f, 0, 2 * PI) == 4 for f in (s(x), s(2 * x), s(3 * x), s(5 * x), c_(x), c_(4 * x))),
       "Q17b every area is 4")
report(sp.integrate(1 + s(2 * PI * x), (x, 0, 3)) == 3, "Q18a (show) with n = 3")
eq_hw("19", "", area_abs(s(x), 0, 6 * PI))
Q22 = {"a": (s(3 * x), -4 * PI, 4 * PI), "b": (c_(x) ** 2 * s(x) ** 3, -2 * PI, 2 * PI), "c": (c_(x), -5 * PI / 2, 5 * PI / 2),
       "d": (sp.sec(x / 3) ** 2, -PI, PI), "e": (3 + 2 * x + s(x), -PI, PI), "f": (s(2 * x) + c_(3 * x) + 3 * x ** 2, -PI / 2, PI / 2)}
for p, (f, a_, b_) in Q22.items():
    eq_hw("22", p, sp.integrate(f, (x, a_, b_)))
report("\\pi^3" in BH["22"] and "\\pi^2" not in BH["22"], "Q22f prints pi^3/4 (the key's pi^2/4 is a slip)")
try:
    F23 = -sp.Rational(1, 2) * sp.exp(-x) * (s(x) + c_(x))
    report(sp.simplify(sp.diff(F23, x) - sp.exp(-x) * s(x)) == 0, "Q23a derivative")
    t23 = grab(BH["23"], r"<b>b</b> \\\(\\displaystyle\\int_0\^Ne\^\{-x\}\\sin x\\,dx=(.*?)\\\)", "Q23b")
    report(sp.simplify(tex(t23) - sp.integrate(sp.exp(-x) * s(x), (x, 0, N_))) == 0 and sp.limit(tex(t23), N_, sp.oo) == sp.Rational(1, 2), "Q23b integral to N, limit 1/2", t23)
    c1_, c2_ = re.findall(r"=(\\tfrac12[^\\]*?(?:e\^\{-2\\pi\})?\\big\(1\+e\^\{-\\pi\}\\big\))", BH["23"])
    v1 = sp.integrate(sp.exp(-x) * s(x), (x, 0, PI))
    v2 = sp.integrate(sp.exp(-x) * s(x), (x, 2 * PI, 3 * PI))
    report(close(tex(c1_), v1) and close(tex(c2_), v2) and sp.simplify(v2 / v1 - sp.exp(-2 * PI)) == 0
           and sp.simplify(v1 / (1 - sp.exp(-2 * PI)) - sp.exp(PI) / (2 * (sp.exp(PI) - 1))) == 0, "Q23c arches, ratio e^{-2pi}, limiting sum", f"{c1_} ; {c2_}")
except Exception as err:  # noqa: BLE001
    report(False, "Q23", f"ERROR {err!r}")

# ---------------------------------------------------------------- past papers
PPL = dict(re.findall(r'<span class="pn">PP (\d)</span>(.*?)(?=<div class="pp">|$)', ppl, re.S))
PPA = dict(re.findall(r'<span class="pn">PP (\d)</span>(.*?)(?=<div class="ppa"|$)', a_pp, re.S))
LABELS = {"1": "Fort Street High School, 2020, Trial Higher School Certificate Examination, Mathematics Extension&nbsp;1,&nbsp;Q10",
          "2": "Caringbah High School, 2021, Year 12 Mathematics Extension&nbsp;1 HSC Course Assessment Task&nbsp;4,&nbsp;Q12(c)",
          "3": "Northern Beaches Secondary College Manly Selective Campus, 2020, Year 12 Trial Examination, Mathematics <span style=\"white-space:nowrap\">Extension&nbsp;1,&nbsp;Q11(c)",
          "4": "Hornsby Girls High School, 2023, Year 12 Higher School Certificate Trial Examination Term&nbsp;3, Mathematics <span style=\"white-space:nowrap\">Extension&nbsp;1,&nbsp;Q14(b)",
          "5": "Pymble Ladies' College, 2024, Mathematics Extension 1 HSC Trial Examination Term&nbsp;3,&nbsp;Q13(d)"}
MARKS = {"1": 1, "2": 5, "3": 3, "4": 3, "5": 5}
report(sorted(PPL) == sorted(PPA) == list("12345"), "past papers PP 1-5 in both files")
for k, lab in LABELS.items():
    report(PPL[k].startswith(lab) and PPA[k].startswith(lab), f"PP {k} source label identical in both files")
    mk = re.findall(r'<span class="mk">(\d+) marks?</span>', PPL[k])
    subs = [int(z) for z in re.findall(r'<span class="mk">(\d)</span>', PPL[k])]
    report(mk == [str(MARKS[k])] and (not subs or sum(subs) == MARKS[k]), f"PP {k}: {MARKS[k]} marks (parts {subs})")
total = sum(MARKS.values())
report(f"<b>{total} marks</b>" in ppl and f"Suggested time: {5 * round(1.5 * total / 5)} minutes" in ppl and 15 <= total <= 22,
       f"mini exam {total} marks, time {5 * round(1.5 * total / 5)} min")
BANNED = r"product|quotient|chain|substitut|integrat|respect|inverse|reflect|symmetr|odd|even|part \(i|worked example|swap|subject|rule|formula|\d|tan|cos|sin|log|area of|rectangle|subtract"
for k in PPL:
    h = grab(PPL[k], r'<div class="hint"><b>Hint:</b> (.*?)</div>', f"PP {k} hint")
    report(h.endswith("?") and not re.search(BANNED, h, re.I) and "\\(" not in h, f"PP {k} hint is a neutral question", h)
try:
    # PP1: the shaded region lies between the intersections; only option B equals the area
    xs = sorted(sp.solveset(s(x) - c_(x), x, sp.Interval(0, 2 * PI)), key=float)
    A1 = sp.integrate(s(x) - c_(x), (x, xs[0], xs[1]))
    opts = {"A": sp.integrate(c_(x) - s(x), (x, PI / 4, 5 * PI / 4)), "B": sp.integrate(s(x) - c_(x), (x, PI / 4, 5 * PI / 4)),
            "C": sp.integrate(c_(x) + s(x), (x, PI / 4, 5 * PI / 4)), "D": sp.integrate(c_(x) - s(x), (x, PI / 3, 4 * PI / 3))}
    good = [k_ for k_, v in opts.items() if sp.simplify(v - A1) == 0]
    report(xs == [PI / 4, 5 * PI / 4] and good == ["B"] and "<b>Answer (B).</b>" in PPA["1"], "PP1 answer B", str(opts))
    for k_ in "ABCD":
        report(f"{k_}.&ensp;" in PPL["1"], f"PP1 option {k_} printed")
    # PP2: f(x) = 2 acos(x/3)
    f2 = 2 * sp.acos(x / 3)
    report(f2.subs(x, 0) == PI and "The \\(y\\) intercept is \\(\\pi\\)" in PPA["2"], "PP2 (i) y-intercept pi")
    report("\\(-3\\le x\\le3\\)" in PPA["2"] and "\\(0\\le y\\le2\\pi\\)" in PPA["2"] and f2.subs(x, -3) == 2 * PI and f2.subs(x, 3) == 0, "PP2 (ii) domain and range")
    A2 = sp.integrate(f2, (x, 0, 3))
    v = check_all_chains(PPA["2"], "PP2")
    report(close(v[-1], A2) and close(A2, 6) and "The area is \\(6\\) square units" in PPA["2"], "PP2 (iii) area 6 (integrating with respect to x)", str(sp.N(A2)))
    report(all(close(3 * c_(t / 2), sp.solve(sp.Eq(2 * sp.acos(x / 3), t), x)[0]) for t in (sp.Rational(1, 3), 1, 2)), "PP2 inverse x = 3cos(y/2)")
    # PP3: y = atan x, the y-axis and y = +-pi/4
    A3 = 2 * sp.integrate(PI / 4 - sp.atan(x), (x, 0, 1))
    v = check_all_chains(PPA["3"], "PP3")
    report(close(v[-1], A3) and close(A3, sp.log(2)) and "The area is \\(\\ln2\\) square units" in PPA["3"], "PP3 area ln 2 (by x)", str(sp.N(A3)))
    # PP4: y = 2 acos(x + 1/2), first quadrant
    f4 = 2 * sp.acos(x + sp.Rational(1, 2))
    A4 = sp.Integral(f4, (x, 0, sp.Rational(1, 2))).evalf(30)
    v = check_all_chains(PPA["4"], "PP4")
    report(f4.subs(x, 0) == 2 * PI / 3 and close(v[-1], A4) and close(A4, sp.sqrt(3) - PI / 3)
           and "\\Big(\\sqrt3-\\dfrac{\\pi}{3}\\Big)\\) square units" in PPA["4"], "PP4 area sqrt3 - pi/3 (by x)", str(A4))
    report(all(close(c_(t / 2) - sp.Rational(1, 2), sp.solve(sp.Eq(f4, t), x)[0]) for t in (sp.Rational(1, 2), 1, 2)), "PP4 inverse x = cos(y/2) - 1/2")
    # PP5: y = -atan x, the x-axis and x = 1
    A5 = sp.integrate(sp.atan(x), (x, 0, 1))
    v = check_all_chains(PPA["5"], "PP5")
    report(close(v[-1], A5) and close(A5, PI / 4 - sp.log(2) / 2) and "\\Big(1,-\\dfrac{\\pi}{4}\\Big)" in PPA["5"], "PP5 area pi/4 - (1/2) ln 2 and the point (1, -pi/4)")
except Exception as err:  # noqa: BLE001
    report(False, "past papers", f"ERROR {err!r}")
report("timed practice" not in ppl.lower(), "no timed-practice note (the set has 17 marks)")

# ---------------------------------------------------------------- review: Chapter 6
R6 = dict(re.findall(r'<div class="q"><span class="q-num">(\d+)</span>(.*?)(?=<div class="q">|\{\{sec|<p style|$)', rv6l, re.S))
R7 = dict(re.findall(r'<div class="q"><span class="q-num">(\d+)</span>(.*?)(?=<div class="q">|\{\{sec|<p style|$)', rv7l, re.S))
report(sorted(R6, key=int) == [str(i) for i in (16, 17, 18, 19, 20, 21, 22, 23, 32, 33, 34, 35, 36, 38, 39, 41)],
       "Chapter 6 review: the integration questions 16-23, 32-36, 38, 39, 41")
report(sorted(R7, key=int) == [str(i) for i in (5, 6, 7, 8, 9, 10, 11, 16, 17, 18, 19)], "Chapter 7 review: the integration questions 5-11, 16-19")
report("Show that for positive integers" not in R7["19"], "Ch 7 Q19(d) omitted (doubtful: 2 pi should be pi)")
report(set(B6) == set(R6) and set(B7) == set(R7), "review answer blocks match the questions")


def prim(block, n, p, integrand, label, subs=None, pts=(0.31, 0.47, 0.73, 1.13, 1.37)):
    try:
        t_ = part(block[n], p) if p else re.findall(r"\\\((.*?)\\\)", block[n])[0]
        report(deriv_match(tex(t_), integrand, pts=pts, subs=subs), f"{label}: derivative of the answer is the integrand", t_)
    except Exception as err:  # noqa: BLE001
        report(False, label, f"ERROR {err!r}")


ex = sp.exp
for p, f, snip in (("a", ex(5 * x), "e^{5x}"), ("b", 10 * ex(2 - 5 * x), "10e^{2-5x}"), ("c", ex(x / 5), "e^{\\frac15x}"), ("d", 3 * ex(5 * x - 4), "3e^{5x-4}")):
    has(R6, "16", snip)
    prim(B6, "16", p, f, f"R6 Q16{p}")
for p, f, a_, b_ in (("a", ex(x), 0, 2), ("b", ex(2 * x), 0, 1), ("c", ex(-x), -1, 0), ("d", ex(3 * x + 2), -sp.Rational(2, 3), 0),
                     ("e", ex(3 - 2 * x), 0, sp.Rational(1, 2)), ("f", 2 * ex(x / 2), 0, 2)):
    eq_hw("17", p, sp.integrate(f, (x, a_, b_)), block=B6["17"], label=f"R6 Q17{p}")
has(R6, "17", "\\int_{-\\frac23}^0e^{3x+2}", "\\int_0^{\\frac12}e^{3-2x}", "\\int_0^22e^{\\frac12x}")
for p, f, snip in (("a", 1 / ex(5 * x), "\\dfrac{1}{e^{5x}}"), ("b", ex(3 * x) * ex(x), "e^{3x}\\times e^x"), ("c", 6 / ex(3 * x), "\\dfrac{6}{e^{3x}}"),
                   ("d", ex(3 * x) ** 2, "(e^{3x})^2"), ("e", ex(3 * x) / ex(5 * x), "\\dfrac{e^{3x}}{e^{5x}}"), ("f", (ex(3 * x) + 1) / ex(2 * x), "\\dfrac{e^{3x}+1}{e^{2x}}"),
                   ("g", ex(2 * x) * (ex(x) + ex(-x)), "e^{2x}(e^x+e^{-x})"), ("h", (1 + ex(-x)) ** 2, "(1+e^{-x})^2")):
    has(R6, "18", snip)
    prim(B6, "18", p, f, f"R6 Q18{p}")
for p, f, a_, b_ in (("a", 1 + ex(-x), 0, 1), ("b", ex(2 * x) + x, 0, 2), ("c", 2 / ex(x), 0, 1), ("d", ex(3 * x) * (1 - ex(-3 * x)), 0, sp.Rational(1, 3)),
                     ("e", (ex(2 * x) + 1) / ex(x), 0, 1), ("f", (ex(x) + 1) ** 2, 0, 1)):
    eq_hw("19", p, sp.integrate(f, (x, a_, b_)), block=B6["19"], label=f"R6 Q19{p}")
try:
    fx = tex(grab(B6["20"], r"\\\(f\(x\)=(.*?)\\\)", "Q20 f(x)"))
    report(sp.simplify(sp.diff(fx, x) - (ex(x) - ex(-x) - 1)) == 0 and fx.subs(x, 0) == 3, "R6 Q20 f'(x) and f(0) = 3")
    report(close(tex(grab(B6["20"], r"\\\(f\(1\)=(.*?)\\\)", "Q20 f(1)")), fx.subs(x, 1)), "R6 Q20 f(1)")
    report(sp.simplify(tex(part(B6["21"], "a")) - sp.diff(ex(x ** 3), x)) == 0, "R6 Q21a derivative")
    eq_hw("21", "b", sp.integrate(x ** 2 * ex(x ** 3), (x, 0, 1)), block=B6["21"], label="R6 Q21b")
    report(part(B6["22"], "a").strip() == f"{float(sp.integrate(ex(2 * x), (x, 0, 1))):.3g}" == "3.19", "R6 Q22a 3.19 (3 s.f.)")
    report(part(B6["22"], "b").strip() == f"{float(sp.integrate(1 - ex(-x), (x, 0, 1))):.3g}" == "0.368", "R6 Q22b 0.368 (3 s.f.)")
    eq_hw("23", "a", -sp.integrate(ex(2 * x) - 1, (x, -1, 0)), block=B6["23"], label="R6 Q23a")
    eq_hw("23", "b", sp.integrate((E - 1) * x - (ex(x) - 1), (x, 0, 1)), block=B6["23"], label="R6 Q23b")
except Exception as err:  # noqa: BLE001
    report(False, "R6 Q20-23", f"ERROR {err!r}")
for p, f in (("a", 1 / x), ("b", 3 / x), ("c", 1 / (5 * x)), ("d", 1 / (x + 7)), ("e", 1 / (2 * x - 1)), ("f", 1 / (2 - 3 * x)), ("g", 2 / (2 * x + 9)), ("h", 8 / (1 - 4 * x))):
    prim(B6, "32", p, f, f"R6 Q32{p}")
for p, f, a_, b_ in (("a", 1 / (x + 2), 0, 1), ("b", 1 / (4 * x - 3), 1, 4), ("c", 1 / x, 1, E), ("d", 1 / x, E ** 2, E ** 3)):
    eq_hw("33", p, sp.integrate(f, (x, a_, b_)), block=B6["33"], label=f"R6 Q33{p}")
for p, f in (("a", 2 * x / (x ** 2 + 4)), ("b", (3 * x ** 2 - 5) / (x ** 3 - 5 * x + 7)), ("c", x / (x ** 2 - 3)), ("d", (x ** 3 - 1) / (x ** 4 - 4 * x))):
    prim(B6, "34", p, f, f"R6 Q34{p}")
eq_hw("35", "", sp.integrate(1 / x, (x, 2, 4)), block=B6["35"], label="R6 Q35")
report(sorted(sp.solve(sp.Eq(5 / x, 6 - x), x)) == [1, 5], "R6 Q36a intersections x = 1, 5")
eq_hw("36", "b", sp.integrate(6 - x - 5 / x, (x, 1, 5)), block=B6["36"], label="R6 Q36b")
for p, f in (("a", ex(x)), ("b", 2 ** x), ("c", 3 ** x), ("d", 5 ** x)):
    prim(B6, "38", p, f, f"R6 Q38{p}")
try:
    a39 = re.findall(r"\\\((.*?)\\\)", B6["39"])
    report(sp.simplify(tex(a39[0].split("=")[1]) - sp.diff(x * sp.log(x), x)) == 0 and deriv_match(tex(a39[1].split("=")[1]), sp.log(x)), "R6 Q39a derivative and primitive", a39[:2])
    report(sp.simplify(tex(a39[2].split("=")[1]) - sp.diff(x * ex(x), x)) == 0 and deriv_match(tex(a39[3].split("=")[1]), x * ex(x)), "R6 Q39b derivative and primitive", a39[2:4])
    report(sp.integrate(sp.log(x), (x, 1, E)) == 1 and sp.integrate(x * ex(x), (x, 0, 1)) == 1, "R6 Q39c (prove): both integrals are 1")
    v41 = re.findall(r"\\dfrac\{7\}\{(8?)\\ln2\}", B6["41"])
    report(v41 == ["", "8"] and close(sp.integrate(2 ** x, (x, 0, 3)), 7 / sp.log(2)) and close(sp.integrate(2 ** x, (x, -3, 0)), 7 / (8 * sp.log(2))), "R6 Q41a 7/ln2 and 7/(8 ln2)")
except Exception as err:  # noqa: BLE001
    report(False, "R6 Q39/41", f"ERROR {err!r}")

# ---------------------------------------------------------------- review: Chapter 7
for p, f in (("a", 4 * c_(x)), ("b", s(4 * x)), ("c", sp.sec(x / 4) ** 2)):
    prim(B7, "5", p, f, f"R7 Q5{p}")
for p, f, a_, b_ in (("a", sp.sec(x) ** 2, PI / 4, PI / 3), ("b", c_(2 * x), 0, PI / 4), ("c", PI * s(PI * x), 0, sp.Rational(1, 3))):
    eq_hw("6", p, sp.integrate(f, (x, a_, b_)), block=B7["6"], label=f"R7 Q6{p}")
has(R7, "6", "\\int_{\\frac{\\pi}{4}}^{\\frac{\\pi}{3}}\\sec^2x", "\\int_0^{\\frac13}\\pi\\sin\\pi x")
eq_hw("7", "", sp.integrate(s(3 * x), (x, 0, sp.Rational(1, 4))), block=B7["7"], label="R7 Q7", dp=3)
try:
    y8 = tex(grab(B7["8"], r"\\\(y=(.*?)\\\)", "R7 Q8"))
    report(sp.simplify(sp.diff(y8, x) - c_(x / 2)) == 0 and y8.subs(x, PI) == 1, "R7 Q8 y' = cos(x/2) and passes through (pi, 1)")
except Exception as err:  # noqa: BLE001
    report(False, "R7 Q8", f"ERROR {err!r}")
eq_hw("9", "b", area_abs(2 * s(2 * x), PI / 4, 3 * PI / 4), block=B7["9"], label="R7 Q9b")
eq_hw("10", "a", sp.integrate(c_(x), (x, 0, PI / 2)) - sp.integrate(c_(2 * x), (x, 0, PI / 4)), block=B7["10"], label="R7 Q10a")
report(sorted(sp.solveset(c_(x) - c_(2 * x), x, sp.Interval(0, PI)), key=float) == [0, 2 * PI / 3], "R7 Q10b curves meet at 0 and 2pi/3")
eq_hw("10", "b", sp.integrate(c_(x) - c_(2 * x), (x, 0, 2 * PI / 3)), block=B7["10"], label="R7 Q10b")
eq_hw("11", "b", sp.integrate(sp.tan(x), (x, 0, PI / 4)), block=B7["11"], label="R7 Q11b")
for p, f in (("a", ex(2 * x) * c_(ex(2 * x))), ("b", s(ex(-2 * x)) / ex(2 * x)), ("c", sp.sec(x) ** 2 / (3 * sp.tan(x) + 1)),
             ("d", 3 * s(x) / (4 + 5 * c_(x))), ("e", (1 - c_(x) ** 3) / (1 - s(x) ** 2))):
    prim(B7, "16", p, f, f"R7 Q16{p}")
eq_hw("16", "f", sp.integrate(s(x) * c_(x) ** 2, (x, 0, PI)), block=B7["16"], label="R7 Q16f")
report(sp.simplify(sp.tan(x) ** 3 - (sp.tan(x) * sp.sec(x) ** 2 - sp.tan(x))) == 0, "R7 Q17a identity")
prim(B7, "17", "b", sp.tan(x) ** 3, "R7 Q17b(i)")
try:
    t17 = re.findall(r"<b>ii</b> \\\((.*?)\\\)", B7["17"])[0]
    report(deriv_match(tex(t17), sp.tan(x) ** 5), "R7 Q17b(ii): derivative is tan^5 x", t17)
except Exception as err:  # noqa: BLE001
    report(False, "R7 Q17b(ii)", f"ERROR {err!r}")
eq_hw("18", "b", sp.integrate(1 - sp.tan(x), (x, 0, PI / 4)), block=B7["18"], label="R7 Q18b")
try:
    i19 = re.findall(r"<b>b</b> <b>i</b> \\\((.*?)\\\)", B7["19"])[0]
    report(close(tex(i19), sp.integrate(2 * c_(3 * x) * c_(2 * x), (x, 0, PI / 2))), "R7 Q19b(i) 6/5", i19)
    ii19 = re.findall(r"<b>ii</b> \\\((.*?)\\\)", B7["19"])
    report(close(tex(ii19[0]), sp.integrate(c_(3 * x) * c_(4 * x), (x, 0, PI))), "R7 Q19b(ii) 0", ii19[0])
    c19 = re.findall(r"<b>c</b> <b>i</b> \\\((.*?)\\\)", B7["19"])[0]
    report(deriv_match(tex(c19), c_(m_ * x) * c_(n_ * x), subs={m_: 2, n_: 5}) and deriv_match(tex(c19), c_(m_ * x) * c_(n_ * x), subs={m_: 4, n_: 1}),
           "R7 Q19c(i) (m = 2, n = 5 and m = 4, n = 1)", c19)
    report(deriv_match(tex(ii19[1]), c_(3 * x) ** 2, subs={m_: 3, n_: 3}) and "\\tfrac12x" in ii19[1], "R7 Q19c(ii) m = n = 3 (the key's '+ x' should be '+ x/2')", ii19[1])
except Exception as err:  # noqa: BLE001
    report(False, "R7 Q19", f"ERROR {err!r}")

print(f"\n{CNT[0]} checks, {len(FAILS)} failures")
sys.exit(1 if FAILS else 0)
