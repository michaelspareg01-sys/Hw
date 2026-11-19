"""Check of Lesson 17F (Y11 Ch 17 pack): The t-formulae.

Reads the PRINTED answers (data-k spans) in a_17f.html and questions in l17f.html. Each expression in
t is compared NUMERICALLY with the trigonometric expression it came from, by substituting
t = tan(theta/2) (or t = tan theta in Q2); exact values are compared with sympy's evaluation; every
equation is re-solved numerically on its stated domain (a fine scan for sign changes and tangencies,
so that a lost root x = pi is caught) and compared with the printed solution set; the identities set
in the exercise and the past papers are spot-checked numerically. The past-paper block is checked
(marks, time, labels, hints, MC keys, every MC option tested). Exit 1 on failure.
Run: python3 workspace/checks/y11ch17_17f.py
"""
import re
import sympy as sp
from y11ch17_common import (read, get, maths, tex, check, finish, x, al, th, pp_block, mc_key, num_equal)

L = read("l17f.html")
A = read("a_17f.html")
pi, s, c, t_ = sp.pi, sp.sin, sp.cos, sp.tan
d = lambda v: v * pi / 180
R = sp.Rational
sqrt = sp.sqrt
T = sp.Symbol("t")

for q in [r"\tan\theta+\cot\theta", r"\sin\theta+\cos\theta", r"\sin x-\sqrt3\cos x=\sqrt3", r"2\sin x-\cos x=1",
          r"\sin\theta\tan\tfrac12\theta=1-\cos\theta", r"\cos x-\sin x=-1", r"\sin\theta+\sqrt3\cos\theta=1", r"\sin\theta+2\cos\theta=2"]:
    check(q in L, f"question {q} printed")

def in_t(key, expr, half=True):
    """Printed expression in t equals expr(theta) with t = tan(theta/2) (half) or tan(theta)."""
    sv = get(A, key)
    if sv is None:
        return
    m = maths(sv).split("=")[-1]
    got = tex(m)
    tt = [v for v in got.free_symbols if v.name == "t"]
    sub = got.subs(tt[0], t_(th / 2) if half else t_(th)) if tt else got
    check(num_equal(sub, expr), f"{key}: printed {m}")

def val(key, expected):
    sv = get(A, key)
    if sv is None:
        return
    m = maths(sv).split("=")[-1]
    check(num_equal(tex(m), expected), f"{key}: printed {m} vs {expected}")

def roots(f, lo, hi, n=200000):
    """Numerical roots of f on [lo, hi]: sign changes and near-zeros, merged."""
    import math
    xs = [lo + (hi - lo) * i / n for i in range(n + 1)]
    out = []
    vals = []
    for v in xs:
        try:
            vals.append(f(v))
        except (ZeroDivisionError, ValueError):
            vals.append(None)
    for i, v in enumerate(xs):
        a = vals[i]
        if a is None:
            continue
        if abs(a) < 1e-9:
            out.append(v)
        elif i + 1 <= n and vals[i + 1] is not None and a * vals[i + 1] < 0:
            out.append(v)
    merged = []
    for r in out:
        if not merged or r - merged[-1] > 1e-3:
            merged.append(r)
    return merged

def printed_set(key, deg=False):
    sv = get(A, key)
    if sv is None:
        return None
    m = maths(sv)
    m = re.sub(r"^\s*\\?[a-zA-Z]+\s*=", "", m)
    parts = re.split(r",|\\text\{\s*or\s*\}", m)
    out = []
    for p_ in parts:
        p_ = p_.replace(r"\ ", "").strip()
        if not p_:
            continue
        v = float(tex(p_.replace(r"^\circ", "")))
        out.append(v * float(pi) / 180 if deg else v)
    return sorted(out)

def solset(key, f, lo, hi, deg=False, tol=1e-3):
    got = printed_set(key, deg)
    if got is None:
        return
    exp = roots(f, lo, hi)
    ok_ = len(got) == len(exp) and all(abs(a - b) < tol for a, b in zip(got, exp))
    check(ok_, f"{key}: printed {got} vs solved {exp}")

import math
in_t("d1a", t_(th) + 1 / t_(th)); val("d1b", c(d(30)))
check(num_equal((1 - t_(d(15)) ** 2) / (1 + t_(d(15)) ** 2), sqrt(3) / 2), "C1 demo b value")
in_t("y1a", s(th) + c(th)); val("y1b", 2 * t_(5 * pi / 12) / (1 + t_(5 * pi / 12) ** 2))
check(num_equal(s(th) / (1 + c(th)) + (1 + c(th)) / s(th), 2 / s(th)), "C2 demo identity")
check(num_equal(s(th) * t_(th / 2), 1 - c(th)), "C2 your turn identity")
solset("d3", lambda v: math.sin(v) - math.sqrt(3) * math.cos(v) - math.sqrt(3), 0, 2 * math.pi)
solset("y3", lambda v: 2 * math.sin(v) - math.cos(v) - 1, 0, 2 * math.pi, tol=6e-3)
for k, e in {"1a": s(th), "1b": c(th), "1c": t_(th), "1d": 1 / c(th), "1e": 1 - c(th), "1f": (1 - c(th)) / s(th)}.items():
    in_t(k, e)
for k, e in {"2a": c(2 * th), "2b": 1 - s(2 * th), "2c": t_(2 * th) + 1 / c(2 * th)}.items():
    in_t(k, e, half=False)
