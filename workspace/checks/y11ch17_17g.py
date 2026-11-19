"""Check of Lesson 17G and the Chapter 17 review (Y11 Ch 17 pack): Products to sums.

Reads the PRINTED answers (data-k spans) in a_17g.html and questions in l17g.html. Every printed
product-to-sum rewriting is compared NUMERICALLY with the product it came from (degrees converted to
radians); exact values are compared with sympy; every equation is re-solved numerically on its stated
domain (a fine scan for sign changes and tangencies) and compared with the printed solution set; the
identities set in the exercise, the review and the past papers are spot-checked numerically. The
review's values (inverse functions, exact values, compound and double angles, t-formulae) are each
recomputed. The past-paper block is checked (marks, time, labels, hints, MC keys, every MC option
tested). Exit 1 on failure. Run: python3 workspace/checks/y11ch17_17g.py
"""
import math
import re
import sympy as sp
from y11ch17_common import (read, get, maths, tex, check, finish, x, y, A as Asym, B as Bsym, al, th, pp_block, mc_key, num_equal)

L = read("l17g.html")
A = read("a_17g.html")
pi, s, c, t_ = sp.pi, sp.sin, sp.cos, sp.tan
d = lambda v: v * pi / 180
R = sp.Rational
sqrt = sp.sqrt

def side(key, i=-1):
    sv = get(A, key)
    return None if sv is None else maths(sv).split("=")[i]

def val(key, expected, i=-1):
    m = side(key, i)
    if m is None:
        return
    check(num_equal(tex(m), expected), f"{key}: printed {m} vs {expected}")

def chain(key, expected):
    """every side of a printed chain equals expected"""
    sv = get(A, key)
    if sv is None:
        return
    for part in maths(sv).split("="):
        check(num_equal(tex(part), expected), f"{key}: side {part}")

def roots(f, lo, hi, n=200000):
    xs = [lo + (hi - lo) * i / n for i in range(n + 1)]
    vals = []
    for v in xs:
        try:
            vals.append(f(v))
        except (ZeroDivisionError, ValueError):
            vals.append(None)
    out = []
    for i, v in enumerate(xs):
        a = vals[i]
        if a is None:
            continue
        if abs(a) < 1e-9:
            out.append(v)
        elif i < n and vals[i + 1] is not None and a * vals[i + 1] < 0 and abs(a - vals[i + 1]) < 1:
            out.append(v)
    merged = []
    for r in out:
        if not merged or r - merged[-1] > 1e-3:
            merged.append(r)
    return merged

def printed_set(key):
    sv = get(A, key)
    if sv is None:
        return None
    m = re.sub(r"^\s*\\?[a-zA-Z]+\s*=", "", maths(sv))
    parts = re.split(r",|\\text\{\s*or\s*\}", m)
    return sorted(float(tex(p_.replace(r"\ ", "").strip())) for p_ in parts if p_.replace(r"\ ", "").strip())

def solset(key, f, lo, hi, tol=1e-3):
    got = printed_set(key)
    if got is None:
        return
    exp = roots(f, lo, hi)
    check(len(got) == len(exp) and all(abs(a - b) < tol for a, b in zip(got, exp)), f"{key}: printed {got} vs solved {exp}")

for q in [r"2\cos5x\cos2x", r"\sin3x\sin x", r"2\sin6x\cos2x", r"\cos6x\cos2x", r"2\sin75^\circ\cos15^\circ", r"4\cos75^\circ\sin15^\circ",
          r"\cos3x+\cos x=0", r"\sin5x-\sin x=0", r"\cos7x-\cos3x=\sin5x", r"\sin x+\sin2x+\sin3x=0"]:
    check(q in L, f"question {q} printed")
