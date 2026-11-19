"""Shared helpers for the Y11 Ch 17 (Further trigonometry) check scripts.

Printed values are marked in the HTML fragments with <span data-k="KEY">...</span> (answers) or
data-q/data-id spans (questions and identities in the lesson). A helper finds the span with the
given key, which must occur EXACTLY ONCE (missing or repeated -> FAIL), and returns its printed
TeX. TeX is turned into sympy by int3_tex.tex (extended here with cot, cosec and a few relations).
The expected values are always computed independently in the check script, never read from HTML.
"""
import os
import re
import sys

import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import int3_tex  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.environ.get("Y11CH17_SRC", os.path.join(HERE, "..", "build", "y11ch17"))
x = int3_tex.x
t, y, A, B, th, al, be, k, n, a, b = sp.symbols("t y A B theta alpha beta k n a b", real=True)
EXTRA = {"t": t, "y": y, "A": A, "B": B, "theta": th, "alpha": al, "beta": be, "k": k, "n": n,
         "a": a, "b": b, "cot": sp.cot, "csc": sp.csc, "sec": sp.sec, "phi": sp.Symbol("phi", real=True)}
int3_tex.FUNCS.update({"cot": "cot", "cosec": "csc", "csc": "csc"})
int3_tex.GREEK.update({"beta": "beta", "phi": "phi"})

FAILS, NOK = [], [0]


def ok(label):
    NOK[0] += 1
    print("OK   " + label)


def fail(label):
    FAILS.append(label)
    print("FAIL " + label)


def check(cond, label):
    (ok if cond else fail)(label)


def read(name):
    with open(os.path.join(SRC, name), encoding="utf-8") as f:
        return f.read().replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")


def clean(s):
    s = s.replace("\\operatorname{cosec}", "\\cosec").replace("\\,", "").replace("\\!", "")
    s = re.sub(r"\\(?:displaystyle|left|right|Big|big|bigg|Bigg)", "", s)
    return s.strip()


def spans(html, attr="data-k"):
    """All (key, inner) pairs for <span attr="key">inner</span> (no nested spans inside)."""
    return re.findall(r'<span ' + attr + r'="([^"]+)">(.*?)</span>', html, flags=re.S)


def get(html, key, attr="data-k"):
    found = [v for kk, v in spans(html, attr) if kk == key]
    if len(found) != 1:
        fail(f"{key}: printed value found {len(found)} times (need exactly 1)")
        return None
    return found[0]


def maths(s):
    """Strip \\( \\) and return the TeX inside (first maths chunk if several)."""
    m = re.findall(r"\\\((.*?)\\\)", s, flags=re.S)
    return clean(m[0]) if m else clean(s)


def all_maths(s):
    return [clean(m) for m in re.findall(r"\\\((.*?)\\\)", s, flags=re.S)]


def tex(s):
    return int3_tex.tex(clean(s), EXTRA)


def num_equal(e1, e2, subs_list=None, tol=1e-9):
    """Compare two sympy expressions numerically at sample points (or exactly if constant)."""
    e1, e2 = sp.sympify(e1), sp.sympify(e2)
    free = sorted((e1.free_symbols | e2.free_symbols), key=str)
    if not free:
        return abs(complex(sp.N(e1 - e2, 30))) < tol
    import random
    rnd = random.Random(17)
    good = 0
    for _ in range(40):
        pt = {s: sp.Rational(rnd.randint(-300, 300), 211) for s in free}
        if subs_list:
            pt.update(subs_list)
        try:
            v1, v2 = complex(sp.N(e1.subs(pt), 25)), complex(sp.N(e2.subs(pt), 25))
        except (TypeError, ValueError, ZeroDivisionError):
            continue
        if any(map(lambda z: z != z or abs(z) > 1e12, (v1, v2))) or abs(v1.imag) > 1e-12 or abs(v2.imag) > 1e-12:
            continue
        if abs(v1 - v2) > tol * max(1, abs(v1)):
            return False
        good += 1
    return good >= 5


def value(html, key, expected, label=None, attr="data-k"):
    """Printed value (single expression) equals the independently computed expected value."""
    s = get(html, key, attr)
    if s is None:
        return
    try:
        got = tex(maths(s))
    except Exception as e:  # noqa: BLE001
        fail(f"{label or key}: cannot parse {maths(s)!r} ({e})")
        return
    check(num_equal(got, expected), f"{label or key}: printed {maths(s)} vs {sp.nsimplify(expected) if not isinstance(expected, sp.Basic) or expected.is_number else expected}")


def rhs(s):
    """Right-hand side of the last '=' at top level of a printed equation."""
    parts = int3_tex.split_top(s, "=")
    return parts[-1]


def eq_value(html, key, expected, label=None, attr="data-k"):
    """Printed chain 'a = b = ... = value': every top-level side after the first, and the first too
    when it parses as an expression, equals expected."""
    s = get(html, key, attr)
    if s is None:
        return
    m = maths(s)
    parts = int3_tex.split_top(m, "=")
    vals = []
    for i, p in enumerate(parts):
        if i == 0 and len(parts) > 1 and re.match(r"^\s*[fgFGhy]\s*(\^\{-1\})?\s*(\(|$)", p):
            continue
        try:
            v = tex(p)
            if i == 0 and len(parts) > 1 and v.free_symbols and not sp.sympify(expected).free_symbols:
                continue
            vals.append(v)
        except Exception as e:  # noqa: BLE001
            if i == 0:
                continue
            fail(f"{label or key}: cannot parse {p!r} in {m!r} ({e})")
            return
    if i == 0 and len(parts) == 1:
        pass
    check(len(vals) >= 1 and all(num_equal(v, expected) for v in vals), f"{label or key}: printed {m} vs {expected}")


def identity(html, key, label=None, attr="data-id", subs=None, dom=None):
    """A printed identity 'L = R' (top-level '=' split) holds numerically at random points in dom."""
    s = get(html, key, attr)
    if s is None:
        return
    m = maths(s)
    parts = int3_tex.split_top(m, "=")
    if len(parts) < 2:
        fail(f"{label or key}: not an equation: {m}")
        return
    try:
        exprs = [tex(p) for p in parts]
    except Exception as e:  # noqa: BLE001
        fail(f"{label or key}: cannot parse {m!r} ({e})")
        return
    good = all(num_equal(exprs[0], e) for e in exprs[1:])
    check(good, f"{label or key}: identity {m}")


def number_set(html, key, expected, label=None, attr="data-k"):
    """Printed list of solutions (all maths chunks inside the span, split at commas and 'or')
    equals the expected set (sympy numbers)."""
    s = get(html, key, attr)
    if s is None:
        return
    chunks = []
    for m in all_maths(s):
        for part in re.split(r",|\\text\{ or \}|\\quad|\\ \\text\{or\}\\ |\\;\\text\{or\}\\;", m):
            part = part.strip()
            if not part:
                continue
            if "=" in part:
                part = rhs(part)
            chunks.append(part)
    try:
        got = sorted(float(sp.N(tex(c))) for c in chunks)
    except Exception as e:  # noqa: BLE001
        fail(f"{label or key}: cannot parse {chunks} ({e})")
        return
    exp = sorted(float(sp.N(v)) for v in expected)
    check(len(got) == len(exp) and all(abs(p - q) < 1e-6 for p, q in zip(got, exp)),
          f"{label or key}: printed {chunks} vs {exp}")


def finish(name):
    print(f"\n{name}: {NOK[0]} OK, {len(FAILS)} FAIL")
    if FAILS:
        for f in FAILS:
            print("  FAIL:", f)
        sys.exit(1)
