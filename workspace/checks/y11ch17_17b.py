"""Check of Lesson 17B (Y11 Ch 17 pack): Defining the inverse trigonometric functions.

Reads the PRINTED answers (data-k spans) in workspace/build/y11ch17/a_17b.html and the printed
questions in l17b.html, and recomputes every value independently with sympy's asin/acos/atan and
trigonometric evaluation (exact values compared symbolically and numerically; decimals recomputed
and rounded; graph-reading values within 0.01 of the true value); ranges are recomputed with
sympy function_range. The question expressions are typed here from the book and checked to be
printed in the lesson. The past-paper block is checked for marks, time, labels, hints and MC keys,
and each MC key is confirmed by testing every option numerically.
Exit 1 on any failure. Run: python3 workspace/checks/y11ch17_17b.py
"""
import math
import sympy as sp
from sympy.calculus.util import function_range
from y11ch17_common import (read, get, maths, tex, check, finish, x, eq_value, set_value, pp_block, mc_key,
                            num_equal, interval, value)

L = read("l17b.html")
A = read("a_17b.html")
pi = sp.pi
I = sp.Interval
asin, acos, atan, sin, cos, tan, sqrt = sp.asin, sp.acos, sp.atan, sp.sin, sp.cos, sp.tan, sp.sqrt
R = sp.Rational

# ---- lesson examples (question text printed, values recomputed)
Qs = {
    "d1bi": (r"\sin^{-1}\dfrac{\sqrt3}{2}", asin(sqrt(3) / 2)), "d1bii": (r"\cos^{-1}\dfrac{1}{\sqrt2}", acos(1 / sqrt(2))),
    "d1biii": (r"\tan^{-1}\sqrt3", atan(sqrt(3))), "y1bi": (r"\sin^{-1}\dfrac{1}{\sqrt2}", asin(1 / sqrt(2))),
    "y1bii": (r"\cos^{-1}\dfrac{\sqrt3}{2}", acos(sqrt(3) / 2)), "y1biii": (r"\tan^{-1}\dfrac{1}{\sqrt3}", atan(1 / sqrt(3))),
    "d3a": (r"\cos^{-1}\Big(-\dfrac{\sqrt3}{2}\Big)", acos(-sqrt(3) / 2)), "d3b": (r"\tan^{-1}\big(-\sqrt3\big)", atan(-sqrt(3))),
    "d3c": (r"\sin^{-1}\Big(-\dfrac12\Big)", asin(R(-1, 2))), "y3a": (r"\sin^{-1}\Big(-\dfrac{1}{\sqrt2}\Big)", asin(-1 / sqrt(2))),
    "y3b": (r"\tan^{-1}\dfrac{\sqrt3}{3}", atan(sqrt(3) / 3)),
    "d4a": (r"\tan\Big(\cos^{-1}\Big(-\dfrac13\Big)\Big)", tan(acos(R(-1, 3)))),
    "d4b": (r"\cos\Big(\sin^{-1}\Big(-\dfrac56\Big)\Big)", cos(asin(R(-5, 6)))),
    "d4c": (r"\cos\Big(\cos^{-1}\dfrac27\Big)", R(2, 7)), "d4d": (r"\cos^{-1}\Big(\cos\dfrac{5\pi}{3}\Big)", acos(cos(5 * pi / 3))),
    "y4a": (r"\tan\Big(\sin^{-1}\Big(-\dfrac23\Big)\Big)", tan(asin(R(-2, 3)))),
    "y4b": (r"\sin\Big(\cos^{-1}\dfrac{7}{25}\Big)", sin(acos(R(7, 25)))),
    "y4c": (r"\sin\Big(\sin^{-1}\Big(-\dfrac13\Big)\Big)", R(-1, 3)), "y4d": (r"\sin^{-1}\Big(\sin\dfrac{5\pi}{6}\Big)", asin(sin(5 * pi / 6))),
}
for k, (q, v) in Qs.items():
    check(q in L, f"{k}: question {q} printed in the lesson")
    eq_value(A, k, sp.nsimplify(v), f"{k} = {sp.nsimplify(sp.simplify(v))}")