# lesson examples
val("d1a", 2 * c(5 * x) * c(2 * x)); val("d1b", s(3 * x) * s(x)); val("y1a", 2 * s(6 * x) * c(2 * x)); val("y1b", c(6 * x) * c(2 * x))
val("d2a", 2 * s(d(75)) * c(d(15))); val("y2a", 4 * c(d(75)) * s(d(15)))
check(num_equal(2 * s(2 * x) * s(x) + c(3 * x), c(x)), "C2 demo b"); check(num_equal(2 * c(3 * x) * c(x) - c(4 * x), c(2 * x)), "C2 your turn b")
solset("d3", lambda v: math.cos(3 * v) + math.cos(v), 0, 2 * math.pi)
solset("y3", lambda v: math.sin(5 * v) - math.sin(v), 0, math.pi)
# exercise 17G
for k, e in {"1i": 2 * c(d(35)) * c(d(15)), "1ii": 2 * c(d(48)) * s(d(32)), "1iii": s(d(49)) * s(d(22)), "1iv": c(d(61)) * s(d(25)),
             "1v": 2 * s(3 * al) * c(al), "1vi": c(2 * th) * c(th), "1vii": 2 * s(x + y) * s(x - y), "1viii": s(2 * Asym + Bsym) * c(2 * Asym - Bsym)}.items():
    val(k, e)
for lhs, rhs in [(2 * c(d(75)) * c(d(15)), R(1, 2)), (2 * s(d(25)) * s(d(35)), c(d(10)) - R(1, 2)), (4 * s(d(40)) * c(d(10)), 1 + 2 * s(d(50))),
                 (2 * s(d(45)) * c(d(35)), c(d(10)) + s(d(10))), (2 * s(d(54)) * s(d(18)), s(d(54)) - s(d(18))), (4 * c(d(59)) * c(d(61)), 2 * c(d(2)) - 1),
                 (2 * s(3 * th) * c(2 * th) + 2 * c(6 * th) * s(th), s(7 * th) + s(th)), (2 * s(4 * al) * s(3 * al) + 2 * c(5 * al) * c(2 * al), c(3 * al) + c(al)),
                 (2 * c(d(40)) * c(d(20)) - 2 * s(d(25)) * s(d(5)), (sqrt(3) + 1) / 2), (2 * s(d(19)) * c(d(11)) + 2 * s(d(71)) * s(d(11)), 1),
                 (4 * c(4 * x) * c(2 * x) * c(x), c(7 * x) + c(5 * x) + c(3 * x) + c(x)), (4 * s(5 * al) * c(3 * al) * c(al), s(9 * al) + s(7 * al) + s(3 * al) + s(al)),
                 (8 * s(4 * pi / 9) * s(2 * pi / 9) * s(pi / 9), sqrt(3)), (c(4 * pi / 9) * c(2 * pi / 9) * c(pi / 9), R(1, 8)),
                 (2 * s(x) * (c(2 * x) + c(4 * x) + c(6 * x)), s(7 * x) - s(x)), (c(2 * pi / 7) + c(4 * pi / 7) + c(6 * pi / 7), -R(1, 2)),
                 (s(d(35)) + s(d(25)), s(d(85))), (c(d(36)) - c(d(84)), sqrt(3) * s(d(24))), ((s(3 * th) + s(th)) / (c(3 * th) + c(th)), t_(2 * th)),
                 ((s(6 * al) - s(4 * al) + s(2 * al)) / (c(6 * al) - c(4 * al) + c(2 * al)), t_(4 * al))]:
    check(num_equal(lhs, rhs), f"exercise identity {lhs} = {rhs}")
