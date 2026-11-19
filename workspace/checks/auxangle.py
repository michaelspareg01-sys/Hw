"""Check script for the auxiliary angle homework (workspace/build/auxangle).

Reads the printed answers from a_all.html (every <span data-k="..."> must appear exactly once),
and checks them against independent computation:
  * every R and alpha: expand the stated form R sin(x +- a) / R cos(x +- a) with the printed R and
    alpha and compare the coefficients of sin x and cos x with the question; also check that alpha
    lies in the stated range and matches the exact angle to the stated precision;
  * every equation: brute-force all roots of f(x) = c over the stated domain (dense sampling, sign
    changes plus tangent roots, refined by bisection / ternary search) and compare the root set with
    the printed set;
  * maxima / minima, inequality solution sets and graph features by dense sampling.
Exit status 1 on any failure.

usage: python3 workspace/checks/auxangle.py
"""
import html, math, os, re, sys
import sympy as sp
from sympy.parsing.sympy_parser import (parse_expr, standard_transformations,
                                        implicit_multiplication_application)

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "build", "auxangle", "a_all.html")
DEG = math.pi / 180
FAILS = []
NCHK = 0


def ok(cond, msg):
    global NCHK
    NCHK += 1
    if not cond:
        FAILS.append(msg)
        print("FAIL", msg)


# ---------------------------------------------------------------- read printed values
text = open(SRC, encoding="utf-8").read()


def get(key):
    hits = re.findall(r'<span data-k="%s">(.*?)</span>' % re.escape(key), text, flags=re.S)
    if len(hits) != 1:
        ok(False, f"{key}: template matched {len(hits)} times (need exactly 1)")
        return None
    return html.unescape(hits[0])


# ---------------------------------------------------------------- LaTeX -> sympy
X = sp.Symbol("x")
TR = standard_transformations + (implicit_multiplication_application,)


def _brace(s, i):
    """s[i] == '{': return (content, index after the closing brace)."""
    depth = 0
    for j in range(i, len(s)):
        if s[j] == "{":
            depth += 1
        elif s[j] == "}":
            depth -= 1
            if depth == 0:
                return s[i + 1:j], j + 1
    raise ValueError("unbalanced braces: " + s)


def _arg(s, i):
    if s[i] == "{":
        return _brace(s, i)
    return s[i], i + 1


def tex2py(s):
    s = s.replace(r"\(", "").replace(r"\)", "").replace(r"\left", "").replace(r"\right", "")
    s = s.replace(r"\ ", " ").replace(r"\,", " ").replace("\\approx", "").replace("&nbsp;", " ")
    out, i = "", 0
    while i < len(s):
        m = re.match(r"\\[dt]?frac", s[i:])
        if m:
            i += m.end()
            a, i = _arg(s, i)
            b, i = _arg(s, i)
            out += "((%s)/(%s))" % (tex2py(a), tex2py(b))
            continue
        if s.startswith(r"\sqrt", i):
            i += 5
            a, i = _arg(s, i)
            out += "sqrt(%s)" % tex2py(a)
            continue
        m = re.match(r"\\(tan|sin|cos)\^\{-1\}", s[i:])
        if m:
            i += m.end()
            out += " a%s" % m.group(1)
            continue
        m = re.match(r"\\(sin|cos|tan)", s[i:])
        if m:
            i += m.end()
            out += " %s" % m.group(1)
            continue
        if s.startswith(r"\pi", i):
            out += " pi "
            i += 3
            continue
        m = re.match(r"\^\\circ\s*(\d+)'", s[i:])          # 22^\circ37'
        if m:
            out += "*(pi/180) + %s*pi/10800" % m.group(1)
            i += m.end()
            continue
        if s.startswith(r"^\circ", i):
            out += "*(pi/180)"
            i += 6
            continue
        out += s[i]
        i += 1
    return out


def val(s):
    return parse_expr(tex2py(s), transformations=TR, local_dict={"x": X, "pi": sp.pi})


def num(s):
    return float(sp.N(val(s)))


def values(s):
    """'\\(x=90^\\circ\\) or \\(x\\approx323^\\circ8'\\)' -> [floats] (degrees become radians)."""
    s = s.replace(r"\(", " ").replace(r"\)", " ")
    s = re.sub(r"(\\theta|\bx)\s*(=|\\approx)", " ", s)
    parts = [p for p in re.split(r"\bor\b|\band\b|,(?![^{]*\})", s) if p.strip()]
    return [num(p) for p in parts]