set_value(A, "d1d", I(-1, 1), "C2 demo domain of acos")
set_value(A, "d1r", I(0, pi), "C2 demo range of acos")
set_value(A, "y1r", I.open(-pi / 2, pi / 2), "C2 your turn range of atan")

# ---- Exercise 17B (questions typed from the book, checked printed in the lesson)
ex1 = {"1a": 0.4, "1b": 0.8, "1c": 0.25, "1d": -0.1, "1e": -0.4, "1f": -0.75}
for k, v in ex1.items():
    s = get(A, k)
    if s:
        got = float(tex(maths(s)))
        check(abs(got - math.acos(v)) <= 0.01 + 1e-9, f"{k}: read-off {got} within 0.01 of acos({v}) = {math.acos(v):.4f}")
ex2 = {"2a": asin(0), "2b": asin(R(1, 2)), "2c": acos(1), "2d": atan(1), "2e": asin(-1), "2f": acos(0), "2g": atan(0),
       "2h": atan(-1), "2i": asin(-sqrt(3) / 2), "2j": acos(-1 / sqrt(2)), "2k": atan(-1 / sqrt(3)), "2l": acos(-1)}
for k, v in ex2.items():
    eq_value(A, k, v, k)
ex3 = {"3a": math.acos(0.123), "3b": math.acos(-0.123), "3c": math.asin(2 / 3), "3d": math.asin(-2 / 3), "3e": math.atan(5), "3f": math.atan(-5)}
for k, v in ex3.items():
    s = get(A, k)
    if s:
        check(maths(s) == f"{v:.3f}", f"{k}: printed {maths(s)} = {v:.3f}")
ex4 = {"4a": asin(R(-1, 2)) + acos(R(-1, 2)), "4b": sin(acos(0)), "4c": tan(atan(1)), "4d": acos(sin(pi / 3)),
       "4e": sin(acos(sqrt(3) / 2)), "4f": acos(cos(3 * pi / 4)), "4g": atan(-tan(pi / 6)), "4h": cos(2 * atan(-1)),
       "4i": atan(sqrt(6) * sin(pi / 4))}
ex5 = {"5a": asin(sin(4 * pi / 3)), "5b": acos(cos(-pi / 4)), "5c": atan(tan(5 * pi / 6)), "5d": acos(cos(5 * pi / 4)),
       "5e": asin(2 * sin(-pi / 6)), "5f": atan(3 * tan(7 * pi / 6))}
for k, v in {**ex4, **ex5}.items():
    eq_value(A, k, sp.simplify(v), k)
ex7 = {"7i": sin(acos(R(3, 5))), "7ii": tan(asin(R(5, 13))), "7iii": cos(asin(R(2, 3))), "7iv": sin(acos(R(-15, 17))),
       "7v": cos(atan(R(-1, 3))), "7vi": tan(acos(R(-3, 4)))}
for k, v in ex7.items():
    eq_value(A, k, sp.simplify(v), k)
for q in [r"\sin\Big(\cos^{-1}\dfrac35\Big)", r"\tan\Big(\cos^{-1}\Big(-\dfrac34\Big)\Big)", r"\arctan\Big(3\tan\dfrac{7\pi}{6}\Big)",
          r"\cos\big(2\tan^{-1}(-1)\big)", r"\arccos(-0.75)", r"\arctan(-5)"]:
    check(q in L, f"exercise question {q} printed")
# 12b: tan^-1 x + tan^-1 (1/x) for x < 0
vals = {float(sp.N(atan(xv) + atan(1 / xv))) for xv in (R(-1, 3), -1, -5, R(-7, 2))}
check(len({round(v, 12) for v in vals}) == 1, "12b constant for x < 0")
eq_value(A, "12b", -pi / 2, "12b")
set_value(A, "13a", function_range(atan(x ** 2), x, sp.S.Reals), "13a range of atan(x^2)")
set_value(A, "13b", function_range(atan(1 / (1 + x ** 2)), x, sp.S.Reals), "13b range of atan(1/(1+x^2))")
eq_value(A, "14c", asin(sin(2)), "14c asin(sin 2)")
check(abs(float(asin(sin(2))) - (math.pi - 2)) < 1e-12 and abs(float(acos(cos(2))) - 2) < 1e-12, "14a acos(cos 2) = 2, asin(sin 2) = pi - 2")