val("7bii", c(pi / 7) + c(3 * pi / 7) + c(5 * pi / 7))
n_ = 5
check(abs(sum(math.sin((2 * k - 1) * 0.7) for k in range(1, n_ + 1)) - math.sin(n_ * 0.7) ** 2 / math.sin(0.7)) < 1e-12, "Q9 n = 5")
solset("8", lambda v: math.sin(v) + 2 * math.cos(2 * v) * math.sin(v) - 0.5, 0, 2 * math.pi)
solset("12a", lambda v: math.sin(4 * v) - math.sin(2 * v), 0, 2 * math.pi)
solset("12b", lambda v: math.sin(7 * v) + math.sin(3 * v), 0, 2 * math.pi)
solset("12c", lambda v: math.cos(5 * v) + math.cos(3 * v), 0, 2 * math.pi)
solset("12d", lambda v: math.cos(3 * v) - math.cos(2 * v), 0, 2 * math.pi)
# past papers
pp_block(L, A)
def mc(pn, opts, expr, key, letter, k):
    good = [l for l, e in opts.items() if num_equal(e, expr)]
    check(good == [letter], f"{pn} only {letter} ({good})"); val(k, expr); mc_key(A, pn, letter)
mc("PP 1", {"A": 2 * s(4 * x) * c(x), "B": 2 * s(4 * x) * s(x), "C": 2 * c(4 * x) * s(x), "D": 2 * c(4 * x) * c(x)}, s(5 * x) + s(3 * x), "pp1", "A", "pp1")
mc("PP 2", {"A": c(7 * x) - s(9 * x), "B": c(3 * x) - s(3 * x), "C": s(8 * x) * s(x), "D": c(8 * x) * c(x)}, c(5 * x) * c(2 * x) - s(6 * x) * s(3 * x), "pp2", "D", "pp2")
mc("PP 3", {"A": -c(2 * x) - c(8 * x), "B": c(8 * x) - c(2 * x), "C": c(2 * x) - c(8 * x), "D": c(2 * x) + c(8 * x)}, 2 * s(3 * x) * s(5 * x), "pp3", "C", "pp3")
mc("PP 4", {"A": (s(5 * al) + s(al)) / 2, "B": (s(5 * al) - s(al)) / 2, "C": (s(5 * al / 2) + s(al / 2)) / 2, "D": (s(5 * al / 2) - s(al / 2)) / 2},
   c(3 * al) * s(2 * al), "pp4", "B", "pp4")
val("pp5", s(d(255)) * c(d(15)))
check(num_equal(4 * s(3 * x) * s(2 * x) * s(x), s(2 * x) + s(4 * x) - s(6 * x)), "PP6 identity")
check(num_equal(s(x) + s(3 * x), 2 * s(2 * x) * c(x)), "PP7 (i)")
solset("pp7", lambda v: math.sin(v) + math.sin(2 * v) + math.sin(3 * v), 0, 2 * math.pi)
check(num_equal((s(th) + s(3 * th) + s(5 * th)) / (c(th) + c(3 * th) + c(5 * th)), t_(3 * th)), "PP8 (i)")
def f8(v):
    den = math.cos(v) + math.cos(3 * v) + math.cos(5 * v)
    if abs(den) < 1e-9:
        raise ZeroDivisionError
    return (math.sin(v) + math.sin(3 * v) + math.sin(5 * v)) / den - 1
solset("pp8", f8, 0, 2 * math.pi)
solset("pp9", lambda v: math.cos(7 * v) - math.cos(3 * v) - math.sin(5 * v), 0, math.pi)
# chapter review
fx = lambda v: sp.S(v) / 2 + 1
check(sp.Interval(fx(-4), fx(6)) == sp.Interval(-1, 4), "R1a range"); check(r"-1\le f(x)\le4" in (get(A, "r1a") or ""), "R1a printed")
val("r1b", 2 * x - 2); check(num_equal((2 * x - 2).subs(x, fx(x)), x), "R1b inverse")
check(r"-1\le x\le4" in (get(A, "r1c") or "") and r"-4\le f^{-1}(x)\le6" in (get(A, "r1c") or ""), "R1c printed")
val("r2b", sp.exp(x) - 1); check(num_equal(sp.log(sp.exp(x) - 1 + 1), x), "R2b inverse")
val("r3c", 2 - sqrt(x)); check(all(abs((2 - math.sqrt(v) - 2) ** 2 - v) < 1e-12 for v in (0.5, 2, 7)), "R3c inverse on x <= 2")
for k, e in {"r4a": sp.asin(1), "r4b": sp.acos(sqrt(3) / 2), "r4c": sp.atan(sqrt(3)), "r4d": sp.atan(-1), "r4e": sp.acos(-R(1, 2)), "r4f": sp.asin(-R(1, 2)),
             "r5a": c(sp.acos(1)), "r5b": s(sp.atan(1)), "r5c": c(sp.atan(-sqrt(3))), "r5d": sp.atan(-t_(pi / 6)), "r5e": sp.acos(c(4 * pi / 3)),
             "r5f": sp.atan(-2 * s(2 * pi / 3)), "r6a": s(sp.acos(R(1, 3))), "r6b": c(sp.atan(-sqrt(7) / 3))}.items():
    val(k, e)