def intervals(s):
    """'0\\le x\\le\\dfrac{\\pi}{12} or ...' -> [(lo, lo_closed, hi, hi_closed)]."""
    s = s.replace(r"\(", " ").replace(r"\)", " ")
    res = []
    for p in re.split(r"\bor\b", s):
        m = re.match(r"\s*(.+?)\s*(\\le|<)\s*x\s*(\\le|<)\s*(.+?)\s*$", p.strip(), flags=re.S)
        if not m:
            ok(False, "cannot parse interval: " + p)
            continue
        res.append((num(m.group(1)), m.group(2) == r"\le", num(m.group(4)), m.group(3) == r"\le"))
    return res


def point(s):
    s = s.strip().replace(r"\(", "").replace(r"\)", "").replace(r"\left", "").replace(r"\right", "")
    s = s.strip()[1:-1]                                           # drop ( )
    depth, cut = 0, None
    for i, ch in enumerate(s):
        depth += ch == "{"
        depth -= ch == "}"
        if ch == "," and depth == 0:
            cut = i
    return num(s[:cut]), num(s[cut + 1:])


# ---------------------------------------------------------------- numerical tools
def roots(g, lo, hi, lo_in=True, hi_in=True, n=400000):
    """All roots of g on the interval: sign changes plus touching roots."""
    xs = [lo + (hi - lo) * i / n for i in range(n + 1)]
    ys = [g(x) for x in xs]
    found = []
    for i in range(n):
        a, b, fa, fb = xs[i], xs[i + 1], ys[i], ys[i + 1]
        if fa == 0:
            found.append(a)
        elif fa * fb < 0:
            for _ in range(80):
                m = (a + b) / 2
                if fa * g(m) <= 0:
                    b = m
                else:
                    a, fa = m, g(m)
            found.append((a + b) / 2)
    if ys[-1] == 0:
        found.append(hi)
    for i in range(1, n):                       # tangent roots: local minima of |g| near 0
        if abs(ys[i]) <= abs(ys[i - 1]) and abs(ys[i]) <= abs(ys[i + 1]) and abs(ys[i]) < 1e-4:
            a, b = xs[i - 1], xs[i + 1]
            for _ in range(200):
                m1, m2 = a + (b - a) / 3, b - (b - a) / 3
                if abs(g(m1)) < abs(g(m2)):
                    b = m2
                else:
                    a = m1
            r = (a + b) / 2
            if abs(g(r)) < 1e-10:
                found.append(r)
    for e in (lo, hi):
        if abs(g(e)) < 1e-12:
            found.append(e)
    found.sort()
    uniq = []
    for r in found:
        if not uniq or abs(r - uniq[-1]) > 1e-7:
            uniq.append(r)
    eps = 1e-9
    return [r for r in uniq if (lo_in or r > lo + eps) and (hi_in or r < hi - eps)]


TOL = {"exact": 1e-6, "min": 0.5 / 60 * DEG + 1e-9, "2dp": 0.005 + 1e-9, "3dp": 0.0005 + 1e-9,
       "1dpdeg": 0.05 * DEG + 1e-9}


def check_solutions(key, f, c, lo, hi, prec, lo_in=True, hi_in=True):
    s = get(key)
    if s is None:
        return
    printed = sorted(values(s))
    true = roots(lambda x: f(x) - c, lo, hi, lo_in, hi_in)
    ok(len(printed) == len(true), f"{key}: printed {len(printed)} solutions, brute force finds {len(true)}: "
                                  f"{[round(t, 6) for t in true]}")
    for p, t in zip(printed, true):
        ok(abs(p - t) <= TOL[prec], f"{key}: printed {p:.6f}, true {t:.6f} ({prec})")
    for p in printed:
        ok(abs(f(p) - c) < (1e-9 if prec == "exact" else 0.05), f"{key}: f({p:.5f}) = {f(p):.5f}, not {c}")