# ---- past papers
pp_block(L, A)
set_value(A, "pp1", I(R(-2, 3), R(2, 3)), "PP1 domain")
mc_key(A, "PP 1", "A")
set_value(A, "pp2", I(R(-1, 4), R(1, 4)), "PP2 domain")
mc_key(A, "PP 2", "C")
set_value(A, "pp3", function_range(6 * asin(3 * x), x, I(R(-1, 3), R(1, 3))), "PP3 range")
mc_key(A, "PP 3", "B")
check(sp.simplify(sin(11 * pi / 12) - (sqrt(6) - sqrt(2)) / 4) == 0, "PP4 the given value of sin(11pi/12)")
eq_value(A, "pp4", asin((sqrt(6) - sqrt(2)) / 4), "PP4")
mc_key(A, "PP 4", "A")
# PP5: test each option at points of [0, pi]
pts = [k_ * math.pi / 20 for k_ in range(21)]
def holds(f):
    try:
        return all(abs(f(v) - v) < 1e-9 for v in pts)
    except ValueError:
        return False
opts = {"A": lambda v: math.asin(math.sin(v)), "B": lambda v: math.sin(math.asin(v)),
        "C": lambda v: math.acos(math.cos(v)), "D": lambda v: math.cos(math.acos(v))}
true = [k_ for k_, f in opts.items() if holds(f)]
check(true == ["C"], f"PP5 only C holds on [0, pi] ({true})")
mc_key(A, "PP 5", "C")
# PP6, PP7: test options at several angles
al = [math.pi / 2 + k_ * math.pi / 2 / 9 for k_ in range(1, 9)]
o6 = {"A": lambda a: math.pi - a, "B": lambda a: math.pi / 2 - a, "C": lambda a: a - math.pi / 2, "D": lambda a: a + math.pi / 2}
good6 = [k_ for k_, f in o6.items() if all(abs(math.acos(math.sin(a)) - f(a)) < 1e-9 for a in al)]
check(good6 == ["C"], f"PP6 only C ({good6})")
mc_key(A, "PP 6", "C")
th = [1.5 * math.pi + k_ * math.pi / 2 / 9 for k_ in range(1, 9)]
o7 = {"A": lambda t: math.pi / 2 - t, "B": lambda t: 1.5 * math.pi - t, "C": lambda t: -1.5 * math.pi + t, "D": lambda t: 2 * math.pi - t}
good7 = [k_ for k_, f in o7.items() if all(abs(math.asin(math.cos(t)) - f(t)) < 1e-9 for t in th)]
check(good7 == ["C"], f"PP7 only C ({good7})")
mc_key(A, "PP 7", "C")
s = get(A, "pp6")
s7 = get(A, "pp7")
check(s is not None and "\\alpha-\\dfrac\\pi2" in s and s7 is not None and "-\\dfrac{3\\pi}{2}+\\theta" in s7, "PP6/PP7 printed results")
eq_value(A, "pp8", 2 * asin(sqrt(3) / 2) - acos(R(1, 2)) + atan(-1), "PP8")
eq_value(A, "pp9", acos(sin(4 * pi / 3)), "PP9")
u, v = sp.symbols("u v")
sol = sp.solve([2 * u + 3 * v - 3 * pi / 2, 2 * u - 3 * v - pi / 2], [u, v])
xs, ys = sp.sin(sol[u]), sp.cos(sol[v])
check(-pi / 2 <= sol[u] <= pi / 2 and 0 <= sol[v] <= pi, "PP10 u, v inside the ranges")
s = get(A, "pp10")
if s:
    m = maths(s).replace("\\ ", "")
    xv, yv = [p.split("=")[1] for p in m.split(",")]
    check(sp.simplify(tex(xv) - xs) == 0 and sp.simplify(tex(yv) - ys) == 0, f"PP10 x = {xs}, y = {ys}")
set_value(A, "pp11", function_range(sp.sec(x), x, I.open(0, pi / 2)), "PP11 domain of f^-1 = range of sec on (0, pi/2)")
for xv in (R(3, 2), 2, 7):
    check(abs(float(sp.sec(acos(1 / sp.Integer(1) / xv))) - float(xv)) < 1e-12, f"PP11 sec(acos(1/x)) = x at {xv}")
finish("y11ch17_17b")