for k, e in {"r8a": c(3 * th) * c(th) + s(3 * th) * s(th), "r8b": s(d(50)) * c(d(10)) - c(d(50)) * s(d(10)),
             "r8c": (t_(d(41)) + t_(d(9))) / (1 - t_(d(41)) * t_(d(9))), "r8d": c(d(15)) * c(d(55)) - s(d(15)) * s(d(55)),
             "r8e": s(4 * al) * c(2 * al) + c(4 * al) * s(2 * al), "r8f": (1 + t_(2 * th) * t_(th)) / (t_(2 * th) - t_(th)),
             "r9a": 2 * s(2 * th) * c(2 * th), "r9b": c(x / 2) ** 2 - s(x / 2) ** 2, "r9c": 2 * c(3 * al) ** 2 - 1, "r9d": 2 * t_(d(35)) / (1 - t_(d(35)) ** 2),
             "r9e": 1 - 2 * s(d(25)) ** 2, "r9f": 2 * t_(4 * x) / (1 - t_(4 * x) ** 2)}.items():
    chain(k, e)
Aa, Bb = sp.asin(R(3, 5)), sp.acos(R(5, 13))
for k, e in {"r10a": c(Aa), "r10b": c(2 * Aa), "r10c": c(Aa + Bb), "r10d": s(2 * Bb), "r10e": t_(2 * Aa), "r10f": t_(Bb - Aa)}.items():
    val(k, e)
check(num_equal(s(d(75)), (sqrt(3) + 1) / (2 * sqrt(2))) and num_equal(c(d(75)), (sqrt(3) - 1) / (2 * sqrt(2))), "R11a")
for k, e in {"r12a": 2 * s(d(15)) * c(d(15)), "r12b": c(d(35)) * c(d(5)) + s(d(35)) * s(d(5)), "r12c": (t_(d(110)) + t_(d(25))) / (1 - t_(d(110)) * t_(d(25))),
             "r12d": 1 - 2 * s(pi / 8) ** 2, "r12e": c(pi / 12) * s(pi / 12), "r12f": s(8 * pi / 9) * c(2 * pi / 9) - c(8 * pi / 9) * s(2 * pi / 9)}.items():
    chain(k, e)
for lhs, rhs in [((s(al) - c(al)) ** 2, 1 - s(2 * al)), (c(Asym) - s(2 * Asym) * s(Asym), c(Asym) * c(2 * Asym)), (s(2 * th) * (t_(th) + 1 / t_(th)), 2),
                 (1 / t_(al) * s(2 * al) - c(2 * al), 1), (s(2 * x) / (1 + c(2 * x)), t_(x)), ((1 - t_(th) ** 2) / (1 + t_(th) ** 2), c(2 * th)),
                 (1 / (1 - t_(Asym)) - 1 / (1 + t_(Asym)), t_(2 * Asym)), (t_(2 * Asym) * (1 / t_(Asym) - t_(Asym)), 2),
                 (s(th) * t_(th / 2) + c(th), 1), (1 / s(th) - 1 / t_(th), t_(th / 2)), (s(2 * al) * (t_(2 * al) - t_(al)), t_(2 * al) * t_(al)),
                 ((c(2 * al) - s(2 * al) + 1) / (c(2 * al) + s(2 * al) - 1), 1 / t_(al)),
                 (2 * c(d(58)) * c(d(32)), c(d(26))), (2 * c(d(45)) * s(d(35)), c(d(10)) - s(d(10))), (2 * s(d(70)) * s(d(50)), R(1, 2) + c(d(20))),
                 (2 * s(d(55)) * c(d(40)), s(d(15)) + c(d(5))), (4 * c(5 * al) * c(2 * al) * s(al), s(8 * al) - s(6 * al) + s(4 * al) - s(2 * al)),
                 (4 * s(5 * th) * c(3 * th) * s(th), c(th) - c(3 * th) + c(7 * th) - c(9 * th))]:
    check(num_equal(lhs, rhs), f"review identity {lhs} = {rhs}")