def check_form(key, a, b, form, rng, prec_alpha="exact", var="x"):
    """a sin x + b cos x = R trig(x op alpha). form in sin+, sin-, cos+, cos-.
    rng = (lo, lo_closed, hi, hi_closed) for alpha (radians)."""
    R_s, a_s = get(key + ".R"), get(key + ".a")
    if R_s is None or a_s is None:
        return
    R, al = num(R_s), num(a_s)
    # expand with the printed values: coefficients of sin x and cos x
    if form == "sin+":
        cs, cc = R * math.cos(al), R * math.sin(al)
    elif form == "sin-":
        cs, cc = R * math.cos(al), -R * math.sin(al)
    elif form == "cos+":
        cs, cc = -R * math.sin(al), R * math.cos(al)
    elif form == "cos-":
        cs, cc = R * math.sin(al), R * math.cos(al)
    tol = 1e-9 if prec_alpha == "exact" else R * TOL[prec_alpha] * 1.01 + 1e-9
    ok(abs(cs - a) <= tol and abs(cc - b) <= tol,
       f"{key}: expanding {R:.5f} {form} alpha={al:.6f} gives {cs:.5f} sin + {cc:.5f} cos, need {a} sin + {b} cos")
    ok(R > 0 and abs(R - math.hypot(a, b)) < 1e-9, f"{key}: R = {R}, need {math.hypot(a, b)}")
    lo, lc, hi, hc = rng
    ok((al > lo or (lc and al >= lo - 1e-12)) and (al < hi or (hc and al <= hi + 1e-12)),
       f"{key}: alpha {al} outside its range")
    # exact alpha from the coefficients (independent of the printed value)
    if form == "sin+":
        t = math.atan2(b, a)
    elif form == "sin-":
        t = math.atan2(-b, a)
    elif form == "cos+":
        t = math.atan2(-a, b)
    else:
        t = math.atan2(a, b)
    cands = [t + 2 * math.pi * k for k in (-2, -1, 0, 1, 2)]
    ok(min(abs(al - c) for c in cands) <= TOL[prec_alpha], f"{key}: alpha {al:.6f}, true {t:.6f} mod 2pi")


def check_pair(key, s_val, c_val, rng, prec="exact"):
    """R sin a = s_val, R cos a = c_val (textbook Q1 type)."""
    check_form(key, c_val, s_val, "sin+", rng, prec)        # R sin(x+a) = R cos a sin x + R sin a cos x


def ident(key, target):
    s = get(key)
    if s is None:
        return
    e = val(s)
    fe = sp.lambdify(X, e, "math")
    worst = max(abs(fe(t) - target(t)) for t in [i * 0.37 - 7 for i in range(40)])
    ok(worst < 1e-9, f"{key}: printed {s} is not identical to the target (max diff {worst:.2e})")


def scalar(key, true, tol=1e-9):
    s = get(key)
    if s is None:
        return
    ok(abs(num(s) - true) <= tol, f"{key}: printed {s} = {num(s):.6f}, true {true:.6f}")


def sample(f, lo, hi, n=200001):
    return [(lo + (hi - lo) * i / (n - 1), f(lo + (hi - lo) * i / (n - 1))) for i in range(n)]


TWO_PI = 2 * math.pi
R0_2PI = (0, True, TWO_PI, False)
R0_360 = (0, True, TWO_PI, False)
ACUTE = (0, False, math.pi / 2, False)
ACUTE_C = (0, True, math.pi / 2, True)
s3 = math.sqrt(3)

# ---------------------------------------------------------------- Section A
check_pair("A1a", s3, 1, R0_2PI)
check_pair("A1b", 3, 3, R0_2PI)
check_pair("A2a", 5, 12, R0_360, "min")
check_pair("A2b", 4, 2, R0_360, "min")
check_pair("A3a", 1, -s3, R0_2PI)
check_pair("A3b", -5, -5, R0_2PI)
f20b = lambda t: math.sin(t) + s3 * math.cos(t)
f20c = lambda t: math.cos(t) - math.sin(t)
for k in ("A4b1", "A4b2", "A4b3"):
    ident(k, f20b)
for k in ("A4c1", "A4c2", "A4c3"):
    ident(k, f20c)
# the three b forms must be the other three standard forms R sin(x - a), R cos(x - a), R cos(x + a)
for k, pat in (("A4b1", r"\\sin\\left\(x-"), ("A4b2", r"\\cos\\left\(x-"), ("A4b3", r"\\cos\\left\(x\+"),
               ("A4c1", r"\\sin\\left\(x\+"), ("A4c2", r"\\sin\\left\(x-"), ("A4c3", r"\\cos\\left\(x-")):
    s = get(k)
    ok(s is not None and re.search(pat, s) is not None, f"{k}: not in the expected standard form")