for k, e in {"3a": 2 * t_(d(10)) / (1 - t_(d(10)) ** 2), "3b": 2 * t_(d(10)) / (1 + t_(d(10)) ** 2), "3c": (1 - t_(d(10)) ** 2) / (1 + t_(d(10)) ** 2),
             "3d": 2 * t_(2 * x) / (1 + t_(2 * x) ** 2), "3e": 2 * t_(2 * x) / (1 - t_(2 * x) ** 2), "3f": (1 - t_(2 * x) ** 2) / (1 + t_(2 * x) ** 2)}.items():
    sv = get(A, k)
    if sv:
        check(num_equal(tex(maths(sv)), e), f"{k}: printed {maths(sv)}")
for k, e in {"4a": 2 * t_(d(15)) / (1 - t_(d(15)) ** 2), "4b": 2 * t_(d(15)) / (1 + t_(d(15)) ** 2), "4c": (1 - t_(d(75)) ** 2) / (1 + t_(d(75)) ** 2),
             "4d": 2 * t_(d(R(225, 2))) / (1 + t_(d(R(225, 2))) ** 2), "4e": (1 - t_(3 * pi / 8) ** 2) / (1 + t_(3 * pi / 8) ** 2),
             "4f": 2 * t_(11 * pi / 12) / (1 - t_(11 * pi / 12) ** 2)}.items():
    sv = get(A, k)
    if sv:
        for side in maths(sv).split("="):
            check(num_equal(tex(side), e), f"{k}: side {side}")
solset("6c", lambda v: math.cos(v) - math.sin(v) - 1, 0, 2 * math.pi)
solset("7b", lambda v: math.sqrt(3) * math.sin(v) + math.cos(v) - 1, 0, 2 * math.pi)
check(abs(float(t_(d(R(225, 2)))) - float(-sqrt(2) - 1)) < 1e-12, "8b ii other root = tan 112.5")
alpha = pi - sp.atan(R(1, 3))
val("10a", t_(2 * alpha)); val("10b", s(2 * alpha)); val("10c", c(2 * alpha)); val("10d", t_(alpha / 2))
for lhs, rhs in [(c(th) * (t_(th) - t_(th / 2)), t_(th / 2)), ((1 - c(2 * x)) / s(2 * x), t_(x)), ((1 - c(th)) / (1 + c(th)), t_(th / 2) ** 2),
                 ((1 + 1 / s(th)) * t_(th), (1 + t_(th / 2)) / (1 - t_(th / 2))), (t_(th) * t_(th / 2) / (t_(th) - t_(th / 2)), s(th)),
                 ((c(th) + s(th) - 1) / (c(th) - s(th) + 1), t_(th / 2)), ((t_(2 * al) + 1 / t_(al)) / (t_(2 * al) - t_(al)), 1 / t_(al) ** 2),
                 (t_(x / 2 + pi / 4) + t_(x / 2 - pi / 4), 2 * t_(x))]:
    check(num_equal(lhs, rhs), f"Q5 identity {lhs} = {rhs}")
X = t_(th) + 1 / c(th)
check(num_equal((X ** 2 - 1) / (X ** 2 + 1), s(th)), "Q12a")
y = sp.Symbol("y")
cx = (5 * c(y) - 3) / (5 - 3 * c(y))
check(num_equal((1 - cx) / (1 + cx), 4 * t_(y / 2) ** 2), "Q13")
# past papers
pp_block(L, A)
o1 = {"A": 1 / T, "B": (1 + T) / (1 - T), "C": (1 + T ** 2) ** 2 / (1 - T ** 2), "D": (1 + 2 * T - T ** 2) / (1 + T ** 2)}
e1 = (s(th) + 1) / c(th)
check([k for k, e in o1.items() if num_equal(e.subs(T, t_(th / 2)), e1)] == ["B"], "PP1 only B"); in_t("pp1", e1); mc_key(A, "PP 1", "B")
o2 = {"A": 2 * (T + 2) ** 2 / (1 - T ** 2), "B": (T + 4) ** 2 / (1 - T ** 2), "C": 2 * (T + 2) ** 2 / (1 + T ** 2), "D": (T + 4) ** 2 / (1 + T ** 2)}
e2 = 4 * s(th) + 3 * c(th) + 5
check([k for k, e in o2.items() if num_equal(e.subs(T, t_(th / 2)), e2)] == ["C"], "PP2 only C"); in_t("pp2", e2); mc_key(A, "PP 2", "C")
in_t("pp3a", (c(th) - 1) / s(th))
f3 = lambda v: (math.cos(v) - 1) / math.sin(v) + 1
solset("pp3b", f3, 1e-6, math.pi - 1e-6)  # tex reads N^\circ as radians
check(num_equal(1 / t_(x) + t_(x / 2), 1 / s(x)), "PP4 identity")
check(num_equal((s(th) + 1 - c(th)) / (s(th) - 1 + c(th)), (1 + t_(th / 2)) / (1 - t_(th / 2))), "PP5 identity")
check(num_equal((1 + c(x) + s(x)) / (1 - c(x) + s(x)), 1 / t_(x / 2)), "PP6 identity")
solset("pp7", lambda v: math.cos(v) - math.sin(v) + 1, 0, 2 * math.pi)
solset("pp8", lambda v: math.sin(v) + math.sqrt(3) * math.cos(v) - 1, 0, 2 * math.pi)
# PP9: nearest degree, so compare after rounding the solved roots
sv = printed_set("pp9")
if sv is not None:
    exp = [round(math.degrees(r)) for r in roots(lambda v: math.sin(v) + 2 * math.cos(v) - 2, 0, 2 * math.pi)]
    check(sorted(round(math.degrees(v)) for v in sv) == exp, f"PP9: printed {sv} vs {exp}")
finish("y11ch17_17f")