# Q14: h/x from the two triangles, d = horizontal distance: tan a = h/d, tan 2a = (x - h)/d
aa = 0.31
dd = 5.0
hh = dd * math.tan(aa); xx = hh + dd * math.tan(2 * aa)
check(abs(hh / xx - (1 - math.tan(aa) ** 2) / (3 - math.tan(aa) ** 2)) < 1e-12, "R14b")
val("r15b", sp.atan(R(1, 2)) + sp.atan(R(1, 3)))
check(num_equal(sp.asin(1 / sqrt(5)) + sp.asin(1 / sqrt(10)), pi / 4), "R16a"); check(num_equal(sp.atan(R(1, 2)) - sp.atan(R(1, 4)), sp.atan(R(2, 9))), "R16b")
check(num_equal(2 * sp.asin(R(2, 3)), sp.asin(4 * sqrt(5) / 9)), "R17a"); check(num_equal(2 * sp.acos(1 / sqrt(5)), sp.acos(-R(3, 5))), "R17b")
solset("r18a", lambda v: math.sin(2 * v) + math.cos(v), 0, 2 * math.pi)
solset("r18b", lambda v: math.cos(2 * v) - math.sin(v), 0, 2 * math.pi)
solset("r18c", lambda v: 2 * math.cos(2 * v) + 8 * math.cos(v) + 5, 0, 2 * math.pi)
def f18d(v):
    if abs(math.cos(2 * v)) < 1e-9 or abs(math.cos(v)) < 1e-9:
        raise ZeroDivisionError
    return math.sin(2 * v) * math.cos(v) - 3 * math.sin(v) * math.cos(2 * v)  # tan2x - 3tan x times cos2x cos x
solset("r18d", f18d, 0, 2 * math.pi)
def in_t(key, expr):
    m = side(key)
    if m is None:
        return
    got = tex(m)
    tt = [v for v in got.free_symbols if v.name == "t"]
    sub = got.subs(tt[0], t_(th / 2)) if tt else got
    check(num_equal(sub, expr), f"{key}: printed {m}")
for k, e in {"r19a": s(th), "r19b": c(th), "r19c": t_(th), "r19d": 1 / c(th), "r19e": 1 + c(th), "r19f": s(th) / (1 + c(th))}.items():
    in_t(k, e)
T67 = t_(d(R(135, 2)))
chain("r20a", 2 * T67 / (1 - T67 ** 2)); chain("r20b", 2 * T67 / (1 + T67 ** 2)); chain("r20c", (1 - T67 ** 2) / (1 + T67 ** 2))
check(num_equal(t_(d(75)), 2 + sqrt(3)) and num_equal(t_(d(165)), -2 + sqrt(3)), "R22")
val("r23a", 2 * c(2 * Asym) * c(Asym)); val("r23b", 2 * c(5 * Asym) * s(3 * Asym))
val("r23c", 2 * s(3 * Asym + 2 * Bsym) * c(2 * Asym - Bsym)); val("r23d", 2 * s(2 * Asym + 5 * Bsym) * s(Asym + 3 * Bsym))
finish("y11ch17_17g")
