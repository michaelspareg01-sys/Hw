"""Shared helpers for the y11ch6 checks: read printed values from the HTML, turn the pack's LaTeX
into sympy, and find every solution of an equation on a domain by brute-force scanning."""
import os, re, sys, math, random
import sympy as sp
from sympy.parsing.latex import parse_latex

ROOT = os.environ.get("Y11CH6_SRC", os.path.join(os.path.dirname(__file__), "..", "build", "y11ch6"))
FAILS, OKS = [], [0]


def read(name):
    with open(os.path.join(ROOT, name), encoding="utf-8") as f:
        return f.read()


def spans(html, attr):
    """{key: inner text} for every <span ATTR="key">...</span>; a key printed twice is a FAIL."""
    out = {}
    for m in re.finditer(r'<span %s="([\w-]+)"[^>]*>(.*?)</span>' % attr, html, re.S):
        if m.group(1) in out:
            fail(f"{attr}={m.group(1)} printed more than once")
        out[m.group(1)] = m.group(2)
    return out


def need(d, key, what=""):
    if key not in d:
        fail(f"missing {what} {key}")
        return None
    return d[key]


def ok(msg=""):
    OKS[0] += 1


def fail(msg):
    FAILS.append(msg)
    print("FAIL", msg)


def check(cond, msg):
    ok() if cond else fail(msg)


def finish(name):
    print(f"{name}: {OKS[0]} OK, {len(FAILS)} FAIL")
    sys.exit(1 if FAILS else 0)


def tex(s):
    """Pack LaTeX (one \\( \\) group) -> sympy expression (degrees become radians)."""
    s = s.strip().replace("\\)<br>\\(", "").replace("\\qquad", "").replace("\\quad", "")
    s = re.sub(r"^\\\(|\\\)$", "", s).strip()
    s = re.sub(r"\\operatorname\{cosec\}(?=[A-Za-z])", r"\\csc ", s).replace(r"\operatorname{cosec}", r"\csc").replace(r"\dfrac", r"\frac").replace(r"\tfrac", r"\frac")
    s = s.replace(r"\,(", r"\cdot(").replace(r"\,", " ").replace(r"\left", "").replace(r"\right", "").replace(r"\!", "")
    s = re.sub(r"(\d+(?:\.\d+)?)\^\\circ", r"(\1\\cdot\\frac{\\pi}{180})", s)
    s = re.sub(r"\\sqrt(\d+)", r"\\sqrt{\1}", s)
    s = re.sub(r"\\frac(\d)(\d)", r"\\frac{\1}{\2}", s)
    g = r"(?:\\alpha|\\beta|\\gamma|\\delta|\\theta|\\phi|[A-Za-z])"
    s = re.sub(r"\\(sin|cos|tan|csc|sec|cot)(\^\{?\d\}?)?\s*(" + g + r")(?![A-Za-z])", r"\\\1\2(\3)", s)
    return parse_latex(s).subs(sp.Symbol('pi'), sp.pi)


def num_equal(a, b, trials=40, tol=1e-7):
    """True if sympy expressions a and b agree at random points (both defined)."""
    syms = sorted((a.free_symbols | b.free_symbols) - {sp.pi}, key=str)
    fa, fb = sp.lambdify(syms, a, "math"), sp.lambdify(syms, b, "math")
    good = 0
    rnd = random.Random(12345)
    for _ in range(trials * 5):
        vals = [rnd.uniform(-3, 3) for _ in syms]
        try:
            x, y = float(fa(*vals)), float(fb(*vals))
        except (ZeroDivisionError, ValueError, OverflowError):
            continue
        if abs(x) > 1e4 or abs(y) > 1e4:
            continue
        if abs(x - y) > tol * max(1, abs(x)):
            return False
        good += 1
        if good >= trials:
            return True
    return good > 5


def roots_deg(f, lo, hi, step=0.005, tol=1e-9):
    """All x in [lo, hi] (degrees) with f(x) = 0: sign changes (not poles) plus touching zeros, refined."""
    def F(x):
        try:
            v = f(x)
            return v if math.isfinite(v) else None
        except (ZeroDivisionError, ValueError, OverflowError):
            return None
    n = int(round((hi - lo) / step))
    xs = [lo + i * step for i in range(n + 1)]
    vs = [F(x) for x in xs]
    found = []

    def add(r):
        if lo - 1e-6 <= r <= hi + 1e-6 and all(abs(r - q) > 1e-4 for q in found):
            found.append(r)
    for i in range(n + 1):
        if vs[i] is not None and abs(vs[i]) < 1e-12:
            add(xs[i])
    for i in range(n):
        a, b, fa, fb = xs[i], xs[i + 1], vs[i], vs[i + 1]
        if fa is None or fb is None:
            continue
        if fa * fb < 0 and abs(fa) < 1 and abs(fb) < 1:          # skip jumps across a pole
            for _ in range(80):
                m = (a + b) / 2; fm = F(m)
                if fm is None: break
                if fa * fm <= 0: b, fb = m, fm
                else: a, fa = m, fm
            add((a + b) / 2)
    for i in range(1, n):                                         # touching zeros: local min of |f|
        if None in (vs[i - 1], vs[i], vs[i + 1]):
            continue
        if abs(vs[i]) < 1e-4 and abs(vs[i]) <= abs(vs[i - 1]) and abs(vs[i]) <= abs(vs[i + 1]):
            a, b = xs[i - 1], xs[i + 1]
            for _ in range(100):                                  # golden-section on |f|
                m1, m2 = a + (b - a) * 0.382, a + (b - a) * 0.618
                if abs(F(m1)) < abs(F(m2)): b = m2
                else: a = m1
            r = (a + b) / 2
            if abs(F(r)) < 1e-9:
                add(r)
    return sorted(found)


def parse_angles(s):
    """'60^\\circ, 120^\\circ' or '5^\\circ44'' -> list of degrees (minutes allowed). Returns [] for 'no solutions'."""
    s = re.sub(r"\\\(|\\\)", "", s)
    s = s.replace("\\circ", "°").replace("{}", "").replace("^", "").replace("−", "-").replace("\\prime", "'")
    out = []
    for m in re.finditer(r"(-?\d+(?:\.\d+)?)\s*°\s*(?:(\d+)\s*')?", s):
        d = float(m.group(1)); mi = float(m.group(2) or 0)
        out.append(d - mi / 60 if d < 0 or m.group(1).startswith("-") else d + mi / 60)
    return out