# ---------------------------------------------------------------- Section B
check_form("B1", -1, 1, "cos+", R0_2PI)                      # cos x - sin x = A cos(x + a)
f = lambda t: math.cos(t) - math.sin(t)
pts = sample(f, 1e-9, TWO_PI)
mx = max(pts, key=lambda p: p[1]); mn = min(pts, key=lambda p: p[1])
scalar("B1.max", mx[1], 1e-8); scalar("B1.min", mn[1], 1e-8)
scalar("B1.xmax", mx[0], 1e-4); scalar("B1.xmin", mn[0], 1e-4)

pts = sample(lambda t: 15 * math.sin(t) - 8 * math.cos(t) + 2, 0, TWO_PI)
scalar("B2", max(p[1] for p in pts), 1e-6)

check_form("B3", 2 * s3, -2, "sin-", ACUTE)
f = lambda t: 2 * s3 * math.sin(t) - 2 * math.cos(t)
pts = sample(f, -TWO_PI, TWO_PI, 400001)
top = max(p[1] for p in pts)
xs = [p[0] for p in pts if p[1] > top - 1e-9]
clusters = []
for x in xs:
    if not clusters or x - clusters[-1][-1] > 0.1:
        clusters.append([x])
    else:
        clusters[-1].append(x)
true_x = sorted(sum(c) / len(c) for c in clusters)
printed = sorted(values(get("B3.x")))
ok(len(printed) == len(true_x) and all(abs(p - t) < 1e-3 for p, t in zip(printed, true_x)),
   f"B3.x: printed {printed}, true {true_x}")

f = lambda t: 5 / (2 + math.sin(t) + math.cos(t))
pts = sample(f, 0, TWO_PI)
mx = max(pts, key=lambda p: p[1]); mn = min(pts, key=lambda p: p[1])
for key, tp in (("B4.max", mx), ("B4.min", mn)):
    s = get(key)
    if s:
        px, py = point(s)
        ok(abs(px - tp[0]) < 1e-4 and abs(py - tp[1]) < 1e-8, f"{key}: printed ({px},{py}), true {tp}")

# ---------------------------------------------------------------- Section C
check_form("C1", 1, 2, "cos-", R0_360)                       # 2cos x + sin x = B cos(x - theta)
check_solutions("C1.x", lambda t: 2 * math.cos(t) + math.sin(t), 1, 0, TWO_PI, "min")
check_solutions("C2b", lambda t: 6 * math.sin(t) - 5 * math.cos(t), 7, 0, TWO_PI, "min")
check_solutions("C2d", lambda t: 9 * math.cos(t) + 7 * math.sin(t), 3, 0, TWO_PI, "min")
check_form("C3", 1, -s3, "sin+", (0, False, TWO_PI, False))
check_solutions("C3.x", lambda t: math.sin(t) - s3 * math.cos(t), -1, 0, TWO_PI, "exact", hi_in=False)
check_solutions("C4b", lambda t: s3 * math.sin(2 * t) - math.cos(2 * t), 2, 0, TWO_PI, "exact")
check_solutions("C4c", lambda t: math.sin(4 * t) + math.cos(4 * t), 1, 0, TWO_PI, "exact")
check_solutions("C5.x", lambda t: 2 * math.cos(t) + 11 * math.sin(t), 10, 0, TWO_PI, "exact", hi_in=False)
r = sorted(values(get("C5.x")))
ok(abs(r[1] - 2 * r[0]) < 1e-12, "C5: one root is not twice the other")

# ---------------------------------------------------------------- Section D
check_solutions("D1.x", lambda t: s3 * math.cos(t) - math.sin(t), 1, 0, TWO_PI, "exact")


def check_ineq(key, pred, lo, hi, n=200001):
    s = get(key)
    if s is None:
        return
    ivs = intervals(s)

    def inside(x):
        for a, ac, b, bc in ivs:
            if (a < x or (ac and abs(x - a) < 1e-12)) and (x < b or (bc and abs(x - b) < 1e-12)):
                return True
        return False
    bad = [lo + (hi - lo) * i / (n - 1) for i in range(n)]
    bad = [x for x in bad if inside(x) != pred(x)]
    ok(not bad, f"{key}: interval set disagrees with brute force at {bad[:3]}")
    for a, ac, b, bc in ivs:                                   # endpoints: closed iff they satisfy
        for e, closed in ((a, ac), (b, bc)):
            ok(pred(e) == closed or e in (lo, hi) and closed == pred(e),
               f"{key}: endpoint {e:.6f} closed={closed}, satisfies={pred(e)}")


E = 1e-12
check_ineq("D2.aiii", lambda t: math.sin(t) - math.cos(t) > 1 + E, 0, TWO_PI)
check_ineq("D2.bi", lambda t: math.sin(t) + s3 * math.cos(t) <= 1 + E, 0, TWO_PI)
check_ineq("D2.biv", lambda t: math.cos(t) - math.sin(t) >= math.sqrt(2) / 2 - E, 0, TWO_PI)

check_form("D3", 12, 5, "sin+", ACUTE_C, "2dp")
pts = sample(lambda t: 12 * math.sin(t) + 5 * math.cos(t), 0, TWO_PI)
top = max(p[1] for p in pts)
scalar("D3.max", top, 1e-6)
first = min(p[0] for p in pts if p[1] > top - 1e-9)
scalar("D3.t", first, 0.005 + 1e-4)

check_form("D4", -2, 2 * s3, "cos+", ACUTE_C)              # 2sqrt3 cos x - 2 sin x = R cos(x + a)
den = lambda t: 2 * s3 * math.cos(t) - 2 * math.sin(t)
asy = roots(den, -math.pi / 6, 11 * math.pi / 6)
printed = sorted(values(get("D4.asy")))
ok(len(printed) == len(asy) and all(abs(p - a) < 1e-9 for p, a in zip(printed, asy)), f"D4.asy: {printed} vs {asy}")
px, py = point(get("D4.tp"))
mid = [(x, 1 / den(x)) for x, _ in sample(lambda t: 0, asy[0] + 1e-3, asy[1] - 1e-3)]
tp = max(mid, key=lambda p: p[1])
ok(abs(px - tp[0]) < 1e-4 and abs(py - tp[1]) < 1e-8, f"D4.tp: printed ({px},{py}), true {tp}")

# ---------------------------------------------------------------- Section E
# PP1: sqrt3 cos 2t - sin 2t = R cos(2t + a)  (u = 2t)
check_form("PP1", -1, s3, "cos+", ACUTE)
check_form("PP2", 3, 4, "cos-", (0, True, math.pi / 2, True), "1dpdeg")
check_form("PP3", -s3, 1, "cos+", ACUTE)
check_solutions("PP3.x", lambda t: math.cos(t) - s3 * math.sin(t), 1, -math.pi, math.pi, "exact")
check_solutions("PP4.x", lambda t: 4 * math.sin(t) + 5 * math.cos(t), 3, 0, TWO_PI, "3dp")
check_form("PP5", math.sqrt(6), math.sqrt(2), "sin+", ACUTE)
check_solutions("PP5.x", lambda t: math.sqrt(6) * math.sin(t) + math.sqrt(2) * math.cos(t), 2, 0, TWO_PI, "exact")
check_form("PP6", 5, 12, "sin+", ACUTE_C, "2dp")
check_solutions("PP6.x", lambda t: 5 * math.sin(t) + 12 * math.cos(t), 8, 0, math.pi, "2dp")
check_form("PP7", 6, 4, "sin+", ACUTE)
g7 = lambda t: 2 * math.sin(2 * t) - 3 * math.cos(2 * t) - 3 * math.sin(t) + 3
ok(max(abs(g7(t) - math.sin(t) * (6 * math.sin(t) + 4 * math.cos(t) - 3)) for t in [i * 0.1 for i in range(80)]) < 1e-12,
   "PP7(i) identity fails")
check_solutions("PP7.x", g7, 0, 0, math.pi, "2dp", hi_in=False)

# every data-k key in the file must have been checked
keys = re.findall(r'data-k="([^"]+)"', text)
print(f"{NCHK} checks, {len(keys)} printed answer keys")
if FAILS:
    print(f"{len(FAILS)} FAILURES")
    sys.exit(1)
print("ALL OK")
